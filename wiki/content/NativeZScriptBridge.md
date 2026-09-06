# Native-to-ZScript Bridge Reference

### Confirmed Architecture
The DoDA bridge provides a narrow, strictly isolated boundary between the native C++ strategic simulation and the UZDoom ZScript runtime. All strategic state (people, cases, assignments, department resources, strategic clock, validation rules, save/load serialization) is owned exclusively by native C++ in the UZDoom fork (`uzdoom-official`). ZScript interfaces with strategic state solely through read-only native action functions declared on `struct DoDA native`.

## Engine Implementation Seams
- **Native Declaration**: `DoDA/Native/DoDA.zs` in `doda-core` declares `struct DoDA native` and is included in the root translation unit via `#region NativeBridge` in `zscript.txt`.
- **Action Function Registration**: `src/doda/DoDA_ZBind.cpp` registers native C++ methods with the UZDoom VM using the `DEFINE_ACTION_FUNCTION` macro.
- **Simulation State Authority**: `DoDASimulation` (`src/doda/DoDA_Simulation.h`, `src/doda/DoDA_Simulation.cpp`) manages canonical simulation state.
- **Persistence Boundary**: `DoDASimulation::Serialize(FSerializer& arc)` participates in engine save/load flows through `G_DoLoadGame` and `G_SaveGame` in `src/g_game.cpp` using Save Schema Version 2 (`DODA_SAVE_SCHEMA_VERSION = 2`).
- **Campaign Default Initialization**: `DoDASimulation::ClearForNewCampaign()` deterministically initializes 5 default person records on new campaign boot without runtime file I/O or external dependencies.

## Committed Personnel Snapshot V1 Native Methods (API Version 1)
Personnel Snapshot V1 exposes exactly 12 read-only query methods on `struct DoDA native`:
1. `native static int GetPersonnelSnapshotApiVersion();`
2. `native static String GetPersonnelSnapshotRevisionText();`
3. `native static String GetPersonnelSnapshotStrategicMinutesText();`
4. `native static int GetPersonnelSnapshotCount();`
5. `native static String GetPersonnelPersonIdText(int index);`
6. `native static String GetPersonnelDisplayName(int index);`
7. `native static int GetPersonnelStatus(int index);`
8. `native static int GetPersonnelSkill(int index);`
9. `native static int GetPersonnelWorkload(int index);`
10. `native static String GetPersonnelCurrentAssignmentIdText(int index);`
11. `native static String GetPersonnelCurrentTaskIdText(int index);`
12. `native static String GetPersonnelCurrentTaskTitle(int index);`

## Return Value & State Conventions
- **Invalid Index Behavior**: For any out-of-range or negative index:
  - String getters (`GetPersonnelPersonIdText`, `GetPersonnelDisplayName`, `GetPersonnelCurrentAssignmentIdText`, `GetPersonnelCurrentTaskIdText`, `GetPersonnelCurrentTaskTitle`) return empty string (`""`).
  - Numeric metrics (`GetPersonnelSkill`, `GetPersonnelWorkload`) return `0`.
  - Status (`GetPersonnelStatus`) returns `2` (`Unavailable`).
- **Unassigned Representation**: When a person has no active assignment, `GetPersonnelCurrentAssignmentIdText`, `GetPersonnelCurrentTaskIdText`, and `GetPersonnelCurrentTaskTitle` return empty strings (`""`).
- **Snapshot Availability**: Non-empty `RevisionText` indicates active simulation availability; empty string indicates unavailable native state.
- **Revision Stability**: Comparing `RevisionText` before and after row iteration guarantees that the snapshot was not modified mid-read by concurrent simulation ticks.

## Bridge Boundary Rules
1. **Read-Only Invariance**: Snapshot functions must never alter native simulation state.
2. **Opaque Tokens**: All persistent IDs (`PersonIdText`, `AssignmentIdText`, `TaskIdText`), revision counters (`RevisionText`), and timestamps (`StrategicMinutesText`) cross the boundary as opaque decimal-string tokens. ZScript never performs numeric casting or arithmetic on IDs.
3. **No Pointer or Container Leakage**: Raw C++ pointers, engine references, LibColony structures, and internal standard containers (`std::vector`, `std::string`) are strictly forbidden from crossing the ZScript boundary.
4. **Authorized Adapter Access**: In ZScript presentation architecture, only dedicated adapter classes (e.g., `PersonnelSnapshotV1Adapter.zs`) are permitted to query `DoDA` native methods. Models and ViewStates must remain pure data/presentation objects with zero native calls.
5. **Zero Allocation in Engine Core**: Query bindings perform fast indexing and conversion directly against existing simulation structures.

### Planned
- Future snapshot contracts for Case, Assignment, and Strategic Time subsystems.
- Validated event submission actions for discrete tactical-to-macro state reporting.

### Resolved Decisions
- **Native Declaration Placement**: Resolved. `struct DoDA native` is placed in `DoDA/Native/DoDA.zs` and integrated into `doda-core/zscript.txt` under `#region NativeBridge`.
- **Diagnostics API Sufficiency**: Resolved. Audit and live engine proof verified that existing 12 methods fully satisfy all diagnostic, bounding, revision stability, and error classification requirements without requiring additional native endpoints.
