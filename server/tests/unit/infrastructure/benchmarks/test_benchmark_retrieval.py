"""Benchmark: Retrieval – Hybrid (baseline) vs Hybrid + MMR diversity (optimized).

Evaluates retrieval quality and context diversity on the test PDFs.
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.in_memory_embedding_service import InMemoryEmbeddingService
from raggae.infrastructure.services.mmr_diversity_reranker_service import (
    MmrDiversityRerankerService,
)
from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)

from .conftest import (
    context_diversity,
    context_redundancy,
    cosine_similarity,
    make_row,
    mrr,
    ndcg_at_k,
    precision_at_k,
    write_benchmark_csv,
)

CHUNK_SIZE = 500
TOP_K = 5

QUERIES: list[dict[str, Any]] = [
    {"query": "Quelles sont les conditions pour bénéficier du télétravail ?", "expected_doc": "Charte télétravail"},
    {"query": "Qui peut bénéficier du télétravail dans l'entreprise ?", "expected_doc": "Charte télétravail"},
    {"query": "Quelles sont les obligations de l'employeur en matière de télétravail ?", "expected_doc": "Charte télétravail"},
    {"query": "Comment signaler un cas de harcèlement au travail ?", "expected_doc": "harcèlement"},
    {"query": "Quelles sont les sanctions prévues en cas de harcèlement ?", "expected_doc": "harcèlement"},
    {"query": "Quelle est la définition du harcèlement moral et sexuel ?", "expected_doc": "harcèlement"},
    {"query": "Quelles sont les règles d'utilisation des systèmes d'information ?", "expected_doc": "systèmes d'information"},
    {"query": "Quelles sont les obligations en matière de sécurité informatique ?", "expected_doc": "systèmes d'information"},
    {"query": "Que se passe-t-il en cas de non-respect de la charte informatique ?", "expected_doc": "systèmes d'information"},
    {"query": "Comment se passe l'intégration d'un nouveau collaborateur ?", "expected_doc": "LIVRET"},
    {"query": "Quels sont les avantages offerts aux salariés ?", "expected_doc": "LIVRET"},
    {"query": "Quelles sont les bonnes pratiques pour les photos ?", "expected_doc": "Bonne-pratique"},
]


def _doc_matches(filename: str, expected_keyword: str) -> bool:
    return expected_keyword.lower() in filename.lower()


# ---------------------------------------------------------------------------
# In-memory retrieval helpers
# ---------------------------------------------------------------------------


async def _build_index(
    sanitized_texts: dict[str, str],
    embedding_svc: InMemoryEmbeddingService,
) -> tuple[list[str], list[str], list[list[float]], list[str]]:
    """Build a flat index: returns (chunk_texts, chunk_ids, embeddings, source_filenames)."""
    chunker = ParagraphTextChunkerService(chunk_size=CHUNK_SIZE)
    all_texts: list[str] = []
    all_ids: list[str] = []
    all_sources: list[str] = []

    for filename, text in sanitized_texts.items():
        chunks = await chunker.chunk_text(text, ChunkingStrategy.PARAGRAPH)
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                all_texts.append(chunk)
                all_ids.append(f"{filename}::{i}")
                all_sources.append(filename)

    embeddings = await embedding_svc.embed_texts(all_texts)
    return all_texts, all_ids, embeddings, all_sources


def _hybrid_retrieve(
    query_embedding: list[float],
    query_text: str,
    chunk_texts: list[str],
    chunk_ids: list[str],
    embeddings: list[list[float]],
    vector_weight: float = 0.6,
    fulltext_weight: float = 0.4,
    limit: int = TOP_K,
) -> list[tuple[str, float, int]]:
    """Simple hybrid retrieval returning (chunk_id, score, index)."""
    query_terms = set(query_text.lower().split())
    scored: list[tuple[str, float, int]] = []

    for i, (text, cid, emb) in enumerate(zip(chunk_texts, chunk_ids, embeddings)):
        vec_score = cosine_similarity(query_embedding, emb)
        content_terms = set(text.lower().split())
        lex_score = len(query_terms & content_terms) / max(len(query_terms), 1)
        score = vector_weight * vec_score + fulltext_weight * lex_score
        scored.append((cid, score, i))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestBenchmarkRetrieval:
    """Compare Hybrid retrieval (baseline) vs Hybrid + MMR diversity (optimized)."""

    @pytest.mark.asyncio
    async def test_hybrid_vs_mmr_diversity(
        self, sanitized_texts: dict[str, str]
    ) -> None:
        assert sanitized_texts, "No test documents found"

        embedding_svc = InMemoryEmbeddingService(dimension=32)
        chunk_texts, chunk_ids, embeddings, chunk_sources = await _build_index(
            sanitized_texts, embedding_svc
        )

        mmr_reranker = MmrDiversityRerankerService(lambda_param=0.85)
        rows: list[dict] = []
        benchmark_name = "Retrieval: Hybrid vs Hybrid+Diversity"

        for q_info in QUERIES:
            query = q_info["query"]
            expected_kw = q_info["expected_doc"]
            label = query[:30]

            relevant_ids = {
                cid for cid, src in zip(chunk_ids, chunk_sources)
                if _doc_matches(src, expected_kw)
            }

            q_emb = (await embedding_svc.embed_texts([query]))[0]

            # --- Baseline: standard hybrid ---
            baseline_results = _hybrid_retrieve(
                q_emb, query, chunk_texts, chunk_ids, embeddings
            )
            base_retrieved = [r[0] for r in baseline_results]
            base_embs = [embeddings[r[2]] for r in baseline_results]

            # --- Optimized: hybrid + MMR reranking ---
            # First get more candidates, then MMR rerank
            candidate_results = _hybrid_retrieve(
                q_emb, query, chunk_texts, chunk_ids, embeddings, limit=TOP_K * 3
            )
            candidate_dtos = [
                RetrievedChunkDTO(
                    chunk_id=uuid4(),
                    document_id=uuid4(),
                    content=chunk_texts[r[2]],
                    score=r[1],
                    chunk_index=r[2],
                )
                for r in candidate_results
            ]
            candidate_embs = [embeddings[r[2]] for r in candidate_results]

            mmr_results = await mmr_reranker.rerank(
                query=query,
                chunks=candidate_dtos,
                top_k=TOP_K,
                chunk_embeddings=candidate_embs,
                query_embedding=q_emb,
            )
            opt_retrieved = [
                chunk_ids[dto.chunk_index] for dto in mmr_results if dto.chunk_index is not None
            ]
            opt_embs = [
                embeddings[dto.chunk_index] for dto in mmr_results if dto.chunk_index is not None
            ]

            # --- Metrics ---
            # precision@5
            p_base = precision_at_k(base_retrieved, relevant_ids, TOP_K)
            p_opt = precision_at_k(opt_retrieved, relevant_ids, TOP_K)
            rows.append(make_row(benchmark_name, label, "precision@5", p_base, p_opt))

            # mrr
            m_base = mrr(base_retrieved, relevant_ids)
            m_opt = mrr(opt_retrieved, relevant_ids)
            rows.append(make_row(benchmark_name, label, "mrr", m_base, m_opt))

            # ndcg@5
            n_base = ndcg_at_k(base_retrieved, relevant_ids, TOP_K)
            n_opt = ndcg_at_k(opt_retrieved, relevant_ids, TOP_K)
            rows.append(make_row(benchmark_name, label, "ndcg@5", n_base, n_opt))

            # ctx_diversity
            d_base = context_diversity(base_embs) if base_embs else 0.0
            d_opt = context_diversity(opt_embs) if opt_embs else 0.0
            rows.append(make_row(benchmark_name, label, "ctx_diversity", d_base, d_opt))

            # ctx_relevance_density
            rel_base = sum(1 for r in base_retrieved if r in relevant_ids) / max(len(base_retrieved), 1)
            rel_opt = sum(1 for r in opt_retrieved if r in relevant_ids) / max(len(opt_retrieved), 1)
            rows.append(make_row(benchmark_name, label, "ctx_relevance_density", rel_base, rel_opt))

            # ctx_redundancy
            red_base = context_redundancy(base_embs) if base_embs else 0.0
            red_opt = context_redundancy(opt_embs) if opt_embs else 0.0
            rows.append(
                make_row(benchmark_name, label, "ctx_redundancy", red_base, red_opt, higher_is_better=False)
            )

        filepath = write_benchmark_csv("retrieval_hybrid_vs_diversity.csv", rows)
        assert filepath.exists()
        assert len(rows) > 0



