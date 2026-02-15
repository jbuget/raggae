import re

from raggae.application.dto.document_structure_analysis_dto import DocumentStructureAnalysisDTO

_ATX_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S")
_NUMBERED_HEADING_RE = re.compile(r"^\s*\d+(?:\.\d+)*[.)]?\s+\S")
_UPPER_HEADING_RE = re.compile(r"^[A-Z0-9][A-Z0-9\s\-:]{4,}$")


class HeuristicDocumentStructureAnalyzer:
    """Simple deterministic analyzer based on textual structure signals."""

    async def analyze_text(self, text: str) -> DocumentStructureAnalysisDTO:
        normalized = text.strip()
        if not normalized:
            return DocumentStructureAnalysisDTO(
                has_headings=False,
                paragraph_count=0,
                average_paragraph_length=0,
            )

        paragraphs = [part.strip() for part in normalized.split("\n\n") if part.strip()]
        paragraph_count = len(paragraphs)
        average_paragraph_length = (
            sum(len(paragraph) for paragraph in paragraphs) // paragraph_count
            if paragraph_count > 0
            else 0
        )

        has_headings = False
        for line in normalized.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if (
                _ATX_HEADING_RE.match(stripped)
                or _NUMBERED_HEADING_RE.match(stripped)
                or _UPPER_HEADING_RE.match(stripped)
            ):
                has_headings = True
                break

        return DocumentStructureAnalysisDTO(
            has_headings=has_headings,
            paragraph_count=paragraph_count,
            average_paragraph_length=average_paragraph_length,
        )
