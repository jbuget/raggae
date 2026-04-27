from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_SHEET_PREFIX = "[SHEET:"
_HEADERS_PREFIX = "[HEADERS]:"
_ROW_PREFIX = "[ROW:"


class TabularTextChunkerService:
    """Chunk tabular structured text into one Markdown table chunk per data row."""

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.TABULAR,
        embedding_service: EmbeddingService | None = None,
    ) -> list[str]:
        _ = (strategy, embedding_service)
        return self._parse_chunks(text)

    def _parse_chunks(self, text: str) -> list[str]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        chunks: list[str] = []
        current_sheet: str | None = None
        current_headers: list[str] | None = None

        for line in lines:
            if line.startswith(_SHEET_PREFIX) and line.endswith("]"):
                current_sheet = line[len(_SHEET_PREFIX) : -1]
            elif line.startswith(_HEADERS_PREFIX):
                current_headers = line[len(_HEADERS_PREFIX) :].split("|")
            elif line.startswith(_ROW_PREFIX):
                if current_headers is None:
                    continue
                colon_idx = line.index("]:")
                row_num = line[len(_ROW_PREFIX) : colon_idx]
                row_values = line[colon_idx + 2 :].split("|")
                chunks.append(self._build_chunk(current_sheet, row_num, current_headers, row_values))

        return chunks

    def _build_chunk(
        self,
        sheet: str | None,
        row_num: str,
        headers: list[str],
        values: list[str],
    ) -> str:
        marker = f"[SHEET:{sheet}] [ROW:{row_num}]" if sheet is not None else f"[ROW:{row_num}]"
        header_row = "| " + " | ".join(h.replace("&#124;", "|") for h in headers) + " |"
        sep_row = "| " + " | ".join("---" for _ in headers) + " |"
        padded = (list(values) + [""] * len(headers))[: len(headers)]
        data_row = "| " + " | ".join(v.replace("&#124;", "|") for v in padded) + " |"
        return f"{marker}\n{header_row}\n{sep_row}\n{data_row}"
