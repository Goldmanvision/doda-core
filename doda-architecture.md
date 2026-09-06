
# DoDA Working Architecture & Design Reference

## Status Summary

### Confirmed
- `FieldAgent` is the active ZScript authority for Deadzone Aim mode, angular offsets, smoothing, and limits.
- `DoDALeanInput` and `DoDALeanController` own lean input reading and view translation math.
- `DoDAWeapon` currently drives the update lifecycle for `DoDALeanInput` and `DoDALeanController`.
- Native strategic simulation in UZDoom C++ fork owns canonical persistent state; Personnel Snapshot V1 is read-only (Native API v1, Save schema v2).

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