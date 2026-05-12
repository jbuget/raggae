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

## Scénarios de tests

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

---

## Structure du fichier de test

```
tests/components/organisms/project/settings/project-advanced-panel.test.tsx
├── Smoke                              — rendu de base, accès aux sections
├── User project / Models section      — scénarios 1–5
├── User project / Retrieval section   — scénarios 6–10
├── User project / Indexing section    — scénarios 11–13
├── Org project / Models section       — scénarios 14–18
└── Org project / Retrieval section    — scénarios 19–22
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
