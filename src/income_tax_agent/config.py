"""All settings in one place. Values come from environment variables or `.env`."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root: src/income_tax_agent/config.py -> three levels up.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Data paths ---
    pdf_path: Path = (
        PROJECT_ROOT / "data/raw/Income-tax-Act-2025_2026_2026-08-25_10-41-45_a1d3cd_en.pdf"
    )
    pages_path: Path = PROJECT_ROOT / "data/processed/pages.jsonl"
    index_dir: Path = PROJECT_ROOT / "data/index"

    # --- Cleaning ---
    # Footnotes often quote old, repealed text. Removing them is the default.
    # Set to False only for the ablation that measures how much this matters.
    strip_footnotes: bool = True

    # --- Models ---
    # Gemini model names change often on the free tier, so they are never hardcoded.
    google_api_key: str = ""
    gemini_model: str = ""
    gemini_judge_model: str = ""
    llm_cache_dir: Path = PROJECT_ROOT / ".cache/llm"
    # None = the model's default. Some models ignore temperature (fixed sampling).
    gemini_temperature: float | None = None
    # Answer model only (Gemini 3+): "minimal", "low", "medium", "high". Empty = model default.
    # Flash-Lite without thinking refused 2 of 4 tries at "tax on a 50 lakh salary" although
    # the rate table was retrieved (2026-10-29).
    gemini_thinking_level: str | None = None
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    # Added to queries (not passages). BGE recommends it for query -> passage search.
    embedding_query_prefix: str = "Represent this sentence for searching relevant passages: "
    # fastembed's default cache is a temp folder that macOS may wipe. Keep models here.
    model_cache_dir: Path = PROJECT_ROOT / ".cache/fastembed"
    # A folder with the model's files (scripts/download_model.py), used instead of the cache.
    # Set on Vercel: the model ships inside the deployment, so nothing is downloaded at start.
    embedding_model_dir: Path | None = None

    # --- Index ---
    chunk_size: int = 1000
    chunk_overlap: int = 150
    # Structured chunker (chunkers/structured.py): sizes without whitespace runs.
    structured_max_chars: int = 1500
    structured_min_chars: int = 300
    # The index the app and eval use by default. Grid of 4 indexes x 3 modes x expansion x
    # reranker (eval/results, 2026-10-24): structured + dense + expansion + reranker was best,
    # strict hit@1 dev 23/23, held-out 9/10 (fixed-header, same setup: 19/23, 7/10).
    index_name: str = "structured-1500__bge-base"

    # --- Retrieval ---
    # Reciprocal Rank Fusion constant. The paper's 60 makes rank 1 worth barely more than
    # rank 10, so a strong hit from only dense or only BM25 got outvoted. Sweep on 2026-10-19
    # (hybrid, no expansion): dev strict MRR 0.73 at k=60, 0.79 at k=2.
    rrf_k: int = 2
    hybrid_candidates: int = 50  # how deep each list goes before fusing
    # What the answer pipeline uses. With the reranker the first-stage mode matters little
    # (it only has to get the right chunk into the pool); dense was best and is simplest
    # (2026-10-24: hit@1 dev 23/23 vs hybrid 22/23).
    answer_mode: str = "dense"
    answer_k: int = 5
    answer_neighbours: bool = True

    # --- Query expansion ---
    # An LLM writes extra search queries in the Act's wording (prompts.EXPAND_SYSTEM).
    # On: dense + expansion + neighbours raised strict hit@1 from 15/22 to 18/22, hit@5 from
    # 20/22 to 21/22 and MRR from 0.76 to 0.87 (eval/results, 2026-10-18). Hybrid gained less.
    expand_queries: bool = True
    # Empty = GEMINI_MODEL. A small task, so Flash-Lite (the largest free quota) is enough.
    gemini_expand_model: str = ""
    # How the queries' lists are merged: "max" (best rank in any list; see fusion.py) or "rrf".
    # With RRF, a section that only one rewrite finds at rank 1 was outvoted by chunks that
    # were mediocre for every query (held-out h09: lost). Max keeps it: hybrid dev strict
    # hit@5 19/22 -> 21/22, MRR 0.88 both (sweep, 2026-10-19).
    expand_fusion: str = "max"
    # How deep each query's list goes before merging.
    expand_candidates: int = 10

    # --- Reranking ---
    # A cross-encoder (retrieval/rerank.py) reorders the pooled candidates of all queries
    # (Retriever.rerank). Replaces expand_fusion when on. The biggest single gain in the
    # 2026-10-24 grid (+4 to +5 questions at hit@1); costs ~2.3 s per question on an M2.
    rerank: bool = True
    # Model sweep on structured + hybrid + expansion (2026-10-24): the smallest (80 MB) was
    # best on dev; MiniLM-L-12, both jina models and bge-reranker-base (1 GB) were not better.
    rerank_model: str = "Xenova/ms-marco-MiniLM-L-6-v2"
    # Like embedding_model_dir: a folder with the model's files (scripts/download_model.py).
    rerank_model_dir: Path | None = None
    # Candidates taken from each query's list (question + rewrites), then pooled.
    # 10 scored the same as 20 with dense (2026-10-24) at half the reranker time.
    rerank_candidates: int = 10
    # Weight of the best rewrite's score next to the question's (only 0.5 was tried).
    rerank_rewrite_weight: float = 0.5

    # --- App ---
    # Strangers share one free API quota. Per visitor (IP address) and for all visitors
    # together, over a sliding window kept in server memory, so a page reload doesn't reset
    # it (limits.py). Off in dev mode. The total is not shown in the app; the server log
    # prints it after every answer.
    max_questions_per_visitor: int = 20
    max_questions_total: int = 150
    question_window_hours: float = 24
    # Earlier turns used to rewrite a follow-up question (prompts.REWRITE_SYSTEM).
    history_turns: int = 3
    # Shows timings, token counts, cache hits, prompts and memory under each answer.
    # For local testing only: set DEV_MODE=1 in .env, never in Streamlit Cloud's Secrets.
    dev_mode: bool = False

    # CI sets this to 1: fake embeddings and a fake LLM, so no keys or downloads.
    fake_models: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
