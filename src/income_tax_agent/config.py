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
    embedding_model: str = "BAAI/bge-base-en-v1.5"

    # CI sets this to 1: fake embeddings and a fake LLM, so no keys or downloads.
    fake_models: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
