# AGENTS.md - Guide pour Claude Code

## Vue d'ensemble du projet

**Raggae** (RAG Generator Agent Expert) est une plateforme permettant de créer, gérer et publier des agents conversationnels basés sur RAG (Retrieval Augmented Generation).

## Principes de développement OBLIGATOIRES

### 1. Clean Architecture

Respecter strictement la séparation en couches :

```
Domain Layer (Entities)
    ↓
Application Layer (Use Cases)
    ↓
Infrastructure Layer (Repositories, External Services)
    ↓
Presentation Layer (API, Controllers)
```

**Règles impératives :**
- Les entités du domaine ne dépendent de RIEN
- Les use cases ne dépendent QUE des entités et des interfaces
- L'infrastructure implémente les interfaces définies par les use cases
- La couche présentation (API) orchestre les use cases

### 2. Test-Driven Development (TDD)

**Cycle Red-Green-Refactor STRICT :**

1. **RED** : Écrire un test qui échoue
2. **GREEN** : Écrire le code minimum pour faire passer le test
3. **REFACTOR** : Améliorer le code sans casser les tests

**Jamais de code sans test préalable.**

### 3. Baby Steps

- Une fonctionnalité = une série de petits commits
- Chaque commit doit :
  - Compiler
  - Passer tous les tests
  - Apporter une amélioration mesurable
- Maximum 50-100 lignes de code par commit

### 4. Conventional Commits

Format strict :
```
type(scope): description

[optional body]
```

Types autorisés :
- `feat`: nouvelle fonctionnalité
- `fix`: correction de bug
- `test`: ajout/modification de tests
- `refactor`: refactoring sans changement de comportement
- `docs`: documentation
- `chore`: tâches de maintenance
- `build`: configuration build/deps

**JAMAIS de mention de Claude ou co-auteur dans les commits.**

## Structure du projet Backend (Clean Architecture)

```
server/
├── src/raggae/
│   ├── domain/                     # Couche Domaine (aucune dépendance externe)
│   │   ├── entities/               # 13 entités : User, Project, Document, DocumentChunk,
│   │   │   │                       #   Conversation, Message, Organization, OrganizationMember,
│   │   │   │                       #   OrganizationInvitation, UserModelProviderCredential,
│   │   │   │                       #   OrgModelProviderCredential, ProjectSnapshot
│   │   ├── value_objects/          # Email, Password, Embedding, etc.
│   │   └── exceptions/             # Exceptions métier par domaine
│   │
│   ├── application/                # Couche Application
│   │   ├── use_cases/              # 70+ use cases organisés par domaine :
│   │   │   ├── user/               #   register, login, oauth, update, get_current
│   │   │   ├── organization/       #   CRUD + membres + invitations + config
│   │   │   ├── project/            #   CRUD + publish/unpublish + reindex
│   │   │   ├── document/           #   upload, delete, reindex, list_chunks
│   │   │   ├── chat/               #   send_message (streaming), conversations, messages
│   │   │   ├── credentials/        #   user & org level, activate/deactivate
│   │   │   └── project_snapshot/   #   create, get, list, restore
│   │   ├── interfaces/             # Ports (repositories + services)
│   │   ├── dto/                    # 25+ Data Transfer Objects
│   │   ├── services/               # Services applicatifs
│   │   └── config/                 # Config OAuth (Entra)
│   │
│   ├── infrastructure/             # Couche Infrastructure
│   │   ├── database/
│   │   │   ├── models/             # 14 modèles SQLAlchemy
│   │   │   └── repositories/       # 25 repositories (SQLAlchemy + InMemory pour tests)
│   │   ├── services/               # 44 implémentations de services :
│   │   │   │                       #   bcrypt, JWT, OpenAI embeddings/LLM, sentence-transformers,
│   │   │   │                       #   MinIO, PDF/DOCX extractors, reranking, BM25, MSAL OAuth
│   │   ├── cache/                  # Couche de cache
│   │   └── config/                 # Settings (pydantic-settings)
│   │
│   └── presentation/               # Couche Présentation
│       └── api/v1/
│           ├── endpoints/          # 11 fichiers FastAPI :
│           │   │                   #   auth, entra, organizations, projects, documents,
│           │   │                   #   chat, model_credentials, org_model_credentials,
│           │   │                   #   project_snapshots, model_catalog, org_default_config
│           ├── schemas/            # Schemas Pydantic (request/response)
│           └── dependencies.py
│
├── tests/                          # Miroir de src/ (~160 fichiers)
│   ├── unit/                       # 139 fichiers (domain, application, infrastructure)
│   ├── integration/
│   └── e2e/
│
├── alembic/versions/               # 39 migrations (fondations → OAuth → snapshots)
├── pyproject.toml
└── .env.example
```

## Workflow de développement

### Exemple : Implémenter "Register User"

#### Étape 1 : Test de l'entité User
```bash
# Fichier : tests/unit/domain/entities/test_user.py
```

**Test (RED)** :
```python
def test_create_user_with_valid_data():
    user = User(
        id=UserId(uuid4()),
        email=Email("user@example.com"),
        password=HashedPassword("hashed_pwd"),
        full_name="John Doe"
    )
    assert user.email.value == "user@example.com"
```

**Code (GREEN)** :
```python
# src/raggae/domain/entities/user.py
@dataclass(frozen=True)
class User:
    id: UserId
    email: Email
    password: HashedPassword
    full_name: str
    is_active: bool = True
```

**Commit** :
```
test(domain): add user entity creation test
```

#### Étape 2 : Value Object Email
**Test (RED)** :
```python
def test_email_rejects_invalid_format():
    with pytest.raises(InvalidEmailError):
        Email("not-an-email")
```

**Code (GREEN)** :
```python
# src/raggae/domain/value_objects/email.py
```

**Commit** :
```
feat(domain): add email value object with validation
```

#### Étape 3 : Use Case RegisterUser
**Test (RED)** :
```python
async def test_register_user_success():
    repo = InMemoryUserRepository()
    hasher = FakePasswordHasher()
    use_case = RegisterUser(repo, hasher)
    
    result = await use_case.execute(
        email="user@example.com",
        password="SecurePass123!",
        full_name="John Doe"
    )
    
    assert result.email == "user@example.com"
```

**Code (GREEN)** :
```python
# src/raggae/application/use_cases/user/register_user.py
```

**Commit** :
```
feat(application): implement register user use case
```

#### Étape 4 : Repository SQLAlchemy
**Test (INTEGRATION)** :
```python
async def test_sqlalchemy_user_repository_save():
    # Test avec vraie DB (testcontainers ou DB test)
```

**Code (GREEN)** :
```python
# src/raggae/infrastructure/database/repositories/sqlalchemy_user_repository.py
```

**Commit** :
```
feat(infrastructure): implement sqlalchemy user repository
```

#### Étape 5 : API Endpoint
**Test (E2E)** :
```python
async def test_register_endpoint_returns_201():
    response = client.post("/api/v1/auth/register", json={
        "email": "user@example.com",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    })
    assert response.status_code == 201
```

**Code (GREEN)** :
```python
# src/raggae/presentation/api/v1/endpoints/auth.py
```

**Commit** :
```
feat(api): add user registration endpoint
```

## Règles de test

### Pyramide des tests
- **70% Unit tests** : Domaine + Application (use cases)
- **20% Integration tests** : Infrastructure (repositories, services)
- **10% E2E tests** : API complète

### Conventions de nommage
```python
# Unit tests
def test_<what>_<condition>_<expected>():
    # Given
    # When
    # Then

# Integration tests
async def test_integration_<component>_<scenario>():
    pass

# E2E tests
async def test_e2e_<feature>_<scenario>():
    pass
```

### Fixtures et mocks
```python
# tests/conftest.py
@pytest.fixture
def in_memory_user_repository():
    return InMemoryUserRepository()

@pytest.fixture
def fake_password_hasher():
    return FakePasswordHasher()
```

## Commandes essentielles

```bash
# Lancer les tests
pytest                              # Tous les tests
pytest tests/unit                   # Tests unitaires seulement
pytest -v -s                        # Verbose avec output
pytest --cov=src --cov-report=html  # Coverage

# Linting
ruff check src/
mypy src/

# Formatting
ruff format src/

# Migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

## Checklist avant chaque commit

- [ ] Les tests passent (`pytest`)
- [ ] Le code est formaté (`ruff format`)
- [ ] Pas d'erreur de linting (`ruff check`)
- [ ] Type hints vérifiés (`mypy`)
- [ ] Commit message en Conventional Commits
- [ ] Changement atomique (une seule chose)

## Dépendances critiques

```toml
# pyproject.toml
[project]
dependencies = [
    # API & serveur
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "python-multipart>=0.0.6",
    "httpx>=0.26.0",

    # Base de données
    "sqlalchemy[asyncio]>=2.0.25",
    "alembic>=1.13.0",
    "asyncpg>=0.29.0",
    "pgvector>=0.2.4",

    # Auth & sécurité
    "python-jose[cryptography]>=3.3.0",
    "bcrypt>=4.0.0",
    "msal>=1.30.0",         # OAuth Entra/Microsoft
    "itsdangerous>=2.1.0",

    # LLM & embeddings
    "openai>=1.10.0",
    "sentence-transformers>=3.0.0",
    "llama-index-core>=0.12.0",

    # Traitement documentaire
    "pypdf>=5.0.0",
    "python-docx>=1.1.0",
    "langdetect>=1.0.9",

    # RAG avancé
    "keybert>=0.8.5",
    "scikit-learn>=1.5.0",

    # Stockage fichiers
    "minio>=7.2.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "types-python-jose>=3.3.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]
```

## Périmètre fonctionnel implémenté

Authentification (local + OAuth Entra/MSAL), gestion des utilisateurs, organisations multi-tenant
(membres, invitations, rôles), projets RAG (CRUD, publication, reindex, snapshots), gestion documentaire
(upload PDF/DOCX/MD, chunking adaptatif, embeddings pgvector, recherche hybride BM25 + vecteur, reranking),
chat avec streaming et scoring de fiabilité, gestion des credentials LLM (user & org level), catalogue
de providers. Voir l'historique git pour le détail des changements.

## Prochaines itérations possibles

- Traitement documentaire asynchrone (queue de jobs)
- Support multi-LLM étendu (Mistral, Anthropic, etc.)
- Évaluation de la qualité RAG (métriques automatisées)
- Webhooks / notifications
- Frontend complet (Next.js)

## Points d'attention pour Claude Code

1. **Toujours commencer par le test**
2. **Respecter la Clean Architecture** (pas de dépendances inversées)
3. **Un commit = un changement atomique**
4. **Ne jamais skipper le refactoring**
5. **Maintenir une couverture de tests > 80%**
6. **Documentation inline (docstrings) pour use cases et entités**

## En cas de blocage

Si tu es bloqué :
1. Revenir au dernier test qui passe
2. Découper le problème en plus petits morceaux
3. Écrire un test encore plus simple
4. Demander une revue de l'approche

---

**Important** : Ce fichier est la référence absolue pour le développement. Toute déviation doit être documentée et justifiée.
