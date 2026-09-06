# Weapon Architecture

### Confirmed
The DoDA weapon system is based on `DoDAWeapon`, extending `Weapon`:
- Core State: Owns weapon presentation state, FOV management, fire-control locks (`fireLockTics`), and procedural angular offsets (`yawGap`, `pitchGap`).
- Auxiliary Drivers: Currently instantiates and drives `DoDALeanInput`, `DoDALeanController`, `DoDAHandSwapController`, and `DoDASpriteAnimator`.
- Deadzone Integration: Reads `FieldAgent` deadzone offsets for sprite procedural sway and firing trace adjustment.
- Manual Dispatch: `UsesManualFireDispatch()` and `GetFireState()` support burst firing and mode selection.

### Planned
- Lean Lifecycle Extraction: Extracting `DoDALeanInput` and `DoDALeanController` lifecycle execution from `DoDAWeapon` into an independent player/ability system.

### Investigation
- HUDDeadzone Rendering: Investigating why `DoDAHUDDeadzone` fails to draw screen overlays during active Deadzone Aim.
- Trajectory Alignment: Resolving MP5KSD center-screen trace discrepancy (`A_FireBullets` vs reticle offset).
