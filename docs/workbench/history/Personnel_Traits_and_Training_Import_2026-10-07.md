# Personnel Traits and Training Import — 2026-10-07

Status: PROPOSED drafts. All rows are inactive (`active=false`). No runtime behaviour is implemented; each agent's actual values are campaign/save state owned by the native simulation.

## Source

`doda_02_personnel_and_operations_v107.xlsx`: `TraitDefsCat` rows 3–5 and `TrainingCat` rows 2–6. `ActivePersTraits` is campaign state and is not imported.

## Decisions

- PERS-13: Traits, training (skills), qualifications, and conditions stay in separate catalogs, following the handoff spec rule that they must not be collapsed.
- PERS-14: TrainingCat IDs (`TRAIN_*`) are the canonical training IDs. The five duplicate `*_TRAINING` rows in TraitDefsCat (rows 6–10) are not imported. Loyalty (TraitDefsCat row 2) stays a condition stat per PERS-03 and is not a trait.
- PERS-06 applies to traits: they have the "Counts Toward Health" option and Health formula dropdown, all starting as not counting. A PERCENT_OF_REFERENCE reference must be another trait.
- PERS-10 applies to traits: all three are `RANDOM_IN_RANGE` 0–100 (workbook: randomized at creation, default TBD).
- PERS-15: Training is binary. An agent is either trained in a skill or not; there are no skill levels. Agents can be trained in any and all skills, with no limit. Training therefore has no range, starting value, or Health option. (Supersedes the workbook's 0–100 training values.)
- PERS-16: A newly generated hire randomly has one or two trained skills on their dossier, drawn from trainings marked "Can Appear on New Hire Dossier" (`eligible_at_creation`). All five are eligible.
- PERS-17: RemedyCat `TRAINED_*` requirements mean "is trained in that skill". `TRAINED_MEDIC` = trained in `TRAIN_MEDICAL`.
- PERS-18: Culinary, Hospitality, Survivalist, and Magic are trainings (`TRAIN_CULINARY`, `TRAIN_HOSPITALITY`, `TRAIN_SURVIVALIST`, `TRAIN_MAGIC`; workbook flags `TRAINED_*` map to them). These trainings let an agent or analyst perform the matching tasks and personal-care actions without being at a location designated for them.
- PERS-19: The new-hire roll is even: one or two skills with equal chance, and every eligible skill equally likely to be drawn, with no repeats. Weighted rolls may come later.

## Files

- `data_authoring/source/personnel_traits.csv` — Courage (Personality), Agility (Attribute), Paranormal Sensitivity (Special Aptitude). These are fixed after creation.
- `data_authoring/source/training_catalog.csv` — Combat, Investigative, Medical, Research, Administrative, Culinary, Hospitality, Survivalist, and Magic training (9 rows, all eligible at creation). Columns: ID, name, category, eligible at creation, uses, related systems, source, description, sort order, active.
- Validator/exporter `tools/doda_content_workbench/doda_agent_attribute_rules.py`, exporting `generated/data/personnel_attributes_catalog.json` (`runtimeImplemented: false`).
- Workbench pages: Personnel and Care > Traits, Training. Included in Validate All and Export All.

## Validator rules

- Unique IDs within each table and across both tables.
- Category enums per table (traits: PERSONALITY, ATTRIBUTE, SPECIAL_APTITUDE; training: TACTICAL, INVESTIGATIVE, MEDICAL, RESEARCH, ADMINISTRATIVE).
- Traits: minimum and maximum required, minimum below maximum, default inside the range; DEFAULT needs a default, RANDOM_IN_RANGE has none; the same Health-option rules as condition stats.
- Training: warns when trainings are active but fewer than two are eligible at creation (PERS-16); every `TRAINED_*` alias must point to an existing training.

## Workbook notes

- `TrainingCat` related task and event IDs (e.g. `TASK_HEAL`, `EVENT_COMBAT_INJURY`) are kept as text in `related_systems`, not as references; those catalogs do not exist in the Workbench yet.
- TRAIN_MEDICAL is the skill behind CARE-03 (agents delivering medical attention).
- What each new training allows, from the workbooks (recorded as text in `primary_uses` / `related_systems`):

| Training | Allows (workbook source) |
|---|---|
| Culinary | Eating (v107 RemedyCat row 12; template row 12) |
| Hospitality | Eating, Resting, Decompression (template rows 12–14) |
| Survivalist | Eating, Resting, Decompression; Injury Stabilization; Emergency Transport support (v107 rows 7, 12–14; template rows 3, 12–13) |
| Magic | Resurrection (deferred); related to Digital Encantation (TREE-03, open) (v107 row 4) |

- New categories `PERSONAL_CARE` (Culinary, Hospitality, Survivalist) and `ARCANE` (Magic) are proposals; the workbook has no category for these flags.
- The TRAIN_COMBAT workbook note "can improve later through training systems" is superseded by PERS-15.

## Open items

- PERS-OPEN-07: How traits and training affect tasks, events, stress, and compliance.
- PERS-OPEN-08: How agents get trained after hiring (cost, time, location).
- PERS-OPEN-09: Structured links from trainings to the tasks and personal-care services they allow away from designated locations; to be added with the personal-care services slice.
- PERS-OPEN-10: Weighted new-hire skill rolls (PERS-19).
- Roll distribution for trait RANDOM_IN_RANGE (assumed uniform).
