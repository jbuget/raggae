# SKILLS.md - Compétences techniques requises

## Vue d'ensemble

Ce fichier détaille les compétences et connaissances techniques nécessaires pour développer Raggae selon les standards définis.

## 1. Clean Architecture

### Concepts fondamentaux

**Dependency Rule** : Les dépendances pointent toujours vers l'intérieur (vers le domaine).

```
Presentation → Application → Domain
Infrastructure → Application → Domain
```

### Couche Domain (Cœur métier)

**Responsabilités** :
- Définir les entités métier (business objects)
- Définir les value objects (objets immuables)
- Définir les règles métier (business rules)
- Définir les exceptions métier

**Interdictions** :
- ❌ Dépendre de frameworks (FastAPI, SQLAlchemy)
- ❌ Dépendre de l'infrastructure (DB, API externes)
- ❌ Contenir de la logique technique

**Exemple - Entité User** :
```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class User:
    """
    Entité User du domaine.
    Immuable, contient uniquement la logique métier.
    """
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    is_active: bool
    created_at: datetime
    
    def deactivate(self) -> "User":
        """Désactive l'utilisateur (business rule)."""
        if not self.is_active:
            raise UserAlreadyInactiveError()
        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=False,
            created_at=self.created_at
        )
```

**Exemple - Value Object Email** :
```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Email:
    """Value Object pour email avec validation."""
    value: str
    
    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidEmailError(f"Invalid email: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
```

### Couche Application (Use Cases)

**Responsabilités** :
- Orchestrer le flux métier
- Coordonner les entités du domaine
- Définir les interfaces (ports) pour l'infrastructure
- Gérer les transactions

**Structure d'un Use Case** :
```python
from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

# Interface (Port)
class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...
    async def find_by_email(self, email: str) -> User | None: ...

class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

# Use Case
class RegisterUser:
    """
    Use Case: Enregistrer un nouvel utilisateur.
    """
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
    
    async def execute(
        self,
        email: str,
        password: str,
        full_name: str
    ) -> UserDTO:
        # 1. Vérifier que l'email n'existe pas
        existing = await self._user_repository.find_by_email(email)
        if existing:
            raise UserAlreadyExistsError(email)
        
        # 2. Créer l'entité User
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=self._password_hasher.hash(password),
            full_name=full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # 3. Persister
        await self._user_repository.save(user)
        
        # 4. Retourner DTO
        return UserDTO.from_entity(user)
```

### Couche Infrastructure (Implémentations)

**Responsabilités** :
- Implémenter les interfaces définies par Application
- Gérer la persistence (DB)
- Gérer les services externes (OpenAI, email, etc.)
- Configuration

**Exemple - Repository SQLAlchemy** :
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class SQLAlchemyUserRepository:
    """Implémentation SQLAlchemy du UserRepository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, user: User) -> None:
        # Convertir entité → modèle SQLAlchemy
        model = UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        self._session.add(model)
        await self._session.flush()
    
    async def find_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        # Convertir modèle SQLAlchemy → entité
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            created_at=model.created_at
        )
```

### Couche Presentation (API)

**Responsabilités** :
- Gérer les requêtes HTTP
- Valider les inputs (Pydantic)
- Appeler les use cases
- Formater les réponses

**Exemple - Endpoint FastAPI** :
```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case)
) -> UserResponse:
    try:
        user_dto = await use_case.execute(
            email=data.email,
            password=data.password,
            full_name=data.full_name
        )
        return UserResponse.from_dto(user_dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
```

## 2. Test-Driven Development (TDD)

### Cycle Red-Green-Refactor

```
1. RED    → Écrire un test qui échoue
2. GREEN  → Écrire le code minimum pour passer
3. REFACTOR → Améliorer sans casser
```

### Tests unitaires (Domain + Application)

**Caractéristiques** :
- Rapides (< 1ms par test)
- Isolés (pas de DB, pas de réseau)
- Déterministes

**Exemple - Test entité** :
```python
import pytest
from uuid import uuid4
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserAlreadyInactiveError

class TestUser:
    def test_create_user_with_valid_data(self):
        # Given
        user_id = uuid4()
        email = "test@example.com"
        
        # When
        user = User(
            id=user_id,
            email=email,
            hashed_password="hashed",
            full_name="Test User",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Then
        assert user.id == user_id
        assert user.email == email
        assert user.is_active is True
    
    def test_deactivate_active_user(self):
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Test",
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # When
        deactivated = user.deactivate()
        
        # Then
        assert deactivated.is_active is False
    
    def test_deactivate_inactive_user_raises_error(self):
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Test",
            is_active=False,
            created_at=datetime.utcnow()
        )
        
        # When / Then
        with pytest.raises(UserAlreadyInactiveError):
            user.deactivate()
```

**Exemple - Test use case** :
```python
import pytest
from unittest.mock import AsyncMock
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.domain.exceptions.user_exceptions import UserAlreadyExistsError

class TestRegisterUser:
    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_password_hasher(self):
        hasher = AsyncMock()
        hasher.hash.return_value = "hashed_password"
        return hasher
    
    @pytest.fixture
    def use_case(self, mock_user_repository, mock_password_hasher):
        return RegisterUser(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher
        )
    
    async def test_register_user_success(
        self,
        use_case,
        mock_user_repository,
        mock_password_hasher
    ):
        # Given
        mock_user_repository.find_by_email.return_value = None
        
        # When
        result = await use_case.execute(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User"
        )
        
        # Then
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        mock_password_hasher.hash.assert_called_once_with("SecurePass123!")
        mock_user_repository.save.assert_called_once()
    
    async def test_register_user_email_already_exists(
        self,
        use_case,
        mock_user_repository
    ):
        # Given
        existing_user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hash",
            full_name="Existing",
            is_active=True,
            created_at=datetime.utcnow()
        )
        mock_user_repository.find_by_email.return_value = existing_user
        
        # When / Then
        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(
                email="test@example.com",
                password="pass",
                full_name="Test"
            )
```

### Tests d'intégration (Infrastructure)

**Caractéristiques** :
- Testent les implémentations réelles
- Utilisent une vraie DB (testcontainers ou DB dédiée)
- Plus lents (< 100ms par test)

**Exemple - Test repository** :
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository
)

@pytest.fixture
async def db_session():
    # Setup
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
    
    # Teardown
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

class TestSQLAlchemyUserRepository:
    async def test_save_and_find_user(self, db_session):
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
        
        found = await repo.find_by_email("test@example.com")
        
        # Then
        assert found is not None
        assert found.id == user.id
        assert found.email == user.email
```

### Tests E2E (API)

**Caractéristiques** :
- Testent l'application complète
- Simulent un client HTTP réel
- Les plus lents (< 500ms par test)

**Exemple - Test API** :
```python
import pytest
from httpx import AsyncClient
from raggae.presentation.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestAuthEndpoints:
    async def test_register_user_success(self, client):
        # When
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePass123!",
                "full_name": "Test User"
            }
        )
        
        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "password" not in data
    
    async def test_register_user_duplicate_email(self, client):
        # Given - premier utilisateur
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Pass123!",
                "full_name": "First"
            }
        )
        
        # When - tentative de duplication
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "Pass456!",
                "full_name": "Second"
            }
        )
        
        # Then
        assert response.status_code == 409
```

## 3. Python avancé pour Clean Architecture

### Type Hints stricts

```python
from typing import Protocol, TypeVar, Generic
from collections.abc import Sequence

T = TypeVar("T")

class Repository(Protocol[T]):
    async def save(self, entity: T) -> None: ...
    async def find_by_id(self, id: UUID) -> T | None: ...
    async def find_all(self) -> Sequence[T]: ...
```

### Dataclasses immuables

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)  # Immuable
class Project:
    id: UUID
    name: str
    description: str
    
    def with_name(self, new_name: str) -> "Project":
        """Retourne une nouvelle instance avec un nom modifié."""
        return replace(self, name=new_name)
```

### Dependency Injection

```python
from typing import Callable
from fastapi import Depends

# Factory
def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(session)

def get_register_user_use_case(
    repo: UserRepository = Depends(get_user_repository),
    hasher: PasswordHasher = Depends(get_password_hasher)
) -> RegisterUser:
    return RegisterUser(repo, hasher)

# Endpoint
@router.post("/register")
async def register(
    data: RegisterRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case)
):
    return await use_case.execute(...)
```

## 4. SQLAlchemy 2.0 Async

### Modèles

```python
from sqlalchemy import String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID, uuid4

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### Requêtes async

```python
from sqlalchemy import select, update, delete

# Select
stmt = select(UserModel).where(UserModel.email == "test@example.com")
result = await session.execute(stmt)
user = result.scalar_one_or_none()

# Insert
session.add(user_model)
await session.flush()

# Update
stmt = (
    update(UserModel)
    .where(UserModel.id == user_id)
    .values(full_name="New Name")
)
await session.execute(stmt)

# Delete
stmt = delete(UserModel).where(UserModel.id == user_id)
await session.execute(stmt)
```

## 5. Alembic

### Créer une migration

```bash
# Auto-générer depuis les modèles
alembic revision --autogenerate -m "create users table"

# Migration manuelle
alembic revision -m "add index on email"
```

### Migration fichier

```python
# alembic/versions/xxx_create_users_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('idx_users_email')
    op.drop_table('users')
```

## 6. FastAPI avancé

### Gestion des erreurs

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

# Exception handler global
@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )
```

### Streaming responses (pour chat)

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(
    message: str,
    use_case: SendMessage = Depends(...)
):
    async def generate():
        async for chunk in use_case.execute_stream(message):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## 7. Pytest avancé

### Fixtures

```python
# conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def in_memory_user_repository():
    return InMemoryUserRepository()

@pytest.fixture(autouse=True)
async def reset_database(db_session):
    """Reset DB avant chaque test."""
    await db_session.execute("TRUNCATE users CASCADE")
    await db_session.commit()
```

### Parametrize

```python
@pytest.mark.parametrize("email,expected_valid", [
    ("valid@example.com", True),
    ("invalid", False),
    ("no@domain", False),
    ("@nodomain.com", False),
])
def test_email_validation(email, expected_valid):
    if expected_valid:
        Email(email)  # Ne doit pas raise
    else:
        with pytest.raises(InvalidEmailError):
            Email(email)
```

### Async tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected
```

## 8. Outils de qualité

### Ruff (linting + formatting)

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
```

### Mypy (type checking)

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

## 9. Patterns utiles

### Repository Pattern

```python
# Interface
class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...
    async def find_by_id(self, id: UUID) -> User | None: ...

# In-memory (pour tests)
class InMemoryUserRepository:
    def __init__(self):
        self._users: dict[UUID, User] = {}
    
    async def save(self, user: User) -> None:
        self._users[user.id] = user
    
    async def find_by_id(self, id: UUID) -> User | None:
        return self._users.get(id)
```

### Unit of Work Pattern

```python
class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
```

---

**Points clés** :
- Clean Architecture = séparation stricte des couches
- TDD = Red → Green → Refactor
- Tests = 70% unit, 20% integration, 10% E2E
- Type hints partout
- Async/await pour I/O
