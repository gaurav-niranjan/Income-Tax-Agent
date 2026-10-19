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
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    # Added to queries (not passages). BGE recommends it for query -> passage search.
    embedding_query_prefix: str = "Represent this sentence for searching relevant passages: "
    # fastembed's default cache is a temp folder that macOS may wipe. Keep models here.
    model_cache_dir: Path = PROJECT_ROOT / ".cache/fastembed"

    # --- Index ---
    chunk_size: int = 1000
    chunk_overlap: int = 150
    # The index the app and eval use by default. Chosen on the retrieval eval
    # (eval/results, 2026-10-18): header + dense + neighbours had the best strict hit@5
    # (20/22) and MRR (0.76), and is simpler than hybrid.
    index_name: str = "fixed-1000-150-header__bge-base"

    # --- Retrieval ---
    # Reciprocal Rank Fusion constant. The paper's 60 makes rank 1 worth barely more than
    # rank 10, so a strong hit from only dense or only BM25 got outvoted. Sweep on 2026-10-19
    # (hybrid, no expansion): dev strict MRR 0.73 at k=60, 0.79 at k=2.
    rrf_k: int = 2
    hybrid_candidates: int = 50  # how deep each list goes before fusing
    # What the answer pipeline uses. Hybrid with the fusion below (2026-10-19).
    answer_mode: str = "hybrid"
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

    # --- App ---
    # Strangers share one free API quota; this cap keeps one visitor from using it all.
    # (Per browser session: a page reload resets it. Good enough for a demo.)
    max_questions_per_session: int = 10

    # CI sets this to 1: fake embeddings and a fake LLM, so no keys or downloads.
    fake_models: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
