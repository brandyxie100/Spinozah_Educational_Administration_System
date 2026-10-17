# Soft River UI — Spinozah home redesign

**Status:** Approved 2026-10-17  
**Approach:** Workflow lanes (A) + Soft river visual (1)  
**Theme accent:** Orange `#EA580C`

## Goals

- Show all existing functions without a rigid identical-card grid.
- Clear, easy to scan (ADHD-friendly).
- Orange as accent only; warm canvas, dark ink for contrast.
- No rewrite of feature logic; shell + home only in first pass.

## Color tokens

| Token | Value | Use |
|-------|--------|-----|
| `--sp-canvas` | `#FFF8F3` | Page background |
| `--sp-surface` | `#FFFFFF` | Content panels |
| `--sp-ink` | `#1C1917` | Primary text |
| `--sp-muted` | `#78716C` | Secondary text |
| `--sp-orange` | `#EA580C` | Accent / CTA / focus |
| `--sp-orange-soft` | `#FFEDD5` | Hover wash |
| `--sp-hairline` | `#E7E5E4` | Separators |

## Home structure

Lanes (top → bottom):

1. **Overview** — Admin Dashboard  
2. **People** — User Management, Teacher Management, Student Management, Parent Student Links  
3. **Schedule** — Schedule Management, Teacher Timetable, Enrolment Management  
4. **Attendance** — Attendance & Leave  
5. **Money** — Finance & Invoice  
6. **AI insights** — Question Analysis, AI Reports, Lesson Planning, University Pathway, Parent Portal  

Actions are soft chips (uneven widths), not card tiles. Search filters chips.

## Module shell

Warm canvas, orange primary buttons, dark titles. Existing forms/lists unchanged.

## Typography

- Display: Fraunces  
- UI/body: DM Sans  

## Motion

Lane fade-in; chip hover to orange-soft; orange focus ring.

## Out of scope (v1)

Dark mode; redesigning every form field; new features.
