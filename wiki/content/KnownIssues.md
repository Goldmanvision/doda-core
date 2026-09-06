# Known Issues

### Confirmed Defects
- MP5 Deadzone Trajectory Alignment: `DoDAMP5KSD` uses `A_FireBullets` directly, causing bullets to fire from screen center and ignoring `FieldAgent` deadzone crosshair angular offsets.

### Planned Work
- Lean Lifecycle Extraction: Migrating `DoDALeanInput` and `DoDALeanController` update execution out of `DoDAWeapon` into a player-owned ability lifecycle.

### Active Investigations
- HUDDeadzone Screen Drawing: Diagnosing why `DoDAHUDDeadzone` fails to render overlay graphics to the screen during active Deadzone Aim.
- Deadzone Camera Locking: Investigating camera-lock mechanics during Deadzone Aim until reticle reaches angular boundaries.
- B92 Deadzone Firing: Investigating `PistolBase.ShouldStartFire` override behavior when Deadzone Aim mode is active.
- MAP03 Console Loading: Investigating MAPINFO registration and WAD packaging markers for MAP03 access.

### Open Decisions
- Configuration Lump Organization: Standardizing and cleaning up `CVARINFO`, `KEYCONF`, and `MENUDEFS`.
- Orphaned Code Disposition: Resolving final status of `DoDA/Aim/DeadzoneController.zs` (archival vs deletion).

### Resolved Decisions
- Production Native Binding Placement: Resolved. `struct DoDA native` is permanently placed in `DoDA/Native/DoDA.zs` and loaded via `#region NativeBridge` in `zscript.txt`.
- Personnel Diagnostics Contract: Resolved. Verified existing 12 native methods satisfy adapter validation and state needs.
