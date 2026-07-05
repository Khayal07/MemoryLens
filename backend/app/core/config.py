from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment / .env. Never hardcode secrets."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    cors_origins: str = "http://localhost:5173"

    # OpenAI (primary LLM reasoning)
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-nano"
    openai_base_url: str = "https://api.openai.com/v1"

    # OpenRouter (fallback LLM reasoning)
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # LLM provider chain: fall back to OpenRouter if OpenAI fails/runs out
    llm_fallback_enabled: bool = True

    # Ingestion sources (optional — fixtures used when absent)
    tmdb_api_key: str = ""
    rawg_api_key: str = ""
    # OMDb: poster fallback when TMDb has none (movies/tv). Blank → placeholder only.
    omdb_api_key: str = ""

    # Database
    database_url: str = "postgresql+psycopg://memorylens:memorylens@localhost:5432/memorylens"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 7

    # Local AI models
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"

    # Retrieval tuning
    rrf_vector_weight: float = 1.0
    rrf_keyword_weight: float = 0.6
    rerank_top_n: int = 12
    hyde_enabled: bool = False
    # Multilingual queries: local embed/rerank models are English-only, so a
    # non-English memory is translated to English for retrieval while the LLM keeps
    # the original text and answers in the user's language.
    translate_enabled: bool = True
    # Free-form fallback: when the best grounded match scores below this (0..100),
    # let the LLM name the real item from its own knowledge.
    freeform_enabled: bool = True
    freeform_confidence_floor: float = 65.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
