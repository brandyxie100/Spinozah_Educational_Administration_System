# Technical Standards — Faculty Management System

## 1. Document Purpose

This document provides a **comprehensive overview** of the full project technology stack, coding conventions, testing requirements, and quality gates. All contributors and AI-assisted development must comply.

**Repository:** `spinozah-ai-education`  
**Product:** Spinozah AI Education — Faculty / tutoring center management platform

---

## 2. Technology Stack Overview

### 2.1 Stack Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  Next.js 16 · React 19 · TypeScript 5 · Tailwind CSS 4      │
│  TanStack Query (planned) · Zustand (optional)               │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS / REST / JSON
┌───────────────────────────▼─────────────────────────────────┐
│                    API Interface Layer                       │
│  FastAPI · Pydantic v2 · JWT middleware · OpenAPI 3         │
│  Next.js Route Handlers (BFF / prototype only)               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Application Layer                         │
│  Use cases · Command/Query handlers · Transaction boundaries │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Domain Layer                            │
│  Entities · Value objects · Domain services · Events         │
└───────────────────────────┬─────────────────────────────────┘
                            │ interfaces
┌───────────────────────────▼─────────────────────────────────┐
│                   Infrastructure Layer                       │
│  SQLAlchemy async · Alembic · PostgreSQL · S3 · OpenAI      │
│  ReportLab · Email adapters                                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Version Targets

| Component | Version / Target |
|-----------|------------------|
| Node.js | 20 LTS or 22 LTS |
| Python | 3.11+ |
| PostgreSQL | 15+ |
| Next.js | 16.x |
| React | 19.x |
| TypeScript | 5.x |
| FastAPI | 0.110+ |
| SQLAlchemy | 2.0+ async |

---

## 3. Bounded Contexts & Naming

Commit scopes and module tags MUST match bounded contexts:

| Scope | Responsibility |
|-------|----------------|
| `identity` | Auth, users, roles, tenants |
| `students` | Student CRUD, enrolment, lesson balance |
| `scheduling` | Timetables, classrooms, conflicts |
| `attendance` | Check-in, leave, deductions |
| `finance` | Invoices, payments, credits |
| `ai-analysis` | Exam, essay, question analysis |
| `parent-portal` | Parent views, magic links |
| `planning` | Lesson plans, Cambridge, university pathway |
| `shared` | Cross-cutting utilities, base types |
| `frontend` | UI-only changes |

Linear issue format: `[p{n}][{Type}][{module}] {title}`

---

## 4. Backend Standards (Python)

**Applies to:** `backend/**/*.py`

### 4.1 Tooling

| Tool | Configuration |
|------|---------------|
| Formatter / linter | Ruff (line length 88) |
| Type checker | mypy `--strict` |
| Test runner | pytest |
| Test data | factory_boy |
| Migrations | Alembic |

### 4.2 Code Style

- **Naming:** `snake_case` functions/variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants
- **Docstrings:** Google style on all public classes and functions
- **Type hints:** Required on all function signatures (mypy strict)

### 4.3 Required Pattern

```python
def calculate_remaining_lessons(
    total_lessons: int,
    completed_lessons: int,
) -> int:
    """Calculate remaining lessons for a student enrolment.

    Args:
        total_lessons: Total lessons purchased.
        completed_lessons: Lessons already consumed.

    Returns:
        Non-negative count of remaining lessons.

    Raises:
        ValueError: If completed_lessons exceeds total_lessons.
    """
    if completed_lessons > total_lessons:
        raise ValueError("completed_lessons cannot exceed total_lessons")
    return total_lessons - completed_lessons
```

### 4.4 Layer Rules

| Rule | Detail |
|------|--------|
| No ORM in domain | `from sqlalchemy import ...` forbidden in `domain/` |
| Tenant filter | Every repository query includes `tenant_id` |
| No magic numbers | Extract to named constants |
| Config | Use `pydantic-settings`; no hardcoded secrets |
| Exceptions | No bare `except:`; log and re-raise or map to domain errors |

### 4.5 File Naming (per entity)

```text
student_entity.py          # domain entity (or entities.py per context)
student_repository.py      # interface in domain; impl in infrastructure
student_service.py         # application use case (or handlers/)
student_schema.py          # Pydantic API schemas
student_router.py          # FastAPI routes
```

### 4.6 API Conventions

- RESTful resources, plural nouns: `/api/v1/students`
- Pagination: `?page=1&page_size=20`
- Errors: consistent JSON envelope `{ "detail": "...", "code": "..." }`
- Async handlers for I/O-bound endpoints
- OpenAPI tags per bounded context

### 4.7 Testing (Backend)

| Type | Naming | Marker |
|------|--------|--------|
| Unit (domain) | `test_<method>_<scenario>_<expected>` | default |
| Integration (API/DB) | same | `pytest.mark.integration` |
| Tenant isolation | `test_tenant_a_cannot_see_tenant_b_data` | `pytest.mark.tenant_isolation` |

**Coverage targets:**

- Overall: ≥ 80%
- Domain layer: ≥ 90%

Use `factory_boy` — never hardcode entity construction in tests.

---

## 5. Frontend Standards (TypeScript)

**Applies to:** `app/**/*.{ts,tsx}` and future `frontend/**/*.{ts,tsx}`

### 5.1 Tooling

| Tool | Configuration |
|------|---------------|
| Linter | ESLint 9 + `eslint-config-next` |
| Type checker | `tsc --noEmit` strict |
| Formatter | Prettier (printWidth 100, singleQuote true) — when added |
| CSS | Tailwind CSS utility classes only |
| Tests | Jest + React Testing Library + MSW |

### 5.2 Code Style

- **Imports:** Absolute `@/` alias when configured
- **One component per file;** filename matches component name
- **`any` is banned** — use `unknown` with type guards

### 5.3 Component Patterns

| Pattern | Usage |
|---------|--------|
| Container / Presenter | `StudentListContainer` + `StudentListView` |
| Custom hooks | `useAuth()`, `useStudents()`, `useSchedule()` |
| Providers | `AuthProvider`, `TenantProvider` via React Context |
| Server state | TanStack Query — no ad-hoc `fetch` in components |

### 5.4 Security (Frontend)

| Rule | Reason |
|------|--------|
| Access token in memory only | Reduce XSS exfiltration |
| Refresh token in httpOnly cookie | Not accessible to JS |
| No `localStorage` for tokens | XSS risk |
| API calls via hooks/services | Single place for auth headers |

### 5.5 Testing (Frontend)

```typescript
describe('AttendanceCard', () => {
  it('should show leave count when student has used leave', () => { ... });
  it('should show empty state when no attendance records', () => { ... });
});
```

- Test user-visible behavior, not implementation details
- Mock APIs with MSW

---

## 6. Database Standards

### 6.1 Schema Conventions

| Rule | Example |
|------|---------|
| Primary keys | UUID (`gen_random_uuid()`) |
| Timestamps | `created_at`, `updated_at` (UTC, timezone-aware) |
| Soft delete | `deleted_at` nullable where needed |
| Multi-tenant | `tenant_id UUID NOT NULL` on all tenant data |
| Foreign keys | Indexed |
| Enums | PostgreSQL `ENUM` types for stable domains |

### 6.2 Migration Rules

- One logical change per Alembic revision
- Reversible migrations when feasible
- Never edit applied migrations in shared environments

---

## 7. AI & Integration Standards

### 7.1 Structured AI Responses

All AI endpoints return parseable JSON:

```json
{
  "scores": {
    "grammar_score": 82,
    "vocabulary_score": 75,
    "structure_score": 80
  },
  "strengths": [],
  "weaknesses": [],
  "recommendations": []
}
```

### 7.2 Prompt & Adapter Location

- Prompts: `backend/app/infrastructure/ai/prompts/`
- Domain defines output schema (Pydantic models)
- Infrastructure calls OpenAI and validates response against schema

### 7.3 File Uploads

- Max size enforced at API layer
- Allowed MIME types whitelisted
- Store in S3; DB holds metadata + URL only

---

## 8. Security Standards

| Area | Standard |
|------|----------|
| Passwords | bcrypt with appropriate cost factor |
| API auth | Bearer JWT; short access TTL |
| RBAC | `admin`, `frontdesk`, `teacher`, `parent` |
| CORS | Explicit allowed origins in production |
| Secrets | Environment variables only |
| Dependencies | Regular `npm audit` / `pip-audit` in CI |
| PII | Minimize logs; no student data in debug output |

---

## 9. Git & CI Quality Gates

### 9.1 Pre-Merge Requirements

```bash
# Backend (when present)
ruff check backend/
mypy --strict backend/
pytest backend/tests/ --cov=backend/app --cov-fail-under=80

# Frontend
npm run lint          # eslint
npx tsc --noEmit
npm test              # when test script added
```

Or use `make lint` and `make test` when Makefile is added.

### 9.2 CI Pipeline (Target — 6 checks)

1. PR base branch = `main`
2. Backend lint (Ruff + mypy)
3. Backend tests + coverage
4. Frontend lint (ESLint + tsc)
5. Frontend tests
6. Build verification (`next build`, Docker image if applicable)

### 9.3 Pull Request Limits

- PR diff &lt; 800 lines — split otherwise
- Description: Summary, Motivation, Changes, Testing checklist

---

## 10. Documentation Standards

| Artifact | Requirement |
|----------|-------------|
| Public Python APIs | Google docstrings |
| Public TS exports | TSDoc for non-obvious APIs |
| Architecture changes | Update `docs/01-system_architecture.md` |
| New env vars | Document in `.env.example` and `04-operations-manual.md` |
| Critical logic | Inline comment at non-obvious decision points only |

---

## 11. Docker & Environment (Target)

```yaml
# docker-compose.yml (illustrative)
services:
  db:
    image: postgres:15
  api:
    build: ./backend
    env_file: .env
  web:
    build: .
    ports: ["3000:3000"]
```

See `04-operations-manual.md` for setup steps.

---

## 12. Forbidden Practices (Global)

| Forbidden | Alternative |
|-----------|-------------|
| Business logic in API routes | Application use case |
| `any` in TypeScript | `unknown` + guards |
| Bare `except:` in Python | Specific exceptions + logging |
| Magic numbers | Named constants |
| Hardcoded config strings | Settings / env |
| Cross-tenant queries without `tenant_id` | Repository base filter |
| Tokens in localStorage | Memory + httpOnly cookie |
| Inline styles | Tailwind utilities |
| Direct OpenAI calls from domain | Infrastructure adapter |

---

## 13. Development Workflow Summary

Every feature or bugfix:

1. Branch from `main`
2. Read relevant `docs/`
3. Write failing tests first
4. Implement (Domain → Application → Infrastructure → API)
5. Run lint + tests
6. Conventional Commit
7. PR to `main` → CI → review → squash merge

Full detail: `05-git-workflow-guide.md` and `.cursor/rules/workflow.mdc`.

---

## 14. Related Documents

| Document | Content |
|----------|---------|
| `01-system_architecture.md` | Layers and modules |
| `02-technology-selection.md` | Why each tool was chosen |
| `04-operations-manual.md` | Run and deploy |
| `05-git-workflow-guide.md` | Git and PR process |
| `function_development_skills_guide.md` | Cursor skills per feature |

---

## 15. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-19 | Initial technical standards |
