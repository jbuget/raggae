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
quatre niveaux de la hiérarchie de configuration :

```
APP   (system defaults — 1 ligne, seedée depuis les env vars)
  ↑
USER  (defaults d'un utilisateur)   ORGA  (defaults d'une organisation)
  ↑                                   ↑
PROJECT (config propre d'un projet — 1 ligne par projet)
```

Un projet appartient soit à une org soit à un user (jamais les deux).
La cascade suit le parent direct : `PROJECT ?? (ORGA | USER) ?? APP ?? None`.

`null` dans un champ = hériter du niveau supérieur. Si aucun niveau ne définit le champ, la valeur résolue est `None` (pas d'erreur, comportement actuel conservé).

La résolution est gérée par un service domaine **`ConfigExtractor`** :
```python
def resolve(
    project: AgentConfiguration,
    parent: AgentConfiguration | None,  # ORGA ou USER selon l'appartenance du projet
    app: AgentConfiguration | None,     # APP, None si env var non définie
) -> ResolvedAgentConfiguration:
    # pour chaque champ : project.field ?? parent.field ?? app.field
```

Retourne un value object **`ResolvedAgentConfiguration`** : uniquement les ~19 champs config (tous
`Optional`), sans `id`, `owner_id` ni `type`. Une configuration résolue n'est pas une entité persistée
— lui donner un identifiant serait un mensonge dans le domaine.

```python
@dataclass(frozen=True)
class ResolvedAgentConfiguration:
    embedding_backend: str | None = None
    ...  # ~19 champs config, tous Optional
```

## Modèle de domaine

**Une seule classe** `AgentConfiguration` avec un champ `type: AgentConfigurationType`.
Pas de sous-classes Python : le type joue uniquement le rôle de discriminant, aucun comportement spécifique par type.

`owner_id` identifie le propriétaire selon le type : UUID de l'utilisateur (`USER`), de l'organisation
(`ORGA`), du projet (`PROJECT`), ou sentinel `SYSTEM_OWNER_ID` (`APP`).

```python
class AgentConfigurationType(str, Enum):
    APP     = "APP"
    USER    = "USER"
    ORGA    = "ORGA"
    PROJECT = "PROJECT"

@dataclass(frozen=True)
class AgentConfiguration:
    id: UUID
    owner_id: UUID          # SYSTEM_OWNER_ID pour APP
    type: AgentConfigurationType
    # ~19 champs config, tous Optional
    embedding_backend: str | None = None
    ...
```

## Cardinalités

- `APP`    : 1 ligne unique (owner_id = UUID sentinel `00000000-0000-0000-0000-000000000001`)
- `USER`   : 1 ligne par utilisateur
- `ORGA`   : 1 ligne par organisation
- `PROJECT`: 1 ligne par projet (relation 1-1)

## Colonnes config migrées depuis `projects`

```
embedding_backend, embedding_model, embedding_api_key_credential_id
llm_backend, llm_model, llm_api_key_credential_id
chunking_strategy, processing_strategy, parent_child_chunking
retrieval_strategy, retrieval_top_k, retrieval_min_score
reranking_enabled, reranker_backend, reranker_model, reranker_candidate_multiplier
chat_history_window_size, chat_history_max_chars
```

Pas de contraintes FK sur les credential IDs pour l'instant (table `credentials` unifiée = phase future).

## Décisions techniques

- `owner_id` reste non-nullable ; pour APP on utilise `SYSTEM_OWNER_ID`
- Contrainte unique `(owner_id, owner_type)` inchangée
- `find_app_defaults()` : lit la ligne APP ; si absente, lit les env vars (fallback pour tests/CI)
- La migration inclut une data migration :
  - Créer la ligne APP seedée depuis les env vars
  - Créer une ligne PROJECT par projet (copie des ~19 colonnes config depuis `projects`)
- Les ~19 colonnes config + 10 flags `overrides_*` sont supprimés de `projects`
- Pas d'endpoint admin pour modifier APP (hors scope)

## Découpage en tâches atomiques

### Étape 1 — Migration Alembic

- [ ] Renommer la table `project_defaults` → `agent_configurations`
      et étendre l'enum `owner_type` : USER + ORGA (existants) + PROJECT + APP (nouveaux)
- [ ] Data migration : insérer la ligne APP depuis les env vars
- [ ] Data migration : insérer une ligne PROJECT par projet (copie des ~19 colonnes config)
- [ ] Supprimer les ~19 colonnes config de `projects`
- [ ] Supprimer les 10 colonnes `overrides_*_from_org/user` de `projects`
- [ ] Downgrade : restaurer les colonnes + supprimer les lignes PROJECT et APP

### Étape 2 — Domain

- [ ] Renommer `ProjectDefaultsOwnerType` → `AgentConfigurationType` (+ valeurs PROJECT, APP)
- [ ] Renommer entité `ProjectDefaults` → `AgentConfiguration`
- [ ] Ajouter constante `SYSTEM_OWNER_ID`
- [ ] Supprimer les ~19 champs config + 10 flags `overrides_*` de l'entité `Project`
- [ ] Nouveau value object `ResolvedAgentConfiguration` (~19 champs config, tous Optional, pas d'id)
- [ ] Nouveau service domaine `ConfigExtractor.resolve(project, parent, app)` → `ResolvedAgentConfiguration`
- [ ] Tests unitaires `ConfigExtractor` (tous les cas : cascade complète, parent None, app None)
- [ ] Tests unitaires entité `Project` mise à jour

### Étape 3 — Application

- [ ] Renommer interface `ProjectDefaultsRepository` → `AgentConfigurationRepository`
      + méthode `find_by_owner(owner_id: UUID, type: AgentConfigurationType) → AgentConfiguration | None`
      + méthode `find_app_defaults() → AgentConfiguration | None` (fallback env vars si ligne absente)
- [ ] Renommer DTO `ProjectDefaultsDTO` → `AgentConfigurationDTO`
- [ ] Renommer UC `GetOrganizationProjectDefaults` → `GetOrgAgentConfiguration`
- [ ] Renommer UC `UpsertOrganizationProjectDefaults` → `UpsertOrgAgentConfiguration`
- [ ] Renommer UC `GetUserProjectDefaults` → `GetUserAgentConfiguration`
- [ ] Renommer UC `UpsertUserProjectDefaults` → `UpsertUserAgentConfiguration`
- [ ] Nouveau UC `GetProjectConfiguration(project_id)` → `AgentConfigurationDTO`
- [ ] Nouveau UC `UpdateProjectConfiguration(project_id, data)` → `AgentConfigurationDTO`
- [ ] Mettre à jour `CreateProject` : créer une ligne PROJECT vide (tout null = hérite tout)
- [ ] Mettre à jour `UpdateProject` : supprimer les champs config + flags `overrides_*` (config gérée exclusivement via `UpdateProjectConfiguration`)
- [ ] Mettre à jour `DeleteProject` : supprimer la ligne PROJECT dans `agent_configurations` avant de supprimer le projet (owner_id polymorphique → pas de FK CASCADE possible, gestion manuelle)
- [ ] Mettre à jour `UploadDocument` :
      - Charger la config PROJECT via le repository
      - Déterminer l'appartenance du projet (user ou org) et charger le parent
      - Charger APP via `find_app_defaults()`
      - Appeler `ConfigExtractor.resolve(project, parent, app)` → `ResolvedAgentConfiguration`
      - Supprimer `_resolve_effective_project_for_embedding`
- [ ] Mettre à jour `ProjectDTO` : supprimer ~19 champs config + 10 flags
- [ ] Tests unitaires pour tous les UC modifiés

### Étape 4 — Infrastructure

- [ ] Renommer `ProjectDefaultsModel` → `AgentConfigurationModel`
- [ ] Renommer `SQLAlchemyProjectDefaultsRepository` → `SQLAlchemyAgentConfigurationRepository`
      + implémenter `find_app_defaults()` (lit APP ; fallback env vars si absente)
- [ ] Renommer `InMemoryProjectDefaultsRepository` → `InMemoryAgentConfigurationRepository`
- [ ] Mettre à jour `ProjectModel` : supprimer les ~29 colonnes (19 config + 10 overrides)
- [ ] Tests d'intégration `SQLAlchemyAgentConfigurationRepository` :
      cascade complète, `find_app_defaults()` avec ligne APP présente, fallback env vars si absente

### Étape 5 — Présentation backend

- [ ] Renommer schemas `OrganizationProjectDefaultsResponse` → `OrgAgentConfigurationResponse`
      et `UserProjectDefaultsResponse` → `UserAgentConfigurationResponse`
- [ ] Nouveau schema `AgentConfigurationResponse` + `UpdateAgentConfigurationRequest`
- [ ] Nouveaux endpoints projet : `GET /projects/{id}/configuration` → `GetProjectConfiguration`
      et `PUT /projects/{id}/configuration` → `UpdateProjectConfiguration`
- [ ] Mettre à jour `GET /system-defaults` → lit la ligne APP depuis DB
- [ ] Mettre à jour `ProjectResponse` : supprimer ~19 champs config + 10 flags
- [ ] Mettre à jour DI (`dependencies.py`)

### Étape 6 — Frontend

- [ ] Mettre à jour types `api.ts` :
      - `ProjectResponse` sans champs config
      - Nouveau `AgentConfigurationResponse`
      - Nouveau `UpdateAgentConfigurationRequest`
- [ ] Nouvelle API `getProjectConfiguration` / `updateProjectConfiguration`
- [ ] Nouveau hook `useProjectConfiguration(projectId)` + `useUpdateProjectConfiguration(projectId)`
- [ ] `ProjectAdvancedPanel` : lire depuis `useProjectConfiguration` au lieu de `useProject`
      - Supprimer les override switches (`overrides_*_from_org/user`)
      - Bouton "Réinitialiser" par section (remet les champs à null → hérite du parent)
- [ ] `ProjectDefaultsForm` molecule : adapter pour le contexte PROJECT
      - Prop `inheritedDefaults?: ProjectDefaultsConfig` (valeurs héritées depuis ORGA/USER/APP)
      - Bouton "Réinitialiser" par section

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
