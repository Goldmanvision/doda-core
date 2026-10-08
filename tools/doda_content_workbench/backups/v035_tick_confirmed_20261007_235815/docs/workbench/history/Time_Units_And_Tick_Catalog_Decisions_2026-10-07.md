# Time units and tick catalog decisions - 2026-10-07 (late evening)

Status: decisions only. No schema, data, or code changes. Working branch: feature/workbench-data-bridge.

## Reference facts
- Doom and ZDoom-family engines run game logic at 35 tics per second; a tic is about 28.57 ms. Actor logic is tic-based; UI drawing is not.
- DoDA sim ticks are a separate unit used for authored per-tick rates.

## Confirmed
- Fixed global sim tick; signed decimal per-tick rates; whole-tick durations; constant rates for now (PCARE-11, PCARE-12, PCARE-13).
- Global time settings live in their own catalog; activity-specific rates stay in the activity catalogs (TIME-01).
- Doom tics and DoDA sim ticks are distinct (TIME-02).
- Decimal authoring, four-decimal cap, scaled-integer export (TIME-03).
- Metrics sampling policy logged as an open reconciliation item (TIME-04).

## Proposed
- One sim tick = one strategic minute (PCARE-OPEN-07).
- A global time-settings catalog (TIME-05).

## Open
- Doom tics per strategic minute at normal speed.
- UZDoom 5.0 tic rate check against local source.
- Metrics sampling versus the sim tick unit.

## Files touched
- Appended a section to docs\workbench\spec\DESIGN_DECISIONS_2026-10-07.md.
- Created this file.
- Backup: tools\doda_content_workbench\backups\v034_docs_time_units_<timestamp>
