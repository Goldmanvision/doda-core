# Test and Debugging Guide

## Test Matrix
- B92 normal fire, deadzone fire, empty/reload behavior.
- MP5 semi, burst (partial magazine), automatic fire.
- MP5 tactical reload, empty reload/cocking, dry fire.
- MP5 deadzone crosshair alignment (WIP / unverified).

## Diagnostic Markers
- `[DEBUG/RELOAD]`: `PistolBase.CanReload`, `QueueReload`, `DoDA_BeginReload`, `DoDA_CommitReload`.
- `[DODA/WEAPON]`: `PistolBase.CommitReload`.
- `HANDSWAP`: `PistolBase.RequestHandSwap`.
- `MP5`: `MP5KSD` fire modes, burst, reload, chamber loading, shot traces.
- `SPRITE`: `WeaponBase.PrintDebugSpriteOffsets`.
