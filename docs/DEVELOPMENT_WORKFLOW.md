# DEVELOPMENT_WORKFLOW.md - Workflow de développement

## Vue d'ensemble

Ce document décrit le workflow quotidien pour développer Raggae en TDD, Clean Architecture et baby steps.

## Découpage validé Sprint 4 (Documents)

Avant de coder, appliquer ce découpage en tâches atomiques :

- [ ] Domain: ajouter l'entité `Document`
- [ ] Domain: ajouter exceptions (`InvalidDocumentTypeError`, `DocumentTooLargeError`, `DocumentNotFoundError`)
- [ ] Application: définir le port `DocumentRepository`
- [ ] Application: définir le port `FileStorageService`
- [ ] Application: implémenter `UploadDocument` (sans processing/indexing)
- [ ] Application: implémenter `ListProjectDocuments`
- [ ] Application: implémenter `DeleteDocument`
- [ ] Infrastructure: repository in-memory document
- [ ] Infrastructure: adapter S3-compatible (MinIO local)
- [ ] Presentation: endpoint `POST /projects/{project_id}/documents`
- [ ] Presentation: endpoint `GET /projects/{project_id}/documents`
- [ ] Presentation: endpoint `DELETE /projects/{project_id}/documents/{document_id}`
- [ ] Tests E2E: upload/list/delete + sécurité ownership

Contraintes Sprint 4A :
- formats autorisés : `txt`, `md`, `pdf`, `doc`, `docx`
- taille max : `100 Mo`
- binaire stocké en S3-compatible (MinIO)
- aucun chunking/embedding/indexing dans cette phase

## Découpage validé Sprint 4C (Chunking adaptatif)

Avant de coder, appliquer ce découpage en tâches atomiques :

- [ ] Application: ajouter le port `DocumentStructureAnalyzer`
- [ ] Application: ajouter `ChunkingStrategySelector` (règles simples, déterministes)
- [ ] Domain/Application: définir un enum/VO `ChunkingStrategy` (`fixed_window`, `paragraph`, `heading_section`)
- [ ] Infrastructure: implémenter `HeuristicDocumentStructureAnalyzer`
- [ ] Infrastructure: implémenter `ParagraphTextChunkerService`
- [ ] Infrastructure: implémenter `HeadingSectionTextChunkerService`
- [ ] Infrastructure: conserver `SimpleTextChunkerService` comme fallback `fixed_window`
- [ ] Application: intégrer selector + routeur de stratégie dans le pipeline upload processing
- [ ] Tests unitaires: selector + analyzer + chunkers par stratégie
- [ ] Tests d'intégration: vérifier la stratégie choisie sur documents représentatifs

Contraintes Sprint 4C :
- priorité à la robustesse déterministe (pas de LLM dans la sélection de stratégie)
- fallback systématique vers `fixed_window` en cas d'ambiguïté
- aucun couplage direct de la couche Application à une lib de parsing spécifique

## Découpage validé Sprint 4D (Metadata JSON sur chunks)

Avant de coder, appliquer ce découpage en tâches atomiques :

- [ ] Domain: ajouter `metadata_json` sur `DocumentChunk`
- [ ] Infrastructure DB: ajouter colonne `metadata_json` (`JSONB`) sur `document_chunks`
- [ ] Alembic: migration dédiée non destructive (`nullable=True`)
- [ ] Repositories: mapper `metadata_json` (save/find)
- [ ] Application: enrichir `UploadDocument` pour renseigner le noyau metadata minimal
- [ ] DTO/API: exposer `metadata_json` dans le listing des chunks
- [ ] Tests unitaires: use case + mapping DTO/schema
- [ ] Tests d'intégration: repository SQLAlchemy (persist/load JSON)
- [ ] Tests E2E: endpoint chunks retourne `metadata_json`

Contraintes Sprint 4D :
- metadata flexible mais avec noyau commun obligatoire (`metadata_version`, `processing_strategy`, `source_type`)
- backward compatible (chunks historiques sans metadata acceptés)
- pas de logique métier domaine spécifique codée en dur dans la couche Domain

## Cycle de développement

### 1. Choisir une fonctionnalité

**Décomposition en tâches atomiques** :

Exemple : Feature "Créer un projet"
- [ ] Entité Project (Domain)
- [ ] Value Object ProjectName (Domain)
- [ ] Exception ProjectAlreadyExistsError (Domain)
- [ ] Use Case CreateProject (Application)
- [ ] Interface ProjectRepository (Application)
- [ ] DTO ProjectDTO (Application)
- [ ] SQLAlchemy ProjectModel (Infrastructure)
- [ ] SQLAlchemy ProjectRepository (Infrastructure)
- [ ] Migration Alembic (Infrastructure)
- [ ] Endpoint POST /projects (Presentation)
- [ ] Schema CreateProjectRequest (Presentation)
- [ ] Tests E2E (Tests)

### 2. TDD Red-Green-Refactor

Pour chaque tâche atomique :

#### Phase RED (Test qui échoue)

```bash
# 1. Créer le fichier de test
touch tests/unit/domain/entities/test_project.py

# 2. Écrire le test
# tests/unit/domain/entities/test_project.py
```

```python
import pytest
from uuid import uuid4
from datetime import datetime
from raggae.domain.entities.project import Project

class TestProject:
    def test_create_project_with_valid_data(self):
        # Given
        project_id = uuid4()
        user_id = uuid4()
        
        # When
        project = Project(
            id=project_id,
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
            is_published=False,
            created_at=datetime.utcnow()
        )
        
        # Then
        assert project.id == project_id
        assert project.name == "My Project"
        assert project.is_published is False
```

```bash
# 3. Lancer le test (doit échouer)
pytest tests/unit/domain/entities/test_project.py -v

# Output attendu:
# ModuleNotFoundError: No module named 'raggae.domain.entities.project'
```

#### Phase GREEN (Code minimum)

```bash
# 1. Créer le fichier source
mkdir -p src/raggae/domain/entities
touch src/raggae/domain/entities/__init__.py
touch src/raggae/domain/entities/project.py
```

```python
# src/raggae/domain/entities/project.py
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass(frozen=True)
class Project:
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
```

```bash
# 2. Relancer le test (doit passer)
pytest tests/unit/domain/entities/test_project.py -v

# Output attendu:
# test_create_project_with_valid_data PASSED
```

#### Phase REFACTOR (Amélioration)

```python
# Si nécessaire, améliorer le code sans casser les tests
# Exemple: ajouter validation

@dataclass(frozen=True)
class Project:
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Project name cannot be empty")
        if len(self.name) > 255:
            raise ValueError("Project name too long")
```

```bash
# Relancer TOUS les tests
pytest tests/unit/domain/entities/test_project.py -v
```

#### Commit

```bash
# Formater le code
ruff format src/ tests/

# Vérifier le linting
ruff check src/ tests/

# Type checking
mypy src/

# Tous les tests passent
pytest

# Commit (Conventional Commits)
git add src/raggae/domain/entities/project.py
git add tests/unit/domain/entities/test_project.py
git commit -m "feat(domain): add project entity"
```

### 3. Itérer

Répéter Red-Green-Refactor pour chaque comportement de l'entité.

**Exemple : Ajouter méthode publish()**

#### RED
```python
# tests/unit/domain/entities/test_project.py
def test_publish_unpublished_project(self):
    # Given
    project = Project(
        id=uuid4(),
        user_id=uuid4(),
        name="Test",
        description="",
        system_prompt="prompt",
        is_published=False,
        created_at=datetime.utcnow()
    )
    
    # When
    published = project.publish()
    
    # Then
    assert published.is_published is True
    assert published.id == project.id  # Même identité
```

#### GREEN
```python
# src/raggae/domain/entities/project.py
from dataclasses import replace

@dataclass(frozen=True)
class Project:
    # ... existing fields
    
    def publish(self) -> "Project":
        """Publie le projet."""
        return replace(self, is_published=True)
```

#### REFACTOR
```python
# Ajouter validation métier
def publish(self) -> "Project":
    """Publie le projet."""
    if self.is_published:
        raise ProjectAlreadyPublishedError()
    return replace(self, is_published=True)
```

#### Commit
```bash
git add src/raggae/domain/entities/project.py
git add tests/unit/domain/entities/test_project.py
git commit -m "feat(domain): add publish method to project entity"
```

## Workflow par couche

### Domain Layer

**Tests** : 100% unitaires, ultra-rapides

```bash
# Structure
tests/unit/domain/
├── entities/
│   ├── test_user.py
│   ├── test_project.py
│   └── test_document.py
└── value_objects/
    ├── test_email.py
    └── test_password.py
```

**Exemple complet - Value Object Email** :

#### 1. RED
```python
# tests/unit/domain/value_objects/test_email.py
import pytest
from raggae.domain.value_objects.email import Email
from raggae.domain.exceptions.validation_errors import InvalidEmailError

class TestEmail:
    def test_create_email_with_valid_format(self):
        # When
        email = Email("valid@example.com")
        
        # Then
        assert email.value == "valid@example.com"
    
    @pytest.mark.parametrize("invalid_email", [
        "not-an-email",
        "@example.com",
        "user@",
        "user @example.com",
        "",
    ])
    def test_create_email_with_invalid_format_raises_error(self, invalid_email):
        # When / Then
        with pytest.raises(InvalidEmailError):
            Email(invalid_email)
```

```bash
pytest tests/unit/domain/value_objects/test_email.py -v
# FAIL: ModuleNotFoundError
```

#### 2. GREEN
```python
# src/raggae/domain/value_objects/email.py
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self._is_valid(self.value):
            from raggae.domain.exceptions.validation_errors import InvalidEmailError
            raise InvalidEmailError(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
```

```python
# src/raggae/domain/exceptions/validation_errors.py
class InvalidEmailError(ValueError):
    pass
```

```bash
pytest tests/unit/domain/value_objects/test_email.py -v
# PASS
```

#### 3. COMMIT
```bash
git add src/raggae/domain/value_objects/email.py
git add src/raggae/domain/exceptions/validation_errors.py
git add tests/unit/domain/value_objects/test_email.py
git commit -m "feat(domain): add email value object with validation"
```

### Application Layer (Use Cases)

**Tests** : Unitaires avec mocks

```bash
# Structure
tests/unit/application/use_cases/
├── user/
│   ├── test_register_user.py
│   └── test_login_user.py
└── project/
    ├── test_create_project.py
    └── test_publish_project.py
```

**Exemple complet - Use Case CreateProject** :

#### 1. RED
```python
# tests/unit/application/use_cases/project/test_create_project.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from raggae.application.use_cases.project.create_project import (
    CreateProject,
    CreateProjectCommand
)
from raggae.domain.entities.user import User
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.not_found_errors import UserNotFoundError

class TestCreateProject:
    @pytest.fixture
    def mock_project_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, mock_project_repository, mock_user_repository):
        return CreateProject(
            project_repository=mock_project_repository,
            user_repository=mock_user_repository
        )
    
    async def test_create_project_success(
        self,
        use_case,
        mock_user_repository,
        mock_project_repository
    ):
        # Given
        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@example.com",
            hashed_password="hashed",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )
        mock_user_repository.find_by_id.return_value = user
        
        command = CreateProjectCommand(
            user_id=user_id,
            name="My Project",
            description="Description",
            system_prompt="You are helpful"
        )
        
        # When
        result = await use_case.execute(command)
        
        # Then
        assert result.name == "My Project"
        assert result.user_id == user_id
        mock_project_repository.save.assert_called_once()
    
    async def test_create_project_user_not_found(
        self,
        use_case,
        mock_user_repository
    ):
        # Given
        mock_user_repository.find_by_id.return_value = None
        
        command = CreateProjectCommand(
            user_id=uuid4(),
            name="Project",
            description="",
            system_prompt="prompt"
        )
        
        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(command)
```

```bash
pytest tests/unit/application/use_cases/project/test_create_project.py -v
# FAIL
```

#### 2. GREEN
```python
# src/raggae/application/use_cases/project/create_project.py
from dataclasses import dataclass
from uuid import uuid4, UUID
from datetime import datetime

@dataclass
class CreateProjectCommand:
    user_id: UUID
    name: str
    description: str
    system_prompt: str

class CreateProject:
    def __init__(self, project_repository, user_repository):
        self._project_repository = project_repository
        self._user_repository = user_repository
    
    async def execute(self, command: CreateProjectCommand):
        from raggae.domain.exceptions.not_found_errors import UserNotFoundError
        from raggae.domain.entities.project import Project
        from raggae.application.dto.project_dto import ProjectDTO
        
        # Vérifier que l'utilisateur existe
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(f"User {command.user_id} not found")
        
        # Créer le projet
        project = Project(
            id=uuid4(),
            user_id=command.user_id,
            name=command.name,
            description=command.description,
            system_prompt=command.system_prompt,
            is_published=False,
            created_at=datetime.utcnow()
        )
        
        # Sauvegarder
        await self._project_repository.save(project)
        
        # Retourner DTO
        return ProjectDTO.from_entity(project)
```

```python
# src/raggae/application/dto/project_dto.py
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class ProjectDTO:
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    
    @classmethod
    def from_entity(cls, project):
        return cls(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at
        )
```

```bash
pytest tests/unit/application/use_cases/project/test_create_project.py -v
# PASS
```

#### 3. COMMIT
```bash
git add src/raggae/application/use_cases/project/create_project.py
git add src/raggae/application/dto/project_dto.py
git add tests/unit/application/use_cases/project/test_create_project.py
git commit -m "feat(application): add create project use case"
```

### Infrastructure Layer (Repositories)

**Tests** : Intégration avec vraie DB

```bash
# Structure
tests/integration/infrastructure/repositories/
├── test_sqlalchemy_user_repository.py
└── test_sqlalchemy_project_repository.py
```

**Setup DB de test** :

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from raggae.infrastructure.database.models import Base

@pytest.fixture(scope="session")
def database_url():
    return "postgresql+asyncpg://test:test@localhost/raggae_test"

@pytest.fixture
async def engine(database_url):
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
```

**Exemple complet** :

#### 1. RED
```python
# tests/integration/infrastructure/repositories/test_sqlalchemy_project_repository.py
import pytest
from uuid import uuid4
from datetime import datetime
from raggae.domain.entities.project import Project
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository
)

class TestSQLAlchemyProjectRepository:
    async def test_save_and_find_by_id(self, db_session):
        # Given
        repo = SQLAlchemyProjectRepository(db_session)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test Project",
            description="A test",
            system_prompt="Be helpful",
            is_published=False,
            created_at=datetime.utcnow()
        )
        
        # When
        await repo.save(project)
        await db_session.commit()
        
        found = await repo.find_by_id(project.id)
        
        # Then
        assert found is not None
        assert found.id == project.id
        assert found.name == "Test Project"
```

```bash
pytest tests/integration/infrastructure/repositories/test_sqlalchemy_project_repository.py -v
# FAIL
```

#### 2. GREEN

Créer le modèle SQLAlchemy :

```python
# src/raggae/infrastructure/database/models/project_model.py
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime
from raggae.infrastructure.database.models.base import Base

class ProjectModel(Base):
    __tablename__ = "projects"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
```

Créer le repository :

```python
# src/raggae/infrastructure/database/repositories/sqlalchemy_project_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from raggae.domain.entities.project import Project
from raggae.infrastructure.database.models.project_model import ProjectModel

class SQLAlchemyProjectRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, project: Project) -> None:
        model = ProjectModel(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at
        )
        self._session.add(model)
        await self._session.flush()
    
    async def find_by_id(self, project_id: UUID) -> Project | None:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return Project(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            system_prompt=model.system_prompt,
            is_published=model.is_published,
            created_at=model.created_at
        )
```

Créer la migration Alembic :

```bash
alembic revision --autogenerate -m "add projects table"
alembic upgrade head
```

```bash
pytest tests/integration/infrastructure/repositories/test_sqlalchemy_project_repository.py -v
# PASS
```

#### 3. COMMIT
```bash
git add src/raggae/infrastructure/database/models/project_model.py
git add src/raggae/infrastructure/database/repositories/sqlalchemy_project_repository.py
git add alembic/versions/*_add_projects_table.py
git add tests/integration/infrastructure/repositories/test_sqlalchemy_project_repository.py
git commit -m "feat(infrastructure): add project repository and model"
```

### Presentation Layer (API)

**Tests** : E2E avec TestClient

```bash
# Structure
tests/e2e/api/v1/
├── test_auth_endpoints.py
└── test_project_endpoints.py
```

#### 1. RED
```python
# tests/e2e/api/v1/test_project_endpoints.py
import pytest
from httpx import AsyncClient
from raggae.presentation.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def authenticated_client(client):
    # Register et login pour obtenir un token
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client

class TestProjectEndpoints:
    async def test_create_project(self, authenticated_client):
        # When
        response = await authenticated_client.post(
            "/api/v1/projects",
            json={
                "name": "My Project",
                "description": "A test project",
                "system_prompt": "You are a helpful assistant"
            }
        )
        
        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Project"
        assert "id" in data
```

```bash
pytest tests/e2e/api/v1/test_project_endpoints.py -v
# FAIL
```

#### 2. GREEN

Créer l'endpoint :

```python
# src/raggae/presentation/api/v1/endpoints/projects.py
from fastapi import APIRouter, Depends, status
from raggae.presentation.api.v1.schemas.project_schema import (
    CreateProjectRequest,
    ProjectResponse
)
from raggae.application.use_cases.project.create_project import (
    CreateProject,
    CreateProjectCommand
)
from raggae.presentation.api.dependencies import (
    get_current_user,
    get_create_project_use_case
)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectRequest,
    current_user = Depends(get_current_user),
    use_case: CreateProject = Depends(get_create_project_use_case)
) -> ProjectResponse:
    command = CreateProjectCommand(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        system_prompt=data.system_prompt
    )
    project_dto = await use_case.execute(command)
    return ProjectResponse.from_dto(project_dto)
```

Créer les schemas Pydantic :

```python
# src/raggae/presentation/api/v1/schemas/project_schema.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    system_prompt: str = Field(..., min_length=10)

class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    system_prompt: str
    is_published: bool
    created_at: datetime
    
    @classmethod
    def from_dto(cls, dto):
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            system_prompt=dto.system_prompt,
            is_published=dto.is_published,
            created_at=dto.created_at
        )
```

```bash
pytest tests/e2e/api/v1/test_project_endpoints.py -v
# PASS
```

#### 3. COMMIT
```bash
git add src/raggae/presentation/api/v1/endpoints/projects.py
git add src/raggae/presentation/api/v1/schemas/project_schema.py
git add tests/e2e/api/v1/test_project_endpoints.py
git commit -m "feat(api): add create project endpoint"
```

## Commandes quotidiennes

### Avant de commencer à coder

```bash
# Mise à jour
git pull origin main

# Créer une branche (optionnel)
git checkout -b feature/create-project

# Installer les dépendances
pip install -e ".[dev]"

# Vérifier que les tests passent
pytest

# Lancer la DB de dev
docker-compose up -d postgres
```

### Pendant le dev

```bash
# Lancer les tests en continu (watch mode)
pytest-watch

# Ou lancer manuellement
pytest tests/unit  # Rapide
pytest tests/integration  # Moyen
pytest tests/e2e  # Lent
pytest  # Tout

# Coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Linting
ruff check src/ tests/
ruff format src/ tests/

# Type checking
mypy src/
```

### Avant chaque commit

```bash
# Checklist automatique
./scripts/pre-commit-check.sh
```

```bash
# scripts/pre-commit-check.sh
#!/bin/bash
set -e

echo "🧪 Running tests..."
pytest

echo "🎨 Formatting code..."
ruff format src/ tests/

echo "🔍 Linting..."
ruff check src/ tests/

echo "🏷️  Type checking..."
mypy src/

echo "✅ All checks passed!"
```

### Après un commit

```bash
# Push
git push origin feature/create-project

# Ou si c'est main
git push origin main
```

## Organisation des sessions de dev

### Session type (2-3h)

**9h00 - 9h15 : Setup**
- Pull latest
- Vérifier les tests passent
- Choisir la prochaine tâche

**9h15 - 11h00 : TDD Red-Green-Refactor**
- Écrire 1 test
- Implémenter
- Refactor
- Commit
- Répéter 5-10 fois

**11h00 - 11h15 : Review & Cleanup**
- Relire les commits
- Vérifier la coverage
- Push

### Metrics de productivité

**Objectifs quotidiens** :
- 10-20 commits (baby steps)
- Coverage > 80%
- 0 erreur mypy
- 0 erreur ruff

**Red flags** :
- Commits > 200 lignes
- Tests qui échouent en CI
- Coverage qui baisse
- Code non formaté

## Debugging

### Tests qui échouent

```bash
# Mode verbose + output
pytest -vv -s

# Stopper au premier échec
pytest -x

# Lancer un test spécifique
pytest tests/unit/domain/entities/test_user.py::TestUser::test_create_user

# PDB au premier échec
pytest --pdb
```

### DB issues

```bash
# Reset DB
docker-compose down -v
docker-compose up -d postgres

# Recréer les tables
alembic downgrade base
alembic upgrade head

# Vérifier les migrations
alembic history
alembic current
```

### Type errors

```bash
# Mode strict
mypy --strict src/

# Ignorer un fichier
mypy --exclude 'src/raggae/infrastructure' src/
```

## Résolution de problèmes courants

### "Import error" dans les tests

```python
# Mauvais
from raggae.domain.entities import User

# Bon
from raggae.domain.entities.user import User
```

### "Circular import"

```python
# Utiliser TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raggae.domain.entities.project import Project

class User:
    projects: list["Project"]  # Forward reference
```

### "AsyncMock not working"

```python
# Python 3.8+
from unittest.mock import AsyncMock

# Sinon
from asyncmock import AsyncMock
```

---

**Rappels importants** :
- RED → GREEN → REFACTOR (toujours)
- Un commit = un changement atomique
- Tests avant code (TDD strict)
- Baby steps (petits changements)
- Conventional Commits
