# PLAN_IN_PROGRESS.md

> Ce fichier décrit la fonctionnalité en cours de développement.
> Il est mis à jour au début et pendant l'implémentation, puis vidé (remis au template) une fois la PR mergée.
> Il est lu automatiquement par Claude Code à chaque session de travail.

## Fonctionnalité en cours

Refactoring domaine — Phase 2 : table `agent_configurations` polymorphique

## Branche Git

```
refactor/agent-configurations
```

## Problème / Contexte

La configuration LLM/embedding/retrieval/reranking/history est actuellement dupliquée à trois endroits :
- `project_defaults` (USER + ORGA) : defaults par user et par org
- `projects` : ~19 colonnes config + 10 flags `overrides_*_from_org/user`
- Variables d'env : system defaults lus à chaud

L'objectif est une table unique `agent_configurations` avec un discriminant `type` couvrant
trois niveaux de la hiérarchie de configuration :

```
ENV (system defaults, variables d'environnement)
  ↑
USER  (defaults d'un utilisateur)     ORGA  (defaults d'une organisation)
  ↑                                     ↑
AGENT (config propre d'un projet — 1 ligne par projet)
```

`null` dans une ligne AGENT = hériter du niveau supérieur (ORGA si projet d'org, USER si projet personnel).
Cela remplace les 10 flags `overrides_*_from_org/user` par une logique de cascade implicite.

La résolution de config est gérée par un service domaine **`ConfigExtractor`** qui prend :
- `agent_config: AgentConfiguration` (la ligne AGENT du projet)
- `parent_defaults: AgentConfiguration` (la ligne ORGA ou USER selon le projet)

et retourne la configuration effective (les champs null de AGENT héritent du parent,
les champs null du parent héritent des env vars).

## Cardinalités

- `USER`  : 1 ligne par utilisateur (owner_id = user.id)
- `ORGA`  : 1 ligne par organisation (owner_id = organization.id)
- `AGENT` : 1 ligne par projet (owner_id = project.id), relation 1-1

Les defaults système restent dans les variables d'environnement (hors scope, pas de type APP).

## Colonnes config migrées depuis `projects`

Les ~19 colonnes suivantes sont déplacées de `projects` vers `agent_configurations` :

```
embedding_backend, embedding_model, embedding_api_key_credential_id
llm_backend, llm_model, llm_api_key_credential_id
chunking_strategy, processing_strategy, parent_child_chunking
retrieval_strategy, retrieval_top_k, retrieval_min_score
reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier
chat_history_window_size, chat_history_max_chars
```

## Décisions techniques

- `owner_id` reste non-nullable
- Contrainte unique `(owner_id, owner_type)` inchangée
- La migration inclut une data migration : créer une ligne AGENT par projet (copie des colonnes config)
- Les ~19 colonnes config + 10 flags `overrides_*` sont supprimés de `projects`
- Le frontend `ProjectAdvancedPanel` lit la config depuis un nouvel endpoint
  `GET /projects/{id}/configuration` au lieu de `ProjectResponse`
- Les defaults système restent dans les env vars (`GetSystemDefaults` endpoint inchangé)

## Découpage en tâches atomiques

### Étape 1 — Migration Alembic

- [ ] Renommer la table `project_defaults` → `agent_configurations`
      et étendre l'enum `owner_type` : USER + ORGA (existants) + AGENT (nouveau)
- [ ] Data migration : insérer une ligne AGENT par projet (copie des ~19 colonnes config)
- [ ] Supprimer les ~19 colonnes config de `projects`
- [ ] Supprimer les 10 colonnes `overrides_*_from_org/user` de `projects`
- [ ] Downgrade : restaurer les colonnes + supprimer les lignes AGENT

### Étape 2 — Domain

- [ ] Renommer `ProjectDefaultsOwnerType` → `AgentConfigurationType` (+ valeur AGENT)
- [ ] Renommer entité `ProjectDefaults` → `AgentConfiguration`
- [ ] Supprimer les ~19 champs config + 10 flags `overrides_*` de l'entité `Project`
- [ ] Nouveau service domaine `ConfigExtractor` :
      `resolve(agent: AgentConfiguration, parent: AgentConfiguration, system: SystemDefaults) → EffectiveConfig`
      - Pour chaque champ : `agent.field ?? parent.field ?? system.field`
- [ ] Tests unitaires `AgentConfiguration` (cascade null, types)
- [ ] Tests unitaires `ConfigExtractor` (tous les cas de cascade)
- [ ] Tests unitaires entité `Project` mise à jour

### Étape 3 — Application

- [ ] Renommer interface `ProjectDefaultsRepository` → `AgentConfigurationRepository`
      (méthode `find_by_owner(owner_id, type)` inchangée)
- [ ] Renommer DTO `ProjectDefaultsDTO` → `AgentConfigurationDTO`
- [ ] Renommer UC `GetOrganizationProjectDefaults` → `GetOrgAgentConfiguration`
- [ ] Renommer UC `UpsertOrganizationProjectDefaults` → `UpsertOrgAgentConfiguration`
- [ ] Renommer UC `GetUserProjectDefaults` → `GetUserAgentConfiguration`
- [ ] Renommer UC `UpsertUserProjectDefaults` → `UpsertUserAgentConfiguration`
- [ ] Mettre à jour `CreateProject` :
      - Créer une ligne AGENT vide à la création du projet
      - Supprimer la logique d'héritage inline (remplacée par la cascade null + `ConfigExtractor`)
- [ ] Mettre à jour `UpdateProject` :
      - Les changements config vont dans la ligne AGENT (plus dans `projects`)
      - Supprimer les flags `overrides_*` de `UpdateProjectRequest`
- [ ] Mettre à jour `UploadDocument` :
      - Résolution embedding : utiliser `ConfigExtractor` avec ligne AGENT + ligne ORGA/USER
- [ ] Mettre à jour `ProjectDTO` : supprimer ~19 champs config + 10 flags
- [ ] Tests unitaires pour tous les UC modifiés

### Étape 4 — Infrastructure

- [ ] Renommer `ProjectDefaultsModel` → `AgentConfigurationModel`
      (table `agent_configurations`, colonnes inchangées)
- [ ] Renommer `SQLAlchemyProjectDefaultsRepository` → `SQLAlchemyAgentConfigurationRepository`
- [ ] Renommer `InMemoryProjectDefaultsRepository` → `InMemoryAgentConfigurationRepository`
- [ ] Mettre à jour `ProjectModel` : supprimer les ~29 colonnes (19 config + 10 overrides)

### Étape 5 — Présentation backend

- [ ] Renommer schemas `OrganizationProjectDefaultsResponse` → `OrgAgentConfigurationResponse`
      et `UserProjectDefaultsResponse` → `UserAgentConfigurationResponse`
- [ ] Nouveau schema `AgentConfigurationResponse` + `UpdateAgentConfigurationRequest`
- [ ] Nouveaux endpoints projet : `GET/PUT /projects/{id}/configuration`
- [ ] Mettre à jour `ProjectResponse` : supprimer ~19 champs config + 10 flags
- [ ] Mettre à jour DI (`dependencies.py`)

### Étape 6 — Frontend

- [ ] Mettre à jour types `api.ts` :
      - `ProjectResponse` sans champs config
      - Nouveau `AgentConfigurationResponse`
      - Nouveau `UpdateAgentConfigurationRequest`
- [ ] Nouvelle API `getProjectConfiguration` / `updateProjectConfiguration`
- [ ] Nouveau hook `useProjectConfiguration(projectId)` + `useUpdateProjectConfiguration`
- [ ] `ProjectAdvancedPanel` : lire depuis `useProjectConfiguration` au lieu de `useProject`
      - Supprimer les override switches (`overrides_*_from_org/user`)
      - Remplacer par action "Réinitialiser aux defaults org/user" (remet les champs à null dans AGENT)
- [ ] `ProjectDefaultsForm` molecule : adapter pour le contexte AGENT
      - Prop `inheritedDefaults?: ProjectDefaultsConfig` (valeurs héritées depuis ORGA/USER)
      - Bouton "Réinitialiser" par section (remet null → hérite du parent)

## Vérification

```bash
# Backend
cd server && pytest tests/
cd server && ruff format src/ tests/ && ruff check src/ tests/ && mypy src/

# Frontend
cd client && npx tsc --noEmit
cd client && npx vitest run
```

## Vagues précédentes (terminées)

| Branche | Fonctionnalité | Statut |
|---------|---------------|--------|
| feat/org-project-defaults | Defaults org/user (USER + ORGA dans project_defaults) + UI accordions | ✅ pushé, PR à créer |
