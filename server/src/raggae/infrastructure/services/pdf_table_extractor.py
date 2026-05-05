import logging
from dataclasses import dataclass, field
from io import BytesIO

from raggae.domain.exceptions.document_exceptions import DocumentExtractionError

logger = logging.getLogger(__name__)


@dataclass
class TableData:
    rows: list[list[str]]
    page_number: int
    table_index: int
    bbox: tuple[float, float, float, float] | None = field(default=None, repr=False)

    def to_markdown(self) -> str:
        if not self.rows:
            return ""
        header = self.rows[0]
        lines = [
            "| " + " | ".join(cell if cell else "—" for cell in header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]
        for row in self.rows[1:]:
            padded = (list(row) + [""] * len(header))[: len(header)]
            lines.append("| " + " | ".join(cell if cell else "—" for cell in padded) + " |")
        return "\n".join(lines)

    def to_chunk(self) -> str:
        return f"[[PAGE:{self.page_number}]] [TABLE:{self.table_index}]\n\n{self.to_markdown()}"


class PdfTableExtractor:
    """Extract structured tables from PDF pages using pdfplumber's vector-line detection."""

    def extract_tables(self, content: bytes) -> list[TableData]:
        try:
            import pdfplumber
        except ModuleNotFoundError as exc:  # pragma: no cover
            raise DocumentExtractionError("pdfplumber is required for PDF table extraction") from exc

        try:
            result: list[TableData] = []
            with pdfplumber.open(BytesIO(content)) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    for table_idx, found_table in enumerate(page.find_tables(), start=1):
                        raw = found_table.extract()
                        if raw is None:
                            continue
                        rows = [[str(cell) if cell is not None else "" for cell in row] for row in raw]
                        non_empty = [r for r in rows if any(c.strip() for c in r)]
                        if len(non_empty) < 2:
                            continue
                        result.append(
                            TableData(
                                rows=non_empty,
                                page_number=page_num,
                                table_index=table_idx,
                                bbox=found_table.bbox,
                            )
                        )
            return result
        except DocumentExtractionError:
            raise
        except Exception as exc:  # pragma: no cover
            raise DocumentExtractionError(f"Failed to extract PDF tables: {exc}") from exc
