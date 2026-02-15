from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://user:password@localhost/raggae"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: str = ""
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    max_upload_size: int = 10485760

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
