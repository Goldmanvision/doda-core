# Vehicle prerequisite description correction v114

Only PRE_INVESTIGATE_VEHICLE.description is changed.
Old sentence: Vehicle catalog and runtime capacity/allocation checks are not implemented.
New sentence: Generic vehicle types are cataloged; runtime capacity enforcement and allocation are not implemented.

Generic vehicle types now exist; runtime capacity enforcement and allocation do not.
All prerequisite IDs, kinds, scopes, roles, values, quantities and active flags are unchanged.
No Python application files or export schemas are changed.
CSV encoding and line endings are preserved by exact byte replacement.
Candidate temporary export checked; no live generated outputs overwritten.
Acceptance: 663 tests before and after; one description field changed.
