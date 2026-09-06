# Junie Changelog

## [2026-08-22 00:45:00] - FOIMS-X Static Host Save/Restore Non-Serialization Proof & Cleanup

### Completed
- Completed the FOIMS-X static host save/restore proof: verified that `DoDAFOIMSXHostLifecycleProbe : StaticEventHandler` instance fields persist in memory during an in-process save/restore sequence without being rewound to save-time state, that registration occurs exactly once per engine session (`event=register scope=static`), and that `WorldLoaded()` is received on save restore with `e.IsSaveGame = true`.
- Removed all temporary `mWorldLoadedCount` lifecycle-counter instrumentation and restored `DoDA/UI/FOIMSX/FOIMSXHostLifecycleProbe.zs` to its exact clean pre-counter baseline (`4F7F8A8908F791B3728E70010A7C23F5AD895DF993D3063089CE8CD4C569FF2B`, 1078 bytes, 28 lines).
- Preserved all proof logs and dedicated save artifacts (`log-foimsx-static-host-save-restore-2026-08-21-23-54-00.txt`, `log-foimsx-static-host-save-restore-final-2026-08-22-06-59-00.txt`, `dodafoimsxsrtest.zds`).
- All other files (`MAPINFO`, `zscript.txt`, Personnel V1 files, `BackgroundSimPOC.zs`, `DoDA.zs`, native engine worktree) remain untouched and byte-identical to baseline.

### Verified Artifacts
- Cleanup Baseline Hash: `DoDA/UI/FOIMSX/FOIMSXHostLifecycleProbe.zs` -> `4F7F8A8908F791B3728E70010A7C23F5AD895DF993D3063089CE8CD4C569FF2B`
- Preserved Proof Logs:
  - `cmake-build-debug/log-foimsx-static-host-save-restore-2026-08-21-23-54-00.txt` (10757 bytes, SHA-256 `44D4D27B0DC84654C0AD08A238708B36C14D92CC68805B792375409902D9BB24`)
  - `cmake-build-debug/log-foimsx-static-host-save-restore-final-2026-08-22-06-59-00.txt` (13398 bytes, SHA-256 `7580E2F9AB2C0927B438EFE245A17E03E80A199F005399582159BCB60F4400AA`)
  - `C:\Users\nicka\Saved Games\UZDoom\doom.freedoom.phase2\dodafoimsxsrtest.zds` (187030 bytes, SHA-256 `18C7DFFF01134A515BBBCB2D5D73A87680BD40FB92FE2F46CB7CBDA93C9C15A4`)

## [2026-08-21 23:25:00] - FOIMS-X Static Host Lifecycle Proof

### Completed
- Added the dedicated, empty FOIMS-X static host `DoDAFOIMSXHostLifecycleProbe : StaticEventHandler` in the new file `DoDA/UI/FOIMSX/FOIMSXHostLifecycleProbe.zs`, included through one new `FOIMSXHostLifecycleProbe` region in `zscript.txt` after the active Personnel V1 region, and registered by appending the class name to the existing `gameinfo AddEventHandlers` list in `MAPINFO`. The class overrides only `OnRegister()` and `WorldLoaded(WorldEvent e)` and declares no field.
- Single-session MAP01 → MAP02 runtime proof on the existing Win32 debug `uzdoom.exe` with no native rebuild: registration occurred exactly once per engine session (`event=register scope=static`), and `WorldLoaded()` occurred exactly once for MAP01 and once for MAP02 (`map=MAP01` and `map=MAP02`, both `hqEligible=no`), the map name being read from the loaded level rather than hardcoded. The transition used the stock engine console command `changemap MAP02` (`CCMD (changemap)`, `src/console/c_cmds.cpp`); no command, keybind, event or test helper was added to cause it.
- No snapshot acquisition, ViewState instance, selection state, drawing, input, UI/tick processing, native mutation, persistence operation, task/assignment change or strategic-time action was added; the probe emitted no lines other than the three lifecycle records. Log shows zero ZScript errors, exactly the two pre-existing `shotgun.zs:540` truncation warnings, normal MAP01 BackgroundSimPOC progression (`0 → 60 → 120 → 180 → 240` strategic minutes, `0% → 25% → 50% → 75% → 100%`, normal completion auto-stop) and zero `[DoDA-FOIMSX-PersonnelV1-Proof]` occurrences.
- `PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs`, `DoDA/Native/DoDA.zs` and `DoDA/POC/BackgroundSimPOC.zs` (`2F59EC72BAE26FDF4966EE0BA19D92B4DFA9D8FBDC6EB0FB85F540D8C9486EA5`, 8044 bytes) remain byte-identical; the native engine worktree is clean at `d81345126e9d74c0a266ed00f12e7f8961e3c291`.
- Scope limit: this proves registration-once and map-lifecycle callbacks for an otherwise empty static FOIMS-X host only. It does not yet prove save/restore refresh behavior or snapshot freshness across map transitions.

### Verified Artifacts
- Proof log: `cmake-build-debug/log-foimsx-static-host-lifecycle-2026-08-21-23-25-00.txt`
  - Size: `18987` bytes
  - SHA-256: `C3E02D3813BBF10C902A7E27A07E46CCFA57E83E6D855E1F0CF1E3E7A0E8E165`

## [2026-08-21 17:10:00] - FOIMS-X Personnel Snapshot V1: Temporary Proof-Harness Removal Proof

### Completed
- Removed the temporary Personnel Snapshot V1 read-only probe from `DoDA/POC/BackgroundSimPOC.zs`: the single `RunPersonnelV1ReadOnlyProof();` call in `DoDABackgroundSimPOC.WorldLoaded()` and the complete private `RunPersonnelV1ReadOnlyProof()` method with its temporary comments. Removal-only; no adjacent code, EventHandler registration, `WorldTick`, `InputProcess`, `NetworkProcess`, debug controls, strategic stepping, reset behavior or legacy `DoDA.GetPersonnelSnapshot*` diagnostics were altered. The file is now byte-identical to its pre-probe state (`2F59EC72BAE26FDF4966EE0BA19D92B4DFA9D8FBDC6EB0FB85F540D8C9486EA5`, 8044 bytes).
- Zero remaining source matches for `RunPersonnelV1ReadOnlyProof` or `[DoDA-FOIMSX-PersonnelV1-Proof]`. The earlier read-only round-trip proof log remains preserved unmodified (`log-foimsx-personnel-v1-readonly-roundtrip-2026-08-21-15-12-00.txt`, 12031 bytes, SHA-256 `1D29FCF3ABA24D864BDCCFE5D59A6B9BFB6D18343F68DD04EDF28FA89D5CA69D`).
- MAP01 regression proof on the existing Win32 debug `uzdoom.exe` with no native rebuild: zero ZScript errors, exactly the two pre-existing `shotgun.zs:540` truncation warnings, normal BackgroundSimPOC startup, progression `0 → 60 → 120 → 180 → 240` strategic minutes with `0% → 25% → 50% → 75% → 100%` task progress, normal completion auto-stop, and zero `[DoDA-FOIMSX-PersonnelV1-Proof]` occurrences.
- Personnel V1 returns to compile-active but runtime-uninstantiated: no FOIMS-X host, container, EventHandler, drawing, input, mutation, persistence write, task/assignment change or added time behavior. `PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs` and `zscript.txt` are byte-identical to their pre-edit baselines; the native engine worktree is clean at `d81345126e9d74c0a266ed00f12e7f8961e3c291`.
- Audit note: `PersonnelSnapshotV1ViewState.zs` measured `E0219B6A443E92773AEDC870C76A12F1D68471FD9F24E3452B0301CE78AC2884` / 6962 bytes at pre-edit audit, one byte larger than the 15:12:00 record (`735D2166…` / 6961 bytes). The difference is a stray backtick inside the line-1 banner comment, introduced outside this pass; it is inert, was left untouched, and compiles without error.

### Verified Artifacts
- Removal proof log: `cmake-build-debug/log-foimsx-personnel-v1-proof-harness-removal-2026-08-21-17-10-00.txt`
  - Size: `11438` bytes
  - SHA-256: `FF33534DB812456E25F986AD2EEC306DD1CF2BC0C0F6914F48C232317A6CC9FE`

## [2026-08-21 15:12:00] - FOIMS-X Personnel Snapshot V1: Read-Only Runtime Round-Trip Proof

### Completed
- Added a temporary, reversible one-time read-only probe (`RunPersonnelV1ReadOnlyProof()`) to the existing MAP01 seam `DoDABackgroundSimPOC.WorldLoaded()` in `DoDA/POC/BackgroundSimPOC.zs`; it is the only file changed. `PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs` and `zscript.txt` remained byte-identical.
- The probe acquires via `DoDAPersonnelSnapshotV1Adapter.AcquireSnapshot()` only, projects through `DoDAPersonnelSnapshotV1ViewState.UpdateFromSnapshot()`, exercises one `SelectById()` identity match using exact `PersonIdText` string equality, and emits exactly one `[DoDA-FOIMSX-PersonnelV1-Proof]` line. No new native snapshot call site, EventHandler, container, rendering, input, console command, mutation, persistence write, task/assignment change, strategic-time advance or per-tic polling was added.
- Runtime proof on the existing Win32 debug `uzdoom.exe` with no native rebuild: zero ZScript errors, exactly the two pre-existing `shotgun.zs:540` truncation warnings, normal MAP01 startup, and BackgroundSimPOC progression identical to the prior baseline run (0 → 240 strategic minutes, 0% → 100%, revisions 1–5).
- Proof line observed once, at strategic minute `0` / revision `1`: `apiVersion=1 apiAccepted=yes acquisitionState=5 (ACQUISITION_POPULATED) personnelCount=5 viewState=6 (VIEWSTATE_UNASSIGNED) selection=exact-match selectedPersonIdText=1 mutation=none-readonly`. Count `5` and the unassigned first record (`Ruth M. Green`, id `1`) match the native default fixture in `src/doda/DoDA_Simulation.cpp`.
- Pre-existing scope note (unchanged, not remediated here): the legacy temporary debug harness `BackgroundSimPOC` still contains its own direct `DoDA.GetPersonnelSnapshot*` diagnostic calls that predate the V1 contract, so the Adapter is the sole caller of the V1 acquisition path but not literally the only ZScript caller of the raw native snapshot API.

### Verified Artifacts
- Proof log: `cmake-build-debug/log-foimsx-personnel-v1-readonly-roundtrip-2026-08-21-15-12-00.txt`
  - Size: `12031` bytes
  - SHA-256: `1D29FCF3ABA24D864BDCCFE5D59A6B9BFB6D18343F68DD04EDF28FA89D5CA69D`

## [2026-08-21 14:56:00] - FOIMS-X Personnel Snapshot V1: `State` Keyword Remediation & Compile-Activation Proof

### Completed
- Renamed the `DoDAPersonnelSnapshotV1ViewState` field `State` to `CurrentViewState` in `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1ViewState.zs` (declaration plus 10 assignment sites), resolving the ZScript `TK_State` keyword conflict that produced 10 parser errors; `PersonnelSnapshotV1Model.zs` and `PersonnelSnapshotV1Adapter.zs` remained byte-identical.
- Activated Personnel Snapshot V1 by adding the `FOIMSXPersonnelV1` include region (Model, Adapter, ViewState) to `zscript.txt` after the `UserInterface` region and downstream of `NativeBridge`; no other include ordering or content changed.
- Compile-startup proof on the existing Win32 debug `uzdoom.exe` with no native rebuild: zero ZScript errors, exactly the two pre-existing `shotgun.zs:540` truncation warnings, normal MAP01 startup and normal BackgroundSimPOC execution.
- No FOIMS-X runtime behavior added: no EventHandler, host container, registration, rendering, input, console commands, mutation, or gameplay effect.

### Verified Artifacts
- Proof log: `cmake-build-debug/log-foimsx-personnel-v1-keyword-remediation-2026-08-21-14-56-00.txt`
  - Size: `11782` bytes
  - SHA-256: `7BF5A2EE8B62DF28B737708DD49615CA7A1DA73DE9734D44109A868702671307`
- Prior failure log preserved unchanged: `cmake-build-debug/log-foimsx-personnel-v1-compile-activation-2026-08-21-14-50-00.txt`
  - Size: `2575` bytes
  - SHA-256: `8B830BA7D667FDD7A145DC2A87CD00359C78011581502A023F02B741251BD968`

## [2026-08-21 14:18:00] - Schema 2 Assignment Validation Fix & Save/Load Identity Correction Proof

### Completed
- **Defect.** Schema 2 assignment validation in `src/doda/DoDA_Simulation.cpp` falsely required task IDs to be unique across assignment records and therefore rejected the valid default fixture, whose two personnel are both assigned to Task 1. Every load aborted with `Schema 2 task ID 1 appears in multiple assignments; reset to default state.`
- **Correction.** Removed only that invariant, so a task may legitimately carry multiple personnel assignments. Unique assignment IDs, unique per-person assignment (one active assignment per person), assignment ID range/counter checks, negative-cost rejection, person/task cross-link existence checks and person/task `Assigned` status consistency checks are all retained unchanged. Serialization layout, `DODA_SAVE_SCHEMA_VERSION = 2`, location persistence, scheduler rules, harness controls, UI, maps, FOIMS-X and LibColony untouched.
- **Rebuild.** Cached-CMake Debug x64 rebuild under `VsDevCmd.bat -arch=x64 -host_arch=x64` succeeded, including `[25/26] Building CXX object src\CMakeFiles\zdoom.dir\doda\DoDA_Simulation.cpp.obj` and `[26/26] Linking CXX executable uzdoom.exe` — exit code `0`.

### Runtime Proof (MAP01, manual keyboard controls only)
- Saved at strategic minutes `120` / Task 1 progress `50%`, diverged to `180` / `75%`, then loaded that saved slot.
- Reload restored `[DoDA] Restore: Successfully loaded Schema 2 state (5 people, 1 tasks, 2 assignments, 120 minutes).` — Task 1 `Survey anomalous emissions` at `50%`, status `1` (Assigned).
- `Michelle C. Thomas (id 2)` and `Brian C. Gordon (id 3)` both restored as status `1` (Assigned) with workload `1`.
- One further post-load 60-minute step reached `180` minutes / `75%`, proving continued progression after restore; no `multiple assignments` error occurred in any restore.

### Deferred / Not Observable
- **Deferred persistence blocker — location serialization.** Fixture-only location persistence remains deferred: `mLocations` and `mNextLocationId` are still not serialized and are reconstructed from the hardcoded fallback (ID `1`, `Morrow Point Waterworks`, `mNextLocationId = 2`). Full location persistence requires a future schema-versioned save/load identity batch.

### Verified Artifacts
- Original failure log (preserved unchanged): `cmake-build-debug/log-2026-08-21_13-51-00_background-sim-save-load-identity-proof_log-doda-background-sim-save-load-identity.txt`
  - Size: `23196` bytes
  - SHA-256: `2B148C6E0CAD19085520FD4D314478B4505E3D396A5001A551F348010834AFAB`
- Correction proof log (preserved unchanged): `cmake-build-debug/log-2026-08-21_14-05-44_background-sim-save-load-identity-correction-proof_log-doda-background-sim-save-load-identity-fix.txt`
  - Size: `18275` bytes
  - SHA-256: `68E38A1A11E675F9CE48AF267861FB1F5173455B4651625D2DCB9ADC045A12C3`

## [2026-08-21 13:45:00] - Background Simulation POC: Review Triage & MAP01 Runtime Proof

### Completed
- Triaged the code-review findings against the Background Simulation POC scope; accepted two targeted native fixes and explicitly deferred the rest.
- `src/doda/DoDA_Simulation.cpp` — `AdvanceStrategicMinutes()`: restricted automatic progress accrual to `DoDATaskStatus::Assigned` only. `Pending`/unassigned tasks can no longer accrue progress or self-complete with zero personnel released.
- `src/doda/DoDA_Simulation.cpp` — Schema 2 load validation: added a task `progress < 0 || progress > 100` rejection to the existing task validation loop, matching the surrounding `ResetPersonnelSnapshotAfterLoadFailure()` + reset-to-default pattern.
- `src/doda/DoDA_Simulation.cpp` — save path: removed the `location_id` write for tasks. This branch was persisting `task.LocationId` while `mLocations`/`mNextLocationId` were never serialized. The tolerant optional read (`if (arc.HasKey("location_id"))`, default `1`) is retained for in-branch saves; `DODA_SAVE_SCHEMA_VERSION` remains `2`.
- `DoDA/POC/BackgroundSimPOC.zs`: declaration-only correction. The harness referenced `EVENT_START`, `EVENT_PAUSE`, `EVENT_STEP`, `EVENT_SMALLSTEP`, `EVENT_RESET`, `EVENT_STATUS`, `EVENT_PERSONNEL` and `EVENT_CONTROLS` without ever declaring them (`Unknown identifier`, script compilation aborted). Added a single file-local const block with the `DoDAPOC*` names; all send and comparison call sites are unchanged.
- Rebuilt `zdoom` (Ninja / VS BuildTools, existing `cmake-build-debug` cache) and ran the MAP01 harness to completion using the existing POC controls and preserved a durable engine log.

### Runtime Proof (MAP01)
- Script compilation completed with 0 errors (only the two pre-existing `shotgun.zs:540` float-truncation warnings, out of scope).
- New campaign fixture: 5 personnel, 1 location (`Morrow Point Waterworks`), 1 task, 2 assignments. Native API v1, Personnel Snapshot API v1.
- Initial state: strategic minutes `0`, task 1 `Survey anomalous emissions`, progress `0%`, status `1` (Assigned).
- Throttled advancement, one strategic hour per five real seconds: `25%` @ 60 min, `50%` @ 120 min, `75%` @ 180 min, `100%` @ 240 min — exactly +25% per hour, no drift.
- Completion: task status `2` (Completed); `2 personnel returned to Available`; idle stepping stopped automatically.
- Personnel after completion: `Michelle C. Thomas (id 2)` and `Brian C. Gordon (id 3)` both status `0` (Available), workload `0`, task `''` — assignment records removed.
- Reset (keypad 0 / `DoDAPOCReset`): fixture reinitialized to strategic minutes `0`, task progress `0%`, status `1`, both staff status `1` (Assigned) with workload `1`; a post-reset status re-query confirmed the state is stable.

### Deferred / Not Observable
- **Deferred persistence blocker — location serialization.** `mLocations` and `mNextLocationId` are not serialized; post-load reconstructs the fixture location ID `1` (`Morrow Point Waterworks`) with `mNextLocationId = 2` via the hardcoded fallback. Full location persistence requires a future version-bumped save-schema batch (serializing both, a `DODA_SAVE_SCHEMA_VERSION` bump, a migration path, and save/load identity tests). Out of scope for this POC and must precede any future re-introduction of `location_id` into the save stream.
- **Deferred — fractional-minute remainder.** `(deltaMinutes * 25) / 60` still truncates, so sub-hour steps below 3 minutes add nothing and repeated sub-hour steps drift. The harness advances exactly one full strategic hour per step, so its 25% increments remain exact. Remainder accumulation carries persistence, reset and semantic decisions belonging to a dedicated strategic-time/persistence batch.
- **Not observable — Pending non-advancement.** The default fixture's only task ships as `Assigned` and no existing POC control creates a `Pending` task, so the Assigned-only restriction could not be demonstrated at runtime without extending the test surface. It is enforced at source level in `AdvanceStrategicMinutes()`.

### Verified Artifacts
- Proof Log: `wiki/junie/logs/2026-08-21_13-42-00_background-sim-poc-proof_log-doda-background-sim-poc-2026-08-21-13-40-00.txt`
  - SHA-256: `5CA26FC4B86BF3A43F60352D72A063D89898DA72BD1BD3895DAFC4A1B1CDDAE8`

### Scope Boundary Verification
- Implementation source files changed in this pass: `src/doda/DoDA_Simulation.cpp` and `DoDA/POC/BackgroundSimPOC.zs` only.
- Documentation/log artifacts: this changelog entry and the preserved MAP01 proof log (`wiki/junie/logs/2026-08-21_13-42-00_background-sim-poc-proof_log-doda-background-sim-poc-2026-08-21-13-40-00.txt`). No other documentation file was created or modified.
- `DoDA_SaveSchema.h` / `DODA_SAVE_SCHEMA_VERSION`: Untouched (`True`)
- `src/doda/DoDA_ZBind.cpp`, `DoDA/Native/DoDA.zs`: Untouched in this pass (`True`)
- FOIMS-X Personnel V1 inert files, TAB/TAPLINE, KEYCONF, MENUDEF, HUD, maps, weapons, missions, FONTDEFS, LibColony, save/load persistence: Untouched (`True`)

## [2026-08-21 12:44:00] - Changelog Consolidation & Single-File Enforcement

### Completed
- Consolidated all changelog records across the repository into `wiki/junie/CHANGELOG.md` as the single authoritative source of truth.
- Removed duplicate file `wiki/content/Changelog.md`.
- Integrated historical core systems documentation into `CHANGELOG.md`.
- Established changelog policy: all future updates, implementations, task completions, test proofs, and architectural milestones must have entries added exclusively to `CHANGELOG.md`.

## [2026-08-21 12:40:00] - Milestone Progress & Status Report Review & Synchronization

### Completed
- Conducted comprehensive milestone review and status assessment across all active DoDA subsystems:
  - **Milestone 1 — Native Strategic Core & Bridge (Complete)**: Confirmed 12-method read-only Personnel Snapshot V1 C++ contract (`DoDASimulation`, `DoDA_ZBind.cpp`) (Native API v1, Save Schema v2), active ZScript declaration (`DoDA/Native/DoDA.zs`), `#region NativeBridge` integration in `zscript.txt`, and deterministic 5-person native campaign default fixture.
  - **Milestone 2 — FOIMS-X Presentation Architecture (Inert Complete)**: Confirmed 3 decoupled, inert ZScript presentation classes (`PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs`) under `DoDA/UI/FOIMSX/PersonnelV1/` with verified single bounded transaction, complete validation, pre/post revision stability checks, 8 discrete presentation states, and strict `PersonIdText` selection identity; un-included and unregistered with zero runtime overhead.
  - **Milestone 3 — Documentation & Wiki Synchronization (Complete)**: Synchronized all technical records across `doda-core/wiki/` (`NativeZScriptBridge.md`, `PersonnelSnapshotV1.md`, `ActiveLoadGraph.md`, `WIP.md`, `KnownIssues.md`, `Changelog.md`, `structure.html`, and durable proof reports) with 100% architectural alignment.
  - **Milestone 4 — Tactical Subsystems Baseline (Stable)**: Confirmed operational status of `FieldAgent` deadzone aim mode, angular offsets, smoothing, limits, `DoDALeanInput`/`DoDALeanController` lean math, B92/MP5K-SD weapons, auxiliary controllers, and mission ledger. Clean production state with zero test residue.
  - **Milestone 5 — Active & Upcoming Milestones Roadmap (Planned)**: Tracked planned lean ability lifecycle extraction to `DoDA/Abilities/`, `HUDDeadzone` screen drawing investigation, deadzone camera locking, B92 firing integration, and the Weekend V2 Persistent Operational Slice (native strategic clock progression, 2–3 locations, 2–4 tasks, save/load round-trip, read-only FOIMS-X browsing).
- Updated `doda-core/wiki/content/Changelog.md` and `doda-core/wiki/junie/CHANGELOG.md` with complete milestone progress and status report entries.

## [2026-08-21 12:35:00] - Comprehensive Systems Wiki & Documentation Synchronization

### Completed
- Synchronized all technical records under `wiki/content/` with current confirmed source implementation:
  - `NativeZScriptBridge.md`: Documented committed `DoDA/Native/DoDA.zs` placement, `#region NativeBridge` integration in `zscript.txt`, Save Schema Version 2 persistence boundary, campaign startup initialization in C++, 12 read-only query methods, and resolved placement decisions.
  - `PersonnelSnapshotV1.md`: Updated engine baseline commit (`4d7ef89286`), deterministic 5-person campaign default fixture details, inert FOIMS-X presentation tier architecture (`PersonnelSnapshotV1Model.zs`, `PersonnelSnapshotV1Adapter.zs`, `PersonnelSnapshotV1ViewState.zs`), diagnostics contract verification findings, and runtime proof evidence links.
  - `ActiveLoadGraph.md`: Added `#region NativeBridge` (`DoDA/Native/DoDA.zs`) as active root region, documented inert presentation files under `DoDA/UI/FOIMSX/PersonnelV1/`, and resolved the native binding bridge placement decision.
  - `WIP.md`: Updated confirmed status for native strategic baseline, native bridge, inert FOIMS-X presentation tier, and diagnostics surface; updated planned FOIMS-X rendering; resolved native declaration and campaign fixture open decisions.
  - `KnownIssues.md`: Resolved open decisions regarding native binding placement and diagnostics surface.
  - `Changelog.md`: Added comprehensive Systems & Architecture section covering native bridge, snapshot contract, campaign fixtures, inert presentation files, and diagnostics verification.
- Updated `wiki/structure.html` to include `NativeBridge` in the module directory.
- Created comprehensive diagnostics proof report in `wiki/junie/reports/2026-08-21_12-25-00_personnel-diagnostics-proof.md`.
- Verified consistency, integrity, and cross-references across all wiki documentation files.

## [2026-08-21 12:25:00] - FOIMS-X Personnel Snapshot V1 Native Diagnostics Contract Proof & Audit

### Completed
- Conducted thorough audit and evaluation of the 12 native read-only query methods on `struct DoDA native` against the requirements of `PersonnelSnapshotV1Adapter.zs` and downstream view-state presentation logic.
- Confirmed that existing native query contract fully satisfies all diagnostic, compatibility (`ApiVersion=1`), availability, revision stability (`RevisionText` pre/post comparison), strategic time tracking, collection bounding (`GetPersonnelSnapshotCount()`), row field extraction, and error classification requirements without leaking native internals or requiring any new native methods.
- Compiled `uzdoom.exe` (Debug x64) and executed standalone live runtime proof via temporary `DoDA/Test/TempPersonnelDiagnosticsProof.zs` handler.
- Verified live engine execution in UZDoom engine log: `ApiVersion=1`, `Rev=1`, `StratMin=0`, `Count=5`, `RevisionMatch=1`, and exact match on all 5 fixture person rows (Ruth M. Green, Michelle C. Thomas, Brian C. Gordon, Leonard M. Martin, Harold M. Beltz) with status 0, skills 5-8, workload 0%, and empty assignment triples.
- Verified 0 script, native, VM, assertion, or fatal errors.
- Cleaned up temporary test handler `TempPersonnelDiagnosticsProof.zs` and directory `DoDA/Test/`.
- Restored `zscript.txt` (#region Test removed, #region NativeBridge preserved) and `MAPINFO` (4 production handlers restored).
- Verified FOIMS-X inert presentation files remain untouched, un-included, and unregistered with verified matching SHA-256 hashes.
- Generated durable proof report `wiki/junie/reports/2026-08-21_12-25-00_personnel-diagnostics-proof.md`.

### Verified Artifacts
- Proof Report: `wiki/junie/reports/2026-08-21_12-25-00_personnel-diagnostics-proof.md`
- Presentation Files Hashes:
  - `PersonnelSnapshotV1Model.zs`: `B585AFB2DE73F19D363DC38C290F016EABF72581387AE76CAFD3ECE669106C6B`
  - `PersonnelSnapshotV1Adapter.zs`: `D7F87EA8924045997114EB8A87A369F91CA5CE0772612AFE3B88A0E068158C6C`
  - `PersonnelSnapshotV1ViewState.zs`: `9215451C18CFD0349D9A75787D4E6D3695F96523F3897A80E878AC2FF5E54C1E`

### Cleanup Verification
- `DoDA/Test/TempPersonnelDiagnosticsProof.zs`: Absent (`True`)
- `DoDA/Test/`: Absent (`True`)
- `DoDA/Native/DoDA.zs`: Present (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Present (`True`)
- `zscript.txt`: `#region NativeBridge` retained intact (`True`)
- `MAPINFO`: Restored to 4 production handlers (`True`)
- `src/doda/DoDA_Simulation.cpp`: Permanent default fixture retained (`True`)

## [2026-08-21 11:50:00] - FOIMS-X Personnel V1 Inert Files Implementation

### Completed
- Created the containing directory `DoDA/UI/FOIMSX/PersonnelV1/` (absent prior to creation).
- Implemented exactly the 3 approved inert, isolated Personnel V1 presentation files using the approved V3 specification verbatim:
  1. `PersonnelSnapshotV1Model.zs`: Pure data model representing snapshot metadata, record fields, structural assignment classification enum (`ASSIGNMENT_UNASSIGNED`, `ASSIGNMENT_ASSIGNED`, `ASSIGNMENT_INVALID`), acquisition state enum, and validation reason enum.
  2. `PersonnelSnapshotV1Adapter.zs`: Authorized read-only ZScript adapter owning the single bounded acquisition transaction with complete bounded-row validation and pre/post revision equality checking; zero auxiliary polling helpers.
  3. `PersonnelSnapshotV1ViewState.zs`: Pure presentation view-state model for the 8 required states (`UNAVAILABLE`, `INVALID_VERSION`, `EMPTY`, `STALE`, `OUT_OF_RANGE`, `SELECTED_PERSON_DISAPPEARED`, `UNASSIGNED`, `POPULATED`), persistent `PersonIdText` reconciliation, stale model retention, and diagnostic disappearance tracking without index selection.
- Enforced all architectural non-negotiables and review constraints:
  - All classes inherit exclusively from `Object`; zero inheritance of `EventHandler`, `StatusBar`, `BaseStatusBar`, `Menu`, or actor classes.
  - Zero diagnostics, `Console.Printf`, or test code.
  - `PersonnelSnapshotV1Adapter.zs` is the sole file calling native `DoDA.GetPersonnelSnapshot*` methods; zero direct native calls in Model and ViewState.
  - Opaque identity and token fields (`PersonIdText`, `RevisionText`, `StrategicMinutesText`, assignment/task IDs) retained as exact `String` types without numeric parsing.
  - Selection and lookup keyed strictly by exact `String` equality on `PersonIdText` (never row index).
  - Pre/post revision mismatch rejects candidate models (`IsValid = false`, `AcquisitionState = ACQUISITION_REVISION_CHANGED`, `ValidationReason = VALIDATION_REVISION_CHANGED_DURING_ACQUISITION`).
  - Full bounded-row validation rejects invalid candidate snapshots (negative count, size mismatch, blank ID, blank name, duplicate ID, invalid status, mixed assignment triple).
  - Assignment classification evaluated strictly from the complete triple without inferring assignment from raw status.
  - Raw status integer and raw enums preserved with all renderer stringification helpers removed.
  - Automatic fallback selection removed; disappearance clears `SelectedPersonIdText` and sets `PreviousSelectedPersonIdText` for diagnostics.
  - ViewState retains last accepted model as `STALE` on receiving rejected candidate snapshot.
  - Zero refresh loops, polling, renderers, root includes, or activation hooks.
- Preserved complete file and runtime isolation:
  - Zero modifications to existing files (`zscript.txt`, `MAPINFO`, `DoDA/Native/DoDA.zs`, `zscript.txt.native_bridge_pretest.bak` remain untouched).
  - Zero fourth file created.
  - Files remain un-included in `zscript.txt` and unregistered in `MAPINFO` (inert and isolated).
  - Zero compile, packaging, or runtime execution actions occurred.

### Created Artifacts & Hashes
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Model.zs`:
  - SHA-256: `B585AFB2DE73F19D363DC38C290F016EABF72581387AE76CAFD3ECE669106C6B`
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Adapter.zs`:
  - SHA-256: `D7F87EA8924045997114EB8A87A369F91CA5CE0772612AFE3B88A0E068158C6C`
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1ViewState.zs`:
  - SHA-256: `9215451C18CFD0349D9A75787D4E6D3695F96523F3897A80E878AC2FF5E54C1E`

### Isolation & Integrity Verification
- `DoDA/UI/FOIMSX/PersonnelV1/`: Created (`True`)
- `zscript.txt`: Untouched; `#region NativeBridge` retained intact without `#region Test` or UI includes (`True`)
- `MAPINFO`: Untouched; 4 production handlers retained (`True`)
- `DoDA/Native/DoDA.zs`: Untouched (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Untouched (`True`)
- `src/doda/DoDA_Simulation.cpp`: Permanent default fixture retained (`True`)

## [2026-08-21 11:35:00] - FOIMS-X Personnel V1 Inert Model, Adapter & ViewState Plan

### Completed
- Prepared plan-only specification and complete exact source contents for the 3 isolated Personnel V1 ZScript files under `DoDA/UI/FOIMSX/PersonnelV1/`:
  1. `PersonnelSnapshotV1Model.zs`: Pure data model representing snapshot metadata and record fields.
  2. `PersonnelSnapshotV1Adapter.zs`: Authorized isolation layer querying `DoDA.GetPersonnelSnapshot*` native methods.
  3. `PersonnelSnapshotV1ViewState.zs`: Pure presentation view-state model keyed by persistent `personIdText` with explicit state representation (`UNAVAILABLE`, `INVALID_VERSION`, `EMPTY`, `STALE`, `OUT_OF_RANGE`, `SELECTED_PERSON_DISAPPEARED`, `UNASSIGNED`, `POPULATED`).
- Enforced all architectural non-negotiables:
  - Zero inheritance of `EventHandler`, `StatusBar`, `BaseStatusBar`, `Menu`, or actor classes.
  - Zero diagnostics, `Console.Printf`, or test code.
  - Zero direct `DoDA` native calls outside `PersonnelSnapshotV1Adapter.zs`.
  - Identity and token fields (`personIdText`, `revisionText`, `strategicMinutesText`, assignment/task IDs) retained as exact `String` types without numeric parsing.
  - Selection keyed strictly by exact `String` equality on `personIdText`.
  - Zero polling loops, per-frame acquisition, or activation hooks.
- Preserved strict plan-only state: zero files created on disk pending review by Terra (Perplexity Coordinator) and authorization by Human Project Owner.

## [2026-08-21 11:25:00] - Native Populated-Personnel Default Fixture Implementation & Proof

### Completed
- Implemented 5 deterministic campaign-default person records in native C++ (`DoDASimulation::ClearForNewCampaign()` in `src/doda/DoDA_Simulation.cpp`) using lore-aligned names from the seed dataset without CSV parsing or runtime I/O.
- Compiled `uzdoom.exe` (Debug x64) and executed standalone read-only runtime proof via temporary `DoDA/Test/TempDefaultFixtureProof.zs` handler.
- Verified live engine execution in UZDoom engine log: `ApiVersion=1`, `Rev=1`, `StratMin=0`, `Count=5`, pre/post revision equality (`RevisionMatch=1`), and 5 populated rows (Ruth M. Green, Michelle C. Thomas, Brian C. Gordon, Leonard M. Martin, Harold M. Beltz) with status 0, skills 5-8, workload 0, and empty assignment/task fields.
- Verified 0 script, native, VM, assertion, or fatal errors.
- Cleaned up temporary test handler `TempDefaultFixtureProof.zs` and folder `DoDA/Test/`.
- Restored `zscript.txt` (#region Test removed, #region NativeBridge preserved) and `MAPINFO` (4 production handlers restored).
- Preserved `DoDA/Native/DoDA.zs` and `zscript.txt.native_bridge_pretest.bak` untouched.
- Retained permanent C++ campaign fixture changes in `src/doda/DoDA_Simulation.cpp`.
- Preserved durable proof log artifact, instruction file, and report in `wiki/junie/`.

### Verified Artifacts
- Proof Log: `wiki/junie/logs/2026-08-21_11-20-00_default-fixture-proof_log-doda-default-fixture-2026-08-21-11-20-00.txt`
  - SHA-256: `B607586A38C67E9526639FD47A805288470378A65E0B9C09F0B09331FBD3541C`
- Proof Report: `wiki/junie/reports/2026-08-21_11-25-00_default-fixture-proof.md`
- Instruction File: `wiki/junie/test-instructions/2026-08-21_11-20-00_doda-default-fixture-2026-08-21-11-20-00.md`

### Cleanup Verification
- `DoDA/Test/TempDefaultFixtureProof.zs`: Absent (`True`)
- `DoDA/Test/`: Absent (`True`)
- `DoDA/Native/DoDA.zs`: Present (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Present (`True`)
- `zscript.txt`: `#region NativeBridge` retained intact (`True`)
- `MAPINFO`: Restored to 4 production handlers (`DoDAMissionDirector`, `DoDAAimInput`, `Map03RangeStartHandler`, `MP5ModeHandler`)
- `src/doda/DoDA_Simulation.cpp`: Permanent default fixture retained (`True`)

## [2026-08-21 10:53:00] - Native Populated-Personnel Fixture Feasibility Audit

### Completed
- Conducted strict plan/inspection feasibility audit of native C++ simulation initialization and person record schema (`DoDA_Types.h`, `DoDA_Simulation.h`, `DoDA_Simulation.cpp`, `DoDA_ZBind.cpp`, `DoDA_SaveSchema.h`).
- Identified root cause of `Count=0` snapshot: `DoDASimulation::ClearForNewCampaign()` resets simulation state and initializes an empty `mPeople` vector on campaign boot/autostart.
- Evaluated `DebugResetFixture()` limitations (introduces unlinked placeholder names "Alice", "Bob", "Charlie" and requires prohibited runtime mutation calls).
- Evaluated and ranked 4 candidate fixture routes; recommended Route A (compiled native campaign default initialization in `DoDASimulation`) as the cleanest, 100% schema-compliant, read-only approach.
- Confirmed Save Schema 2 compatibility: deterministic population of 3–5 initial records conforms fully to existing serialization and validation constraints without schema version changes.
- Reaffirmed architectural rules: native C++ creates and owns persistent IDs (`PersonId`), while source UUIDs serve as authoring provenance only.

## [2026-08-21 10:51:00] - Fictionalized Personnel Seed Dataset Analysis & Planning

### Completed
- Conducted read-only analysis and schema mapping of fictionalized authoring dataset `doda_personnel_seed_v1.csv`.
- Profiled 5,808 rows and 36 columns (headerless); validated column 36 (`source_uuid`) uniqueness (100% unique) as authoring provenance key.
- Defined minimal safe native V1 projection (`displayName`, coarse role/occupation, `status=0`, `skill`, `workload=0`) and deferred 29 non-essential mock/PII/biometric fields.
- Selected 5 lore-aligned fixture candidate records by source UUID (`b97f04e7...`, `6da1acf7...`, `3bd31425...`, `972b3886...`, `1e34a9e2...`).
- Established core design rules: CSV data is authoring input only; no runtime CSV parser in ZScript or native engine; native C++ owns canonical IDs; criminal status is derived from native case state/evidence rules.

## [2026-08-21 10:47:00] - FOIMS-X Visual Language Reference Analysis

### Completed
- Analyzed 8 visual language reference archetypes (Vigilant 2000, TuiCss database forms, Borland Turbo Vision, MS-DOS Executive, id Software De-ICE installer, Norton/McFile manager, DESQview/X, Windows 3.1 Program Manager).
- Correlated visual grammar with canonical `doda-architecture.md` specification (DOS data density, 16-color functional palette, dotted field formatting, dual-pane layout, keyboard command bar language).
- Reaffirmed architectural non-negotiables: `personIdText` as persistent identity key, strict read-only presentation, and explicit handling of unavailable/empty/stale/unassigned states.

## [2026-08-21 10:42:00] - Personnel Snapshot V1 Shape Proof & Cleanup

### Completed
- Executed standalone `doda-core` read-only runtime proof calling 12 native `DoDA.GetPersonnelSnapshot*` methods.
- Verified live native C++ binding execution in UZDoom engine log returning collection metadata (`ApiVersion=1`, `Rev=1`, `StratMin=0`, `Count=0`) and empty row state without error.
- Cleaned up temporary test handler `DoDA/Test/TempPersonnelSnapshotShapeProof.zs` and directory `DoDA/Test/`.
- Restored `zscript.txt` by removing temporary `#region Test` block, preserving `#region NativeBridge` verbatim.
- Restored `MAPINFO` by removing `DoDAPersonnelSnapshotShapeProofHandler` from `gameinfo.AddEventHandlers`, restoring original 4 handlers.
- Retained `DoDA/Native/DoDA.zs` and `zscript.txt.native_bridge_pretest.bak` untouched.
- Preserved durable proof log artifact and cleanup report in `wiki/junie/`.

### Verified Artifacts
- Proof Log: `wiki/junie/logs/2026-08-21_10-42-00_personnel-shape-proof_log-doda-personnel-shape-2026-08-21-10-39-00.txt`
  - SHA-256: `9E2EC01FB1E1FB31FCAA564702663B130A610464EF54359CB1590348F0B2C11F`
- Proof Report: `wiki/junie/reports/2026-08-21_10-42-00_personnel-shape-proof.md`

### Cleanup Verification
- `DoDA/Test/TempPersonnelSnapshotShapeProof.zs`: Absent (`True`)
- `DoDA/Test/`: Absent (`True`)
- `DoDA/Native/DoDA.zs`: Present (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Present (`True`)
- `zscript.txt`: `#region NativeBridge` retained intact (`True`)
- `MAPINFO`: Restored to 4 production handlers (`DoDAMissionDirector`, `DoDAAimInput`, `Map03RangeStartHandler`, `MP5ModeHandler`)

## [2026-08-21 10:22:00] - Scalar Native-Call Proof & Cleanup

### Completed
- Executed standalone `doda-core` read-only runtime proof calling `DoDA.GetPersonnelSnapshotApiVersion()`.
- Verified live native C++ binding execution in UZDoom engine log returning integer `1`.
- Cleaned up temporary test handler `DoDA/Test/TempDoDANativeCallProof.zs` and directory `DoDA/Test/`.
- Restored `zscript.txt` by removing temporary `#region Test` block, preserving `#region NativeBridge` verbatim.
- Restored `MAPINFO` by removing `DoDANativeCallProofHandler` from `gameinfo.AddEventHandlers`, restoring original 4 handlers.
- Retained `DoDA/Native/DoDA.zs` and `zscript.txt.native_bridge_pretest.bak` untouched.
- Preserved durable proof log artifact and cleanup report in `wiki/junie/`.

### Verified Artifacts
- Proof Log: `wiki/junie/logs/2026-08-21_10-07-00_scalar-native-proof_log-doda-native-readonly.txt`
  - SHA-256: `1BB1A29851FF024E1798563CC0026CE724C4300267093032F3AD5638286F7991`
- Cleanup Report: `wiki/junie/reports/2026-08-21_10-22-00_scalar-proof-cleanup.md`

### Cleanup Verification
- `DoDA/Test/TempDoDANativeCallProof.zs`: Absent (`True`)
- `DoDA/Test/`: Absent (`True`)
- `DoDA/Native/DoDA.zs`: Present (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Present (`True`)
- `zscript.txt`: `#region NativeBridge` retained intact
- `MAPINFO`: Restored to 4 production handlers (`DoDAMissionDirector`, `DoDAAimInput`, `Map03RangeStartHandler`, `MP5ModeHandler`)

## [2026-08-17 00:00:00] - Historical Core Systems Documentation Baseline

### Completed
- Initial documentation of the DoDA weapon and aim system.
- Documented files: `WeaponBase.zs`, `PistolBase.zs`, `B92Left.zs`, `B92Right.zs`, `MP5KSD.zs`, `MP5ModeHandler.zs`, `AimInput.zs`, `HUDDeadzone.zs`, `HUDDeadzoneBridge.zs`.
- Documented character classes (`FieldAgent`, `Analyst`, `SAC`) and ability systems (`LeanInput`, `LeanController`).
- Documented weapon auxiliary systems (`HandSwapController`, `SpriteAnimator`, `AmmoDispenser`) and the Mission System (`MissionManager` and components).
- Pages created: `WeaponArchitecture.md`, `B92Pistols.md`, `MP5KSD.md`, `InputDeadzone.md`, `TestDebugging.md`.
