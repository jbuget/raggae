# Spécifications SSO Microsoft Entra

**Statut** : Approuvé
**Date** : 2026-03-19
**Scope** : Authentification SSO via Microsoft Entra ID (Azure AD), v1

---

## Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Spécifications fonctionnelles](#2-spécifications-fonctionnelles)
3. [Spécifications techniques](#3-spécifications-techniques)
4. [Variables d'environnement](#4-variables-denvironnement)
5. [Modifications par couche](#5-modifications-par-couche)
6. [Stratégie de tests](#6-stratégie-de-tests)
7. [Ordre d'implémentation](#7-ordre-dimplémentation)
8. [Hors scope v1](#8-hors-scope-v1)
9. [Évolutions futures](#9-évolutions-futures)

---

## 1. Contexte et objectifs

### Système d'authentification actuel

- Email/password uniquement, JWT HS256 (30 min)
- Entité `User` : `id, email, hashed_password, full_name, is_active, created_at, locale`
- Aucun mécanisme OAuth/SSO existant
- Clean Architecture stricte : Domain → Application → Infrastructure → Presentation

### Objectifs v1

- Permettre la connexion via **Microsoft Entra ID** (Azure AD, OAuth 2.0 Authorization Code Flow + PKCE)
- Activer/désactiver via variable d'environnement (`ENTRA_ENABLED`)
- Restreindre l'accès à un ou plusieurs domaines email configurables (`ENTRA_ALLOWED_DOMAINS`)
- Lier automatiquement un compte email/password existant lors du premier login SSO
- Architecture extensible pour Google Connect et GitHub Connect

---

## 2. Spécifications fonctionnelles

### 2.1 Activation du SSO

| État | Comportement |
|---|---|
| `ENTRA_ENABLED=false` (défaut) | Endpoints SSO retournent `HTTP 501 Not Implemented` |
| `ENTRA_ENABLED=true` | Flow SSO disponible |

### 2.2 Flux de connexion SSO

```
Utilisateur → "Se connecter avec Microsoft"
  → GET /api/v1/auth/entra/login?redirect=/projects/42
      - Génère state : { csrf_token, redirect_url, expires_at }
      - Signe et pose cookie httponly "oauth_state" (TTL 5 min)
      - Redirect vers Microsoft (Authorization Code Flow + PKCE)

  → Authentification Microsoft

  → GET /api/v1/auth/entra/callback?code=...&state=...
      - Vérifie state (cookie signé vs. paramètre)
      - Supprime le cookie oauth_state
      - Échange le code contre un token Microsoft (via msal)
      - Valide la signature et les claims (iss, aud, exp, nbf) — délégué à msal
      - Extrait : oid, email (mail → preferred_username → upn), full_name
      - Valide le domaine email si ENTRA_ALLOWED_DOMAINS configuré
          ├── Domaine non autorisé → log "domain_rejected" + HTTP 403
          └── Domaine autorisé →
                ├── find_by_entra_id(oid) → compte trouvé → connexion directe
                │     + log "sso_login"
                ├── find_by_email(email) → compte existant → liaison automatique
                │     - link_entra(oid) sur le compte existant
                │     - mise à jour silencieuse si email divergent + log "email_updated"
                │     + log "account_linked"
                └── aucun compte → création automatique + log "account_created"
      - Génère un one-time code (UUID, TTL 30s, stocké in-memory)
      - Redirect vers frontend : {FRONTEND_URL}/auth/callback?code={one_time_code}
            + redirect_url encodée dans le state pour deep linking

  → POST /api/v1/auth/entra/token  { "code": "{one_time_code}" }
      - Échange le code contre un JWT Raggae
      - Invalide le code immédiatement (usage unique)
      - Retourne { access_token, token_type: "bearer", is_new_user, account_linked }

  → Requêtes suivantes → Authorization: Bearer {jwt}, identique à l'auth classique
```

### 2.3 Restriction par domaine email

- `ENTRA_ALLOWED_DOMAINS=waat.fr` → seuls `*@waat.fr` acceptés
- `ENTRA_ALLOWED_DOMAINS=waat.fr,client.com` → plusieurs domaines, virgule-séparés
- Non défini ou vide → aucune restriction de domaine
- La validation s'applique à **chaque login**, pas seulement à la création du compte
- Un changement de `ENTRA_ALLOWED_DOMAINS` prend effet immédiatement

Exemples avec `ENTRA_ALLOWED_DOMAINS=waat.fr` :

| Email | Résultat |
|---|---|
| `j.buget.ext@waat.fr` | ✅ Accepté (guest Entra traité comme membre) |
| `d.gourdon@waat.fr` | ✅ Accepté |
| `j.buget@pix.fr` | ❌ Rejeté — log `domain_rejected` |

### 2.4 Résolution du `full_name` depuis Entra

Priorité décroissante sur les claims Microsoft :

1. `givenName` + `" "` + `surname` (si les deux sont présents et non vides)
2. `displayName` (si présent et non vide)
3. Partie locale de l'email (avant le `@`)

### 2.5 Résolution de l'email depuis Entra

Priorité décroissante sur les claims Microsoft :

1. `mail`
2. `preferred_username`
3. `upn`

Les comptes **guests** (ex : `*.ext@waat.fr`) sont traités comme des membres ordinaires — aucune distinction sur le claim `userType`.

### 2.6 États d'un compte utilisateur

| État | `hashed_password` | `entra_id` | Connexion possible via |
|---|---|---|---|
| Local classique | ✅ | `None` | Email/password |
| SSO Entra only | `None` | ✅ | Entra SSO |
| Hybride (lié) | ✅ | ✅ | Email/password **ou** Entra SSO |

### 2.7 Liaison de compte existant

- Un compte email/password existant est détecté par son email au moment du premier login SSO
- L'`entra_id` (`oid`) est stocké sur le compte existant
- Le `hashed_password` est **conservé** — les deux méthodes de connexion restent fonctionnelles
- L'événement est tracé : log structuré `account_linked`

### 2.8 Compte existant désactivé

Si l'email ou l'`entra_id` correspond à un compte avec `is_active=False` :
- Connexion refusée, `HTTP 403`
- Comportement identique à l'auth classique — aucune réactivation automatique

### 2.9 Tentative de login email/password sur un compte SSO-only

- `hashed_password=None` → `InvalidCredentialsError` générique
- Même réponse `HTTP 401` qu'un mauvais mot de passe — aucun info leak sur le type de compte

### 2.10 Dérive d'email dans Entra

Si le compte est retrouvé par `oid` mais que l'email du token Entra diffère de l'email en base :
- L'email en base est mis à jour silencieusement avec le nouvel email Microsoft
- L'événement est tracé : log structuré `email_updated` (ancien email, nouvel email, user_id)

### 2.11 Déconnexion

| Config | Comportement |
|---|---|
| `ENTRA_SINGLE_LOGOUT=false` (défaut) | Logout local uniquement — JWT Raggae invalidé côté client, session Microsoft conservée |
| `ENTRA_SINGLE_LOGOUT=true` | Redirect vers `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/logout` après logout local |

### 2.12 Expiration du secret Azure

- Variable optionnelle `ENTRA_CLIENT_SECRET_EXPIRES_AT` (format ISO 8601)
- Au démarrage de l'application, si `ENTRA_ENABLED=true` et que la date est dans moins de 30 jours : log d'avertissement structuré

### 2.13 Audit log (logs structurés JSON)

Événements émis sur stdout en JSON :

| `event_type` | Déclencheur |
|---|---|
| `sso_login` | Connexion SSO réussie, compte déjà lié |
| `account_linked` | Première connexion SSO, compte email/password existant lié |
| `account_created` | Première connexion SSO, nouveau compte créé |
| `domain_rejected` | Domaine email non autorisé |
| `email_updated` | Dérive d'email détectée et corrigée |

Champs communs : `event_type`, `provider`, `user_id` (si connu), `email`, `timestamp`, `ip`.

---

## 3. Spécifications techniques

### 3.1 Protocole et bibliothèques

| Aspect | Choix |
|---|---|
| Flow OAuth | Authorization Code Flow |
| Sécurité | PKCE activé (géré par `msal`) |
| Validation token | Délégué à `msal` (JWKS, signature, claims) |
| Identifiant Microsoft | Claim `oid` (Object ID, stable dans le tenant) |
| Bibliothèque | `msal` (Microsoft Authentication Library for Python) |
| State CSRF | Cookie httponly signé via `itsdangerous` (TTL 5 min) |
| One-time code | UUID v4, dict in-memory, TTL 30s |

### 3.2 Structure du `state`

```python
@dataclass
class OAuthState:
    csrf_token: str       # UUID v4
    redirect_url: str     # URL de destination post-auth (défaut : "/")
    expires_at: datetime  # now + 5 minutes
```

Sérialisé, signé et stocké dans un cookie httponly `oauth_state`.

### 3.3 `EntraConfig` (injectable)

```python
@dataclass
class EntraConfig:
    client_id: str
    client_secret: str
    tenant_id: str
    redirect_uri: str
    allowed_domains: list[str]   # vide = pas de restriction
    single_logout: bool = False
    client_secret_expires_at: datetime | None = None
```

Injectée en paramètre dans les use cases et services (pas de singleton global),
pour faciliter l'évolution vers une config par organisation.

---

## 4. Variables d'environnement

```dotenv
# Activation
ENTRA_ENABLED=false                         # true pour activer

# Credentials Azure App Registration
ENTRA_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ENTRA_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxx
ENTRA_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# URL de callback (doit correspondre à l'App Registration Azure)
ENTRA_REDIRECT_URI=https://app.raggae.io/api/v1/auth/entra/callback

# Domaines autorisés (optionnel, virgule-séparé)
ENTRA_ALLOWED_DOMAINS=waat.fr

# Single Logout (optionnel)
ENTRA_SINGLE_LOGOUT=false

# Expiration du secret (optionnel, format ISO 8601)
ENTRA_CLIENT_SECRET_EXPIRES_AT=2027-03-01T00:00:00Z
```

---

## 5. Modifications par couche

### 5.1 Domain Layer

**`domain/entities/user.py`** — ajouts :

```python
@dataclass(frozen=True)
class User:
    # ... champs existants ...
    hashed_password: str | None      # None = compte SSO-only
    entra_id: str | None = None      # Microsoft Object ID (claim oid)

    def link_entra(self, entra_id: str) -> "User":
        return dataclasses.replace(self, entra_id=entra_id)

    def update_email(self, email: str) -> "User":
        return dataclasses.replace(self, email=email)

    def has_local_credentials(self) -> bool:
        return self.hashed_password is not None
```

**`domain/exceptions/user_exceptions.py`** — ajouts :

```python
class OAuthDomainNotAllowedError(Exception): ...
class OAuthProviderError(Exception): ...
```

### 5.2 Application Layer

**Nouveau port `application/interfaces/services/oauth_provider.py`** :

```python
@dataclass
class OAuthUserInfo:
    provider_id: str    # claim oid pour Entra
    email: str
    full_name: str
    provider: str       # "entra" | "google" | "github"

class OAuthProvider(Protocol):
    async def get_authorization_url(self, state: str, config: EntraConfig) -> str: ...
    async def exchange_code(
        self, code: str, state: str, config: EntraConfig
    ) -> OAuthUserInfo: ...
```

**Nouveau port `application/interfaces/repositories/user_repository.py`** — ajout :

```python
async def find_by_entra_id(self, entra_id: str) -> User | None: ...
```

**Nouveaux use cases** :

```
application/use_cases/user/
  ├── initiate_oauth_login.py      # génère OAuthState, retourne URL d'autorisation
  └── handle_oauth_callback.py    # traite callback, lie/crée compte, retourne LoginResult
```

`HandleOAuthCallback` — logique :

1. Valide le `state` (signature + expiration)
2. Appelle `oauth_provider.exchange_code(code, state, config)`
3. Valide le domaine email si `config.allowed_domains` non vide
4. `find_by_entra_id(oid)` → connexion directe + log `sso_login`
5. `find_by_email(email)` → `link_entra(oid)` + mise à jour email si divergent + log `account_linked`
6. Sinon → crée `User(entra_id=oid, hashed_password=None, ...)` + log `account_created`
7. Retourne `OAuthLoginResult(access_token, token_type, is_new_user, account_linked)`

**Nouveau DTO** :

```python
@dataclass
class OAuthLoginResult:
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False
    account_linked: bool = False
```

### 5.3 Infrastructure Layer

**`infrastructure/services/entra_oauth_provider.py`** :

```python
class EntraOAuthProvider:
    """Implémente OAuthProvider pour Microsoft Entra via msal."""

    async def get_authorization_url(self, state: str, config: EntraConfig) -> str:
        # msal.ConfidentialClientApplication
        # Scopes : ["openid", "profile", "email", "User.Read"]
        # PKCE géré automatiquement par msal
        ...

    async def exchange_code(
        self, code: str, state: str, config: EntraConfig
    ) -> OAuthUserInfo:
        # msal.acquire_token_by_authorization_code()
        # Validation signature + claims déléguée à msal
        # Extraction : oid → provider_id, mail/preferred_username/upn → email
        # Résolution full_name : givenName+surname → displayName → partie locale email
        ...
```

**`infrastructure/cache/oauth_code_store.py`** :

```python
class InMemoryOAuthCodeStore:
    """Stockage des one-time codes (UUID → JWT, TTL 30s).

    NOTE: incompatible avec un déploiement multi-instances.
    Migration vers Redis : extraire l'interface OAuthCodeStore et fournir
    une implémentation RedisOAuthCodeStore.
    """
    ...
```

**`infrastructure/database/models/user_model.py`** — ajouts :

```python
entra_id: Mapped[str | None] = mapped_column(
    String(255), unique=True, nullable=True, index=True
)
hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

**`infrastructure/database/repositories/sqlalchemy_user_repository.py`** — ajout :

```python
async def find_by_entra_id(self, entra_id: str) -> User | None: ...
```

**`infrastructure/config/settings.py`** — ajouts :

```python
entra_enabled: bool = False
entra_client_id: str = ""
entra_client_secret: str = ""
entra_tenant_id: str = ""
entra_redirect_uri: str = ""
entra_allowed_domains: list[str] = []
entra_single_logout: bool = False
entra_client_secret_expires_at: datetime | None = None
```

**Migration Alembic** :

```sql
-- Rendre hashed_password nullable
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;

-- Ajouter entra_id
ALTER TABLE users ADD COLUMN entra_id VARCHAR(255);
CREATE UNIQUE INDEX idx_users_entra_id ON users (entra_id)
  WHERE entra_id IS NOT NULL;
```

### 5.4 Presentation Layer

**Nouveaux endpoints** (`/api/v1/auth/entra`) :

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/v1/auth/entra/login` | GET | Génère l'URL Microsoft, pose cookie `oauth_state`, redirige |
| `/api/v1/auth/entra/callback` | GET | Reçoit `code`+`state`, génère one-time code, redirige frontend |
| `/api/v1/auth/entra/token` | POST | Échange one-time code contre JWT Raggae |

Si `ENTRA_ENABLED=false` : les trois endpoints retournent `HTTP 501 Not Implemented`.

**Schémas** :

```python
class OAuthTokenRequest(BaseModel):
    code: str

class OAuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool
    account_linked: bool
```

**Démarrage de l'application** (`main.py`) :

```python
# Au startup, si ENTRA_ENABLED et ENTRA_CLIENT_SECRET_EXPIRES_AT < now + 30 jours
logger.warning({
    "event": "entra_secret_expiring_soon",
    "expires_at": settings.entra_client_secret_expires_at,
    "days_remaining": ...,
})
```

---

## 6. Stratégie de tests

### Unit tests

| Scénario | Composant testé |
|---|---|
| `link_entra()` retourne une nouvelle instance avec `entra_id` | `User` entity |
| `has_local_credentials()` selon `hashed_password` | `User` entity |
| `update_email()` retourne une nouvelle instance | `User` entity |
| Résolution `full_name` (3 cas de fallback) | `EntraOAuthProvider` |
| Résolution email (`mail` → `preferred_username` → `upn`) | `EntraOAuthProvider` |
| Validation de domaine (autorisé, refusé, liste vide) | `HandleOAuthCallback` |
| Compte trouvé par `entra_id` → connexion directe | `HandleOAuthCallback` |
| Compte trouvé par email → liaison + `account_linked` | `HandleOAuthCallback` |
| Nouveau compte → création + `account_created` | `HandleOAuthCallback` |
| Dérive d'email → mise à jour + `email_updated` | `HandleOAuthCallback` |
| Compte désactivé → `UserAlreadyInactiveError` | `HandleOAuthCallback` |
| `hashed_password=None` → `InvalidCredentialsError` | `LoginUser` |
| Expiration state CSRF | `InitiateOAuthLogin` |
| One-time code usage unique et TTL | `InMemoryOAuthCodeStore` |

Fakes à créer : `FakeEntraOAuthProvider`, `InMemoryOAuthCodeStore` (déjà impl. pour prod).

### Integration tests

| Scénario | Composant testé |
|---|---|
| `find_by_entra_id` sur PostgreSQL | `SQLAlchemyUserRepository` |
| `hashed_password` nullable en base | Migration Alembic |
| `entra_id` unique en base | Migration Alembic |

### E2E tests

Flow complet avec `pytest-httpx` pour mocker les endpoints Microsoft :

- Login SSO → création compte → échange one-time code → JWT valide
- Login SSO → liaison compte existant
- Login SSO → domaine refusé → 403
- Login SSO → compte désactivé → 403

---

## 7. Ordre d'implémentation

Les étapes suivent le principe **Red-Green-Refactor**, chacune compilable et testée.

| Étape | Contenu | Couche |
|---|---|---|
| 1 | Migration : `entra_id` nullable + `hashed_password` nullable | Infrastructure |
| 2 | `User` : champ `entra_id`, méthodes `link_entra()`, `update_email()`, `has_local_credentials()` | Domain |
| 3 | Nouvelles exceptions : `OAuthDomainNotAllowedError`, `OAuthProviderError` | Domain |
| 4 | `UserRepository` : `find_by_entra_id` (interface + SQLAlchemy + InMemory) | Application/Infra |
| 5 | Port `OAuthProvider` + `OAuthUserInfo` + `EntraConfig` | Application |
| 6 | `LoginUser` : gestion `hashed_password=None` → `InvalidCredentialsError` | Application |
| 7 | Use case `InitiateOAuthLogin` (TDD) | Application |
| 8 | Use case `HandleOAuthCallback` (TDD, avec `FakeEntraOAuthProvider`) | Application |
| 9 | Settings Entra + validation `EntraConfig` au démarrage + warning expiration | Infrastructure |
| 10 | `EntraOAuthProvider` avec `msal` (PKCE, validation token, résolution claims) | Infrastructure |
| 11 | `InMemoryOAuthCodeStore` (one-time codes, TTL 30s) | Infrastructure |
| 12 | Endpoints `/entra/login`, `/entra/callback`, `/entra/token` | Presentation |
| 13 | Gestion `oauth_state` (cookie signé `itsdangerous`, deep linking) | Presentation |
| 14 | Single Logout (`ENTRA_SINGLE_LOGOUT`) | Presentation |
| 15 | Logs structurés JSON pour tous les événements SSO | Transverse |
| 16 | Tests E2E avec mock Microsoft | Tests |
| 17 | Mise à jour `.env.example` et documentation | Docs |

---

## 8. Hors scope v1

- Ajout d'un mot de passe sur un compte SSO-only (futur : via flow "mot de passe oublié")
- Stockage et utilisation du refresh token Entra
- Config Entra par organisation (architecture prête, config en env vars pour l'instant)
- Vérification active de révocation à chaque requête
- Stockage multi-instances du one-time code (migration Redis triviale via interface)
- Interface d'administration des comptes SSO

---

## 9. Évolutions futures

### Autres providers OAuth (Google, GitHub)

L'interface `OAuthProvider` est générique. Pour ajouter un provider :

1. Ajouter `google_id` / `github_id` dans l'entité `User` + migration
2. Créer `GoogleOAuthProvider` / `GitHubOAuthProvider` implémentant `OAuthProvider`
3. Ajouter les variables d'env `GOOGLE_*` / `GITHUB_*`
4. Enregistrer les endpoints `/api/v1/auth/google/*` / `/api/v1/auth/github/*`

Le use case `HandleOAuthCallback` est **générique** et réutilisable sans modification.

### Config Entra par organisation (multi-tenant SaaS)

`EntraConfig` étant déjà injectable, la migration consiste à :

1. Créer une table `org_entra_configs` (client_id, client_secret chiffré, tenant_id, etc.)
2. Résoudre la config depuis la base plutôt que depuis `settings`
3. Router le callback OAuth vers la bonne org (via un paramètre `org_slug` dans le `state`)

### Scalabilité horizontale du one-time code store

Extraire `OAuthCodeStore` en interface et fournir `RedisOAuthCodeStore` :

```python
class OAuthCodeStore(Protocol):
    async def store(self, code: str, jwt: str, ttl_seconds: int) -> None: ...
    async def consume(self, code: str) -> str | None: ...  # None si expiré/déjà utilisé
```
