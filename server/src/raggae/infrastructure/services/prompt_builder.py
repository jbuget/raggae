def build_rag_prompt(query: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks) if context_chunks else "No context available."
    return (
        "You are a retrieval-augmented assistant.\n"
        "Use only the provided context.\n"
        "If the context is insufficient, explicitly say you do not know.\n\n"
        f"Context:\n{context}\n\n"
        f"User query: {query}"
    )
