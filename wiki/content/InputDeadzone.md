# Input and Deadzone

### Confirmed
- `DoDAAimInput`: Thin input handler (`RequireMouse = true`, `SetOrder(-100)`). Captures raw mouse deltas into `doda_raw_mouse_x`/`y` CVars when `FieldAgent.IsDeadzoneAimActive()` is true.
- `FieldAgent`: Consumes raw mouse input CVars, applies smoothing, enforces `DeadzoneYawLimit`/`DeadzonePitchLimit`, and maintains `ReticleYawOffset`/`ReticlePitchOffset`.
- `DoDAHUDDeadzone` / `DoDAHUDDeadzoneBridge`: Read-only HUD components intended to display deadzone reticle overlay.
- `DoDADeadzoneController`: **LEGACY / ORPHAN**. Not included in `zscript.txt`.

### Investigation
- HUDDeadzone Rendering Failure: `DoDAHUDDeadzone` currently fails to draw overlay elements to the screen when Deadzone Aim mode is active. Diagnosis is underway.
- Camera Locking: Camera remains active during Deadzone Aim mode; locking camera view until the reticle reaches angular boundaries is under investigation.
- No engine-level C++ deadzone implementation exists or is currently approved.

### Open decision
- Orphaned Code: Disposition of `DoDA/Aim/DeadzoneController.zs` (archival vs deletion).
