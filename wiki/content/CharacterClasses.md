# Character Classes

### Confirmed
DoDA features three playable character classes inheriting from `DoomPlayer`: `FieldAgent`, `Analyst`, and `SAC`.

## Deadzone Aim Ownership (FieldAgent)
`FieldAgent` is the active ZScript authority for deadzone aim state and calculations:
- `DeadzoneAimActive`: Tracks if deadzone aim mode is currently active.
- `ReticleYawOffset` / `ReticlePitchOffset`: Signed angular offset between actor aim and red-dot aim.
- `DeadzoneYawLimit` / `DeadzonePitchLimit`: Angular constraints on reticle movement.
- `SmoothedMouseX` / `SmoothedMouseY`: Smoothed per-tick mouse input for trackball-like inertia.
- `ResetDeadzoneAim()`: Resets all deadzone state variables and clears raw mouse CVars.
- `Tick()`: Manages deadzone activation via `BT_ALTATTACK` (alt-fire), lean keys (`BT_USER1`, `BT_USER2`), or debug CVars.

## Starting Inventory
- `FieldAgent`: Starts with `DoDAB92Left`, `DoDAB92Right`, `DoDAMP5KSD`, `DoDAHolster`, `Clip` (100).
- `Analyst`: Starts with `Clip` (100).
- `SAC`: Starts with `DoDAB92Left`, `DoDAB92Right`, `Clip` (100).

### Investigation
- Camera Lock: The current implementation moves the weapon sprite with mouse movement, but the camera is still active. Camera locking until reticle reaches bounding box limits is an active investigation.
- No C++ engine deadzone implementation is approved or implemented.
