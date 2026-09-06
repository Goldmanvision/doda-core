# Work in Progress & Open Decisions

### Confirmed Status
- **Native Strategic Baseline**: Personnel Snapshot V1 implemented and verified (Engine commit `4d7ef89286`, Native API v1, Save schema v2). State is read-only, persistent, and seeds 5 deterministic campaign-default personnel records on startup.
- **Native-to-ZScript Bridge**: Committed to `DoDA/Native/DoDA.zs` in `doda-core` and active in the root load graph via `#region NativeBridge` in `zscript.txt`.
- **Inert FOIMS-X Presentation Layer**: Three decoupled ZScript files implemented under `DoDA/UI/FOIMSX/PersonnelV1/` (`PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs`) providing pure data modeling, single-transaction bounded acquisition, and 8-state presentation view-state reconciliation. Files remain inert, isolated, and un-included.
- **Native Diagnostics Surface**: Confirmed that the 12 existing native query methods satisfy all diagnostic, compatibility, revision stability, bounding, and error classification requirements without requiring additional native endpoints.

### Planned
- **FOIMS-X UI Presentation**: Terminal, HUD, and menu presentation consuming the inert view-state logic once visual integration is authorized.
- **Lean Lifecycle Extraction**: Moving lean input and controller update logic from `DoDAWeapon` to an independent player-owned ability lifecycle.
- **Future Snapshot Extensions**: Read-only query contracts for Cases, Assignments, and Strategic Time.
- **Tactical-to-Macro Bridge**: Validated event submission actions for reporting tactical mission outcomes.

### Investigation
- **HUDDeadzone Rendering Failure**: Diagnosing why deadzone crosshair HUD overlay fails to draw on screen.
- **Deadzone Camera Locking**: Implementing view locking during Deadzone Aim mode.
- **Shotgun Subsystem**: Under active runtime stabilization; documentation deferred until stabilized.
- **MP5 Trajectory Alignment**: Replacing `A_FireBullets` with deadzone-aware trace calculations.

### Open Decisions
- `DoDA/Aim/DeadzoneController.zs`: Orphaned component. Decision required on permanent removal vs archival.
- Configuration Lump Cleanup: Resolving overlapping definitions in `CVARINFO`, `KEYCONF`, and `MENUDEFS`.

### Resolved Decisions
- **Production Native Declarations**: Resolved. `struct DoDA native` is permanently placed in `DoDA/Native/DoDA.zs` and included in `zscript.txt`.
- **Campaign Fixture Route**: Resolved. Compiled native C++ initialization in `DoDASimulation::ClearForNewCampaign()` seeds the 5 default personnel records without runtime file I/O.
- **Diagnostics Native Scope**: Resolved. Existing 12 native methods completely satisfy adapter and diagnostics requirements.
