# Alcohol and Sobriety Import - 2026-10-08

Authoring, validation and export only; no runtime behaviour. runtimeImplemented is false in every new export. Decisions are in DESIGN_DECISIONS_2026-10-08.md.

## New module and tables
- doda_sobriety_rules.py (0.1.0): sobriety_stages.csv (4 rows), sobriety_settings.csv (2), sobriety_shift_rules.csv (3). Exports generated\data\sobriety_catalog.json.
- Pages in the Recreation subgroup: Sobriety Stages, Sobriety Settings, Sobriety Shift Rules.

## Changes to existing modules and data
- doda_recreation_content_rules.py: new scales INTOXICATION_GAIN (percent of the intoxication range) and HUNGER_LOSS (percent of the nutrition range). effect_levels.csv now has 49 rows: seven levels per new scale, with starting values 5 to 35 on INTOXICATION_GAIN.
- doda_personal_care_rules.py: activity columns intoxication_gain_level_id, off_duty_only and hunger_loss_level_id; new feature CAP_ALCOHOL. An activity with an intoxication level may sit at a place type that offers CAP_ALCOHOL instead of CAP_RECREATION. The vacation-return reset list now includes INTOXICATION.
- condition_stats.csv: new INTOXICATION stat (CONDITION, 0-100, not counted toward Health).
- personal_care_features.csv and personal_care_place_type_features.csv: CAP_ALCOHOL on PLACE_BAR_LOUNGE, PLACE_RESTAURANT and PLACE_VACATION_RESORT.
- recreation_activities.csv: 12 inactive drink activities with energy_required_to_start 10.
- doda_page_registry.py, doda_network_editor.py and doda_content_gui.py: pages, editors, draft validation and export wired in.

## Tests
- 159 passing at the start of the work, 214 at the end. New test files: test_recreation_effect_scales, test_personal_care_effects, test_intoxication_activity, test_intoxication_scale, test_sobriety_rules, test_alcohol_places, test_shipped_data (validates the real data), test_vacation_return, test_editor_coverage (every registry table has an editor) and test_sobriety_scope.

## Backups
- Per-file .bak_<timestamp> copies made during the session were moved into backups\vNNN_alcohol_sobriety_session_<timestamp> with a MANIFEST.txt of SHA-256 hashes.