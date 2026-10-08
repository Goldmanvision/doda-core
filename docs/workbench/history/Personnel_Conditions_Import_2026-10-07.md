# Personnel Conditions Import — 2026-10-07

Status: PROPOSED drafts. All rows are inactive (`active=false`). No runtime behaviour is implemented; live condition values stay owned by the native simulation and campaign/save state.

## Source

- `doda_02_personnel_and_operations_v107.xlsx`, sheets `StatsCat` (rows 2–10) and `CondBandsCat` (rows 2–36).
- Not imported: `ActivePersConds` (campaign state, not definitions), `CondRules` and `EventsCat` (tick rates and effects; later slice).

## Decisions

- PERS-03: The condition catalog holds per-agent stats only: Health, Current HP, Base HP, Injury, Fatigue, Nutrition, Stress, Workload, Loyalty. Public Trust and Congressional Influence belong with department metrics (`metrics.csv` already has Public Trust on 0–1000). Cult Influence and Paranormal Pressure wait for a world-pressure slice.
- PERS-04: Health is an at-a-glance flavor feature, not an exact measure. It averages the contributing condition values and shows a colour-coded label such as "Condition: Healthy", "Condition: Sick", or "Condition: Injured". Health bands are presentation only, so they have no assignment effects and never force an agent off duty. This replaces the open HP/Health synchronization question (PERS-02): no synchronization contract is needed.
- PERS-05: A band may suggest a care service where one exists; other actions stay as text until personal-care services are authored.
- PERS-06: Any agent stat authored in the Workbench can count toward the Health average, with a formula chosen from a dropdown:
  - `NORMALIZED`: the value's position within the stat's minimum–maximum range.
  - `PERCENT_OF_REFERENCE`: the value as a percent of another stat (Current HP as a percent of Base HP).
  NEGATIVE stats are inverted before averaging. Counting toward Health: Injury, Fatigue, Nutrition, Stress, Workload (NORMALIZED) and Current HP (PERCENT_OF_REFERENCE of Base HP). Not counting: Loyalty, and Base HP itself (it is the reference).
- PERS-07: Death happens when Current HP drops to zero or below (killed in action). Causes: NPC damage, or severe illness when Nutrition, Stress, or Fatigue drive HP very low. That simulation is not implemented yet. The export records it as `deathRule`.
- PERS-08: Health uses the workbook labels with colours: Dead dark red `#8B0000`, Incapacitated red `#FF0000`, Very Unhealthy orange `#FF8C00`, Unhealthy yellow `#FFD700`, Healthy green `#00C000`, Very Healthy bright blue `#00BFFF`. The exact hex values are editable proposals.
- PERS-09: HP ranges from 40 to 120, similar to the player. Base HP is 40–120; Current HP is 0–120 and capped by the agent's Base HP. Defaults are undecided.
- PERS-10: Each stat records how its value starts when an agent or analyst is created: `DEFAULT` (the default value), `RANDOM_IN_RANGE` (a roll within the stat's minimum–maximum), or `COPY_OF_STAT` (another stat's starting value). Base HP is a random roll from 40 to 120; Current HP starts equal to Base HP. The other direct stats use their defaults; Health and Workload are calculated. The roll's distribution is not specified (assumed uniform).
- PERS-11 (deferred): HP drains on a tick, like Fatigue and Nutrition. More severe conditions (e.g. extreme starvation, or extreme fatigue for weeks) cause rapid deterioration with a high HP-loss rate.
- PERS-12: Dead means dead. The Dead label is shown only when the agent is dead (Current HP at or below 0), never from the Health average. HEALTH_DEAD now uses `band_trigger = DEATH_STATE` with no range; Incapacitated extends from 1–10 to 0–10 so the average still covers 0–100.

## Files

- `data_authoring/source/condition_stats.csv` — 9 stats.
- `data_authoring/source/condition_bands.csv` — 35 bands for Health, Fatigue, Injury, Nutrition, Stress, and Workload. Loyalty has no bands in v107.
- Validator/exporter `tools/doda_content_workbench/doda_condition_rules.py`, exporting `generated/data/personnel_conditions_catalog.json` (`runtimeImplemented: false`).
- Workbench pages: Personnel and Care > Condition Stats, Condition Bands. Included in Validate All and Export All.

## Validator rules

- A stat that counts toward Health needs a formula; a stat that does not count has no formula or reference. NORMALIZED needs a known minimum and maximum; PERCENT_OF_REFERENCE needs an existing, different reference stat with a minimum of at least 1, active when the stat is active.
- Current HP must be able to reach 0 (death rule).
- Direct stats need a starting-value rule; calculated stats have none. DEFAULT needs a default value; RANDOM_IN_RANGE needs a known range and no default; COPY_OF_STAT needs an existing, different source that is not itself a copy and whose range fits inside the stat's range.
- RANGE bands need a range; DEATH_STATE bands have none, only the Health summary may have one, and at most one per stat.

- Enumerated categories, directions, storage models, derivations, visibilities, severities, and assignment effects.
- DERIVED stats need a derivation (`AVERAGE_OF_CONTRIBUTORS` for Health, `FROM_ASSIGNMENTS` for Workload); DIRECT stats have none.
- Only one Health summary; it cannot count toward itself; an active Health summary needs at least one active contributor; contributors need a known range.
- Health bands: assignment effect NONE and not forced off duty (PERS-04).
- Each stat's bands tile its range with no gaps or overlaps.
- Suggested care services must exist in `care_services.csv`; colours are `#RRGGBB` or blank; an active band needs an active stat.

## Changes from the workbook

- Health category changed from CONDITION to SUMMARY and its derivation set to `AVERAGE_OF_CONTRIBUTORS`.
- Health band effects removed (PERS-04): Dead and Incapacitated were hard blocks (Incapacitated also forced off duty); Very Unhealthy and Unhealthy had penalties. Each band's description records what was removed.
- Health contributors and formulas set per PERS-06.
- HP ranges set per PERS-09 and starting values per PERS-10 (workbook: TBD).
- HEALTH_DEAD changed to a death-state band and HEALTH_INCAPACITATED to 0–10 (PERS-12).
- Workbook text effects normalized to codes: Minor penalty → MINOR_PENALTY, Major penalty → MAJOR_PENALTY, Hard block → HARD_BLOCK, Hard high-risk-task block → HIGH_RISK_TASK_BLOCK, Hard new-task block → NEW_TASK_BLOCK.
- Health band colours set per PERS-08; other bands have no colour.

## Care-service links (PERS-05)

| Band | Suggested care service |
|---|---|
| FATIGUE_UNCONSCIOUS | REMED_RECOVERY |
| INJURY_COMA | REMED_MEDICAL_ATTENTION |
| STRESS_BURNOUT, STRESS_TRAUMATIC, STRESS_BREAKDOWN | REMED_THERAPY_PSYC |

Other band actions stay as text: Resting, Healing, Retrieval, Eating, Off Duty, Recovering.

## Open items

- PERS-OPEN-04: HP drain tick rates by condition severity (PERS-11), how NPC damage is applied, and incapacity rules.
- PERS-OPEN-05: Tick rates, decay, and event effects (`CondRules`, `EventsCat`).
- Native `DoDAPersonRecord` has only Workload and Fatigue today.
- Editor fixes: optional dropdowns include a blank entry so a value can be cleared, and optional number fields may be left blank.
