# Product User Guide — Spinozah AI Education

**Audience:** Tutoring-centre staff, teachers, and parents using the local or deployed web app.  
**Last updated:** 2026-07-24

Companion docs: root [`README.md`](../README.md) (setup), [`04-operations-manual.md`](04-operations-manual.md) (ops/deploy).

---

## 1. Roles

| Role | Typical access |
|------|----------------|
| **admin** | Users, KPIs, all CRUD, finance, parent links |
| **frontdesk** | Students, teachers, enrolments, schedules, invoices, attendance |
| **teacher** | Own timetable, attendance confirmation, leave, AI analysis tools |
| **parent** | Magic-link portal for linked children only |

Staff modules that call FastAPI require a signed-in staff session (JWT). AI modules call Next.js BFF routes and need `OPENAI_API_KEY` on the server.

---

## 2. Staff sign-in

1. Open the app home page.
2. Click **Staff sign in**.
3. Enter **tenant slug**, **email**, and **password**.
4. On success, the auth bar shows your name/role; ops modules can call the API.

Sign out from the same auth bar when finished.

**Tip:** Create additional users under **User Management** (admin). Teachers need a user with role `teacher` plus a teacher profile under **Teacher Management**.

---

## 3. Dashboard modules

### 3.1 Admin Dashboard

- Shows student/teacher counts, revenue summary, and unpaid invoice alerts.
- Requires admin (or staff JWT permitted by the KPI API).

### 3.2 User Management

- List, create, update, and deactivate users in your tenant.
- Roles: `admin`, `frontdesk`, `teacher`, `parent`.
- Parents created here can later be linked to students.

### 3.3 Teacher Management

- Create/edit teacher profiles (linked to a user).
- Required before scheduling lessons for that teacher.

### 3.4 Student Management

- Create and edit students.
- Use together with **Enrolment Management** for lesson packages.

### 3.5 Enrolment Management

- Create enrolments (lesson packages) for a student.
- Adjust remaining lessons when packages change.

### 3.6 Schedule Management

- Create lesson schedules (teacher + student + time slot).
- Conflicts return a clear error (HTTP 409).
- Created items for the current session appear in the local “Created this session” list (staff list endpoint may not expose full history yet).

### 3.7 Teacher Timetable

- Teachers (or staff selecting a teacher) view upcoming lessons.
- Used as the source for attendance schedule picking.

### 3.8 Attendance & Leave

1. Select teacher → lesson date → schedule slot from the timetable (no UUID typing).
2. Confirm attendance / record leave per policy (e.g. leave limits).
3. Leave approvals update remaining lessons according to domain rules.

### 3.9 Finance & Invoice

- List invoices for the tenant; create invoices with semester labels and amounts.
- Unpaid items surface on the Admin Dashboard.

### 3.10 Parent Student Links

1. Ensure a user with role `parent` exists (User Management — admin).
2. Select parent + student and create the link.
3. Parent can then use the Parent Portal for that child.

### 3.11 Parent Portal

1. Enter tenant slug + parent email to request a magic link.
2. Open the link (`/parent/magic-link?...`) to establish a parent session.
3. View linked students’ attendance / remaining lessons / related info.

In local development, check API responses/logs for the magic-link token if email delivery is not configured.

### 3.12 Question Analysis

1. Upload a test paper (PDF/image as supported by the panel).
2. Review extracted text preview.
3. Run analysis for weaknesses / structured feedback.
4. Optionally persist results via FastAPI analyses API (client helpers in `lib/api/analyses.ts`).

### 3.13 AI Reports (Essay)

1. Provide student name, title, and essay text (or upload flow if shown).
2. Generate structured scores and comments.
3. Download PDF when available.

### 3.14 Lesson Planning (Cambridge)

1. Enter student context / weaknesses / curriculum inputs.
2. Generate a structured lesson plan.
3. Review lessons and learning goals before using in class.

### 3.15 University Pathway

1. Choose qualification: **IGCSE**, **A-Level**, **NCEA**, or **IB**.
2. Enter grades / preferences.
3. Generate pathway recommendations.
4. **Download PDF** for sharing with families.

---

## 4. Suggested day-one staff workflow

```text
Sign in as admin
  → User Management (create frontdesk / teacher / parent)
  → Teacher Management + Student Management
  → Enrolment Management (package)
  → Schedule Management (book lessons)
  → Parent Student Links
  → Teacher confirms Attendance
  → Finance creates invoices
  → AI modules for learning insights
```

---

## 5. Deep links

Append `?module=<Module Title>` to the home URL. The title must match the dashboard card exactly, for example:

```text
http://localhost:3000/?module=Enrolment%20Management
http://localhost:3000/?module=University%20Pathway
```

---

## 6. Related technical docs

| Doc | When to read |
|-----|----------------|
| [`04-operations-manual.md`](04-operations-manual.md) | Environment, smoke tests, deploy |
| [`01-system_architecture.md`](01-system_architecture.md) | Bounded contexts |
| [`backend/README.md`](../backend/README.md) | REST API surface |

---

## 7. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-24 | Initial guide after ops + AI productization ship (AIJOB-59…70) |
