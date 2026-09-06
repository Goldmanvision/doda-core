# B92 Pistols

## Overview
The B92 pistols (`DoDAB92Left`, `DoDAB92Right`) are gameplay-distinct weapons, each with an independent magazine and chamber state.

## State Management
- `magazineRounds`: Current rounds in the magazine.
- `chamberLoaded`: Whether a round is chambered.
- `firearmStateInitialized`: Tracks if the state has been initialized.

## Reload Behavior
- `CanReload()`: Allows reloading if reserve ammo (`Clip`) is available and the magazine is not full.
- `CommitReload()`: Returns unused magazine rounds to reserve, loads a new magazine, and chambers a round if empty.
- `QueueReload()`: Flags a reload request.
- `DoDA_BeginReload()`: Validates the request before starting the animation.
- `DoDA_CommitReload()`: Performs the `CommitReload()` call.

## Hand Swap
- `RequestHandSwap()`: Switches between left and right hands.
- `HandSwapController` lock state (`IsPistolSwapLocked()`) restricts swaps if active.
