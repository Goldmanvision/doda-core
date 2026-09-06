# Active Load Graph

### Confirmed Active Regions
The project load graph is defined in the root `zscript.txt`. The following regions are currently active in the translation unit:
- `NativeBridge` (`DoDA/Native/DoDA.zs`)
- `Aim` (`DoDA/Aim/AimInput.zs`)
- `CharacterClasses` (`DoDA/CharacterClasses/FieldAgent.zs`, `Analyst.zs`, `SAC.zs`)
- `UserInterface` (`DoDA/UI/FieldAgent/HUDTapline.zs`, `DoDA/UI/FieldAgent/HUDDeadzone.zs`, `DoDA/UI/FieldAgent/HUDWeapon.zs`, `DoDA/UI/FieldAgent/HUDWeaponBridge.zs`, `DoDA/UI/FieldAgent/HUDDeadzoneBridge.zs`, `DoDA/UI/FieldAgent/HUD.zs`)
- `Abilities` (`DoDA/Abilities/Lean/LeanInput.zs`, `LeanController.zs`)
- `WeaponSystem` (`DoDA/WeaponSystem/HandSwapController.zs`, `SpriteAnimator.zs`, `WeaponBase.zs`, `Casing.zs`, `Tracer.zs`, `Weapons/`, `Ammo/AmmoDispenser.zs`)
- `Range` (`DoDA/Range/Map03RangeStartHandler.zs`)
- `MissionSystem` (`DoDA/MissionSystem/MissionIds.zs`, `ObjectiveIds.zs`, `MissionDefs.zs`, `MissionState.zs`, `CampaignState.zs`, `Evidence/EvidenceLedger.zs`, `LastMissionReport.zs`, `MissionManager.zs`, `MissionDirector.zs`, `DebugTrigger.zs`)
- `MissionSystem-Things` (`DoDA/MissionSystem/Things/MissionPickupMarkers.zs`, `ObjectivePickup.zs`, `MissionPickup.zs`, `MissionInteractable.zs`, `MissionTerminal.zs`, `ExtractionInteractable.zs`, `DeployMissionInteractable.zs`)

Only these regions and their included files are part of the active translation unit.

### Confirmed Inert Components (Intentionally Un-Included)
The following presentation files are committed to disk under `DoDA/UI/FOIMSX/PersonnelV1/` but are intentionally un-included in `zscript.txt` and unregistered in `MAPINFO` to preserve zero-runtime-impact isolation:
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Model.zs`
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Adapter.zs`
- `DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1ViewState.zs`

### Confirmed Legacy / Orphan
- `DoDA/Aim/DeadzoneController.zs`: Not included in `zscript.txt`; orphaned historical component.

### Resolved Decisions
- **Production Native Binding Bridge**: `struct DoDA native` is permanently declared in `DoDA/Native/DoDA.zs` and integrated into the active load graph via `#region NativeBridge` in `zscript.txt`.
