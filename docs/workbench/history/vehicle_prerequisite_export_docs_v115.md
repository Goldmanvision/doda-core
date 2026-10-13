# Vehicle prerequisite export documentation alignment v115

Only PRE-01 open-item text in the prerequisite export payload is changed.
Generic vehicle types and capacities are recognized as authored data.
Owned quantities, runtime capacity enforcement and allocation remain open.
No validation logic, source CSV, export schema or runtime behavior is changed.
Five regression tests cover:
- Corrected authored prerequisite description.
- Export/source description and requirement-semantic agreement.
- Updated exported PRE-01 wording.
- Vehicle export/source capacities and implementation boundaries.
- Temporary exports preserving authoring source files.
Expected tests: 663 baseline; 668 after installation.
Live generated JSON is refreshed separately using Export All.
