import re
from dataclasses import dataclass

_SLIDE_MARKER_RE = re.compile(r"\[SLIDE:(\d+)\]")
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class SlideChunk:
    content: str
    chunk_index: int
    slide_number: int
    slide_title: str


class SlideChunker:
    """Split PPTX-extracted text (with [SLIDE:N] markers) into one chunk per slide."""

    def chunk(self, text: str) -> list[SlideChunk]:
        if not text.strip():
            return []

        parts = _SLIDE_MARKER_RE.split(text)
        # split result: [pre, slide_num, body, slide_num, body, ...]
        # parts[0] is text before the first marker (discarded if empty)
        result: list[SlideChunk] = []
        chunk_index = 0

        i = 1
        while i < len(parts) - 1:
            slide_number = int(parts[i])
            body = parts[i + 1]
            title_match = _TITLE_RE.search(body)
            slide_title = title_match.group(1).strip() if title_match else ""
            result.append(
                SlideChunk(
                    content=body.strip(),
                    chunk_index=chunk_index,
                    slide_number=slide_number,
                    slide_title=slide_title,
                )
            )
            chunk_index += 1
            i += 2

        return result
