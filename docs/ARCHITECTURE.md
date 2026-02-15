# ARCHITECTURE.md - Décisions architecturales

## Vue d'ensemble

Raggae est développé selon les principes de **Clean Architecture** avec une séparation stricte entre les couches métier, application et infrastructure.

## Principes directeurs

### 1. Dependency Rule

Les dépendances pointent toujours vers l'intérieur (vers le domaine) :

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│      (API, Controllers, Schemas)        │
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│       Infrastructure Layer              │
│  (Repositories, Services, Database)     │
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│        Application Layer                │
│   (Use Cases, Interfaces/Ports, DTOs)   │
└──────────────┬──────────────────────────┘
               │ depends on
               ▼
┌─────────────────────────────────────────┐
│          Domain Layer                   │
│  (Entities, Value Objects, Exceptions)  │
│           NO DEPENDENCIES               │
└─────────────────────────────────────────┘
```

**Règle absolue** : Une couche externe peut dépendre d'une couche interne, mais JAMAIS l'inverse.

### 2. Séparation des préoccupations

Chaque couche a une responsabilité unique et bien définie :

| Couche | Responsabilité | Interdit |
|--------|---------------|----------|
| **Domain** | Logique métier pure | Dépendances externes, I/O, frameworks |
| **Application** | Orchestration, use cases | Détails techniques, DB, API |
| **Infrastructure** | Implémentation technique | Logique métier |
| **Presentation** | Interface utilisateur (API) | Logique métier directe |

### 3. Inversion de dépendances

L'infrastructure implémente les interfaces définies par l'application :

```python
# Application définit l'interface (Port)
class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

# Infrastructure implémente (Adapter)
class SQLAlchemyUserRepository:
    async def save(self, user: User) -> None:
        # Implementation...
```

## Architecture détaillée par couche

### Domain Layer

**Localisation** : `src/raggae/domain/`

**Composants** :
- **Entities** : Objets métier avec identité (User, Project, Document)
- **Value Objects** : Objets immuables sans identité (Email, Password, Embedding)
- **Exceptions** : Erreurs métier (UserNotFoundError, InvalidEmailError)

**Caractéristiques** :
- Aucune dépendance externe
- Entités immuables (frozen dataclasses)
- Logique métier pure (validations, règles)

**Exemple** :
```python
# src/raggae/domain/entities/project.py
from dataclasses import dataclass, replace
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
    
    def publish(self) -> "Project":
        """Publie le projet (business rule)."""
        if self.is_published:
            raise ProjectAlreadyPublishedError()
        return replace(self, is_published=True, published_at=datetime.utcnow())
    
    def update_prompt(self, new_prompt: str) -> "Project":
        """Met à jour le prompt système."""
        if not new_prompt.strip():
            raise EmptyPromptError()
        return replace(self, system_prompt=new_prompt)
```

### Application Layer

**Localisation** : `src/raggae/application/`

**Composants** :
- **Use Cases** : Actions métier (RegisterUser, CreateProject, SendMessage)
- **Interfaces (Ports)** : Contrats pour l'infrastructure
- **DTOs** : Objets de transfert de données
- **Exceptions** : Erreurs applicatives

**Caractéristiques** :
- Orchestre les entités du domaine
- Définit les interfaces (pas les implémentations)
- Indépendant du framework web ou de la DB

**Structure d'un Use Case** :
```python
# src/raggae/application/use_cases/project/create_project.py
from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime

@dataclass
class CreateProjectCommand:
    user_id: UUID
    name: str
    description: str
    system_prompt: str

class CreateProject:
    """Use Case: Créer un nouveau projet."""
    
    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository
    ):
        self._project_repository = project_repository
        self._user_repository = user_repository
    
    async def execute(self, command: CreateProjectCommand) -> ProjectDTO:
        # 1. Vérifier que l'utilisateur existe
        user = await self._user_repository.find_by_id(command.user_id)
        if not user:
            raise UserNotFoundError(command.user_id)
        
        # 2. Créer l'entité Project
        project = Project(
            id=uuid4(),
            user_id=command.user_id,
            name=command.name,
            description=command.description,
            system_prompt=command.system_prompt,
            is_published=False,
            created_at=datetime.utcnow()
        )
        
        # 3. Persister
        await self._project_repository.save(project)
        
        # 4. Retourner DTO
        return ProjectDTO.from_entity(project)
```

**Interfaces (Ports)** :
```python
# src/raggae/application/interfaces/repositories/project_repository.py
from typing import Protocol
from uuid import UUID

class ProjectRepository(Protocol):
    """Interface pour la persistence des projets."""
    
    async def save(self, project: Project) -> None:
        """Sauvegarde un projet."""
        ...
    
    async def find_by_id(self, project_id: UUID) -> Project | None:
        """Trouve un projet par son ID."""
        ...
    
    async def find_by_user_id(self, user_id: UUID) -> list[Project]:
        """Trouve tous les projets d'un utilisateur."""
        ...
    
    async def delete(self, project_id: UUID) -> None:
        """Supprime un projet."""
        ...
```

### Infrastructure Layer

**Localisation** : `src/raggae/infrastructure/`

**Composants** :
- **Database** : SQLAlchemy models, repositories
- **Services** : OpenAI, password hashing, JWT
- **Config** : Settings, environment

**Caractéristiques** :
- Implémente les interfaces de l'Application
- Gère les détails techniques (DB, API externes)
- Convertit entre modèles DB et entités domaine

**Repository Implementation** :
```python
# src/raggae/infrastructure/database/repositories/sqlalchemy_project_repository.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

class SQLAlchemyProjectRepository:
    """Implémentation SQLAlchemy du ProjectRepository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, project: Project) -> None:
        # Conversion entité → modèle
        model = ProjectModel.from_entity(project)
        self._session.add(model)
        await self._session.flush()
    
    async def find_by_id(self, project_id: UUID) -> Project | None:
        stmt = select(ProjectModel).where(ProjectModel.id == project_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        # Conversion modèle → entité
        return model.to_entity()
    
    async def find_by_user_id(self, user_id: UUID) -> list[Project]:
        stmt = select(ProjectModel).where(ProjectModel.user_id == user_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        return [model.to_entity() for model in models]
    
    async def delete(self, project_id: UUID) -> None:
        stmt = delete(ProjectModel).where(ProjectModel.id == project_id)
        await self._session.execute(stmt)
```

**SQLAlchemy Model** :
```python
# src/raggae/infrastructure/database/models/project_model.py
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID
from datetime import datetime

class ProjectModel(Base):
    __tablename__ = "projects"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    
    # Relation
    user: Mapped["UserModel"] = relationship(back_populates="projects")
    
    @classmethod
    def from_entity(cls, project: Project) -> "ProjectModel":
        """Convertit une entité en modèle."""
        return cls(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at
        )
    
    def to_entity(self) -> Project:
        """Convertit le modèle en entité."""
        return Project(
            id=self.id,
            user_id=self.user_id,
            name=self.name,
            description=self.description,
            system_prompt=self.system_prompt,
            is_published=self.is_published,
            created_at=self.created_at
        )
```

### Presentation Layer

**Localisation** : `src/raggae/presentation/`

**Composants** :
- **API Endpoints** : Routes FastAPI
- **Schemas** : Pydantic models pour validation
- **Dependencies** : Injection de dépendances

**Caractéristiques** :
- Valide les inputs (Pydantic)
- Appelle les use cases
- Formate les réponses
- Gère les erreurs HTTP

**Endpoint** :
```python
# src/raggae/presentation/api/v1/endpoints/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateProject = Depends(get_create_project_use_case)
) -> ProjectResponse:
    """Crée un nouveau projet."""
    try:
        command = CreateProjectCommand(
            user_id=current_user.id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt
        )
        project_dto = await use_case.execute(command)
        return ProjectResponse.from_dto(project_dto)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    use_case: GetProject = Depends(get_get_project_use_case)
) -> ProjectResponse:
    """Récupère un projet par son ID."""
    project_dto = await use_case.execute(project_id, current_user.id)
    if not project_dto:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.from_dto(project_dto)
```

**Pydantic Schemas** :
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
    def from_dto(cls, dto: ProjectDTO) -> "ProjectResponse":
        return cls(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            system_prompt=dto.system_prompt,
            is_published=dto.is_published,
            created_at=dto.created_at
        )
```

## Flux de données

### Exemple : Créer un projet

```
1. Client HTTP
   POST /api/v1/projects
   { "name": "Mon Projet", "system_prompt": "..." }
        ↓
2. Presentation Layer (API)
   - Validation Pydantic (CreateProjectRequest)
   - Authentication (get_current_user)
   - Injection use case (get_create_project_use_case)
        ↓
3. Application Layer (Use Case)
   - Création command (CreateProjectCommand)
   - Vérification user existe
   - Création entité Project (Domain)
   - Appel repository.save()
        ↓
4. Infrastructure Layer (Repository)
   - Conversion entité → modèle SQLAlchemy
   - INSERT en DB
        ↓
5. Application Layer (Use Case)
   - Conversion entité → DTO
   - Retour DTO
        ↓
6. Presentation Layer (API)
   - Conversion DTO → Response schema
   - Retour JSON au client
```

## Patterns utilisés

### Repository Pattern

**Objectif** : Abstraire la persistence des données.

```python
# Interface (Application)
class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...
    async def find_by_id(self, id: UUID) -> User | None: ...

# Implémentation (Infrastructure)
class SQLAlchemyUserRepository:
    # Implémente l'interface
    pass

# Implémentation test (Infrastructure)
class InMemoryUserRepository:
    # Implémente l'interface
    pass
```

**Avantages** :
- Tests faciles (in-memory repository)
- Changement de DB transparent
- Isolation de la logique métier

### Dependency Injection

**Objectif** : Découpler les composants.

```python
# dependencies.py
from fastapi import Depends

def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session

def get_user_repository(
    session: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return SQLAlchemyUserRepository(session)

def get_create_project_use_case(
    project_repo: ProjectRepository = Depends(get_project_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> CreateProject:
    return CreateProject(project_repo, user_repo)

# endpoint.py
@router.post("/projects")
async def create(
    data: CreateProjectRequest,
    use_case: CreateProject = Depends(get_create_project_use_case)
):
    return await use_case.execute(...)
```

### DTO Pattern

**Objectif** : Séparer les données internes des données exposées.

```python
# Domain Entity (interne)
@dataclass(frozen=True)
class User:
    id: UUID
    email: str
    hashed_password: str  # Sensible, ne doit pas sortir
    full_name: str

# Application DTO (transfert entre couches)
@dataclass
class UserDTO:
    id: UUID
    email: str
    full_name: str
    
    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name
        )

# Presentation Response (API)
class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
```

### Command Pattern

**Objectif** : Encapsuler les paramètres d'un use case.

```python
@dataclass
class CreateProjectCommand:
    user_id: UUID
    name: str
    description: str
    system_prompt: str

class CreateProject:
    async def execute(self, command: CreateProjectCommand) -> ProjectDTO:
        # ...
```

## Gestion des erreurs

### Hiérarchie d'exceptions

```
ApplicationError (base)
├── ValidationError
│   ├── InvalidEmailError
│   ├── WeakPasswordError
│   └── EmptyPromptError
├── NotFoundError
│   ├── UserNotFoundError
│   └── ProjectNotFoundError
├── ConflictError
│   ├── UserAlreadyExistsError
│   └── ProjectAlreadyPublishedError
└── UnauthorizedError
    ├── InvalidCredentialsError
    └── InsufficientPermissionsError
```

### Mapping erreurs → HTTP status

```python
# presentation/api/error_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

## Décisions techniques clés

### Pourquoi Clean Architecture ?

✅ **Avantages** :
- Testabilité maximale (logique métier isolée)
- Indépendance des frameworks
- Changement de DB/API facile
- Code maintenable à long terme

❌ **Inconvénients** :
- Plus de code (boilerplate)
- Courbe d'apprentissage
- Over-engineering pour petits projets

**Décision** : Adopté car Raggae est un projet complexe (RAG, embeddings, chat) qui bénéficiera de l'isolation.

### Pourquoi SQLAlchemy 2.0 async ?

✅ **Avantages** :
- Performance (async I/O)
- Type hints natifs
- ORM moderne

**Décision** : Async obligatoire pour scalabilité (RAG = beaucoup d'I/O).

### Pourquoi pgvector ?

✅ **Avantages** :
- Extension PostgreSQL native
- Pas besoin de DB séparée (Pinecone, Weaviate)
- Simplicité architecture

**Décision** : Simplicité > performance pour MVP.

### Pourquoi FastAPI ?

✅ **Avantages** :
- Async natif
- Validation Pydantic
- OpenAPI auto-généré
- Dependency Injection

**Décision** : Standard Python moderne pour APIs.

## Anti-patterns à éviter

### ❌ Domain dépend d'Infrastructure

```python
# MAUVAIS
from raggae.infrastructure.database.models import UserModel

class User:
    def save_to_db(self):
        UserModel.create(...)  # ❌ Couplage à la DB
```

### ❌ Use Case fait de l'I/O direct

```python
# MAUVAIS
class RegisterUser:
    async def execute(self, email, password):
        # ❌ Accès direct à la DB
        await db.execute("INSERT INTO users ...")
```

### ❌ Entité mutable

```python
# MAUVAIS
class User:
    def __init__(self):
        self.email = ""  # ❌ Mutable
    
    def change_email(self, new_email):
        self.email = new_email  # ❌ Mutation
```

### ❌ Repository retourne des modèles DB

```python
# MAUVAIS
class UserRepository:
    async def find(self, id) -> UserModel:  # ❌ Doit retourner User (entité)
        return await session.get(UserModel, id)
```

## Références

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [DDD (Domain-Driven Design)](https://martinfowler.com/bliki/DomainDrivenDesign.html)

## Décisions Sprint 4 (Documents)

### Scope MVP (Sprint 4A)

- Objectif immédiat : attacher des documents à un projet.
- Aucun chunking, embedding, indexing dans cette première étape.
- Formats acceptés : `txt`, `md`, `pdf`, `doc`, `docx`.
- Taille maximale d'un fichier : `100 Mo`.
- Stockage binaire : S3-compatible (MinIO en local via Docker Compose).

### Modèle de données cible

- `Document` (Domain Entity) rattaché à `Project` par `project_id`.
- `DocumentChunk` sera introduit ensuite pour l'indexation.
- Les embeddings seront stockés dans PostgreSQL via `pgvector` (phase ultérieure).

### Ports applicatifs (contrats)

- `DocumentRepository` : persistance des métadonnées documentaires.
- `FileStorageService` : upload/download/delete dans storage objet S3-compatible.
- `ProjectRepository` : vérification ownership projet (déjà en place).

### Use cases Sprint 4A

- `UploadDocument` :
  - vérifie l'existence du projet et l'ownership utilisateur ;
  - valide extension et taille ;
  - upload le fichier vers S3-compatible ;
  - persiste les métadonnées du document.
- `ListProjectDocuments` : liste les documents d'un projet (ownership check).
- `DeleteDocument` :
  - ownership check ;
  - suppression du binaire S3-compatible ;
  - suppression metadata document (et chunks associés quand ils existeront).

### API Sprint 4A

- `POST /api/v1/projects/{project_id}/documents` (`multipart/form-data`)
- `GET /api/v1/projects/{project_id}/documents`
- `DELETE /api/v1/projects/{project_id}/documents/{document_id}`

### Sécurité

- Toutes les routes documents sont protégées par `access_token`.
- Règle stricte : un utilisateur ne peut manipuler que les documents de ses propres projets.

### Évolution prévue (Sprint 4B)

- Traitement synchrone à l'upload pour `chunking + embeddings` au départ.
- Préparer un toggle de configuration pour mode asynchrone plus tard (variable d'environnement).

### Évolution prévue (Sprint 4C)

- Objectif : sélectionner automatiquement la meilleure stratégie de chunking selon la structure du document extrait.
- Design recommandé :
  - `DocumentStructureAnalyzer` (port application) :
    - détecte des signaux simples et déterministes (densité de sauts de ligne, présence de titres, listes, tables, longueur moyenne de paragraphes).
  - `ChunkingStrategySelector` (application) :
    - convertit l'analyse en stratégie (`fixed_window`, `paragraph`, `heading_section`).
  - `TextChunkerService` devient une façade de stratégies :
    - route vers l'implémentation appropriée.
- Contrainte Clean Architecture :
  - la logique de sélection reste en Application ;
  - les implémentations concrètes des chunkers restent en Infrastructure.
- Traçabilité :
  - stocker la stratégie retenue par document pour faciliter debug/évaluation qualité retrieval.

### Évolution prévue (Sprint 4D)

- Objectif : rendre les chunks exploitables pour des domaines variés (transcripts, procédures, specs, etc.)
  sans figer un schéma métier unique.
- Design recommandé :
  - `DocumentChunk` ajoute `metadata_json: dict[str, Any] | None`.
  - persistance PostgreSQL en `JSONB` sur `document_chunks.metadata_json`.
  - API `GET /projects/{project_id}/documents/{document_id}/chunks` expose aussi `metadata_json`.
- Contrat minimal de metadata (noyau commun) :
  - `metadata_version` (ex: `1`)
  - `processing_strategy` (copie de la stratégie retenue)
  - `source_type` (type de segment textuel)
- Contrainte d'extensibilité :
  - chaque domaine peut enrichir `metadata_json` avec ses clés spécifiques sans migration systématique.
  - les consumers doivent tolérer des clés absentes/inconnues (forward compatibility).
