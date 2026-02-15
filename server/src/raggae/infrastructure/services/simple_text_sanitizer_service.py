import re


class SimpleTextSanitizerService:
    """Safe text sanitizer preserving semantic structure."""

    async def sanitize_text(self, text: str) -> str:
        normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
        without_controls = "".join(
            char
            for char in normalized
            if char == "\n" or char == "\t" or ord(char) >= 32
        )
        stripped_lines = "\n".join(line.rstrip() for line in without_controls.split("\n"))
        collapsed_newlines = re.sub(r"\n{3,}", "\n\n", stripped_lines)
        return collapsed_newlines.strip()
