# Operations Manual — Spinozah AI Education

## 1. Document Purpose

Step-by-step guidelines for **environment setup**, **local development**, **functional testing**, and **production deployment**.

**Audience:** Developers, DevOps, and QA.  
**Last updated:** 2026-07-24

For end-user module walkthroughs see [`06-product-user-guide.md`](06-product-user-guide.md). For a short path see the root [`README.md`](../README.md).

---

## 2. System Components

| Component | Technology | Default Port |
|-----------|------------|--------------|
| Web application | Next.js 16 (App Router) | 3000 |
| API | FastAPI (DDD) | 8000 |
| Database | PostgreSQL 15 | 5432 |
| AI BFF | Next.js Route Handlers (`app/api/ai/…`) | via 3000 |
| Object storage (prod) | AWS S3 | HTTPS |

**Repository layout:** Next.js app at repository root; FastAPI under `backend/`; Compose starts `db` by default and optional `api` profile.

---

## 3. Prerequisites

### 3.1 Required Software

| Tool | Version | Verify |
|------|---------|--------|
| Node.js | 20+ or 22 LTS | `node -v` |
| npm | 10+ | `npm -v` |
| Git | 2.40+ | `git --version` |
| Python | 3.11+ | `python3 --version` |
| Docker | 24+ | `docker --version` |
| Docker Compose | v2 | `docker compose version` |

### 3.2 Optional / Production

| Tool | Purpose |
|------|---------|
| `gh` CLI | Pull requests and CI checks |
| AWS CLI | S3 bucket management |
| `psql` | Direct database inspection |
| OpenAI API key | Exam/essay/pathway/plan generation |

---

## 4. Environment Setup

### 4.1 Clone Repository

```bash
git clone https://github.com/brandyxie100/Spinozah_Educational_Administration_System.git
cd Spinozah_Educational_Administration_System
```

### 4.2 Frontend Environment Variables

```bash
cp .env.example .env.local
```

Minimum for full-stack local use:

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI base (`http://localhost:8000`) |
| `OPENAI_API_KEY` | Server-side AI BFF (never `NEXT_PUBLIC_`) |
| `OPENAI_MODEL` | Optional model override |

**Rules:**

- Prefix browser-exposed vars with `NEXT_PUBLIC_`
- Never expose `OPENAI_API_KEY` to the client
- Document new variables in `.env.example` and this manual

### 4.3 Backend Environment Variables

FastAPI loads `backend/.env` (see `app.core.settings`):

```bash
cp .env.example backend/.env
```

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/spinozah` |
| `JWT_SECRET` | Strong secret in non-dev environments |
| `JWT_ACCESS_EXPIRE_MINUTES` | Default 15 |
| `JWT_REFRESH_EXPIRE_DAYS` | Default 7 |
| `CORS_ORIGINS` | Comma-separated; include `http://localhost:3000` |
| `MAGIC_LINK_BASE_URL` | Parent magic-link landing (default `http://localhost:3000/parent/magic-link`) |
| `ENVIRONMENT` | `development` / `production` |

Generate a secret:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.4 Install Dependencies

**Frontend:**

```bash
npm install
```

**Backend:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 4.5 Start Database

```bash
docker compose up -d db
```

| Variable | Value |
|----------|-------|
| User | `postgres` |
| Password | `postgres` |
| Database | `spinozah` |
| URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/spinozah` |

Optional API container (after migrations):

```bash
docker compose --profile api up -d --build
```

### 4.6 Run Migrations

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

Current head includes identity through analysis records (`0009_analysis_records`).

### 4.7 Seed First Admin (local)

See root README § “Create a first tenant + admin”. Without a tenant/user, staff login cannot succeed.

---

## 5. Project Startup

### 5.1 Full Stack (recommended)

**Terminal 1 — Database:**

```bash
docker compose up -d db
```

**Terminal 2 — API:**

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

**Terminal 3 — Web:**

```bash
npm run dev
```

Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`.

### 5.2 Frontend Only (AI BFF demos)

```bash
npm run dev
```

Ops modules that call FastAPI will fail without the API. AI panels that only hit `app/api/ai/*` can still run if `OPENAI_API_KEY` is set.

### 5.3 Production Build Locally

```bash
npm run build
npm run start
```

### 5.4 Verify Health

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}  (or equivalent ok payload)

curl -I http://localhost:3000
# Expected: HTTP 200
```

---

## 6. Functional Testing

### 6.1 Manual Smoke Test — Staff Ops

1. Seed tenant/admin (README).
2. Start DB + API + `npm run dev`.
3. Open [http://localhost:3000](http://localhost:3000) → **Staff sign in**.
4. Walk modules: Users → Teachers → Students → Enrolments → Schedules → Timetable → Attendance → Parent Links → Finance → Admin Dashboard.
5. Confirm JWT-backed lists load (not empty auth errors).

### 6.2 Manual Smoke Test — Parent Portal

1. Create parent user + student + parent↔student link (admin).
2. Request magic link from Parent Portal.
3. Open `/parent/magic-link` with token; confirm child data.

### 6.3 Manual Smoke Test — AI Modules

1. Set `OPENAI_API_KEY` in `.env.local`.
2. Question Analysis: upload → analyze.
3. AI Reports: essay → scores → PDF.
4. Lesson Planning: generate Cambridge plan.
5. University Pathway: pick NCEA/IB/IGCSE/A-Level → generate → Download PDF.

### 6.4 Automated Tests

```bash
make lint
make test
```

**Backend only:**

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=80
```

**Frontend only:**

```bash
npm test
npm run lint
npx tsc --noEmit
```

### 6.5 Integration Checklist

| Area | Test |
|------|------|
| Auth | Login as admin/teacher; 403 on wrong role |
| Students | CRUD + pagination |
| Enrolments | Create package; patch remaining lessons |
| Scheduling | Create schedule; conflict returns 409 |
| Attendance | Leave approval updates remaining lessons |
| Finance | Invoice amounts and unpaid alerts |
| Analyses | POST/GET `/api/v1/analyses` tenant-scoped |
| Tenant | Tenant A cannot read Tenant B by ID |
| AI BFF | Analyze/generate returns structured JSON |

### 6.6 Role-Based Scenarios

| Role | Key flows |
|------|-----------|
| admin | User management, revenue dashboard, all CRUD |
| frontdesk | Enrolment, scheduling, invoices |
| teacher | Timetable, attendance confirmation, AI uploads |
| parent | Magic link login, view child attendance |

---

## 7. Linting & Code Quality

```bash
make lint
```

Equivalent:

```bash
# Frontend
npm run lint
npx tsc --noEmit

# Backend
cd backend
ruff check app tests
mypy --strict app
```

---

## 8. Official Deployment

### 8.1 Deployment Topology (Recommended)

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Vercel     │────▶│ Railway /    │────▶│  Managed     │
│  (Next.js)   │     │ Render (API) │     │ PostgreSQL   │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   AWS S3     │
                     └──────────────┘
```

### 8.2 Deploy Frontend to Vercel

1. Connect GitHub repository to Vercel
2. Framework preset: **Next.js**
3. Root directory: `.`
4. Build: `npm run build`
5. Set `NEXT_PUBLIC_API_URL`, `OPENAI_API_KEY` (and related) in Vercel
6. Deploy from `main`; enable PR previews

### 8.3 Deploy API

1. Build from `backend/Dockerfile` or Compose `api` profile pattern
2. Set `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, magic-link base URL
3. Attach managed PostgreSQL
4. Release command: `alembic upgrade head`
5. Point Vercel `NEXT_PUBLIC_API_URL` at the public API URL

**Health check path:** `/health`

### 8.4 Database Production

- Automated daily backups
- SSL connection string
- Network restricted to API service
- Separate staging vs production databases

### 8.5 S3 Configuration (when enabling uploads)

1. Private bucket; CORS for API origins only
2. IAM minimal policy: `s3:PutObject`, `s3:GetObject`
3. Lifecycle rules for temp uploads if needed

### 8.6 Post-Deploy Verification

```bash
curl https://api.<your-domain>/health
curl -I https://<your-domain>
```

Checklist:

- [ ] HTTPS on web and API
- [ ] Login works for each role
- [ ] CORS allows production frontend origin only
- [ ] OpenAI calls succeed from server (not browser)
- [ ] Migrations applied
- [ ] Error monitoring configured (optional)

### 8.7 Rollback

| Layer | Action |
|-------|--------|
| Vercel | Redeploy previous deployment |
| API platform | Roll back previous release image |
| Database | Restore from snapshot (test on staging first) |

---

## 9. Monitoring & Maintenance

### 9.1 Logs

- **Vercel:** Function and build logs
- **API host:** Platform log stream; structured JSON recommended
- **PostgreSQL:** Slow query log if p95 degrades

### 9.2 Routine Tasks

| Frequency | Task |
|-----------|------|
| Daily | `git fetch origin && git rebase origin/main` on active branches |
| Weekly | Review dependency security advisories |
| Monthly | Verify DB backup restore on staging |
| On release | Full test suite + production smoke |

### 9.3 Incident Response (Brief)

1. Check `/health` and platform status
2. Review recent deployments
3. Roll back if deployment-correlated
4. Communicate; post-mortem for Sev-1

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `npm run dev` fails | Node version | Use Node 20+ |
| Port 3000/8000 in use | Another process | `lsof -i :3000` / `:8000` |
| PDF/AI 500 | Missing `OPENAI_API_KEY` or bad file | Check `.env.local` and server logs |
| API CORS error | Wrong `CORS_ORIGINS` | Add frontend origin in `backend/.env` |
| DB connection refused | Docker not running | `docker compose up -d db` |
| 401 on API | Expired/missing JWT | Staff sign in again |
| Staff login fails | No tenant/user | Run seed script in README |
| Empty ops lists | Not signed in | Use Staff sign in before opening module |
| Migration errors | Stale DB | Backup; `alembic upgrade head` |

---

## 11. Environment Matrix

| Environment | Web URL | API URL | Database |
|-------------|---------|---------|----------|
| Local | localhost:3000 | localhost:8000 | Docker PG |
| Staging | staging.*.vercel.app | staging-api.* | staging PG |
| Production | app.* | api.* | production PG |

---

## 12. Related Documents

- `01-system_architecture.md` — system structure
- `02-technology-selection.md` — hosting choices
- `03-technical-standards.md` — quality gates
- `05-git-workflow-guide.md` — release process via PR
- `06-product-user-guide.md` — product usage
- `linear-project-plan.md` — milestones / Linear

---

## 13. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-19 | Initial operations manual |
| 1.1 | 2026-07-24 | Synced to shipped FastAPI + dashboard + AI BFF; removed Current/Target placeholders |
