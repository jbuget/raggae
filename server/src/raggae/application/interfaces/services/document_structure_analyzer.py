from typing import Protocol

from raggae.application.dto.document_structure_analysis_dto import DocumentStructureAnalysisDTO


class DocumentStructureAnalyzer(Protocol):
    """Interface for deterministic text-structure analysis."""

    async def analyze_text(self, text: str) -> DocumentStructureAnalysisDTO: ...
