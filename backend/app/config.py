from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration, sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    simulator_enabled: bool = True
    simulator_interval_seconds: float = 5.0
    cors_origins: str = "http://localhost:5173"


settings = Settings()
