from raggae.application.interfaces.services.llm_service import LLMService

_META_PROMPT = """\
You are an expert at designing system prompts for AI assistants built on RAG (Retrieval-Augmented Generation) architectures.

Given a short description of an assistant, generate a complete, professional system prompt.

The generated prompt must:
- Define the assistant's role and purpose clearly
- Specify the tone and communication style
- Describe what the assistant can and cannot do
- Explain how it should handle out-of-scope questions (redirect politely, do not invent answers)
- Specify the response language if relevant
- Be self-contained and ready to use as-is

Respond with only the system prompt text. Do not include any explanation, preamble, or markdown formatting.\
"""


class GenerateProjectPrompt:
    """Use Case: Generate a system prompt from a short description using the default LLM."""

    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def execute(self, description: str, name: str = "", audience: str = "") -> str:
        context_lines = [f"Description: {description}"]
        if name:
            context_lines.insert(0, f"Assistant name: {name}")
        if audience:
            context_lines.append(f"Target audience: {audience}")

        full_prompt = _META_PROMPT + "\n\n" + "\n".join(context_lines)
        return await self._llm_service.generate_answer(full_prompt)
