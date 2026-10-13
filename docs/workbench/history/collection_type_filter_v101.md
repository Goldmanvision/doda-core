# Collection type dropdown refinement v101

Collection Models filters Collection Type by current Collection Kind:
RECEPTACLE -> authored receptacle IDs.
DEVICE -> authored collection-device type IDs.
Blank or invalid kind -> no type choices.

Explicit Kind changes clear an incompatible Type only.
Evidence selections, multipliers, brand/version and other properties are retained.
Row selection, clear/new and CSV paste refresh the choices.
Ordinary refresh does not silently clear stored references.
Legacy two-argument reference_keys calls remain unfiltered.
No source data migration or runtime behavior.

Automated acceptance: 550 baseline tests; 560 after change.
Manual acceptance pending: filtered choices and explicit Kind-change clearing.
