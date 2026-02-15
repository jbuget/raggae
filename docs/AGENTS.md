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
├── src/
│   ├── raggae/
│   │   ├── domain/                 # Couche Domaine
│   │   │   ├── entities/           # Entités métier pures
│   │   │   │   ├── user.py
│   │   │   │   ├── project.py
│   │   │   │   ├── document.py
│   │   │   │   └── conversation.py
│   │   │   ├── value_objects/      # Value Objects
│   │   │   │   ├── email.py
│   │   │   │   ├── password.py
│   │   │   │   └── embedding.py
│   │   │   └── exceptions/         # Exceptions métier
│   │   │       ├── user_exceptions.py
│   │   │       └── project_exceptions.py
│   │   │
│   │   ├── application/            # Couche Application
│   │   │   ├── use_cases/          # Use Cases
│   │   │   │   ├── user/
│   │   │   │   │   ├── register_user.py
│   │   │   │   │   ├── login_user.py
│   │   │   │   │   └── update_user.py
│   │   │   │   ├── project/
│   │   │   │   │   ├── create_project.py
│   │   │   │   │   ├── update_project.py
│   │   │   │   │   └── publish_project.py
│   │   │   │   ├── document/
│   │   │   │   │   ├── upload_document.py
│   │   │   │   │   └── process_document.py
│   │   │   │   └── chat/
│   │   │   │       └── send_message.py
│   │   │   ├── interfaces/         # Interfaces (Ports)
│   │   │   │   ├── repositories/
│   │   │   │   │   ├── user_repository.py
│   │   │   │   │   ├── project_repository.py
│   │   │   │   │   └── document_repository.py
│   │   │   │   └── services/
│   │   │   │       ├── password_hasher.py
│   │   │   │       ├── token_service.py
│   │   │   │       ├── embedding_service.py
│   │   │   │       └── llm_service.py
│   │   │   └── dto/                # Data Transfer Objects
│   │   │       ├── user_dto.py
│   │   │       └── project_dto.py
│   │   │
│   │   ├── infrastructure/         # Couche Infrastructure
│   │   │   ├── database/
│   │   │   │   ├── models/         # SQLAlchemy models
│   │   │   │   │   ├── user_model.py
│   │   │   │   │   └── project_model.py
│   │   │   │   ├── repositories/   # Implémentations repositories
│   │   │   │   │   ├── sqlalchemy_user_repository.py
│   │   │   │   │   └── sqlalchemy_project_repository.py
│   │   │   │   └── session.py
│   │   │   ├── services/           # Implémentations services
│   │   │   │   ├── bcrypt_password_hasher.py
│   │   │   │   ├── jwt_token_service.py
│   │   │   │   ├── openai_embedding_service.py
│   │   │   │   └── openai_llm_service.py
│   │   │   └── config/
│   │   │       └── settings.py
│   │   │
│   │   └── presentation/           # Couche Présentation
│   │       ├── api/
│   │       │   ├── v1/
│   │       │   │   ├── endpoints/
│   │       │   │   │   ├── auth.py
│   │       │   │   │   ├── users.py
│   │       │   │   │   ├── projects.py
│   │       │   │   │   └── chat.py
│   │       │   │   └── schemas/    # Pydantic schemas (API)
│   │       │   │       ├── user_schema.py
│   │       │   │       └── project_schema.py
│   │       │   └── dependencies.py
│   │       └── main.py
│   │
│   └── tests/                      # Tests miroir de src/
│       ├── unit/
│       │   ├── domain/
│       │   ├── application/
│       │   └── infrastructure/
│       ├── integration/
│       └── e2e/
│
├── alembic/                        # Migrations
├── pyproject.toml
├── pytest.ini
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
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.25",
    "alembic>=1.13.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "openai>=1.10.0",
    "pgvector>=0.2.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]
```

## Ordre de développement recommandé

### Sprint 1 : Fondations
1. Setup projet + Docker Compose
2. Migrations Alembic initiales
3. Entités domaine (User, Project)
4. Value Objects (Email, Password)

### Sprint 2 : Authentification
1. Use Case RegisterUser (TDD)
2. Use Case LoginUser (TDD)
3. Password Hasher + JWT Service
4. User Repository (SQLAlchemy)
5. API Auth endpoints

### Sprint 3 : Projects CRUD
1. Use Cases Project (Create, Update, Delete, List)
2. Project Repository
3. API Project endpoints

### Sprint 4 : Documents & RAG
#### Sprint 4A : Upload & gestion documentaire (MVP)
1. Entité `Document` + exceptions métier associées
2. Use Case `UploadDocument` (formats `txt/md/pdf/doc/docx`, max 100Mo)
3. Use Case `ListProjectDocuments`
4. Use Case `DeleteDocument` (suppression storage + métadonnées)
5. Port `FileStorageService` (S3-compatible) + adapter MinIO local
6. Endpoints API documents sous `/projects/{project_id}/documents` (auth obligatoire)

#### Sprint 4B : Processing & indexation (itération suivante)
1. `Document Processing Service` (d'abord synchrone)
2. `Embedding Service` (OpenAI)
3. `DocumentChunk` + stockage embeddings en `pgvector`
4. Possibilité d'activer un mode asynchrone via variable d'environnement

#### Sprint 4C : Stratégies de chunking adaptatives
1. Ajouter un port `DocumentStructureAnalyzer` pour classifier la structure du texte extrait
2. Définir un `ChunkingStrategySelector` (règles déterministes) basé sur le résultat d'analyse
3. Introduire plusieurs stratégies de chunking derrière un port commun :
   - `fixed_window` (fallback sûr)
   - `paragraph` (documents narratifs)
   - `heading_section` (documents structurés en sections/titres)
4. Persister la stratégie choisie sur le document (ou dans metadata processing) pour audit/debug
5. Ajouter tests unitaires du selector + tests d'intégration du pipeline selon type de document

### Sprint 5 : Chat
1. Use Case SendMessage
2. RAG Service (retrieval + generation)
3. Chat API (streaming)

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
