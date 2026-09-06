# Native Populated-Personnel Default Fixture Proof Report

- **Date / Timestamp:** `2026-08-21 11:25:00`
- **Milestone Group:** Native deterministic populated-personnel default fixture
- **Credit Budget:** 5
- **Credits Used:** 3
- **Credits Remaining:** 2

---

### Executive Summary
The native deterministic populated-personnel default fixture was implemented in `DoDASimulation::ClearForNewCampaign()` (`src/doda/DoDA_Simulation.cpp`), compiled under Debug configuration, and verified via a standalone read-only ZScript proof handler in `doda-core`. Live UZDoom engine log evidence confirmed that active ZScript queried the native strategic simulation on new campaign startup, observing collection metadata `ApiVersion=1`, `Rev=1`, `StratMin=0`, `Count=5`, pre/post revision equality (`RevisionMatch=1`), and all 5 populated person records matching approved fixture definitions without errors. All temporary test files and configuration entries were cleanly restored, while the permanent C++ campaign fixture remains active in the engine.

---

### Runtime Proof Artifact Evidence
- **Original Engine Log:** `C:\Dev\uzdoom_src\uzdoom-official\cmake-build-debug\log-doda-default-fixture-2026-08-21-11-20-00.txt`
  - Log Started: `2026-08-21 11:25:21`
  - Byte Size: `8944 bytes`
  - SHA-256: `B607586A38C67E9526639FD47A805288470378A65E0B9C09F0B09331FBD3541C`
- **Durable Copied Log:** `C:\Dev\uzdoom_src\doda-core\wiki\junie\logs\2026-08-21_11-20-00_default-fixture-proof_log-doda-default-fixture-2026-08-21-11-20-00.txt`
  - Byte Size: `8944 bytes`
  - SHA-256: `B607586A38C67E9526639FD47A805288470378A65E0B9C09F0B09331FBD3541C`
  - Hashes Match: `True`

---

### Observed Proof Markers
- **Pre-Loop Metadata Line (Line 88):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] MetaBefore: ApiVersion=1 Rev=1 StratMin=0 Count=5`
- **Populated Person Row 0 (Line 89):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] Row 0: PersonId=1 Name=Ruth M. Green Status=0 Skill=5 Workload=0 AssignId= TaskId= TaskTitle=`
- **Populated Person Row 1 (Line 90):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] Row 1: PersonId=2 Name=Michelle C. Thomas Status=0 Skill=7 Workload=0 AssignId= TaskId= TaskTitle=`
- **Populated Person Row 2 (Line 91):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] Row 2: PersonId=3 Name=Brian C. Gordon Status=0 Skill=8 Workload=0 AssignId= TaskId= TaskTitle=`
- **Populated Person Row 3 (Line 92):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] Row 3: PersonId=4 Name=Leonard M. Martin Status=0 Skill=6 Workload=0 AssignId= TaskId= TaskTitle=`
- **Populated Person Row 4 (Line 93):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] Row 4: PersonId=5 Name=Harold M. Beltz Status=0 Skill=5 Workload=0 AssignId= TaskId= TaskTitle=`
- **Post-Loop Metadata Line (Line 94):**
  `[DODA-DEFAULT-FIXTURE-V1-RUN-20260821-112000] MetaAfter: Rev=1 RevisionMatch=1`
- **Observed Marker Count:** 7 lines (1 MetaBefore, 5 Row records, 1 MetaAfter)
- **Targeted Error Scan:** Clean (0 matches for `Script error`, `Unknown identifier`, `Native function`, `Unknown class`, `Could not start log`, `assertion`, `fatal`, `VM`)

---

### Permanent Native Changes Retained
- `C:\Dev\uzdoom_src\uzdoom-official\src\doda\DoDA_Simulation.cpp`: Added 5 deterministic default person records into `mPeople` within `DoDASimulation::ClearForNewCampaign()`.

---

### Cleanup Performed
1. **Deleted:** `C:\Dev\uzdoom_src\doda-core\DoDA\Test\TempDefaultFixtureProof.zs`
2. **Removed Directory:** `C:\Dev\uzdoom_src\doda-core\DoDA\Test\`
3. **Restored `zscript.txt`:** Removed temporary `#region Test` block, preserving `#region NativeBridge` verbatim.
4. **Restored `MAPINFO`:** Removed `DoDADefaultFixtureProofHandler` from `gameinfo.AddEventHandlers`, restoring original 4 handlers: `"DoDAMissionDirector", "DoDAAimInput", "Map03RangeStartHandler", "MP5ModeHandler"`.

---

### Source Integrity Post-Cleanup
- `DoDA/Test/TempDefaultFixtureProof.zs`: Absent (`True`)
- `DoDA/Test/`: Absent (`True`)
- `DoDA/Native/DoDA.zs`: Present and unchanged (`True`)
- `zscript.txt.native_bridge_pretest.bak`: Present and unchanged (`True`)
- `zscript.txt`: `#region NativeBridge` retained intact (`True`)
- `MAPINFO`: Exactly the four original production handlers (`True`)
- `src/doda/DoDA_Simulation.cpp`: Permanent default fixture retained
