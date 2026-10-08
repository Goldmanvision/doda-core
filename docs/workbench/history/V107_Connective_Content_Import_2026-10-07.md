# V107 connective content import

This is a bounded authoring-content import, not a gameplay or personnel-simulation implementation. Latest user decisions and the tested local source take precedence over workbook plans.

## Imported draft definitions

Eight well-formed capability definitions from `doda_01_department_progression_v107.xlsx`, `FacilityCapsCat`, have been mapped to the existing Workbench capability table. Their released workbook IDs are preserved. All eight are inactive drafts: they have no invented staffing ranges, facility installations, standing-operation labels, or qualification mappings.

| Workbook ID | Display name | Workbook cells |
| --- | --- | --- |
| CAP_FOOD | Food Access | FacilityCapsCat!A2:L2 |
| CAP_BASIC_MEDICAL | Basic Medical Care | FacilityCapsCat!A4:L4 |
| CAP_ADVANCED_MEDICAL | Advanced Medical Care | FacilityCapsCat!A5:L5 |
| CAP_THERAPY | Therapy Services | FacilityCapsCat!A6:L6 |
| CAP_EMERGENCY_TRANSPORT | Emergency Transport | FacilityCapsCat!A7:L7 |
| CAP_RESEARCH | Research Facility | FacilityCapsCat!A8:L8 |
| CAP_EVIDENCE_STORAGE | Evidence Storage | FacilityCapsCat!A9:L9 |
| CAP_ANOMALOUS_CONTAINMENT | Anomalous Containment | FacilityCapsCat!A10:L10 |

The existing ELECTRONIC_SURVEILLANCE and OCCULT_RESPONSE definitions remain active and unchanged. Existing qualifications, staffing defaults/overrides, facilities, and task templates remain unchanged.

The raw source rows, including fields not supported by the current CSV schema, are preserved separately in `data_authoring/reference/v107_connective_source_rows.json`. Unsupported resource, care/task-type, access-policy, role, and workbook-status fields have not been silently converted into gameplay rules.

## Blocked source rows

`FacilityCapsCat!A3:L3` (CAP_REST) and `FacilityCapsCat!A11:L11` (CAP_SAFE_HOUSING) are held back. In both rows, G contains a boolean although its header is `required_staff_or_role`; I contains `FUTURE` although its header is `allows_off_duty_agents`; K contains descriptive text although its header is `v1_status`; L is blank. This is a positional data defect, not an authorization to guess the intended booleans.

The same row patterns occur in the department, HQ/map, and combined schema-template workbooks. No uploaded workbook has been edited.

## Qualification and task boundaries

The uploaded workbook sheet inventories do not include a qualification catalog. `doda_02_personnel_and_operations_v107.xlsx`, `TrainingCat!A2:M6`, defines TRAIN_COMBAT, TRAIN_INVESTIGATIVE, TRAIN_MEDICAL, TRAIN_RESEARCH, and TRAIN_ADMINISTRATIVE. These are training definitions, not the existing staffing qualifications.

For example, `FacilityCapsCat!G4` contains MEDIC_OR_MEDICAL_STAFF and `FacilityCapsCat!G6` contains THERAPIST_OR_APPROVED_PROVIDER. These role alternatives need explicit qualification mappings; they have not been replaced by fabricated qualification IDs or contributor counts.

Workbook task-type references also need reconciliation. Basic/Advanced Medical Care reference TASK_HEAL in `FacilityCapsCat!E4:E5`, whereas the personnel workbook uses TASK_MEDICAL_ATTENTION and TASK_INJURY_STABILIZATION in `TaskTypesCat!A5:A6`. Required training tokens MEDICAL_TRAINING, INVESTIGATIVE_TRAINING, and RESEARCH_TRAINING in TaskTypesCat differ from the released TRAIN_* IDs in TrainingCat. Neither set has been silently renamed.

## Governance retained

The governance workbook's `README!B6:B9` requires native-owned live state, stable identity, compiled authoring data rather than runtime Excel reads, and preservation of released IDs. `TermDictCat!A10:J15` separates hidden Nutrition from visible hunger warnings, strategic Health from Current/Base HP, and Injury from Health. Those definitions inform the next personnel contract; they do not authorize new runtime mechanics.

## Care-service decisions (CONFIRMED 2026-10-07)

- CARE-01: Medical care and therapy are not player-staffed services. They must not receive capability staffing rules or staffing qualifications.
- CARE-02: Emergency medical care is automated and free of cost. Treatment duration, healing amounts, and recovery effects remain OPEN.
- CARE-03: Agents may deliver medical attention through a skill/training (TRAIN_MEDICAL). This is an agent competency, not facility staffing.
- CARE-04: The player assigns an agent to therapy treatment; the provider is handled automatically. Therapy cost, duration, and effects remain OPEN.
- CARE-05: Care services are authored in their own catalog, separate from capabilities and staffing rules. The v107 starting reference is `doda_05_remediation_and_care_v107.xlsx`, `RemedyCat`.
- CARE-06: The care catalog holds medical and therapy services only. Eating, Resting, Off Duty, and Decompression belong with the personnel slice. Retrieval (needs a player-assigned agent) and Resurrection (deferred/archived) are excluded.
- CARE-07: Emergency services (Hospitalization, Injury Stabilization, Emergency Medical Transport) are free. Non-emergency medical care and both physical and psychological therapy have costs; amounts are OPEN.
- CARE-08: Basic Medical Care, Advanced Medical Care, and Therapy Services are places where care services can happen. They are care location features, not staffed capabilities. A service can happen at a place with any one of its linked features.
- CARE-09: Emergency Medical Transport happens at no place. It brings incapacitated agents to a hospital for Advanced Medical Care, so hospitals provide Advanced Medical Care. `care_services.destination_feature_id` records where a service delivers the agent, and the service's follow-up must be offered at that destination.
- CARE-10: Therapy Services offers both Psychological and Physical Therapy. Emergency Hospitalization is offered at Advanced Medical Care, and Medical Check-Up at Basic Medical Care.
- CARE-11: All care happens at hospitals. Every hospital provides Basic Medical Care, Advanced Medical Care, and Therapy Services. An operational territory may have one or more hospitals of varying quality and cost. The care catalog export records this as `careProvider` (HOSPITAL, provides all features, one or more per territory, varies by quality and cost). Hospital records are deferred to territory/location authoring, which does not exist yet; the only v107 reference is the example `LOC_CITY_HOSPITAL` in `PersLocCat`.

## Care services catalog (implemented 2026-10-07)

`data_authoring/source/care_services.csv` holds eight inactive draft rows taken from `RemedyCat` rows 3, 5-10, and 15, keeping the released REMED_* IDs: Emergency Medical Transport, Emergency Hospitalization, Injury Stabilization, Medical Attention, Medical Check-Up, Recovery, Psychological Therapy, and Physical Therapy. Durations are blank (undecided) because the workbook's duration cells were converted to dates by Excel. Workbook follow-ups that point outside the catalog (Retrieval, Off Duty) are left blank.

Deliberate departures from the workbook, per the decisions above: emergency rows are AUTOMATIC and FREE although RemedyCat marks them as player-scheduled with a hospital-service cost; Physical Therapy is categorized as THERAPY; Recovery is COSTED (workbook cost policy: paid leave).

The validator (`doda_care_rules.py`) enforces CARE-02, CARE-04, and CARE-07, checks follow-up references and loops, and warns when an active service has no duration. The catalog appears as Personnel and Care > Care Services in the Workbench, joins Validate All and Export All, and exports `generated/data/care_services_catalog.json` with `runtimeImplemented: false`. It is not part of the FOIMS-X ZScript catalog.

### Care locations (CARE-08)

CAP_BASIC_MEDICAL, CAP_ADVANCED_MEDICAL, and CAP_THERAPY moved, with their IDs unchanged, from `capabilities.csv` to `data_authoring/source/care_location_features.csv` (3 inactive drafts). `care_service_locations.csv` links services to features. It has eight inactive links. Four come straight from `FacilityCapsCat!D4:D5`, and four were confirmed by the user (CARE-10):

| Location feature | Services offered |
|---|---|
| Basic Medical Care | Medical Attention, Injury Stabilization, Medical Check-Up |
| Advanced Medical Care | Medical Attention, Recovery, Emergency Hospitalization |
| Therapy Services | Psychological Therapy, Physical Therapy |

The workbook's `REMED_THERAPY` alias is resolved as both therapy services. Emergency Medical Transport has no location link; its destination is Advanced Medical Care (CARE-09), and its follow-up, Medical Attention, is offered there.

All three features are provided by hospitals (CARE-11). Still OPEN: hospital records per territory and how quality and cost vary (CARE-OPEN-05).

The Workbench shows them as Personnel and Care > Care Locations and Care Service Locations. The link table uses a two-column key (service + feature).

Consequently, the workbook role values MEDIC_OR_MEDICAL_STAFF, MEDICAL_STAFF, and THERAPIST_OR_APPROVED_PROVIDER (FacilityCapsCat!G4:G6) are not to be mapped to qualifications. That non-staffed model now exists as care locations (CARE-08), so these three features no longer live in `capabilities.csv`.

## Next bounded decisions

- Confirm the intended CAP_REST and CAP_SAFE_HOUSING access-policy booleans.
- Decide care-service costs, durations, and effects, then activate rows.
- Define hospital records (per territory, quality, cost) when territory/location authoring starts.
- Map the remaining staff-role alternatives (transport, research, custody, containment) to qualifications, separately from training thresholds.
- Select facility installations and authored staffing ranges before activating the new drafts.
- Reconcile workbook facility aliases without replacing existing Workbench IDs or treating throughput capacities as personnel capacities.

Inactive draft rows are visible in the Workbench capability editor but are deliberately omitted from the active FOIMS-X catalog. Export All should preserve the active runtime proof until those mappings are approved.

## Verification and rollback

The candidate table and the updated local source both passed the existing content validator with zero errors. The content JSON and PK3 overlay exported successfully. The exported capability table contains 10 rows, of which the original 2 remain active; the 8 new rows are inactive drafts. All 57 Python tests passed. The generated ZScript catalog passed its currentness check and its SHA-256 stayed unchanged, so no runtime catalog rows were activated by this import. No new in-game test was performed.

Original source and affected generated artifacts were backed up under `data_authoring/backups/v107_connective_20261007_052455`. The imported source file is `data_authoring/source/capabilities.csv`; qualifications and all relationship tables were left unchanged. The uploaded workbooks were not modified.
