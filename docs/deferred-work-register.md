# DoDA Weapon System & HUD — Deferred Work Register

## 1. Context and Operating Scope

This document serves as the living register for design choices, visual calibration topics, and presentation enhancements intentionally deferred during the completion of **Task 17: Shared Deadzone-Aware Trace**.

### Key Context:
- **Task 17 Delivered**: Centralized common deadzone-aware hitscan geometry calculation (`FireDeadzoneHitscanRay`) into `DoDAWeapon` (`DoDA/WeaponSystem/WeaponBase.zs`).
- **Preserved Family Behaviors**: B92, MP5, and Shotgun retain their family-specific damage calculations, spread models, pellet counts, sounds, ammunition/chamber consumption, tracer behaviors, and state machines.
- **Validated Baseline**: Direct-workstation smoke testing passed with zero parser errors and clean runtime execution.
- **Preserved Aim Policy**: Task 17 intentionally preserved the established **parallel weapon-origin raycast policy**.
- **Explicit Exclusions**: No HUD, viewport projection, dynamic FOV, resolution-locking, aim-convergence, or dynamic reticle behaviors were implemented or modified in Task 17.
- **Living Document Policy**: This register is for documentation and architectural planning only; it does not authorize code modifications.

---

## 2. Deferred Work Register

| Deferred Item | Why Deferred | Current Observed Behavior / Evidence | Proposed Future Scope / Decision Needed | Dependencies | Explicit Non-Goals | Recommended Validation | Suggested Task Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Camera-ray vs. weapon-origin convergence policy** | Out of scope for Task 17 geometry extraction; requires an intentional product decision regarding aim feel and parallax. | The Task 17 baseline uses parallel weapon-origin rays based on `attackZ` elevation and `leanOffset`. | Determine whether the red X represents camera aim direction or predicted weapon-impact direction. Options include: preserving parallel ray parallax, converging weapon rays at a fixed target distance, or implementing a dynamic impact predictor. | Explicit gameplay/UX product decision. | Do not select an aim policy unilaterally without product approval. | Close-, medium-, and long-range wall and actor hit tests under deadzone aim and lean stances. | Future gameplay / aim-contract decision. |
| **B. Close-range red-X / muzzle-parallax presentation** | Depends directly on the selected camera-ray vs. convergence policy. | Camera eye and weapon barrel origins diverge at close range due to vertical offset ($\approx 5$ map units), creating natural close-range parallax. | Evaluate whether close-range parallax should be cosmetically compensated or retained as realistic firearm geometry. | Resolution of Item A (Convergence Policy). | Do not classify natural physical parallax as a defect until an aim policy is selected. | Controlled close-cover, point-blank, and corner-peeking wall impact tests. | Follow-on presentation behavior. |
| **C. Non-16:9 reticle/impact visual calibration** | Requires dedicated engine-specific viewport and projection investigation; prior speculative 2D formulas did not resolve all aspect ratios. | Red-X reticle to 3D impact alignment varies across non-16:9 aspect ratios and windowed modes. | Investigate native UZDoom 3D viewport projection matrix, FOV scaling (Hor+), and letterboxing bounds to achieve aspect-ratio-independent 2D reticle placement. | Direct manual observation and native viewport/projection investigation. | No forced display resolutions, no generic HUD scaling workarounds, no unsourced FOV formulas. | Fixed wall-target test matrix across 16:9, 16:10, 4:3/5:4, ultrawide, and tall/narrow windowed views. | Future HUD / view-projection investigation. |
| **D. MP5 tracer origin / direction redesign** | Task 17 scope was restricted to hitscan raycast geometry; visual projectile tracer was kept local to preserve existing behavior. | MP5 utilizes a separate visual `DoDATracer` fast-projectile actor (`Speed 120`) alongside its instant hitscan ray. | Determine whether the visual projectile tracer should align with the hitscan ray, weapon muzzle, camera view, or serve as a purely cosmetic trail. | Decision on visual tracer representation model. | Do not conflate visual tracer appearance with hitscan damage and impact correctness. | Comparative logging of tracer origin, `BulletPuff` spawn location, and damage under normal, deadzone, and lean conditions across viewports. | Future visual-tracer task. |
| **E. Dynamic impact-predictor reticle** | Optional advanced feature outside the scope of baseline hitscan refactoring. | No dynamic predictor exists; the red X does not dynamically raycast to predict exact distance-dependent impact points. | Design an optional HUD-side lightweight trace/projection pipeline to place the reticle dynamically at the raycast collision point. | Selected aim policy and availability of a performant, safe HUD-side trace mechanism. | Do not treat dynamic prediction as a required refactor or silently inject auto-aim assistance. | Target-distance variation, moving-target tracking, wall penetration, lean, and performance benchmark tests. | Optional UX / aim-assistance feature. |
| **F. HUD scaling and TAPLINE responsive layout** | UI layout scope is distinct from weapon hitscan and state-machine refactoring. | TAPLINE and Weapon HUD use fixed-pixel layout offsets, occupying disproportionate screen real estate at small window resolutions. | Implement a responsive, resolution-aware HUD layout system that preserves bitmap font legibility without distorting UI elements. | Responsive HUD layout design preserving font clarity. | Do not alter deadzone reticle coordinates or the green-box angular extent via generic HUD scaling. | Readability and layout inspection at 16:9, 4:3/5:4, small windowed, 4K fullscreen, and tall/narrow layouts. | Future responsive-HUD task. |
| **G. Akimbo B92 left-lean companion PSprite overlay visibility** | Out of scope for Wave 3 FOIMS-X and HUD parameter refactoring; pre-existing defect in layer-2 PSprite / lean lowering pipeline. | In dual B92 mode, leaning left (`+user1`) causes the left weapon overlay sprite to disappear, while HUD companion ammo readout remains active. Traced to commit `d57d853`. | Investigate PSprite layer 2 (`PSP_LEFTWEAPON`) state resolution and viewport lowering transforms during active left lean in `WeaponBase.zs` and `AkimboInputHandler.zs`. | Dedicated akimbo weapon system refactoring task. | Do not hack temporary position offsets or bypass PSprite layer management. | Single and dual B92 firing, reload, and switching tests across neutral, left-lean, and right-lean stances. | Future akimbo weapon refactoring task. |

---

## 3. Scope Protection & Governance Rules

1. **Isolation from Task 18 (Weapon Archetype)**:
   - None of the items in this register may be bundled into Task 18. Task 18 is strictly confined to weapon archetype contracts.
2. **No Incidental Code Changes**:
   - These items must not be implemented as opportunistic or incidental cleanup during future B92, MP5, Shotgun, or HUD tasks.
3. **Dedicated Task Lifecycle**:
   - Any future work on these items requires:
     - A dedicated, read-only discovery pass.
     - An explicit task boundary and scope specification.
     - Direct-workstation runtime verification.
     - A dedicated, isolated Git commit.

---

## 4. Known Reference Points

The following production files define the active baseline references for the topics in this register (listed for reference only, without modification):
- **Shared Hitscan Helper**: `DoDA/WeaponSystem/WeaponBase.zs` (`FireDeadzoneHitscanRay`, line 1093).
- **MP5 Tracer Spawning**: `DoDA/WeaponSystem/Weapons/SMGs/MP5KSD.zs` (`SpawnDeadzoneAwareTracer`, line 313).
- **Shotgun Pellet & Rack Pipeline**: `DoDA/WeaponSystem/Weapons/Shotguns/Shotgun.zs` (`A_Shotgun_FireTrace`, line 682).
- **Deadzone Reticle & Box Rendering**: `DoDA/UI/FieldAgent/HUDDeadzone.zs` (`DrawDeadzone`, line 21).
- **TAPLINE Layout & Rendering**: `DoDA/UI/FieldAgent/HUDTapline.zs` (`Draw`, line 23).
- **Weapon HUD Layout & Rendering**: `DoDA/UI/FieldAgent/HUDWeapon.zs` (`Draw`, line 35).
