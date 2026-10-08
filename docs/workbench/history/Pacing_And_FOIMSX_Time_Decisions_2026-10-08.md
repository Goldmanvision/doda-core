# Pacing and FOIMS-X time decisions - 2026-10-08 (12:15 AM)

Status: decisions only. No schema, data, or code changes. Working branch: feature/workbench-data-bridge.

## Confirmed
- Outside FOIMS-X, time is real time (1 real second = 1 strategic second = 35 Doom tics).
- In FOIMS-X at 1x, 1 strategic minute (one sim tick) passes per 35 Doom tics.
- Three speeds (1x, 2x, 3x) as float multipliers, FOIMS-X only.
- Player stat bands tick faster at faster speeds.
- Ejection exits FOIMS-X only, uses the same bands as agents, blocks re-entry until the stat is replenished, and shows per-band randomized messages.
- No in-FOIMS-X pause control. The only pause is the Main Menu (Escape). A debug-only pause console command, pausefoimsx, is included for now (TIME-15).
- This supersedes the earlier TIME-06 reading (35 Doom tics per strategic minute as the normal pace).
- Time returns to real time on any exit or ejection; acceleration only inside FOIMS-X (TIME-16).
- Random band messages never repeat the same line twice in a row (TIME-17).
- 2x and 3x multiply the 1x FOIMS-X rate, which is 60x real time (TIME-18).
- Agent activities run in real time outside FOIMS-X (TIME-19).

## Proposed
- Scaled-integer export and a fractional-tick accumulator (TIME-12).
- Band flag plus message-variant table (TIME-13).
- Time-settings catalog rows (TIME-14).

## Open
- Release-build handling of pausefoimsx, whether the chosen speed setting is remembered for the next entry, which bands eject, metrics sampling.

## Files touched
- Appended a section to docs\workbench\spec\DESIGN_DECISIONS_2026-10-07.md. Created this file.
- Backup: tools\doda_content_workbench\backups\v036_pacing_foimsx_<timestamp>
