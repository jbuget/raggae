# Raggae - RAG Generator Agent Expert

Plateforme pour créer, gérer et publier des agents conversationnels basés sur RAG (Retrieval Augmented Generation).

## 🎯 Vision

Raggae permet à quiconque de créer un agent conversationnel personnalisé en :
1. Créant un projet avec un prompt système
2. Ajoutant des documents de connaissance
3. Testant l'agent via une interface chat
4. Publiant l'agent pour un usage public ou privé

## 🏗️ Architecture

Ce projet est développé selon les principes de **Clean Architecture** avec TDD strict.

### Stack technique

- **Backend** : FastAPI (Python 3.11+)
- **Base de données** : PostgreSQL 16 + pgvector
- **ORM** : SQLAlchemy 2.0 (async)
- **Migrations** : Alembic
- **Frontend** : Next.js 14 (TypeScript)
- **LLM** : OpenAI API (GPT-4, text-embedding-3-large)

### Structure du projet

```
raggae/
├── server/
│   ├── src/raggae/
│   │   ├── domain/          # Entités, Value Objects, Exceptions
│   │   ├── application/     # Use Cases, Interfaces, DTOs
│   │   ├── infrastructure/  # DB, Services externes
│   │   └── presentation/    # API FastAPI
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   └── alembic/
├── client/
│   └── src/
└── docs/                    # Documentation développeur
```

## 📚 Documentation développeur

Documentation essentielle pour Claude Code :

- **[AGENTS.md](./AGENTS.md)** : Guide complet pour Claude Code (TDD, Clean Arch, baby steps)
- **[SKILLS.md](./SKILLS.md)** : Compétences techniques requises (Python, FastAPI, SQLAlchemy)
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** : Décisions architecturales et patterns
- **[DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)** : Workflow quotidien (Red-Green-Refactor)

### Lecture obligatoire avant de coder

1. Lire `AGENTS.md` en entier (principes fondamentaux)
2. Consulter `ARCHITECTURE.md` (comprendre la structure)
3. Suivre `DEVELOPMENT_WORKFLOW.md` (workflow TDD)
4. Référencer `SKILLS.md` au besoin (exemples techniques)

## 🚀 Quick Start (Développement)

### Prérequis

- Python 3.11+
- PostgreSQL 16+ avec pgvector
- Node.js 18+ (pour le client)
- Docker & Docker Compose (optionnel)

### Installation

```bash
# 1. Cloner le repo
git clone <repo-url>
cd raggae

# 2. Lancer PostgreSQL (Docker)
docker-compose up -d postgres

# 3. Backend setup
cd server
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate sur Windows
pip install -e ".[dev]"

# 4. Variables d'environnement
cp .env.example .env
# Éditer .env avec vos credentials

# 5. Migrations
alembic upgrade head

# 6. Lancer les tests
pytest

# 7. Lancer le serveur
uvicorn src.raggae.presentation.main:app --reload

# 8. Frontend setup (dans un autre terminal)
cd client
npm install
npm run dev
```

### Commandes essentielles

```bash
# Tests
pytest                              # Tous les tests
pytest tests/unit                   # Tests unitaires uniquement
pytest -v -s                        # Verbose avec output
pytest --cov=src --cov-report=html  # Avec coverage

# Qualité du code
ruff format src/ tests/             # Formater
ruff check src/ tests/              # Linter
mypy src/                           # Type checking

# Base de données
alembic revision --autogenerate -m "description"  # Nouvelle migration
alembic upgrade head                              # Appliquer migrations
alembic downgrade -1                              # Rollback

# Serveur
uvicorn src.raggae.presentation.main:app --reload  # Dev server
```

## 🧪 Principes de développement

### TDD Strict

Cycle Red-Green-Refactor obligatoire :

1. **RED** : Écrire un test qui échoue
2. **GREEN** : Écrire le code minimum pour le faire passer
3. **REFACTOR** : Améliorer sans casser les tests

### Baby Steps

- Commits fréquents (10-20 par jour)
- Changements atomiques (< 100 lignes par commit)
- Chaque commit doit compiler et passer les tests

### Clean Architecture

Séparation stricte des couches :

```
Domain → Application → Infrastructure → Presentation
   ↑          ↑              ↑              ↑
   │          │              │              │
Aucune     Interfaces    Implémente     Appelle
dépendance  (Ports)     les interfaces  use cases
```

### Conventional Commits

Format strict :

```
type(scope): description

feat(domain): add user entity
fix(api): correct email validation
test(application): add create project use case tests
refactor(infrastructure): simplify repository
```

Types : `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`

## 📋 Fonctionnalités

### Phase 1 - MVP ✅ (en cours)

- [ ] Authentification (register, login, JWT)
- [ ] CRUD Projets
- [ ] Upload documents (TXT, MD)
- [ ] RAG basique (chunking + embeddings)
- [ ] Interface chat de test
- [ ] Frontend basique

### Phase 2 - Enrichissement

- [ ] Support PDF, DOCX
- [ ] Gestion conversations (historique)
- [ ] Publication projets (URL publique)
- [ ] Interface publique
- [ ] Amélioration UX

### Phase 3 - Avancé

- [ ] Chunking sémantique
- [ ] Re-ranking
- [ ] Analytics (usage, tokens)
- [ ] Collaboration (partage projets)
- [ ] Fine-tuning prompts

## 🧑‍💻 Contribution

### Workflow de développement

1. Choisir une tâche dans le backlog
2. Créer une branche (optionnel) : `git checkout -b feature/nom`
3. Développer en TDD (voir `DEVELOPMENT_WORKFLOW.md`)
4. Commits réguliers (Conventional Commits)
5. Tests passent : `pytest`
6. Code formaté : `ruff format`
7. Pas d'erreur linting : `ruff check`
8. Pas d'erreur types : `mypy src/`
9. Push et PR

### Checklist avant commit

```bash
# Automatique
./scripts/pre-commit-check.sh

# Ou manuel
pytest
ruff format src/ tests/
ruff check src/ tests/
mypy src/
```

### Standards de qualité

- Coverage > 80%
- Tous les tests passent
- 0 erreur mypy
- 0 erreur ruff
- Documentation inline (docstrings)

## 📖 API Documentation

Une fois le serveur lancé, la documentation interactive est disponible :

- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## 🔧 Configuration

### Variables d'environnement (Backend)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/raggae

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-...

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Variables d'environnement (Frontend)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 🐳 Docker

```bash
# Lancer tous les services
docker-compose up -d

# Logs
docker-compose logs -f

# Arrêter
docker-compose down

# Reset complet (⚠️ efface les données)
docker-compose down -v
```

## 🧪 Tests

### Pyramide des tests

- **70% Unit tests** : Domain + Application (rapides, isolés)
- **20% Integration tests** : Infrastructure (DB réelle)
- **10% E2E tests** : API complète

### Exécution

```bash
# Par type
pytest tests/unit           # < 1s
pytest tests/integration    # < 10s
pytest tests/e2e            # < 30s

# Par fichier
pytest tests/unit/domain/entities/test_user.py

# Par test
pytest tests/unit/domain/entities/test_user.py::TestUser::test_create_user

# Avec coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 📝 License

MIT

## 🙋 Support

Pour toute question sur l'architecture ou le développement, consulter :
1. La documentation dans `/docs`
2. Les tests existants (exemples)
3. Les issues GitHub

---

**Important pour Claude Code** :
- Toujours lire `AGENTS.md` avant de commencer
- Respecter le TDD strict (Red-Green-Refactor)
- Baby steps (petits commits)
- Clean Architecture (séparation des couches)
- Conventional Commits (format strict)
