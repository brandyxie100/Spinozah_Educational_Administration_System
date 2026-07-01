# Linear Project Plan — Spinozah AI Education

**Linear project:** [Spinozah AI Education](https://linear.app/aipoweredcvprime/project/spinozah-ai-education-a4a8ea19a3ca)  
**Team:** AI-PoweredCVPrime (`AIJOB`)  
**Plan created:** 2026-05-19  
**Last updated:** 2026-05-19 (v1.3)  
**Target delivery:** 2026-11-15  
**Cadence:** One feature per week, anchored from today

This plan is derived from `docs/function_development_skills_guide.md`, `docs/01-system_architecture.md`, and project workflow standards (DDD layers, test-first, bounded contexts).

---

## 0. Project Status (Actual Progress — 2026-05-19)

### Completed (pre-work + local)

| Area | Status | Evidence |
|------|--------|----------|
| Architecture docs | **Complete** | `docs/01`–`05`, this plan |
| Linear backlog | **Complete** | AIJOB-19–54 created |
| Next.js dashboard + module stubs | **Complete** | `app/page.tsx` |
| Environment | **Complete** | `.env.example`, `.env.local` |
| Test tooling | **Complete** | Jest, Zod, OpenAI SDK on `feature/ai-analysis-exam-pipeline` |
| Exam Analysis MVP (local) | **Complete** | `lib/ai-analysis/`, 15 tests, API, UI — PR pending |
| Linear issues marked **Done** | **0 of 36** | AIJOB-49 In Progress; merge + mark Done in Week 1 |

### Not started

| Area | Status |
|------|--------|
| `backend/` FastAPI | Not started |
| CI in GitHub Actions | Not started |
| All platform features (W2+) | Not started |

### Linear workflow snapshot (synced 2026-05-19)

| Linear status | Count | Notes |
|---------------|-------|-------|
| **Done** | 0 | Mark AIJOB-49 Done when Week 1 PR merges |
| **In Progress** | 1 | **AIJOB-49** — exam analysis MVP (due May 25) |
| **Todo** | 13 | Due dates updated to weekly plan W2–W26 |
| **Backlog** | 22 | Epic due dates updated |

**All 36 issues** due dates synced to weekly plan (v1.3). Project target: **Nov 15, 2026**.

**Active branch:** `feature/ai-analysis-exam-pipeline` (AIJOB-49).

---

## 1. Executive Summary

| Item | Value |
|------|-------|
| **Phases** | 3 product phases → 5 milestones → **26 weekly features** |
| **Epics** | 10 (AIJOB-19 … AIJOB-28) |
| **Granular issues** | 26 tasks (AIJOB-29 … AIJOB-54) |
| **Total estimate** | ~155 story points |
| **Cadence** | **One shippable feature per week** (Mon–Sun) |
| **Week 1 (current)** | AIJOB-49 — Exam Analysis MVP (PR + Done) |
| **Platform critical path** | AIJOB-33 → AIJOB-32 → AIJOB-29 → AIJOB-31 → AIJOB-35 → … → AIJOB-53 |

---

## 2. Milestones & Timeline

Re-anchored from **2026-05-19**. Each week delivers one primary feature.

| Milestone | Target date | Weeks | Goal |
|-----------|-------------|-------|------|
| **Pre-work** | 2026-05-18 | Pre | Docs, UI shell, env, Linear — **complete** |
| **M-A — Exam Analysis MVP** | 2026-05-25 | W1 | Testable exam/question analysis (Next.js) |
| **M0 — Foundation & DevEx** | 2026-06-22 | W2–W6 | CI, FastAPI DDD, DB, Docker, tenant isolation |
| **M1 — Core SaaS Operations** | 2026-09-21 | W7–W18 | Auth, students, scheduling, attendance |
| **M2 — AI Education & Parent Portal** | 2026-10-26 | W19–W23 | Finance, parent portal, admin, essay AI |
| **M3 — AI Planning Platform** | 2026-11-15 | W24–W26 | Cambridge planner, university pathway |

---

## 3. Weekly Feature Calendar (from 2026-05-19)

One primary feature per week. Due date = **Sunday** of each week.

| Week | Dates | Feature | Linear | Milestone | Status |
|------|-------|---------|--------|-----------|--------|
| **W1** | May 19 – May 25 | **Exam Analysis MVP** — PR, merge, mark Done | AIJOB-49 | M-A | **Current** |
| **W2** | May 26 – Jun 1 | **CI baseline** — GitHub Actions lint/test/build | AIJOB-33 | M0 | Planned |
| **W3** | Jun 2 – Jun 8 | **FastAPI DDD scaffold** | AIJOB-32 | M0 | Planned |
| **W4** | Jun 9 – Jun 15 | **PostgreSQL schema + Alembic** | AIJOB-29 | M0 | Planned |
| **W5** | Jun 16 – Jun 22 | **Docker Compose local stack** | AIJOB-30 | M0 | Planned |
| **W6** | Jun 23 – Jun 29 | **Multi-tenant repository + isolation tests** | AIJOB-31 | M0 | Planned |
| **W7** | Jun 30 – Jul 6 | **Frontend API client + TanStack Query** | AIJOB-34 | M0 | Planned |
| **W8** | Jul 7 – Jul 13 | **JWT auth + refresh flow** | AIJOB-35 | M1 | Planned |
| **W9** | Jul 14 – Jul 20 | **RBAC middleware** | AIJOB-36 | M1 | Planned |
| **W10** | Jul 21 – Jul 27 | **User management CRUD** | AIJOB-38 | M1 | Planned |
| **W11** | Jul 28 – Aug 3 | **Student schema + domain model** | AIJOB-37 | M1 | Planned |
| **W12** | Aug 4 – Aug 10 | **Student CRUD API** | AIJOB-39 | M1 | Planned |
| **W13** | Aug 11 – Aug 17 | **Teacher CRUD API** | AIJOB-40 | M1 | Planned |
| **W14** | Aug 18 – Aug 24 | **Student Management UI** | AIJOB-41 | M1 | Planned |
| **W15** | Aug 25 – Aug 31 | **Schedule schema + recurrence engine** | AIJOB-42 | M1 | Planned |
| **W16** | Sep 1 – Sep 7 | **Conflict detection service** | AIJOB-43 | M1 | Planned |
| **W17** | Sep 8 – Sep 14 | **Teacher Timetable UI** | AIJOB-44 | M1 | Planned |
| **W18** | Sep 15 – Sep 21 | **Attendance check-in** | AIJOB-45 | M1 | Planned |
| **W19** | Sep 22 – Sep 28 | **Leave policy engine** | AIJOB-47 | M1 | Planned |
| **W20** | Sep 29 – Oct 5 | **Invoice generation + PDF** | AIJOB-46 | M2 | Planned |
| **W21** | Oct 6 – Oct 12 | **Magic-link parent auth** | AIJOB-51 | M2 | Planned |
| **W22** | Oct 13 – Oct 19 | **Parent dashboard APIs** | AIJOB-48 | M2 | Planned |
| **W23** | Oct 20 – Oct 26 | **Admin KPI dashboard** | AIJOB-50 | M2 | Planned |
| **W24** | Oct 27 – Nov 2 | **AI essay analysis** | AIJOB-52 | M2 | Planned |
| **W25** | Nov 3 – Nov 9 | **Cambridge learning planner** | AIJOB-54 | M3 | Planned |
| **W26** | Nov 10 – Nov 15 | **University pathway engine** | AIJOB-53 | M3 | Planned |

---

## 4. Bounded Contexts (Issue Scopes)

| Module | Responsibility |
|--------|----------------|
| `shared` | Scaffold, DB, Docker, CI, multi-tenant base |
| `identity` | Auth, users, RBAC |
| `students` | Students, teachers, enrolment |
| `scheduling` | Timetables, conflicts |
| `attendance` | Check-in, leave policy |
| `finance` | Invoices, payments |
| `parent-portal` | Parent auth & views |
| `ai-analysis` | Exam, essay, OCR/LLM |
| `planning` | Cambridge planner, university pathway |
| `frontend` | Next.js UI modules |

**Issue title format:** `[p{n}][{Type}][{module}] {title}`

---

## 5. Epic Breakdown (Parent Issues)

| ID | Epic | Milestone | Week window | Linear |
|----|------|-----------|-------------|--------|
| AIJOB-26 | AI Exam & Essay Analysis | M-A / M2 | W1, W24 | Backlog |
| AIJOB-19 | M0 Foundation & DevEx | M0 | W2 – W7 | Backlog |
| AIJOB-20 | Authentication & RBAC | M1 | W8 – W10 | Backlog |
| AIJOB-21 | Students & Teachers CRUD | M1 | W11 – W14 | Backlog |
| AIJOB-22 | Teacher Scheduling Engine | M1 | W15 – W17 | Backlog |
| AIJOB-23 | Attendance & Leave System | M1 | W18 – W19 | Backlog |
| AIJOB-24 | Finance & Invoicing | M2 | W20 | Backlog |
| AIJOB-25 | Parent Portal | M2 | W21 – W22 | Backlog |
| AIJOB-28 | Admin Dashboard & KPIs | M2 | W23 | Backlog |
| AIJOB-27 | Learning & University Planning | M3 | W25 – W26 | Backlog |

---

## 6. Granular Task Catalog

### Linear status legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Backlog |
| `[T]` | Todo |
| `[~]` | In Progress |
| `[x]` | Done |

### Week 1 — Exam Analysis MVP (parent: AIJOB-26) — **CURRENT**

| Step | Task | Due | Linear | Local |
|------|------|-----|--------|-------|
| 1 | Tooling: Jest, Zod, OpenAI SDK | May 20 | — | **Done** |
| 2 | Failing tests (schema, extract, analyzer, route) | May 21 | — | **Done** |
| 3 | `lib/ai-analysis/` implementation | May 22 | — | **Done** |
| 4 | `POST /api/ai/exams/analyze` | May 23 | — | **Done** |
| 5 | Question Analysis UI (remove mock) | May 24 | — | **Done** |
| 6 | Verify + PR; mark AIJOB-49 Done | **May 25** | AIJOB-49 `[~]` | Pending PR |

### Weeks 2–26 — Feature queue (one per week)

| Week | ID | Task | Est. | Due | Linear | Blocked by |
|------|----|------|------|-----|--------|------------|
| W2 | AIJOB-33 | GitHub Actions CI baseline | 3 | Jun 1 | `[T]` | AIJOB-49 |
| W3 | AIJOB-32 | FastAPI DDD project scaffold | 3 | Jun 8 | `[T]` | AIJOB-33 |
| W4 | AIJOB-29 | PostgreSQL schema + Alembic baseline | 5 | Jun 15 | `[ ]` | AIJOB-32 |
| W5 | AIJOB-30 | Docker Compose local dev stack | 2 | Jun 22 | `[T]` | AIJOB-32 |
| W6 | AIJOB-31 | Multi-tenant repository + isolation tests | 3 | Jun 29 | `[ ]` | AIJOB-29 |
| W7 | AIJOB-34 | API client + TanStack Query setup | 2 | Jul 6 | `[ ]` | AIJOB-32 |
| W8 | AIJOB-35 | JWT auth + refresh flow | 5 | Jul 13 | `[T]` | AIJOB-31 |
| W9 | AIJOB-36 | RBAC middleware | 3 | Jul 20 | `[T]` | AIJOB-35 |
| W10 | AIJOB-38 | User management CRUD | 3 | Jul 27 | `[ ]` | AIJOB-36 |
| W11 | AIJOB-37 | Student schema + domain | 3 | Aug 3 | `[ ]` | AIJOB-29, AIJOB-35 |
| W12 | AIJOB-39 | Student CRUD API | 5 | Aug 10 | `[ ]` | AIJOB-37 |
| W13 | AIJOB-40 | Teacher CRUD API | 3 | Aug 17 | `[ ]` | AIJOB-37 |
| W14 | AIJOB-41 | Student Management UI | 5 | Aug 24 | `[ ]` | AIJOB-39, AIJOB-34 |
| W15 | AIJOB-42 | Schedule schema + recurrence | 5 | Aug 31 | `[ ]` | AIJOB-39, AIJOB-40 |
| W16 | AIJOB-43 | Conflict detection service | 5 | Sep 7 | `[ ]` | AIJOB-42 |
| W17 | AIJOB-44 | Teacher Timetable UI | 5 | Sep 14 | `[ ]` | AIJOB-42, AIJOB-34 |
| W18 | AIJOB-45 | Attendance check-in | 5 | Sep 21 | `[T]` | AIJOB-42, AIJOB-39 |
| W19 | AIJOB-47 | Leave policy engine | 8 | Sep 28 | `[ ]` | AIJOB-45 |
| W20 | AIJOB-46 | Invoice generation + PDF | 8 | Oct 5 | `[T]` | AIJOB-39, AIJOB-23 |
| W21 | AIJOB-51 | Magic-link parent auth | 5 | Oct 12 | `[T]` | AIJOB-36 |
| W22 | AIJOB-48 | Parent dashboard APIs | 5 | Oct 19 | `[T]` | AIJOB-51, AIJOB-45, AIJOB-46 |
| W23 | AIJOB-50 | Admin KPI dashboard | 8 | Oct 26 | `[T]` | AIJOB-46, AIJOB-42 |
| W24 | AIJOB-52 | AI essay analysis | 8 | Nov 2 | `[T]` | AIJOB-49 |
| W25 | AIJOB-54 | Cambridge learning planner | 13 | Nov 9 | `[T]` | AIJOB-52, AIJOB-49 |
| W26 | AIJOB-53 | University pathway engine | 13 | Nov 15 | `[T]` | AIJOB-54 |

*Update Linear due dates to each week's Sunday when the week begins.*

---

## 7. Dependency Graph

### 7.1 Weekly execution track

```mermaid
flowchart LR
    W1[W1 Exam MVP]
    W2[W2 CI]
    W3[W3 FastAPI]
    W4[W4 DB]
    W5[W5 Docker]
    W6[W6 Tenant]
    W7[W7 API Client]
    W8[W8 JWT]
    W9[W9 RBAC]
    W10[W10 Users]
    W11[W11 Student Domain]
    W12[W12 Student API]
    W13[W13 Teacher API]
    W14[W14 Student UI]
    W15[W15 Scheduling]
    W16[W16 Conflicts]
    W17[W17 Timetable UI]
    W18[W18 Attendance]
    W19[W19 Leave]
    W20[W20 Finance]
    W21[W21 Parent Auth]
    W22[W22 Parent APIs]
    W23[W23 Admin KPI]
    W24[W24 Essay AI]
    W25[W25 Cambridge]
    W26[W26 University]

    W1 --> W2 --> W3 --> W4 --> W5 --> W6 --> W7
    W6 --> W8 --> W9 --> W10 --> W11 --> W12 --> W13 --> W14
    W13 --> W15 --> W16 --> W17 --> W18 --> W19 --> W20
    W9 --> W21 --> W22
    W15 --> W23
    W1 --> W24 --> W25 --> W26
```

### 7.2 Active critical path (Week 1 — now)

```
PR merge → mark AIJOB-49 Done → start W2 (AIJOB-33 CI)
```

### 7.3 Platform critical path

```
AIJOB-33 → AIJOB-32 → AIJOB-29 → AIJOB-31 → AIJOB-35 → AIJOB-37 → AIJOB-39
  → AIJOB-42 → AIJOB-45 → AIJOB-46 → AIJOB-52 → AIJOB-54 → AIJOB-53
```

---

## 8. Priority Matrix

| Priority | Meaning | Active examples |
|----------|---------|-----------------|
| **p1 / Urgent** | Current week | AIJOB-49 — PR + Done by May 25 |
| **p2 / High** | Next 4 weeks | AIJOB-33, 32, 29, 30 |
| **p3 / Medium** | UI polish weeks | AIJOB-34, 41, 44 |

---

## 9. Development Standards (Per Issue)

1. **Branch** from `main`: `feature/{module}-{description}`
2. **Tests first** — failing tests before implementation
3. **DDD layers** for platform; layered `lib/` for Next.js MVP
4. **Tenant test** for any new repository
5. **PR** < 800 lines, Conventional Commits, CI green
6. **One feature per week** — ship and mark Linear Done before starting the next

See `docs/05-git-workflow-guide.md`.

---

## 10. Skill Guide Mapping

| Cursor skill | Linear tasks | Week |
|--------------|--------------|------|
| Skill G/H — AI analysis | AIJOB-49, 52 | W1, W24 |
| Skill A — DB schema | AIJOB-29, 37, 42 | W4, W11, W15 |
| Skill B — FastAPI CRUD | AIJOB-39, 40, 38 | W10, W12, W13 |
| Skill C — Auth & RBAC | AIJOB-35, 36, 38 | W8, W9, W10 |
| Skill D — Scheduling | AIJOB-42, 43, 44 | W15, W16, W17 |
| Skill E — Attendance | AIJOB-45, 47 | W18, W19 |
| Skill F — Finance | AIJOB-46 | W20 |
| Skill K — Parent portal | AIJOB-51, 48 | W21, W22 |
| Skill L — Admin dashboard | AIJOB-50 | W23 |
| Phase 3 planning | AIJOB-54, 53 | W25, W26 |

---

## 11. Recommended Start Order (from 2026-05-19)

| Week | Action | Due | Linear |
|------|--------|-----|--------|
| **W1** | Open PR for exam analysis MVP; merge; mark Done | May 25 | AIJOB-49 |
| **W2** | GitHub Actions: lint, test, build on every PR | Jun 1 | AIJOB-33 |
| **W3** | FastAPI DDD scaffold + health endpoint | Jun 8 | AIJOB-32 |
| **W4** | PostgreSQL schema + Alembic baseline | Jun 15 | AIJOB-29 |
| **W5** | Docker Compose (API + DB + frontend) | Jun 22 | AIJOB-30 |

Then continue W6–W26 per §3 calendar.

**Weekly ritual:** Monday — set one issue In Progress; Sunday — PR merged + Linear Done.

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Week 1 PR not merged by May 25 | W2+ slips | Ship AIJOB-49 PR first; defer polish |
| One feature/week too aggressive for 8-pt tasks | Schedule slip | Split large issues (AIJOB-54/53) across buffer days within the week |
| Linear due dates stale | Wrong prioritization | Refresh due dates every Monday |
| 0 Linear Done issues | No velocity signal | Mark AIJOB-49 Done when W1 PR merges |
| CI added in W2 | W1 PR lacks CI gate | Manual verify (lint, tsc, test, build) for W1 |

---

## 13. Linear Links Quick Reference

- **Project:** https://linear.app/aipoweredcvprime/project/spinozah-ai-education-a4a8ea19a3ca
- **Active task:** https://linear.app/aipoweredcvprime/issue/AIJOB-49 (In Progress — finish by May 25)
- **Parent epic:** https://linear.app/aipoweredcvprime/issue/AIJOB-26
- **Next up:** https://linear.app/aipoweredcvprime/issue/AIJOB-33 (W2 — CI baseline)

---

## 14. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-19 | Initial plan synced to Linear AIJOB-19–54 |
| 1.1 | 2026-06-02 | Rebased: Track A exam MVP first; M0–M3 shifted |
| 1.2 | 2026-06-24 | Synced Linear snapshot; 2-week sprints |
| 1.3 | 2026-05-19 | **Weekly cadence:** one feature per week from today; 26-week calendar W1–W26; target Nov 15; reflects exam MVP local completion |
| 1.3.1 | 2026-05-19 | Synced all Linear issue due dates, epic due dates, project target, and milestone dates to weekly plan |
