# Tests d'héritage des paramètres projet

Ce document décrit les scénarios de tests UI couvrant l'héritage des paramètres dans
`ProjectAdvancedPanel` (`tests/components/organisms/project/settings/project-advanced-panel.test.tsx`).

---

## Contexte : chaîne d'héritage

Les paramètres d'un projet sont résolus dans cet ordre de priorité :

```
Projet  →  Organisation ou Utilisateur  →  Système (env)
```

Un paramètre défini au niveau projet **remplace** (surcharge) le paramètre du niveau parent.
Un paramètre `null` au niveau projet signifie "hériter du parent".

---

## Messages affichés par section

Pour chaque section de l'accordéon (Modèles, Indexation, Retrieval, Augmentation, Historique),
le panneau affiche un message contextuel selon l'état d'héritage :

| Condition | Message (FR) |
|-----------|-------------|
| Aucun parent configuré, aucun projet (projet utilisateur uniquement) | "Aucun paramètre configuré — les valeurs système sont utilisées." |
| Parent configuré, projet sans modification | "Aucun paramètre modifié, les paramètres de l'organisation s'appliquent." |
| Parent configuré, projet sans modification (utilisateur) | "Aucun paramètre modifié, les paramètres utilisateur s'appliquent." |
| Parent configuré, projet surcharge partiellement | "Certains paramètres de l'organisation sont modifiés." |
| Parent configuré, projet surcharge partiellement (utilisateur) | "Certains paramètres utilisateur sont modifiés." |
| Parent configuré, projet surcharge tout | "Tous les paramètres de l'organisation sont surchargés." |
| Parent configuré, projet surcharge tout (utilisateur) | "Tous les paramètres utilisateur sont surchargés." |

> **Règle clé** : une valeur projet identique à la valeur parente n'est **pas** considérée
> comme une surcharge. Par exemple, si l'utilisateur a `retrieval_top_k = 10` et le projet
> a aussi `retrieval_top_k = 10`, le message "Aucun paramètre modifié" est affiché.

---

## Scénarios de tests — Messages d'héritage

### Projets utilisateur — Section Modèles

| # | Données utilisateur | Données projet | Message attendu |
|---|---------------------|----------------|-----------------|
| 1 | Aucun | Aucun | "No settings configured — system defaults are used." |
| 2 | `embedding_backend: openai` | Aucun | "No parameters modified, user settings apply." |
| 3 | `embedding_backend: openai` | `embedding_backend: openai` (même valeur) | "No parameters modified, user settings apply." |
| 4 | `embedding_backend: gemini`, `llm_backend: gemini` | `embedding_backend: openai` | "Some user settings are modified." |
| 5 | `embedding_backend: gemini`, `llm_backend: gemini` | `embedding_backend: openai`, `llm_backend: openai` | "All user settings are overridden." |

### Projets utilisateur — Section Retrieval

| # | Données utilisateur | Données projet | Message attendu |
|---|---------------------|----------------|-----------------|
| 6 | Aucun | Aucun | "No settings configured — system defaults are used." |
| 7 | `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | Aucun | "No parameters modified, user settings apply." |
| 8 | `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | `retrieval_top_k: 10`, `retrieval_min_score: 0.5` (même valeurs) | "No parameters modified, user settings apply." |
| 9 | `retrieval_strategy: hybrid`, `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | `retrieval_top_k: 20` | "Some user settings are modified." |
| 10 | `retrieval_strategy: hybrid`, `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | `retrieval_strategy: vector`, `retrieval_top_k: 20`, `retrieval_min_score: 0.8` | "All user settings are overridden." |

### Projets utilisateur — Section Indexation

| # | Données utilisateur | Données projet | Message attendu |
|---|---------------------|----------------|-----------------|
| 11 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | Aucun | "No parameters modified, user settings apply." |
| 12 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | `chunking_strategy: fixed_window` | "Some user settings are modified." |
| 13 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | `chunking_strategy: fixed_window`, `parent_child_chunking: false` | "All user settings are overridden." |

### Projets organisation — Section Modèles

| # | Données org | Données projet | Message attendu |
|---|-------------|----------------|-----------------|
| 14 | Aucun | Aucun | *(aucun message — pas de message "système" pour les projets org)* |
| 15 | `embedding_backend: openai` | Aucun | "No parameters modified, organization settings apply." |
| 16 | `embedding_backend: openai` | `embedding_backend: openai` (même valeur) | "No parameters modified, organization settings apply." |
| 17 | `embedding_backend: gemini`, `llm_backend: gemini` | `embedding_backend: openai` | "Some organization settings are modified." |
| 18 | `embedding_backend: gemini`, `llm_backend: gemini` | `embedding_backend: openai`, `llm_backend: openai` | "All organization settings are overridden." |

### Projets organisation — Section Retrieval

| # | Données org | Données projet | Message attendu |
|---|-------------|----------------|-----------------|
| 19 | `retrieval_top_k: 15`, `retrieval_min_score: 0.4` | Aucun | "No parameters modified, organization settings apply." |
| 20 | `retrieval_top_k: 15` | `retrieval_top_k: 15` (même valeur) | "No parameters modified, organization settings apply." |
| 21 | `retrieval_strategy: hybrid`, `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | `retrieval_top_k: 20` | "Some organization settings are modified." |
| 22 | `retrieval_strategy: hybrid`, `retrieval_top_k: 10`, `retrieval_min_score: 0.5` | `retrieval_strategy: fulltext`, `retrieval_top_k: 20`, `retrieval_min_score: 0.9` | "All organization settings are overridden." |

### Projets utilisateur — Section Reclassement (Context augmentation)

| # | Données utilisateur | Données projet | Message attendu |
|---|---------------------|----------------|-----------------|
| 23 | Aucun | Aucun | "No settings configured — system defaults are used." |
| 24 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | Aucun | "No parameters modified, user settings apply." |
| 25 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | `reranking_enabled: false` | "Some user settings are modified." |
| 26 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | `reranking_enabled: false`, `reranker_backend: inmemory` | "All user settings are overridden." |

### Projets utilisateur — Section Historique (Answer generation)

| # | Données utilisateur | Données projet | Message attendu |
|---|---------------------|----------------|-----------------|
| 27 | Aucun | Aucun | "No settings configured — system defaults are used." |
| 28 | `chat_history_window_size: 16`, `chat_history_max_chars: 8000` | Aucun | "No parameters modified, user settings apply." |
| 29 | `chat_history_window_size: 16`, `chat_history_max_chars: 8000` | `chat_history_window_size: 4` | "Some user settings are modified." |
| 30 | `chat_history_window_size: 16`, `chat_history_max_chars: 8000` | `chat_history_window_size: 4`, `chat_history_max_chars: 2000` | "All user settings are overridden." |

### Projets organisation — Section Indexation

| # | Données org | Données projet | Message attendu |
|---|-------------|----------------|-----------------|
| 31 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | Aucun | "No parameters modified, organization settings apply." |
| 32 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | `chunking_strategy: fixed_window` | "Some organization settings are modified." |
| 33 | `chunking_strategy: paragraph`, `parent_child_chunking: true` | `chunking_strategy: fixed_window`, `parent_child_chunking: false` | "All organization settings are overridden." |

### Projets organisation — Section Reclassement (Context augmentation)

| # | Données org | Données projet | Message attendu |
|---|-------------|----------------|-----------------|
| 34 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | Aucun | "No parameters modified, organization settings apply." |
| 35 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | `reranking_enabled: false` | "Some organization settings are modified." |
| 36 | `reranking_enabled: true`, `reranker_backend: cross_encoder` | `reranking_enabled: false`, `reranker_backend: inmemory` | "All organization settings are overridden." |

### Projets organisation — Section Historique (Answer generation)

| # | Données org | Données projet | Message attendu |
|---|-------------|----------------|-----------------|
| 37 | `chat_history_window_size: 20`, `chat_history_max_chars: 6000` | Aucun | "No parameters modified, organization settings apply." |
| 38 | `chat_history_window_size: 20`, `chat_history_max_chars: 6000` | `chat_history_window_size: 4` | "Some organization settings are modified." |
| 39 | `chat_history_window_size: 20`, `chat_history_max_chars: 6000` | `chat_history_window_size: 4`, `chat_history_max_chars: 2000` | "All organization settings are overridden." |

---

## Scénarios de tests — Valeurs des champs

Ces tests vérifient que la valeur effective affichée dans chaque champ respecte la chaîne
d'héritage : la valeur projet prime, sinon la valeur parent (org ou utilisateur), sinon la
valeur système.

### Retrieval — Champ Top-K

| # | Projet | Valeur parent | Valeur projet | Valeur affichée |
|---|--------|---------------|---------------|-----------------|
| V1 | Utilisateur | *(système : 8)* | Aucun | 8 |
| V2 | Utilisateur | Utilisateur : 12 | Aucun | 12 |
| V3 | Organisation | Org : 15 | Aucun | 15 |
| V4 | Utilisateur | Utilisateur : 12 | 20 | 20 |
| V5 | Organisation | Org : 15 | 5 | 5 |

### Retrieval — Champ Min Score

| # | Projet | Valeur parent | Valeur projet | Valeur affichée |
|---|--------|---------------|---------------|-----------------|
| V6 | Utilisateur | *(système : 0.3)* | Aucun | 0.3 |
| V7 | Utilisateur | Utilisateur : 0.7 | Aucun | 0.7 |
| V8 | Organisation | Org : 0.6 | Aucun | 0.6 |
| V9 | Utilisateur | Utilisateur : 0.7 | 0.9 | 0.9 |

### Indexation — Switch Parent-child chunking

| # | Projet | Valeur parent | Valeur projet | État du switch |
|---|--------|---------------|---------------|----------------|
| V10 | Utilisateur | *(système : false)* | Aucun | décoché |
| V11 | Utilisateur | Utilisateur : true | Aucun | coché |
| V12 | Utilisateur | Utilisateur : false | Aucun | décoché |
| V13 | Organisation | Org : true | Aucun | coché |
| V14 | Utilisateur | Utilisateur : false | true | coché |
| V15 | Organisation | Org : true | false | décoché |

### Historique — Champ Window Size

| # | Projet | Valeur parent | Valeur projet | Valeur affichée |
|---|--------|---------------|---------------|-----------------|
| V16 | Utilisateur | *(système : 8)* | Aucun | 8 |
| V17 | Utilisateur | Utilisateur : 16 | Aucun | 16 |
| V18 | Organisation | Org : 20 | Aucun | 20 |
| V19 | Utilisateur | Utilisateur : 16 | 4 | 4 |

### Modèles — Label du select Embedding Backend

Le select affiche un label contextuel : `"Default (Backend)"` si aucun parent ne configure
le backend, `"Set by user (Backend)"` ou `"Set by organization (Backend)"` selon l'origine.

| # | Projet | Config parent | Config projet | Label affiché |
|---|--------|---------------|---------------|---------------|
| V20 | Utilisateur | *(système : gemini)* | Aucun | "Default (Gemini)" |
| V21 | Utilisateur | Utilisateur : openai | Aucun | "Set by user (OpenAI)" |
| V22 | Organisation | Org : openai | Aucun | "Set by organization (OpenAI)" |
| V23 | Utilisateur | Utilisateur : null | Aucun | "Default (Gemini)" |

> **Note Radix UI** : le select rend le contenu de l'item sélectionné à plusieurs endroits
> du DOM (trigger + liste cachée). Tous les tests de labels de select utilisent `findAllByText`
> au lieu de `findByText` pour éviter l'erreur "Found multiple elements".

### Modèles — Label du select LLM Backend

| # | Projet | Config parent | Config projet | Label affiché |
|---|--------|---------------|---------------|---------------|
| V24 | Utilisateur | *(système : gemini)* | Aucun | "Default (Gemini)" |
| V25 | Utilisateur | Utilisateur : gemini | Aucun | "Set by user (Gemini)" |
| V26 | Organisation | Org : openai | Aucun | "Set by organization (OpenAI)" |

### Indexation — Label du select Chunking Strategy

| # | Projet | Config parent | Config projet | Label affiché |
|---|--------|---------------|---------------|---------------|
| V27 | Utilisateur | *(système : auto)* | Aucun | "Default (Auto)" |
| V28 | Utilisateur | Utilisateur : paragraph | Aucun | "Set by user (Paragraph)" |
| V29 | Organisation | Org : fixed_window | Aucun | "Set by organization (Fixed window)" |

### Retrieval — Label du select Stratégie

| # | Projet | Config parent | Config projet | Label affiché |
|---|--------|---------------|---------------|---------------|
| V30 | Utilisateur | *(système : hybrid)* | Aucun | "Default (Hybrid)" |
| V31 | Utilisateur | Utilisateur : vector | Aucun | "Set by user (Vector)" |
| V32 | Organisation | Org : fulltext | Aucun | "Set by organization (Fulltext)" |

### Historique — Champ Max Chars

| # | Projet | Valeur parent | Valeur projet | Valeur affichée |
|---|--------|---------------|---------------|-----------------|
| V33 | Utilisateur | *(système : 4000)* | Aucun | 4000 |
| V34 | Utilisateur | Utilisateur : 8000 | Aucun | 8000 |
| V35 | Organisation | Org : 6000 | Aucun | 6000 |
| V36 | Utilisateur | Utilisateur : 8000 | 2000 | 2000 |

---

## Structure du fichier de test

```
tests/components/organisms/project/settings/project-advanced-panel.test.tsx
├── Field values inheritance          — valeurs effectives affichées (V1–V27)
│   ├── Retrieval — Top-K input
│   ├── Retrieval — Min score input
│   ├── Knowledge indexing — Parent-child chunking switch
│   ├── Answer generation — Chat history window size
│   ├── Models — Embedding backend inherited label
│   ├── Models — LLM backend inherited label
│   ├── Knowledge indexing — Chunking strategy inherited label
│   ├── Retrieval — Strategy inherited label
│   └── Answer generation — Chat history max chars
├── Smoke                             — rendu de base, accès aux sections
├── User project / Models section     — messages 1–5
├── User project / Retrieval section  — messages 6–10
├── User project / Indexing section   — messages 11–13
├── User project / Context augmentation — messages reranking (user)
├── User project / Answer generation  — messages historique (user)
├── Org project / Models section      — messages 14–18
├── Org project / Retrieval section   — messages 19–22
├── Org project / Knowledge indexing  — messages indexation (org)
├── Org project / Context augmentation — messages reranking (org)
└── Org project / Answer generation   — messages historique (org)
```

### Mocks et helpers

- **MSW** : tous les appels API sont interceptés (`server.use(...)`)
  - `GET /api/v1/projects/:id` — données projet
  - `GET /api/v1/projects/:id/configuration` — config projet
  - `GET /api/v1/system/defaults` — valeurs système
  - `GET /api/v1/auth/me/project-defaults` — paramètres utilisateur (404 si absent)
  - `GET /api/v1/organizations/:id/project-defaults` — paramètres org (404 si absent)
  - `GET /api/v1/model-catalog` — catalogue modèles
  - `GET /api/v1/model-credentials` — credentials

- **`setup(options)`** : helper qui enregistre les handlers MSW et rend le composant
- **`openSection(regex)`** : helper qui clique sur un trigger d'accordéon pour l'ouvrir

---

## Lancer les tests

```bash
cd client && npx vitest run tests/components/organisms/project/settings/project-advanced-panel.test.tsx
```
