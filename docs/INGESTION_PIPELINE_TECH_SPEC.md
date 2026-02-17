# Specifications techniques — Pipeline d'ingestion v1

> Ce document decrit les choix techniques pour implementer les [specifications fonctionnelles du pipeline d'ingestion](./INGESTION_PIPELINE_SPEC.md).

## 1. Etats du document

### 1.1 Value object `DocumentStatus`

Nouveau `StrEnum` dans la couche Domain, au meme niveau que `ChunkingStrategy` :

```
server/src/raggae/domain/value_objects/document_status.py
```

```python
from enum import StrEnum

class DocumentStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"
```

### 1.2 Transitions protegees dans l'entite `Document`

L'entite `Document` (frozen dataclass) expose une methode `transition_to(status)` qui valide les transitions autorisees et retourne une nouvelle instance :

```python
ALLOWED_TRANSITIONS: dict[DocumentStatus, set[DocumentStatus]] = {
    DocumentStatus.UPLOADED: {DocumentStatus.PROCESSING},
    DocumentStatus.PROCESSING: {DocumentStatus.INDEXED, DocumentStatus.ERROR},
    DocumentStatus.INDEXED: {DocumentStatus.PROCESSING},
    DocumentStatus.ERROR: {DocumentStatus.PROCESSING},
}
```

Si la transition est invalide, lever une `InvalidDocumentStatusTransitionError` (nouvelle exception Domain).

### 1.3 Nouveaux champs sur l'entite `Document`

```python
@dataclass(frozen=True)
class Document:
    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    storage_key: str
    created_at: datetime
    processing_strategy: ChunkingStrategy | None = None
    status: DocumentStatus = DocumentStatus.UPLOADED        # nouveau
    error_message: str | None = None                        # nouveau
    language: str | None = None                             # nouveau
    keywords: list[str] | None = None                       # nouveau
    authors: list[str] | None = None                        # nouveau
    document_date: date | None = None                       # nouveau
    title: str | None = None                                # nouveau
```

### 1.4 Migration Alembic — `add_document_status_and_metadata`

- Ajouter colonne `status VARCHAR(16) NOT NULL DEFAULT 'indexed'` sur `documents`
  - Default `indexed` (et non `uploaded`) pour que les documents existants restent exploitables
- Ajouter colonne `error_message TEXT NULL`
- Ajouter colonne `language VARCHAR(8) NULL`
- Ajouter colonne `keywords JSONB NULL` (liste de strings serialisee en JSON)
- Ajouter colonne `authors JSONB NULL` (liste de strings serialisee en JSON)
- Ajouter colonne `document_date DATE NULL`
- Ajouter colonne `title VARCHAR(512) NULL`

### 1.5 Mapping dans `DocumentModel`

Ajouter les colonnes correspondantes dans `server/src/raggae/infrastructure/database/models/document_model.py`. Les champs `keywords` et `authors` utilisent le type `JSONB` de PostgreSQL.

## 2. Extraction de metadonnees

### 2.1 Architecture : 3 services separes

Chaque extracteur est un service independant avec son interface (Protocol) dans la couche Application et son implementation dans la couche Infrastructure.

```
Application (interfaces)                    Infrastructure (implementations)
─────────────────────────                   ──────────────────────────────────
LanguageDetector                            LangdetectLanguageDetector
KeywordExtractor                            KeybertKeywordExtractor
FileMetadataExtractor                       PdfDocxFileMetadataExtractor
```

### 2.2 Interface `LanguageDetector`

```
server/src/raggae/application/interfaces/services/language_detector.py
```

```python
from typing import Protocol

class LanguageDetector(Protocol):
    async def detect_language(self, text: str) -> str | None: ...
```

- Entree : texte brut (les 5000 premiers caracteres suffisent)
- Sortie : code ISO 639-1 (`"fr"`, `"en"`, etc.) ou `None` si indetermine
- Erreur : ne leve jamais d'exception — retourne `None` en cas d'echec

### 2.3 Implementation `LangdetectLanguageDetector`

```
server/src/raggae/infrastructure/services/langdetect_language_detector.py
```

- Dependance : `langdetect` (pip)
- Tronquer le texte a 5000 caracteres avant detection
- Encapsuler l'appel dans un try/except pour gerer les `LangDetectException` (texte trop court, pas de features)
- `langdetect` est non-deterministe par defaut ; appeler `DetectorFactory.seed = 0` a l'init pour des resultats reproductibles

### 2.4 Interface `KeywordExtractor`

```
server/src/raggae/application/interfaces/services/keyword_extractor.py
```

```python
from typing import Protocol

class KeywordExtractor(Protocol):
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]: ...
```

- Entree : texte sanitise complet
- Sortie : liste de mots-cles (max `max_keywords`), ordonnee par pertinence decroissante
- Erreur : retourne une liste vide en cas d'echec

### 2.5 Implementation `KeybertKeywordExtractor`

```
server/src/raggae/infrastructure/services/keybert_keyword_extractor.py
```

- Dependance : `keybert` (pip), qui embarque `sentence-transformers`
- Modele : `paraphrase-multilingual-MiniLM-L12-v2` (bon support du francais, leger ~120 Mo)
- Le modele est charge une seule fois au premier appel (lazy loading) et reutilise
- Parametres KeyBERT : `keyphrase_ngram_range=(1, 2)`, `stop_words=None` (les stop words des modeles multilingues sont geres implicitement), `top_n=max_keywords`
- Fallback : si KeyBERT echoue (texte trop court, erreur modele), basculer sur un extracteur TF-IDF simple via `sklearn.feature_extraction.text.TfidfVectorizer`

### 2.6 Interface `FileMetadataExtractor`

```
server/src/raggae/application/interfaces/services/file_metadata_extractor.py
```

```python
from dataclasses import dataclass
from datetime import date
from typing import Protocol

@dataclass(frozen=True)
class FileMetadata:
    title: str | None = None
    authors: list[str] | None = None
    document_date: date | None = None

class FileMetadataExtractor(Protocol):
    async def extract_metadata(self, file_content: bytes, content_type: str) -> FileMetadata: ...
```

- Entree : contenu binaire du fichier + content type
- Sortie : `FileMetadata` (tous champs nullable)
- Erreur : retourne un `FileMetadata()` vide en cas d'echec

### 2.7 Implementation `PdfDocxFileMetadataExtractor`

```
server/src/raggae/infrastructure/services/pdf_docx_file_metadata_extractor.py
```

- **PDF** : `pypdf.PdfReader` → `reader.metadata` expose `/Author`, `/Title`, `/CreationDate`
  - Parser la date avec `datetime.strptime` (format PDF : `D:YYYYMMDDHHmmSS`)
  - L'auteur peut contenir plusieurs noms separes par `,` ou `;` → split + strip
- **DOCX** : `python-docx` → `document.core_properties` expose `author`, `title`, `created`
- **TXT/MD** : retourne `FileMetadata()` vide (pas de metadonnees disponibles)
- Aucune nouvelle dependance (pypdf et python-docx sont deja utilises)

### 2.8 Tests

Chaque service a son fake/in-memory pour les tests unitaires :

- `InMemoryLanguageDetector` : retourne un code langue configurable
- `InMemoryKeywordExtractor` : retourne une liste de mots-cles configurable
- `InMemoryFileMetadataExtractor` : retourne un `FileMetadata` configurable

## 3. Strategie de chunking — extensions

### 3.1 Ajout de `SEMANTIC` et `AUTO` a `ChunkingStrategy`

```python
class ChunkingStrategy(StrEnum):
    AUTO = "auto"                      # nouveau
    FIXED_WINDOW = "fixed_window"
    PARAGRAPH = "paragraph"
    HEADING_SECTION = "heading_section"
    SEMANTIC = "semantic"              # nouveau
```

`AUTO` n'est pas une strategie de chunking a proprement parler : c'est une valeur de configuration projet qui signifie "le systeme choisit via le `ChunkingStrategySelector`". Le pipeline resout `AUTO` en une strategie concrete avant d'appeler le chunker.

### 3.2 Nouveau service `SemanticTextChunkerService`

```
server/src/raggae/infrastructure/services/semantic_text_chunker_service.py
```

**Interface :** implemente `TextChunkerService` (Protocol existant).

**Dependance supplementaire :** un `EmbeddingService` dedie, injecte au constructeur. Ce n'est PAS le meme que celui du pipeline principal — c'est une instance separee, configuree de la meme facon, mais injectee independamment pour decoupler chunking et embedding.

**Algorithme :**

1. Decouper le texte en phrases via regex : split sur `(?<=[.!?])\s+|\n` (gere les fins de phrase classiques et les sauts de ligne)
2. Generer un embedding pour chaque phrase via le `EmbeddingService` dedie
3. Calculer la similarite cosinus entre chaque paire de phrases consecutives
4. Identifier les points de coupure : indices ou la similarite < `similarity_threshold` (defaut : 0.5)
5. Regrouper les phrases entre deux coupures en un chunk
6. Si un chunk depasse `chunk_size`, le re-decouper avec `SimpleTextChunkerService` (fallback taille fixe)

**Constructeur :**

```python
class SemanticTextChunkerService:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        chunk_size: int = 1000,
        similarity_threshold: float = 0.5,
        fallback_chunker: TextChunkerService | None = None,
    ) -> None: ...
```

### 3.3 Integration dans `AdaptiveTextChunkerService`

Ajouter le routage vers `SemanticTextChunkerService` pour `ChunkingStrategy.SEMANTIC` :

```python
# dans AdaptiveTextChunkerService.__init__
self._semantic_chunker = semantic_chunker  # nouveau parametre

# dans le routage
if strategy == ChunkingStrategy.SEMANTIC:
    return await self._semantic_chunker.chunk_text(text, strategy=strategy)
```

### 3.4 Resolution de `AUTO` dans le pipeline

Dans `DocumentIndexingService.run_pipeline()`, le `ChunkingStrategy` provient desormais du projet (pas du selecteur directement). La logique de resolution :

```python
strategy = project.chunking_strategy  # depuis le projet

if strategy == ChunkingStrategy.AUTO:
    analysis = await self._document_structure_analyzer.analyze_text(sanitized_text)
    strategy = self._chunking_strategy_selector.select(...)

# Le selecteur ne retourne jamais AUTO ni SEMANTIC
# SEMANTIC n'est selectionne que si l'utilisateur l'a explicitement choisi
```

Le `DeterministicChunkingStrategySelector` reste inchange : il ne connait pas `AUTO` ni `SEMANTIC` et continue de retourner `FIXED_WINDOW`, `PARAGRAPH` ou `HEADING_SECTION`.

## 4. Parent-child chunking

### 4.1 Nouveaux champs sur l'entite `DocumentChunk`

```python
@dataclass(frozen=True)
class DocumentChunk:
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: list[float]
    created_at: datetime
    metadata_json: dict[str, Any] | None = None
    chunk_level: str = "standard"              # nouveau : "standard" | "parent" | "child"
    parent_chunk_id: UUID | None = None        # nouveau
```

### 4.2 Value object `ChunkLevel`

```
server/src/raggae/domain/value_objects/chunk_level.py
```

```python
from enum import StrEnum

class ChunkLevel(StrEnum):
    STANDARD = "standard"
    PARENT = "parent"
    CHILD = "child"
```

### 4.3 Migration Alembic — `add_parent_child_chunking`

- Ajouter colonne `chunk_level VARCHAR(16) NOT NULL DEFAULT 'standard'` sur `document_chunks`
- Ajouter colonne `parent_chunk_id UUID NULL REFERENCES document_chunks(id) ON DELETE CASCADE` sur `document_chunks`
- Ajouter index sur `parent_chunk_id`

### 4.4 Service `ParentChildChunkingService`

```
server/src/raggae/application/services/parent_child_chunking_service.py
```

Ce service se place dans la couche **Application** (il orchestre des interfaces, pas de l'infrastructure).

**Interface :**

```python
class ParentChildChunkingService:
    def __init__(
        self,
        parent_chunk_size: int = 2000,
        child_chunk_size: int = 500,
        child_chunk_overlap: int = 50,
    ) -> None: ...

    def split_into_parent_child(
        self,
        chunks: list[str],
    ) -> list[tuple[str, list[str]]]:
        """Prend les chunks standard et retourne des paires (parent_text, [child_texts])."""
        ...
```

**Algorithme :**

1. Recevoir les chunks produits par le chunker standard
2. Regrouper les chunks adjacents pour former des chunks parents de ~2000 caracteres
3. Re-decouper chaque chunk parent en chunks enfants de ~500 caracteres avec overlap de 50
4. Retourner la liste de paires `(parent_content, [child_contents])`

**Integration dans `DocumentIndexingService` :**

Le service est utilise apres le chunking standard, si `project.parent_child_chunking` est `True` :

```python
if project.parent_child_chunking:
    parent_child_pairs = self._parent_child_service.split_into_parent_child(chunks)
    # Creer les DocumentChunk avec les bons chunk_level et parent_chunk_id
else:
    # Comportement actuel : chunks standard
```

Les chunks parents sont stockes avec `embedding=[]` (liste vide) et `chunk_level="parent"`. Seuls les chunks enfants (`chunk_level="child"`) sont envoyes a l'`EmbeddingService`.

### 4.5 Impact sur le retrieval

Dans `QueryRelevantChunks` et `SQLAlchemyChunkRetrievalService` :

- La recherche vectorielle filtre sur `chunk_level IN ('standard', 'child')` (jamais `parent`)
- Quand un chunk `child` est selectionne, charger le chunk parent associe via `parent_chunk_id`
- Injecter le contenu du chunk parent (pas de l'enfant) dans le contexte du LLM

## 5. Configuration du projet

### 5.1 Nouveaux champs sur l'entite `Project`

```python
@dataclass(frozen=True)
class Project:
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.AUTO      # nouveau
    parent_child_chunking: bool = False                               # nouveau
    reindex_status: str | None = None                                 # nouveau
    reindex_progress: int | None = None                               # nouveau
    reindex_total: int | None = None                                  # nouveau
```

### 5.2 Methodes metier sur `Project`

```python
def start_reindex(self, total: int) -> "Project":
    """Demarre la reindexation. Leve si deja en cours."""
    if self.reindex_status == "in_progress":
        raise ProjectReindexInProgressError()
    return replace(self, reindex_status="in_progress", reindex_progress=0, reindex_total=total)

def advance_reindex(self) -> "Project":
    """Incremente le compteur de progression."""
    return replace(self, reindex_progress=(self.reindex_progress or 0) + 1)

def finish_reindex(self) -> "Project":
    """Termine la reindexation."""
    return replace(self, reindex_status=None, reindex_progress=None, reindex_total=None)

def is_reindexing(self) -> bool:
    return self.reindex_status == "in_progress"
```

### 5.3 Migration Alembic — `add_project_ingestion_settings`

- Ajouter colonne `chunking_strategy VARCHAR(32) NOT NULL DEFAULT 'auto'` sur `projects`
- Ajouter colonne `parent_child_chunking BOOLEAN NOT NULL DEFAULT FALSE` sur `projects`
- Ajouter colonne `reindex_status VARCHAR(16) NULL` sur `projects`
- Ajouter colonne `reindex_progress INTEGER NULL` sur `projects`
- Ajouter colonne `reindex_total INTEGER NULL` sur `projects`

### 5.4 Mise a jour de `UpdateProject`

Le use case `UpdateProject` existant doit accepter `chunking_strategy` et `parent_child_chunking` en parametres optionnels. L'endpoint `PATCH /projects/{project_id}` les expose.

## 6. Gestion des doublons et remplacement

### 6.1 Modification du comportement d'upload existant

Dans `UploadDocument.execute_many()`, remplacer le renommage automatique (`-copie-#`) par un rejet avec code `DUPLICATE_FILENAME` :

- Quand un `file_name` existe deja dans le projet (query `find_by_project_id` + filtre sur `file_name`)
- Ajouter dans `errors` : `{"filename": ..., "code": "DUPLICATE_FILENAME", "message": "Un document avec ce nom existe deja (id: {existing_id})"}`
- Les autres fichiers du batch continuent normalement

### 6.2 Nouveau use case `ReplaceDocument`

```
server/src/raggae/application/use_cases/document/replace_document.py
```

**Dependances :**

- `DocumentRepository`
- `ProjectRepository`
- `FileStorageService`
- `DocumentChunkRepository`
- `DocumentIndexingService`

**Flux :**

1. Verifier que le projet existe et appartient a l'utilisateur
2. Verifier que le document existe et appartient au projet
3. Verifier que le projet n'est pas en reindexation (`409 Conflict`)
4. Valider le nouveau fichier (format, taille)
5. Supprimer les chunks existants du document
6. Remplacer le fichier en storage (supprimer ancien + stocker nouveau)
7. Mettre a jour le document : `file_name`, `content_type`, `file_size`, `storage_key`, `status → processing`
8. Lancer le pipeline d'indexation
9. Si succes : `status → indexed`
10. Si echec : `status → error` avec `error_message` (pas de rollback vers l'ancien fichier)

**Endpoint :**

```
PUT /projects/{project_id}/documents/{document_id}
Content-Type: multipart/form-data
Body: file (single UploadFile)
```

Reponse : `200 OK` avec `DocumentResponse` mis a jour.

## 7. Reindexation batch

### 7.1 Nouveau use case `ReindexProject`

```
server/src/raggae/application/use_cases/project/reindex_project.py
```

**Dependances :**

- `ProjectRepository`
- `DocumentRepository`
- `FileStorageService`
- `DocumentIndexingService`

**Flux :**

1. Verifier que le projet existe et appartient a l'utilisateur
2. Verifier que le projet n'est pas deja en reindexation (`409 Conflict`)
3. Charger tous les documents du projet (etats `indexed` et `error`)
4. Appeler `project.start_reindex(total=len(documents))` → sauvegarder le projet
5. Pour chaque document, sequentiellement :
   a. `document.transition_to(PROCESSING)` → sauvegarder
   b. Charger le fichier depuis le storage
   c. Lancer `document_indexing_service.run_pipeline()`
   d. Si succes : `document.transition_to(INDEXED)` → sauvegarder
   e. Si echec : `document.transition_to(ERROR)` avec `error_message` → sauvegarder, continuer
   f. `project.advance_reindex()` → sauvegarder
6. `project.finish_reindex()` → sauvegarder
7. Retourner le rapport : `{total, succeeded, failed, errors: [{document_id, error_message}]}`

### 7.2 Endpoint

```
POST /projects/{project_id}/reindex
```

- Requete bloquante (synchrone) — pas de `BackgroundTasks`
- Reponse : `200 OK` avec le rapport de reindexation
- Timeout : considerer un timeout genereux cote serveur (10 minutes via `uvicorn --timeout-keep-alive`)

### 7.3 Verrouillage du projet

Les endpoints suivants verifient `project.is_reindexing()` et retournent `409 Conflict` si vrai :

- `POST /projects/{project_id}/documents` (upload)
- `PUT /projects/{project_id}/documents/{document_id}` (remplacement)
- `POST /projects/{project_id}/documents/{document_id}/reindex` (reindex unitaire)
- `POST /projects/{project_id}/reindex` (reindex batch — si deja en cours)
- `POST /projects/{project_id}/chat` (envoi de message)

Les endpoints en lecture restent accessibles :

- `GET /projects/{project_id}`
- `GET /projects/{project_id}/documents`
- `GET /projects/{project_id}/documents/{document_id}/chunks`

### 7.4 Nouvelle exception Domain

```python
class ProjectReindexInProgressError(Exception):
    """Raised when a mutation is attempted on a project being reindexed."""
```

### 7.5 DTO de rapport

```python
@dataclass(frozen=True)
class ReindexReportDTO:
    total: int
    succeeded: int
    failed: int
    errors: list[ReindexErrorDTO]

@dataclass(frozen=True)
class ReindexErrorDTO:
    document_id: UUID
    file_name: str
    error_message: str
```

## 8. Modification du pipeline d'indexation

### 8.1 Nouveau flux dans `DocumentIndexingService.run_pipeline()`

Le service recoit desormais le `Project` en plus du `Document` :

```python
async def run_pipeline(
    self,
    document: Document,
    file_content: bytes,
    project: Project,
) -> Document:
```

**Etapes :**

1. **Extraction du texte** (existant)
2. **Extraction des metadonnees fichier** (nouveau) → `FileMetadataExtractor.extract_metadata(file_content, content_type)`
3. **Detection de langue** (nouveau) → `LanguageDetector.detect_language(extracted_text[:5000])`
4. **Sanitization du texte** (existant)
5. **Extraction des mots-cles** (nouveau) → `KeywordExtractor.extract_keywords(sanitized_text)`
6. **Resolution de la strategie de chunking** :
   - Si `project.chunking_strategy == AUTO` : utiliser le `ChunkingStrategySelector` (existant)
   - Sinon : utiliser `project.chunking_strategy` directement
7. **Chunking** (existant, + routage vers `SemanticTextChunkerService` si `SEMANTIC`)
8. **Parent-child** (nouveau, si `project.parent_child_chunking`)
9. **Embedding** des chunks `child` ou `standard` (existant)
10. **Suppression des anciens chunks** (existant)
11. **Persistance** (existant, avec nouveaux champs `chunk_level` et `parent_chunk_id`)
12. **Mise a jour du document** avec metadonnees : `language`, `keywords`, `authors`, `document_date`, `title`
13. **Retour** du document mis a jour

### 8.2 Nouvelles dependances de `DocumentIndexingService`

```python
class DocumentIndexingService:
    def __init__(
        self,
        document_chunk_repository: DocumentChunkRepository,
        document_text_extractor: DocumentTextExtractor,
        text_sanitizer_service: TextSanitizerService,
        document_structure_analyzer: DocumentStructureAnalyzer,
        text_chunker_service: TextChunkerService,
        embedding_service: EmbeddingService,
        language_detector: LanguageDetector,                      # nouveau
        keyword_extractor: KeywordExtractor,                      # nouveau
        file_metadata_extractor: FileMetadataExtractor,           # nouveau
        parent_child_chunking_service: ParentChildChunkingService, # nouveau
        chunking_strategy_selector: ChunkingStrategySelector | None = None,
        chunker_backend: str = "native",
    ) -> None: ...
```

## 9. Limites et configuration

### 9.1 Modifications dans `Settings`

```python
max_upload_size: int = 10485760          # 10 Mo (etait 104857600)
max_documents_per_project: int = 100     # nouveau
```

### 9.2 Retrait du format `.doc`

Dans `UploadDocument`, retirer `"doc"` de `ALLOWED_EXTENSIONS` :

```python
ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "docx"}  # doc retire
```

### 9.3 Validation du quota projet

Dans `UploadDocument.execute_many()`, avant de traiter chaque fichier :

1. Compter les documents existants du projet
2. Verifier que `count + files_remaining <= max_documents_per_project`
3. Si depasse : rejeter les fichiers excedentaires avec code `PROJECT_DOCUMENT_LIMIT_REACHED`

## 10. Nouvelles dependances Python

| Package | Version | Usage |
|---------|---------|-------|
| `langdetect` | ~0.1.13 | Detection de langue |
| `keybert` | ~0.8 | Extraction de mots-cles (embarque sentence-transformers) |
| `scikit-learn` | ~1.4 | Fallback TF-IDF pour les mots-cles |

A ajouter dans `server/pyproject.toml` sous `[project.dependencies]`.

Note : `keybert` tire `sentence-transformers` qui tire `torch`. L'impact sur la taille de l'image Docker est significatif (~2 Go). Si c'est un probleme, on peut commencer avec TF-IDF uniquement et ajouter KeyBERT plus tard.

## 11. Assemblage dans le conteneur DI

### 11.1 Nouveaux services a instancier dans `dependencies.py`

```python
from raggae.infrastructure.services.langdetect_language_detector import LangdetectLanguageDetector
from raggae.infrastructure.services.keybert_keyword_extractor import KeybertKeywordExtractor
from raggae.infrastructure.services.pdf_docx_file_metadata_extractor import PdfDocxFileMetadataExtractor
from raggae.application.services.parent_child_chunking_service import ParentChildChunkingService

_language_detector = LangdetectLanguageDetector()
_keyword_extractor = KeybertKeywordExtractor()
_file_metadata_extractor = PdfDocxFileMetadataExtractor()
_parent_child_chunking_service = ParentChildChunkingService()

# Embedding service dedie au chunking semantique (meme config que le principal)
_semantic_embedding_service = ...  # meme instanciation que _embedding_service

# Chunker semantique
_semantic_chunker = SemanticTextChunkerService(
    embedding_service=_semantic_embedding_service,
    chunk_size=settings.chunk_size,
)

# Mise a jour de l'AdaptiveTextChunkerService
_text_chunker_service = AdaptiveTextChunkerService(
    fixed_window_chunker=_fixed_window_chunker,
    paragraph_chunker=_paragraph_chunker,
    heading_section_chunker=_heading_section_chunker,
    semantic_chunker=_semantic_chunker,            # nouveau
    context_window_size=settings.chunk_overlap,
)

# Mise a jour de DocumentIndexingService
_document_indexing_service = DocumentIndexingService(
    ...,  # existants
    language_detector=_language_detector,
    keyword_extractor=_keyword_extractor,
    file_metadata_extractor=_file_metadata_extractor,
    parent_child_chunking_service=_parent_child_chunking_service,
)
```

### 11.2 Nouveaux use cases a enregistrer

```python
def get_replace_document_use_case() -> ReplaceDocument: ...
def get_reindex_project_use_case() -> ReindexProject: ...
```

## 12. Migrations Alembic — recapitulatif

4 migrations, dans cet ordre :

| # | Nom | Tables impactees | Description |
|---|-----|-----------------|-------------|
| 1 | `add_document_status_and_metadata` | `documents` | Colonnes `status`, `error_message`, `language`, `keywords`, `authors`, `document_date`, `title` |
| 2 | `add_project_ingestion_settings` | `projects` | Colonnes `chunking_strategy`, `parent_child_chunking`, `reindex_status`, `reindex_progress`, `reindex_total` |
| 3 | `add_parent_child_chunking` | `document_chunks` | Colonnes `chunk_level`, `parent_chunk_id` (FK + index) |
| 4 | `update_limits_remove_doc` | — | Pas de migration schema, mais script de donnees si necessaire |

## 13. Arborescence des fichiers crees/modifies

### Nouveaux fichiers

```
server/src/raggae/
├── domain/
│   ├── value_objects/
│   │   ├── document_status.py                    # enum DocumentStatus
│   │   └── chunk_level.py                        # enum ChunkLevel
│   └── exceptions/
│       ├── document_exceptions.py                # + InvalidDocumentStatusTransitionError
│       └── project_exceptions.py                 # + ProjectReindexInProgressError
├── application/
│   ├── interfaces/services/
│   │   ├── language_detector.py                  # Protocol
│   │   ├── keyword_extractor.py                  # Protocol
│   │   └── file_metadata_extractor.py            # Protocol + FileMetadata dataclass
│   ├── dto/
│   │   └── reindex_report_dto.py                 # ReindexReportDTO, ReindexErrorDTO
│   ├── services/
│   │   └── parent_child_chunking_service.py      # ParentChildChunkingService
│   └── use_cases/
│       ├── document/
│       │   └── replace_document.py               # ReplaceDocument
│       └── project/
│           └── reindex_project.py                # ReindexProject
└── infrastructure/
    └── services/
        ├── langdetect_language_detector.py        # LangdetectLanguageDetector
        ├── keybert_keyword_extractor.py           # KeybertKeywordExtractor
        ├── pdf_docx_file_metadata_extractor.py    # PdfDocxFileMetadataExtractor
        └── semantic_text_chunker_service.py       # SemanticTextChunkerService
```

### Fichiers modifies

```
server/src/raggae/
├── domain/
│   ├── entities/document.py                       # + status, error_message, metadonnees, transition_to()
│   ├── entities/document_chunk.py                 # + chunk_level, parent_chunk_id
│   ├── entities/project.py                        # + chunking_strategy, parent_child_chunking, reindex_*
│   └── value_objects/chunking_strategy.py         # + AUTO, SEMANTIC
├── application/
│   ├── services/document_indexing_service.py      # pipeline etendu, signature run_pipeline modifiee
│   └── use_cases/document/upload_document.py      # doublon → rejet, quota projet, retrait .doc
├── infrastructure/
│   ├── config/settings.py                         # max_upload_size, max_documents_per_project
│   ├── database/models/document_model.py          # + nouvelles colonnes
│   ├── database/models/document_chunk_model.py    # + chunk_level, parent_chunk_id
│   ├── database/models/project_model.py           # + nouvelles colonnes
│   └── services/adaptive_text_chunker_service.py  # + routage SEMANTIC
└── presentation/
    ├── api/dependencies.py                        # assemblage nouveaux services
    └── api/v1/endpoints/
        ├── documents.py                           # + PUT replace, modification upload
        └── projects.py                            # + POST reindex, PATCH settings
```

## 14. Strategie de tests

### 14.1 Tests unitaires (prioritaires)

| Composant | Tests |
|-----------|-------|
| `Document.transition_to()` | Transitions valides, transitions invalides → exception |
| `LangdetectLanguageDetector` | Texte francais → `"fr"`, texte anglais → `"en"`, texte vide → `None` |
| `KeybertKeywordExtractor` | Texte normal → liste de mots-cles, texte vide → `[]`, fallback TF-IDF |
| `PdfDocxFileMetadataExtractor` | PDF avec metadonnees, PDF sans, DOCX avec, TXT → vide |
| `SemanticTextChunkerService` | Texte avec rupture semantique, texte homogene, chunk trop long → fallback |
| `ParentChildChunkingService` | Split correct parent/enfant, tailles respectees |
| `ReplaceDocument` | Remplacement OK, document inexistant, projet en reindexation |
| `ReindexProject` | Batch complet, echec partiel, projet deja en reindexation |

### 14.2 Tests d'integration

- Pipeline complet avec metadonnees (extraction → sanitize → detect langue → chunk → embed → persist)
- Reindexation batch avec base PostgreSQL
- Remplacement de document avec storage MinIO

### 14.3 Fakes pour les tests

- `InMemoryLanguageDetector`
- `InMemoryKeywordExtractor`
- `InMemoryFileMetadataExtractor`
