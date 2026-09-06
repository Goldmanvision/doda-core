# Lean Ability

### Confirmed
The lean ability allows for tactical lateral view translation and is composed of two primary ZScript classes:

## Component Ownership
- `DoDALeanInput`: Reads lean button inputs (`BT_USER1` for Q, `BT_USER2` for E) and performs edge-trigger detection (`LeaningLeftPressed`, `LeaningRightPressed`).
- `DoDALeanController`: Manages lean smoothing (0.25), distance adjustment [8.0, 40.0] via `BT_USER4`, `owner.SetViewPos` lateral view translation, `IsLeanLocked()`, and hand restriction (`GetLockedHand()`).
- `DoDAWeapon`: Currently owns and drives the update lifecycle for `DoDALeanInput` and `DoDALeanController`.

### Planned
- Lean Lifecycle Extraction: Migration of `DoDALeanInput` and `DoDALeanController` update execution out of `DoDAWeapon` into a player-owned ability lifecycle under `DoDA/Abilities/Lean/` is planned. The extraction is not yet implemented.
