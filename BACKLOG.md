# Finanzapp – Development Backlog

This backlog tracks planned work after the v1.0.1 release.
The focus is on stability, clarity, and incremental improvement. Items may be refined or re-prioritized over time.

---

## P1 – Short Term (Stability & Core Functionality)

### Data change tracking (foundation)

* Track and display **last data modification timestamp** for the monthly overview

  * Timestamp reflects the **last create/update/delete** action affecting the month
  * Backend-derived (not UI reload time)
  * Displayed read-only in the monthly view

* Prepare groundwork for future change history (timestamps available per entity)

### UX & Structure

* Integrate or link the User Guide into the InfoPage
* Clarify separation of development and production configuration (ENV handling)
* Improve frontend error handling and user feedback (API errors, empty states)
* Define and document consistent API path conventions

---

## P2 – Quality & Architecture

### Backend & Data Model

* Unify REST naming conventions (hyphens vs. underscores)
* Introduce backend tests for core business logic
* Define a basic backend logging strategy
* Review data model edge cases (history, recalculation logic)

### Change visibility

* Make changes in fixed expenses/income more visible (what changed and when)
* Introduce entity-level modification timestamps (created_at / updated_at)

---

## P3 – Tooling, Analytics & Long-Term Improvements

### Tooling

* Migrate frontend toolchain from Vue CLI to Vite
* Introduce a dedicated development environment setup
* Add CI pipeline (linting, tests)

### Analytics & Insights

* Extend analytics (categories, trends, historical comparisons)
* Monthly overview summary: fixed vs. variable income/expenses
* Show sum of all not-yet-balanced unplanned expenses per month and cumulative up to current month

### History & Archiving

* Add internal timestamp when creating unplanned/variable expenses and sort by it
* Show amount history over time
* Display change history where values changed over time
* Archive old fixed income/expense items (hide from current lists, keep historical access)

### UI Improvements

* Improve UI for fixed items (clarity, editing, visibility)
* Clean up yearly overview and link actual account balance with calculated target balance

---

## Notes

* `main` represents a stable, deployable state
* Active development happens exclusively on `dev`
* Releases are created only from `main`

