# DoDA Wiki Reconciliation Report - 2026-08-17

## Local Revision Context
Audit conducted on 2026-08-17. Sole source of truth is the active filesystem at `gzdoda/doda-core/`.

## Files and Directories Inspected
- `zscript.txt` (Root translation unit)
- `MAPINFO`
- `DoDA/Aim/`
- `DoDA/CharacterClasses/`
- `DoDA/Abilities/`
- `DoDA/WeaponSystem/`
- `wiki/` (including content/ and generated HTML files)

## Active Load Graph
- `zscript.txt` includes:
  - Aim (AimInput.zs)
  - CharacterClasses (FieldAgent, Analyst, SAC)
  - UserInterface (HUD modules)
  - Abilities (LeanInput, LeanController)
  - WeaponSystem (HandSwapController, SpriteAnimator, WeaponBase, etc.)
  - Range (Map03RangeStartHandler)
  - MissionSystem (including EvidenceLedger)

## Documentation Claim Matrix
| Feature | Claim Status | Evidence |
| :--- | :--- | :--- |
| `DoDADeadzoneController` | Legacy | Not included in `zscript.txt` |
| `FieldAgent` deadzone | Source-confirmed | `FieldAgent.zs` (Tick, ResetDeadzoneAim) |
| `LeanInput` / `LeanController` | Source-confirmed | `zscript.txt` inclusions |
| MP5 firing/burst | Source-confirmed | `MP5KSD.zs`, `MP5ModeHandler.zs` |

## Confirmed Active Architecture
- `FieldAgent` owns deadzone state, yaw/pitch offsets, smoothing, and limits.
- `AimInput` is a thin handler for raw mouse capture.
- `LeanInput` and `LeanController` are loaded and active.

## Contradicted or Stale Documentation
- Wiki mentions `DoDADeadzoneController` as active. It is NOT loaded in `zscript.txt`.

## Missing-source or Unverified References
- EvidenceLedger: Class exists in `DoDA/MissionSystem/Evidence/EvidenceLedger.zs`.

## Planned-design items incorrectly documented as implemented
- None identified yet; need further review of `WIP.md`.

## Current Bug-Status Documentation
- MP5 deadzone-crosshair shot alignment: Confirmed defect.
- B92 firing during Deadzone Aim: Under focused investigation.
- MAP03 console loading: Investigation underway.

## Recommended Wiki Information Architecture
- `index.html`: Keep as entry.
- `wiki/content/`: Use for source-confirmed markdown.
- `wiki/`: Retain legacy/HTML for reference but clearly mark as such.

## Documentation Maintenance Rules
1. Every tech page must contain a status badge.
2. Only source-confirmed info goes to `content/` MD files.
3. Legacy documentation to be clearly labeled.
