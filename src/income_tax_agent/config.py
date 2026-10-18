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
    # The index the app and eval use by default.
    index_name: str = "fixed-1000-150__bge-base"

    # --- Retrieval ---
    rrf_k: int = 60  # Reciprocal Rank Fusion constant
    hybrid_candidates: int = 50  # how deep each list goes before fusing
    # What the answer pipeline uses.
    answer_mode: str = "hybrid"
    answer_k: int = 5
    answer_neighbours: bool = False

    # CI sets this to 1: fake embeddings and a fake LLM, so no keys or downloads.
    fake_models: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
