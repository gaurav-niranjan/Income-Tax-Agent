"""Gemini client with retry on rate limits and a disk cache.

The free tier is small, so:
- every response is cached on disk, keyed by a hash of (model, temperature, messages).
  Re-running the eval with unchanged prompts makes no API calls.
- HTTP 429 (rate limit) and 5xx errors are retried with exponential backoff (tenacity).
  The LangChain client's own retries are switched off so retries happen in one place.

For the app's dev mode, every call can be logged (model, tokens, cache hit, time, prompt)
with `record_llm_calls()`. The log is a context variable, not an attribute of the LLM,
because one LLM object is shared by all app visitors at once.
"""

import hashlib
import json
import re
import time
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Protocol

from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from income_tax_agent.config import Settings, get_settings

_call_log: ContextVar[list[dict] | None] = ContextVar("llm_call_log", default=None)


@contextmanager
def record_llm_calls() -> Iterator[list[dict]]:
    """Collect one record per LLM call made inside the block (same thread)."""
    calls: list[dict] = []
    token = _call_log.set(calls)
    try:
        yield calls
    finally:
        _call_log.reset(token)


def _log_call(
    model: str,
    system: str,
    user: str,
    reply: str,
    usage: dict | None,
    cached: bool,
    start: float,
) -> None:
    calls = _call_log.get()
    if calls is not None:
        calls.append(
            {
                "model": model,
                "cached": cached,
                "ms": round((time.perf_counter() - start) * 1000),
                "usage": usage,
                "system": system,
                "user": user,
                "reply": reply,
            }
        )


def _usage(message) -> dict | None:
    """Token counts from a LangChain reply. Gemini's output count includes thinking tokens."""
    meta = getattr(message, "usage_metadata", None)
    if not meta:
        return None
    return {
        "input": meta.get("input_tokens", 0),
        "output": meta.get("output_tokens", 0),
        "thinking": (meta.get("output_token_details") or {}).get("reasoning", 0),
        "total": meta.get("total_tokens", 0),
    }


class LLM(Protocol):
    model_name: str

    def complete(self, system: str, user: str) -> str: ...


class NotRetryable(Exception):
    """An API error that will not fix itself (bad key, unknown model, bad request)."""


class QuotaExhausted(NotRetryable):
    """The free tier's *daily* request limit is used up. Retrying within minutes is pointless."""


def _cache_key(
    model: str,
    temperature: float | None,
    system: str,
    user: str,
    thinking: str | None = None,
) -> str:
    # The thinking level is added only when set, so entries cached before it existed still match.
    payload = json.dumps(
        [model, temperature, system, user, *([thinking] if thinking else [])],
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class GeminiLLM:
    def __init__(
        self,
        model_name: str,
        api_key: str,
        cache_dir: Path | None,
        temperature: float | None = None,
        thinking_level: str | None = None,
    ):
        # temperature=None uses the model's default. Some Gemini models (e.g. 3.5 Flash-Lite)
        # use fixed sampling and ignore temperature, so answers can vary between calls.
        # Reproducible eval runs come from the disk cache, not from temperature.
        # cache_dir=None: no cache. The app uses this for answers, so one bad answer is not
        # repeated for everyone who asks the same question.
        if not model_name:
            raise ValueError(
                "GEMINI_MODEL is not set. Add the current free-tier model name to .env."
            )
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in .env.")
        from langchain_google_genai import ChatGoogleGenerativeAI

        self.model_name = model_name
        self.temperature = temperature
        self.thinking_level = thinking_level or None
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
        options = {} if temperature is None else {"temperature": temperature}
        if self.thinking_level:  # Gemini 3+: "minimal", "low", "medium" or "high"
            options["thinking_level"] = self.thinking_level
        self._chat = ChatGoogleGenerativeAI(
            model=model_name, google_api_key=api_key, max_retries=0, **options
        )
        self.api_calls = (
            0  # requests that reached Google (cache misses, including retries)
        )

    def complete(self, system: str, user: str) -> str:
        start = time.perf_counter()
        key = _cache_key(
            self.model_name, self.temperature, system, user, self.thinking_level
        )
        path = self.cache_dir / f"{key}.json" if self.cache_dir else None
        cached = bool(path and path.exists())
        if cached:
            record = json.loads(path.read_text())
        else:
            text, usage = self._call(system, user)
            # Usage is stored too, so a cache hit can show what the call cost the first time.
            record = {
                "model": self.model_name,
                "temperature": self.temperature,
                "text": text,
                "usage": usage,
            }
            if path:
                path.write_text(json.dumps(record, ensure_ascii=False))
        # Records cached before usage was stored have none.
        _log_call(
            self.model_name,
            system,
            user,
            record["text"],
            record.get("usage"),
            cached,
            start,
        )
        return record["text"]

    # Waits 4s, 8s, 16s, 32s between attempts (capped at 60s), then gives up.
    @retry(
        retry=retry_if_not_exception_type(NotRetryable),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def _call(self, system: str, user: str) -> tuple[str, dict | None]:
        from langchain_google_genai.chat_models import (
            GoogleAPIError,
            GoogleRateLimitError,
        )

        self.api_calls += 1
        try:
            reply = self._chat.invoke([("system", system), ("human", user)])
            return reply.text, _usage(reply)
        except GoogleRateLimitError as e:
            # Per-minute limits clear quickly; per-day limits (quotaId "...PerDay...") do not.
            if "PerDay" in str(e):
                raise QuotaExhausted(
                    f"{self.model_name}: daily free-tier quota used up"
                ) from e
            raise  # per-minute 429: worth retrying
        except GoogleAPIError:
            raise  # 5xx: worth retrying
        except Exception as e:
            raise NotRetryable(str(e)) from e


class FakeLLM:
    """For tests and CI: no key, no network. Cites the first section it was shown."""

    model_name = "fake"

    def complete(self, system: str, user: str) -> str:
        reply = self._reply(user)
        _log_call(
            self.model_name, system, user, reply, None, False, time.perf_counter()
        )
        return reply

    def _reply(self, user: str) -> str:
        if user.startswith(
            "Question: "
        ):  # query expansion: echo the question (adds nothing)
            return user.removeprefix("Question: ")
        if (
            "Follow-up question: " in user
        ):  # follow-up rewrite: prepend the last question
            last = re.findall(r"^User: (.*)$", user, re.MULTILINE)[-1]
            return f"{last} {user.split('Follow-up question: ')[-1]}"
        # Excerpt headers look like "[Excerpt 1 | Section 202 | ...]".
        m = re.search(r"\| Sections? ([^ ,;|\]]+)", user)
        if not m:
            return "I could not find this in the Act."
        return f"Fake answer based on the excerpts [Section {m.group(1)}]."


def get_llm(
    settings: Settings | None = None, model_name: str | None = None, cache: bool = True
) -> LLM:
    """The answer model (GEMINI_MODEL with GEMINI_THINKING_LEVEL), or another model by name."""
    settings = settings or get_settings()
    if settings.fake_models:
        return FakeLLM()
    return GeminiLLM(
        model_name or settings.gemini_model,
        settings.google_api_key,
        settings.llm_cache_dir if cache else None,
        settings.gemini_temperature,
        None if model_name else settings.gemini_thinking_level,
    )


def get_expand_llm(settings: Settings | None = None) -> LLM:
    """The model that writes search queries (GEMINI_EXPAND_MODEL, else GEMINI_MODEL)."""
    settings = settings or get_settings()
    return get_llm(settings, settings.gemini_expand_model or settings.gemini_model)
