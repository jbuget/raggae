"""Benchmark: Embedding strategies – Plain (baseline) vs Contextual prefix (optimized).

Uses the test PDFs chunked with a consistent strategy, then compares retrieval
quality with plain vs contextual embeddings.
"""

from __future__ import annotations

from typing import Any

import pytest

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.contextual_embedding_service import (
    ContextualEmbeddingService,
)
from raggae.infrastructure.services.in_memory_embedding_service import InMemoryEmbeddingService
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)

from .conftest import (
    cosine_similarity,
    make_row,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    write_benchmark_csv,
)

CHUNK_SIZE = 500

# French queries + the expected source document filename substring
QUERIES: list[dict[str, Any]] = [
    {
        "query": "Quelles sont les conditions pour bénéficier du télétravail ?",
        "expected_doc": "Charte télétravail",
    },
    {
        "query": "Qui peut bénéficier du télétravail dans l'entreprise ?",
        "expected_doc": "Charte télétravail",
    },
    {
        "query": "Quelles sont les obligations de l'employeur en matière de télétravail ?",
        "expected_doc": "Charte télétravail",
    },
    {
        "query": "Comment signaler un cas de harcèlement au travail ?",
        "expected_doc": "harcèlement",
    },
    {
        "query": "Quelles sont les sanctions prévues en cas de harcèlement ?",
        "expected_doc": "harcèlement",
    },
    {
        "query": "Quelle est la définition du harcèlement moral et sexuel ?",
        "expected_doc": "harcèlement",
    },
    {
        "query": "Quelles sont les règles d'utilisation des systèmes d'information ?",
        "expected_doc": "systèmes d'information",
    },
    {
        "query": "Quelles sont les obligations en matière de sécurité informatique ?",
        "expected_doc": "systèmes d'information",
    },
    {
        "query": "Que se passe-t-il en cas de non-respect de la charte informatique ?",
        "expected_doc": "systèmes d'information",
    },
    {
        "query": "Comment se passe l'intégration d'un nouveau collaborateur ?",
        "expected_doc": "LIVRET",
    },
    {
        "query": "Quels sont les avantages offerts aux salariés ?",
        "expected_doc": "LIVRET",
    },
    {
        "query": "Quelles sont les bonnes pratiques pour les photos ?",
        "expected_doc": "Bonne-pratique",
    },
]


def _doc_matches(filename: str, expected_keyword: str) -> bool:
    return expected_keyword.lower() in filename.lower()


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBenchmarkEmbedding:
    """Compare Plain embedding (baseline) vs Contextual embedding (optimized)."""

    @pytest.mark.asyncio
    async def test_plain_vs_contextual_embedding(
        self, sanitized_texts: dict[str, str]
    ) -> None:
        assert sanitized_texts, "No test documents found"

        # --- Chunk all docs ---
        chunker = ParagraphTextChunkerService(chunk_size=CHUNK_SIZE)
        doc_chunks: dict[str, list[str]] = {}
        for filename, text in sanitized_texts.items():
            chunks = await chunker.chunk_text(text, ChunkingStrategy.PARAGRAPH)
            doc_chunks[filename] = chunks

        # Flatten to (chunk_text, source_filename) pairs
        all_chunks: list[tuple[str, str]] = []
        for fname, chunks in doc_chunks.items():
            for chunk in chunks:
                if chunk.strip():
                    all_chunks.append((chunk, fname))

        chunk_texts = [c[0] for c in all_chunks]
        chunk_sources = [c[1] for c in all_chunks]

        # --- Baseline: Plain embedding ---
        plain_emb = InMemoryEmbeddingService(dimension=32)
        plain_embeddings = await plain_emb.embed_texts(chunk_texts)

        # --- Optimized: Contextual embedding ---
        ctx_emb = ContextualEmbeddingService(
            delegate=InMemoryEmbeddingService(dimension=32),
            document_prefix="search_document: ",
            query_prefix="search_query: ",
        )
        ctx_embeddings = await ctx_emb.embed_texts(chunk_texts)

        # --- Evaluate queries ---
        rows: list[dict] = []
        benchmark_name = "Embedding: Plain vs Contextual"

        for q_info in QUERIES:
            query = q_info["query"]
            expected_kw = q_info["expected_doc"]
            label = query[:30]

            # Relevant chunk indices
            relevant_indices = {
                str(i) for i, src in enumerate(chunk_sources)
                if _doc_matches(src, expected_kw)
            }

            # Baseline retrieval
            q_emb_plain = (await plain_emb.embed_texts([query]))[0]
            plain_scores = [
                (str(i), cosine_similarity(q_emb_plain, emb))
                for i, emb in enumerate(plain_embeddings)
            ]
            plain_scores.sort(key=lambda x: x[1], reverse=True)
            plain_retrieved = [s[0] for s in plain_scores]

            # Optimized retrieval
            q_emb_ctx = await ctx_emb.embed_query(query)
            ctx_scores = [
                (str(i), cosine_similarity(q_emb_ctx, emb))
                for i, emb in enumerate(ctx_embeddings)
            ]
            ctx_scores.sort(key=lambda x: x[1], reverse=True)
            ctx_retrieved = [s[0] for s in ctx_scores]

            # Metrics
            for metric_name, metric_fn in [
                ("precision@5", lambda r, rel: precision_at_k(r, rel, 5)),
                ("recall@5", lambda r, rel: recall_at_k(r, rel, 5)),
                ("mrr", lambda r, rel: mrr(r, rel)),
                ("ndcg@5", lambda r, rel: ndcg_at_k(r, rel, 5)),
            ]:
                base_val = metric_fn(plain_retrieved, relevant_indices)
                opt_val = metric_fn(ctx_retrieved, relevant_indices)
                rows.append(make_row(benchmark_name, label, metric_name, base_val, opt_val))

        filepath = write_benchmark_csv("embedding_plain_vs_contextual.csv", rows)
        assert filepath.exists()
        assert len(rows) > 0


