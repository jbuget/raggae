from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentStructureAnalysisDTO:
    """Deterministic structural signals extracted from sanitized text."""

    has_headings: bool
    paragraph_count: int
    average_paragraph_length: int
