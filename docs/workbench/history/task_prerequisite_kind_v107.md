# Task Prerequisites dependent fields v107

Explicit Requirement Kind selection:
- WEAPON_TYPE sets per-agent scope and AGENT role, preserving a valid weapon type.
- Applicable receptacle sets per-agent scope and AGENT role, clearing value.
- Motor vehicle sets TASK scope, clearing role and value.
- Invalid weapon values clear only after explicit Kind selection.

Ordinary choice refresh never rewrites stored scope, role or value.
Row selection, clear/new and CSV paste refresh dependent choices.
Quantity, description, Active, and IDs are unchanged by Kind selection.
Blank quantity is never assigned an invented default.
Apply to List and Save to Source remain separate.
No source CSV migration, runtime checks, allocation or inventory.

Automated acceptance: 598 baseline tests; 606 after installation.
Manual acceptance pending: explicit Kind changes and selection restoration.
