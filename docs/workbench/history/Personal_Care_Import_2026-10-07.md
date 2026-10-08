# Personal Care Import — 2026-10-07

Status: PROPOSED drafts. All rows are inactive (`active=false`). No runtime behaviour is implemented; when agents eat, rest, or go off duty is simulation state owned by the native simulation.

## Source

- `doda_05_remediation_and_care_v107.xlsx` RemedyCat rows 11–14 (actions, places, trainings).
- `doda_01_department_progression_v107.xlsx` FacilityCapsCat rows 2, 3, 11 (places).
- `dodabase-v107_department_schema_template.xlsx` RemedyCat rows 12–14 (`required_helper_role`, for Hospitality).

## Decisions

- PCARE-01: Personal-care actions are Off Duty, Eating, Resting, and Decompression, in their own catalog (care services stay medical and therapy only, CARE-06). IDs keep the workbook `REMED_*` IDs.
- PCARE-02 (confirmed by user): Places where personal care happens are personal-care features: Food Access (`CAP_FOOD`), Rest Facility (`CAP_REST`), Recreation (`CAP_RECREATION`), and the deprecated Safe Housing (`CAP_SAFE_HOUSING`). An action can happen at a place with ANY of its linked features. `CAP_FOOD` moved out of `capabilities.csv` with its ID unchanged (it was referenced nowhere else).
- PERS-18 applied: an agent or analyst trained in a linked training can perform the action anywhere, without a linked place.
- PCARE-03: Place types are the kinds of real places, and each offers features. Food places: restaurant, agent's home, FBI safe house, office kitchen, cult mess hall, gas station. Rest places are exclusively home (agent's home, safe house), hotel, and car or van.
- PCARE-04: A safe house serves as a home but belongs to no agent; its occupancy depends on its beds. Agents can rest at a safe house (confirmed). `CAP_SAFE_HOUSING` is deprecated (kept inactive for ID history) in favour of place type `PLACE_SAFE_HOUSE`; its two action links were removed.
- PCARE-05: Rest happens at a hospital only while an agent is in recovery from illness or injury, and agents are also fed there during recovery. Not during Emergency Hospitalization (confirmed). Authored in `personal_care_during_care.csv`: Recovery (`REMED_RECOVERY`) provides Resting and Eating.
- PCARE-08: Agents can eat at hotels (Hotel offers Food).
- PCARE-10: Energy is the inverse of Fatigue (energy = Fatigue maximum − Fatigue, so 0–100). An agent or analyst can start an activity only when their energy is at or above the activity's Energy Required to Start. The check reads the Fatigue maximum from `condition_stats.csv`.
- PCARE-09: Agents and analysts have no tracked money. Personal care, food, and recreation are free: the player pays nothing and the agent pays nothing. Salaried payroll on hire is separate, and medical and therapy costs (CARE-07) are unaffected. The cost column was removed from personal-care actions; the workbook cost policy IDs (COST_PAID_LEAVE, COST_CONTRACTOR_SERVICE) are noted in the descriptions as not used.
- PCARE-06: Recreation (workbook `FUN_CAPABLE`) is offered by 12 recreation place types: movie theater, shopping mall, video arcade, amusement park, vacation resort, luxury cruise, national park, video rental store, bookstore, bowling alley, gym, bar or lounge. They are randomized throughout operational territory; some agents and analysts may need to travel to another territory or outside territory to reach one. Linked to Off Duty and Decompression.
- PCARE-07: Each recreation activity has a place (dropdown), description, a time cost (duration in minutes plus a label), company options (alone, friends, strangers), stress reduction per tick, fatigue cost per tick (energy used; formerly exhaustion per tick), energy required to start, and hunger reduction per tick (some activities involve eating). Activities with different durations are separate rows. The earlier draft rows REC_CAMP and REC_FISH (never released) were split into REC_CAMP_OVERNIGHT / _3_DAYS / _1_WEEK and REC_FISH_1_HOUR / _2_HOURS / _ALL_DAY.

## Files

- `personal_care_actions.csv` (4): ID, name, who starts it (PLAYER_SCHEDULED / AGENT_INITIATED), requires off duty, follow-up action, workbook status, source, description.
- `personal_care_features.csv` (3).
- `personal_care_locations.csv` (8 action → place links).
- `personal_care_trainings.csv` (7 action → training links).
- `personal_care_place_types.csv` (20), `personal_care_place_type_features.csv` (22), `recreation_activities.csv` (14), `personal_care_during_care.csv` (2).
- Validator/exporter `doda_personal_care_rules.py`, exporting `generated/data/personal_care_catalog.json` (`runtimeImplemented: false`).
- Workbench pages under Personnel and Care: Personal Care, Personal Care Places, Personal Care Place Links, Personal Care Trainings, Place Types, Place Type Features, Recreation Activities, Personal Care During Care. Included in Validate All and Export All.

## Imported content

| Action | Who starts it | Workbook cost policy (not used, PCARE-09) | Follow-up | Places | Trainings (anywhere) |
|---|---|---|---|---|---|
| Scheduled Off Duty Time | Player | COST_PAID_LEAVE | Eating | Rest, Food, Recreation | — |
| Eating | Agent | COST_CONTRACTOR_SERVICE | Off Duty | Food (plus hospitals during Recovery) | Culinary, Hospitality, Survivalist |
| Resting | Agent | — | Off Duty | Rest (plus hospitals during Recovery) | Hospitality, Survivalist |
| Decompression (workbook: DEFERRED) | Agent | — | Resting | Rest, Food, Recreation | Hospitality, Survivalist |

All four require the agent to be off duty (workbook `OFF_DUTY_REQUIRED`). Off Duty → Eating → Off Duty is a follow-up loop in the workbook and is kept as written.

## Place types

| Place type | Features | Notes |
|---|---|---|
| Agent's Home | Food, Rest | Home, owned by an agent |
| FBI Safe House | Food, Rest | Home, owned by no agent, occupancy by beds |
| Hotel | Rest, Food | |
| Car or Van | Rest | |
| Restaurant, Office Kitchen, Cult Mess Hall, Gas Station | Food | |
| 12 recreation place types | Recreation | Randomized in territory |

## Recreation activities (user examples only)

| Place | Activity | Duration | Company |
|---|---|---|---|
| Bowling Alley | Bowl | not yet set | Alone, friends, strangers |
| Bookstore | Buy Books; Read Books; Do Research | not yet set | — |
| Gym | Work Out; Play Basketball; Swim | not yet set | — |
| National Park | Hike | not yet set | — |
| National Park | Camp Overnight | label only (Overnight) | — |
| National Park | Camp for Three Days | 4,320 min | — |
| National Park | Camp for a Week | 10,080 min | — |
| National Park | Go Fishing for an Hour / Two Hours | 60 / 120 min | — |
| National Park | Go Fishing All Day | label only (All day) | — |

Stress reduction, fatigue cost, energy required, and hunger reduction are blank on every row (not invented). The other eight recreation place types have no activities yet.

## Validator rules

- Unique action IDs; who-starts-it enum; follow-up must exist, not be itself, and not be inactive when the action is active.
- Place IDs must be unique across personal-care places, care locations, and capabilities.
- Links must point to existing actions, places, and trainings; active links cannot use inactive targets; no duplicate links.
- Place types: unique IDs; only a home can be agent-owned; occupancy is UNSPECIFIED or BEDS; feature links must exist with no duplicates.
- Activities: place type must offer Recreation; company options from ALONE, FRIENDS, STRANGERS with no repeats; duration above 0 and required once active; stress, fatigue, and hunger rates are numbers (decimals and negatives allowed); energy required is 0 to the Fatigue maximum.
- Personal care during care: care service and action must exist; no duplicates; active links can't use inactive actions.
- Warnings: an active action with no active place or training; an active place hosting no active actions; a home place type that doesn't offer Rest.

## Not imported (workbook data defects or later work)

- Eating's duration cell reads "2 days, 12:00:00" (malformed), so no duration is imported.
- Accommodations (personal residence, rental, hotel, vehicle), location conditions (safe, public, private, hostile), undercover routes, motor-vehicle requirement, escalation policies, hard blocks, and compliance notes.

## Open items

- PCARE-OPEN-01: Durations, effects on fatigue/nutrition/stress, and cost amounts.
- PCARE-OPEN-02: Activities for the other eight recreation place types; durations for Overnight, All day, bowling, and the untimed activities; stress, fatigue, energy, and hunger values.
- PCARE-OPEN-07: Tick length and how per-tick rates apply (with PERS-11 HP drain).
- PCARE-OPEN-06: Actual places, safe-house bed counts, recreation placement and travel (territory authoring).
- PCARE-OPEN-04: Accommodations, location conditions, undercover routes, and compliance.
- PCARE-OPEN-05: CAP_REST and CAP_SAFE_HOUSING access booleans (workbook row shift).
