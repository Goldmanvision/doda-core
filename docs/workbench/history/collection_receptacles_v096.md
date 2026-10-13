# Collection receptacle foundation v096

CONFIRMED:
- Exactly two collection-receptacle types: evidence bags and chemical kits.
- Each Investigation agent carries a pistol and an applicable receptacle.
- Existing motor-vehicle requirement remains.
- Receptacles do not reclassify evidence categories.

Implemented:
- Two active catalog definitions; no inventory is created.
- Validation module and standalone export CLI.
- Main validation includes the catalog when present.
- Task Template candidate saves stage the new CSV.
- No computer/phone/PDA device-slot accounting changes.
- All existing source CSVs and weapon definitions are preserved.

Pending:
- GUI and Export All integration.
- Evidence-type collection mappings and task prerequisite tables.
- Kit capacity, consumption and missing-kit selection policy.
- Vehicle, surveillance and mobile-laptop authoring.
- Runtime inventory, eligibility and execution.

Acceptance: 504 baseline tests; 512 after installation.
