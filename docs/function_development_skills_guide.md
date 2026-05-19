# Cursor Function Development Skills Guide

Based on the uploaded requirements document for the AI Education / Faculty Management SaaS Platform. fileciteturn0file0

---

# 1. Project Positioning

## Product Type
AI-powered education management and academic planning SaaS platform.

## Core Capabilities
- Student management
- Teacher scheduling
- Attendance and leave deduction
- Parent portal
- AI exam analysis
- AI essay analysis
- Cambridge learning planner
- University recommendation system
- Finance and invoicing
- Role-based administration

## Recommended Tech Stack

### Frontend
- React
- Next.js
- TypeScript
- TailwindCSS
- Zustand / Redux
- React Query / TanStack Query

### Backend
- FastAPI (recommended)
- Python
- SQLAlchemy ORM
- Pydantic

### Database
- PostgreSQL

### AI Layer
- OpenAI API
- OCR service
- Embedding search (optional)

### File Storage
- AWS S3

### PDF Generation
- ReportLab

### Deployment
- Docker
- AWS EC2 / Railway / Render
- Nginx

---

# 2. Cursor Development Skills Organization

The following skills should be organized as reusable Cursor workflows.

---

# 3. Core Cursor Skills

# Skill A — Database Schema Generator

## Purpose
Generate PostgreSQL schema and migrations from requirements.

## Responsibilities
- Create SQL tables
- Create relationships
- Create indexes
- Generate foreign keys
- Generate enum types
- Generate migration files

## Cursor Prompt Template

```txt
Generate PostgreSQL schema for the following module:

Requirements:
- Use UUID primary keys
- Include created_at and updated_at
- Add indexes for foreign keys
- Use PostgreSQL enum types
- Generate SQLAlchemy models
- Generate Alembic migration

Module:
{{MODULE_NAME}}
```

## Example Modules
- users
- students
- teachers
- schedules
- attendance
- invoices
- exams
- essays
- teaching_plans

---

# Skill B — FastAPI CRUD Generator

## Purpose
Rapidly generate API endpoints.

## Responsibilities
- CRUD routes
- Validation schemas
- Service layer
- Repository layer
- Error handling
- Pagination
- Authentication hooks

## Cursor Prompt Template

```txt
Generate FastAPI CRUD structure.

Requirements:
- Use FastAPI
- Use SQLAlchemy
- Use async functions
- Use repository pattern
- Use dependency injection
- Include pagination
- Include validation
- Return RESTful responses

Entity:
{{ENTITY_NAME}}
```

## Example Endpoints

### Students
- POST /students
- GET /students
- GET /students/{id}
- PUT /students/{id}
- DELETE /students/{id}

### Schedules
- GET /teachers/{id}/schedule
- POST /schedules
- PATCH /schedules/{id}

### Attendance
- POST /attendance/check-in
- POST /leave-request

---

# Skill C — Authentication & RBAC Generator

## Purpose
Generate secure login and role permission system.

## Roles
- admin
- frontdesk
- teacher
- parent

## Responsibilities
- JWT login
- Password hashing
- Route protection
- Role middleware
- Permission guards
- Session validation

## Cursor Prompt Template

```txt
Build authentication and RBAC system.

Requirements:
- FastAPI
- JWT authentication
- Refresh tokens
- Role-based permissions
- Password hashing with bcrypt
- Middleware authorization
- Protected routes

Roles:
admin
teacher
parent
frontdesk
```

---

# Skill D — Teacher Schedule Engine

## Purpose
Build timetable and scheduling system.

## Responsibilities
- Weekly schedule
- Daily schedule
- Conflict detection
- Reschedule logic
- Leave adjustment
- Notification trigger

## Core Logic

### Conflict Detection
- Teacher unavailable
- Student unavailable
- Duplicate classroom booking

### Schedule Status
- not_started
- in_progress
- completed
- cancelled
- rescheduled

## Cursor Prompt Template

```txt
Build teacher scheduling engine.

Requirements:
- Detect time conflicts
- Weekly recurring schedules
- Reschedule support
- Leave handling
- Classroom assignment
- Generate teacher calendar API
- PostgreSQL support
```

---

# Skill E — Attendance & Deduction Engine

## Purpose
Implement leave and lesson deduction logic.

## Core Rules
- First 2 leaves are free
- After 2 leaves:
  - auto extend semester
  - deduct lesson logic

## Responsibilities
- Attendance records
- Leave approval
- Auto cancellation
- Remaining lesson calculation
- Semester tracking

## Formula

```txt
remaining_lessons = total_lessons - completed_lessons
```

## Cursor Prompt Template

```txt
Build attendance and deduction system.

Rules:
- First 2 leaves are free
- Additional leaves extend course duration
- Support sick leave and personal leave
- Auto calculate remaining lessons
- Generate monthly leave report
```

---

# Skill F — Invoice & Finance Generator

## Purpose
Generate tuition invoices automatically.

## Responsibilities
- Tuition calculation
- Semester invoice generation
- PDF invoices
- Payment tracking
- Credit deduction

## Formula

```txt
final_amount = subtotal - credit
```

## Cursor Prompt Template

```txt
Generate finance and invoice module.

Requirements:
- Semester invoice generation
- PDF export
- Stripe-ready architecture
- Payment status tracking
- Tuition calculation
- Multiple subjects per invoice
```

---

# Skill G — AI Essay Analysis Module

## Purpose
Analyze essays using AI.

## Responsibilities
- Grammar scoring
- Vocabulary analysis
- Sentence structure analysis
- Cohesion analysis
- Rewrite suggestions
- PDF report generation

## AI Output

### Scores
- grammar_score
- vocabulary_score
- structure_score

### Suggestions
- grammar improvements
- advanced vocabulary
- sentence rewrites

## Cursor Prompt Template

```txt
Build AI essay analysis service.

Requirements:
- OpenAI API integration
- Analyze grammar and vocabulary
- Return JSON response
- Generate rewrite suggestions
- Store reports in PostgreSQL
- Generate PDF summary
```

---

# Skill H — AI Exam Analysis Module

## Purpose
Analyze uploaded test papers.

## Responsibilities
- OCR extraction
- Wrong answer detection
- Knowledge point classification
- Weakness analysis
- Improvement plan generation

## Supported Formats
- PDF
- image upload

## Example Categories
- Algebra
- Geometry
- Statistics
- Reading
- Writing

## Cursor Prompt Template

```txt
Build AI exam analysis module.

Requirements:
- OCR support
- Question classification
- Weak topic analysis
- Improvement recommendations
- OpenAI integration
- Generate structured JSON output
```

---

# Skill I — Cambridge Learning Planner

## Purpose
Generate dynamic Cambridge teaching plans.

## Supported Curriculums
- Cambridge Primary
- Lower Secondary
- Checkpoint
- IGCSE
- AS Level
- A Level

## Responsibilities
- Syllabus tracking
- Lesson generation
- Weak topic mapping
- Homework generation
- Dynamic lesson adjustment

## Example Knowledge Points
- Fractions
- Algebra
- Geometry
- Probability

## Cursor Prompt Template

```txt
Build Cambridge learning planner.

Requirements:
- Generate 10-lesson plans
- Track syllabus mastery
- Dynamic lesson adjustment
- Weak topic detection
- Homework generation
- Teacher progress tracking
```

---

# Skill J — Academic Pathway Analyzer

## Purpose
Recommend majors and universities.

## Supported Systems
- NCEA
- IGCSE
- A-Level
- IB

## Responsibilities
- Grade parsing
- Subject analysis
- University matching
- Admission probability
- Career recommendations

## University Regions
- UK
- USA
- Australia
- New Zealand

## Cursor Prompt Template

```txt
Build academic pathway analyzer.

Requirements:
- Parse student reports
- Recommend majors
- Recommend universities
- Analyze admission probability
- Generate application roadmap
- Export PDF report
```

---

# Skill K — Parent Portal Generator

## Purpose
Generate secure parent-facing dashboard.

## Features
- Remaining lessons
- Homework reports
- Teacher feedback
- Attendance history
- AI reports
- Invoice access

## Cursor Prompt Template

```txt
Build parent portal.

Requirements:
- Parent login
- Student dashboard
- Homework reports
- Attendance records
- AI performance reports
- Invoice access
```

---

# Skill L — Admin Dashboard Generator

## Purpose
Generate operational management dashboard.

## Features
- Student statistics
- Teacher statistics
- Revenue analytics
- Today's schedule
- Unpaid invoice alerts
- User management

## Cursor Prompt Template

```txt
Build admin dashboard.

Requirements:
- KPI dashboard
- Revenue charts
- Schedule overview
- User management
- RBAC support
- Analytics APIs
```

---

# 4. Recommended Project Structure

```txt
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── ai/
│   ├── auth/
│   ├── utils/
│   └── main.py
│
├── migrations/
├── tests/
└── requirements.txt

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── stores/
│   ├── layouts/
│   └── utils/
```

---

# 5. Recommended Development Sequence

# Phase 1 — Core SaaS Foundation

Build first:
- authentication
- users
- students
- teachers
- schedules
- attendance
- invoices

## Goal
Operational tutoring center management.

---

# Phase 2 — AI Education Features

Build:
- essay analysis
- exam analysis
- homework reports
- parent portal

## Goal
AI-assisted educational workflow.

---

# Phase 3 — High-Value AI Systems

Build:
- Cambridge learning planner
- academic pathway analyzer
- university recommendation engine

## Goal
AI education planning platform.

---

# 6. Recommended Cursor Rules

## Rule 1
Always generate:
- service layer
- repository layer
- schema layer
- route layer

Never place business logic directly in routes.

---

## Rule 2
All APIs should:
- return typed responses
- use async/await
- support pagination
- include error handling

---

## Rule 3
Use strict naming conventions.

### Example
- student_service.py
- student_repository.py
- student_schema.py
- student_router.py

---

## Rule 4
All AI responses should return structured JSON.

Example:

```json
{
  "strengths": [],
  "weaknesses": [],
  "recommendations": [],
  "score": 85
}
```

---

# 7. Recommended Cursor AI Workflow

## Workflow

### Step 1
Generate database schema.

### Step 2
Generate ORM models.

### Step 3
Generate API endpoints.

### Step 4
Generate frontend forms.

### Step 5
Generate dashboard pages.

### Step 6
Integrate AI services.

### Step 7
Generate reports and PDFs.

---

# 8. Final Recommendation

This project should be treated as:

## AI Education Operating System

Not only:
- scheduling
- tutoring management

But also:
- AI diagnosis
- learning planning
- university pathway planning
- automated reporting

The strongest commercialization modules are:

1. Cambridge Learning Planner
2. Academic Pathway Analyzer
3. AI Exam Analysis
4. AI Essay Analysis

These create the platform differentiation.

---

# 9. Suggested Next Cursor Tasks

Recommended immediate implementation order:

## Sprint 1
- Authentication
- User system
- Student CRUD
- Teacher CRUD

## Sprint 2
- Scheduling engine
- Attendance system
- Leave system

## Sprint 3
- Parent portal
- Invoice system
- Dashboard analytics

## Sprint 4
- AI essay analysis
- AI exam analysis

## Sprint 5
- Cambridge planner
- Academic pathway analyzer

