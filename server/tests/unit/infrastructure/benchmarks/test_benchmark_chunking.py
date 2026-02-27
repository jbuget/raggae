"""Benchmark: Chunking strategies – Fixed Window (baseline) vs Semantic/Paragraph (optimized).

Compares chunk quality across all test PDFs and writes results to CSV.
"""

from __future__ import annotations

import pytest

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.in_memory_embedding_service import InMemoryEmbeddingService
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)
from raggae.infrastructure.services.semantic_text_chunker_service import (
    SemanticTextChunkerService,
)
from raggae.infrastructure.services.simple_text_chunker_service import SimpleTextChunkerService

from .conftest import (
    boundary_coherence,
    chunk_size_std,
    empty_chunk_count,
    information_density,
    make_row,
    single_word_chunk_count,
    write_benchmark_csv,
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _label(filename: str) -> str:
    """Short label for CSV output from filename."""
    return filename[:20]


async def _chunk_with_strategy(
    text: str,
    strategy: str,
) -> list[str]:
    """Chunk text using the specified strategy."""
    if strategy == "fixed_window":
        chunker = SimpleTextChunkerService(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        return await chunker.chunk_text(text, ChunkingStrategy.FIXED_WINDOW)

    if strategy == "paragraph":
        chunker_p = ParagraphTextChunkerService(chunk_size=CHUNK_SIZE)
        return await chunker_p.chunk_text(text, ChunkingStrategy.PARAGRAPH)

    if strategy == "semantic":
        embedding_svc = InMemoryEmbeddingService(dimension=16)
        chunker_s = SemanticTextChunkerService(
            embedding_service=embedding_svc,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            similarity_threshold=0.65,
        )
        return await chunker_s.chunk_text(text, ChunkingStrategy.SEMANTIC)

    raise ValueError(f"Unknown strategy: {strategy}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBenchmarkChunkingFixedVsSemantic:
    """Compare Fixed Window (baseline) vs Semantic chunking (optimized)."""

    @pytest.mark.asyncio
    async def test_fixed_vs_semantic_all_docs(
        self, sanitized_texts: dict[str, str]
    ) -> None:
        assert sanitized_texts, "No test documents found"

        rows: list[dict] = []
        benchmark_name = "Chunking: Fixed Window vs Semantic"

        for filename, text in sanitized_texts.items():
            label = _label(filename)

            baseline_chunks = await _chunk_with_strategy(text, "fixed_window")
            optimized_chunks = await _chunk_with_strategy(text, "semantic")

            # boundary_coherence – higher is better
            bc_base = boundary_coherence(baseline_chunks)
            bc_opt = boundary_coherence(optimized_chunks)
            rows.append(make_row(benchmark_name, label, "boundary_coherence", bc_base, bc_opt))

            # chunk_size_std – lower is better (more uniform)
            std_base = chunk_size_std(baseline_chunks)
            std_opt = chunk_size_std(optimized_chunks)
            rows.append(
                make_row(benchmark_name, label, "chunk_size_std", std_base, std_opt, higher_is_better=False)
            )

            # empty_chunks – lower is better
            ec_base = float(empty_chunk_count(baseline_chunks))
            ec_opt = float(empty_chunk_count(optimized_chunks))
            rows.append(
                make_row(benchmark_name, label, "empty_chunks", ec_base, ec_opt, higher_is_better=False)
            )

            # single_word_chunks – lower is better
            sw_base = float(single_word_chunk_count(baseline_chunks))
            sw_opt = float(single_word_chunk_count(optimized_chunks))
            rows.append(
                make_row(benchmark_name, label, "single_word_chunks", sw_base, sw_opt, higher_is_better=False)
            )

            # information_density – higher is better
            id_base = information_density(baseline_chunks)
            id_opt = information_density(optimized_chunks)
            rows.append(make_row(benchmark_name, label, "information_density", id_base, id_opt))

        filepath = write_benchmark_csv("chunking_fixed_vs_semantic.csv", rows)
        assert filepath.exists()
        assert len(rows) > 0


@pytest.mark.unit
class TestBenchmarkChunkingFixedVsParagraph:
    """Compare Fixed Window (baseline) vs Paragraph chunking (optimized)."""

    @pytest.mark.asyncio
    async def test_fixed_vs_paragraph_all_docs(
        self, sanitized_texts: dict[str, str]
    ) -> None:
        assert sanitized_texts, "No test documents found"

        rows: list[dict] = []
        benchmark_name = "Chunking: Fixed Window vs Paragraph"

        for filename, text in sanitized_texts.items():
            label = _label(filename)

            baseline_chunks = await _chunk_with_strategy(text, "fixed_window")
            optimized_chunks = await _chunk_with_strategy(text, "paragraph")

            bc_base = boundary_coherence(baseline_chunks)
            bc_opt = boundary_coherence(optimized_chunks)
            rows.append(make_row(benchmark_name, label, "boundary_coherence", bc_base, bc_opt))

            std_base = chunk_size_std(baseline_chunks)
            std_opt = chunk_size_std(optimized_chunks)
            rows.append(
                make_row(benchmark_name, label, "chunk_size_std", std_base, std_opt, higher_is_better=False)
            )

            ec_base = float(empty_chunk_count(baseline_chunks))
            ec_opt = float(empty_chunk_count(optimized_chunks))
            rows.append(
                make_row(benchmark_name, label, "empty_chunks", ec_base, ec_opt, higher_is_better=False)
            )

            sw_base = float(single_word_chunk_count(baseline_chunks))
            sw_opt = float(single_word_chunk_count(optimized_chunks))
            rows.append(
                make_row(benchmark_name, label, "single_word_chunks", sw_base, sw_opt, higher_is_better=False)
            )

            id_base = information_density(baseline_chunks)
            id_opt = information_density(optimized_chunks)
            rows.append(make_row(benchmark_name, label, "information_density", id_base, id_opt))

        filepath = write_benchmark_csv("chunking_fixed_vs_paragraph.csv", rows)
        assert filepath.exists()
        assert len(rows) > 0


