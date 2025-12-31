"""Configuration management for the Weekly Strategic Insight Engine."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/strategic_insight"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # OpenAI (Optional)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"

    # Grok (Primary LLM)
    grok_api_key: str | None = None
    grok_api_url: str = "https://api.x.ai/v1"
    grok_model: str = "grok-beta"

    # Slack
    slack_bot_token: str | None = None
    slack_user_id: str | None = None

    # n8n
    n8n_url: str = "https://n8n.srv996391.hstgr.cloud"
    n8n_email: str = "frontendlabs.uk@gmail.com"
    n8n_password: str = "4rontEnd#labs"

    # Processing
    embedding_model: str = "all-MiniLM-L6-v2"
    hdbscan_min_cluster_size: int = 3
    topic_similarity_threshold: float = 0.85
    urgency_low_max: int = 3
    urgency_medium_max: int = 7

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
