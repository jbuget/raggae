# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raggae** (RAG Generator Agent Expert) — a platform to create, manage, and publish conversational agents based on RAG (Retrieval Augmented Generation). Currently a greenfield project: backend/ and frontend/ directories are empty, comprehensive documentation is in docs/.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 16 + pgvector, OpenAI API
- **Frontend**: Next.js 14 (TypeScript)
- **Quality tools**: ruff (lint + format), mypy (type check), pytest (tests)

## Essential Commands (Backend)

All backend commands run from `backend/`.

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

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
cd frontend && npm install && npm run dev
```

## Architecture: Clean Architecture (Strict)

Four layers with dependencies always pointing inward:

```
Domain (entities, value objects, exceptions) — NO external dependencies
  ↑
Application (use cases, interfaces/ports, DTOs) — depends only on Domain
  ↑
Infrastructure (SQLAlchemy repos, OpenAI/JWT/bcrypt services, config) — implements Application interfaces
  ↑
Presentation (FastAPI endpoints, Pydantic schemas, DI) — orchestrates use cases
```

Backend source layout: `backend/src/raggae/{domain,application,infrastructure,presentation}/`
Tests mirror source: `backend/tests/{unit,integration,e2e}/`

## Mandatory Development Rules

1. **TDD (Red-Green-Refactor)**: Always write a failing test first, then minimal code to pass, then refactor. Never write code without a test.
2. **Baby Steps**: Small atomic commits (max 50-100 lines). Each commit must compile and pass all tests.
3. **Conventional Commits**: `type(scope): description` — types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `build`.
4. **No Claude attribution**: Never add co-author or Claude mentions in commits.
5. **Clean Architecture**: Respect layer boundaries strictly. Domain depends on nothing. No ORM models in domain.
6. **Test coverage > 80%**: Pyramid — 70% unit, 20% integration, 10% E2E.

## Test Naming Conventions

```python
def test_<what>_<condition>_<expected>():     # Unit
async def test_integration_<component>_<scenario>():  # Integration
async def test_e2e_<feature>_<scenario>():    # E2E
```

Use Given/When/Then structure inside tests. Unit tests use in-memory fakes (e.g., `InMemoryUserRepository`, `FakePasswordHasher`).

## Key Documentation

Read these before coding (in `docs/`):
- **AGENTS.md** — Development principles and workflow (primary reference)
- **ARCHITECTURE.md** — Architectural decisions and patterns
- **DEVELOPMENT_WORKFLOW.md** — Daily Red-Green-Refactor workflow
- **SKILLS.md** — Technical examples (Python, FastAPI, SQLAlchemy patterns)
- **TESTING_STRATEGY.md** — Testing philosophy and fixtures

## Pre-Commit Checklist

Before every commit: `pytest` passes, `ruff format`, `ruff check` clean, `mypy` clean.
