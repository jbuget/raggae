from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

_SERVER_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql+asyncpg://user:password@localhost/raggae"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    default_llm_provider: str = Field(default="inmemory", alias="DEFAULT_LLM_PROVIDER")
    default_llm_api_key: str = Field(default="", alias="DEFAULT_LLM_API_KEY")
    default_llm_model: str = Field(default="", alias="DEFAULT_LLM_MODEL")
    default_embedding_provider: str = Field(
        default="inmemory", alias="DEFAULT_EMBEDDING_PROVIDER"
    )
    default_embedding_api_key: str = Field(default="", alias="DEFAULT_EMBEDDING_API_KEY")
    default_embedding_model: str = Field(default="", alias="DEFAULT_EMBEDDING_MODEL")
    credentials_encryption_key: str = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    user_provider_keys_enabled: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    max_upload_size: int = 10485760
    max_documents_per_project: int = 100
    max_upload_files_per_request: int = 20
    storage_backend: str = "inmemory"
    persistence_backend: str = "inmemory"
    processing_mode: str = "off"
    text_chunker_backend: str = "native"
    gemini_embedding_model: str = "text-embedding-004"
    gemini_llm_model: str = "gemini-1.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.1"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_keep_alive: str = "10m"
    llm_request_timeout_seconds: float = 120.0
    embedding_dimension: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 100
    reranker_backend: str = "none"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_candidate_multiplier: int = 3
    retrieval_context_window_size: int = 1
    retrieval_default_strategy: str = "hybrid"
    retrieval_min_score: float = 0.3
    retrieval_default_chunk_limit: int = 8
    chat_history_window_size: int = 8
    chat_history_max_chars: int = 4000
    retrieval_vector_weight: float = 0.6
    retrieval_fulltext_weight: float = 0.4
    retrieval_candidate_multiplier: int = 5
    retrieval_fulltext_language: str = "french"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "raggae-documents"
    s3_region: str = "us-east-1"
    s3_secure: bool = False

    model_config = {
        "env_file": (_SERVER_ROOT / ".env", ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
