# MP5KSD

## State Fields
- `MagazineCapacity`: 30
- `TotalCapacity`: 31
- `magazineRounds`, `chamberLoaded`
- `fireMode`: 0 (Semi), 1 (Burst), 2 (Auto)
- `burstShotsRemaining`, `burstInProgress`

## Fire Dispatch
- Semi: `Fire` state triggers `MP5KSD_Fire`.
- Burst: `BurstFire` state triggers `MP5KSD_BurstFire` 3 times.
- Auto: `Fire` state triggers `MP5KSD_Fire` while holding fire.

## Reload
- `TryReload()` initiates tactical or empty reload based on `IsEmpty()`.
- `PerformReloadTransfer()` transfers ammo from reserve.
- `LoadChamberFromMagazine()` chambers a round during reload.

## MP5ModeHandler
- `InputProcess()` captures 'C' to cycle fire modes and 'R' to reload.
- `NetworkProcess()` handles network events `DoDA_MP5CycleFireMode` and `DoDA_MP5Reload`.
- *Note: Not registered as a UI processor.*
