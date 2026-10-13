# Task Schema Migration - 2026-10-10

Removed task deadlines, target effort and template auto-allocation. Priority retained.
Added target type/family, loop flag, optional completion duration, reward mode and payout count.
Shared CSV/JSON contract is doda_task_schema.py. Blank completion duration is open-ended.
13 approved work templates are inactive drafts; unknown rates, skills and flows remain unconfigured.
Undercover templates span 7/14/31 days with three evenly spaced payouts, not deadlines.
Auto-allocation is department/personnel scheduling state. No runtime tasks or compatibility shim.
Source/export validation, editor, CRT reference notes and ZScript lookups migrated together.
Department schema version is 3. Runtime assignments and child requirement/flow/risk tables follow.
