# Spinozah AI Education

AI-powered education administration for tutoring centres — students, scheduling, attendance, finance, parent portal, and AI learning analytics.

**Repo:** [Spinozah_Educational_Administration_System](https://github.com/brandyxie100/Spinozah_Educational_Administration_System)  
**Linear:** [Spinozah AI Education](https://linear.app/aipoweredcvprime/project/spinozah-ai-education-a4a8ea19a3ca)  
**Plan:** [`docs/linear-project-plan.md`](docs/linear-project-plan.md)

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Next.js (App Router), TanStack Query, TypeScript |
| Backend | FastAPI (DDD), SQLAlchemy, Alembic, PostgreSQL |
| AI (MVP) | Next.js BFF routes under `app/api/ai/` |

## Local setup

```bash
# 1. Env
cp .env.example .env.local

# 2. Postgres (and optional services)
docker compose up -d

# 3. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # or follow backend/README.md
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 4. Frontend (repo root)
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). API base URL defaults to `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Docs

| Doc | Purpose |
|-----|---------|
| [`docs/01-system_architecture.md`](docs/01-system_architecture.md) | Bounded contexts & architecture |
| [`docs/03-technical-standards.md`](docs/03-technical-standards.md) | Coding / DDD standards |
| [`docs/05-git-workflow-guide.md`](docs/05-git-workflow-guide.md) | Branch, PR, CI |
| [`docs/linear-project-plan.md`](docs/linear-project-plan.md) | Milestones & Linear backlog |

## Verify

```bash
make lint
make test
```

## Next focus

Staff ops completeness — start with **AIJOB-61** (staff login + JWT client wiring). See plan §11.
