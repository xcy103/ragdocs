from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, loaded from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-8"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "ragdocs"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "document_chunks"

    embedding_model: str = "BAAI/bge-small-en-v1.5"

    top_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()
