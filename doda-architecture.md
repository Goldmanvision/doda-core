
# DoDA Working Architecture & Design Reference

## Status Summary

### Confirmed
- `FieldAgent` is the active ZScript authority for Deadzone Aim mode, angular offsets, smoothing, and limits.
- `DoDALeanInput` and `DoDALeanController` own lean input reading and view translation math.
- `DoDAFOIMSXSessionController` is the single active production authority for FOIMS-X session lifecycle, host binding, freeze/unfreeze orchestration, and input arbitration.
- `DoDAHUDWeapon` consumes structured `DoDAWeaponHUDData` directly from `DoDAHUD.DrawWeaponHUD()`.
- Native strategic simulation in UZDoom C++ fork owns canonical persistent state; Personnel Snapshot V1 and Assignment Snapshot V1 are read-only (Native API v1, Save Schema v4).
- Known pre-existing defect: Left B92 weapon overlay sprite can disappear during left lean in dual/akimbo mode (traceable to layer-2 PSprite/lean pipeline around `d57d853`).

### Planned
- Lean Ability Lifecycle Extraction: Extract `DoDALeanInput` and `DoDALeanController` update execution from `DoDAWeapon` into a player-owned ability lifecycle under `DoDA/Abilities/`.
- Native Bridge Integration: Global declaration and placement of `struct DoDA native` bindings for standalone `doda-core`.

### Investigation
- HUDDeadzone Screen Drawing: Diagnose why `DoDAHUDDeadzone` fails to render overlay graphics when Deadzone Aim Mode is active.
- Deadzone Camera Locking: Implement camera-lock behavior during Deadzone Aim mode until reticle reaches bounding limits.
- B92 Deadzone Firing: Investigate `PistolBase.ShouldStartFire` override behavior when Deadzone Aim is active.

### Open decision
- Configuration lump reorganization: Standardize and clean up `CVARINFO`, `KEYCONF`, and `MENUDEFS`.
- Production native declaration placement in standalone `doda-core` without breaking compatibility with standard GZDoom.

---

> **CRITICAL STATUS BANNER — FOIMS-X VISUAL SPECIFICATION:**  
> The following section is a **visual-direction design reference only**.  
> It defines aesthetic and layout intent for the future administrative terminal interface.  
> It **DOES NOT** authorize or represent active ZScript classes, native C++ contracts, resource lumps, menu definitions, HUD components, terminal widgets, or campaign-state mutations. No FOIMS-X code is implemented.

---

# FOIMS-X Visual Language
## DOS Operations Console / Early Desktop Administration Style

**Status:** Visual-direction reference only  
**Scope:** FOIMS-X strategic-management presentation language  
**Non-scope:** Native data contracts, ZScript implementation, UI registration, terminal behavior, HUD changes, and campaign-state mutation

---

## 1. Core Intent

FOIMS-X should feel like a late-1980s to mid-1990s government operations application: a dense, keyboard-first administrative system running in a hybrid DOS / early-windowed environment.

The reference language combines:

- DOS file-manager density
- Turbo Vision-style framed windows
- Early Windows desktop chrome
- Black operational data wells
- Bright CGA/EGA/VGA-style semantic colors
- Monospaced, column-aligned records
- Explicit function-key command bars
- Minimal decoration and maximal information hierarchy

FOIMS-X is not a modern “retro UI.” It should read as a functional in-world departmental system built around constrained display hardware, structured records, and procedural administration.

---

## 2. Visual Personality

### Primary characteristics

- Dense but legible
- Administrative rather than consumer-friendly
- Keyboard-first
- Crisp and grid-aligned
- High contrast
- Functional color coding
- Layered windows and panels
- Narrow borders, hard edges, and visible bevels
- Text as the dominant information carrier
- Little or no animation outside focus, loading, and error feedback

### Avoid

- Rounded cards
- Soft gradients
- Glass effects
- Modern iconography
- Large whitespace-driven layouts
- Touch-first controls
- Decorative dashboards
- Unlabeled visual indicators
- Mutating controls presented before their native contract exists
- Fake “terminal” noise, scanlines, or arbitrary glitch effects

---

## 3. Display Architecture

```text
Fullscreen FOIMS-X surface
└─ Desktop/background field
   └─ Main application window
      ├─ Title bar
      ├─ Menu bar
      ├─ Main work area
      │  ├─ Directory/list window
      │  └─ Detail/readout window
      └─ Command/status bar
```

### Recommended hierarchy

1. **Desktop/background**
   - Deep navy or nearly black
   - May contain subtle dot-pattern or hatch texture only if it remains readable at all resolutions
   - Must not compete with data windows

2. **Application shell**
   - Gray Windows-style frame
   - Dark drop shadow offset down/right
   - Active title bar in deep blue
   - Inactive windows use neutral gray title bars

3. **Operational windows**
   - Dark blue or black content wells
   - Bright cyan, white, gray, or magenta borders depending on function
   - Fixed internal grids and dense rows

4. **Readout fields**
   - Black background
   - White, cyan, green, gold, or red bitmap text
   - Bracketed or ruled headers
   - No paragraph-first presentation

5. **Command strip**
   - Fixed along the lower edge
   - Function-key commands and navigation guidance
   - Informational only until a future native command contract is approved

---

## 4. Palette

Color must communicate both hierarchy and system state.

| Token | Suggested color | Primary use |
|---|---:|---|
| Desktop Navy | `#000080` | Background field, active DOS-style workspace |
| Data Black | `#000000` | List wells, detail wells, dense readouts |
| System Gray | `#B0B0B0` | Window body, menu strip, inactive shell |
| Highlight White | `#FFFFFF` | Bevel highlights, borders, primary readable text |
| Shadow Gray | `#707070` | Bevel shadows, inactive separators |
| Deep Shadow | `#202020` | Drop shadows, recessed edges |
| Cyan | `#00C0C0` | Active pane headers, focused input/readout regions |
| Magenta | `#C000C0` | Menu windows, subsystem navigation, modal emphasis |
| Operational Green | `#00B000` | Valid, available, confirmed, ready |
| Attention Gold | `#C0B000` | Deferred, warning, stale, incomplete-but-readable |
| Fault Red | `#C00000` | Invalid, unavailable, rejected, failure |
| Neutral Blue | `#0000B0` | Secondary window headers, selection preservation |

### Color rules

- Use **cyan** for active focus and primary pane identity.
- Use **magenta** for menus, modal navigation, or a distinct subsystem layer.
- Use **green** only for explicitly valid/available/confirmed data.
- Use **gold** for attention states, deferred fields, stale snapshots, and warnings.
- Use **red** for invalid, unavailable, rejected, or unreadable content.
- Use **white** for neutral data and structural linework.
- Never rely on color alone: pair every semantic color with explicit text.

---

## 5. Typography

### Primary type treatment

- Bitmap or bitmap-like font
- Monospaced wherever columns matter
- Uppercase for system labels, section headers, command labels, and status states
- Title case or normal capitalization only for human-readable names
- Fixed-width numeric formatting where numeric values are shown
- Single-line rows in directories; no wrapping inside tabular records

### Text hierarchy

| Layer | Treatment | Example |
|---|---|---|
| Application title | Uppercase, white on blue | `FOIMS-X // PERSONNEL` |
| Pane title | Uppercase, black on cyan or white on blue | `PERSONNEL DIRECTORY` |
| Section label | Bracketed uppercase | `[CURRENT ASSIGNMENT]` |
| Field label | Uppercase with dots or colon alignment | `STATUS....:` |
| Primary value | White or cyan on black | `AVAILABLE` |
| Good value | Green on black | `AVAILABLE` |
| Warning/deferred value | Gold on black | `— DEFERRED —` |
| Error/fault value | Red on black | `UNAVAILABLE` |
| Keyboard hint | Black or red mnemonic text on gray strip | `F1 HELP` |

### Field formatting

Preferred:

```text
STATUS....: AVAILABLE
SKILL.....: 072
WORKLOAD..: 041
```

Acceptable compact format:

```text
STATUS: AVAILABLE   SKILL: 072   WORKLOAD: 041
```

Avoid:

```text
Current status is available.
The employee has a skill rating of 72.
```

---

## 6. Window Grammar

### Main application window

```text
┌─ FOIMS-X // PERSONNEL ───────────────────────────────────────── _ □ X ┐
│ File  Records  View  Help                              14:32:05         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         Application work area                           │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ F1 Help  F2 Filter  F3 View  Tab Pane  Enter Select  Esc Exit          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Frame behavior

- Use hard rectangular corners.
- Use white top/left bevels and gray/black bottom/right bevels.
- Apply one dark offset drop shadow behind floating windows.
- Keep border thickness consistent across the application.
- Use inset black wells for lists, values, text readouts, and record details.
- Avoid rounded buttons, soft shadows, translucency, or animated chrome.

### Title bars

**Active title bar**
- Deep blue fill
- White title text
- Optional compact application marker at left
- Standard visual control boxes at right only if they do not imply unsupported window-management behavior

**Inactive title bar**
- Neutral gray fill
- Dark text
- Reduced contrast
- Retains title for orientation

---

## 7. Panel Types

### Directory panel

Used for personnel, cases, tasks, locations, evidence, assets, or future lists.

```text
┌─ PERSONNEL DIRECTORY ────────────────────────────────────────┐
│ ID              NAME                    STATUS               │
│ ──────────────────────────────────────────────────────────── │
│ > 100001         Alice Morgan            AVAILABLE            │
│   100002         Bob Reyes               ASSIGNED             │
│   100003         Charlie Vale            UNAVAILABLE          │
│                                                               │
│ RECORDS: 003                                                 │
└───────────────────────────────────────────────────────────────┘
```

Rules:

- First column is a visual selection marker only.
- Persistent identity is never represented by row position.
- Rows remain one line.
- Column headers are fixed.
- Overflow truncates rather than wraps.
- Visible count is informational, not a selection identity.

### Detail panel

Used for the currently selected record.

```text
┌─ PERSONNEL RECORD ───────────────────────────────────────────┐
│ [IDENTITY]                                                    │
│ PERSON ID.: 100001                                            │
│ NAME......: Alice Morgan                                      │
│                                                               │
│ [PERSONNEL STATE]                                             │
│ STATUS....: AVAILABLE                                         │
│ SKILL.....: 072                                               │
│ WORKLOAD..: 041                                               │
│                                                               │
│ [CURRENT ASSIGNMENT]                                          │
│ ASSIGNMENT: — UNASSIGNED —                                    │
│ TASK ID...: —                                                 │
│ TASK......: —                                                 │
└───────────────────────────────────────────────────────────────┘
```

Rules:

- Details are grouped by bracketed headers.
- No unsupported strategic data may be introduced as decorative filler.
- Absent data must be explicit: `—`, `UNASSIGNED`, `UNAVAILABLE`, or `DEFERRED`.
- Detail values must reflect the read-only snapshot, never inferred state.

### Modal panel

Used for errors, contract mismatch, or blocking read failures.

```text
┌─ FOIMS-X NOTICE ───────────────────────────────┐
│                                                  │
│ PERSONNEL SNAPSHOT NOT AVAILABLE                 │
│                                                  │
│ REASON: CONTRACT VERSION MISMATCH                │
│                                                  │
│ PRESS ESC TO RETURN                              │
└──────────────────────────────────────────────────┘
```

Rules:

- Centered over retained background.
- Magenta or blue shell with black content well.
- Red text only for the fault identity; do not render the entire modal in red.
- No implied retry/mutation button unless a future input contract permits it.

---

## 8. Focus and Selection

### Keyboard focus

The interface is keyboard-first even when later mouse support exists.

| State | Visual treatment |
|---|---|
| Active pane | Cyan border or cyan title strip |
| Inactive pane | White/gray border or blue title strip |
| Selected list row | Cyan fill, black text, `>` marker |
| Selected row in inactive pane | Blue or dark fill, white text, no cyan override |
| Focused modal | Magenta or cyan border with strongest contrast |
| Disabled/unavailable item | Red or gray text; cannot visually resemble selection |

### Selection identity rule

```text
Selection key = exact personIdText
```

Never use:

```text
row index
display name
actor pointer
map TID
spawn order
inventory instance
assignment ID
task ID
```

The visual list may reorder. The selected record remains the record whose current `personIdText` exactly matches the stored presentation selection key.

---

## 9. Data States

### Ready

```text
STATUS....: AVAILABLE
```

- Normal black readout well
- White labels
- Green or white valid values
- No warning banner

### Assigned

```text
STATUS....: ASSIGNED
ASSIGNMENT: 700045
TASK ID...: 800112
TASK......: RECORD REVIEW
```

- Status may use cyan or green depending on final semantic policy
- Assignment data appears only when supplied by the native snapshot
- Do not add location, schedule, role, case name, or assignment metadata

### Unassigned

```text
STATUS....: AVAILABLE
ASSIGNMENT: — UNASSIGNED —
TASK ID...: —
TASK......: —
```

- All-empty assignment/task data maps to explicit unassigned presentation
- Do not imply idle time, availability reason, schedule gap, or missing task error

### Unavailable

```text
STATUS....: UNAVAILABLE
```

- Identity and snapshot-supplied values remain visible
- Use red status text
- Do not infer whether the person is injured, deployed, absent, suspended, dead, or otherwise unavailable

### Empty

```text
NO PERSONNEL RECORDS IN CURRENT SNAPSHOT
```

- Valid state
- No selected row
- No fabricated person details
- No error framing unless the snapshot itself was invalid

### Loading

```text
ACQUIRING PERSONNEL SNAPSHOT...
```

- No fake record count
- Optional segmented progress indicator with no fabricated percentage
- Existing accepted content may remain visible only if explicitly labeled stale

### Stale

```text
STALE SNAPSHOT — DISPLAYING LAST VALID READOUT
```

- Gold banner
- Retain last valid data only
- Never present stale values as current
- Do not imply native persistence or mutation failure unless explicitly known

### Invalid / rejected

```text
PERSONNEL SNAPSHOT REJECTED
REASON: INCONSISTENT ROW DATA
```

- Red fault label
- No partial replacement of an accepted model
- Do not render an invalid in-range row
- If no prior valid data exists, show an empty detail area rather than fabricated placeholders

---

## 10. Command-Bar Language

Function-key strips should reinforce the DOS operational feel.

```text
F1 Help  F2 Filter  F3 View  F4 Refresh  Tab Pane  Enter Select  Esc Exit
```

### Rules

- Show only commands supported by the current approved slice.
- Until an action has an approved native/read-only contract, display no command hint for it.
- Do not expose:
  - Assign
  - Deploy
  - Cancel task
  - Transfer
  - Edit personnel
  - Delete record
  - Advance time
  - Save
  - Load
  - Schedule
  - Auction
  - Case operation
- Read-only navigation may eventually include:
  - `F1 HELP`
  - `TAB PANE`
  - `↑↓ SELECT`
  - `PGUP/PGDN BROWSE`
  - `HOME/END`
  - `ESC EXIT`

---

## 11. Personnel Overview Layout

```text
┌─ FOIMS-X // PERSONNEL OVERVIEW ───────────────────────────────────────────┐
│ File  Records  View  Help                                  000000001245    │
├────────────────────────────────────────────────────────────────────────────┤
│ ┌─ PERSONNEL DIRECTORY ─────────────────┐ ┌─ SELECTED PERSON ───────────┐ │
│ │ ID          NAME            STATUS     │ │ [IDENTITY]                  │ │
│ │ ────────────────────────────────────── │ │ PERSON ID.: 100001          │ │
│ │ > 100001     Alice Morgan   AVAILABLE  │ │ NAME......: Alice Morgan     │ │
│ │   100002     Bob Reyes      ASSIGNED   │ │                              │ │
│ │   100003     Charlie Vale   UNAVAILABLE│ │ [PERSONNEL STATE]           │ │
│ │                                        │ │ STATUS....: AVAILABLE        │ │
│ │ RECORDS: 003                           │ │ SKILL.....: 072              │ │
│ └────────────────────────────────────────┘ │ WORKLOAD..: 041              │ │
│                                              │                              │ │
│                                              │ [CURRENT ASSIGNMENT]         │ │
│                                              │ ASSIGNMENT: — UNASSIGNED —   │ │
│                                              │ TASK ID...: —                │ │
│                                              │ TASK......: —                │ │
│                                              └──────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────────┤
│ SNAPSHOT REV: 000000000001  STRATEGIC TIME: 000000001245                  │
│ F1 Help  Tab Pane  ↑↓ Select  PgUp/PgDn Browse  Enter View  Esc Exit      │
└────────────────────────────────────────────────────────────────────────────┘
```

This is a structural reference, not a final layout or implementation requirement.

---

## 12. FOIMS-X Content Rules

### Safe visual content

When supplied by the confirmed Personnel Snapshot V1 contract:

- API version
- Snapshot revision token
- Strategic-minute token
- Person count
- Person ID token
- Display name
- Status
- Skill
- Workload
- Assignment ID token
- Task ID token
- Task title

### Deferred content

Do not show until a future native model explicitly exposes it:

- Role
- Rank
- Department
- Clearance
- Location
- Current post
- Assignment schedule
- Case association
- Case ownership
- Qualifications
- Certifications
- Health
- Stress
- Morale
- Fatigue
- Portrait
- Inventory
- Equipment
- Payroll
- Disciplinary history
- Native actor references
- Map-local identity
- AActor pointer
- TID
- Spawn order
- Inventory instance

---

## 13. Implementation Boundaries

This visual language does not authorize:

- ZScript creation
- Native binding changes
- `doda-core` edits
- `zscript.txt` registration
- MENUDEF changes
- MAPINFO changes
- HUD integration
- Terminal integration
- New event handlers
- Key binding changes
- Strategic mutations
- Task assignment controls
- Scheduler controls
- Campaign persistence operations
- Final UI implementation

Future implementation must remain a read-only presentation client for native-owned Personnel Snapshot V1 data.

---

## 14. Reference Summary

```text
WINDOWS SHELL
+ DOS DATA WELLS
+ TURBO VISION BORDERS
+ FILE-MANAGER DENSITY
+ KEYBOARD COMMAND STRIP
+ EXPLICIT STATUS TEXT
+ STRICT NATIVE DATA BOUNDARY
= FOIMS-X
```

---

# 15. Personnel Simulation Milestones

## 15.1 Personnel Snapshot V1 — Current Capability

**Status:** Native contract and inert presentation tier complete; runtime diagnostics proof complete; renderer and activation remain deferred.

Personnel V1 is a read-only, native-backed personnel snapshot vertical slice. It exposes canonical native people to a future FOIMS-X screen, but it does not yet simulate advancing strategic time, task progression, locations, civilian records, or save/load persistence.

### Confirmed V1 capabilities

| Capability | Current status |
|---|---|
| Canonical person identity | Native-owned `PersonIdText`; exact string equality is the only presentation selection key |
| Default personnel | Five deterministic native campaign-default people |
| Snapshot metadata | Native API version, revision token, strategic-minutes token, and bounded record count |
| Personnel fields | Display name, raw status integer, skill, workload, assignment ID token, task ID token, task title |
| Assignment structure | All-empty triple = unassigned; all-non-empty triple = assigned; mixed triple = invalid |
| Snapshot consistency | Revision-before/revision-after comparison rejects an unstable candidate |
| Snapshot validation | Bounded-row validation, blank/duplicate ID rejection, invalid-status rejection, and assignment-triple validation |
| Native bridge | `struct DoDA native` exposes 12 read-only Personnel Snapshot V1 query methods |
| Presentation tier | Inert Model → Adapter → ViewState files exist under `DoDA/UI/FOIMSX/PersonnelV1/` |
| Live proof | Debug x64 native bridge proof returned API v1, revision 1, strategic minutes 0, five people, and revision match |
| FOIMS-X runtime UI | Deferred; no root include, renderer, lifecycle owner, input owner, or registration exists |

### Current fixture state

```text
API VERSION....: 1
REVISION.......: 1
STRATEGIC TIME.: 0
PERSONNEL COUNT: 5
ASSIGNMENTS....: all fixture rows structurally unassigned
```

The V1 default fixture currently contains:

```text
1  Ruth M. Green
2  Michelle C. Thomas
3  Brian C. Gordon
4  Leonard M. Martin
5  Harold M. Beltz
```

### Explicit V1 non-capabilities

- No advancing strategic time.
- No save/load round-trip proof.
- No canonical task records or task progress.
- No canonical location records or person-location state.
- No civilian snapshot contract.
- No field actor materialization.
- No FOIMS-X renderer, terminal, menu, HUD integration, or input binding.
- No LibColony scheduling or optimization.

---

## 15.2 Weekend V2 Goal — Persistent Operational Slice

**Status:** Planned implementation target.

The weekend V2 target is a deliberately small but complete strategic-simulation chain:

```text
Native strategic clock
→ deterministic task progression
→ people assigned to tasks at fictional locations
→ native persistence
→ read-only FOIMS-X browsing
```

V2 is not a complete economy, final terminal, scheduler, procedural world generator, or full NPC simulation. It is a visible, saveable operational slice that proves native state changes over strategic time and can be browsed through FOIMS-X.

### Native V2 minimum scope

| V2 element | Minimum implementation |
|---|---|
| Strategic clock | Native `StrategicMinutes` advances by explicit fixed increments; no per-tic unloaded-world simulation |
| Persistence | Clock, people, locations, tasks, assignments, and task progress serialize and restore |
| Locations | Two or three fictional locations with stable IDs and display names |
| Personnel | Retain the five default personnel; optionally add a small curated safe civilian subset |
| Tasks | Two to four native task records with stable ID, title, location ID, state, progress, and time requirements |
| Assignment | A person is unassigned or has one complete valid assignment/task triple |
| Progression | Advancing strategic time deterministically changes assigned task progress |
| Completion | Tasks progress through `Pending → Active → Complete` under native rules |
| State updates | Native rules update workload, assignment state, and location/task association |
| Read-only snapshots | Native query contracts expose only fields required by FOIMS-X personnel, task, and location browsing |
| Validation | Native code rejects unknown IDs, illegal transitions, invalid location references, mixed assignment triples, and impossible progress values |

### V2 reference scenario

```text
08:00  TASK: Survey anomalous emissions
       LOCATION: Morrow Point Waterworks
       ASSIGNED: Brian C. Gordon + Michelle C. Thomas
       PROGRESS: 0%

09:00  Advance strategic time by 60 minutes
       PROGRESS: 25%
       Both personnel report a valid active assignment/task/location state.

12:00  Advance strategic time by 180 minutes
       PROGRESS: 100%
       Task transitions to Complete.
       Assignment fields clear or transition according to one explicit
       native-owned completion rule.
       Personnel workload updates deterministically.
```

The scenario is a proof fixture, not a final task-generation or balancing model.

---

## 15.3 V2 FOIMS-X Browsing Scope

**Status:** Planned; read-only only.

The V2 FOIMS-X goal is a browse-only operational database. It must not mutate strategic time, assignments, tasks, locations, or persistent records.

| Screen | Display scope | Interaction scope |
|---|---|---|
| Personnel directory | Name, raw status, skill, workload, assigned/unassigned indicator | Browse; select by exact `PersonIdText` |
| Personnel detail | Full opaque ID, accepted personnel fields, assignment/task/location readout when exposed | Read-only |
| Civilian directory | Curated safe display fields only: name, role/occupation, fictional location, case/task relevance when exposed | Browse/detail only |
| Task board | Task title, native state, progress, location, assigned people | Browse/detail only |
| Location detail | Fictional location name, active-task count, assigned/present people when exposed | Browse/detail only |
| Strategic header | Revision token, strategic-minutes token, current/stale state | Read-only indicator |

### V2 FOIMS-X interaction rules

- `PersonIdText` remains the only persistent personnel-selection identity.
- Row position is temporary visual focus only.
- No automatic first-row selection.
- No automatic reselection after selected-person disappearance.
- No fallback lookup by display name, task ID, assignment ID, actor reference, TID, spawn order, inventory instance, source UUID, or CSV row.
- Stale snapshots remain visibly stale and retain only last accepted data.
- Arrow keys may navigate local UI focus only while an approved FOIMS-X owner has input focus.
- Number keys may be reserved for future FOIMS-X local pages/actions only while FOIMS-X owns input.
- TAB remains reserved for TAPLINE / automap presentation and must not become FOIMS-X activation.

---

## 15.4 V2 Delivery Sequence

Prioritize a vertical slice over broad subsystem completeness:

1. Add native strategic-time advancement by an explicit deterministic increment.
2. Prove strategic time and current personnel state survive save → restart/load.
3. Add two or three canonical fictional locations.
4. Add two to four canonical deterministic tasks tied to locations.
5. Assign two or three existing personnel while retaining unassigned personnel.
6. Advance time and apply deterministic task progress/completion rules.
7. Add a small curated safe civilian subset if needed for browsing coverage.
8. Expose read-only native snapshots for personnel, tasks, and locations.
9. Approve one FOIMS-X activation/lifecycle/input seam.
10. Implement one read-only browse shell using the existing V1 presentation principles.
11. Keep TAPLINE and FOIMS-X as separate modes.

---

## 15.5 V2 Deliberate Deferrals

The following are not weekend blockers:

- LibColony optimization.
- Full case tracks, evidence, warehouse, auction, or economy systems.
- Broad world pressure simulation.
- Field NPC materialization.
- Per-tic simulation of unloaded people.
- Full civilian biography or sensitive authoring-data ingestion.
- Player-driven assignment commands.
- Map generation, travel simulation, or permanent location maps.
- Final raw-status vocabulary.
- Full terminal/menu implementation.
- HUD, weapon, or TAPLINE refactors unrelated to the approved FOIMS-X seam.

---

## 15.6 V2 Completion Definition

The V2 weekend slice is complete when all of the following are true:

1. A new campaign begins with five personnel, a small civilian subset if used, fictional locations, and deterministic tasks.
2. Native strategic time advances in fixed increments.
3. Native tasks progress and complete deterministically as time advances.
4. Native people reflect valid assignment/task/location state.
5. Save, restart, and load restore the same native strategic state.
6. FOIMS-X browses personnel, tasks, and locations read-only through approved native snapshots.
7. Selection survives roster reorder only through exact persistent ID reconciliation.
8. TAPLINE/TAB and FOIMS-X remain separate UI modes.
9. No ZScript component becomes authoritative for strategic state, persistence, task progression, or validation.

---

# 16. Deferred Policy — Recovery, Strategic Continuity, and Persistence

## 16.1 Field-Player Recovery and Strategic State Continuity

**Status:** Approved design policy and future persistence requirement; implementation deferred.

### Design Policy and Lore
- **Recovery and Hospitalization:** Field-player death is represented in game lore and future strategic systems as recovery and hospitalization, not campaign death or strategic-state reset.
- **Strategic Continuity:** A player recovery/respawn must not reset FOIMS-X strategic progression, including personnel availability, assignment progress, cases, evidence, locations, strategic time, or other durable campaign records.
- **Save/Load Independence:** FOIMS-X should not require loading a saved game merely to preserve strategic progression across field-player recovery/respawn.

### Validated Baseline Behavior vs. Future Requirements
- **Current Validated Behavior:** Direct workstation testing showed FOIMS-X personnel task progression survived player recovery/respawn, advancing from 50 percent to 75 percent and then 100 percent after respawn and re-entry.
- **Future Required Implementation:** Persistent recovery/hospitalization mechanics and operational-budget consequences require dedicated native/persistence design and validation. Future approved strategic systems may apply a recovery cost against the player’s operational budget and may apply corresponding recovery, availability, cost, or time effects to downed field agents.

### Deliberately Unresolved Elements (Deferred Scope)
This is a future design requirement only. The following elements are intentionally unresolved and must be designed and implemented in later dedicated tasks:
- Exact recovery cost formulas and operational budget models.
- Hospitalization and recovery duration calculation.
- Downed field-agent recovery, cost, availability, and time rules.
- Stable native identity model for persistent entities (Cross-reference: Task 37).
- Versioned backward-safe save-schema fields and serialization (Cross-reference: Task 38).
- Native invariant validation rules for recovery and persistence transitions (Cross-reference: Task 36 for save/restore validation).
- FOIMS-X UI presentation and notifications for hospitalization/recovery.

---

# 17. FOIMS-X Production Architecture & Seam Boundaries

## 17.1 Session Controller & Lifecycle Ownership
- **Authority**: `DoDAFOIMSXSessionController` (`DoDA/UI/FOIMSX/FOIMSXSessionController.zs`) is a registered `StaticEventHandler` in `MAPINFO` and the sole production owner of FOIMS-X activation, deactivation, host binding, freeze/unfreeze orchestration, and lifecycle safety.
- **Freeze Mechanics**: Centralizes player freeze using engine flag `CF_TOTALLYFROZEN` (`mFOIMSXAppliedFreeze`), ensuring idempotent application on session entry and guaranteed release on session exit, player death, player respawn, host destruction, map load (`WorldLoaded`), and map unload (`WorldUnloaded`).
- **Input Interception**: Intercepts and consumes toggle (`O` / `FOIMSX_KEYSCAN_O`), close (`Escape` / `FOIMSX_KEYSCAN_ESCAPE`), and navigation keys while active, suppressing background gameplay firing, movement, and weapon switching.
- **Host Binding**: Reconciles host bindings (`mBoundHost`) via `WorldLoaded` generation tracking, maintaining strict null-safety across map transitions and engine savegame reloads.

## 17.2 Domain Separation & Pure Renderers
- **Personnel & Assignment Domain Independence**: `PersonnelSnapshotV1` and `AssignmentSnapshotV1` remain distinct domain models, adapters, view states, and renderers.
- **Pure Rendering**: `DoDAFOIMSXDirectoryRenderer` (`PersonnelSnapshotV1Renderer.zs`) and `DoDAAssignmentSnapshotV1Renderer` (`AssignmentSnapshotV1Renderer.zs`) are strictly read-only presentation components. Renderers read `DoDAFOIMSXSessionController.IsSessionActive()` and project view-state data without mutating engine freeze flags, altering session state, or invoking snapshot acquisition during `RenderOverlay()`.

## 17.3 Snapshot Refresh & Invalidation Pipeline
- **Activation-Boundary Refresh (Task 29)**: Successful session activation or re-entry in `DoDAFOIMSXSessionController.ActivateSession()` triggers an explicit full snapshot acquisition (`RefreshSessionData(true)`). No polling or rebuild checks occur during `Tick()`, `UiTick()`, `Render()`, or `RenderOverlay()`.
- **Revision-Driven Refresh (Task 30)**: Native queries `DoDA.GetPersonnelSnapshotRevisionText()` and `DoDA.GetAssignmentSnapshotRevisionText()` provide monotonic revision tokens. Domain data refreshes only when native revisions change or explicit events (`"DoDAFOIMSXDataChanged"`, `"DoDAFOIMSXRefresh"`) are received. Unchanged domains bypass reconstruction.
- **Shared Refresh Bookkeeping (Task 31)**: `DoDAFOIMSXSnapshotRefreshState` (`DoDA/UI/FOIMSX/FOIMSXSnapshotRefreshState.zs`) encapsulates domain-agnostic last-applied revision text, initialization status, `ShouldRefresh()`, and `MarkApplied()` without any domain or native knowledge.
- **Standardized Acquisition Status (Task 32)**: `EDoDAFOIMSXSnapshotAcquireStatus` (`DoDA/UI/FOIMSX/FOIMSXSnapshotAcquireStatus.zs`) standardizes outcome states (`FOIMSX_ACQUIRE_SUCCESS`, `FOIMSX_ACQUIRE_UNAVAILABLE`, `FOIMSX_ACQUIRE_INCOMPATIBLE_VERSION`, `FOIMSX_ACQUIRE_REJECTED`). Failed, rejected, or incompatible acquisitions safely preserve existing UI state and never mark revisions as applied.

## 17.4 Stateless Drawing Primitives (Task 33)
- **Shared Helpers**: `DoDAFOIMSXDrawingHelpers` (`DoDA/UI/FOIMSX/FOIMSXDrawingHelpers.zs`) provides stateless 2D virtual coordinate (640x480) drawing primitives: `DrawVirtualRect`, `GetRealClipRect`, `DrawRaisedPanel`, `DrawSunkenPanel`, `DrawVirtualText`, and `DrawClippedText`.
- **Domain Independence**: Drawing helpers accept all coordinates, fonts, colors, clipping bounds, and text strings explicitly via arguments, possessing zero session, model, adapter, or domain data references.

## 17.5 Navigation Contract & Reserved Keys (Task 35)
- **Command Classification**: `EDoDAFOIMSXNavCommand` formalizes navigation intent (`FOIMSX_NAV_NONE`, `FOIMSX_NAV_PREVIOUS`, `FOIMSX_NAV_NEXT`, `FOIMSX_NAV_PAGE_PREVIOUS`, `FOIMSX_NAV_PAGE_NEXT`, `FOIMSX_NAV_FIRST`, `FOIMSX_NAV_LAST`, `FOIMSX_NAV_SELECT`, `FOIMSX_NAV_CLEAR_SELECTION`).
- **Input Parsing**: `ClassifyNavInput(keyScan, keyChar)` maps raw key inputs to semantic commands without hardcoded magic numbers.
- **Engine-Reserved Escape**: The `Escape` key is engine-reserved for the game main menu and is never intercepted, consumed, or remapped as a FOIMS-X back/close command.

---

# 18. Weapon System HUD Data Flow & Presentation Boundary

## 18.1 Structured HUD Data Parameter Flow (Task 34)
- **Structured Data Forwarding**: `DoDAHUD.DrawWeaponHUD()` (`DoDA/UI/FieldAgent/HUD.zs`) acquires primary and companion weapon data via `DoDAHUDWeaponBridge` and forwards structured `DoDAWeaponHUDData` objects directly to `DoDAHUDWeapon.DrawWeaponReadout()` and `DrawWeaponSlot()` (`DoDA/UI/FieldAgent/HUDWeapon.zs`).
- **Parameter Reduction**: Replaces 19-parameter and 11-parameter unpacked signatures with direct object references (`primary`, `companion`, `reserveRounds`), eliminating redundant field unpacking while preserving 100% of formatting, color-coding, and layout rules.
- **Invariance**: Zero gameplay, damage, spread, aim, recoil, magazine capacity, chambering, or reload mechanics were altered.

## 18.2 PSprite Layer-2 Pipeline & Known Akimbo Left-Lean Defect
- **Pipeline Architecture**: Dual/akimbo weapon presentation renders the companion weapon on weapon PSprite layer 2 (`PSP_LEFTWEAPON`).
- **Known Pre-existing Defect**: When dual B92 pistols are equipped and the player performs a left lean (`+user1`), the left B92 weapon overlay sprite can disappear. The HUD readout for the companion weapon remains active, proving companion weapon data is intact.
- **Provenance**: Verified pre-existing prior to Task 34 and traceable to weapon layer-2 state resolution and lowering offsets in `WeaponBase.zs` / `PistolBase.zs` / `AkimboInputHandler.zs` (introduced in commit `d57d853`). This defect is outside Wave 3 scope and deferred to dedicated akimbo weapon system refactoring.

---

# 19. Native Strategic Persistence & Save Schema 4 Architecture

## 19.1 Native Authority & Serialization Seam (Task 36, 37, 38)
- **Authoritative Simulation**: Native `DoDASimulation` (`uzdoom-official/src/doda/DoDA_Simulation.cpp`) is the sole authoritative owner of strategic time, personnel, fatigue, tasks, locations, and assignments.
- **Persistence Transport**: Serializes into and restores from `globals.json` under root object `"doda"`.
- **Transient UI Separation**: FOIMS-X UI view-states, selection indices, and active session states are transient. Upon savegame restoration (`WorldLoaded`), UI sessions safely reconcile without dangling host pointers, leaving canonical simulation state entirely in native ownership.

## 19.2 Save Schema Version 4 Specification
- **Current Version**: `DODA_SAVE_SCHEMA_VERSION = 4` (`src/doda/DoDA_SaveSchema.h`).
- **Root Fields**: `"schema_version"` (`int`), `"strategic_minutes"` (`uint64`), `"next_person_id"` (`uint64`), `"next_task_id"` (`uint64`), `"next_assignment_id"` (`uint64`), `"next_location_id"` (`uint64`).
- **Entity Collections**:
  - `"locations"`: Array of `{ "id": uint64, "name": string }` (up to `DODA_MAX_LOCATIONS = 1024`).
  - `"people"`: Array of `{ "id": uint64, "name": string, "skill": int, "workload": int, "status": int, "fatigue": int }` (up to `DODA_MAX_PEOPLE = 1024`).
  - `"tasks"`: Array of `{ "id": uint64, "title": string, "location_id": uint64, "priority": int, "required_skill": int, "estimated_work": int, "status": int, "progress": int }` (up to `DODA_MAX_TASKS = 1024`).
  - `"assignments"`: Array of `{ "id": uint64, "person_id": uint64, "task_id": uint64, "cost": int }` (up to `DODA_MAX_ASSIGNMENTS = 1024`).
- **Internal vs. Display Separation**: Native persistence fields (internal fatigue, allocator counters, raw numeric IDs, schema version) are persisted for simulation continuity but are not UI display requirements.

## 19.3 Durable Native Identity & Relational Foreign Keys (Task 37)
- **Durable 64-Bit Keys**: All entities utilize durable `uint64_t` scalar keys (`DoDAPersonId`, `DoDATaskId`, `DoDAAssignmentId`, `DoDALocationId`).
- **Monotonic Allocator Counters**: Allocator counters (`mNextPersonId`, `mNextTaskId`, `mNextAssignmentId`, `mNextLocationId`) are serialized into savegames, strictly post-incremented, and never decremented, guaranteeing collision-free non-reuse of IDs across save/load.
- **Foreign Key Relational Integrity**: All relationships (`Assignment -> Person`, `Assignment -> Task`, `Task -> Location`, `Person -> Assignment -> Task`) resolve exclusively via scalar ID matching. Deserialization strictly verifies foreign key existence and enforces per-person assignment uniqueness (`std::set`). Zero persistent relationships depend on vector indices, UI selection, display names, or memory addresses.

## 19.4 Backward-Safe Schema Migration (Task 38)
- **Schema 1 Migration**: Restores `strategic_minutes` and resets collections to default campaign baseline.
- **Schema 2 Migration**: Deserializes canonical people, tasks, and assignments; synthesizes default Location `{ 1, "Morrow Point Waterworks" }` and `next_location_id = 2`; defaults `Task.LocationId = 1` and `Person.Fatigue = 0`.
- **Schema 3 Migration**: Deserializes canonical people with explicit `fatigue`; synthesizes default location and defaults `Task.LocationId = 1`.
- **Corrupt / Unsupported Save Rejection**: Malformed JSON, missing required fields, enum out-of-range, or unsupported schema versions safely invoke `ResetPersonnelSnapshotAfterLoadFailure()`, restoring clean defaults without engine crashes or memory corruption.

---

# 20. Wave 3 Refactor Task & Delivery Register

| Task | Title | Scope & Delivery Summary | Code Change Status | Validation Status |
|---|---|---|---|---|
| **Task 27** | FOIMS-X Session Controller | Created `DoDAFOIMSXSessionController` as unified lifecycle, freeze, and input owner. | Implemented (`527a90f`) | User-run runtime verified green |
| **Task 28** | FOIMS-X Rendering Consolidation | Audited active production render paths; confirmed single entry point in `DoDAFOIMSXDirectoryRenderer`. | No code change | Verified by static & reference audit |
| **Task 29** | FOIMS-X Activation Refresh | Established forced snapshot refresh at activation boundary; removed render-loop snapshot acquisition. | Implemented (`e9a6161`) | User-run runtime verified green |
| **Task 30** | Revision-Driven Snapshot Refresh | Added native revision query checking and event routing (`DoDAFOIMSXDataChanged`) to prevent redundant rebuilds. | Implemented (`1f24bf1`) | User-run runtime verified green |
| **Task 31** | Shared Snapshot Infrastructure | Extracted domain-agnostic `DoDAFOIMSXSnapshotRefreshState`; includes parser compatibility repair (`83be123`). | Implemented (`f01fec4`, `83be123`) | User-run runtime verified green |
| **Task 32** | Adapter Rejection Standardization | Added `EDoDAFOIMSXSnapshotAcquireStatus` to standardize acquisition outcomes across adapters. | Implemented (`b8a0cbf`) | User-run runtime verified green |
| **Task 33** | FOIMS-X Drawing Helpers | Extracted stateless 2D virtual coordinate drawing primitives into `DoDAFOIMSXDrawingHelpers`. | Implemented (`128d2f1`) | User-run runtime verified green |
| **Task 34** | Weapon/HUD Parameter Reduction | Forwarded structured `DoDAWeaponHUDData` directly to `DrawWeaponReadout`; documented known pre-existing B92 akimbo left-lean defect. | Implemented (`b399502`) | User-run runtime verified green |
| **Task 35** | FOIMS-X Navigation Contract | Formalized `EDoDAFOIMSXNavCommand` and `ClassifyNavInput`; preserved engine-reserved Escape. | Implemented (`ed409d9`) | User-run runtime verified green |
| **Task 36** | Static Host Save/Restore Validation | Validated static host and UI session reconciliation across engine save/restore routines. | No code change | User-run save/restore matrix green |
| **Task 37** | Native Persistence Identity | Audited durable 64-bit scalar entity IDs, monotonic allocators, and foreign-key joins in Schema 4. | No code change | Source-proven & save/restore verified |
| **Task 38** | Save Schema Extension | Audited Save Schema Version 4 field coverage and backward migration for Schemas 1–3. | No code change | User-run Schema 4 save/load verified |
| **Task 39** | MAP03 Packaging Validation | Map packaging and dependency resolution previously validated. | Intentionally skipped | Previously validated |
| **Task 40** | Repository Artifact Archiving | Produced comprehensive Artifact Classification Inventory; retained active POC handlers. | No code change | Classification inventory completed |
| **Task 41** | Technical Documentation Regeneration | Reconciled authoritative architecture, persistence, HUD, and task registers. | Implemented (Task 41) | Documentation validation green |
| **Task 42** | Final Cross-System Verification | End-to-end multi-system integration testing across weapons, FOIMS-X, and save/load. | Pending | Pending |
| **Task 43** | Final Cleanup Gate | Final repository cleanliness audit, baseline verification, and artifact lock. | Pending | Pending |