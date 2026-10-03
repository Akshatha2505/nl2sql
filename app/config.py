from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All values read from container environment (docker-compose env_file + environment)."""

    model_config = SettingsConfigDict(extra="ignore", populate_by_name=True)

    database_url: str = Field(validation_alias="DATABASE_URL")
    ollama_host: str = Field(
        default="http://host.docker.internal:11434",
        validation_alias="OLLAMA_HOST",
    )
    ollama_model: str = Field(
        default="qwen2.5-coder:7b",
        validation_alias="OLLAMA_MODEL",
    )
    query_max_rows: int = Field(default=100, validation_alias="QUERY_MAX_ROWS")
    query_timeout_sec: int = Field(default=30, validation_alias="QUERY_TIMEOUT_SEC")
    schema_cache_ttl_sec: int = Field(
        default=300, validation_alias="SCHEMA_CACHE_TTL_SEC"
    )


settings = Settings()
