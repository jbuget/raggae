# MCP au niveau organisation, activables par projet

> Plan d'implémentation, à dérouler PR après PR.
> Sauvegardé après la session de cadrage du 2026-06-29.
> Quand le refactoring `refactor/agent-configurations` (cf. `PLAN_IN_PROGRESS.md`) sera mergé, ce plan pourra être recopié dans `PLAN_IN_PROGRESS.md` à son tour.

## Vue d'ensemble

Une **organisation** peut déclarer des serveurs **MCP** (Model Context Protocol) distants.
Un **projet** de cette organisation peut **activer (opt-in)** les MCP de son choix pour exposer leurs **tools** au LLM lors des conversations.

## Décisions de cadrage (figées)

| Dimension | Choix |
|---|---|
| Transport | HTTP/SSE distant uniquement (Streamable HTTP) |
| Capabilities exposées | `tools` uniquement |
| Auth supportée | Aucune **ou** Bearer token chiffré |
| Activation projet | Opt-in explicite par projet |
| Granularité tools | Tout ou rien par MCP (pas d'allow-list V1) |
| Découverte tools | Snapshot à la déclaration + bouton "rafraîchir" manuel |
| Collisions de noms | Préfixe automatique `<mcp_slug>__<tool_name>` |
| Sécurité réseau | HTTPS obligatoire + denylist IPs privées (anti-SSRF) |
| Tool calling LLM | Function calling natif (OpenAI / Anthropic / Mistral / Gemini). Providers non compatibles : MCP ignorés avec warning UI. |
| Timeout / retry | Timeout configurable (5–60 s, défaut 30 s), pas de retry serveur, erreur remontée au LLM |
| Observabilité | Logs structurés + compteurs agrégés dans `/stats` |
| Limites V1 | Aucune (à monitorer) |
| Permissions org | OWNER + MAKER (déclarer / modifier / supprimer) |
| Permissions projet | Tout membre ayant accès au projet (activer / désactiver) |
| Lifecycle | Désactivation transparente (active project conservées). Suppression cascade sur les activations projet. |

## Modèle de domaine

### `OrgMcpServer` (rattaché à une org)

```python
@dataclass(frozen=True)
class OrgMcpServer:
    id: UUID
    organization_id: UUID
    name: str                          # humain
    slug: str                          # unique dans l'org, dérivé du name
    url: str                           # HTTPS obligatoire
    auth_type: McpAuthType             # NONE | BEARER
    encrypted_bearer_token: str | None # null si NONE
    token_fingerprint: str | None
    token_suffix: str | None
    is_active: bool                    # org-level on/off
    tools_snapshot: list[McpToolSnapshot]
    tools_snapshot_at: datetime
    timeout_seconds: int               # défaut 30, plage 5-60
    created_at: datetime
    updated_at: datetime
    created_by_user_id: UUID
```

### `ProjectMcpActivation` (jointure project ↔ mcp)

```python
@dataclass(frozen=True)
class ProjectMcpActivation:
    project_id: UUID
    org_mcp_server_id: UUID
    is_active: bool
    activated_at: datetime
    activated_by_user_id: UUID
```

### Value objects

```python
class McpAuthType(str, Enum):
    NONE = "none"
    BEARER = "bearer"

@dataclass(frozen=True)
class McpToolSnapshot:
    name: str
    description: str
    input_schema: dict  # JSON Schema
```

### Exceptions domaine

- `McpServerNotFoundError`
- `McpDuplicateSlugError`
- `McpAccessDeniedError`
- `McpUrlForbiddenError` (URL non HTTPS, IP privée, hôte interdit)
- `McpHandshakeError` (échec `tools/list` à la déclaration)
- `McpToolNotFoundError`
- `McpCallTimeoutError`

## Règles métier détaillées

1. **HTTPS obligatoire**. Résolution DNS côté serveur, refus des IPs privées / loopback / link-local (10/8, 127/8, 169.254/16, 172.16/12, 192.168/16, fc00::/7, ::1, etc.). Validation à la déclaration **et** à chaque appel (le DNS peut changer entre-temps).
2. **Slug unique par org**. Généré depuis le `name` (kebab-case ASCII). En cas de conflit, suffixe numérique `-2`, `-3`, etc.
3. **Permissions**
   - Déclarer / modifier / supprimer un MCP org : `OWNER` ou `MAKER` (analogue à `OrgModelProviderCredential`).
   - Activer / désactiver dans un projet : tout membre ayant accès au projet.
4. **Lifecycle**
   - `OrgMcpServer.is_active = false` : les activations projet sont **conservées** mais le MCP n'est plus appelé. Réactivation = retour à l'état précédent.
   - Suppression : **cascade** sur `ProjectMcpActivation`.
5. **Refresh des tools** : appel `tools/list` sur le serveur MCP, mise à jour du snapshot. Bouton manuel uniquement en V1. Pas de job périodique.
6. **Tool calling**
   - Tools exposés au LLM uniquement si le provider supporte le function calling natif (OpenAI / Anthropic / Mistral / Gemini).
   - Pour les autres providers : MCP activés **ignorés silencieusement** avec un warning visible dans les settings projet.
   - Préfixe `<mcp_slug>__<tool_name>` côté LLM pour lever les collisions. Séparateur `__` car compatible avec la regex tool name d'OpenAI (`^[a-zA-Z0-9_-]{1,64}$`).
7. **Exécution d'un tool call**
   - Timeout par défaut 30 s (paramétrable par MCP, 5–60 s).
   - Pas de retry serveur — toute erreur (timeout, 5xx, MCP down) est remontée comme `tool_result` d'erreur au LLM, qui décide.
   - Logs structurés (`project_id`, `mcp_id`, `tool_name`, `status`, `latency_ms`). Agrégation pour `/stats`.

## Découpage en 6 PRs (baby steps)

Chaque PR doit être **petite** (~300–700 lignes max), compiler, passer tous les tests, et être autonome.
La PR `n+1` peut s'appuyer sur la PR `n` mergée, mais ne doit pas être bloquée par elle pour partir en review.

---

### PR 1 — Domaine + use cases org (in-memory)

**Branche** : `feat/mcp-domain-and-org-use-cases`

Objectif : poser les briques pures (zéro dépendance externe), avec repository in-memory + tests unitaires.
Aucun endpoint, aucune migration, aucune UI.

#### Domain

- [ ] `domain/value_objects/mcp_auth_type.py` — enum `McpAuthType`
- [ ] `domain/value_objects/mcp_tool_snapshot.py` — value object `McpToolSnapshot`
- [ ] `domain/entities/org_mcp_server.py` — entité immutable + invariants (URL HTTPS, masquage token, helpers `mask_token`)
- [ ] `domain/entities/project_mcp_activation.py` — entité immutable
- [ ] `domain/exceptions/mcp_exceptions.py` — toutes les exceptions listées
- [ ] Tests unitaires entités + value objects

#### Application

- [ ] `application/dto/org_mcp_server_dto.py` — DTO sortie (sans token clair)
- [ ] `application/dto/project_mcp_activation_dto.py`
- [ ] `application/interfaces/repositories/org_mcp_server_repository.py`
- [ ] `application/interfaces/repositories/project_mcp_activation_repository.py`
- [ ] `application/interfaces/services/mcp_client.py` (ports `list_tools`, `call_tool`)
- [ ] `application/interfaces/services/url_safety_validator.py`
- [ ] Use cases org sous `application/use_cases/org_mcp/` :
  - [ ] `declare_org_mcp_server.py` — handshake `list_tools` à la déclaration
  - [ ] `update_org_mcp_server.py`
  - [ ] `refresh_org_mcp_tools.py`
  - [ ] `activate_org_mcp_server.py`
  - [ ] `deactivate_org_mcp_server.py`
  - [ ] `delete_org_mcp_server.py` (cascade sur activations)
  - [ ] `list_org_mcp_servers.py`
- [ ] Tests unitaires de chaque use case avec :
  - `InMemoryOrgMcpServerRepository`
  - `InMemoryProjectMcpActivationRepository`
  - `FakeMcpClient` (renvoie un snapshot scripté)
  - `FakeUrlSafetyValidator` (toujours OK ou raise selon le test)

#### Critères d'acceptation PR 1

- `pytest tests/unit/` vert
- `ruff format` / `ruff check` / `mypy` propres
- Aucune modification dans `infrastructure/`, `presentation/`, `client/`

---

### PR 2 — Infrastructure : persistence, client MCP, anti-SSRF

**Branche** : `feat/mcp-infrastructure`
**Dépend de** : PR 1 mergée.

#### Migration Alembic

- [ ] Table `org_mcp_servers`
  - `id` UUID PK
  - `organization_id` UUID FK `organizations.id` ON DELETE CASCADE
  - `name` text NOT NULL
  - `slug` text NOT NULL
  - `url` text NOT NULL
  - `auth_type` text NOT NULL (`none` / `bearer`)
  - `encrypted_bearer_token` text NULL
  - `token_fingerprint` text NULL
  - `token_suffix` text NULL
  - `is_active` boolean NOT NULL DEFAULT true
  - `tools_snapshot` jsonb NOT NULL DEFAULT `'[]'`
  - `tools_snapshot_at` timestamptz NOT NULL
  - `timeout_seconds` integer NOT NULL DEFAULT 30
  - `created_by_user_id` UUID NOT NULL
  - `created_at`, `updated_at` timestamptz
  - UNIQUE `(organization_id, slug)`
- [ ] Table `project_mcp_activations`
  - `project_id` UUID FK `projects.id` ON DELETE CASCADE
  - `org_mcp_server_id` UUID FK `org_mcp_servers.id` ON DELETE CASCADE
  - `is_active` boolean NOT NULL DEFAULT true
  - `activated_at` timestamptz NOT NULL
  - `activated_by_user_id` UUID NOT NULL
  - PK `(project_id, org_mcp_server_id)`

#### Infrastructure

- [ ] `infrastructure/database/models/org_mcp_server_model.py`
- [ ] `infrastructure/database/models/project_mcp_activation_model.py`
- [ ] `infrastructure/database/repositories/sqlalchemy_org_mcp_server_repository.py`
- [ ] `infrastructure/database/repositories/sqlalchemy_project_mcp_activation_repository.py`
- [ ] `infrastructure/services/url_safety_validator_impl.py`
  - Résolution DNS (toutes les adresses)
  - Refus IPv4 privées, loopback, link-local, multicast, broadcast, "this network"
  - Refus IPv6 unique-local (fc00::/7), loopback (::1), link-local (fe80::/10)
  - Exige scheme `https://`
- [ ] `infrastructure/services/http_mcp_client.py`
  - Basé sur `httpx.AsyncClient`
  - Implémente `list_tools(url, auth)` et `call_tool(url, auth, tool, args, timeout)`
  - Re-valide l'URL via `UrlSafetyValidator` à chaque appel
  - Mapping erreurs HTTP → exceptions domaine
- [ ] Réutilisation du `ProviderApiKeyCryptoService` existant pour chiffrer/déchiffrer le bearer token

#### Tests

- [ ] Tests intégration `SQLAlchemyOrgMcpServerRepository`
- [ ] Tests intégration `SQLAlchemyProjectMcpActivationRepository`
- [ ] Tests unitaires `UrlSafetyValidatorImpl` (chaque famille d'IPs interdites, IPv4 + IPv6)
- [ ] Tests unitaires `HttpMcpClient` avec serveur MCP factice (`pytest-httpx` ou équivalent)

#### Critères d'acceptation PR 2

- Migrations passent en up + downgrade
- Tests d'intégration verts
- Aucune modification dans `presentation/` ni `client/`

---

### PR 3 — Endpoints org + UI org

**Branche** : `feat/mcp-org-endpoints-and-ui`
**Dépend de** : PR 2 mergée.

#### Présentation backend

- [ ] Schemas Pydantic `presentation/api/v1/schemas/org_mcp_server.py`
  - `OrgMcpServerCreateRequest`, `OrgMcpServerUpdateRequest`, `OrgMcpServerResponse`, `McpToolSnapshotResponse`
- [ ] Route `presentation/api/v1/routes/org_mcp_servers.py`
  - `POST /api/v1/organizations/{org_id}/mcp-servers` → declare
  - `GET /api/v1/organizations/{org_id}/mcp-servers` → list
  - `GET /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}` → detail
  - `PATCH /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}` → update
  - `POST /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}/refresh` → refresh tools
  - `POST /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}/activate` → org-level activate
  - `POST /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}/deactivate`
  - `DELETE /api/v1/organizations/{org_id}/mcp-servers/{mcp_id}` → cascade
- [ ] Injection DI dans `dependencies.py`
- [ ] Tests E2E avec `TestClient` + DB de test

#### Frontend

- [ ] Régénérer le client Orval depuis le schéma OpenAPI mis à jour
- [ ] `client/src/components/atoms/mcp/` — chips, badges (status, masque token)
- [ ] `client/src/components/molecules/mcp/mcp-server-form.tsx` — formulaire déclaration / édition (URL, auth, timeout)
- [ ] `client/src/components/molecules/mcp/mcp-tools-list.tsx` — affichage du snapshot
- [ ] `client/src/components/organisms/organization/org-mcp-list.tsx` — CRUD complet, bouton refresh, toggle is_active
- [ ] Intégration dans `templates/organization/...-template.tsx` (paramètres org existants)
- [ ] Tests Vitest sur les molecules et l'organism (comportement, pas style)

#### Critères d'acceptation PR 3

- Parcours complet possible en local : déclarer un MCP, rafraîchir ses tools, le désactiver, le supprimer
- Tests backend + frontend verts
- Aucune modification du flux chat

---

### PR 4 — Activations projet

**Branche** : `feat/mcp-project-activations`
**Dépend de** : PR 3 mergée.

#### Application

- [ ] Use cases sous `application/use_cases/project_mcp/`
  - [ ] `activate_project_mcp.py` — vérifie que le MCP est `is_active` au niveau org et appartient à la même org que le projet
  - [ ] `deactivate_project_mcp.py`
  - [ ] `list_project_mcp_activations.py` — retourne les activations + snapshot des tools pour chaque MCP
- [ ] DTO + tests unitaires

#### Présentation backend

- [ ] Schemas `presentation/api/v1/schemas/project_mcp_activation.py`
- [ ] Route `presentation/api/v1/routes/project_mcp_activations.py`
  - `GET /api/v1/projects/{project_id}/mcp-activations` → liste activations + tools
  - `POST /api/v1/projects/{project_id}/mcp-activations/{mcp_id}` → activate
  - `DELETE /api/v1/projects/{project_id}/mcp-activations/{mcp_id}` → deactivate
- [ ] Tests E2E

#### Frontend

- [ ] Régénérer Orval
- [ ] `client/src/components/organisms/project/project-mcp-activations.tsx`
  - Liste des MCP org disponibles (uniquement ceux `is_active=true`)
  - Toggle activate/deactivate par MCP
  - Snapshot des tools visible (read-only en V1)
  - Warning visible si le provider LLM courant ne supporte pas le function calling
- [ ] Insertion dans `templates/project/project-settings-template.tsx`

#### Critères d'acceptation PR 4

- Un maker peut activer/désactiver un MCP dans son projet
- Le warning provider non-compatible s'affiche correctement
- Tests verts

---

### PR 5 — Intégration dans le flux chat (tool calling)

**Branche** : `feat/mcp-chat-tool-calling`
**Dépend de** : PR 4 mergée.

> **Note de re-scoping (2026-06-29)** — Le wiring complet dans `send_message.py`
> (modification de l'interface `LLMService`, boucle de tool-calling avec
> streaming, adapters par provider) représente un chantier trop large pour
> tenir dans une PR sereinement mergeable. La PR 5 livre les **fondations
> isolées et testables** : le `McpToolResolver` et le `McpToolExecutor`,
> branchés en DI. Le wiring final dans `send_message.py` est reporté à une
> PR dédiée ("PR 5b") qui pourra réutiliser ces services tels quels.

Cœur de la valeur utilisateur : les tools MCP deviennent effectivement appelables par le LLM.

#### Domain / Application

- [ ] Service domaine ou application `McpToolResolver` :
  - Charge les activations projet
  - Filtre celles dont `OrgMcpServer.is_active = true`
  - Aplati les tools en `[{prefixed_name, mcp_id, original_name, description, input_schema}, ...]`
- [ ] Adapter le use case `SendChatMessage` (ou équivalent) :
  - Appelle `McpToolResolver` au début
  - Si le provider LLM supporte les tools : ajoute `tools=[...]` au payload
  - Si non : ignore les MCP (déjà signalé en UI)
  - Boucle de tool-use : recevoir tool_call, router vers le bon MCP via `mcp_id`, appeler `McpClient.call_tool(...)`, renvoyer `tool_result` au LLM, recommencer jusqu'à réponse finale
  - Logs structurés (`project_id`, `mcp_id`, `tool_name`, `status`, `latency_ms`)

#### Infrastructure

- [ ] Adapter chaque adapter LLM existant pour accepter une liste de tools standardisée et la traduire au format du provider
- [ ] Identifier proprement les providers compatibles function calling (capability flag)

#### Tests

- [ ] Tests unitaires `McpToolResolver` (préfixage, filtrage org `is_active`, projet `is_active`)
- [ ] Tests intégration de bout en bout du flux chat avec un `FakeMcpClient` qui renvoie un résultat scripté
- [ ] Tests sur la gestion des erreurs : timeout, MCP down, tool inconnu

#### Critères d'acceptation PR 5

- Conversation en local avec un MCP réel (ex: serveur de test) qui répond à un tool call
- Logs structurés présents dans les bons formats
- Comportement gracieux en cas d'erreur

---

### PR 6 — Stats / observabilité

**Branche** : `feat/mcp-stats`
**Dépend de** : PR 5 mergée.

- [ ] Compteurs agrégés (en mémoire ou table légère) :
  - Nombre d'appels par `mcp_id` (succès / erreurs)
  - Latence p50/p95
  - Comptage par jour pour les graphes 90j
- [ ] Endpoint `/api/v1/stats/mcp` ou extension de `/stats` existant
- [ ] Frontend : section MCP dans la page `/stats`
- [ ] Tests

---

## Pre-Push Checklist (à chaque PR)

```bash
# Backend
cd server && pytest
cd server && ruff format src/ tests/
cd server && ruff check src/ tests/
cd server && mypy src/

# Frontend
cd client && npx tsc --noEmit
cd client && npx vitest run
```

## Points de vigilance globaux

- **Sécurité SSRF** : la validation anti-SSRF doit être couverte par des tests unitaires exhaustifs (chaque famille d'IPs privées IPv4 et IPv6). La validation doit être faite **à chaque appel**, pas seulement à la déclaration (le DNS peut changer).
- **Chiffrement du token Bearer** : réutiliser strictement le `ProviderApiKeyCryptoService` existant (même algo, même clé, même rotation). Ne jamais logger le token clair.
- **Pas de limites V1** : surveiller la taille du payload `tools` envoyé au LLM. Un compteur dans `/stats` permettra de réintroduire une limite si on observe des dérives.
- **Préfixage tools** : séparateur `__` (deux underscores), compatible regex OpenAI. Ne pas utiliser `.` ni `:`.
- **Pas d'attribution Claude** dans les commits / PRs.
- **PR title & description en français**, format `Problème / Solution / Implémentation / Recette`.

## Quand ce plan reprend la main

Quand le refactoring `refactor/agent-configurations` est mergé et que `PLAN_IN_PROGRESS.md` est libéré, copier la PR 1 ci-dessus dans `PLAN_IN_PROGRESS.md` et démarrer.
