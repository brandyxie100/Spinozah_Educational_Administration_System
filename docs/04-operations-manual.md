# Operations Manual — AI Education Management System

## 1. Document Purpose

Step-by-step guidelines for **environment setup**, **local development**, **functional testing**, and **production deployment** of the Spinozah AI Education (Faculty Management) platform.

**Audience:** Developers, DevOps, and QA.

---

## 2. System Components

| Component | Technology | Default Port |
|-----------|------------|--------------|
| Web application | Next.js | 3000 |
| API (target) | FastAPI | 8000 |
| Database (target) | PostgreSQL | 5432 |
| Object storage (prod) | AWS S3 | HTTPS |

**Current repository state:** Next.js app at repository root with prototype API route `app/api/analyze`. Backend and Docker services are **planned** — sections below mark **(Current)** vs **(Target)**.

---

## 3. Prerequisites

### 3.1 Required Software

| Tool | Version | Verify |
|------|---------|--------|
| Node.js | 20+ or 22 LTS | `node -v` |
| npm | 10+ | `npm -v` |
| Git | 2.40+ | `git --version` |
| Python (target) | 3.11+ | `python3 --version` |
| Docker (target) | 24+ | `docker --version` |
| Docker Compose (target) | v2 | `docker compose version` |

### 3.2 Optional / Production

| Tool | Purpose |
|------|---------|
| `gh` CLI | Pull requests and CI checks |
| AWS CLI | S3 bucket management |
| `psql` | Direct database inspection |

---

## 4. Environment Setup

### 4.1 Clone Repository

```bash
git clone <repository-url>
cd spinozah-ai-education
```

### 4.2 Frontend Environment Variables (Current)

Create `.env.local` in the project root (never commit):

```bash
# .env.local (example)
# NEXT_PUBLIC_API_URL=http://localhost:8000   # when FastAPI is running
# OPENAI_API_KEY=sk-...                        # server-side only; use in API routes
```

Copy from `.env.example` in the project root:

```bash
cp .env.example .env.local
```

**Rules:**

- Prefix client-exposed vars with `NEXT_PUBLIC_`
- Never expose `OPENAI_API_KEY` to the browser
- Add new variables to `.env.example` and this manual

### 4.3 Backend Environment Variables (Target)

Create `backend/.env`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/spinozah
JWT_SECRET=<generate-strong-secret>
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=spinozah-uploads
AWS_REGION=ap-southeast-1
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

Generate a secret:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.4 Install Dependencies (Current)

```bash
npm install
```

### 4.5 Install Backend Dependencies (Target)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4.6 Start Database (Target)

Using Docker Compose (when `docker-compose.yml` is added):

```bash
docker compose up -d db
```

Or standalone PostgreSQL:

```bash
createdb spinozah
```

### 4.7 Run Migrations (Target)

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

---

## 5. Project Startup

### 5.1 Development — Frontend Only (Current)

```bash
# From repository root
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**Production build locally:**

```bash
npm run build
npm run start
```

### 5.2 Development — Full Stack (Target)

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

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`.

### 5.3 Verify Health (Target)

```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:3000
# Expected: HTML dashboard
```

---

## 6. Functional Testing

### 6.1 Manual Smoke Test — Dashboard (Current)

1. Start dev server: `npm run dev`
2. Open [http://localhost:3000](http://localhost:3000)
3. Confirm **Spinozah AI Education** dashboard loads
4. Open each module card and verify navigation:
   - Teacher Timetable
   - Student Management
   - Attendance & Leave
   - Question Analysis
   - Parent Portal
   - Finance & Invoice
   - AI Reports
   - Lesson Planning
   - University Pathway
5. Use **← Back** to return to dashboard

### 6.2 Manual Test — PDF Upload / Analyze (Current)

1. Navigate to **Question Analysis**
2. Upload a PDF test paper
3. Confirm **Extracted Content Preview** appears
4. Click **Analyze Test Paper**
5. Confirm structured report section renders

**API direct test:**

```bash
curl -X POST http://localhost:3000/api/analyze \
  -F "file=@/path/to/sample.pdf"
```

Expected JSON: `{ "text": "..." }` or `{ "error": "..." }`

### 6.3 Automated Tests (Target)

**Backend:**

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

**Frontend:**

```bash
npm test
npm run lint
npx tsc --noEmit
```

**Full gate (when Makefile exists):**

```bash
make lint
make test
```

### 6.4 Integration Test Checklist (Target)

| Area | Test |
|------|------|
| Auth | Login as admin, teacher, parent; verify 403 on wrong role |
| Students | CRUD + pagination |
| Scheduling | Create schedule; conflict returns 409 |
| Attendance | Leave approval updates remaining lessons |
| Finance | Invoice `final_amount = subtotal - credit` |
| Tenant | Tenant A cannot read Tenant B student by ID |
| AI | Upload → job → poll → structured JSON report |

### 6.5 Role-Based Scenarios

| Role | Key flows |
|------|-----------|
| admin | User management, revenue dashboard, all CRUD |
| frontdesk | Student enrolment, scheduling, invoices |
| teacher | Timetable, attendance confirmation, upload exam |
| parent | Magic link login, view child attendance and reports |

---

## 7. Linting & Code Quality

### 7.1 Frontend (Current)

```bash
npm run lint
npx tsc --noEmit
```

### 7.2 Backend (Target)

```bash
ruff check backend/
ruff format --check backend/
mypy --strict backend/
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
3. Root directory: `.` (repository root)
4. Build command: `npm run build`
5. Output: Next.js default
6. Set environment variables in Vercel dashboard (no secrets in git)
7. Deploy from `main` branch; enable preview deployments for PRs

```bash
# Optional CLI
npx vercel --prod
```

### 8.3 Deploy API (Target)

**Railway / Render / Fly.io:**

1. Create service from `backend/` Dockerfile or buildpack
2. Set all `backend/.env` variables in platform UI
3. Attach managed PostgreSQL plugin
4. Run release command: `alembic upgrade head`
5. Note public API URL → set `NEXT_PUBLIC_API_URL` on Vercel

**Health check path:** `/health`

### 8.4 Database Production

- Enable automated daily backups
- Use SSL connection string (`?sslmode=require`)
- Restrict network access to API service only
- Separate databases for staging and production

### 8.5 S3 Configuration

1. Create bucket with private ACL
2. CORS for API upload origins only
3. IAM user with minimal policy: `s3:PutObject`, `s3:GetObject` on bucket prefix
4. Set lifecycle rule for temp uploads if needed

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
- [ ] File upload reaches S3
- [ ] Error monitoring configured (e.g. Sentry)

### 8.7 Rollback

| Layer | Action |
|-------|--------|
| Vercel | Redeploy previous deployment from dashboard |
| API platform | Roll back to previous release image |
| Database | Restore from snapshot (last resort; test on staging first) |

---

## 9. Monitoring & Maintenance

### 9.1 Logs

- **Vercel:** Function and build logs in dashboard
- **API host:** Platform log stream; structured JSON recommended
- **PostgreSQL:** Slow query log if p95 degrades

### 9.2 Routine Tasks

| Frequency | Task |
|-----------|------|
| Daily | `git fetch origin && git rebase origin/main` for active branches |
| Weekly | Review dependency security advisories |
| Monthly | Verify DB backup restore on staging |
| On release | Run full test suite; smoke test production |

### 9.3 Incident Response (Brief)

1. Check `/health` and platform status
2. Review recent deployments
3. Roll back if deployment-correlated
4. Communicate to stakeholders; post-mortem for Sev-1

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `npm run dev` fails | Node version | Use Node 20+ |
| Port 3000 in use | Another process | `lsof -i :3000` and stop process |
| PDF analyze 500 | Invalid PDF or parse error | Check server logs; try smaller file |
| API CORS error | Wrong `CORS_ORIGINS` | Add frontend URL to backend env |
| DB connection refused | Docker not running | `docker compose up -d db` |
| 401 on API | Expired JWT | Refresh token flow or re-login |

---

## 11. Environment Matrix

| Environment | Web URL | API URL | Database |
|-------------|---------|---------|----------|
| Local | localhost:3000 | localhost:8000 | local Docker PG |
| Staging | staging.*.vercel.app | staging-api.* | staging PG |
| Production | app.* | api.* | production PG |

---

## 12. Related Documents

- `01-system_architecture.md` — system structure
- `02-technology-selection.md` — hosting choices
- `03-technical-standards.md` — quality gates
- `05-git-workflow-guide.md` — release process via PR

---

## 13. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-19 | Initial operations manual |
