# DoDA Codebase Audit 2026-08-17

## 1. Audit scope and local revision context
- Project: DoDA GZDoom mod (unpacked `doda-core`)
- Date: 2026-08-17
- Scope: Read-only triage of MP5/B92 firing issues and MAP03 loading; architecture mapping.
- Authority: Local filesystem is the sole source of truth.

## 2. Files/directories inspected
- `zscript.txt` (Load order)
- `MAPINFO` (Map definitions)
- `maps/` (Map files)
- `DoDA/WeaponSystem/Weapons/SMGs/MP5KSD.zs`
- `DoDA/WeaponSystem/Weapons/Pistols/PistolBase.zs`
- `DoDA/WeaponSystem/Weapons/Pistols/B92Left.zs`
- `console_log.txt`

## 3. Executive findings
- The project has a clear ZScript module structure, but several weapon firing systems are independently implementing trace logic, leading to inconsistencies with the central Deadzone Aim system.
- MAP03 packaging/metadata is misaligned with the GZDoom map-loading system.

## 4. Immediate triage findings

### MP5 deadzone trajectory
- **Severity**: High
- **Confidence**: Confirmed
- **Evidence**: `DoDA/WeaponSystem/Weapons/SMGs/MP5KSD.zs` line 356: `A_FireBullets(0, 0, 1, 10, "BulletPuff", FBF_NORANDOM);`
- **Why it matters**: `A_FireBullets` fires directly from the player's center view, ignoring the Deadzone Aim crosshair offset.
- **Remediation**: Replace `A_FireBullets` with a custom projectile or adjust the fire vector to include the deadzone crosshair offset.
- **Validation**: Compare trace impact with deadzone aim active vs inactive.

### B92 firing in Deadzone Aim
- **Severity**: High
- **Confidence**: Likely
- **Evidence**: `DoDA/WeaponSystem/Weapons/Pistols/PistolBase.zs` lines 30-33: `override bool ShouldStartFire(...) { return false; }`
- **Why it matters**: The pistol base class explicitly disables firing, and it is not clearly overridden by `B92Left`/`B92Right` in a way that respects Deadzone Aim state.
- **Remediation**: Allow `ShouldStartFire` to return `true` if the weapon is ready and Deadzone Aim is either inactive or properly integrated.
- **Validation**: Check if `ShouldStartFire` is called during firing attempts in Deadzone Aim mode.

### MAP03 console loading
- **Severity**: Medium
- **Confidence**: Likely
- **Evidence**: `console_log.txt` shows `No map file:MAP03` while `MAP03.wad` exists in `maps/`.
- **Why it matters**: Map is inaccessible via console.
- **Remediation**: Verify WAD map marker naming (should be `MAP03`) or ensure the `maps/` folder is included in the PK3/load path correctly.
- **Validation**: `open MAP03` in console.

## 5. Architecture map
- `zscript.txt`: Root of all includes.
- `DoDA/Aim/AimInput.zs`: Raw input capture.
- `DoDA/CharacterClasses/FieldAgent.zs`: Deadzone state controller.
- `DoDA/WeaponSystem/WeaponBase.zs`: Weapon pipeline.
- `DoDA/WeaponSystem/Weapons/`: Individual weapon state machines.
- `maps/`: Contains maps (MAP01-MAP03).

## 6. Confirmed defects
- `A_FireBullets` usage in `MP5KSD` ignores deadzone offset.
- `PistolBase` explicitly disables firing in `ShouldStartFire`.

## 7. Likely defects requiring one gameplay test
- MAP03 WAD map marker naming mismatch.

## 8. Dead-code and redundancy candidates
- Unused/Orphaned code in `DoDA/Aim/DeadzoneController.zs` (if not referenced by current `zscript.txt`).

## 9. Documentation and wiki findings
- The current `wiki/` directory content is stale and mostly outdated.
- Documentation needs to be rebuilt based on current active source.

## 10. Recommended task backlog
1. Resolve MP5 `A_FireBullets` logic to account for deadzone aim.
2. Investigate/fix B92 `ShouldStartFire` override.
3. Validate/fix MAP03 WAD packaging.
4. Clean up legacy/unreferenced files (needs audit).

## Do not change yet
- Do not modify `WeaponBase` wholesale.
- Do not add `IsUiProcessor = true` to non-UI handlers.

## Wiki-update plan
- Create `wiki/content/MP5_Firing_Logic.md`.
- Create `wiki/content/Deadzone_Aim_Integration.md`.
