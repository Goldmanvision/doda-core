# Remove Incorrect Sandbox Task Spawner - 2026-10-10

Removed deadline-based TaskBoard and TasksCatalog runtime modules,
Tasks screen, task-spawning controls and six preview helper methods.
Removed 16 tests of the rejected runtime design; added four regression
tests of removal and retained session reset/catalog/debug behavior.
Personnel, Debug Panel, sandbox clock/metrics/Evidence remain intact.
Source CSVs and generated catalogs are unchanged in this block.
Authoring schema migration follows; no runtime compatibility shim retained.
