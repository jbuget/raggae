# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raggae** (RAG Generator Agent Expert) — a platform to create, manage, and publish conversational agents
based on RAG (Retrieval Augmented Generation).

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 16 + pgvector
- **Frontend**: Next.js 14 (TypeScript)
- **Quality tools**: ruff (lint + format), mypy (type check), pytest (tests)

## Essential Commands (Backend)

All backend commands run from `server/`.

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,test]"

# Tests
pytest                              # All tests
pytest tests/unit                   # Unit tests only
pytest tests/unit/domain/entities/test_user.py  # Single file
pytest tests/unit/domain/entities/test_user.py::TestUser::test_create_user  # Single test
pytest --cov=src --cov-report=html  # With coverage

# Code quality
ruff format src/ tests/             # Format
ruff check src/ tests/              # Lint
mypy src/                           # Type check

# Database
alembic upgrade head                # Apply migrations
alembic revision --autogenerate -m "description"  # New migration
alembic downgrade -1                # Rollback

# Dev server
uvicorn src.raggae.presentation.main:app --reload
```

## Frontend Commands

```bash
cd client && npm install && npm run dev
```

## Architecture: DDD + Clean Architecture (Strict)

Domain-Driven Design with four layers, dependencies always pointing inward:

```
Domain (entities, value objects, domain services, exceptions) — NO external dependencies
  ↑
Application (use cases, interfaces/ports, DTOs, application services) — depends only on Domain
  ↑
Infrastructure (SQLAlchemy repos, external services, config) — implements Application interfaces
  ↑
Presentation (FastAPI endpoints, Pydantic schemas, DI) — orchestrates use cases
```

Backend source layout: `server/src/raggae/{domain,application,infrastructure,presentation}/`
Tests mirror source: `server/tests/{unit,integration,e2e}/`

## Mandatory Development Rules

### Code Quality

1. **TDD (Red-Green-Refactor)**: Always write a failing test first, then minimal code to pass, then
   refactor. Never write code without a test.
2. **Baby Steps**: Small atomic commits (max 50–100 lines). Each commit must compile and pass all tests.
3. **DDD + Clean Architecture**: Respect layer boundaries strictly. Domain has zero external dependencies.
   No ORM models in domain. Use ubiquitous language in entity and use case naming.
4. **Test coverage > 80%**: Pyramid — 70% unit, 20% integration, 10% E2E.
5. **Clean Code**: Meaningful names, small focused functions, no magic values, no dead code.
   Follow Software Craftsmanship principles (SOLID, DRY, YAGNI, KISS).

### Language Conventions

| What | Language |
|------|----------|
| Source code (variables, functions, classes, inline comments) | **English** |
| Documentation (docs/, docstrings) | **French** |
| Commit messages | **French** |
| PR titles and descriptions | **French** |

### Git Workflow

> **RÈGLE ABSOLUE** : ne jamais commiter ni pusher directement sur `main`.
> Toujours passer par une branche + Pull Request, sans exception.

1. **Feature branching** — never commit directly to `main`. Always create a branch:

   ```bash
   git checkout -b feat/register-user     # new feature
   git checkout -b fix/login-token        # bug fix
   git checkout -b refactor/user-entity   # refactoring
   git checkout -b test/project-use-cases # tests only
   git checkout -b docs/architecture      # documentation
   ```

2. **Conventional Commits** (message in French):

   ```
   type(scope): description en français
   ```

   Allowed types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`.

3. **No Claude attribution**: Never add co-author or Claude mentions in commits.

4. **Quality gate before push**: run the full pre-push checklist (see below) before every `git push`.

5. **Pull Request** : one PR per feature/fix/refactor. Use the PR format below.
   **Never merge to `main` without a PR** — even for small or cosmetic changes.

### Pull Request Format

PR title and description must be in French. Description structure:

```markdown
## Problème
Describe the problem or need this PR addresses.

## Solution
Explain the chosen approach and why.

## Implémentation
List the main technical changes (files, layers, patterns used).

## Recette
Steps or scenarios to manually validate the feature works correctly.
```

## Test Naming Conventions

```python
def test_<what>_<condition>_<expected>():              # Unit
async def test_integration_<component>_<scenario>():   # Integration
async def test_e2e_<feature>_<scenario>():             # E2E
```

Use Given/When/Then structure inside every test. Unit tests use in-memory fakes
(e.g., `InMemoryUserRepository`, `FakePasswordHasher`).

## Key Documentation

Read these before coding:

- **PLAN_IN_PROGRESS.md** — Current feature being developed: tasks, decisions, branch (read first if present)
- **docs/AGENTS.md** — Development principles, workflow, and project scope (primary reference)
- **docs/ARCHITECTURE.md** — Architectural decisions and patterns
- **docs/DEVELOPMENT_WORKFLOW.md** — Daily Red-Green-Refactor workflow and git practices
- **docs/SKILLS.md** — Technical examples (Python, FastAPI, SQLAlchemy patterns)
- **docs/TESTING_STRATEGY.md** — Testing philosophy and fixtures

## Commande "envoie en prod"

Quand l'utilisateur dit **"envoie en prod"**, exécuter dans l'ordre :

1. Tirer une branche depuis `main` en respectant les conventions de nommage
2. Faire le ou les commits unitaires (Conventional Commits, messages en français)
3. Lancer les tests et les checks qualité (voir Pre-Push Checklist ci-dessous)
4. `git push` vers le remote
5. Créer la PR en respectant le template (titre et description en français)
6. Merger la PR

## Pre-Push Checklist

Run all of the following before every `git push`. All must pass with zero errors:

```bash
pytest                   # All tests pass
ruff format src/ tests/  # Code formatted
ruff check src/ tests/   # No lint errors
mypy src/                # No type errors
```
