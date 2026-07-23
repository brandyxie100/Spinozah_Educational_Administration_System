# Spinozah AI Education

AI-powered education administration for tutoring centres — students, scheduling, attendance, finance, parent portal, and AI learning analytics.

| | |
|---|---|
| **Repo** | [Spinozah_Educational_Administration_System](https://github.com/brandyxie100/Spinozah_Educational_Administration_System) |
| **Linear** | [Spinozah AI Education](https://linear.app/aipoweredcvprime/project/spinozah-ai-education-a4a8ea19a3ca) |
| **Plan** | [`docs/linear-project-plan.md`](docs/linear-project-plan.md) |
| **User guide** | [`docs/06-product-user-guide.md`](docs/06-product-user-guide.md) |

## What you get

| Area | Capabilities |
|------|----------------|
| **Identity** | Staff JWT login, refresh cookies, RBAC (`admin` / `frontdesk` / `teacher` / `parent`) |
| **Ops** | Users, teachers, students, enrolments, schedules, timetable, attendance & leave |
| **Finance** | Invoice list / create for staff |
| **Parent** | Magic-link login, child dashboard; staff parent↔student linking |
| **Admin** | KPI dashboard (students, teachers, revenue, unpaid alerts) |
| **AI** | Exam/question analysis, essay reports (+ PDF), Cambridge lesson plans, university pathway (IGCSE / A-Level / NCEA / IB + PDF) |
| **Persistence** | FastAPI + PostgreSQL multi-tenant schema; AI analyses stored via `/api/v1/analyses` |

AI generation runs through Next.js BFF routes under `app/api/ai/` (requires `OPENAI_API_KEY`). Ops data goes to FastAPI on port `8000`.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js 16 (App Router), React 19, TanStack Query, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI (DDD), SQLAlchemy async, Alembic, PostgreSQL 15 |
| AI (BFF) | Next.js Route Handlers + OpenAI (`app/api/ai/…`) |
| Local infra | Docker Compose (`db`, optional `api` profile) |

## Prerequisites

- Node.js **20+** (or 22 LTS) and npm 10+
- Python **3.11+**
- Docker + Docker Compose v2 (for PostgreSQL)
- An OpenAI API key (for AI modules only)

## Quick start

### 1. Clone and env

```bash
git clone https://github.com/brandyxie100/Spinozah_Educational_Administration_System.git
cd Spinozah_Educational_Administration_System

cp .env.example .env.local
# Edit .env.local:
#   - set OPENAI_API_KEY for AI features
#   - keep NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend reads backend/.env (or process env)
cp .env.example backend/.env
# Ensure DATABASE_URL, JWT_SECRET, CORS_ORIGINS are set in backend/.env
```

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

Defaults: user/password/db = `postgres` / `postgres` / `spinozah` on port `5432`.

### 3. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- Health: [http://localhost:8000/health](http://localhost:8000/health)
- OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)

Optional: run API in Docker after migrations — `docker compose --profile api up -d --build`.

### 4. Frontend

```bash
# from repository root (new terminal)
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 5. Create a first tenant + admin (one-time)

There is no public self-registration. Seed a local tenant and admin from `backend/` with the venv active:

```bash
cd backend && source .venv/bin/activate
python - <<'PY'
import asyncio
from app.infrastructure.persistence.models import TenantModel, UserModel, UserRole
from app.infrastructure.persistence.session import create_engine, create_session_factory
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher

async def main() -> None:
    engine = create_engine()
    session_factory = create_session_factory(engine)
    async with session_factory() as session:
        tenant = TenantModel(name="Demo Centre", slug="demo")
        session.add(tenant)
        await session.flush()
        session.add(
            UserModel(
                tenant_id=tenant.id,
                email="admin@demo.local",
                full_name="Demo Admin",
                hashed_password=BcryptPasswordHasher().hash("ChangeMe123!"),
                role=UserRole.ADMIN,
                is_active=True,
            )
        )
        await session.commit()
        print("tenant_slug=demo  email=admin@demo.local  password=ChangeMe123!")
    await engine.dispose()

asyncio.run(main())
PY
```

Then on the dashboard click **Staff sign in** and use:

| Field | Value |
|-------|--------|
| Tenant slug | `demo` |
| Email | `admin@demo.local` |
| Password | `ChangeMe123!` |

Change the password after first login (User Management).

## Using the app

1. Open [http://localhost:3000](http://localhost:3000).
2. **Staff sign in** (required for JWT-backed ops modules).
3. Open a dashboard card — modules include:

| Module | Typical roles | Notes |
|--------|---------------|--------|
| Admin Dashboard | admin | KPIs and unpaid alerts |
| User Management | admin | Create staff/parent users |
| Teacher / Student / Enrolment | admin, frontdesk | Core CRM |
| Schedule Management / Timetable | admin, frontdesk, teacher | Create slots; teachers view timetable |
| Attendance & Leave | teacher+ | Pick a schedule from the timetable (no raw UUID) |
| Parent Student Links | admin | Link parent users to students |
| Finance & Invoice | admin, frontdesk | List/create invoices |
| Parent Portal | parent | Request magic link → open emailed URL (or API token in dev) |
| Question Analysis / AI Reports / Lesson Planning / University Pathway | any (AI key) | BFF + optional FastAPI analysis persistence |

Deep links: `http://localhost:3000/?module=Student%20Management` (module title must match the card title).

Full walkthrough: [`docs/06-product-user-guide.md`](docs/06-product-user-guide.md).

## Verify

```bash
make lint
make test
```

Or separately:

```bash
# Frontend
npm run lint && npx tsc --noEmit && npm test

# Backend
cd backend && ruff check app tests && mypy --strict app
pytest tests/ --cov=app --cov-fail-under=80
```

## Documentation map

| Doc | Purpose |
|-----|---------|
| [`docs/06-product-user-guide.md`](docs/06-product-user-guide.md) | How to use each dashboard module |
| [`docs/04-operations-manual.md`](docs/04-operations-manual.md) | Setup, smoke tests, deploy, troubleshooting |
| [`docs/01-system_architecture.md`](docs/01-system_architecture.md) | Bounded contexts & DDD layers |
| [`docs/02-technology-selection.md`](docs/02-technology-selection.md) | Stack choices |
| [`docs/03-technical-standards.md`](docs/03-technical-standards.md) | Coding / testing standards |
| [`docs/05-git-workflow-guide.md`](docs/05-git-workflow-guide.md) | Branch, PR, CI |
| [`docs/linear-project-plan.md`](docs/linear-project-plan.md) | Milestones & Linear history |
| [`backend/README.md`](backend/README.md) | FastAPI layout, auth, API surface |

## Project status

Milestones M0–M3, dashboard polish (AIJOB-55–58), ops completeness (AIJOB-59…67), and AI productization (AIJOB-60, 68–70) are **shipped**. Next product backlog is TBD — see the Linear project.

## Contributing

Follow [`docs/05-git-workflow-guide.md`](docs/05-git-workflow-guide.md): branch from `main`, Conventional Commits, PR &lt; 800 lines, CI green, squash-merge.
