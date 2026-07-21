# Backend — Spinozah AI Education

FastAPI DDD scaffold (`AIJOB-32`).

## Layout

```
backend/
├── app/
│   ├── api/             # HTTP routers
│   ├── application/     # Use cases
│   ├── domain/          # Business rules (no FastAPI/SQLAlchemy)
│   ├── infrastructure/  # Adapters
│   ├── core/            # Settings
│   └── main.py
├── migrations/          # Alembic (AIJOB-29)
└── tests/
```

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

Health: http://localhost:8000/health

## Database (AIJOB-29)

```bash
# with Postgres running locally (or via Docker in AIJOB-30):
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/spinozah
cd backend
alembic upgrade head
```
