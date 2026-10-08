# Recreation and bookstore decisions - 2026-10-08 (1:01 AM)

Status: decisions only. No schema, data, or code changes. Working branch: feature/workbench-data-bridge.

## Confirmed
- Variable-length activities via minimum, step, and maximum duration (bookstore: 20-minute steps up to 4 hours).
- Named effect-level scale in a lookup table; values set once by the user.
- Cafe is a randomized boolean on generated recreation places; any recreation place can potentially have one; no separate place type.
- Coffee is available anywhere food is available and restores some energy.
- One book per agent; any bookstore trip gives a new book if none; random 3 to 18 hours total reading; read anywhere off duty at lower benefit; destroyed when finished with dusty-bookshelf text.
- Buying books is covered by visiting.
- Bookstore energy requirement: 20 (0 to 100 scale).

## Proposed
- Duration step and maximum fields; effect_levels table; cafe_possible on place types; place-independent reading activity with book prerequisite; coffee model; Buy Books deprecated.

## Open
- Energy to read anywhere, level names and values, cafe probability, book type text, finish benefit, coffee model.

## Files touched
- Appended a section to docs\workbench\spec\DESIGN_DECISIONS_2026-10-07.md. Created this file.
- Backup: tools\doda_content_workbench\backups\v041_docs_recreation_<timestamp>
