# 📊 RAG Pipeline Optimization Benchmarks

> Auto-generated report comparing baseline vs optimized techniques across the full RAG pipeline.

> Test corpus: 5 French PDF documents (company policies)

---

## 📋 Executive Summary

| Metric | Count |
|--------|-------|
| **Optimized wins** | 0 |
| **Baseline wins** | 0 |
| **Ties** | 0 |

## 🔬 Methodology

### Test Corpus
All benchmarks use the same 5 French PDF documents:
1. **Charte télétravail** – Remote work policy
2. **Charte de prévention du harcèlement** – Harassment prevention charter
3. **Charte des systèmes d'information** – IT systems charter
4. **Bonne-pratique Photo** – Photography best practices
5. **LIVRET D'ACCUEIL** – Employee welcome booklet

### Queries
13 French queries covering all documents, testing different aspects:

- Factual questions (conditions, definitions)
- Procedural questions (how to report, how integration works)
- Policy questions (sanctions, obligations)

### Metrics

| Category | Metric | Description | Higher is better? |
|----------|--------|-------------|-------------------|
| Chunking | `boundary_coherence` | Fraction of chunks ending at sentence boundaries | ✅ Yes |
| Chunking | `chunk_size_std` | Standard deviation of chunk sizes | ❌ No (lower = more uniform) |
| Chunking | `empty_chunks` | Number of empty chunks produced | ❌ No |
| Chunking | `single_word_chunks` | Number of single-word chunks | ❌ No |
| Chunking | `information_density` | Ratio of unique to total words per chunk | ✅ Yes |
| Retrieval | `precision@5` | Fraction of top-5 results that are relevant | ✅ Yes |
| Retrieval | `recall@5` | Fraction of relevant docs found in top-5 | ✅ Yes |
| Retrieval | `mrr` | Mean Reciprocal Rank | ✅ Yes |
| Retrieval | `ndcg@5` | Normalized Discounted Cumulative Gain | ✅ Yes |
| Retrieval | `ctx_diversity` | Average pairwise cosine distance of results | ✅ Yes |
| Retrieval | `ctx_redundancy` | 1 - ctx_diversity (overlap between results) | ❌ No |
| Context | `source_attribution` | Presence of source references in prompt | ✅ Yes |
| Context | `structure_quality` | Structured sections (headers, numbering) | ✅ Yes |
| Context | `query_preserved` | Original query present in final prompt | ✅ Yes |
| Context | `context_utilization` | Fraction of retrieved chunks used in prompt | ✅ Yes |

## 🛠️ Techniques Compared

### Baseline Pipeline
- **Chunking:** Fixed window (500 chars, 50 overlap)
- **Embedding:** SHA256-based deterministic hashing
- **Retrieval:** Hybrid search (0.6 vector + 0.4 lexical)
- **Reranking:** None
- **Prompt:** Simple flat template

### Optimized Pipeline
- **Chunking:** Paragraph-aware chunking (respects natural boundaries)
- **Embedding:** Contextual prefix embedding (search_document/search_query)
- **Retrieval:** Hybrid search + MMR diversity reranking (λ=0.7)
- **Reranking:** Maximal Marginal Relevance for diversity
- **Prompt:** Enhanced template with source attribution, structured sections

## 💡 Recommendations

Results are mixed. Further tuning of parameters may be needed.

### Suggested next steps:
1. Test with real embedding models (OpenAI, Gemini) instead of SHA256 hashing
2. Tune MMR λ parameter (currently 0.7) for optimal relevance-diversity balance
3. Experiment with semantic chunking similarity thresholds
4. Add cross-encoder reranking for production workloads
5. Benchmark with larger document corpora

---

*Report generated automatically by the RAG benchmark suite.*
