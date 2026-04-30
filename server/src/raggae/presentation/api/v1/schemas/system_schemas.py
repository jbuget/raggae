from pydantic import BaseModel


class SystemDefaultsResponse(BaseModel):
    llm_backend: str
    llm_model: str
    embedding_backend: str
    embedding_model: str
    retrieval_strategy: str
    retrieval_top_k: int
    retrieval_min_score: float
    reranker_backend: str
    reranker_model: str
    reranker_candidate_multiplier: int
    chat_history_window_size: int
    chat_history_max_chars: int
