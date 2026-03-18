# Pipeline RAG — Spécification

## Vue d'ensemble

Le pipeline RAG (Retrieval Augmented Generation) de Raggae est découpé en **5 étapes** :

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE OFFLINE (indexation)                                         │
│                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │  1. Document     │ ───► │  2. Knowledge    │                    │
│  │     Ingestion    │      │     Indexing     │                    │
│  └──────────────────┘      └──────────────────┘                    │
│  Chargement, parsing,      Chunking, embedding,                    │
│  nettoyage, metadata       stockage vecteurs                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  PHASE ONLINE (requête)                                             │
│                                                                     │
│  ┌──────────────────┐      ┌──────────────────┐      ┌──────────┐ │
│  │  3. Context      │ ───► │  4. Context      │ ───► │  5.      │ │
│  │     Retrieval    │      │     Augmentation │      │  Answer  │ │
│  └──────────────────┘      └──────────────────┘      │  Genera- │ │
│  Embed query, recherche    Re-ranking, assemblage     │  tion    │ │
│  hybride (vector + BM25)   du prompt RAG             └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

Les étapes 1 et 2 s'exécutent **offline** (à l'upload ou à la réindexation).
Les étapes 3, 4 et 5 s'exécutent **online** à chaque requête utilisateur.

---

## Étape 1 : Document Ingestion

### Responsabilité

Prendre un fichier brut, l'analyser et produire un texte nettoyé enrichi de métadonnées, prêt pour l'indexation.

### Cycle de vie du document

```
uploaded → processing → indexed
                    ↘ error
indexed  → processing  (réindexation)
error    → processing  (retry)
```

Entité : `Document` (`server/src/raggae/domain/entities/document.py`)

| Champ | Type | Description |
|-------|------|-------------|
| `status` | `DocumentStatus` | État courant (`UPLOADED`, `PROCESSING`, `INDEXED`, `ERROR`) |
| `language` | `str \| None` | Langue détectée |
| `keywords` | `list[str] \| None` | Mots-clés extraits |
| `authors` | `list[str] \| None` | Auteurs (PDF/DOCX) |
| `title` | `str \| None` | Titre extrait |
| `processing_strategy` | `ChunkingStrategy \| None` | Stratégie utilisée lors de l'indexation |
| `error_message` | `str \| None` | Message d'erreur si `status = ERROR` |

### Formats supportés

`txt`, `md`, `pdf`, `doc`, `docx` — taille max 10 MB, quota 100 documents/projet.

### Composants

| Composant | Interface | Implémentations |
|-----------|-----------|-----------------|
| Extraction texte | `DocumentTextExtractor` | `SimpleDocumentTextExtractor`, `MultiformatDocumentTextExtractor` |
| Nettoyage texte | `TextSanitizerService` | `SimpleTextSanitizerService` |
| Analyse structure | `DocumentStructureAnalyzer` | `HeuristicDocumentStructureAnalyzer` |
| Détection langue | `LanguageDetector` | `LangdetectLanguageDetector`, `InMemoryLanguageDetector` |
| Extraction mots-clés | `KeywordExtractor` | `KeybertKeywordExtractor`, `InMemoryKeywordExtractor` |
| Métadonnées fichier | `FileMetadataExtractor` | `PdfDocxFileMetadataExtractor` |
| Stockage fichier | `FileStorageService` | `MinioFileStorageService`, `InMemoryFileStorageService` |

### Use case

- `UploadDocument` — `application/use_cases/document/upload_document.py`

---

## Étape 2 : Knowledge Indexing

### Responsabilité

Transformer le texte extrait en chunks vectorisés stockés dans PostgreSQL avec pgvector.

### Flux d'indexation

```
texte nettoyé
  → [DocumentStructureAnalyzer] analyse structure
  → [ChunkingStrategySelector] sélection stratégie optimale
  → [TextChunkerService] découpage en chunks
  → optionnel: [ParentChildChunkingService] hiérarchie parent/enfant
  → [EmbeddingService] vectorisation des chunks
  → [DocumentChunkRepository] persistance
```

### Stratégies de chunking

| Stratégie | Cas d'usage |
|-----------|-------------|
| `FIXED_WINDOW` | Texte homogène sans structure |
| `PARAGRAPH` | Texte avec paragraphes distincts |
| `HEADING_SECTION` | Documents structurés (Markdown, PDF avec titres) |
| `SEMANTIC` | Texte dense nécessitant une segmentation sémantique |
| `AUTO` | Sélection automatique via `ChunkingStrategySelector` |

### Chunking parent-enfant

Pour les documents longs, les chunks sont organisés en deux niveaux :
- **Parent** (~2000 chars) : fournit le contexte large, pas vectorisé
- **Enfant** (~500 chars) : utilisé pour la recherche vectorielle

Champ `DocumentChunk.chunk_level` : `STANDARD`, `PARENT`, `CHILD`.

### Contrats d'interface

```python
# TextChunkerService
async def chunk_text(
    text: str,
    strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    embedding_service: EmbeddingService | None = None,
) -> list[str]

# EmbeddingService
async def embed_texts(texts: list[str]) -> list[list[float]]
```

### Composants

| Composant | Interface | Implémentations |
|-----------|-----------|-----------------|
| Chunking | `TextChunkerService` | `SimpleTextChunkerService`, `ParagraphTextChunkerService`, `HeadingSectionTextChunkerService`, `SemanticTextChunkerService`, `AdaptiveTextChunkerService`, `LlamaindexTextChunkerService` |
| Sélection stratégie | `ChunkingStrategySelector` | `DeterministicChunkingStrategySelector` |
| Chunking hiérarchique | `ParentChildChunkingService` | (service applicatif) |
| Embedding | `EmbeddingService` | `OpenaiEmbeddingService`, `OllamaEmbeddingService`, `GeminiEmbeddingService`, `InMemoryEmbeddingService` |
| Stockage chunks | `DocumentChunkRepository` | `SQLAlchemyDocumentChunkRepository` |

### Service d'orchestration

- `DocumentIndexingService` — `application/services/document_indexing_service.py`

---

## Étape 3 : Context Retrieval

### Responsabilité

À partir d'une requête utilisateur, retrouver les chunks les plus pertinents via une recherche hybride.

### Flux de retrieval

```
requête utilisateur
  → [EmbeddingService] vectorisation de la requête
  → [ChunkRetrievalService] recherche hybride
      ├── vector search (cosine distance, pgvector)
      ├── full-text search (ts_rank_cd, PostgreSQL)
      └── fusion des scores (weighted sum : 60% vector + 40% BM25)
  → optionnel: [context window expansion] chunks voisins
  → optionnel: [parent chunk resolution] contexte large
```

### Stratégies de recherche (auto-détectées)

| Stratégie | Déclencheur |
|-----------|-------------|
| `vector` | Requêtes sémantiques longues |
| `fulltext` | Termes entre guillemets, mots-clés courts |
| `hybrid` | Cas général (défaut) |

### Filtrage métadonnées

Filtres supportés : `document_type`, `language`, `source_type`, `processing_strategy`, `tags`.

### Contrat d'interface

```python
# ChunkRetrievalService
async def retrieve_chunks(
    project_id: UUID,
    query_text: str,
    query_embedding: list[float],
    limit: int,
    offset: int = 0,
    min_score: float = 0.0,
    strategy: str = "hybrid",
    metadata_filters: dict[str, object] | None = None,
) -> list[RetrievedChunkDTO]
```

### Composants

| Composant | Interface | Implémentations |
|-----------|-----------|-----------------|
| Recherche hybride | `ChunkRetrievalService` | `SQLAlchemyChunkRetrievalService` |
| Vectorisation requête | `EmbeddingService` | (voir étape 2) |

### Use case

- `QueryRelevantChunks` — `application/use_cases/chat/query_relevant_chunks.py`

---

## Étape 4 : Context Augmentation

### Responsabilité

Affiner et organiser les chunks récupérés, puis construire le prompt final enrichi du contexte.

### Flux d'augmentation

```
chunks récupérés (étape 3)
  → [RerankerService] re-scoring par pertinence sémantique (optionnel)
  → [_filter_relevant_chunks] suppression chunks vides
  → [_select_useful_chunks] distribution anti-redondance (1 chunk/doc en premier)
  → [build_rag_prompt] assemblage du prompt
      ├── prompt système du projet
      ├── historique de conversation (sliding window : 8 messages, 4000 chars max)
      ├── extraits numérotés avec démarcation claire
      └── mesures anti-injection (instructions pour ignorer les commandes dans les données)
```

### Contrat d'interface

```python
# RerankerService
async def rerank(
    query: str,
    chunks: list[RetrievedChunkDTO],
    top_k: int,
) -> list[RetrievedChunkDTO]
```

### Composants

| Composant | Interface | Implémentations |
|-----------|-----------|-----------------|
| Re-ranking | `RerankerService` | `CrossEncoderRerankerService`, `InMemoryRerankerService`, `MmrDiversityRerankerService` |
| Assemblage prompt | `build_rag_prompt()` | `infrastructure/services/prompt_builder.py` |

### Sécurité

Le prompt inclut des instructions systèmes pour prévenir les attaques par injection via le contenu des documents.

---

## Étape 5 : Answer Generation

### Responsabilité

Appeler le LLM avec le prompt augmenté, gérer l'historique de conversation et tracer les sources.

### Flux de génération

```
prompt augmenté (étape 4)
  → [LLMService] génération de la réponse (streaming ou non)
  → [ChatSecurityPolicy.sanitize_model_answer] nettoyage de la réponse
  → calcul du taux de fiabilité (ratio chunks utilisés / disponibles)
  → traçage des documents sources
  → persistance du message (MessageRepository)
  → optionnel: [ConversationTitleGenerator] titre automatique (1er message)
```

### LLM providers

| Provider | Implémentation |
|----------|----------------|
| OpenAI | `OpenaiLLMService` |
| Gemini | `GeminiLLMService` |
| Ollama | `OllamaLLMService` |
| In-memory (test) | `InMemoryLLMService` |

La sélection se fait par projet (`Project.llm_backend`).

### Streaming

Le LLM peut être interrogé en mode streaming : les tokens sont émis via `ChatStreamEvent` (`ChatStreamToken` | `ChatStreamDone`).

### Contrats d'interface

```python
# LLMService
async def generate_answer(prompt: str) -> str
def generate_answer_stream(prompt: str) -> AsyncIterator[str]

# ConversationTitleGenerator
async def generate_title(first_message: str) -> str
```

### Composants

| Composant | Interface | Implémentations |
|-----------|-----------|-----------------|
| Génération LLM | `LLMService` | `OpenaiLLMService`, `GeminiLLMService`, `OllamaLLMService`, `InMemoryLLMService` |
| Titre conversation | `ConversationTitleGenerator` | `LlmConversationTitleGenerator` |
| Politique sécurité | `ChatSecurityPolicy` | `StaticChatSecurityPolicy` |

### Use case

- `SendMessage` — `application/use_cases/chat/send_message.py`

---

## Gaps identifiés (v1)

| Gap | Priorité | Notes |
|-----|----------|-------|
| Endpoint `POST .../reindex` (batch) | Haute | Use case `ReindexDocument` existe, endpoint manquant |
| Endpoint `PUT .../documents/{id}` (remplacement) | Moyenne | Use case `ReplaceDocument` à créer |
| Endpoints projets CRUD | Haute | Use cases existent, endpoints manquants |
| Endpoints documents CRUD | Haute | Use cases existent, endpoints manquants |
| Endpoints conversation / chat | Haute | Use cases existent, endpoints manquants |
| Endpoint `POST .../query` (RAG sans conversation) | Haute | Use case existe, endpoint manquant |

## Non-objectifs (v1)

- Compression/résumé du contexte avant envoi au LLM
- Réécriture automatique de la requête (query rewriting)
- Reciprocal Rank Fusion (weighted sum utilisé à la place)
- Chunking incrémental (seul le réindexage complet est supporté)
- Paramètres de chunking configurables par l'utilisateur
