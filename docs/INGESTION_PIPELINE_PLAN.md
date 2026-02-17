# Plan operationnel — Pipeline d'ingestion v1

> Ref: [Spec fonctionnelle](./INGESTION_PIPELINE_SPEC.md) | [Spec technique](./INGESTION_PIPELINE_TECH_SPEC.md)

## Vue d'ensemble

6 epics, 28 stories, ordonnees par dependances. Chaque story est implementable en TDD (red-green-refactor) et donne lieu a un ou plusieurs commits atomiques.

---

## Epic 1 — Cycle de vie du document (fondation)

> Prerequis pour tous les autres epics. Introduit les etats, les transitions protegees et la migration associee.

### Story 1.1 — Creer le value object `DocumentStatus`

**En tant que** developpeur,
**je veux** un `StrEnum` `DocumentStatus` dans la couche Domain,
**afin de** representer les etats d'un document de facon type-safe.

**Taches :**
- [ ] Creer `server/src/raggae/domain/value_objects/document_status.py` avec `UPLOADED`, `PROCESSING`, `INDEXED`, `ERROR`
- [ ] Tests unitaires : valeurs, serialisation string

### Story 1.2 — Ajouter les transitions protegees a l'entite `Document`

**En tant que** developpeur,
**je veux** que `Document.transition_to(status)` valide les transitions autorisees,
**afin de** garantir l'integrite du cycle de vie au niveau du domaine.

**Taches :**
- [ ] Ajouter les champs `status` (defaut `UPLOADED`) et `error_message` a l'entite `Document`
- [ ] Implementer `transition_to(status, error_message=None)` avec la table de transitions
- [ ] Creer `InvalidDocumentStatusTransitionError` dans `document_exceptions.py`
- [ ] Tests unitaires : toutes les transitions valides, toutes les transitions invalides → exception

### Story 1.3 — Migration Alembic `add_document_status_and_metadata`

**En tant que** developpeur,
**je veux** ajouter les colonnes `status` et `error_message` a la table `documents`,
**afin de** persister les etats.

**Taches :**
- [ ] Creer la migration : `status VARCHAR(16) NOT NULL DEFAULT 'indexed'`, `error_message TEXT NULL`
- [ ] Ajouter aussi les colonnes de metadonnees (story 2.x) dans la meme migration : `language`, `keywords`, `authors`, `document_date`, `title`
- [ ] Mettre a jour `DocumentModel` avec les nouvelles colonnes
- [ ] Mettre a jour le mapping entite ↔ modele dans le repository
- [ ] Test d'integration : migration up/down

### Story 1.4 — Integrer les transitions d'etat dans le pipeline existant

**En tant que** developpeur,
**je veux** que `UploadDocument` et `ReindexDocument` utilisent les transitions d'etat,
**afin que** chaque document passe par `uploaded → processing → indexed | error`.

**Taches :**
- [ ] Modifier `UploadDocument` : creer le document en `uploaded`, transition vers `processing` avant le pipeline, vers `indexed` ou `error` apres
- [ ] Modifier `ReindexDocument` : transition `indexed → processing → indexed | error`
- [ ] Mettre a jour les reponses API pour inclure `status` et `error_message`
- [ ] Mettre a jour le client pour afficher le statut
- [ ] Tests unitaires et d'integration

### Story 1.5 — Ajuster les limites et retirer `.doc`

**En tant que** developpeur,
**je veux** reduire la taille max a 10 Mo, limiter a 100 docs/projet et retirer `.doc`,
**afin de** correspondre au perimetre v1.

**Taches :**
- [ ] Modifier `settings.py` : `max_upload_size = 10485760`, ajouter `max_documents_per_project = 100`
- [ ] Modifier `UploadDocument` : retirer `"doc"` de `ALLOWED_EXTENSIONS`
- [ ] Ajouter la validation du quota projet (compter les documents existants avant upload)
- [ ] Nouveau code d'erreur `PROJECT_DOCUMENT_LIMIT_REACHED`
- [ ] Tests unitaires : quota atteint, format .doc rejete

---

## Epic 2 — Extraction de metadonnees

> Depend de l'Epic 1 (colonnes de metadonnees creees en story 1.3).

### Story 2.1 — Service de detection de langue

**En tant que** systeme,
**je veux** detecter automatiquement la langue d'un document,
**afin d'** enrichir les metadonnees pour le retrieval.

**Taches :**
- [ ] Ajouter `langdetect` dans `pyproject.toml`
- [ ] Creer l'interface `LanguageDetector` (Protocol) dans `application/interfaces/services/`
- [ ] Implementer `LangdetectLanguageDetector` dans `infrastructure/services/`
- [ ] Creer `InMemoryLanguageDetector` pour les tests
- [ ] Tests unitaires : texte francais → `"fr"`, texte anglais → `"en"`, texte vide → `None`, texte trop court → `None`

### Story 2.2 — Service d'extraction de mots-cles

**En tant que** systeme,
**je veux** extraire automatiquement les mots-cles d'un document,
**afin d'** enrichir les metadonnees pour le retrieval et l'affichage.

**Taches :**
- [ ] Ajouter `keybert` et `scikit-learn` dans `pyproject.toml`
- [ ] Creer l'interface `KeywordExtractor` (Protocol) dans `application/interfaces/services/`
- [ ] Implementer `KeybertKeywordExtractor` avec lazy loading du modele et fallback TF-IDF
- [ ] Creer `InMemoryKeywordExtractor` pour les tests
- [ ] Tests unitaires : texte normal → liste de mots-cles, texte vide → `[]`, fallback TF-IDF quand KeyBERT echoue

### Story 2.3 — Service d'extraction de metadonnees fichier

**En tant que** systeme,
**je veux** extraire titre, auteur et date depuis les proprietes des fichiers PDF et DOCX,
**afin d'** enrichir les metadonnees sans cout supplementaire.

**Taches :**
- [ ] Creer l'interface `FileMetadataExtractor` (Protocol) + `FileMetadata` dataclass dans `application/interfaces/services/`
- [ ] Implementer `PdfDocxFileMetadataExtractor` (pypdf + python-docx, deja disponibles)
- [ ] Creer `InMemoryFileMetadataExtractor` pour les tests
- [ ] Tests unitaires : PDF avec metadonnees, PDF sans, DOCX avec metadonnees, TXT → `FileMetadata()` vide
- [ ] Tests avec fichiers de test reels (fixtures)

### Story 2.4 — Integrer les 3 extracteurs dans le pipeline

**En tant que** systeme,
**je veux** que le pipeline d'indexation appelle les 3 extracteurs de metadonnees,
**afin que** chaque document indexe soit enrichi automatiquement.

**Taches :**
- [ ] Ajouter les 3 services en dependances de `DocumentIndexingService`
- [ ] Inserer les appels dans `run_pipeline()` : metadonnees fichier → langue → (sanitize) → mots-cles
- [ ] Mettre a jour le document avec les metadonnees extraites (`replace()`)
- [ ] L'echec d'un extracteur ne bloque pas le pipeline (try/except, log warning)
- [ ] Assembler dans `dependencies.py`
- [ ] Mettre a jour `DocumentResponse` pour inclure les metadonnees
- [ ] Tests unitaires du pipeline avec fakes
- [ ] Test d'integration : upload d'un PDF avec metadonnees → verification en base

---

## Epic 3 — Chunking configurable et semantique

> Depend de l'Epic 1 (etats du document). Independant de l'Epic 2.

### Story 3.1 — Etendre `ChunkingStrategy` avec `AUTO` et `SEMANTIC`

**En tant que** developpeur,
**je veux** ajouter `AUTO` et `SEMANTIC` au `StrEnum` `ChunkingStrategy`,
**afin de** supporter les nouvelles strategies.

**Taches :**
- [ ] Ajouter `AUTO = "auto"` et `SEMANTIC = "semantic"` dans `ChunkingStrategy`
- [ ] Verifier que le `DeterministicChunkingStrategySelector` ne retourne jamais `AUTO` ni `SEMANTIC`
- [ ] Tests unitaires

### Story 3.2 — Ajouter `chunking_strategy` au projet

**En tant qu'** utilisateur,
**je veux** choisir la strategie de chunking pour mon projet,
**afin de** controler la facon dont mes documents sont decoupes.

**Taches :**
- [ ] Migration Alembic `add_project_ingestion_settings` : colonnes `chunking_strategy`, `parent_child_chunking`, `reindex_status`, `reindex_progress`, `reindex_total` sur `projects`
- [ ] Ajouter les champs a l'entite `Project`
- [ ] Mettre a jour `ProjectModel` et le mapping repository
- [ ] Modifier `UpdateProject` pour accepter `chunking_strategy` et `parent_child_chunking`
- [ ] Modifier l'endpoint `PATCH /projects/{project_id}` pour exposer ces champs
- [ ] Mettre a jour `ProjectResponse` pour les inclure
- [ ] Tests unitaires et d'integration

### Story 3.3 — Implementer le `SemanticTextChunkerService`

**En tant que** systeme,
**je veux** decouper un texte selon les ruptures de similarite semantique,
**afin de** produire des chunks plus coherents sur les documents peu structures.

**Taches :**
- [ ] Creer `SemanticTextChunkerService` implementant `TextChunkerService`
- [ ] Injecter un `EmbeddingService` dedie (distinct du principal)
- [ ] Implementer l'algorithme : sentence split (regex) → embed → cosine similarity → coupure → regroupement → fallback taille fixe
- [ ] Tests unitaires avec `InMemoryEmbeddingService` : texte avec rupture semantique, texte homogene, chunk trop long

### Story 3.4 — Integrer le chunking semantique dans le routage

**En tant que** systeme,
**je veux** que `AdaptiveTextChunkerService` route vers `SemanticTextChunkerService`,
**afin que** la strategie semantique soit utilisable.

**Taches :**
- [ ] Ajouter `semantic_chunker` en parametre de `AdaptiveTextChunkerService`
- [ ] Ajouter le case `SEMANTIC` dans le routage
- [ ] Instancier le chunker semantique et son `EmbeddingService` dedie dans `dependencies.py`
- [ ] Tests unitaires du routage

### Story 3.5 — Resoudre `AUTO` depuis le projet dans le pipeline

**En tant que** systeme,
**je veux** que le pipeline utilise la strategie du projet (et resolve `AUTO` via le selecteur),
**afin que** la configuration projet soit respectee.

**Taches :**
- [ ] Modifier la signature de `run_pipeline()` pour recevoir `Project`
- [ ] Lire `project.chunking_strategy` au lieu d'appeler le selecteur directement
- [ ] Si `AUTO` : utiliser le `ChunkingStrategySelector` existant
- [ ] Sinon : utiliser la strategie du projet directement
- [ ] Mettre a jour tous les appelants (`UploadDocument`, `ReindexDocument`)
- [ ] Tests unitaires

---

## Epic 4 — Parent-child chunking

> Depend de l'Epic 3 (strategie de chunking configuree sur le projet).

### Story 4.1 — Creer le value object `ChunkLevel` et la migration

**En tant que** developpeur,
**je veux** un `StrEnum` `ChunkLevel` et les colonnes associees,
**afin de** differencier chunks standard, parents et enfants.

**Taches :**
- [ ] Creer `server/src/raggae/domain/value_objects/chunk_level.py`
- [ ] Ajouter `chunk_level` et `parent_chunk_id` a l'entite `DocumentChunk`
- [ ] Migration Alembic `add_parent_child_chunking` : `chunk_level VARCHAR(16) NOT NULL DEFAULT 'standard'`, `parent_chunk_id UUID NULL` avec FK et index
- [ ] Mettre a jour `DocumentChunkModel` et le mapping repository
- [ ] Tests unitaires

### Story 4.2 — Implementer le `ParentChildChunkingService`

**En tant que** systeme,
**je veux** transformer une liste de chunks en paires parent/enfants,
**afin de** supporter le pattern parent-child.

**Taches :**
- [ ] Creer `ParentChildChunkingService` dans `application/services/`
- [ ] Implementer `split_into_parent_child(chunks) -> list[tuple[str, list[str]]]`
- [ ] Algorithme : regrouper en parents (~2000 chars), re-decouper en enfants (~500 chars, overlap 50)
- [ ] Tests unitaires : tailles respectees, mapping parent→enfants correct, cas limites (chunk unique, chunk geant)

### Story 4.3 — Integrer le parent-child dans le pipeline

**En tant que** systeme,
**je veux** que le pipeline cree des chunks parent et enfant quand l'option est activee,
**afin que** les documents du projet beneficient du pattern parent-child.

**Taches :**
- [ ] Dans `DocumentIndexingService.run_pipeline()` : si `project.parent_child_chunking`, appeler `ParentChildChunkingService`
- [ ] Creer les `DocumentChunk` parents avec `embedding=[]` et `chunk_level=PARENT`
- [ ] Creer les `DocumentChunk` enfants avec embedding et `chunk_level=CHILD`, `parent_chunk_id` pointe vers le parent
- [ ] Assembler dans `dependencies.py`
- [ ] Tests unitaires avec fakes
- [ ] Test d'integration : upload avec parent-child → verification chunks en base

### Story 4.4 — Adapter le retrieval pour le parent-child

**En tant que** systeme,
**je veux** que la recherche vectorielle ignore les chunks parents et remonte le contexte parent,
**afin que** le LLM dispose d'un contexte riche.

**Taches :**
- [ ] Modifier `SQLAlchemyChunkRetrievalService` : filtrer `chunk_level IN ('standard', 'child')`
- [ ] Modifier `QueryRelevantChunks` : quand un chunk `child` est selectionne, charger le parent via `parent_chunk_id`
- [ ] Injecter le contenu du parent dans le contexte LLM (a la place de l'enfant)
- [ ] Mettre a jour l'endpoint de consultation des chunks pour afficher `chunk_level` et `parent_chunk_id`
- [ ] Tests unitaires et d'integration

---

## Epic 5 — Gestion des doublons et remplacement

> Depend de l'Epic 1 (etats du document).

### Story 5.1 — Rejeter les doublons par nom a l'upload

**En tant qu'** utilisateur,
**je veux** etre informe quand j'uploade un fichier dont le nom existe deja,
**afin de** decider si je veux le remplacer.

**Taches :**
- [ ] Modifier `UploadDocument.execute_many()` : remplacer le renommage `-copie-#` par un rejet `DUPLICATE_FILENAME`
- [ ] Le message d'erreur inclut l'ID du document existant
- [ ] Les autres fichiers du batch continuent normalement
- [ ] Tests unitaires : batch avec doublons → fichiers valides passes, doublons rejetes
- [ ] Mettre a jour le client pour afficher le message de doublon

### Story 5.2 — Implementer le use case `ReplaceDocument`

**En tant qu'** utilisateur,
**je veux** remplacer un document existant par une nouvelle version,
**afin de** mettre a jour le contenu sans creer de doublon.

**Taches :**
- [ ] Creer `ReplaceDocument` use case
- [ ] Flux : verification owner/projet/document → validation fichier → suppression chunks → remplacement storage → mise a jour document → pipeline → status indexed|error
- [ ] Verifier que le projet n'est pas en reindexation (→ 409)
- [ ] Creer l'endpoint `PUT /projects/{project_id}/documents/{document_id}`
- [ ] Assembler dans `dependencies.py`
- [ ] Tests unitaires avec fakes
- [ ] Test d'integration
- [ ] Mettre a jour le client : bouton "Remplacer" sur un document existant

---

## Epic 6 — Reindexation batch

> Depend des Epics 1, 3 et 4 (etats, strategie projet, parent-child). A implementer en dernier.

### Story 6.1 — Ajouter les methodes de reindexation a l'entite `Project`

**En tant que** developpeur,
**je veux** que `Project` expose `start_reindex()`, `advance_reindex()`, `finish_reindex()`,
**afin de** gerer le cycle de reindexation au niveau du domaine.

**Taches :**
- [ ] Implementer les 3 methodes + `is_reindexing()`
- [ ] Creer `ProjectReindexInProgressError` dans `project_exceptions.py`
- [ ] Tests unitaires : demarrage, progression, fin, double demarrage → exception

### Story 6.2 — Implementer le use case `ReindexProject`

**En tant qu'** utilisateur,
**je veux** reindexer tous les documents de mon projet en un clic,
**afin de** prendre en compte un changement de strategie ou corriger des erreurs.

**Taches :**
- [ ] Creer `ReindexProject` use case
- [ ] Flux : verification owner → start_reindex → boucle sur documents (processing → pipeline → indexed|error → advance) → finish_reindex → rapport
- [ ] Creer `ReindexReportDTO` et `ReindexErrorDTO`
- [ ] Tests unitaires avec fakes : batch complet OK, echec partiel, projet deja en reindexation

### Story 6.3 — Creer l'endpoint et le verrouillage

**En tant qu'** utilisateur,
**je veux** que le projet soit en lecture seule pendant la reindexation,
**afin d'** eviter les conflits.

**Taches :**
- [ ] Creer l'endpoint `POST /projects/{project_id}/reindex` (requete bloquante)
- [ ] Ajouter la verification `is_reindexing()` → `409 Conflict` sur les endpoints de mutation : upload, replace, reindex unitaire, reindex batch, chat
- [ ] Assembler dans `dependencies.py`
- [ ] Tests d'integration : reindexation complete, tentative d'upload pendant reindex → 409

### Story 6.4 — Affichage cote client

**En tant qu'** utilisateur,
**je veux** voir un bandeau de progression pendant la reindexation et un rapport a la fin,
**afin de** suivre l'avancement.

**Taches :**
- [ ] Afficher le bandeau "Reindexation en cours (X/N)" quand `reindex_status == "in_progress"` sur `GET /projects/{project_id}`
- [ ] Desactiver les boutons d'upload, chat et reindex pendant la reindexation
- [ ] Afficher le rapport de fin (X reussis, Y en erreur) apres refresh
- [ ] Afficher les documents en erreur avec leur message

---

## Ordre d'implementation recommande

```
Epic 1 — Cycle de vie (fondation)
  │
  ├──→ Epic 2 — Metadonnees (independant des Epics 3-6)
  │
  ├──→ Epic 3 — Chunking configurable
  │      │
  │      └──→ Epic 4 — Parent-child
  │
  ├──→ Epic 5 — Doublons et remplacement (independant des Epics 3-4)
  │
  └──→ Epic 6 — Reindexation batch (depend de 1, 3, 4)
```

**Parallelisation possible :**
- Epics 2 et 3 peuvent etre travailles en parallele apres l'Epic 1
- Epic 5 peut etre travaille en parallele avec 3 et 4
- Epic 6 doit attendre 1, 3 et 4

**Estimation en stories :** 28 stories au total
- Epic 1 : 5 stories (fondation, a faire en premier)
- Epic 2 : 4 stories
- Epic 3 : 5 stories
- Epic 4 : 4 stories
- Epic 5 : 2 stories
- Epic 6 : 4 stories
- Client (transversal) : 4 stories (1.4, 5.1, 5.2, 6.4)
