# Backend — Spinozah AI Education

FastAPI service with DDD layers, multi-tenant PostgreSQL, JWT auth, and REST APIs for ops + analysis persistence.

## Layout

```
backend/
├── app/
│   ├── api/             # HTTP routers (`/api/v1/...`)
│   ├── application/     # Use cases / services
│   ├── domain/          # Business rules (no FastAPI/SQLAlchemy)
│   ├── infrastructure/  # Persistence, security adapters
│   ├── core/            # Settings
│   └── main.py
├── migrations/          # Alembic (head: analysis records)
└── tests/
```

## Run locally

Prerequisites: PostgreSQL via root `docker compose up -d db`, and `backend/.env` (copy from root `.env.example`).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- Health: http://localhost:8000/health  
- OpenAPI: http://localhost:8000/docs  

Seed a first admin using the script in the root README.

## Auth

```bash
# Login — returns access_token JSON; sets httpOnly refresh_token cookie
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"tenant_slug":"demo","email":"admin@demo.local","password":"ChangeMe123!"}'

# Refresh — reads cookie, returns new access_token
curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/v1/auth/refresh

# Logout — clears refresh cookie
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/logout
```

Set `JWT_SECRET` (and optional TTLs) via environment — see root `.env.example`.

## RBAC

Protect routes with `Depends(require_roles(...))` from `app.api.deps`:

```python
from app.api.deps import require_roles
from app.domain.identity.roles import Role

@router.get("/admin/ping")
async def admin_ping(claims=Depends(require_roles(Role.ADMIN))):
    ...
```

Probe endpoints: `GET /api/v1/me` (any auth), `/api/v1/admin/ping` (admin), `/api/v1/staff/ping` (admin/frontdesk/teacher).

## API surface (v1)

| Prefix | Purpose |
|--------|---------|
| `/api/v1/auth` | Login, refresh, logout |
| `/api/v1/users` | Admin user CRUD |
| `/api/v1/students` | Student CRUD |
| `/api/v1/enrolments` | Lesson packages |
| `/api/v1/teachers` | Teacher CRUD |
| `/api/v1/schedules` | Create / teacher timetable |
| `/api/v1/attendance` | Attendance & leave |
| `/api/v1/invoices` | Finance invoices |
| `/api/v1/analyses` | Persist/list exam & essay analyses |
| `/api/v1/parent` | Magic link + parent dashboard reads |
| `/api/v1/admin/...` | KPI / admin read models |

AI **generation** (OpenAI) lives in the Next.js BFF (`app/api/ai/...` at repo root). This API stores analysis records and serves ops data.

## Tests & lint

```bash
ruff check app tests
mypy --strict app
pytest tests/ --cov=app --cov-fail-under=80
```

From repo root: `make lint` / `make test`.
