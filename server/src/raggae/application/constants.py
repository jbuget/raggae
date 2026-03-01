ALLOWED_LLM_MODELS: dict[str, frozenset[str]] = {
    "openai": frozenset({
        "gpt-5.2", "gpt-5.2-pro", "gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-5-nano",
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
    }),
    "gemini": frozenset({
        "gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-3-deep-think-preview",
    }),
    "anthropic": frozenset({
        "claude-opus-4-6-20260205", "claude-opus-4-5-20251101",
        "claude-sonnet-4-6-20260217", "claude-sonnet-4-20250514",
        "claude-haiku-4-5-20251001",
    }),
    "inmemory": frozenset({
        "inmemory-chat-accurate", "inmemory-chat-balanced", "inmemory-chat-fast",
    }),
}

ALLOWED_EMBEDDING_MODELS: dict[str, frozenset[str]] = {
    "openai": frozenset({
        "text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002",
    }),
    "gemini": frozenset({
        "gemini-embedding-001", "text-multilingual-embedding-002",
    }),
    "inmemory": frozenset({
        "inmemory-embed-accurate", "inmemory-embed-balanced", "inmemory-embed-fast",
    }),
}

MAX_PROJECT_SYSTEM_PROMPT_LENGTH = 8000
MIN_PROJECT_CHAT_HISTORY_WINDOW_SIZE = 1
MAX_PROJECT_CHAT_HISTORY_WINDOW_SIZE = 40
DEFAULT_PROJECT_CHAT_HISTORY_WINDOW_SIZE = 8
MIN_PROJECT_CHAT_HISTORY_MAX_CHARS = 128
MAX_PROJECT_CHAT_HISTORY_MAX_CHARS = 16000
DEFAULT_PROJECT_CHAT_HISTORY_MAX_CHARS = 4000
MIN_PROJECT_RERANKER_CANDIDATE_MULTIPLIER = 1
MAX_PROJECT_RERANKER_CANDIDATE_MULTIPLIER = 10
DEFAULT_PROJECT_RERANKER_CANDIDATE_MULTIPLIER = 3
MIN_PROJECT_RETRIEVAL_TOP_K = 1
MAX_PROJECT_RETRIEVAL_TOP_K = 40
DEFAULT_PROJECT_RETRIEVAL_TOP_K = 8
MIN_PROJECT_RETRIEVAL_MIN_SCORE = 0.0
MAX_PROJECT_RETRIEVAL_MIN_SCORE = 1.0
DEFAULT_PROJECT_RETRIEVAL_MIN_SCORE = 0.3
