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

## Auth (AIJOB-35)

```bash
# Login — returns access_token JSON; sets httpOnly refresh_token cookie
curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"tenant_slug":"acme","email":"admin@acme.test","password":"..."}'

# Refresh — reads cookie, returns new access_token
curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/v1/auth/refresh

# Logout — clears refresh cookie
curl -b cookies.txt -X POST http://localhost:8000/api/v1/auth/logout
```

Set `JWT_SECRET` (and optional TTLs) via environment — see root `.env.example`.
