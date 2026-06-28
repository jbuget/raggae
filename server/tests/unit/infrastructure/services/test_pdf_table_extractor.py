import sys
import types

import pytest

from raggae.infrastructure.services.pdf_table_extractor import PdfTableExtractor, TableData


def _make_fake_pdfplumber(pages_tables: list[list[list[list[str | None]]]]) -> types.ModuleType:
    """Build a fake pdfplumber module.

    pages_tables[page_idx] = list of tables on that page
    Each table = list of rows; each row = list of cell strings (None → empty cell).
    """

    class FakeFoundTable:
        def __init__(self, data: list[list[str | None]], bbox: tuple[float, float, float, float]) -> None:
            self._data = data
            self.bbox = bbox

        def extract(self) -> list[list[str | None]]:
            return self._data

    class FakePage:
        def __init__(self, tables: list[list[list[str | None]]]) -> None:
            self._tables = tables

        def find_tables(self) -> list[FakeFoundTable]:
            return [
                FakeFoundTable(t, (10.0 + i * 50, 20.0, 200.0, 100.0 + i * 50))
                for i, t in enumerate(self._tables)
            ]

    class FakePdf:
        def __init__(self, pages: list[FakePage]) -> None:
            self.pages = pages

        def __enter__(self) -> "FakePdf":
            return self

        def __exit__(self, *args: object) -> None:
            pass

    _pages = [FakePage(tables) for tables in pages_tables]

    fake = types.ModuleType("pdfplumber")
    fake.open = lambda buf: FakePdf(_pages)  # type: ignore[attr-defined]
    return fake


class TestTableData:
    def test_to_markdown_uses_first_row_as_headers(self) -> None:
        # Given
        table = TableData(
            rows=[["Produit", "Prix"], ["Widget A", "48 €"]],
            page_number=1,
            table_index=1,
        )

        # When
        md = table.to_markdown()

        # Then
        assert "| Produit | Prix |" in md
        assert "|" in md.split("\n")[1]  # separator line

    def test_to_markdown_renders_empty_cell_as_dash(self) -> None:
        # Given
        table = TableData(
            rows=[["A", "B"], ["val", ""]],
            page_number=1,
            table_index=1,
        )

        # When
        md = table.to_markdown()

        # Then
        assert "| val | — |" in md

    def test_to_markdown_includes_separator_line(self) -> None:
        # Given
        table = TableData(
            rows=[["Col1", "Col2"], ["v1", "v2"]],
            page_number=1,
            table_index=1,
        )

        # When
        lines = table.to_markdown().split("\n")

        # Then
        assert lines[1] == "| --- | --- |"

    def test_to_chunk_contains_page_and_table_markers(self) -> None:
        # Given
        table = TableData(
            rows=[["H1"], ["v1"]],
            page_number=3,
            table_index=2,
        )

        # When
        chunk = table.to_chunk()

        # Then
        assert chunk.startswith("[[PAGE:3]] [TABLE:2]")

    def test_to_chunk_contains_markdown_table(self) -> None:
        # Given
        table = TableData(
            rows=[["Produit", "Stock"], ["Widget A", "14"]],
            page_number=1,
            table_index=1,
        )

        # When
        chunk = table.to_chunk()

        # Then
        assert "| Produit | Stock |" in chunk
        assert "| Widget A | 14 |" in chunk


class TestPdfTableExtractor:
    @pytest.fixture
    def extractor(self) -> PdfTableExtractor:
        return PdfTableExtractor()

    async def test_extract_tables_pdf_without_tables_returns_empty_list(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — one page, no tables
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then
        assert result == []

    async def test_extract_tables_two_tables_same_page_have_distinct_table_index(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — one page with two tables
        table_a = [["H1", "H2"], ["v1", "v2"]]
        table_b = [["X", "Y"], ["a", "b"]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[table_a, table_b]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then
        assert len(result) == 2
        assert result[0].page_number == result[1].page_number == 1
        assert result[0].table_index == 1
        assert result[1].table_index == 2

    async def test_extract_tables_table_on_page_3_has_correct_page_number(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — three pages; table only on page 3
        table = [["Label", "Value"], ["Event", "2024-01-15"]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[], [], [table]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then
        assert len(result) == 1
        assert result[0].page_number == 3
        assert result[0].table_index == 1

    async def test_extract_tables_none_cell_becomes_empty_string(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — table with a None cell (pdfplumber returns None for merged/empty cells)
        table: list[list[str | None]] = [["A", "B"], ["val", None]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[table]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then — TableData rows contain strings, not None
        assert result[0].rows[1][1] == ""

    async def test_extract_tables_table_with_only_headers_is_ignored(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — table with only one row (headers, no data)
        table = [["H1", "H2"]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[table]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then
        assert result == []

    async def test_extract_tables_empty_rows_are_ignored(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given — table with empty rows interspersed
        table: list[list[str | None]] = [["H1", "H2"], [None, None], ["v1", "v2"]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[table]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then — empty row filtered out, 2 rows remain (header + data)
        assert len(result[0].rows) == 2

    async def test_extract_tables_exposes_bbox(
        self,
        extractor: PdfTableExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        table = [["H1"], ["v1"]]
        monkeypatch.setitem(sys.modules, "pdfplumber", _make_fake_pdfplumber([[table]]))

        # When
        result = extractor.extract_tables(b"%PDF")

        # Then — bbox is set (used by MultiFormatDocumentTextExtractor for text exclusion)
        assert result[0].bbox is not None
        assert len(result[0].bbox) == 4
