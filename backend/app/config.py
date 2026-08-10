from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    database_url: str

    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_chat_model: str = "gpt-5.5"
    openai_grounding_model: str = "gpt-4.1-mini"
    openai_agent_request_limit: int = 20
    openai_agent_temperature: float = 0.0

    retrieval_candidate_k: int = 50
    retrieval_top_k: int = 10
    retrieval_rrf_k: int = 60
    retrieval_neighbor_radius: int = 1
    retrieval_fts_config: str = "english"
    retrieval_fts_keyword_model: str = "gpt-4.1-mini"
    retrieval_fts_keyword_min: int = 3
    retrieval_fts_keyword_max: int = 5
    retrieval_fts_keyword_fast_path_tokens: int = 5

    # Comma-separated in .env; use `cors_origins` for the parsed list.
    allowed_origins: str = "http://localhost:5173"

    @computed_field
    @property
    def sqlalchemy_database_url(self) -> str:
        """Normalize Supabase-style URLs for SQLAlchemy + psycopg v3."""
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
