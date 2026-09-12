# DoDA Unified Input Ownership Map

## 1. Overview & Architecture

The DoDA input subsystem coordinates player controls across multiple layers: native engine input capture, UI input events, command buttons, networked console events, player pawn ticking, and weapon state machines.

This document establishes the explicit single owner for each input responsibility to prevent overlapping consumption, race conditions, binding conflicts, and ambiguous input flows.

---

## 2. Input Subsystem Ownership Registry

| Input Responsibility | Primary Owner Class | Input Channel / Trigger | Consumption / Write Target | Lifecycle / Runtime Status |
| :--- | :--- | :--- | :--- | :--- |
| **Raw Mouse Capture** | `DoDAAimInput` | `UIProcess(UiEvent e)` with `Type_MouseMove` | `doda_raw_mouse_x`, `doda_raw_mouse_y` via `DoDAInputUtility` | **Production** (`StaticEventHandler`) |
| **Deadzone Buffer Consumption** | `DoDAPlayerBase` | Player `Tick()` / movement loop | Consumes & clears `doda_raw_mouse_x/y` via `DoDAInputUtility` | **Production** (Player base class) |
| **Deadzone Aim Activation Policy** | `FieldAgent` (overriding `DoDAPlayerBase`) | `BT_ALTATTACK` (Mouse2), `doda_debug_force_deadzone`, or active Lean | Sets `DeadzoneAimActive` | **Production** (Player character class) |
| **Lean Button Edge Detection** | `DoDALeanInput` | Polled in `FieldAgent.Tick()` via `player.cmd.buttons` (`BT_USER1`, `BT_USER2`, `BT_USER4`) | Updates `LeaningLeft`, `LeaningRight`, `ScrollDown` state | **Production** (`Object` component owned by `FieldAgent`) |
| **Lean Offset & Viewport Smoothing** | `DoDALeanController` | Polled in `FieldAgent.Tick()` from `DoDALeanInput` flags | Applies smoothed `SetViewPos()` viewport offset and sets `FieldAgent.LeanOffset` | **Production** (`Object` component owned by `FieldAgent`) |
| **Akimbo Mode Toggle** | `DoDAAkimboInputHandler` | `NetworkProcess(ConsoleEvent e)` via netevent `DoDA_ToggleAkimbo` | Invokes `DoDA.EnterAkimbo()` / `DoDA.ExitAkimbo()`, updates PSprite layers | **Production** (`StaticEventHandler`) |
| **Hand Swap / Firemode Toggle** | Weapon State Machines (`PistolBase`, `MP5ModeHandler`, `MP5KSD`) | `BT_USER3` (`+user3` / `+doda_firemode`) or weapon secondary input | State jumps (`CheckHandSwap()`, `DoDA_FiremodeMP5`) | **Production** (Weapons & EventHandlers) |
| **FOIMS-X Terminal Interaction** | `DoDAMissionTerminal` / `DoDAMissionDirector` | `+use` / activation trigger on world thing | Opens terminal / lifecycle event | **Production** (World Things / UI) |
| **FOIMS-X UI Navigation** | FOIMS-X ViewStates (`PersonnelSnapshotV1ViewState`, `AssignmentSnapshotV1ViewState`) | UI Event routing / programmatic selection | ViewState selection index | **Production** (UI Models / ViewStates) |
| **Global Raw Key Diagnostics** | `DODAGlobalInputCapture` | `InputProcess(InputEvent e)` | Console debug logging | **Diagnostic / Inert** (Debug handler; not registered in MAPINFO) |
| **Background Sim POC Ticking** | `DoDABackgroundSimPOC` | Map / world ticks | Background simulation step | **POC / Simulation** (`StaticEventHandler`) |

---

## 3. Input Channels & Binding Specifications

### 3.1 Direct Command Buttons (`player.cmd.buttons`)
- `+attack` (`BT_ATTACK`): Primary weapon fire. Handled directly by weapon state machines (`A_WeaponReady`, `A_GunFlash`).
- `+altattack` (`BT_ALTATTACK`): Aim mode / Deadzone activation trigger in single-weapon mode. When Akimbo is active without leaning, `BT_ALTATTACK` is processed as secondary weapon fire.
- `+user1` (`BT_USER1`): Left Lean. Bound to `q` by default in KEYCONF. Consumed by `DoDALeanInput`.
- `+user2` (`BT_USER2`): Right Lean. Bound to `e` by default in KEYCONF. Consumed by `DoDALeanInput`.
- `+user3` (`BT_USER3`): Weapon firemode toggle / burst mode. Bound via `+doda_firemode` alias in KEYCONF.
- `+user4` (`BT_USER4`): Lean distance decrease step. Consumed by `DoDALeanInput`.
- `+reload` (`BT_RELOAD`): Weapon reload sequence. Handled by weapon state machines.
- `+use` (`BT_USE`): World interaction (doors, mission interactables, terminals).

### 3.2 UI & Raw Mouse Events (`UiEvent`)
- Captured exclusively by `DoDAAimInput.UIProcess(UiEvent e)`.
- Filters for `e.Type == UIInputEvent.Type_MouseMove`.
- Mouse delta accumulation writes directly to `doda_raw_mouse_x` and `doda_raw_mouse_y` using `DoDAInputUtility.ReadFloatSetting` and `DoDAInputUtility.SafeWriteFloat`.
- No other event handler or UI widget may capture or modify raw mouse position buffers.

### 3.3 Network Console Events (`ConsoleEvent` / `netevent`)
- Captured by `DoDAAkimboInputHandler.NetworkProcess(ConsoleEvent e)`.
  - `DoDA_ToggleAkimbo`: Toggles akimbo state for dual B92 pistols.
  - `DoDA_ToggleDualWield`: Reserved / stubbed netevent for future dual-wield expansion.

---

## 4. CVar Communication Contracts

All CVar reads and buffer drains must use `DoDAInputUtility` methods:

1. **`doda_raw_mouse_x` / `doda_raw_mouse_y`** (User float):
   - **Writer**: `DoDAAimInput` (accumulates delta per UI event).
   - **Reader & Drainer**: `DoDAPlayerBase` (drains and zeroes buffer each `Tick()`).
   - **Reset**: `DoDAPlayerBase.ResetDeadzoneAim()`.

2. **`doda_aim_sensitivity`** (User float, default 0.20):
   - **Writer**: Menu / Console user setting.
   - **Reader**: `DoDAPlayerBase` (scales mouse delta input).

3. **`doda_debug_force_deadzone`** (User bool, default false):
   - **Writer**: Developer console command.
   - **Reader**: `DoDAPlayerBase.ShouldActivateDeadzoneAim()`, `FieldAgent.ShouldActivateDeadzoneAim()`.

4. **`doda_swap_beretta` / `doda_weapon_secondary` / `doda_toggle_pistol_swap_lock`**:
   - Weapon-specific input state CVars mapped to key aliases in KEYCONF.

---

## 5. Input Collision & Defect Catalog

1. **Key `v` Dual-Binding**:
   - In baseline `KEYCONF`, key `v` is bound to both `+doda_swapberetta` and `+doda_weaponsecondary`.
   - *Status*: Cataloged baseline defect. Preservation required until dedicated binding refactor task.
2. **Key `c` Dual-Binding**:
   - In baseline `KEYCONF`, key `c` is bound to both `+doda_toggle_pistol_swap_lock` and `+doda_firemode`.
   - *Status*: Cataloged baseline defect. Preservation required until dedicated binding refactor task.
3. **Scan-Code Constants**:
   - Inspection confirms all production input flows rely on engine button masks (`BT_*`), `UiEvent.Type_MouseMove`, or `ConsoleEvent.Name`.
   - Hardcoded keyboard scan codes are present only in inert diagnostic capture (`DODAGlobalInputCapture`), which is unreferenced in `MAPINFO`.
   - Therefore, introducing global scan-code constants into production code is unnecessary and omitted to maintain zero unnecessary code footprint.
