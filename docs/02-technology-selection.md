# Technology Selection — Faculty Management System

## 1. Document Purpose

This document records **technology choices** for the Spinozah AI Education (Faculty Management) platform. Given **limited user scale** (single or few tutoring centers, tens to low hundreds of concurrent users), selections prioritize **lightweight tooling**, **low operational overhead**, and **ease of maintenance** over premature scale-out.

---

## 2. Selection Principles

| Principle | Implication |
|-----------|-------------|
| **Boring is good** | Prefer widely adopted frameworks with strong docs |
| **Monolith first** | Single deployable API + web app; no microservices until proven need |
| **Managed where cheap** | Use hosted DB/PaaS before self-managed Kubernetes |
| **Pay for scale later** | Avoid Redis clusters, message buses, and multi-region until required |
| **Type safety** | TypeScript (frontend) + Python typing + mypy (backend) |
| **AI as adapter** | OpenAI behind infrastructure layer; swappable provider |

---

## 3. Summary Matrix

| Concern | Selected | Alternatives Considered | Why Selected |
|---------|----------|-------------------------|--------------|
| **Web framework** | Next.js 16 (App Router) | Remix, Vite+React SPA | SSR/SSG optional, API routes for BFF, strong ecosystem |
| **UI** | React 19 + Tailwind CSS 4 | MUI, Chakra | Utility-first, small bundle, fast iteration |
| **API (backend)** | FastAPI (Python 3.11+) | Django REST, Node Express | Async, OpenAPI auto-docs, fits AI/ML ecosystem |
| **ORM** | SQLAlchemy 2.x (async) | Django ORM, Prisma | Explicit repositories, DDD-friendly |
| **Validation** | Pydantic v2 | Marshmallow | Native FastAPI integration |
| **Database** | PostgreSQL 15+ | MySQL, SQLite | JSON support, reliability, SaaS multi-tenant |
| **Migrations** | Alembic | Flyway, raw SQL | Standard with SQLAlchemy |
| **Auth** | JWT + bcrypt | Session-only cookies, Auth0 | Simple for small team; Auth0 if SSO needed later |
| **AI** | OpenAI API (single-shot BFF) | Azure OpenAI, Anthropic, Deep Agents | Quality + structured JSON for analyzers; Deep Agents only for multi-step orchestration prototypes (`scripts/deep-agents/`) |
| **OCR** | Tesseract.js (client/proto), server OCR later | Google Vision | Cost control at low volume |
| **PDF parse** | pdf-parse (Node), ReportLab (Python reports) | PyPDF2 only | Match current prototype + Python reporting |
| **File storage** | AWS S3 (or compatible: R2, MinIO dev) | Local disk only | Durable uploads for exams/essays |
| **PDF reports** | ReportLab | WeasyPrint | Python-native invoice/report generation |
| **Payments (future)** | Stripe-ready schema | PayPal | Industry standard for tuition billing |
| **Containerization** | Docker + docker-compose | Bare metal | Reproducible dev/prod |
| **Hosting** | Vercel (frontend) + Railway/Render/Fly.io (API+DB) | AWS EC2 full stack | Minimal ops for small scale |
| **Reverse proxy** | Platform-native (Vercel) / Caddy or Nginx on VPS | Traefik | Only if self-hosting API |
| **CI** | GitHub Actions | CircleCI | Free for OSS/small teams |
| **Issue tracking** | Linear | Jira | Lightweight product workflow |
| **State (frontend)** | TanStack Query (+ light React state) | Redux | Server state via Query; session helpers for JWT |
| **Client state** | Zustand (optional, small slices) | Redux Toolkit | Simpler than Redux for local UI state |
| **Testing (backend)** | pytest + factory_boy | unittest | Fast fixtures, DDD test naming |
| **Testing (frontend)** | Jest + React Testing Library + MSW | Playwright-only | Unit/integration first; E2E for critical paths |
| **Lint/format (Python)** | Ruff + mypy strict | black+flake8 | Single fast tool |
| **Lint/format (TS)** | ESLint + Prettier + tsc strict | Biome only | Matches Next.js defaults |

---

## 4. Layer-by-Layer Rationale

### 4.1 Frontend — Next.js + React + TypeScript

**Why Next.js at small scale:**

- One repository can serve UI and thin BFF routes (`app/api/*`) during early development
- Built-in routing, fonts, and deployment on Vercel
- Easy path to split `frontend/` folder when backend grows

**Why not a separate SPA only:**

- Extra deployment and CORS configuration without benefit at current size

**Current dependencies (repo):** `next@16`, `react@19`, `tailwindcss@4`, `@tanstack/react-query`, `openai`, `zod`, `pdf-parse`, `tesseract.js`.

---

### 4.2 Backend — FastAPI + SQLAlchemy

**Why FastAPI:**

- Automatic OpenAPI schema for frontend contract
- Native async for I/O-bound AI and DB calls
- Python ecosystem for ReportLab, data processing, future ML

**Why not Django:**

- Heavier ORM opinions conflict with strict DDD layering
- Acceptable alternative if team is Django-only — would adjust domain layout

**Why not Node backend:**

- Duplicates language; Python better for PDF/report and AI scripting

---

### 4.3 Database — PostgreSQL

**Why PostgreSQL:**

- ACID transactions for billing and attendance
- `UUID`, `ENUM`, `JSONB` for flexible AI report payloads
- Row-level security available if tenant isolation tightens

**Why not SQLite in production:**

- Concurrent writes from multiple staff; PostgreSQL is still low-cost managed

**Why not MongoDB:**

- Relational model fits students ↔ schedules ↔ invoices; avoid dual consistency models

---

### 4.4 AI & Document Processing

| Capability | Tool | Notes |
|------------|------|-------|
| LLM analysis | OpenAI API (GPT-4o / mini class) | Single-shot JSON + Zod in `lib/ai-analysis/`; `OPENAI_MODEL` override; usage logged as `[ai-usage]` |
| PDF text extract | pdf-parse (Node route) → move to Python | Prototype in `app/api/analyze` |
| OCR (images) | Tesseract.js / pytesseract | Use server-side for production |
| Report PDF | ReportLab | Invoices, analysis reports |
| Multi-step agent lab | Deep Agents (`deepagents`) | Exam→plan prototype only — see `docs/07-deep-agents-decision-guide.md` |

**Deferred at small scale:**

- Vector DB / embedding search — add when knowledge-base search is required
- Self-hosted models — cost and ops exceed benefit for few centers
- Production Deep Agents orchestration — promote only after token/quality comparison vs two-shot baseline (`npm run deep-agents:compare`)

---

### 4.5 Infrastructure & Deployment

**Recommended small-team topology:**

```text
[Browser] → [Vercel: Next.js]
                ↓ HTTPS
            [Railway/Render: FastAPI]
                ↓
            [Managed PostgreSQL]
                ↓
            [S3 bucket: uploads]
```

**Why Vercel + PaaS API:**

- Zero server patching for frontend
- One-click previews per PR
- API platform handles TLS and scaling to ~100s RPS

**Why not Kubernetes:**

- Operational cost exceeds benefit for &lt; 1k users

**Docker role:**

- `docker-compose` for local PostgreSQL + API
- Optional single VPS with compose for cost-sensitive production

---

### 4.6 Authentication

**Selected:** JWT access token (memory) + refresh token (httpOnly cookie) + bcrypt password hashing.

**Why not localStorage tokens:** XSS risk.

**When to upgrade:** Auth0 / Clerk / Entra ID if enterprise SSO or parent magic-link provider integration centralizes auth.

---

### 4.7 Observability & Ops (Minimal)

| Tool | Use |
|------|-----|
| Platform logs | Vercel/Railway built-in |
| Sentry (optional) | Error tracking when in production |
| Uptime monitor | Free tier ping on `/health` |

**Deferred:** Datadog, ELK, Kafka.

---

## 5. Explicit Non-Selections (YAGNI)

The following are **intentionally excluded** until scale or requirements demand them:

| Technology | Reason to defer |
|------------|-----------------|
| Microservices | Monolith + bounded contexts sufficient |
| Kubernetes | Ops burden |
| Redis | PostgreSQL handles session/cache at small scale |
| RabbitMQ / Kafka | In-process events or DB outbox later |
| Elasticsearch | PostgreSQL full-text + JSONB first |
| GraphQL | REST + OpenAPI simpler for small team |
| Multiple databases | One PostgreSQL instance |
| Mobile native apps | Responsive web first |

---

## 6. Environment & Configuration

- **12-factor:** All secrets via environment variables
- **Python:** `pydantic-settings` for typed config
- **Node:** `.env.local` (never committed); example in `.env.example`
- **No secrets in repo**

---

## 7. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI cost spikes | Rate limits per tenant; cache analysis results |
| Vendor lock-in (OpenAI) | Adapter interface in infrastructure |
| Single DB failure | Managed DB backups; daily snapshots |
| Next.js + FastAPI CORS | Shared API domain or BFF proxy |

---

## 8. Decision Review Triggers

Revisit this document when:

- Active tenants &gt; 50 or MAU &gt; 5,000
- p95 API latency &gt; 500ms sustained
- Compliance requires region-specific AI (→ Azure OpenAI)
- Payment volume requires dedicated PCI scope review (→ Stripe Elements)

---

## 9. Related Documents

- `01-system_architecture.md` — where each technology sits in layers
- `03-technical-standards.md` — how to use the stack consistently
- `04-operations-manual.md` — running the system locally and in production

---

## 10. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-19 | Initial lightweight stack selection |
