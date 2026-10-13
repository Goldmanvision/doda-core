# FOIMS-X Tasks Screen - 2026-10-10

Added a Tasks screen and Debug Panel controls (template picker, Spawn Task,
Cancel Selected Task, Clear Tasks). Task instances use the sandbox strategic
minute as their clock; list state and details recompute on every render so
stepping or playing the clock updates remaining time and overdue flags.
Overdue is flagged only. Reset Session clears tasks. No assignment, no work
progress, no CSV writes. Added 7 tests.
