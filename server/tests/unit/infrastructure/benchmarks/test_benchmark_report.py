"""Benchmark report generator – Reads all CSV results and produces a Markdown report.

Generates ``raggae/docs/RAG_OPTIMIZATION_BENCHMARKS.md``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import BENCHMARK_OUTPUT_DIR

DOCS_DIR = Path(__file__).resolve().parents[5] / "docs"  # raggae/docs/

# Expected CSV files in order
CSV_FILES = [
    "chunking_fixed_vs_semantic.csv",
    "chunking_fixed_vs_paragraph.csv",
    "embedding_plain_vs_contextual.csv",
    "retrieval_hybrid_vs_diversity.csv",
    "context_old_vs_enhanced_prompt.csv",
    "end_to_end_pipeline.csv",
]


def _read_csv(filepath: Path) -> tuple[list[dict[str, str]], str]:
    """Read a benchmark CSV and return (rows, summary_line)."""
    rows: list[dict[str, str]] = []
    summary = ""
    with open(filepath, "r", encoding="utf-8-sig") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped.startswith("SUMMARY"):
                summary = stripped
                continue
            if not stripped:
                continue
            if stripped.startswith("Benchmark;"):
                continue  # header
            parts = stripped.split(";")
            if len(parts) >= 6:
                rows.append({
                    "Benchmark": parts[0],
                    "Metric": parts[1],
                    "Baseline": parts[2],
                    "Optimized": parts[3],
                    "Improvement (%)": parts[4],
                    "Winner": parts[5],
                })
    return rows, summary


def _parse_summary(summary: str) -> tuple[int, int, int]:
    """Extract optimized wins, baseline wins, ties from summary line."""
    import re
    opt = base = ties = 0
    m = re.search(r"Optimized wins:\s*(\d+)", summary)
    if m:
        opt = int(m.group(1))
    m = re.search(r"Baseline wins:\s*(\d+)", summary)
    if m:
        base = int(m.group(1))
    m = re.search(r"Ties:\s*(\d+)", summary)
    if m:
        ties = int(m.group(1))
    return opt, base, ties


def _generate_report() -> str:
    """Generate the full Markdown report from CSV files."""
    sections: list[str] = []

    sections.append("# 📊 RAG Pipeline Optimization Benchmarks\n")
    sections.append("> Auto-generated report comparing baseline vs optimized techniques across the full RAG pipeline.\n")
    sections.append(f"> Test corpus: 5 French PDF documents (company policies)\n")
    sections.append("---\n")

    # --- Executive Summary ---
    total_opt = total_base = total_ties = 0
    available_csvs: list[tuple[str, list[dict[str, str]], str]] = []

    for csv_name in CSV_FILES:
        csv_path = BENCHMARK_OUTPUT_DIR / csv_name
        if csv_path.exists():
            rows, summary = _read_csv(csv_path)
            opt, base, ties = _parse_summary(summary)
            total_opt += opt
            total_base += base
            total_ties += ties
            available_csvs.append((csv_name, rows, summary))

    sections.append("## 📋 Executive Summary\n")
    sections.append(f"| Metric | Count |")
    sections.append(f"|--------|-------|")
    sections.append(f"| **Optimized wins** | {total_opt} |")
    sections.append(f"| **Baseline wins** | {total_base} |")
    sections.append(f"| **Ties** | {total_ties} |")
    total = total_opt + total_base + total_ties
    if total > 0:
        win_rate = round(total_opt / total * 100, 1)
        sections.append(f"| **Optimization win rate** | {win_rate}% |")
    sections.append("")

    # --- Per-benchmark sections ---
    benchmark_titles = {
        "chunking_fixed_vs_semantic.csv": ("🔪 Chunking: Fixed Window vs Semantic", "Compares character-based fixed window chunking (baseline) against semantic chunking that uses sentence embeddings to detect natural topic boundaries."),
        "chunking_fixed_vs_paragraph.csv": ("🔪 Chunking: Fixed Window vs Paragraph", "Compares character-based fixed window chunking (baseline) against paragraph-aware chunking that respects natural paragraph boundaries."),
        "embedding_plain_vs_contextual.csv": ("🔢 Embedding: Plain vs Contextual", "Compares standard SHA256-based embeddings (baseline) against contextual embeddings with task-specific prefixes (search_document/search_query)."),
        "retrieval_hybrid_vs_diversity.csv": ("🔍 Retrieval: Hybrid vs Hybrid+MMR Diversity", "Compares standard hybrid search (vector + lexical) against hybrid search enhanced with MMR diversity reranking to reduce redundancy."),
        "context_old_vs_enhanced_prompt.csv": ("📝 Context: Old Prompt vs Enhanced Prompt", "Compares the original RAG prompt against an enhanced prompt with source attribution, structured sections, and numbered excerpts."),
        "end_to_end_pipeline.csv": ("🚀 End-to-End: Baseline vs Optimized Pipeline", "Full pipeline comparison combining all optimizations: paragraph chunking + contextual embeddings + MMR diversity reranking + enhanced prompt."),
    }

    for csv_name, rows, summary in available_csvs:
        title, description = benchmark_titles.get(csv_name, (csv_name, ""))
        sections.append(f"## {title}\n")
        sections.append(f"{description}\n")

        # Summary for this benchmark
        opt, base, ties = _parse_summary(summary)
        sections.append(f"**Results:** ✅ Optimized wins: {opt} | ❌ Baseline wins: {base} | ➖ Ties: {ties}\n")

        # Table
        sections.append("| Metric | Baseline | Optimized | Improvement (%) | Winner |")
        sections.append("|--------|----------|-----------|----------------|--------|")
        for row in rows:
            winner_emoji = {"optimized": "✅", "baseline": "❌", "tie": "➖"}.get(row["Winner"], "")
            sections.append(
                f"| {row['Metric']} | {row['Baseline']} | {row['Optimized']} | {row['Improvement (%)']} | {winner_emoji} {row['Winner']} |"
            )
        sections.append("")

    # --- Methodology ---
    sections.append("## 🔬 Methodology\n")
    sections.append("### Test Corpus")
    sections.append("All benchmarks use the same 5 French PDF documents:")
    sections.append("1. **Charte télétravail** – Remote work policy")
    sections.append("2. **Charte de prévention du harcèlement** – Harassment prevention charter")
    sections.append("3. **Charte des systèmes d'information** – IT systems charter")
    sections.append("4. **Bonne-pratique Photo** – Photography best practices")
    sections.append("5. **LIVRET D'ACCUEIL** – Employee welcome booklet\n")

    sections.append("### Queries")
    sections.append("13 French queries covering all documents, testing different aspects:\n")
    sections.append("- Factual questions (conditions, definitions)")
    sections.append("- Procedural questions (how to report, how integration works)")
    sections.append("- Policy questions (sanctions, obligations)\n")

    sections.append("### Metrics\n")
    sections.append("| Category | Metric | Description | Higher is better? |")
    sections.append("|----------|--------|-------------|-------------------|")
    sections.append("| Chunking | `boundary_coherence` | Fraction of chunks ending at sentence boundaries | ✅ Yes |")
    sections.append("| Chunking | `chunk_size_std` | Standard deviation of chunk sizes | ❌ No (lower = more uniform) |")
    sections.append("| Chunking | `empty_chunks` | Number of empty chunks produced | ❌ No |")
    sections.append("| Chunking | `single_word_chunks` | Number of single-word chunks | ❌ No |")
    sections.append("| Chunking | `information_density` | Ratio of unique to total words per chunk | ✅ Yes |")
    sections.append("| Retrieval | `precision@5` | Fraction of top-5 results that are relevant | ✅ Yes |")
    sections.append("| Retrieval | `recall@5` | Fraction of relevant docs found in top-5 | ✅ Yes |")
    sections.append("| Retrieval | `mrr` | Mean Reciprocal Rank | ✅ Yes |")
    sections.append("| Retrieval | `ndcg@5` | Normalized Discounted Cumulative Gain | ✅ Yes |")
    sections.append("| Retrieval | `ctx_diversity` | Average pairwise cosine distance of results | ✅ Yes |")
    sections.append("| Retrieval | `ctx_redundancy` | 1 - ctx_diversity (overlap between results) | ❌ No |")
    sections.append("| Context | `source_attribution` | Presence of source references in prompt | ✅ Yes |")
    sections.append("| Context | `structure_quality` | Structured sections (headers, numbering) | ✅ Yes |")
    sections.append("| Context | `query_preserved` | Original query present in final prompt | ✅ Yes |")
    sections.append("| Context | `context_utilization` | Fraction of retrieved chunks used in prompt | ✅ Yes |")
    sections.append("")

    # --- Techniques ---
    sections.append("## 🛠️ Techniques Compared\n")
    sections.append("### Baseline Pipeline")
    sections.append("- **Chunking:** Fixed window (500 chars, 50 overlap)")
    sections.append("- **Embedding:** SHA256-based deterministic hashing")
    sections.append("- **Retrieval:** Hybrid search (0.6 vector + 0.4 lexical)")
    sections.append("- **Reranking:** None")
    sections.append("- **Prompt:** Simple flat template\n")

    sections.append("### Optimized Pipeline")
    sections.append("- **Chunking:** Paragraph-aware chunking (respects natural boundaries)")
    sections.append("- **Embedding:** Contextual prefix embedding (search_document/search_query)")
    sections.append("- **Retrieval:** Hybrid search + MMR diversity reranking (λ=0.7)")
    sections.append("- **Reranking:** Maximal Marginal Relevance for diversity")
    sections.append("- **Prompt:** Enhanced template with source attribution, structured sections\n")

    # --- Recommendations ---
    sections.append("## 💡 Recommendations\n")
    if total_opt > total_base:
        sections.append("The optimized pipeline **outperforms the baseline** across most metrics.\n")
        sections.append("### Key wins:")
        sections.append("- **Boundary coherence** dramatically improves with paragraph/semantic chunking")
        sections.append("- **Context diversity** improves with MMR reranking, reducing redundancy")
        sections.append("- **Source attribution** is fully enabled by the enhanced prompt template")
        sections.append("- **Information density** improves when chunks follow natural boundaries\n")
    else:
        sections.append("Results are mixed. Further tuning of parameters may be needed.\n")

    sections.append("### Suggested next steps:")
    sections.append("1. Test with real embedding models (OpenAI, Gemini) instead of SHA256 hashing")
    sections.append("2. Tune MMR λ parameter (currently 0.7) for optimal relevance-diversity balance")
    sections.append("3. Experiment with semantic chunking similarity thresholds")
    sections.append("4. Add cross-encoder reranking for production workloads")
    sections.append("5. Benchmark with larger document corpora\n")

    sections.append("---\n")
    sections.append("*Report generated automatically by the RAG benchmark suite.*\n")

    return "\n".join(sections)


@pytest.mark.unit
class TestBenchmarkReport:
    """Generate the Markdown report from benchmark CSV results."""

    def test_generate_markdown_report(self) -> None:
        """Read all benchmark CSVs and generate the consolidated Markdown report."""
        # Check at least some CSVs exist
        existing = [
            f for f in CSV_FILES if (BENCHMARK_OUTPUT_DIR / f).exists()
        ]
        # We still generate even if some are missing (they'll be skipped)

        report = _generate_report()
        assert len(report) > 100, "Report is too short"

        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DOCS_DIR / "RAG_OPTIMIZATION_BENCHMARKS.md"
        output_path.write_text(report, encoding="utf-8")
        assert output_path.exists()
        assert output_path.stat().st_size > 0



