# Time Settings Catalog Import (v038-v039), 2026-10-08

## Summary
- v038 added the `time_settings` authoring catalog: `data_authoring/source/time_settings.csv`,
  `doda_time_rules.py`, `tests/test_time_rules.py`, a "Time Settings" page (Administration group),
  and wiring in the page registry, network editor and GUI export/validate chain.
- v039a moved PCARE-OPEN-07 from open items to settled in `doda_personal_care_rules.py`.
- Authoring only: `runtimeImplemented: false`. All seven rows are inactive.

## Verification
- 144 tests OK (135 before, plus 9 time tests). Validation passed with zero errors.
- Every export PASS, including time settings; ZScript catalog current; REGISTRY OK.

## Rows
| Setting | Value | Category |
|---|---|---|
| DOOM_TICS_PER_SECOND | 35 (engine constant, not editable) | ENGINE |
| SIM_TICK_STRATEGIC_MINUTES | 1 | SIM_TICK |
| DOOM_TICS_PER_SIM_TICK_FOIMSX_1X | 35 | PACING |
| STRATEGIC_SECONDS_PER_REAL_SECOND_OUTSIDE | 1 | PACING |
| FOIMSX_SPEED_1X / 2X / 3X | 1 / 2 / 3 | FOIMSX_SPEED |

## Validation rules
- Values above 0, at most 4 decimal places; exported with a scaled integer (x10000).
- Sim tick is a whole number of minutes; FOIMS-X speeds must ascend; engine rows not editable.
- Warning if the engine tic rate is not 35 or the speed count is not 3.

## Settled decisions
- TIME-01 global time catalog; per-tick activity rates stay in their own catalogs.
- TIME-02 Doom tic (35/s) is distinct from a DoDA sim tick.
- PCARE-OPEN-07 one sim tick is one strategic minute.
- TIME-03 decimal authoring, 4 places, scaled-integer export.
- TIME-06 real time outside FOIMS-X; 1x inside is one sim tick per 35 Doom tics.
- TIME-07 / TIME-18 three FOIMS-X multipliers of the 1x rate, subject to change.
- TIME-08, TIME-10, TIME-15, TIME-16, TIME-19 as recorded in `doda_time_rules.DECISIONS`.

## Open items
- TIME-OPEN-01 remember chosen FOIMS-X speed between entries?
- TIME-OPEN-02 exclude `pausefoimsx` from release builds?
- TIME-OPEN-03 native fractional-tick accumulator and save-schema impact (deferred native task).
- TIME-OPEN-04 reconcile metrics sampling policy (every 10 ticks, 50 samples) with the sim tick.
- TIME-OPEN-05 ejecting condition bands and per-band message variants (vs existing `foims_warning`).

## Deferred
- Validator check that activity durations are sim-tick multiples.
- `condition_bands` ejection flag and message-variants table.
- Known pre-existing note: the proof-of-concept script steps time every 5 real seconds.
