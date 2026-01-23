# Finanzapp – Development Backlog

This backlog tracks planned work after the v1.0.1 release.
The focus is on stability, clarity, and incremental improvement. Items may be refined or re‑prioritized over time.

---

## P1 – Short Term (Stability & Usability)

* Introduce "last edited" information on all pages
* Integrate or link the User Guide into the InfoPage
* Clarify separation of development and production configuration (ENV handling)
* Improve frontend error handling and user feedback (API errors, empty states)
* Define and document consistent API path conventions

---

## P2 – Quality & Architecture

* Unify REST naming conventions (hyphens vs. underscores)
* Introduce backend tests for core business logic
* Define a basic backend logging strategy
* Review data model edge cases (history, recalculation logic)

---

## P3 – Tooling & Future Improvements

* Migrate frontend toolchain from Vue CLI to Vite
* Introduce a dedicated development environment setup
* Add CI pipeline (linting, tests)
* Extend analytics (categories, trends, historical comparisons)
* make changes in feste Ausgaben more visible, which items changed when in this year, maybe with history
* show sum of all not yet balanced unplaned expenses for each month and overall up until this month
* Ich möchte noch ein Übersicht für die Monate hinzufügen, dort will ich sehen wie der Monat lief, also: Wie hoch waren einnahmen und ausgaben fest/ungeplant
	
* Noch ein Datum beim Einfügen der variablen/ungeplanten Ausgaben hinzufügen im Hintergrund und die Daten danach sortieren. 
* In der Jahresübersicht aufräumen und irgendwo noch die Verknüpfung zum aktuellen Kontostand zum "Soll-Kontostand"
* Verbesserung UI "feste Posten"
* Wo eine Änderung über die Zeit gemacht wurde, soll man die Historie auch sehen können
* Anzeige der Betragshistorie

---

## Notes

* `main` represents a stable, deployable state
* Active development happens exclusively on `dev`
* Releases are created only from `main`
