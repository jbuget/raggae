# Specifications fonctionnelles — Pipeline d'ingestion v1

## 1. Contexte

Le pipeline d'ingestion est le processus qui transforme un fichier brut uploade par l'utilisateur en chunks vectorises exploitables par le moteur de recherche (retrieval). C'est l'etape la plus determinante pour la qualite des reponses du chatbot.

Aujourd'hui, le pipeline existe sous forme basique : extraction texte (pypdf, python-docx, UTF-8), sanitization, analyse structurelle heuristique, chunking (3 strategies), embedding (OpenAI/Ollama), stockage pgvector. Cette spec definit les evolutions v1 pour ameliorer la qualite du retrieval.

## 2. Objectifs v1

- Ajouter des etats explicites au cycle de vie d'un document
- Gerer le remplacement de documents existants (doublon par nom)
- Extraire automatiquement des metadonnees (langue, mots-cles, metadonnees fichier)
- Proposer 5 strategies de chunking configurables par projet (dont chunking semantique)
- Supporter le pattern parent-child chunking (option par projet)
- Permettre la reindexation batch d'un projet avec suivi de progression
- Ajuster les limites (10 Mo/fichier, 100 docs/projet)

## 3. Cycle de vie d'un document

### 3.1 Etats

Un document suit le cycle de vie suivant :

```
uploaded → processing → indexed
               ↓
             error
```

| Etat | Description |
|------|-------------|
| `uploaded` | Fichier stocke, pas encore indexe |
| `processing` | Extraction, chunking et embedding en cours |
| `indexed` | Chunks et embeddings disponibles, document exploitable pour le retrieval |
| `error` | L'ingestion a echoue ; un message d'erreur est associe |

### 3.2 Transitions autorisees

| Depuis | Vers | Declencheur |
|--------|------|-------------|
| `uploaded` | `processing` | Lancement de l'indexation (auto a l'upload si `processing_mode=sync`, ou manuel) |
| `processing` | `indexed` | Pipeline termine avec succes |
| `processing` | `error` | Echec d'une etape du pipeline |
| `indexed` | `processing` | Reindexation manuelle (document ou batch) |
| `error` | `processing` | Relance manuelle de l'indexation |

### 3.3 Stockage

- Nouveau champ `status` sur l'entite Document : `uploaded | processing | indexed | error`
- Nouveau champ `error_message` (nullable) : message d'erreur en cas d'echec
- Migration Alembic requise

## 4. Gestion des doublons (remplacement de document)

### 4.1 Regles

- La detection de doublon se fait par **nom de fichier** au sein d'un meme projet
- Quand un fichier uploade porte le meme nom qu'un document existant dans le projet :
  - L'API rejette le fichier avec le code d'erreur `DUPLICATE_FILENAME`
  - Le message d'erreur indique le nom du fichier et l'ID du document existant
- L'utilisateur peut ensuite choisir explicitement de **remplacer** le document existant via un endpoint dedie

### 4.2 Endpoint de remplacement

- `PUT /projects/{project_id}/documents/{document_id}` avec le nouveau fichier
- Comportement :
  1. Supprime les chunks existants du document
  2. Remplace le fichier en storage
  3. Met a jour les metadonnees du document (taille, content_type, date)
  4. Relance le pipeline d'indexation
- Reponse : le document mis a jour avec son nouveau statut

### 4.3 Comportement en upload batch

- Les fichiers sans doublon sont uploades et traites normalement
- Les fichiers en doublon sont rejetes avec `DUPLICATE_FILENAME` dans la liste `errors`
- Le traitement n'est pas bloque : les fichiers valides passent, les doublons sont signales

### 4.4 Codes d'erreur

- `DUPLICATE_FILENAME` : un document avec ce nom existe deja dans le projet (ajout au contrat existant)

## 5. Metadonnees automatiques

### 5.1 Perimetre v1

Seules les metadonnees extractibles automatiquement, de facon deterministe, rapide et sans cout externe sont dans le scope.

| Metadonnee | Niveau | Methode d'extraction | Stockage |
|-----------|--------|---------------------|----------|
| **Langue** | Document | `langdetect` sur le texte extrait | Champ `language` (code ISO 639-1, ex: `fr`, `en`) |
| **Mots-cles** | Document | TF-IDF ou KeyBERT (local, sans appel LLM) | Champ `keywords` (liste de strings, max 10) |
| **Auteur(s)** | Document | Proprietes du fichier PDF/DOCX (si disponibles) | Champ `authors` (liste de strings, nullable) |
| **Date du document** | Document | Proprietes du fichier PDF/DOCX (si disponibles) | Champ `document_date` (date, nullable) |
| **Titre** | Document | Proprietes du fichier PDF/DOCX (si disponibles) | Champ `title` (string, nullable) |

### 5.2 Moment d'extraction

Les metadonnees sont extraites pendant la phase `processing`, apres l'extraction du texte :

1. Extraction du texte brut
2. **Extraction des metadonnees fichier** (auteur, date, titre) a partir du fichier source
3. **Detection de langue** sur le texte extrait
4. Sanitization du texte
5. **Extraction des mots-cles** sur le texte sanitise
6. Analyse structurelle, chunking, embedding (pipeline existant)

### 5.3 Regles

- La detection de langue s'effectue sur les 5000 premiers caracteres du texte extrait (suffisant pour une detection fiable)
- Les mots-cles sont extraits sur le texte complet, limites a 10 par document
- Les metadonnees fichier sont extraites en best-effort : si le fichier ne contient pas l'information, le champ reste `null`
- Pour les fichiers TXT et MD, les metadonnees fichier (auteur, date, titre) ne sont pas disponibles ; seuls langue et mots-cles sont extraits

### 5.4 Affichage

- Les metadonnees sont visibles dans le detail d'un document (endpoint existant et interface client)
- Les metadonnees sont incluses dans la reponse `DocumentResponse`

## 6. Chunking

### 6.1 Strategies disponibles

5 strategies de chunking sont exposees, configurables au niveau du projet :

| Strategie | Identifiant | Description |
|-----------|-------------|-------------|
| **Automatique** | `auto` | Selection heuristique basee sur l'analyse structurelle du document (comportement actuel) |
| **Taille fixe** | `fixed_window` | Decoupe a taille fixe avec overlap (existant) |
| **Paragraphe** | `paragraph` | Decoupe sur les frontieres de paragraphes (existant) |
| **Sections / titres** | `heading_section` | Decoupe sur les frontieres de titres (existant) |
| **Semantique** | `semantic` | Decoupe basee sur les ruptures de similarite semantique entre phrases consecutives (nouveau) |

### 6.2 Configuration par projet

- Nouveau champ `chunking_strategy` sur l'entite Project : valeur parmi `auto | fixed_window | paragraph | heading_section | semantic`
- Valeur par defaut : `auto`
- Modifiable via `PATCH /projects/{project_id}`
- Tous les documents du projet utilisent cette strategie
- Le changement de strategie ne declenche pas automatiquement de reindexation ; l'utilisateur doit lancer une reindexation batch manuellement

### 6.3 Chunking semantique — comportement

- Decouper le texte en phrases (sentence boundary detection)
- Calculer les embeddings de chaque phrase via le modele d'embedding global
- Mesurer la similarite cosinus entre phrases consecutives
- Couper aux endroits ou la similarite chute sous un seuil (deterministe, configurable en interne)
- Regrouper les phrases entre deux coupures en un chunk
- Si un chunk depasse la taille maximale, appliquer un split secondaire (taille fixe avec overlap)

### 6.4 Parametres internes (non exposes a l'utilisateur en v1)

| Parametre | Valeur par defaut | Description |
|-----------|-------------------|-------------|
| `chunk_size` | 1000 caracteres | Taille cible d'un chunk |
| `chunk_overlap` | 100 caracteres | Chevauchement entre chunks adjacents (strategies fixe et paragraphe) |
| `semantic_similarity_threshold` | 0.5 | Seuil de similarite pour le chunking semantique |

## 7. Parent-child chunking

### 7.1 Principe

Quand cette option est activee sur un projet :
- Chaque document produit **deux niveaux de chunks** :
  - **Chunks enfants** (petits, precis) : utilises pour la recherche vectorielle (retrieval)
  - **Chunks parents** (plus larges, contextuels) : injectes dans le prompt du LLM quand un chunk enfant est selectionne
- L'objectif : precision de la recherche (petits chunks) + richesse du contexte pour la generation (grands chunks)

### 7.2 Configuration

- Nouveau champ `parent_child_chunking` sur l'entite Project : `bool`, defaut `false`
- Modifiable via `PATCH /projects/{project_id}`
- S'applique a tous les documents du projet
- Le changement ne declenche pas de reindexation automatique

### 7.3 Generation des chunks

Quand `parent_child_chunking = true` :

1. **Chunks parents** : generes avec la strategie de chunking du projet, taille cible ~2000 caracteres
2. **Chunks enfants** : chaque chunk parent est re-decoupe en sous-chunks de ~500 caracteres avec overlap
3. Les chunks enfants recoivent les embeddings (vectorises)
4. Les chunks parents ne sont pas vectorises ; ils sont stockes comme reference

### 7.4 Modele de donnees

- Nouveau champ `parent_chunk_id` sur l'entite DocumentChunk : UUID nullable, reference vers le chunk parent
- Nouveau champ `chunk_level` sur l'entite DocumentChunk : `parent | child | standard`
  - `standard` : chunk classique (quand parent-child est desactive)
  - `parent` : chunk parent (pas d'embedding)
  - `child` : chunk enfant (avec embedding, lie a un parent)
- Les chunks parents ont un embedding `null` (ou vecteur zero) puisqu'ils ne servent pas au retrieval vectoriel
- Migration Alembic requise

### 7.5 Affichage

- Les chunks parents ET enfants sont visibles dans l'interface de consultation des chunks (pour le debug)
- Les chunks enfants affichent une reference vers leur chunk parent
- Distinction visuelle entre les deux niveaux (label ou icone)

### 7.6 Impact sur le retrieval

- La recherche vectorielle s'effectue uniquement sur les chunks de niveau `child` (ou `standard`)
- Quand un chunk enfant est selectionne, le contenu du chunk parent est injecte dans le contexte du LLM a la place du chunk enfant

## 8. Reindexation batch

### 8.1 Declenchement

- Endpoint : `POST /projects/{project_id}/reindex`
- Declenchement : manuel uniquement (bouton dans l'interface)
- Seul l'owner du projet peut declencher la reindexation
- Non declenchee automatiquement lors d'un changement de parametres (strategie, parent-child)

### 8.2 Comportement

1. Le projet passe en etat **lecture seule** :
   - Consultation des documents et chunks : autorisee
   - Upload de documents, chat, recherche : interdits
   - L'interface affiche un bandeau "Reindexation en cours (X/N documents)"
2. Tous les documents du projet en etat `indexed` ou `error` sont reindexes sequentiellement
3. Chaque document suit le cycle : `status → processing → indexed | error`
4. Si un document echoue, il passe en `error` et le batch continue sur les documents suivants
5. A la fin du batch, le projet quitte le mode lecture seule

### 8.3 Suivi de progression

- Nouveau champ `reindex_status` sur l'entite Project : `null | in_progress`
- Nouveaux champs `reindex_progress` et `reindex_total` sur l'entite Project (integers, nullables)
- Endpoint de consultation : `GET /projects/{project_id}` retourne les champs de progression
- Le client affiche la progression au chargement de la page ; un simple refresh suffit pour mettre a jour

### 8.4 Rapport de fin

A la fin de la reindexation :
- `reindex_status` repasse a `null`
- L'API retourne (ou le client affiche) un resume : "X documents reindexes, Y en erreur"
- Les documents en erreur sont consultables individuellement pour voir le message d'erreur

### 8.5 Codes d'erreur

- `PROJECT_REINDEXING` : le projet est en cours de reindexation, l'action demandee est temporairement interdite (HTTP 409 Conflict)

## 9. Limites et garde-fous

### 9.1 Limites v1

| Limite | Valeur | Actuelle | Changement |
|--------|--------|----------|------------|
| Taille max par fichier | 10 Mo | 100 Mo | Reduction |
| Nombre max de fichiers par requete d'upload | 20 | 20 | Inchange |
| Nombre max de documents par projet | 100 | Illimite | Nouveau |
| Formats autorises | txt, md, pdf, docx | txt, md, pdf, doc, docx | Retrait de `doc` |

### 9.2 Gestion des erreurs d'ingestion

- Si l'extraction de texte echoue : le document passe en `error` avec le message d'erreur
- Si la generation d'embeddings echoue : le document passe en `error`, les chunks partiels sont supprimes
- Si l'extraction de metadonnees echoue : **l'ingestion continue** (les metadonnees sont best-effort, pas bloquantes)
- En upload batch : les erreurs d'un fichier n'affectent pas les autres fichiers
- En reindexation batch : les erreurs d'un document n'affectent pas les autres documents

### 9.3 Validation a l'upload

- Verifier le format du fichier (extension) avant tout traitement
- Verifier la taille du fichier avant tout traitement
- Verifier le nombre de documents du projet (rejet si >= 100)
- Verifier les doublons par nom de fichier

## 10. Pipeline d'ingestion — flux complet v1

```
Fichier uploade
    │
    ├─ Validations (format, taille, quota projet, doublon nom)
    │
    ├─ Stockage du fichier (storage backend)
    │
    ├─ Creation du document en base (status = uploaded)
    │
    ├─ Lancement du pipeline (status → processing)
    │   │
    │   ├─ 1. Extraction du texte (pypdf, python-docx, UTF-8)
    │   │
    │   ├─ 2. Extraction des metadonnees fichier (auteur, date, titre)
    │   │
    │   ├─ 3. Detection de langue (langdetect)
    │   │
    │   ├─ 4. Sanitization du texte
    │   │
    │   ├─ 5. Extraction des mots-cles (TF-IDF / KeyBERT)
    │   │
    │   ├─ 6. Chunking (selon strategie du projet)
    │   │      Si parent-child active :
    │   │        → Generer chunks parents (taille ~2000 chars)
    │   │        → Decouper en chunks enfants (~500 chars)
    │   │      Sinon :
    │   │        → Generer chunks standard
    │   │
    │   ├─ 7. Embedding des chunks (enfants ou standard uniquement)
    │   │
    │   ├─ 8. Suppression des anciens chunks (si reindexation)
    │   │
    │   └─ 9. Persistance des chunks en base (pgvector)
    │
    └─ status → indexed (succes) ou error (echec)
```

## 11. Impact sur le modele de donnees

### 11.1 Entite Document — nouveaux champs

| Champ | Type | Nullable | Defaut | Description |
|-------|------|----------|--------|-------------|
| `status` | `string` (enum) | non | `uploaded` | Etat du document |
| `error_message` | `string` | oui | `null` | Message d'erreur si `status = error` |
| `language` | `string` (ISO 639-1) | oui | `null` | Langue detectee |
| `keywords` | `list[string]` | oui | `null` | Mots-cles extraits (max 10) |
| `authors` | `list[string]` | oui | `null` | Auteurs extraits du fichier |
| `document_date` | `date` | oui | `null` | Date extraite du fichier |
| `title` | `string` | oui | `null` | Titre extrait du fichier |

### 11.2 Entite DocumentChunk — nouveaux champs

| Champ | Type | Nullable | Defaut | Description |
|-------|------|----------|--------|-------------|
| `chunk_level` | `string` (enum) | non | `standard` | `standard`, `parent` ou `child` |
| `parent_chunk_id` | `UUID` | oui | `null` | Reference vers le chunk parent (si `child`) |

### 11.3 Entite Project — nouveaux champs

| Champ | Type | Nullable | Defaut | Description |
|-------|------|----------|--------|-------------|
| `chunking_strategy` | `string` (enum) | non | `auto` | Strategie de chunking du projet |
| `parent_child_chunking` | `bool` | non | `false` | Activation du parent-child chunking |
| `reindex_status` | `string` | oui | `null` | `null` ou `in_progress` |
| `reindex_progress` | `int` | oui | `null` | Nombre de documents reindexes |
| `reindex_total` | `int` | oui | `null` | Nombre total de documents a reindexer |

## 12. Non-objectifs v1

- Ingestion incrementale (diff de contenu, re-embedding partiel)
- Mode async (background processing avec queue)
- Ingestion par URL
- Detection de doublons par contenu (hash)
- Historique des versions de documents
- Contextual retrieval (prefixe de contexte par LLM)
- Enrichissement de metadonnees par LLM (resume, questions potentielles)
- OCR pour PDF scannes
- Support PPTX, CSV, Excel
- Parametres de chunking configurables par l'utilisateur (taille, overlap, seuil semantique)
- Versioning des embeddings
- Ingestion par URL

## 13. Criteres d'acceptation

### Documents

- [ ] Un document possede un etat (`uploaded`, `processing`, `indexed`, `error`) visible dans l'API et l'interface
- [ ] Un document en erreur affiche son message d'erreur
- [ ] L'utilisateur peut relancer l'indexation d'un document en erreur
- [ ] L'upload d'un fichier dont le nom existe deja dans le projet est rejete avec `DUPLICATE_FILENAME`
- [ ] L'utilisateur peut remplacer un document existant via `PUT`
- [ ] La limite est de 10 Mo par fichier et 100 documents par projet
- [ ] Le format `.doc` n'est plus accepte

### Metadonnees

- [ ] La langue du document est detectee automatiquement et affichee
- [ ] Les mots-cles (max 10) sont extraits automatiquement et affiches
- [ ] Les metadonnees fichier (auteur, date, titre) sont extraites quand disponibles
- [ ] L'echec de l'extraction de metadonnees ne bloque pas l'ingestion

### Chunking

- [ ] Le projet expose un champ `chunking_strategy` configurable (auto, fixed_window, paragraph, heading_section, semantic)
- [ ] Le chunking semantique fonctionne via analyse de similarite entre phrases
- [ ] Le parent-child chunking est activable par projet
- [ ] Quand active, les chunks parents et enfants sont visibles dans l'interface
- [ ] Le retrieval utilise les chunks enfants pour la recherche et les chunks parents pour le contexte LLM

### Reindexation batch

- [ ] L'owner peut declencher une reindexation batch sur un projet
- [ ] Le projet passe en lecture seule pendant la reindexation
- [ ] La progression est affichee (X/N documents)
- [ ] Les documents en erreur n'arretent pas le batch
- [ ] Un rapport est affiche a la fin (X reussis, Y en erreur)
