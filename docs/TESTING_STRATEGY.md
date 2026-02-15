# TESTING_STRATEGY.md - Stratégie de tests

## Philosophie des tests

> "Tests are specifications, not afterthoughts."

Les tests définissent le comportement attendu du système. Ils sont écrits **AVANT** le code (TDD) et servent de documentation vivante.

## Focus Sprint 4A (Documents upload)

Comportements minimaux à couvrir :

- Upload document accepté pour `txt`, `md`, `pdf`, `doc`, `docx`.
- Rejet des extensions non autorisées.
- Rejet des fichiers > `100 Mo`.
- Ownership strict : un utilisateur ne peut ni lister ni supprimer les documents d'un projet qu'il ne possède pas.
- Suppression document : suppression metadata + suppression objet S3-compatible.

Répartition recommandée :

- Unit tests : validations métier (`type`, `size`, ownership checks dans use cases).
- Integration tests : adapter S3-compatible (MinIO) et repository document.
- E2E tests : `POST/GET/DELETE /projects/{project_id}/documents` avec auth bearer.

## Pyramide des tests

```
        /\
       /  \      E2E Tests (10%)
      /    \     - Lents (< 500ms)
     /------\    - Fragiles
    /        \   - Haute valeur métier
   /  Integration Tests (20%)
  /            \ - Moyens (< 100ms)
 /              \- DB réelle
/________________\ 
   Unit Tests (70%)
   - Rapides (< 1ms)
   - Isolés
   - Nombreux
```

### Distribution recommandée

| Type | Quantité | Temps | Scope |
|------|----------|-------|-------|
| Unit | 70% | < 1ms | Domain + Application |
| Integration | 20% | < 100ms | Infrastructure |
| E2E | 10% | < 500ms | API complète |

## Tests unitaires (Domain + Application)

### Caractéristiques

- **Ultra rapides** : < 1ms par test
- **Isolés** : Pas de DB, pas de réseau, pas de fichiers
- **Déterministes** : Même résultat à chaque exécution
- **Nombreux** : 10-20 tests par classe

### Ce qu'on teste

#### Domain Layer

**Entités** :
```python
# tests/unit/domain/entities/test_user.py
class TestUser:
    def test_create_user_with_valid_data(self):
        """Vérifie création d'un utilisateur valide."""
        
    def test_user_immutability(self):
        """Vérifie que l'entité est immuable."""
        
    def test_deactivate_active_user(self):
        """Vérifie la désactivation d'un utilisateur actif."""
        
    def test_deactivate_inactive_user_raises_error(self):
        """Vérifie qu'on ne peut pas désactiver un utilisateur déjà inactif."""
```

**Value Objects** :
```python
# tests/unit/domain/value_objects/test_email.py
class TestEmail:
    def test_create_email_with_valid_format(self):
        """Email valide est accepté."""
        
    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "@example.com",
        "user@",
        "",
    ])
    def test_create_email_with_invalid_format_raises_error(self, invalid_email):
        """Emails invalides sont rejetés."""
```

#### Application Layer

**Use Cases** :
```python
# tests/unit/application/use_cases/user/test_register_user.py
class TestRegisterUser:
    def test_register_user_success(self):
        """Inscription réussie avec données valides."""
        
    def test_register_user_email_already_exists(self):
        """Inscription échoue si email déjà utilisé."""
        
    def test_register_user_weak_password(self):
        """Inscription échoue si mot de passe trop faible."""
```

### Patterns de tests unitaires

#### Given-When-Then

```python
def test_publish_unpublished_project(self):
    # Given - État initial
    project = Project(
        id=uuid4(),
        user_id=uuid4(),
        name="Test Project",
        description="",
        system_prompt="prompt",
        is_published=False,
        created_at=datetime.utcnow()
    )
    
    # When - Action
    published = project.publish()
    
    # Then - Vérifications
    assert published.is_published is True
    assert published.id == project.id
```

#### Mocks et Stubs

```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_user_repository():
    """Repository mocké pour tests."""
    return AsyncMock()

@pytest.fixture
def mock_password_hasher():
    """Password hasher mocké."""
    hasher = AsyncMock()
    hasher.hash.return_value = "hashed_password"
    return hasher

async def test_register_user_success(
    mock_user_repository,
    mock_password_hasher
):
    # Given
    mock_user_repository.find_by_email.return_value = None
    use_case = RegisterUser(mock_user_repository, mock_password_hasher)
    
    # When
    result = await use_case.execute(
        email="test@example.com",
        password="SecurePass123!",
        full_name="Test User"
    )
    
    # Then
    assert result.email == "test@example.com"
    mock_password_hasher.hash.assert_called_once_with("SecurePass123!")
    mock_user_repository.save.assert_called_once()
```

#### Parametrize pour cas multiples

```python
@pytest.mark.parametrize("email,password,expected_error", [
    ("invalid", "Pass123!", InvalidEmailError),
    ("test@example.com", "weak", WeakPasswordError),
    ("", "Pass123!", InvalidEmailError),
])
async def test_register_user_validation_errors(
    email,
    password,
    expected_error
):
    use_case = RegisterUser(...)
    
    with pytest.raises(expected_error):
        await use_case.execute(
            email=email,
            password=password,
            full_name="Test"
        )
```

## Tests d'intégration (Infrastructure)

### Caractéristiques

- **Moyens** : < 100ms par test
- **DB réelle** : PostgreSQL de test
- **Isolés** : Chaque test dans une transaction
- **Moins nombreux** : Focus sur les implémentations critiques

### Ce qu'on teste

- Repositories (SQLAlchemy)
- Services externes (OpenAI, si mocké)
- Migrations de DB

### Setup de la DB de test

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from raggae.infrastructure.database.models import Base

@pytest.fixture(scope="session")
def test_database_url():
    """URL de la base de données de test."""
    return "postgresql+asyncpg://test:test@localhost:5433/raggae_test"

@pytest.fixture(scope="session")
async def test_engine(test_database_url):
    """Engine SQLAlchemy pour tests."""
    engine = create_async_engine(test_database_url, echo=False)
    
    # Créer toutes les tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Nettoyer
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Session DB isolée par test."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        async with session.begin():
            yield session
            # Rollback automatique à la fin du test
            await session.rollback()
```

### Exemple de test d'intégration

```python
# tests/integration/infrastructure/repositories/test_sqlalchemy_user_repository.py
import pytest
from uuid import uuid4
from datetime import datetime
from raggae.domain.entities.user import User
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)

class TestSQLAlchemyUserRepository:
    async def test_save_and_find_by_id(self, db_session):
        # Given
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # When
        await repo.save(user)
        await db_session.commit()
        
        found = await repo.find_by_id(user.id)
        
        # Then
        assert found is not None
        assert found.id == user.id
        assert found.email == user.email
    
    async def test_find_by_email_not_found(self, db_session):
        # Given
        repo = SQLAlchemyUserRepository(db_session)
        
        # When
        result = await repo.find_by_email("nonexistent@example.com")
        
        # Then
        assert result is None
    
    async def test_update_user(self, db_session):
        # Given
        repo = SQLAlchemyUserRepository(db_session)
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Original Name",
            is_active=True,
            created_at=datetime.utcnow()
        )
        await repo.save(user)
        await db_session.commit()
        
        # When
        updated_user = user.with_full_name("Updated Name")
        await repo.save(updated_user)
        await db_session.commit()
        
        found = await repo.find_by_id(user.id)
        
        # Then
        assert found.full_name == "Updated Name"
```

### DB de test avec Docker

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  postgres-test:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: raggae_test
    ports:
      - "5433:5432"
    tmpfs:
      - /var/lib/postgresql/data  # In-memory pour vitesse
```

```bash
# Lancer la DB de test
docker-compose -f docker-compose.test.yml up -d

# Lancer les tests d'intégration
pytest tests/integration

# Arrêter
docker-compose -f docker-compose.test.yml down
```

## Tests E2E (API)

### Caractéristiques

- **Lents** : < 500ms par test
- **Fragiles** : Dépendent de toute la stack
- **Haute valeur** : Testent les scénarios utilisateur complets
- **Peu nombreux** : Focus sur les happy paths et cas critiques

### Ce qu'on teste

- Endpoints API complets
- Flows utilisateur (register → login → create project)
- Validations Pydantic
- Codes HTTP
- Authentification

### Setup du client de test

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from raggae.presentation.main import app

@pytest.fixture
async def client():
    """Client HTTP pour tests E2E."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def authenticated_client(client):
    """Client HTTP authentifié."""
    # Register
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    
    return client
```

### Exemple de tests E2E

```python
# tests/e2e/api/v1/test_auth_flow.py
import pytest

class TestAuthFlow:
    async def test_register_login_flow(self, client):
        # Register
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User"
            }
        )
        
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == "newuser@example.com"
        assert "id" in user_data
        assert "password" not in user_data
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
    
    async def test_register_duplicate_email(self, client):
        # Premier utilisateur
        await client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass123!",
            "full_name": "First"
        })
        
        # Tentative de duplication
        response = await client.post("/api/v1/auth/register", json={
            "email": "duplicate@example.com",
            "password": "Pass456!",
            "full_name": "Second"
        })
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
```

```python
# tests/e2e/api/v1/test_project_flow.py
class TestProjectFlow:
    async def test_create_and_get_project(self, authenticated_client):
        # Create
        create_response = await authenticated_client.post(
            "/api/v1/projects",
            json={
                "name": "My RAG Agent",
                "description": "A helpful assistant",
                "system_prompt": "You are a helpful AI assistant"
            }
        )
        
        assert create_response.status_code == 201
        project = create_response.json()
        project_id = project["id"]
        
        # Get
        get_response = await authenticated_client.get(
            f"/api/v1/projects/{project_id}"
        )
        
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["id"] == project_id
        assert retrieved["name"] == "My RAG Agent"
    
    async def test_unauthorized_access(self, client):
        # Sans token
        response = await client.get("/api/v1/projects")
        
        assert response.status_code == 401
```

## Fixtures et Factories

### Factories pour tests

```python
# tests/factories.py
from uuid import uuid4
from datetime import datetime
from raggae.domain.entities.user import User
from raggae.domain.entities.project import Project

class UserFactory:
    @staticmethod
    def create(
        email: str = "test@example.com",
        full_name: str = "Test User",
        is_active: bool = True,
        **kwargs
    ) -> User:
        return User(
            id=kwargs.get("id", uuid4()),
            email=email,
            hashed_password=kwargs.get("hashed_password", "hashed"),
            full_name=full_name,
            is_active=is_active,
            created_at=kwargs.get("created_at", datetime.utcnow())
        )

class ProjectFactory:
    @staticmethod
    def create(
        name: str = "Test Project",
        user_id: UUID | None = None,
        **kwargs
    ) -> Project:
        return Project(
            id=kwargs.get("id", uuid4()),
            user_id=user_id or uuid4(),
            name=name,
            description=kwargs.get("description", "Test description"),
            system_prompt=kwargs.get("system_prompt", "Test prompt"),
            is_published=kwargs.get("is_published", False),
            created_at=kwargs.get("created_at", datetime.utcnow())
        )
```

Usage :

```python
def test_with_factory():
    user = UserFactory.create(email="custom@example.com")
    project = ProjectFactory.create(user_id=user.id, name="Custom Project")
```

### Fixtures communes

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_user():
    return UserFactory.create()

@pytest.fixture
def sample_project(sample_user):
    return ProjectFactory.create(user_id=sample_user.id)

@pytest.fixture
def multiple_projects(sample_user):
    return [
        ProjectFactory.create(user_id=sample_user.id, name=f"Project {i}")
        for i in range(5)
    ]
```

## Coverage et qualité

### Objectifs de coverage

- **Global** : > 80%
- **Domain** : 100%
- **Application** : > 90%
- **Infrastructure** : > 70%
- **Presentation** : > 60%

### Mesurer la coverage

```bash
# Générer le rapport
pytest --cov=src --cov-report=html --cov-report=term-missing

# Ouvrir le rapport HTML
open htmlcov/index.html

# Coverage par fichier
pytest --cov=src --cov-report=term-missing

# Échouer si coverage < 80%
pytest --cov=src --cov-fail-under=80
```

### Configuration pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests"
]
```

### Exécution sélective

```bash
# Par marker
pytest -m unit           # Tests unitaires seulement
pytest -m integration    # Tests d'intégration seulement
pytest -m e2e            # Tests E2E seulement

# Exclure les lents
pytest -m "not slow"

# Par répertoire
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Par fichier
pytest tests/unit/domain/entities/test_user.py

# Par test
pytest tests/unit/domain/entities/test_user.py::TestUser::test_create_user

# Parallèle (plus rapide)
pytest -n auto  # Requiert pytest-xdist
```

## Bonnes pratiques

### ✅ DO

- **Un test = un comportement**
- **Nommage descriptif** : `test_<what>_<condition>_<expected>`
- **Given-When-Then** pour la structure
- **Arrange-Act-Assert** (synonyme)
- **Tests isolés** : pas de dépendances entre tests
- **Mocks pour les dépendances externes**
- **Factories pour les données de test**

### ❌ DON'T

- **Tests qui dépendent de l'ordre d'exécution**
- **Tests qui modifient l'état global**
- **Tests avec sleeps ou timeouts**
- **Tests trop longs** (> 1s pour unit, > 100ms pour integration)
- **Tests fragiles** (dépendent de détails d'implémentation)
- **Assertions multiples non liées**

## Debugging des tests

### PDB (Python Debugger)

```bash
# Lancer avec debugger
pytest --pdb

# Stopper au premier échec
pytest -x --pdb

# PDB sur échec seulement
pytest --pdb-trace
```

```python
# Dans le test
def test_something():
    result = some_function()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

### Logs en mode verbose

```bash
# Output complet
pytest -vv -s

# Logs capturés
pytest --log-cli-level=DEBUG
```

### Tests en isolation

```bash
# Un seul test
pytest tests/unit/domain/entities/test_user.py::TestUser::test_create_user -vv

# Réexécuter les échecs
pytest --lf  # last-failed
pytest --ff  # failed-first
```

## CI/CD

### GitHub Actions exemple

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: raggae_test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

**Rappels** :
- TDD strict : Red → Green → Refactor
- 70% unit, 20% integration, 10% E2E
- Coverage > 80%
- Tests = documentation vivante
