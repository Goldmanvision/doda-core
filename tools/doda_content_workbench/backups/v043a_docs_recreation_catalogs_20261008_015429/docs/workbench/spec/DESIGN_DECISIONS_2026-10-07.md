# DoDA Design Decisions Addendum - 2026-10-07 (continued)

CONFIRMED user decisions recorded after the handoff's Part Five. Merge into
docs\workbench\spec\DoDA_Working_Specification_and_Handoff_2026-10-07.md
(Part Five) when that folder is attached. Encoded in doda_network_rules.py (TASK_INTERRUPTION).

## Processing-task interruption (resolves TASK-01 and TASK-02)
- TASK-01a: Shift end pauses a processing task. It resumes at the person's next shift unless the player reassigns it to another person.
- TASK-01b: Incapacity mid-task fails the task. The unresolved evidence is destroyed: the processed portion keeps its positive credit and the remainder is recorded as lost evidence.
- TASK-01c: If the player cancels a task, the evidence waits as partly processed. It is not lost and not reset.
- TASK-02: Another qualified person may take over a partly finished processing task and keeps its progress.
- Unchanged: equipment unavailability gives reduced effectiveness or a pause, never destruction.

## System-update interruption
- UPD-01: An interrupted system update must restart from the beginning.

## Register changes
- TASK-01: RESOLVED (transfers via INT-01..10; processing via TASK-01a..c; updates via UPD-01).
- TASK-02: RESOLVED (keep progress on takeover).
- UPD-02 RESOLVED: overdue-update risk keeps building through a restart until the update completes.
- NET-03b RESOLVED: one technician may attend both transfer ends only if able to move between both device locations.
- INT-11 RESOLVED: permanent unavailability = death, dismissal, defection, or retirement.

## Network content (populated from diagram)
- NET-CONTENT-01: Five tiers confirmed: DIALUP G1 (14.4KB/s), DIALUP G2 (56K), LEASED_LINE G1 (1.5MB/s, T1), LEASED_LINE G2 (44MB/s, T3), FIBER G1 (2GB/s).
- NET-CONTENT-02: One placeholder router per tier confirmed (diagram shows no routers).
- NET-06 PARTIAL: diagram speed labels kept verbatim; file sizes are deliberately exaggerated for gamification. Numeric units for timing remain open.

Status: fully merged into docs\workbench\spec\DoDA_Working_Specification_and_Handoff_2026-10-07.md (Part Five).

## Care services (recorded after the Part Five merge)
- CARE-01: Medical care and therapy are not player-staffed services; no staffing rules or staffing qualifications.
- CARE-02: Emergency medical care is automated and free of cost. Duration, healing, and recovery effects remain OPEN.
- CARE-03: Agents may deliver medical attention as a skill/training competency, not as facility staffing.
- CARE-04: The player assigns an agent to therapy; the provider is handled automatically. Therapy cost, duration, and effects remain OPEN.
- CARE-05: Care services are authored in their own catalog, separate from capabilities and staffing rules. v107 reference: doda_05_remediation_and_care_v107.xlsx, RemedyCat.
- CARE-06: The care catalog holds medical and therapy services only; personal care (eating, resting, off duty, decompression) belongs with the personnel slice.
- CARE-07: Emergency services are free; non-emergency medical care and physical and psychological therapy have costs (amounts OPEN).
- Implemented as data_authoring/source/care_services.csv (8 inactive drafts) with validator doda_care_rules.py.
- CARE-08: Basic Medical Care, Advanced Medical Care, and Therapy Services are places where care services can happen (care location features, not staffed capabilities). Moved from capabilities.csv to care_location_features.csv with IDs unchanged; linked to services in care_service_locations.csv.
- CARE-09: Emergency Medical Transport happens at no place; it brings incapacitated agents to a hospital for Advanced Medical Care (destination_feature_id = CAP_ADVANCED_MEDICAL). Hospitals provide Advanced Medical Care.
- CARE-10: Therapy Services offers both Psychological and Physical Therapy; Hospitalization is offered at Advanced Medical Care; Check-Up at Basic Medical Care.
- CARE-11: All care happens at hospitals; every hospital provides Basic Medical Care, Advanced Medical Care, and Therapy Services. A territory may have one or more hospitals of varying quality and cost. Hospital records are deferred to territory/location authoring.

Status of the care section: not yet merged into the handoff's Part Five.

## Personnel conditions

- PERS-03: The condition catalog holds per-agent stats only (Health, Current HP, Base HP, Injury, Fatigue, Nutrition, Stress, Workload, Loyalty). Department scores stay in metrics; world pressure is deferred.
- PERS-04: Health is an at-a-glance flavor label, not an exact measure. It averages the contributing condition values and shows a colour-coded "Condition: ..." label (e.g. Healthy, Sick, Injured). Health bands are presentation only. Supersedes the HP/Health synchronization question (PERS-02).
- PERS-05: Bands suggest a care service where one exists; other actions remain text.
- PERS-06: Any agent stat can count toward the Health average with a formula dropdown (NORMALIZED or PERCENT_OF_REFERENCE). Counting: Injury, Fatigue, Nutrition, Stress, Workload, Current HP (as % of Base HP). Not Loyalty.
- PERS-07: Death happens when Current HP drops to 0 or below (killed in action), from NPC damage or severe illness driven by Nutrition, Stress, or Fatigue. Simulation not implemented yet.
- PERS-08: Health labels are the workbook's, coloured Dead dark red, Incapacitated red, Very Unhealthy orange, Unhealthy yellow, Healthy green, Very Healthy bright blue.
- PERS-09: HP ranges 40-120 like the player (Base HP 40-120; Current HP 0-120, capped by Base HP).
- PERS-10: Starting values: Base HP is a random roll 40-120 on agent/analyst creation; Current HP starts equal to Base HP. Each stat has a starting-value rule (DEFAULT, RANDOM_IN_RANGE, COPY_OF_STAT).
- PERS-11 (deferred): Tick-based HP drain like Fatigue and Nutrition; severe conditions (extreme starvation, weeks of extreme fatigue) drain HP rapidly.
- PERS-12: Dead means dead. The Dead label comes only from the death state, never from the Health average.
- Implemented as condition_stats.csv (9) and condition_bands.csv (35), all inactive, validator doda_condition_rules.py. Record: docs/workbench/history/Personnel_Conditions_Import_2026-10-07.md.

## Personnel traits and training

- PERS-13: Traits, training, qualifications, and conditions stay in separate catalogs.
- PERS-14: TrainingCat TRAIN_* IDs are canonical; the duplicate *_TRAINING rows in TraitDefsCat are not imported; Loyalty stays a condition stat.
- PERS-15: Training is binary (trained or not, no levels); agents can be trained in any number of skills.
- PERS-16: New hires randomly have one or two trained skills on their dossier.
- PERS-17: RemedyCat TRAINED_* requirements mean "trained in that skill"; TRAINED_MEDIC = TRAIN_MEDICAL.
- PERS-18: Culinary, Hospitality, Survivalist, and Magic are trainings; they let an agent or analyst perform the matching tasks and personal-care actions without being at a designated location.
- PERS-19: New-hire roll is even: one or two skills with equal chance, every eligible skill equally likely. Weighted rolls may come later.
- Implemented as personnel_traits.csv (Courage, Agility, Paranormal Sensitivity) and training_catalog.csv (5 TRAIN_* rows), all inactive, RANDOM_IN_RANGE 0-100, with the Health option (off). Validator doda_agent_attribute_rules.py. Record: docs/workbench/history/Personnel_Traits_and_Training_Import_2026-10-07.md.

## Personal care

- PCARE-01: Off Duty, Eating, Resting, and Decompression are personal-care actions in their own catalog (personal_care_actions.csv), keeping workbook REMED_* IDs.
- PCARE-02 (confirmed): Food Access, Rest Facility, and Safe Housing are personal-care places (personal_care_features.csv). CAP_FOOD moved out of capabilities.csv, ID unchanged. An action can happen at ANY linked place; agents trained in a linked training can do it anywhere (PERS-18).
- Record: docs/workbench/history/Personal_Care_Import_2026-10-07.md.
- PCARE-03: Place types (restaurant, agent's home, safe house, hotel, car or van, office kitchen, cult mess hall, gas station, 12 recreation types) offer features. Rest is exclusively home, hotel, car or van.
- PCARE-04: Safe houses serve as homes, belong to no agent, occupancy by beds. CAP_SAFE_HOUSING deprecated for PLACE_SAFE_HOUSE.
- PCARE-05: Rest and food at hospitals only during recovery; personal_care_during_care.csv links REMED_RECOVERY to Resting and Eating.
- PCARE-06: Recreation feature (CAP_RECREATION); recreation places randomized in territory, travel may be needed.
- PCARE-07: Recreation place types have activities with company and duration options.
- PCARE-08: Hotels offer food. Safe-house rest confirmed.
- PCARE-07 (revised): Recreation activities have place dropdown, description, one duration, company options, stress reduction per tick, exhaustion per tick; duration variants are separate rows.
- PCARE-05 confirmed: hospital rest and food only during Recovery, not Emergency Hospitalization.
- PCARE-09: Agents and analysts have no tracked money; personal care, food, and recreation are free to player and agent. Payroll separate; CARE-07 care costs unaffected.
- PCARE-07 (revised): activity fields are time cost (minutes), stress reduction, fatigue cost, and hunger reduction per tick.
- PCARE-10: Activities have both a fatigue cost per tick and an energy required to start. Energy = Fatigue maximum - Fatigue; an agent can start only when energy is at or above the requirement.

## Slice log: handoff takeover review (2026-10-07, evening)

Status: record only. No new user decisions. Nothing was promoted from PROPOSED to CONFIRMED. No source CSVs, code, or exports were changed in this slice.

### Observed state (read-only check, 2026-10-07 9:42 PM EDT)
Row counts of data_authoring\source files, taken from the user's pasted output:
- personal_care_actions.csv: 4
- personal_care_features.csv: 4
- personal_care_locations.csv: 8
- personal_care_trainings.csv: 7
- personal_care_place_types.csv: 20
- personal_care_place_type_features.csv: 23
- personal_care_during_care.csv: 2
- recreation_activities.csv: 14

All rows seen in the sampled heads have active=false. recreation_activities.csv has the energy_required_to_start column (PCARE-10). Sampled recreation rows have blank durations, rates, and energy values; none were invented.

### Backups
Latest existing folders in tools\doda_content_workbench\backups: v032_energy_required_20261007_211724, v031_activity_costs_20261007_210549, v030_recreation_fields_20261007_205741. This slice is v033.

### Corrections and discrepancies
- The row count for personal_care_place_type_features is 23. The Personal Care import note (history) says 22 and is stale for that figure.
- Two backup locations are in use: tools\doda_content_workbench\backups (vNNN folders) and data_authoring\backups (the v107 connective import folder). The handoff rule names the first. OPEN: confirm whether the second is legacy only.
- The 135-test and zero-error validation result is the packet's last known good. It was not re-run in this slice.

### Open items (unchanged)
- Recreation activity time costs and rates; activities for the eight empty recreation places.
- PCARE-OPEN-07 and PERS-11: tick length and tick-based HP drain.
- PCARE-OPEN-04: accommodations, location conditions, undercover routes, compliance.
- PCARE-OPEN-05: CAP_REST and CAP_SAFE_HOUSING access booleans (workbook row shift).
- PCARE-OPEN-06 and CARE-11: territory authoring.
- PERS-OPEN-07 and PERS-OPEN-08: trait and training effects; post-hire training.
- Care costs, durations, effects; role-to-qualification mappings.

## Time units and tick decisions (2026-10-07, late evening)

Working branch: feature/workbench-data-bridge (user, 2026-10-07). The local E: drive remains authoritative; GitHub master is reference only (WB-01).

### CONFIRMED
- PCARE-11: One fixed global sim tick. All per-tick rates are signed decimal values (positive or negative).
- PCARE-12: Activity durations are whole numbers of sim ticks.
- PCARE-13: Per-tick rates are constant over an activity for now. Variable rate curves are deferred; they can be added later as an optional column without breaking existing rows.
- TIME-01: Global time settings get their own catalog. Per-tick rates for recreation, medical care, rest, and other activities belong in the catalog of the activity they describe, not in the global catalog.
- TIME-02: Two distinct time units are recognized. A Doom tic is the engine unit (35 per second, real time). A DoDA sim tick is the strategic-simulation unit. Authored rates use sim ticks.
- TIME-03: Float handling. Authoring stays decimal. The validator limits rates to four decimal places. The export also emits scaled integers so native code does not parse floats. (Matches the native rule against unconstrained floating-point state.)
- TIME-04: Metrics sampling history (every 10 strategic ticks, 50 samples retained, from an earlier workbook design) is logged as an open reconciliation item. No data changed.
- PCARE-OPEN-07 RESOLVED (CONFIRMED by user, 2026-10-07 11:57 PM): One sim tick equals one strategic minute. Changing it later requires scaling every per-tick rate by the same factor; durations are stored in minutes and stay valid. At this tick length, the earlier metrics policy (sample every 10 ticks, keep 50 samples) would span about 500 strategic minutes (8 h 20 min); TIME-04 remains open.

### PROPOSED (not confirmed)
- TIME-05: A global time-settings catalog holding at least: Doom tics per second (35, informational), strategic minutes per sim tick, and Doom tics per strategic minute at normal speed. The validator would check that durations are multiples of the sim tick.

### OPEN
- Doom tics per strategic minute at normal speed (pacing value; blank until the user decides).
- Confirm UZDoom 5.0 tic rate against local source during the read-only audit.
- Reconcile metrics sampling (TIME-04) with the sim tick unit.
- Sequence: global time catalog, then recreation values, then CAP_REST booleans, then trait and training effects, then the V1A workbench audit.

## Pacing and FOIMS-X time decisions (2026-10-08, 12:15 AM)

### CONFIRMED (user)
- TIME-06 (SUPERSEDES any earlier TIME-06 wording): Outside FOIMS-X, strategic time runs in real time: 1 real second = 1 strategic second (35 Doom tics). Inside FOIMS-X at 1x, time is accelerated to 1 strategic minute (one sim tick) per 35 Doom tics (1 real second). The earlier "one real second per strategic minute" pacing applies only to FOIMS-X at 1x.
- TIME-07: FOIMS-X has three speed settings, 1x, 2x, 3x (Normal, Fast, Fastest). They are float multipliers and subject to change. They are not accessible outside FOIMS-X.
- TIME-08: Player stat bands keep ticking while the player is in FOIMS-X. At faster speeds the player's stats tick faster too.
- TIME-09 (revised): When the player's bands reach a blocking state, the player is ejected from FOIMS-X only. The player is not forced off duty; the player is "too X to focus on the computer screen right now." The player uses the same condition stats and bands as agents.
- TIME-10: After an ejection the player cannot re-enter FOIMS-X until the stat that caused it is replenished.
- TIME-11: Each ejecting band has its own message lines, with several randomized variations per band.
- TIME-15: FOIMS-X has no pause control of its own. The only pause is opening the Main Menu with Escape. For now a debug-only pause is included as a console command named pausefoimsx.
- TIME-16: Outside FOIMS-X, including after any exit or ejection, time returns to real time (1 real second = 1 strategic second = 35 Doom tics). Acceleration exists only inside FOIMS-X.
- TIME-17: Random band messages must not repeat the same line twice in a row.
- TIME-18: The 2x and 3x multipliers apply to the 1x FOIMS-X rate (60x real time).
- TIME-19: Agent activities proceed in real time outside FOIMS-X (a 1-hour activity takes 1 real hour). For now time is accelerated only inside FOIMS-X.

### Derived arithmetic (not a decision)
- Outside FOIMS-X: 1 sim tick = 60 real seconds = 2,100 Doom tics; 1 strategic day = 24 real hours.
- FOIMS-X 1x: 60x real time; 1 strategic day = 24 real minutes. If multipliers apply to the 1x rate: 2x = 12 minutes, 3x = 8 minutes.

### PROPOSED (not confirmed)
- TIME-12: Speed multipliers are authored as decimals and exported as scaled integers (TIME-03). Native keeps a fractional-tick accumulator so non-integer rates (for example 3x = 35/3 Doom tics per sim tick) stay deterministic.
- TIME-13: The ejection gate is an authored yes/no flag on condition bands (working name blocks_foimsx_for_player) plus a child table of message variants per band (band id, message text, active). Check against the existing flavor-text catalog to avoid duplication.
- TIME-14: The time-settings catalog holds: Doom tics per second (35, informational), Doom tics per sim tick at FOIMS-X 1x (35), strategic seconds per real second outside FOIMS-X (1), and three speed multipliers (starting values 1, 2, 3; user-editable).

### OPEN
- Whether the pausefoimsx debug command is excluded from release builds.
- Whether the chosen speed setting (1x, 2x, 3x) is remembered for the next FOIMS-X entry.
- PROPOSED validator rule: each ejecting band needs at least two active message variants so the no-repeat rule (TIME-17) can work.
- Which bands carry the ejection flag (user to choose when reviewing bands).
- Reconcile TIME-04 metrics sampling with the sim tick.

## Time settings catalog implemented (2026-10-08, 12:42 AM)

Authoring, validation, and export only. No runtime behaviour. Working branch: feature/workbench-data-bridge.

### Implemented
- data_authoring/source/time_settings.csv: 7 inactive draft rows (engine tics per second, strategic minutes per sim tick, Doom tics per sim tick at FOIMS-X 1x, strategic seconds per real second outside FOIMS-X, and FOIMS-X speed multipliers 1x, 2x, 3x).
- tools/doda_content_workbench/doda_time_rules.py (0.1.0): validator and exporter with CLI. Exports generated/data/time_settings_catalog.json with runtimeImplemented false, scaled integers (value x 10000), and derived pacing values.
- Workbench page: Time Settings (group: Administration), editor tab, Validate All and Export All integration, catalog regeneration gated on the new result.
- tests/test_time_rules.py (9 tests); Time Settings tab added to the page-registry test.

### Verified (2026-10-08 12:42 AM, user-run)
- 144 tests OK; Validation passed with zero errors; five exports PASS (care, conditions, attributes, personal care, time); ZScript catalog current; REGISTRY OK.

### Source facts confirmed locally
- TICRATE is 35 (uzdoom-official/src/doomdef.h).
- Native bridge: GetStrategicMinutes() returns an integer; AdvanceStrategicMinutes(int deltaMinutes) advances only when called. The proof-of-concept idle stepping (strategic minutes every 5 real seconds) is a proof artifact and does not match TIME-06 pacing. Aligning it is native or ZScript work, not part of this batch.

### Backups in this period
- v038_time_settings: pre-edit copies of the four edited files.
- v039a_pcare_open07 (from another thread): doda_personal_care_rules.py only; PCARE-OPEN-07 settled note.
- v040_docs_time_catalog: this record.

### Deferred or open
- Check that activity durations are multiples of the sim tick (cross-table rule).
- Ejection flag on condition bands plus per-band message variants; reconcile with the existing foims_warning field (TIME-13).
- Native fractional-tick accumulator and save-schema impact (TIME-OPEN-03).
- Whether the chosen FOIMS-X speed is remembered; release handling of pausefoimsx.
- Reconcile metrics sampling with the sim tick (TIME-04).
- Page group for Time Settings may move later.

## Recreation and bookstore decisions (2026-10-08, 1:01 AM)

Decisions only. No schema or data changes in this entry. No balancing values were invented.

### CONFIRMED (user)
- REC-01: Variable-length activities are supported through optional minimum, step, and maximum duration fields instead of one row per duration. Bookstore: 20-minute steps up to 4 hours.
- REC-02: Effect strength uses a named scale (levels) kept in one small lookup table. The user sets the per-tick numbers per level once; activities choose a level. Level values stay blank until set.
- REC-03: Cafe is a boolean randomized when recreation places are generated in an operation territory. Any recreation place can potentially have a cafe, and a cafe supports eating. There is no separate bookstore-with-cafe place type. Territory generation is deferred territory authoring.
- REC-04: Coffee can be obtained anywhere food is available, and it restores some energy.
- REC-05: An agent holds at most one book. Any bookstore trip, of any length, gives the agent a new book if they have none. A book has a random total reading time of 3 to 18 hours. Reading can be done anywhere while off duty, at a lower benefit than reading at the bookstore. When a book is finished it is destroyed, with in-game text that the agent finished the book and placed it on a dusty bookshelf, unlikely to ever be read again.
- REC-06: Buying books is covered by visiting; there is no separate buy activity.
- REC-07: Bookstore activities require 20 energy to start (0 to 100 scale; tired but not fainting or drowsy).
- REC-08 (bookstore intent, qualitative): company alone; stress reduction moderate; fatigue cost very low, lower with a cafe; hunger reduction none without a cafe and small with one; a cafe allows coffee for energy.

### PROPOSED (not confirmed)
- REC-09: Add optional duration step and maximum fields; the existing duration_minutes becomes the minimum. Validator: maximum minus minimum is a multiple of the step, and all values are multiples of the sim tick.
- REC-10: A lookup table of effect levels (working name effect_levels) with blank per-tick values for stress reduction, fatigue cost, hunger reduction, and energy restored. Activities pick levels, with separate cafe-adjusted levels for fatigue cost and hunger reduction. Existing numeric per-tick columns stay as optional overrides.
- REC-11: Place types gain a boolean (working name cafe_possible), true for recreation types. The per-place has-cafe value is generated at territory generation and belongs to territory authoring and native state, not to the catalog.
- REC-12: Reading anywhere is a place-independent activity requiring that the agent holds a book, with a randomized total length of 180 to 1080 minutes stored as minimum and maximum fields.
- REC-13: Coffee is an energy-restoring drink available at any food place; its catalog home is undecided.
- REC-14: The Buy Books row is deprecated (kept inactive for history), not renamed or deleted.

### OPEN
- Energy required to read anywhere (the user's reading-before-sleeping idea suggests lower or none).
- Names of the effect levels and their per-tick values.
- Cafe probability at territory generation (blank).
- What the X in the finished-book text refers to (book type or genre) and whether lines vary.
- Any benefit on finishing a book.
- Coffee model and energy amount.
