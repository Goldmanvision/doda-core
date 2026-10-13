# FOIMS-X Sandbox Task Board - 2026-10-10

Added doda_foims_x_tasks.py: in-memory task instances spawned from authored
templates. Copies capability, priority, target effort and deadline; rejects
missing/inactive templates and capabilities and invalid minutes. Overdue is
derived from the current minute and never stored; missed tasks stay open.
Cancel and reset supported. Takes the current minute as an argument; sandbox
clock integration and a Tasks screen follow. No GUI change, no CSV writes.
Added 9 tests.
