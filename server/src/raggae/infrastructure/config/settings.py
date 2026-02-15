from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://user:password@localhost/raggae"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: str = ""
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    max_upload_size: int = 104857600
    storage_backend: str = "inmemory"
    persistence_backend: str = "inmemory"
    processing_mode: str = "off"
    embedding_backend: str = "inmemory"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 100
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "raggae-documents"
    s3_region: str = "us-east-1"
    s3_secure: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
