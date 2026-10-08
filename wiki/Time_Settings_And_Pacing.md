# Time Settings and Pacing

Status: authoring catalog only (v038-v039, 2026-10-08). `runtimeImplemented: false`; all rows inactive.

## Units
- **Doom tic:** engine unit, 35 per real second (`TICRATE` in doomdef.h).
- **Sim tick:** DoDA strategic unit; one sim tick = one strategic minute (PCARE-OPEN-07, settled).
- **Strategic clock:** native, whole minutes (`GetStrategicMinutes`, `AdvanceStrategicMinutes`).

## Pacing
- Outside FOIMS-X: real time (1 strategic second per real second). No speed control.
- Inside FOIMS-X at 1x: one sim tick per 35 Doom tics (60 strategic seconds per real second).
- Speeds 1x / 2x / 3x multiply the 1x rate (subject to change).
- Player stats tick inside FOIMS-X, faster at higher speeds. Agent activities run in real time outside.
- Pause: Main Menu only, plus debug console command `pausefoimsx`. No in-FOIMS-X pause control.
- Any exit or ejection returns time to real time. After ejection, re-entry waits until the stat is replenished.

## Catalog
- Source: `data_authoring/source/time_settings.csv`
- Code: `tools/doda_content_workbench/doda_time_rules.py`; tests: `tests/test_time_rules.py`
- Export: `generated/data/time_settings_catalog.json` (decimal + scaled integer, scale 10000)
- GUI: "Time Settings" page (Administration group); included in the network-rules validate/export chain.

| Setting | Value | Category |
|---|---|---|
| DOOM_TICS_PER_SECOND | 35 (not editable) | ENGINE |
| SIM_TICK_STRATEGIC_MINUTES | 1 | SIM_TICK |
| DOOM_TICS_PER_SIM_TICK_FOIMSX_1X | 35 | PACING |
| STRATEGIC_SECONDS_PER_REAL_SECOND_OUTSIDE | 1 | PACING |
| FOIMSX_SPEED_1X / 2X / 3X | 1 / 2 / 3 | FOIMSX_SPEED |

## Validation
- Values above 0, at most 4 decimal places. Sim tick is a whole number of minutes.
- Speeds ascend; engine rows not editable. Warnings if the tic rate is not 35 or the speed count is not 3.

## Formulas
- Sim ticks per real second inside FOIMS-X = multiplier x 35 / DOOM_TICS_PER_SIM_TICK_FOIMSX_1X
- Doom tics per sim tick at a speed = DOOM_TICS_PER_SIM_TICK_FOIMSX_1X / multiplier (3x = 11.6667)
- Outside: real seconds per sim tick = 60 x SIM_TICK / STRATEGIC_SECONDS_PER_REAL_SECOND_OUTSIDE (= 60)
- Proposed runtime accumulator: acc += multiplier each tic; fire a sim tick at each 35.
- Rate conversion: rate_per_tick = rate_per_minute x SIM_TICK_STRATEGIC_MINUTES

## Open items
- TIME-OPEN-01 remember the FOIMS-X speed between entries?
- TIME-OPEN-02 drop `pausefoimsx` from release builds?
- TIME-OPEN-03 native fractional accumulator for sub-minute time; save-format impact.
- TIME-OPEN-04 reconcile metrics sampling (10 ticks, 50 samples) with the sim tick.
- TIME-OPEN-05 which condition bands eject the player; per-band message variants vs `foims_warning`.
- Key question: is player stat drain per sim tick (60x faster in FOIMS-X) or per real second?

## Known gaps
- CLI `doda_content_workbench.py validate` may not include time settings (verify).
- Proof-of-concept script still steps time every 5 real seconds (contradicts real-time pacing).
- Time settings are not yet in the generated ZScript catalog.

## Next steps
1. Validate that activity durations are whole multiples of the sim tick.
2. Add a `condition_bands` ejection flag and message-variants table.
3. Native time work: fractional accumulator, save format, replace the proof-of-concept stepping.

History: docs/workbench/history/Time_Settings_Catalog_Import_2026-10-08.md
