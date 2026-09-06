# FOIMS-X Input Architecture & Simulation Variable Template Handoff

## 1. Current Boundary and Status

### Architectural Boundary Summary
The Department of Dead Affairs (DoDA) architecture enforces a strict, decoupled boundary between the native engine simulation layer and the ZScript gameplay/presentation layers:

- **Native C++ Simulation Core:**
  - Owns canonical, persistent strategic domain entities (People, Cases, Tasks, Assignments, Resources, Strategic Time, Simulation Variables).
  - Owns authoritative validation, state machines, business invariant enforcement, mutation transitions, and native persistence (save/load serialization).
  - Native data structures represent the single source of truth for strategic and organizational state.
- **ZScript / GZDoom Presentation & Field Layer:**
  - Owns in-level presentation, UI widgets, field viewport rendering, tactical gameplay interactions, temporary playsim actors, and local weapon/movement mechanics.
  - Owns future validated discrete-event reporting (tactical outcomes, field reports) submitted back to native core via explicit contracts.
  - Owns zero persistent strategic state and zero unvalidated native mutation authority.
- **FOIMS-X (Field Operations Information Management System - Extended):**
  - Serves as the strategic management interface accessible during tactical gameplay.
  - Does **NOT** own strategic mutation, persistence, scheduler tick rules, economy models, payroll accounting, or world progression mechanics.
  - Operates strictly as a read-only presentation client or structured command submission gateway.
- **Existing Host Session-Control Baseline (`DoDAFOIMSXHostLifecycleProbe`):**
  - Owns MAP01-only eligibility gating (`Level.MapName == "MAP01"`).
  - Owns active session toggling via `Key 'O'` and `Key 'Escape'`.
  - Owns single-console-player freeze application (`CF_TOTALLYFROZEN`), velocity zeroing (`(0, 0, 0)`), and ownership flag tracking (`mFOIMSXAppliedFreeze`).
  - Owns active-session input consumption in `InputProcess` (locking field movement and weapon firing while active).
  - Owns safe freeze release and UI active-state invalidation across `WorldLoaded` and `WorldUnloaded` transitions (`mObservedWorldLoadGeneration` synchronization).
  - Owns the public read-only UI query seam `IsFOIMSXActive()` used by `DoDAHUD.ProcessNotify` for top-left notification string suppression.

---

### Status Separation Matrix

| Category | Item / Component | Status / Boundary Description |
| :--- | :--- | :--- |
| **Source-Confirmed Facts** | Native Personnel Snapshot API V1 | Native C++ exports `DoDA.GetPersonnelSnapshotRevision()`, `DoDA.GetPersonnelSnapshotCount()`, `DoDA.GetPersonnelSnapshotPersonId()`, `DoDA.GetPersonnelSnapshotDisplayName()`, `DoDA.GetPersonnelSnapshotStatus()`, and `DoDA.GetPersonnelSnapshotAssignment()`. Validated with version check (`1`). |
| **Source-Confirmed Facts** | `DoDAPersonnelSnapshotV1Adapter` | Implements bounded, revision-safe snapshot acquisition from native C++ with duplicate ID checking, status bounds validation, and assignment triple validation. |
| **Source-Confirmed Facts** | `DoDAPersonnelSnapshotV1ViewState` | Implements view-state projection (`EDoDAPersonnelViewState`), stale-state retention (`LastAcceptedSnapshot`), selection tracking keyed exclusively by `PersonIdText`, and disappearance semantics. |
| **Source-Confirmed Facts** | Host Boundary Separation (V3) | `DoDAFOIMSXHostLifecycleProbe.zs` contains only lifecycle, MAP01 gating, single-player freeze, velocity reset, generation observation, input consumption, and `IsFOIMSXActive()`. Contains zero drawing or snapshot acquisition code. |
| **Source-Confirmed Facts** | HUD Notification Suppression | `DoDAHUD.ProcessNotify` queries `DoDAFOIMSXHostLifecycleProbe.IsFOIMSXActive()` and suppresses top-left screen notifications while FOIMS-X is active. |
| **Proposed Contracts** | Semantic Intent Router | Decoupled UI input mapping layer converting raw scan codes / key events into high-level navigation intents (`NavigateUp`, `Confirm`, `NextTab`, etc.). |
| **Proposed Contracts** | Dedicated Renderer Integration | Standalone UI renderer (`DoDAFOIMSXDirectoryRenderer`) consuming `DoDAPersonnelSnapshotV1ViewState` to draw the 640×480 virtual frame, directory table, selection details, and status panels. |
| **Proposed Contracts** | Discrete Field Event Submissions | Future narrow, validated command/event submissions from field play to native simulation (e.g. mission completion reports, casualty notifications). |
| **Open Decisions** | Tactical vs. Strategic Time | Rate of strategic clock progression during active field play versus discrete end-of-mission batch processing. |
| **Open Decisions** | Simulation Variables Domain | Scale, entity scope, and update triggers for psychological, physical, and financial variables. |
| **Deferred Work** | Multi-Tab FOIMS-X Navigation | Cases, Operations, and System tab implementations are deferred. |
| **Deferred Work** | Interactive Directory Selection UI | Keyboard/mouse cursor selection, list scrolling, and inspector panel population are deferred. |
| **Deferred Work** | Economy & Strategic Progression | Budgeting, payroll runs, equipment procurement, and facility maintenance logic are deferred. |

---

## 2. Future FOIMS-X Input Architecture

### Conceptual Data & Control Flow
The input architecture adheres to a one-way unidirectional pipeline:

```text
Input Source (Keyboard / Mouse / Gamepad)
       │
       ▼
Host Eligibility & Session Gate (DoDAFOIMSXHostLifecycleProbe)
       │
       ▼
FOIMS-X Semantic Intent Router
       │
       ▼
Active Panel / List Controller
       │
       ▼
Read-Only ViewState Query  ──OR──►  Validated Future Command Submission
       │                                            │
       ▼                                            ▼
FOIMS-X Renderer (UI Display)             Native C++ Simulation Core
```

---

### Architectural Rules
1. **Host Isolation:**
   - The Host owns only session opening and closure, map eligibility, freeze/unfreeze lifecycle ownership, raw input consumption while active, and active-state queries.
   - The Host does not interpret navigation keys, manipulate view state, or query domain models.
2. **Intent Translation Without Mutation:**
   - The future Semantic Intent Router translates raw input events (key down, key repeat) into abstract semantic intents.
   - The Intent Router never mutates native state directly.
3. **UI Focus and Navigation Ownership:**
   - The Panel/List Controller owns visual focus, active list index, pagination offsets, and active tab indices.
   - Persistent entities are tracked and selected exclusively by canonical, stable string IDs (`PersonIdText`), **never** by transient row index, actor pointer, map TID, or spawn order.
4. **Separation of Queries and Commands:**
   - Presentation updates query `ViewState` read-only.
   - User actions that modify strategic state (e.g. reassigning personnel) must formulate a discrete, strongly-typed command for submission to the native core via a validated interface.
5. **No Per-Frame Polling:**
   - Input processing is purely event-driven (`InputProcess`). Continuous per-frame polling of keystrokes or asynchronous input scanning in `Tick()` / `RenderOverlay()` is strictly prohibited.

---

### Approved Semantic Intent Identifiers
The following intent symbols constitute the approved semantic vocabulary:

- `ToggleFOIMSX`: Request to open or close the FOIMS-X interface (bound to `Key 'O'`).
- `CloseFOIMSX`: Explicit request to close the interface (bound to `Key 'Escape'`).
- `NavigateUp`: Move selection cursor or active highlight upward in the current list/panel.
- `NavigateDown`: Move selection cursor or active highlight downward in the current list/panel.
- `NavigateLeft`: Move focus to adjacent left panel or adjust numeric slider leftward.
- `NavigateRight`: Move focus to adjacent right panel or adjust numeric slider rightward.
- `Confirm`: Activate currently focused item, inspect record, or confirm pending prompt.
- `Back`: Cancel current modal dialog, return focus to parent container, or step back one hierarchy level.
- `NextTab`: Switch active interface view to the next top-level tab (e.g. Directory $\to$ Cases $\to$ Operations $\to$ System).
- `PreviousTab`: Switch active interface view to the preceding top-level tab.
- `ScrollPageUp`: Advance list selection or view window upward by one full page view.
- `ScrollPageDown`: Advance list selection or view window downward by one full page view.

---

### Input Policy & Scoping Guardrails
- **Activation Keys:** `Key 'O'` and `Key 'Escape'` remain strictly owned by the existing Host lifecycle implementation.
- **Navigation Candidates:** Standard Arrow Keys (`Up`, `Down`, `Left`, `Right`), Numpad navigation keys, and PageUp/PageDown are designated candidates for the future Intent Router.
- **Function Keys Prohibited:** Function keys (`F1` through `F12`) must **not** be bound or intercepted, preserving engine developer shortcuts, console toggles, quicksave/quickload, and screenshot operations.
- **No Engine-Level Bindings:** No custom bindings, `KEYCONF`, `MENUDEFS`, `CVARINFO`, or global console commands shall be created or modified for internal FOIMS-X navigation.
- **TAPLINE Out of Scope:** The tactical field HUD tapline (`DoDAHUDTapline` / `TAB` key) is a separate subsystem and is entirely out of scope for FOIMS-X.

---

### Conceptual Focus Precedence Hierarchy
Input events are evaluated strictly according to the following priority cascade:

1. **Engine Console / System Menus (Highest Priority):**
   - When the developer console (`~`) or engine escape menu is open, the engine handles all input. FOIMS-X receives no input events.
2. **Non-MAP01 Gameplay (TITLEMAP, MAP02, etc.):**
   - FOIMS-X Host eligibility guard evaluates to `false`. All input passes transparently to standard engine gameplay and menus.
3. **MAP01 Tactical Field Gameplay (FOIMS-X Inactive):**
   - Host evaluates `mActive == false`.
   - Host checks for `Key 'O'`. If pressed, consumes event and triggers activation network freeze.
   - All other input passes directly to field player movement, aiming, and combat controls.
4. **MAP01 Active FOIMS-X Session (Lowest Tier Interception):**
   - Host evaluates `mActive == true`.
   - Host intercepts `Key 'O'` or `Key 'Escape'` to trigger closure and unfreeze.
   - Host routes remaining navigation keys (`Arrows`, `Enter`, `Tab`, `PgUp`, `PgDn`) to the FOIMS-X Semantic Intent Router.
   - Host consumes all remaining gameplay keys (`WASD`, fire, reload, use) to guarantee total player stillness and prevent accidental weapon discharges.

---

## 3. Simulation-Variable Template Catalogue

### Catalog Policy & Authority Baseline
- **Template Status:** All variables documented below are **template specifications only**. Zero implementation, zero native C++ API expansion, and zero FOIMS-X presentation bindings are approved in this batch.
- **Psychological / Physiological Variables (Hunger, Fatigue, Stress):** Native person state only. The field gameplay layer may never directly mutate these values; it may only report future validated discrete events (e.g. mission elapsed time, severe trauma incident).
- **Mission & Objective Progress:** A strict architectural separation exists between temporary tactical field session progress (monitored by `DoDAMissionDirector` in GZDoom) and canonical native mission/case outcomes committed to the strategic ledger upon mission resolution.
- **Task Progress:** Native task/case authority; updated via future validated field-event receipts.
- **Corruption:** Strategic world-pressure placeholder only. System rules, factions, crime metrics, or paranormal mechanics are not defined and must not be invented.
- **Salary & Operating Costs:** Financial ledger placeholders only. Payroll formulas, disbursement cadences, expense categorization, and budgets are not defined and must not be invented.

---

### Variable 1: Hunger
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `person.vitals.hunger` |
| **Display Label** | `HUNGER` |
| **Canonical Owner** | Native C++ Personnel Simulation Core (`DoDA::PersonEntity`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Simulation State) |
| **Entity Scope** | Individual Person (`PersonIdText`) |
| **Recommended Type / Unit** | `uint8_t` / Normalized Scalar ($0 = \text{Satiated}, 100 = \text{Starving}$) |
| **Recommended Valid Range / Domain** | Integer `[0, 100]` |
| **Update Trigger Category** | Strategic Time Tick / Macro Simulation Step (e.g. hourly metabolic decay) |
| **Future Native Snapshot Exposure** | Projected field in future `DoDAPersonnelV2` snapshot payload (read-only) |
| **Future FOIMS-X Presentation State** | Personnel Dossier / Medical & Vitals Tab (Read-Only Status Bar / Alert) |
| **Future Field-Event Inputs** | Tactical Ration Consumption Event (`Event_ConsumeRation`) |
| **Explicit Non-Owner Systems** | ZScript UI, `DoDAHUD`, `DoDAFOIMSXHostLifecycleProbe`, `DoDAMissionDirector` |
| **Open Design Decisions** | Threshold values for performance penalties; interaction with strategic rations inventory. |

---

### Variable 2: Fatigue
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `person.vitals.fatigue` |
| **Display Label** | `FATIGUE` |
| **Canonical Owner** | Native C++ Personnel Simulation Core (`DoDA::PersonEntity`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Simulation State) |
| **Entity Scope** | Individual Person (`PersonIdText`) |
| **Recommended Type / Unit** | `uint8_t` / Normalized Scalar ($0 = \text{Rested}, 100 = \text{Exhausted}$) |
| **Recommended Valid Range / Domain** | Integer `[0, 100]` |
| **Update Trigger Category** | Active Duty Time, Tactical Deployment Duration, Sleep/Rest Recovery Tick |
| **Future Native Snapshot Exposure** | Projected field in future `DoDAPersonnelV2` snapshot payload (read-only) |
| **Future FOIMS-X Presentation State** | Personnel Directory Row Status Indicator & Personnel Detail Panel |
| **Future Field-Event Inputs** | Extended Tactical Field Deployment Exertion Event (`Event_FieldExertion`) |
| **Explicit Non-Owner Systems** | ZScript UI, Field Agent Movement Controller, `DoDAFOIMSXHostLifecycleProbe` |
| **Open Design Decisions** | Recovery curve formula during off-duty hours; fatigue-induced operational failure rates. |

---

### Variable 3: Stress
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `person.psych.stress` |
| **Display Label** | `STRESS` |
| **Canonical Owner** | Native C++ Personnel Simulation Core (`DoDA::PersonEntity`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Simulation State) |
| **Entity Scope** | Individual Person (`PersonIdText`) |
| **Recommended Type / Unit** | `uint8_t` / Normalized Scalar ($0 = \text{Composed}, 100 = \text{Breaking Point}$) |
| **Recommended Valid Range / Domain** | Integer `[0, 100]` |
| **Update Trigger Category** | Combat Exposure, Casualty Proximity, High-Stakes Investigation Outcome |
| **Future Native Snapshot Exposure** | Projected field in future `DoDAPersonnelV2` snapshot payload (read-only) |
| **Future FOIMS-X Presentation State** | Personnel Dossier / Psychological Evaluation Panel |
| **Future Field-Event Inputs** | Critical Combat Trauma Event (`Event_TraumaEncountered`), Casualty Witness Event |
| **Explicit Non-Owner Systems** | ZScript Playsim, Weapon Systems, FOIMS-X Host |
| **Open Design Decisions** | Psychiatric leave recovery rate; breakdown thresholds triggering erratic field behavior. |

---

### Variable 4: Mission Progress
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `operation.mission.progress` |
| **Display Label** | `MISSION PROGRESS` |
| **Canonical Owner** | Native C++ Case & Operations Manager (`DoDA::CaseManager`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Campaign State) |
| **Entity Scope** | Active Strategic Case / Operation (`CaseIdText`) |
| **Recommended Type / Unit** | `uint8_t` / Percentage Completion ($0\% \dots 100\%$) |
| **Recommended Valid Range / Domain** | Integer `[0, 100]` |
| **Update Trigger Category** | Validated Tactical Mission Debriefing / Milestone Event Commit |
| **Future Native Snapshot Exposure** | Projected field in future `DoDAOperationsSnapshotV1` |
| **Future FOIMS-X Presentation State** | Operations Overview & Active Case File Summary Table |
| **Future Field-Event Inputs** | Field Mission Completion Receipt (`Event_MissionDebriefCommit`) |
| **Explicit Non-Owner Systems** | `DoDAMissionDirector` (owns only temporary local map progression, not strategic record) |
| **Open Design Decisions** | Reversibility upon tactical failure; partial score calculation across branch milestones. |

---

### Variable 5: Objective Progress
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `operation.objective.progress` |
| **Display Label** | `OBJECTIVE STATUS` |
| **Canonical Owner** | Native C++ Case & Operations Manager (`DoDA::ObjectiveEntity`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Campaign State) |
| **Entity Scope** | Specific Objective within Case (`ObjectiveIdText`) |
| **Recommended Type / Unit** | `uint8_t` Enum / State (`0=Pending, 1=InProgress, 2=Accomplished, 3=Failed`) |
| **Recommended Valid Range / Domain** | Enumerated `[0, 3]` |
| **Update Trigger Category** | Objective Event Receipt Validation |
| **Future Native Snapshot Exposure** | Projected array in future `DoDAOperationsSnapshotV1` |
| **Future FOIMS-X Presentation State** | Active Case Details Sub-Panel / Objective Checklist |
| **Future Field-Event Inputs** | Tactical Objective Trigger (`Event_ObjectiveMilestoneReached`) |
| **Explicit Non-Owner Systems** | ZScript HUD, Level Scripts, FOIMS-X Host |
| **Open Design Decisions** | Optional vs. mandatory objective dependencies; branch outcome weightings. |

---

### Variable 6: Task Progress
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `task.assignment.progress` |
| **Display Label** | `TASK PROGRESS` |
| **Canonical Owner** | Native C++ Task Allocation Engine (`DoDA::TaskManager`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Simulation State) |
| **Entity Scope** | Strategic Task (`TaskIdText`) assigned to Agent (`PersonIdText`) |
| **Recommended Type / Unit** | `uint32_t` / Accumulated Effort Minutes or Completion Percentage |
| **Recommended Valid Range / Domain** | Integer `[0, TargetMinutes]` or Percentage `[0, 100]` |
| **Update Trigger Category** | Strategic Simulation Work-Hour Tick |
| **Future Native Snapshot Exposure** | Projected field in future `DoDATaskSnapshotV1` |
| **Future FOIMS-X Presentation State** | Task Allocation Board / Personnel Current Assignment View |
| **Future Field-Event Inputs** | Tactical Intel Discovery (`Event_IntelDiscovered`) adding effort credits |
| **Explicit Non-Owner Systems** | ZScript Presentation Classes, FOIMS-X Host |
| **Open Design Decisions** | Collaboration multiplier when multiple agents assigned; interruption penalty. |

---

### Variable 7: Corruption
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `world.pressure.corruption` |
| **Display Label** | `SYSTEM CORRUPTION` |
| **Canonical Owner** | Native C++ World State Engine (`DoDA::WorldPressureTracker`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Campaign State) |
| **Entity Scope** | Department / Regional Sector Jurisdiction |
| **Recommended Type / Unit** | `uint16_t` / Strategic Pressure Index |
| **Recommended Valid Range / Domain** | Integer `[0, 1000]` (Placeholder Domain) |
| **Update Trigger Category** | Unresolved Case Timeout, Compromised Asset Event, Black-Market Interaction |
| **Future Native Snapshot Exposure** | Projected field in future `DoDASystemSnapshotV1` |
| **Future FOIMS-X Presentation State** | System Diagnostics / Strategic Situation Monitor |
| **Future Field-Event Inputs** | Evidence Compromise Event (`Event_EvidenceTainted`) |
| **Explicit Non-Owner Systems** | Tactical Playsim, Field Weapons, FOIMS-X Host |
| **Open Design Decisions** | Scope (global vs. jurisdictional vs. institutional); consequence scaling and event thresholds. |

---

### Variable 8: Salary
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `financial.payroll.salary` |
| **Display Label** | `SALARY (MONTHLY)` |
| **Canonical Owner** | Native C++ Department Ledger (`DoDA::FinanceLedger`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Ledger State) |
| **Entity Scope** | Individual Agent Contract (`PersonIdText`) |
| **Recommended Type / Unit** | `uint32_t` / Department Standard Currency Units |
| **Recommended Valid Range / Domain** | Integer `[0, 1000000]` |
| **Update Trigger Category** | Contract Renegotiation, Rank Promotion, Periodic Payroll Accrual Run |
| **Future Native Snapshot Exposure** | Projected field in future `DoDAPersonnelV2` or Financial Snapshot |
| **Future FOIMS-X Presentation State** | Personnel Contract Summary & Department Financial Ledger |
| **Future Field-Event Inputs** | None (Field layer possesses zero payroll mutation authority) |
| **Explicit Non-Owner Systems** | ZScript UI, Playsim Actors, FOIMS-X Host |
| **Open Design Decisions** | Payment frequency (weekly/monthly/per-case); hazard pay modifiers; arrears handling. |

---

### Variable 9: Operating Costs
*Status: Template only — no implementation. No current native API expansion approved. No current FOIMS-X renderer exposure approved.*

| Specification Attribute | Contract Definition |
| :--- | :--- |
| **Stable Contract Key** | `financial.ledger.operating_costs` |
| **Display Label** | `OPERATING EXPENSES` |
| **Canonical Owner** | Native C++ Department Ledger (`DoDA::FinanceLedger`) |
| **Persistence Scope** | Native Savegame Archive (Strategic Ledger State) |
| **Entity Scope** | Department / Station Asset Base |
| **Recommended Type / Unit** | `uint32_t` / Currency Units per Strategic Cycle |
| **Recommended Valid Range / Domain** | Integer `[0, 10000000]` |
| **Update Trigger Category** | Facility Maintenance Tick, Asset Procurement, Operational Deployment Billing |
| **Future Native Snapshot Exposure** | Projected summary in future `DoDASystemSnapshotV1` |
| **Future FOIMS-X Presentation State** | System / Finance Overview Panel |
| **Future Field-Event Inputs** | Tactical Asset Loss Receipt (`Event_AssetDestroyed`) |
| **Explicit Non-Owner Systems** | ZScript Presentation, `DoDAHUD`, FOIMS-X Host |
| **Open Design Decisions** | Fixed overhead vs. variable deployment costs; budget insolvency failure state. |

---

## 4. Shared Contract Rules

To maintain long-term stability and prevent architectural erosion across engine boundaries, all future integration contracts must satisfy the following six foundational rules:

1. **Persistent Entities Require Stable Identifiers:**
   - Every persistent entity (Person, Case, Objective, Task, Asset) must possess a globally unique, immutable string identifier (e.g. `PersonIdText`, `CaseIdText`).
   - Transient pointers, array row indices, GZDoom Actor references, map TIDs, and spawn sequences must **never** be used to identify persistent entities across frames or save cycles.
2. **Opaque Tokens for IDs, Revisions, and Timestamps:**
   - Where a contract exposes identifiers, state revisions, or strategic timestamps to ZScript, they must be formatted as opaque, structured `String` tokens.
   - UI code must treat revision tokens as opaque keys and avoid performing custom arithmetic or bitwise manipulations on internal IDs.
3. **Native Core Validates Invariants Exclusively:**
   - The native C++ core is the sole arbiter of domain invariants. Native code must rigorously validate entity IDs, revision tokens, state transitions, numeric bounds, and caller permissions for every transaction.
   - ZScript UI validation acts only as an advisory guardrail to enhance responsiveness; it cannot replace authoritative native validation.
4. **Read-Only Queries Imply Zero Mutation Authority:**
   - Snapshot acquisition interfaces (e.g. `AcquireSnapshot()`) are strictly read-only and side-effect free.
   - Performing a query never reserves resources, advances simulation clocks, or mutates entity state.
5. **Strict Separation Between Queries and Event Submissions:**
   - Data flows down from Native to ZScript via immutable, validated Snapshot models.
   - Commands flow up from ZScript to Native via explicit, strongly-typed discrete event structures.
   - Snapshot acquisition and command submission must never be combined into a single ambiguous interface.
6. **Strict Versioning for APIs and Save Schemas:**
   - Every native API transaction contract must negotiate an explicit version token (e.g. `API Version 1`). If a version mismatch occurs, the adapter must fail safely with an explicit error state (`ACQUISITION_INVALID_VERSION`).
   - All native savegame schemas must include sequential schema versioning to guarantee backward compatibility and deterministic migration.

---

## 5. Handoff Roadmap

The future development progression is structured into seven distinct, sequential milestones:

```text
Milestone 1: Verify & Archive Host-Boundary Baseline
       │
       ▼
Milestone 2: Plan & Approve ViewState / Dedicated Renderer Separation
       │
       ▼
Milestone 3: Plan UI Semantic Intent Router (No Native Mutation)
       │
       ▼
Milestone 4: Define Single Read-Only Simulation Snapshot Contract
       │
       ▼
Milestone 5: Define Single Validated Discrete-Event Contract
       │
       ▼
Milestone 6: Execute Macro-to-Field-to-Macro Round-Trip Proof
       │
       ▼
Milestone 7: Defer Broader Economy, Payroll & Procedural Systems
```

---

### Milestone 1: Verify & Archive Host-Boundary Baseline
- **Subsystem Target:** `DoDA/UI/FOIMSX/FOIMSXHostLifecycleProbe.zs` & Host Test Suite.
- **Prerequisite Evidence:** Completed V3 Host-boundary implementation and clean compilation logs with 0 errors.
- **Smallest Safe Change:** Archive baseline hashes and test logs into documentation records; zero code changes.
- **Focused Test:** Execute `FOIMSX-HOST-BOUNDARY-V3-VERIFICATION` (MAP01 toggle, unfreeze on MAP02, save/load release).
- **Non-Goals:** No renderer creation, no ViewState wiring, no input expansion.

### Milestone 2: Plan & Approve ViewState / Dedicated Renderer Integration
- **Subsystem Target:** `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Renderer.zs` (New File).
- **Prerequisite Evidence:** Approved Host-boundary baseline and validated `DoDAPersonnelSnapshotV1ViewState`.
- **Smallest Safe Change:** Implement pure presentation renderer class drawing 640×480 frame and personnel directory driven exclusively by `DoDAPersonnelSnapshotV1ViewState`.
- **Focused Test:** Visual validation on MAP01 confirming identical layout, status color mapping, and string clipping without host coupling.
- **Non-Goals:** No interactive selection, no keyboard scrolling, no native mutation.

### Milestone 3: Plan UI Semantic Intent Router (No Native Mutation)
- **Subsystem Target:** `DoDA/UI/FOIMSX/Input/FOIMSXIntentRouter.zs` (New Component).
- **Prerequisite Evidence:** Standalone Renderer and ViewState integration verified.
- **Smallest Safe Change:** Implement event router translating Arrow keys and Enter into `NavigateUp`, `NavigateDown`, and `Confirm` intents to modify local ViewState selection index.
- **Focused Test:** Keyboard-driven cursor movement across personnel directory rows with selection tracking by `PersonIdText`.
- **Non-Goals:** No native C++ bridge modifications, no case assignment changes.

### Milestone 4: Define Single Read-Only Simulation Snapshot Contract
- **Subsystem Target:** Native C++ Simulation Bridge & `DoDASimulationSnapshotV1Adapter.zs`.
- **Prerequisite Evidence:** Intent router operational and stable in ZScript.
- **Smallest Safe Change:** Define one read-only native C++ export for a single simulation variable (e.g. `person.vitals.fatigue`) with version and revision checking.
- **Focused Test:** Snapshot acquisition test confirming valid numeric reading matching native entity state across world loads.
- **Non-Goals:** No multi-variable bulk expansion, no mutation endpoints.

### Milestone 5: Define Single Validated Discrete-Event Contract
- **Subsystem Target:** Native Event Ingestion Queue & ZScript Event Dispatcher.
- **Prerequisite Evidence:** Milestone 4 read-only snapshot verified.
- **Smallest Safe Change:** Implement one validated discrete event submission (e.g. `SubmitRationConsumption(PersonIdText)`) with native bounds validation and error codes.
- **Focused Test:** Unit proof confirming event submission correctly mutates native person entity and increments revision counter.
- **Non-Goals:** No complex game balance adjustments, no cascading economy ticks.

### Milestone 6: Execute Macro-to-Field-to-Macro Round-Trip Proof
- **Subsystem Target:** End-to-End Simulation-Field Loop.
- **Prerequisite Evidence:** Milestones 4 and 5 completed and tested in isolation.
- **Smallest Safe Change:** Configure a single tactical mission milestone that emits a validated event, updates native simulation state, and reflects the updated state in FOIMS-X UI upon next opening.
- **Focused Test:** Full round-trip test: observe initial state in FOIMS-X $\to$ perform tactical field action $\to$ verify updated state in FOIMS-X.
- **Non-Goals:** No multi-level campaign progression, no procedural generation.

### Milestone 7: Defer Broader Economy, Payroll & Procedural Systems
- **Subsystem Target:** Strategic Simulation Core Expansion.
- **Prerequisite Evidence:** Successful completion and architectural review of Milestone 6 round-trip proof.
- **Smallest Safe Change:** Formalize design specifications for department ledger, dynamic corruption mechanics, and procedural case generation prior to implementation.
- **Focused Test:** Architectural review and specification approval by Human Project Owner.
- **Non-Goals:** No ad-hoc implementation without prior design freeze.

---

## 6. Open Decisions Register

The following unresolved design decisions are recorded for future architectural alignment:

1. **Corruption Definition, Entity Scope, and Scale:**
   - *Status:* Open.
   - *Question:* Is corruption a systemic regional pressure metric, an organizational institutional decay score, or an individual psychological trait? What numeric scale ($[0, 100]$ vs. $[0, 1000]$) and threshold events govern it?
2. **Hunger / Fatigue / Stress Applicability:**
   - *Status:* Open.
   - *Question:* Do psychological and physiological vitals apply equally to all agents, or are certain specialist classes exempt? How do vitals degrade during off-screen strategic time versus active tactical missions?
3. **Strategic Time Progression Model:**
   - *Status:* Open.
   - *Question:* Should strategic time advance continuously in real-time during tactical field play (e.g. 1 real second = 1 strategic minute), advance via discrete end-of-mission batch ticks, or follow a hybrid model?
4. **Salary Cadence, Eligibility, and Ledger Treatment:**
   - *Status:* Open.
   - *Question:* What is the formal payroll accounting cycle (daily, weekly, per mission)? How are agents in hospital/detention compensated, and what penalties arise from salary arrears?
5. **Operating Cost Categories and Accrual Rules:**
   - *Status:* Open.
   - *Question:* What fixed categories (facility rent, armory maintenance, vehicle upkeep) and variable categories (ammunition expended, medical treatment) constitute operational expenditure?
6. **Mission / Objective / Task Canonical Hierarchy & Commit Points:**
   - *Status:* Open.
   - *Question:* At what exact point does a tactical field outcome become immutable in the strategic ledger? Is commit immediate upon objective trigger or deferred to mission debriefing?
7. **Empty-List Focus and Navigation Behavior:**
   - *Status:* Open.
   - *Question:* How should the future Intent Router and panel controller handle keyboard navigation when a directory or case list is empty (`ACQUISITION_EMPTY`) or unavailable?
8. **Renderer Placement and Registration Seam:**
   - *Status:* Open.
   - *Question:* Should the future `DoDAFOIMSXDirectoryRenderer` be instantiated directly by the Host, invoked via a dedicated UI static event handler, or registered as a sub-component of the presentation pipeline?
9. **Multiplayer Policy Beyond Single-Console-Player Proof:**
   - *Status:* Open.
   - *Question:* Will FOIMS-X support cooperative multiplayer in future phases, and if so, how will pause/freeze mechanics, player-specific view states, and input lockouts be partitioned per client?
