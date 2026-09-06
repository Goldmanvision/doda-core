# Personnel Snapshot V1 Specification & Verification Record

### Confirmed Baseline
- **Engine Repository**: `C:\Dev\uzdoom_src\uzdoom-official`
- **Engine Branch**: `doda/strategic-core-v0`
- **Engine Commit**: `4d7ef89286`
- **Native Declaration**: `DoDA/Native/DoDA.zs` in `doda-core` (included via `#region NativeBridge` in `zscript.txt`)
- **Native API Version**: `1`
- **Save Schema Version**: `2`

### Confirmed Architecture & Boundary Rules
- **Canonical State Ownership**: All strategic state (people, cases, assignments, department resources, time, save serialization) is owned exclusively by native C++ in the UZDoom fork (`DoDASimulation`).
- **Read-Only Query Contract**: Personnel Snapshot V1 exposes 12 read-only query actions to ZScript on `struct DoDA native`. ZScript cannot mutate native strategic simulation state via snapshot queries.
- **Data Exchange Format**: Record IDs, revision numbers, and strategic minute timestamps cross the native-to-ZScript boundary as opaque decimal-string tokens. Snapshot V1 does not expose roles or locations.
- **ZScript Presentation Tier**: Three isolated, inert ZScript files reside in `DoDA/UI/FOIMSX/PersonnelV1/` (un-included in `zscript.txt`, unregistered in `MAPINFO`):
  1. `PersonnelSnapshotV1Model.zs`: Pure data model representing snapshot metadata and record fields.
  2. `PersonnelSnapshotV1Adapter.zs`: Authorized isolation layer querying `DoDA.GetPersonnelSnapshot*` native methods with complete validation and pre/post revision checks.
  3. `PersonnelSnapshotV1ViewState.zs`: Pure presentation view-state model keyed by persistent `PersonIdText` with 8 discrete presentation states (`UNAVAILABLE`, `INVALID_VERSION`, `EMPTY`, `STALE`, `OUT_OF_RANGE`, `SELECTED_PERSON_DISAPPEARED`, `UNASSIGNED`, `POPULATED`).

### Confirmed Default Campaign Fixture
The native C++ simulation (`DoDASimulation::ClearForNewCampaign()` in `src/doda/DoDA_Simulation.cpp`) seeds exactly 5 deterministic personnel records on campaign start:
1. **PersonId 1**: `Ruth M. Green` | Status: `0` (Available) | Skill: `5` | Workload: `0%` | Assignment: Unassigned
2. **PersonId 2**: `Michelle C. Thomas` | Status: `0` (Available) | Skill: `7` | Workload: `0%` | Assignment: Unassigned
3. **PersonId 3**: `Brian C. Gordon` | Status: `0` (Available) | Skill: `8` | Workload: `0%` | Assignment: Unassigned
4. **PersonId 4**: `Leonard M. Martin` | Status: `0` (Available) | Skill: `6` | Workload: `0%` | Assignment: Unassigned
5. **PersonId 5**: `Harold M. Beltz` | Status: `0` (Available) | Skill: `5` | Workload: `0%` | Assignment: Unassigned

### Confirmed Diagnostics & Verification Contract
The native query contract provides complete diagnostics without requiring additional native endpoints:
- API compatibility check via `GetPersonnelSnapshotApiVersion()`.
- Simulation availability check via non-empty `GetPersonnelSnapshotRevisionText()`.
- Revision stability verification via pre- and post-acquisition revision comparison.
- Strategic clock tracking via `GetPersonnelSnapshotStrategicMinutesText()`.
- Bounded row iteration via `GetPersonnelSnapshotCount()`.
- Safe out-of-bounds handling (empty strings, status `2 Unavailable`, metric `0`).

### Verified Runtime Proof Evidence
- **Scalar Native-Call Proof**: Verified `ApiVersion = 1` (`wiki/junie/reports/2026-08-21_10-22-00_scalar-proof-cleanup.md`).
- **Snapshot Shape Proof**: Verified collection metadata and empty row safety (`wiki/junie/reports/2026-08-21_10-42-00_personnel-shape-proof.md`).
- **Populated Campaign Fixture Proof**: Verified live 5-person default fixture in engine log (`wiki/junie/reports/2026-08-21_11-25-00_default-fixture-proof.md`).
- **Diagnostics Contract Proof**: Verified full diagnostic contract and adapter requirements (`wiki/junie/reports/2026-08-21_12-25-00_personnel-diagnostics-proof.md`).

### Planned
- Future expansion to Case, Assignment, and Strategic Time snapshot query bindings.
- Field-to-macro state event reporting functions for discrete verified mutations.
- Visual FOIMS-X UI presentation rendering integration when authorized.

### Resolved Decisions
- **Native Declaration Placement**: Resolved. Committed to `DoDA/Native/DoDA.zs` and included in `zscript.txt`.
- **Campaign Default Population**: Resolved. Implemented as compiled native C++ initialization in `DoDASimulation`.
- **Diagnostics Surface**: Resolved. Retained the existing 12 native query methods without unnecessary additions.
