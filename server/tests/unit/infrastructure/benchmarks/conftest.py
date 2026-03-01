"""Shared fixtures and helpers for RAG pipeline benchmarks.

All benchmarks use the 5 PDF test documents in ``tests/docs/`` and produce
CSV files in ``server/benchmark_results/``.
"""

from __future__ import annotations

import csv
import os
import re
import statistics
from math import log2, sqrt
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_TESTS_DIR = Path(__file__).resolve().parents[3]  # server/tests
DOCS_DIR = _TESTS_DIR / "docs"
SERVER_DIR = _TESTS_DIR.parent  # server/
BENCHMARK_OUTPUT_DIR = SERVER_DIR / "benchmark_results"


# ---------------------------------------------------------------------------
# CSV writer
# ---------------------------------------------------------------------------

def write_benchmark_csv(
    filename: str,
    rows: list[dict[str, Any]],
    *,
    output_dir: Path = BENCHMARK_OUTPUT_DIR,
) -> Path:
    """Write benchmark rows to a semicolon-separated CSV.

    Each row dict must have keys:
        Benchmark, Metric, Baseline, Optimized, Improvement (%), Winner
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename

    fieldnames = ["Benchmark", "Metric", "Baseline", "Optimized", "Improvement (%)", "Winner"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

        # Summary line
        wins_opt = sum(1 for r in rows if r["Winner"] == "optimized")
        wins_base = sum(1 for r in rows if r["Winner"] == "baseline")
        ties = sum(1 for r in rows if r["Winner"] == "tie")
        fh.write(f"\nSUMMARY;Optimized wins: {wins_opt};Baseline wins: {wins_base};Ties: {ties};;\n")

    return filepath


def _improvement_pct(baseline: float, optimized: float) -> float:
    if baseline == 0.0:
        if optimized == 0.0:
            return 0.0
        return 100.0
    return round((optimized - baseline) / abs(baseline) * 100, 2)


def _winner(baseline: float, optimized: float, higher_is_better: bool = True) -> str:
    if abs(baseline - optimized) < 1e-9:
        return "tie"
    if higher_is_better:
        return "optimized" if optimized > baseline else "baseline"
    return "optimized" if optimized < baseline else "baseline"


def make_row(
    benchmark_name: str,
    query_label: str,
    metric_name: str,
    baseline: float,
    optimized: float,
    higher_is_better: bool = True,
) -> dict[str, Any]:
    return {
        "Benchmark": benchmark_name,
        "Metric": f"[{query_label}] {metric_name}",
        "Baseline": round(baseline, 4),
        "Optimized": round(optimized, 4),
        "Improvement (%)": _improvement_pct(baseline, optimized),
        "Winner": _winner(baseline, optimized, higher_is_better),
    }


# ---------------------------------------------------------------------------
# Chunking quality metrics
# ---------------------------------------------------------------------------

_SENTENCE_END_RE = re.compile(r"[.!?;:]\s*$")


def boundary_coherence(chunks: list[str]) -> float:
    """Fraction of chunks that end at a sentence boundary."""
    if not chunks:
        return 0.0
    good = sum(1 for c in chunks if _SENTENCE_END_RE.search(c.strip()))
    return good / len(chunks)


def chunk_size_std(chunks: list[str]) -> float:
    """Standard deviation of chunk lengths (lower = more uniform)."""
    if len(chunks) < 2:
        return 0.0
    lengths = [len(c) for c in chunks]
    return statistics.stdev(lengths)


def empty_chunk_count(chunks: list[str]) -> int:
    return sum(1 for c in chunks if not c.strip())


def single_word_chunk_count(chunks: list[str]) -> int:
    return sum(1 for c in chunks if len(c.strip().split()) <= 1 and c.strip())


def information_density(chunks: list[str]) -> float:
    """Average ratio of unique words to total words per chunk."""
    if not chunks:
        return 0.0
    densities: list[float] = []
    for chunk in chunks:
        words = chunk.lower().split()
        if not words:
            continue
        densities.append(len(set(words)) / len(words))
    return statistics.mean(densities) if densities else 0.0


# ---------------------------------------------------------------------------
# Retrieval metrics
# ---------------------------------------------------------------------------

def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int = 5) -> float:
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    return sum(1 for rid in top_k if rid in relevant_ids) / len(top_k)


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int = 5) -> float:
    if not relevant_ids:
        return 0.0
    top_k = retrieved_ids[:k]
    return sum(1 for rid in top_k if rid in relevant_ids) / len(relevant_ids)


def mrr(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    for i, rid in enumerate(retrieved_ids, 1):
        if rid in relevant_ids:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int = 5) -> float:
    top_k = retrieved_ids[:k]
    dcg = 0.0
    for i, rid in enumerate(top_k, 1):
        rel = 1.0 if rid in relevant_ids else 0.0
        dcg += rel / log2(i + 1)
    ideal_hits = min(len(relevant_ids), k)
    idcg = sum(1.0 / log2(i + 1) for i in range(1, ideal_hits + 1))
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a))
    nb = sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def context_diversity(embeddings: list[list[float]]) -> float:
    """Average pairwise cosine distance (1 - sim) among embeddings."""
    n = len(embeddings)
    if n < 2:
        return 1.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1.0 - cosine_similarity(embeddings[i], embeddings[j])
            count += 1
    return total / count if count else 1.0


def context_redundancy(embeddings: list[list[float]]) -> float:
    return 1.0 - context_diversity(embeddings)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_has_test_pdfs = DOCS_DIR.is_dir() and bool(list(DOCS_DIR.glob("*.pdf")))


@pytest.fixture(scope="session")
def pdf_texts() -> dict[str, str]:
    """Extract text from all test PDFs (session-scoped for performance).

    Skips the entire benchmark session when ``tests/docs/`` is missing or
    contains no PDF files.
    """
    if not _has_test_pdfs:
        pytest.skip(
            f"Benchmark test PDFs not found in {DOCS_DIR}. "
            "Place PDF files in server/tests/docs/ to enable benchmarks."
        )

    from raggae.infrastructure.services.multiformat_document_text_extractor import (
        MultiFormatDocumentTextExtractor,
    )
    import asyncio

    extractor = MultiFormatDocumentTextExtractor()
    texts: dict[str, str] = {}

    async def _extract_all() -> None:
        for pdf_file in sorted(DOCS_DIR.glob("*.pdf")):
            raw = pdf_file.read_bytes()
            text = await extractor.extract_text(pdf_file.name, raw, "application/pdf")
            texts[pdf_file.name] = text

    asyncio.run(_extract_all())
    return texts


@pytest.fixture(scope="session")
def sanitized_texts(pdf_texts: dict[str, str]) -> dict[str, str]:
    """Sanitize extracted texts."""
    from raggae.infrastructure.services.simple_text_sanitizer_service import (
        SimpleTextSanitizerService,
    )
    import asyncio

    sanitizer = SimpleTextSanitizerService()
    result: dict[str, str] = {}

    async def _sanitize_all() -> None:
        for name, text in pdf_texts.items():
            result[name] = await sanitizer.sanitize_text(text)

    asyncio.run(_sanitize_all())
    return result


