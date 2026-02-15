class StaticChatSecurityPolicy:
    """Static, deterministic security policy enforced outside the LLM prompt."""

    def is_disallowed_user_message(self, message: str) -> bool:
        normalized = message.lower()
        return any(pattern in normalized for pattern in self._EXFILTRATION_PATTERNS)

    def sanitize_model_answer(self, answer: str) -> str:
        normalized = answer.lower()
        if any(marker in normalized for marker in self._LEAK_MARKERS):
            return (
                "I cannot disclose system or internal instructions. "
                "Please ask a question related to your project content."
            )
        return answer

    _EXFILTRATION_PATTERNS = (
        "prompt system",
        "system prompt",
        "instructions internes",
        "internal instructions",
        "affiche le prompt",
        "show the prompt",
        "reveal the prompt",
        "ignore previous instructions",
        "developer prompt",
        "admin prompt",
    )

    _LEAK_MARKERS = (
        "instructions système plateforme raggae",
        "system prompt",
        "internal instructions",
        "developer prompt",
        "admin prompt",
    )
