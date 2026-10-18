"""Gemini client with retry on rate limits and a disk cache.

The free tier is small, so:
- every response is cached on disk, keyed by a hash of (model, temperature, messages).
  Re-running the eval with unchanged prompts makes no API calls.
- HTTP 429 (rate limit) and 5xx errors are retried with exponential backoff (tenacity).
  The LangChain client's own retries are switched off so retries happen in one place.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Protocol

from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from income_tax_agent.config import Settings, get_settings


class LLM(Protocol):
    model_name: str

    def complete(self, system: str, user: str) -> str: ...


class NotRetryable(Exception):
    """An API error that will not fix itself (bad key, unknown model, bad request)."""


class QuotaExhausted(NotRetryable):
    """The free tier's *daily* request limit is used up. Retrying within minutes is pointless."""


def _cache_key(model: str, temperature: float | None, system: str, user: str) -> str:
    payload = json.dumps([model, temperature, system, user], ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


class GeminiLLM:
    def __init__(
        self, model_name: str, api_key: str, cache_dir: Path, temperature: float | None = None
    ):
        # temperature=None uses the model's default. Some Gemini models (e.g. 3.5 Flash-Lite)
        # use fixed sampling and ignore temperature, so answers can vary between calls.
        # Reproducible eval runs come from the disk cache, not from temperature.
        if not model_name:
            raise ValueError("GEMINI_MODEL is not set. Add the current free-tier model name to .env.")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in .env.")
        from langchain_google_genai import ChatGoogleGenerativeAI

        self.model_name = model_name
        self.temperature = temperature
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        options = {} if temperature is None else {"temperature": temperature}
        self._chat = ChatGoogleGenerativeAI(
            model=model_name, google_api_key=api_key, max_retries=0, **options
        )
        self.api_calls = 0  # requests that reached Google (cache misses, including retries)

    def complete(self, system: str, user: str) -> str:
        path = self.cache_dir / f"{_cache_key(self.model_name, self.temperature, system, user)}.json"
        if path.exists():
            return json.loads(path.read_text())["text"]
        text = self._call(system, user)
        record = {"model": self.model_name, "temperature": self.temperature, "text": text}
        path.write_text(json.dumps(record, ensure_ascii=False))
        return text

    # Waits 4s, 8s, 16s, 32s between attempts (capped at 60s), then gives up.
    @retry(
        retry=retry_if_not_exception_type(NotRetryable),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _call(self, system: str, user: str) -> str:
        from langchain_google_genai.chat_models import GoogleAPIError, GoogleRateLimitError

        self.api_calls += 1
        try:
            return self._chat.invoke([("system", system), ("human", user)]).text
        except GoogleRateLimitError as e:
            # Per-minute limits clear quickly; per-day limits (quotaId "...PerDay...") do not.
            if "PerDay" in str(e):
                raise QuotaExhausted(f"{self.model_name}: daily free-tier quota used up") from e
            raise  # per-minute 429: worth retrying
        except GoogleAPIError:
            raise  # 5xx: worth retrying
        except Exception as e:
            raise NotRetryable(str(e)) from e


class FakeLLM:
    """For tests and CI: no key, no network. Cites the first section it was shown."""

    model_name = "fake"

    def complete(self, system: str, user: str) -> str:
        if user.startswith("Question: "):  # query expansion: echo the question (adds nothing)
            return user.removeprefix("Question: ")
        # Excerpt headers look like "[Excerpt 1 | Section 202 | ...]".
        m = re.search(r"\| Sections? ([^ ,;|\]]+)", user)
        if not m:
            return "I could not find this in the Act."
        return f"Fake answer based on the excerpts [Section {m.group(1)}]."


def get_llm(settings: Settings | None = None, model_name: str | None = None) -> LLM:
    settings = settings or get_settings()
    if settings.fake_models:
        return FakeLLM()
    return GeminiLLM(
        model_name or settings.gemini_model, settings.google_api_key, settings.llm_cache_dir,
        settings.gemini_temperature,
    )


def get_expand_llm(settings: Settings | None = None) -> LLM:
    """The model that writes search queries (GEMINI_EXPAND_MODEL, else GEMINI_MODEL)."""
    settings = settings or get_settings()
    return get_llm(settings, settings.gemini_expand_model or settings.gemini_model)
