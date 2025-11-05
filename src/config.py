"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Medical Annotation API"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./medical_annotations.db"
    test_db_url: str = "sqlite:///./test.db"
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

