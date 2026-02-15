from raggae.infrastructure.services.admin_system_prompt import ADMIN_SYSTEM_PROMPT


def build_rag_prompt(
    query: str,
    context_chunks: list[str],
    project_system_prompt: str | None = None,
) -> str:
    context = "\n\n".join(context_chunks) if context_chunks else "No context available."
    project_prompt = (project_system_prompt or "").strip()
    project_prompt_section = (
        f"\n\nProject-level instructions (lower priority than admin):\n{project_prompt}"
        if project_prompt
        else ""
    )
    return (
        f"{ADMIN_SYSTEM_PROMPT}\n\n"
        "You are a retrieval-augmented assistant.\n"
        "Always follow admin instructions first, then project instructions.\n"
        "Use only the provided context.\n"
        "If the context is insufficient, explicitly say you do not know."
        f"{project_prompt_section}\n\n"
        f"Context:\n{context}\n\n"
        f"User query: {query}"
    )
