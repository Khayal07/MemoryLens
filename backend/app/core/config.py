from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_JWT_DEFAULT = "change-me-in-production"


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
    jwt_secret: str = _INSECURE_JWT_DEFAULT
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 7

    # Abuse / cost controls on the paid LLM search. `search_rate_per_min` paces
    # bursts; `search_daily_quota` is a hard per-user ceiling (see core/rate_limit).
    search_rate_per_min: int = 10
    search_daily_quota: int = 50
    # Shared secret guarding /metrics in production (sent as X-Metrics-Token). Blank
    # in development leaves the endpoint open for local Prometheus scraping.
    metrics_token: str = ""

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
    # Grey zone above the floor: a grounded match here isn't strong, so we still ask the
    # LLM for its world-knowledge answer and override the catalog pick only when it names
    # a *different* title (the grounded match was likely wrong). Same title → keep the
    # grounded row so its poster/source survive.
    freeform_grey_margin: float = 8.0
    # Akinator mode: when the best grounded match is below this (0..100), attach ONE
    # LLM-written clarifying question to the response; the frontend folds the user's
    # answer back into a refined re-search.
    clarify_enabled: bool = True
    clarify_floor: float = 65.0

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.env.lower() != "development"

    @model_validator(mode="after")
    def _require_strong_secret_in_prod(self) -> "Settings":
        """Fail fast at startup rather than silently signing tokens with the public
        default secret — anyone could forge JWTs. Dev keeps the friendly default."""
        if self.is_production and (
            not self.jwt_secret or self.jwt_secret == _INSECURE_JWT_DEFAULT
        ):
            raise ValueError(
                "JWT_SECRET must be set to a strong random value when ENV is not "
                "'development' (generate one with: openssl rand -hex 32)."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
