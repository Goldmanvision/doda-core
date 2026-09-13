///////////////////////////
// DoDA/WeaponSystem/WeaponBase.zs
///////////////////////////

enum EDoDAWeaponArchetype
{
    ARCHETYPE_Default,
    ARCHETYPE_Pistol,
    ARCHETYPE_SMG,
    ARCHETYPE_Shotgun
};

class DoDAWeapon : Weapon
{
    double yawGap;
    double pitchGap;

    double normalFOV;
    double zoomedFOV;
    double crouchZoomBonus;

    double hipfireSpread;
    double deadzoneSpread;
    double offhandSpreadMult;

    int fireLockTics;
    int leftFireLockTics;
    int rightFireLockTics;
    double currentRightLowerY;
    double currentLeftLowerY;
    bool wasAkimboActive;
    bool wasSwapBerettaHeld;
    bool wasAkimboToggleHeld;
    bool wasWeaponSecondaryHeld;
    bool wasDeadzoneAimActive;
    bool wasHoldingFire;
    bool wasHoldingAlt;
    bool wasReloadHeld;
    bool wasPistolSwapLockHeld;
    bool initialized;

    DoDALeanInput leanInput;
    DoDALeanController leanController;
    DoDAHandSwapController handSwapController;
    DoDASpriteAnimator spriteAnimator;

    double debugSpriteX;
    double debugSpriteY;
    double debugSpriteRot;
    double debugSpriteScale;
    bool lastDebugPrintToggleState;

    bool pipelineInitialized;
    Weapon lastLoggedReadyWeapon;
    Weapon lastLoggedPendingWeapon;
    State lastLoggedWeaponState;
    bool lastLoggedReadyWasSelf;
    bool lastLoggedAttackDown;
    int lastLoggedRequestedHand;
    int lastLoggedActualHand;

    const Hand_Left = 0;
    const Hand_Right = 1;

    Default
    {
        +WEAPON.NOAUTOAIM;
    }

    virtual void HandleManualWeaponControl()
    {
    }

    virtual void HandleSecondaryWeaponAction()
    {
    }

    virtual void HandleDeadzoneAimActivated()
    {
    }

    virtual bool ShouldStartFire(bool holdingFire, bool firePressed)
    {
        return firePressed;
    }

    virtual bool UsesManualFireDispatch()
    {
        return false;
    }

    virtual State GetFireState(bool holdingFire, bool firePressed)
    {
        if (firePressed)
        {
            return ResolveState("Fire");
        }

        return null;
    }

    void PrintDebugSpriteOffsets(int hand)
    {
        Console.Printf(
            "SPRITE x=%.2f y=%.2f rot=%.2f | dbgX=%.2f dbgY=%.2f dbgRot=%.2f scale=%.3f | hand=%d",
            spriteAnimator.GetFinalX(),
            spriteAnimator.GetFinalY(),
            spriteAnimator.GetFinalRotation(),
            debugSpriteX,
            debugSpriteY,
            debugSpriteRot,
            debugSpriteScale,
            hand
        );
    }

    String DescribeWeapon(Weapon weapon)
    {
        if (weapon == WP_NOCHANGE)
        {
            return "WP_NOCHANGE";
        }

        if (weapon == null)
        {
            return "null";
        }

        return weapon.GetClassName();
    }

    String DescribeWeaponState(PSprite weaponSprite)
    {
        if (weaponSprite == null)
        {
            return "no-psprite";
        }

        if (weaponSprite.CurState == null)
        {
            return "null-state";
        }

        if (weaponSprite.CurState == ResolveState("Ready"))
        {
            return "Ready";
        }

        if (weaponSprite.CurState == ResolveState("AltFire"))
        {
            return "AltFire";
        }

        if (weaponSprite.CurState == ResolveState("Reload"))
        {
            return "Reload";
        }

        if (weaponSprite.CurState == ResolveState("Deselect"))
        {
            return "Deselect";
        }

        if (weaponSprite.CurState == ResolveState("Select"))
        {
            return "Select";
        }

        if (weaponSprite.CurState.InStateSequence(ResolveState("Fire")))
        {
            return "Fire";
        }

        return "other-state";
    }

    void PrintWeaponPipeline(
        Weapon readyWeapon,
        Weapon pendingWeapon,
        PSprite weaponSprite,
        bool readyWasSelf,
        bool attackDown,
        bool attackPressed,
        int actualHand,
        int requestedHand,
        bool requestGate,
        bool swapLock
    )
    {
    }

    void RequestLowestLoadedPistolReload(
        DoDAPistol activePistol
    )
    {
        if (
            owner == null
            || owner.player == null
            || activePistol == null
            || owner.player.PendingWeapon != WP_NOCHANGE
        )
        {
            return;
        }

        let playerBase = DoDAPlayerBase(owner);
        let handState = playerBase ? playerBase.GetHandState() : null;

        let leftPistol = handState
            ? handState.GetLeftPistol(owner)
            : DoDAPistol(owner.FindInventory('DoDAB92Left'));

        let rightPistol = handState
            ? handState.GetRightPistol(owner)
            : DoDAPistol(owner.FindInventory('DoDAB92Right'));

        bool leftCanReload = leftPistol != null
            && leftPistol.CanReload();

        bool rightCanReload = rightPistol != null
            && rightPistol.CanReload();

        if (!leftCanReload && !rightCanReload)
        {
            return;
        }

        DoDAPistol reloadTarget = null;

        if (leftCanReload && !rightCanReload)
        {
            reloadTarget = leftPistol;
        }
        else if (rightCanReload && !leftCanReload)
        {
            reloadTarget = rightPistol;
        }
        else if (
            leftPistol.GetLoadedRoundCount()
            < rightPistol.GetLoadedRoundCount()
        )
        {
            reloadTarget = leftPistol;
        }
        else if (
            rightPistol.GetLoadedRoundCount()
            < leftPistol.GetLoadedRoundCount()
        )
        {
            reloadTarget = rightPistol;
        }
        else
        {
            reloadTarget = activePistol;
        }

        if (reloadTarget == null)
        {
            return;
        }

        reloadTarget.QueueReload();

        if (reloadTarget == activePistol)
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("Reload")
            );
        }
        else
        {
            owner.player.PendingWeapon = reloadTarget;
        }
    }

    override void Tick()
    {
        Super.Tick();

        if (!owner || !owner.player)
        {
            return;
        }

        let pawn = PlayerPawn(owner);

        if (pawn == null || pawn.health <= 0)
        {
            return;
        }

        if (leanInput == null)
        {
            leanInput = new("DoDALeanInput");
        }

        if (leanController == null)
        {
            leanController = new("DoDALeanController");
            leanController.Reset();
        }

        if (handSwapController == null)
        {
            handSwapController = new("DoDAHandSwapController");
        }

        if (spriteAnimator == null)
        {
            spriteAnimator = new("DoDASpriteAnimator");
        }

        normalFOV = 90.0;
        zoomedFOV = 65.0;
        crouchZoomBonus = 8.0;

        hipfireSpread = 6.0;
        deadzoneSpread = 0.0;
        offhandSpreadMult = 3.5;

        double fovSmoothing = 0.15;

        let agent = FieldAgent(owner);

        bool deadzoneActive = agent != null
            && agent.IsDeadzoneAimActive();

        bool deadzoneAimJustActivated =
            deadzoneActive && !wasDeadzoneAimActive;

        wasDeadzoneAimActive = deadzoneActive;

        yawGap = agent ? agent.GetDeadzoneYawGap() : 0.0;
        pitchGap = agent ? agent.GetDeadzonePitchGap() : 0.0;

        double yawLimit = agent
            ? agent.GetDeadzoneYawLimit()
            : 12.0;

        leanInput.Update(pawn);

        bool leaningLeft = leanInput.IsLeaningLeft();
        bool leaningRight = leanInput.IsLeaningRight();
        bool isLeaning = leanInput.IsLeaning();

        leanController.Update(
            pawn,
            leaningLeft,
            leaningRight,
            leanInput.IsScrollUp(),
            leanInput.IsScrollDown()
        );

        double crouchAmount = 1.0 - owner.player.crouchFactor;
        double effectiveZoomFOV = zoomedFOV
            - crouchZoomBonus * crouchAmount;

        if (!initialized)
        {
            owner.player.DesiredFOV = normalFOV;
            owner.player.SetFOV(normalFOV);
            initialized = true;
        }

        double targetFOV = deadzoneActive
            ? effectiveZoomFOV
            : normalFOV;

        double newFOV = owner.player.FOV
            + (targetFOV - owner.player.FOV) * fovSmoothing;

        owner.player.DesiredFOV = targetFOV;
        owner.player.SetFOV(newFOV);

        if (fireLockTics > 0)
        {
            fireLockTics--;
        }
        if (leftFireLockTics > 0)
        {
            leftFireLockTics--;
        }
        if (rightFireLockTics > 0)
        {
            rightFireLockTics--;
        }

        bool attackDown = (owner.player.cmd.buttons & BT_ATTACK) != 0;
        bool attackPressed = attackDown && !wasHoldingFire;
        wasHoldingFire = attackDown;

        bool reloadDown = (owner.player.cmd.buttons & BT_RELOAD) != 0;
        bool reloadPressed = reloadDown && !wasReloadHeld;
        wasReloadHeld = reloadDown;

        Weapon readyWeapon = owner.player.ReadyWeapon;
        Weapon pendingWeapon = owner.player.PendingWeapon;
        PSprite weaponSprite = owner.player.GetPSprite(PSP_WEAPON);

        let pistol = DoDAPistol(readyWeapon);

        int actualHand = Hand_Right;

        if (pistol != null)
        {
            actualHand = pistol.GetWeaponHand();
        }

        handSwapController.SetCurrentHand(actualHand);

        bool leanLocked = leanController.IsLeanLocked();

        int requestedHand = handSwapController.ResolveDesiredHand(
            deadzoneActive,
            yawGap,
            yawLimit,
            leanInput.WasLeaningLeftPressed(),
            leanInput.WasLeaningRightPressed(),
            isLeaning,
            false,
            leanLocked,
            leanController.GetLockedHand()
        );

        CVar swapBerettaCVar = CVar.GetCVar(
            'doda_swap_beretta',
            owner.player
        );

        bool swapBerettaDown = swapBerettaCVar
            ? swapBerettaCVar.GetBool()
            : false;

        bool swapBerettaPressed =
            swapBerettaDown && !wasSwapBerettaHeld;

        wasSwapBerettaHeld = swapBerettaDown;

        bool readyWasSelf = readyWeapon == self;

        CVar pistolSwapLockCVar = CVar.GetCVar(
            'doda_toggle_pistol_swap_lock',
            owner.player
        );

        bool pistolSwapLockDown = pistolSwapLockCVar
            ? pistolSwapLockCVar.GetBool()
            : false;

        bool pistolSwapLockPressed =
            pistolSwapLockDown && !wasPistolSwapLockHeld;

        wasPistolSwapLockHeld = pistolSwapLockDown;

        if (pistolSwapLockPressed && readyWasSelf && pistol != null)
        {
            handSwapController.TogglePistolSwapLock();
        }

        let playerBase = DoDAPlayerBase(owner);
        let handState = playerBase ? playerBase.GetHandState() : null;

        bool isAkimbo = (handState != null)
            ? handState.IsAkimboActive()
            : DoDA.IsAkimboActive();

        if (isAkimbo && !wasAkimboActive)
        {
            currentLeftLowerY = 120.0; // B92Left initializes below screen on Akimbo entry and raises smoothly!
            currentRightLowerY = 0.0;
        }
        else if (!isAkimbo && wasAkimboActive)
        {
            currentLeftLowerY = 0.0;
            currentRightLowerY = 0.0;
        }
        wasAkimboActive = isAkimbo;

        bool altDown = (owner.player.cmd.buttons & BT_ALTATTACK) != 0;
        bool altPressed = altDown && !wasHoldingAlt;
        wasHoldingAlt = altDown;

        let leftW = (isAkimbo && handState != null)
            ? handState.GetLeftWeapon(owner)
            : ((isAkimbo && owner != null) ? Weapon(owner.FindInventory('DoDAB92Left')) : null);
        let rightW = (isAkimbo && handState != null)
            ? handState.GetRightWeapon(owner)
            : ((isAkimbo && owner != null) ? Weapon(owner.FindInventory('DoDAB92Right')) : null);

        let leftPistol = DoDAPistol(leftW);
        let leftMP5 = DoDAMP5KSD(leftW);
        let rightPistol = DoDAPistol(rightW ? rightW : pistol);

        if (isAkimbo && readyWasSelf && rightPistol != null)
        {
            if (leftMP5 != null)
            {
                // Mixed Left MP5KSD / Right B92 Akimbo mode:
                // Left click (BT_ATTACK) fires Left MP5KSD
                bool shouldFire = leftMP5.ShouldStartFire(attackDown, attackPressed);
                if (shouldFire && leftFireLockTics <= 0 && !DoDA.IsReloadLocked())
                {
                    if (DoDA.RequestLeftHandFire())
                    {
                        State fireState = leftMP5.GetSecondaryFireState(attackDown, attackPressed);
                        if (fireState != null)
                        {
                            owner.player.SetPSprite(2, fireState);
                            let psp = owner.player.GetPSprite(2);
                            if (psp != null)
                            {
                                psp.Caller = leftMP5;
                                psp.bMirror = true;
                                psp.bAddBob = true;
                                psp.bAddWeapon = false;
                            }
                            leftFireLockTics = (leftMP5.fireMode == DoDAMP5KSD.Fire_Auto) ? 4 : 2;
                        }
                    }
                }

                // Right click (BT_ALTATTACK) fires Right B92
                if (altPressed && rightFireLockTics <= 0 && !DoDA.IsReloadLocked())
                {
                    if (DoDA.RequestRightHandFire())
                    {
                        rightFireLockTics = 2;
                        if (rightPistol.IsChamberLoaded())
                        {
                            owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("Fire"));
                        }
                        else
                        {
                            owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("DryFire"));
                        }
                    }
                }

                // Note: Mixed-pair reload is deferred/rejected in Phase 4A to preserve state integrity
            }
            else
            {
                bool isLeaningLeft = (leanController != null && leanController.GetLeanAmount() < -0.1);
                bool isLeaningRight = (leanController != null && leanController.GetLeanAmount() > 0.1);
                bool isLeaning = isLeaningLeft || isLeaningRight;

                // Priority 3: Akimbo leaning left (focus Left B92 only; Right mouse = Deadzone Aim)
                if (isLeaningLeft && !DoDA.IsReloadLocked())
                {
                    if (attackPressed && leftFireLockTics <= 0)
                    {
                        if (DoDA.RequestLeftHandFire())
                        {
                            leftFireLockTics = 2;
                            if (leftPistol != null)
                            {
                                if (leftPistol.IsChamberLoaded())
                                {
                                    owner.player.SetPSprite(2, leftPistol.ResolveState("SecondaryFire"));
                                }
                                else
                                {
                                    owner.player.SetPSprite(2, leftPistol.ResolveState("SecondaryDryFire"));
                                }
                            }
                        }
                    }
                }
                // Priority 4: Akimbo leaning right (focus Right B92 only; Right mouse = Deadzone Aim)
                else if (isLeaningRight && !DoDA.IsReloadLocked())
                {
                    if (attackPressed && rightFireLockTics <= 0)
                    {
                        if (DoDA.RequestRightHandFire())
                        {
                            rightFireLockTics = 2;
                            if (rightPistol.IsChamberLoaded())
                            {
                                owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("Fire"));
                            }
                            else
                            {
                                owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("DryFire"));
                            }
                        }
                    }
                }
                // Priority 5: Akimbo neutral (Left click = Left B92; Right click = Right B92)
                else if (!isLeaning && !DoDA.IsReloadLocked())
                {
                    // Left Mouse requests Left Hand
                    if (attackPressed && leftFireLockTics <= 0)
                    {
                        if (DoDA.RequestLeftHandFire())
                        {
                            leftFireLockTics = 2;
                            if (leftPistol != null)
                            {
                                if (leftPistol.IsChamberLoaded())
                                {
                                    owner.player.SetPSprite(2, leftPistol.ResolveState("SecondaryFire"));
                                }
                                else
                                {
                                    owner.player.SetPSprite(2, leftPistol.ResolveState("SecondaryDryFire"));
                                }
                            }
                        }
                    }

                    // Right Mouse requests Right Hand
                    if (altPressed && rightFireLockTics <= 0)
                    {
                        if (DoDA.RequestRightHandFire())
                        {
                            rightFireLockTics = 2;
                            if (rightPistol.IsChamberLoaded())
                            {
                                owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("Fire"));
                            }
                            else
                            {
                                owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("DryFire"));
                            }
                        }
                    }
                }

                // In Akimbo mode: Sequential Reload (lowest-loaded pistol first; if tied, right first)
                if (reloadPressed && leftFireLockTics <= 0 && rightFireLockTics <= 0 && !DoDA.IsReloadLocked())
                {
                    int leftTotal = leftPistol ? leftPistol.GetLoadedRoundCount() : 16;
                    int rightTotal = rightPistol ? rightPistol.GetLoadedRoundCount() : 16;

                    bool leftEligible = (leftPistol != null && leftTotal < 16);
                    bool rightEligible = (rightPistol != null && rightTotal < 16);

                    if (leftEligible || rightEligible)
                    {
                        bool pickRight = false;
                        if (rightEligible && leftEligible)
                        {
                            pickRight = (rightTotal <= leftTotal); // If tied, select right B92 first!
                        }
                        else if (rightEligible)
                        {
                            pickRight = true;
                        }
                        else
                        {
                            pickRight = false;
                        }

                        if (DoDA.RequestAkimboReload())
                        {
                            if (pickRight)
                            {
                                rightPistol.reloadQueued = false;
                                rightPistol.reloadInProgress = true;
                                owner.player.SetPSprite(PSP_WEAPON, rightPistol.ResolveState("Reload"));
                            }
                            else
                            {
                                leftPistol.reloadQueued = false;
                                leftPistol.reloadInProgress = true;
                                owner.player.SetPSprite(2, leftPistol.ResolveState("SecondaryReload"));
                            }
                        }
                    }
                }
            }
        }

        CVar secondaryActionCVar = CVar.GetCVar(
            'doda_weapon_secondary',
            owner.player
        );

        bool secondaryActionDown = secondaryActionCVar
            ? secondaryActionCVar.GetBool()
            : false;

        bool secondaryActionPressed =
            secondaryActionDown && !wasWeaponSecondaryHeld;

        wasWeaponSecondaryHeld = secondaryActionDown;

        if (!isAkimbo && swapBerettaPressed)
        {
            requestedHand = handSwapController.ResolveDesiredHand(
                deadzoneActive,
                yawGap,
                yawLimit,
                leanInput.WasLeaningLeftPressed(),
                leanInput.WasLeaningRightPressed(),
                isLeaning,
                true,
                leanLocked,
                leanController.GetLockedHand()
            );
        }

        if (!isAkimbo && leanLocked && swapBerettaPressed)
        {
            leanController.SetLockedHand(requestedHand);
        }

        if (deadzoneAimJustActivated && readyWasSelf)
        {
            HandleDeadzoneAimActivated();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            !isAkimbo
            && secondaryActionPressed
            && readyWasSelf
        )
        {
            HandleSecondaryWeaponAction();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            !isAkimbo
            && swapBerettaPressed
            && readyWasSelf
        )
        {
            HandleManualWeaponControl();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            !isAkimbo
            && readyWasSelf
            && pistol != null
            && pistol.IsReloadQueued()
            && pendingWeapon == WP_NOCHANGE
            && weaponSprite != null
            && (
                weaponSprite.CurState == ResolveState("Ready")
                || weaponSprite.CurState == ResolveState("ReadyEmpty")
            )
        )
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("Reload")
            );

            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            !isAkimbo
            && readyWasSelf
            && ShouldStartFire(attackDown, attackPressed)
            && fireLockTics <= 0
            && UsesManualFireDispatch()
        )
        {
            State fireState = GetFireState(attackDown, attackPressed);

            if (fireState != null)
            {
                owner.player.SetPSprite(PSP_WEAPON, fireState);
            }
        }

        bool reloadAnimationActive =
            weaponSprite != null
            && weaponSprite.CurState != null
            && weaponSprite.CurState.InStateSequence(
                ResolveState("Reload")
            );

        if (
            !isAkimbo
            && readyWasSelf
            && pistol != null
            && reloadPressed
            && pendingWeapon == WP_NOCHANGE
            && fireLockTics <= 0
            && !reloadAnimationActive
        )
        {
            RequestLowestLoadedPistolReload(pistol);
            pendingWeapon = owner.player.PendingWeapon;
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        bool requestGate =
            !isAkimbo
            && pistol != null
            && readyWasSelf
            && pendingWeapon == WP_NOCHANGE
            && requestedHand != actualHand
            && fireLockTics <= 0
            && (
                weaponSprite == null
                || weaponSprite.CurState != ResolveState("Reload")
            );

        bool pipelineChanged =
            !pipelineInitialized
            || readyWeapon != lastLoggedReadyWeapon
            || pendingWeapon != lastLoggedPendingWeapon
            || (
                weaponSprite != null
                && weaponSprite.CurState != lastLoggedWeaponState
            )
            || readyWasSelf != lastLoggedReadyWasSelf
            || attackDown != lastLoggedAttackDown
            || requestedHand != lastLoggedRequestedHand
            || actualHand != lastLoggedActualHand
            || attackPressed
            || swapBerettaPressed
            || secondaryActionPressed
            || deadzoneAimJustActivated;

        if (pipelineChanged)
        {
            pipelineInitialized = true;
            lastLoggedReadyWeapon = readyWeapon;
            lastLoggedPendingWeapon = pendingWeapon;
            lastLoggedWeaponState = weaponSprite
                ? weaponSprite.CurState
                : null;
            lastLoggedReadyWasSelf = readyWasSelf;
            lastLoggedAttackDown = attackDown;
            lastLoggedRequestedHand = requestedHand;
            lastLoggedActualHand = actualHand;
        }

        if (requestGate)
        {
            pistol.RequestHandSwap(
                requestedHand,
                swapBerettaPressed
            );
        }

        spriteAnimator.Update(
            actualHand,
            yawGap,
            pitchGap,
            leanController.GetLeanAmount(),
            0.0,
            isLeaning,
            leaningLeft,
            GetWeaponArchetype()
        );

        CVar debugXCVar = CVar.GetCVar(
            'doda_debug_sprite_x',
            owner.player
        );

        CVar debugYCVar = CVar.GetCVar(
            'doda_debug_sprite_y',
            owner.player
        );

        CVar debugRotationCVar = CVar.GetCVar(
            'doda_debug_sprite_rot',
            owner.player
        );

        CVar debugScaleCVar = CVar.GetCVar(
            'doda_debug_sprite_scale',
            owner.player
        );

        CVar debugPrintCVar = CVar.GetCVar(
            'doda_debug_print_now',
            owner.player
        );

        debugSpriteX = debugXCVar ? debugXCVar.GetFloat() : 0.0;
        debugSpriteY = debugYCVar ? debugYCVar.GetFloat() : 0.0;

        debugSpriteRot = debugRotationCVar
            ? debugRotationCVar.GetFloat()
            : 0.0;

        debugSpriteScale = debugScaleCVar
            ? Max(0.05, debugScaleCVar.GetFloat())
            : 1.0;

        bool printNow = debugPrintCVar
            ? debugPrintCVar.GetBool()
            : false;

        if (printNow != lastDebugPrintToggleState)
        {
            lastDebugPrintToggleState = printNow;

            if (printNow)
            {
                PrintDebugSpriteOffsets(actualHand);
            }
        }

        if (
            !readyWasSelf
            || weaponSprite == null
            || weaponSprite.CurState == null
        )
        {
            return;
        }

        if (isAkimbo)
        {
            let rightPistol = (handState != null && handState.GetRightPistol() != null)
                ? handState.GetRightPistol()
                : pistol;
            let leftPistol = (handState != null)
                ? handState.GetLeftPistol(owner)
                : ((owner != null) ? DoDAPistol(owner.FindInventory('DoDAB92Left')) : null);

            bool rightReloading = (rightPistol != null && rightPistol.reloadInProgress);
            bool leftReloading = (leftPistol != null && leftPistol.reloadInProgress);

            double targetRightLowerY = 0.0;
            double targetLeftLowerY = 0.0;

            // Priority 1: Active sequential reload
            if (rightReloading)
            {
                targetRightLowerY = 0.0;
                targetLeftLowerY = 120.0; // Left lowers offscreen
            }
            else if (leftReloading)
            {
                targetLeftLowerY = 0.0;
                targetRightLowerY = 120.0; // Right lowers offscreen
            }
            // Priority 2: Lean
            else if (leanController.GetLeanAmount() < -0.1) // Leaning Left
            {
                targetLeftLowerY = 0.0; // Left stays visible
                targetRightLowerY = 120.0; // Right lowers offscreen
            }
            else if (leanController.GetLeanAmount() > 0.1) // Leaning Right
            {
                targetRightLowerY = 0.0; // Right stays visible
                targetLeftLowerY = 120.0; // Left lowers offscreen
            }
            // Priority 3: Neutral
            else
            {
                targetRightLowerY = 0.0;
                targetLeftLowerY = 0.0;
            }

            // Smooth interpolation toward target lowering offset
            double lowerSpeed = 0.25;
            currentRightLowerY += (targetRightLowerY - currentRightLowerY) * lowerSpeed;
            currentLeftLowerY += (targetLeftLowerY - currentLeftLowerY) * lowerSpeed;

            // Right Hand (PSP_WEAPON / DoDAB92Right) - Base Right Profile (Rest Y = 32.0)
            double rightRestX = 48.0;
            double rightRestY = 32.0;
            double finalRightX = rightRestX - yawGap * 3.0 + leanController.GetLeanAmount() * 8.0;
            double finalRightY = rightRestY + pitchGap * 0.6 + currentRightLowerY;
            weaponSprite.x = finalRightX + debugSpriteX;
            weaponSprite.y = finalRightY + debugSpriteY;
            weaponSprite.rotation = spriteAnimator.GetFinalRotation() + debugSpriteRot;
            weaponSprite.HAlign = PSPA_CENTER;
            weaponSprite.VAlign = PSPA_CENTER;
            weaponSprite.bPivotPercent = true;
            weaponSprite.pivot = (0.5, 0.5);
            weaponSprite.bFlip = false;

            // Left Hand (PSP_DODA_SECONDARY / DoDAB92Left) - Base Left Profile (Calibrated Rest Y = 8.0 for level alignment with Right B92 at 32.0)
            let secSprite = owner.player.GetPSprite(2);
            if (secSprite != null)
            {
                double leftRestX = -48.0;
                double leftRestY = 8.0;
                double finalLeftX = leftRestX - yawGap * 3.0 + leanController.GetLeanAmount() * 8.0;
                double finalLeftY = leftRestY + pitchGap * 0.6 + currentLeftLowerY;
                secSprite.x = finalLeftX + debugSpriteX;
                secSprite.y = finalLeftY + debugSpriteY;
                secSprite.rotation = spriteAnimator.GetFinalRotation() + debugSpriteRot;
                secSprite.HAlign = PSPA_CENTER;
                secSprite.VAlign = PSPA_CENTER;
                secSprite.bPivotPercent = true;
                secSprite.pivot = (0.5, 0.5);
                secSprite.bFlip = false;
            }

            return;
        }

        bool isReadyState =
            weaponSprite.CurState == ResolveState("Ready");

        bool isFireState =
            weaponSprite.CurState.InStateSequence(
                ResolveState("Fire")
            );

        bool isReloadState =
            weaponSprite.CurState.InStateSequence(
                ResolveState("Reload")
            );

        bool isDeselectState =
            weaponSprite.CurState == ResolveState("Deselect");

        bool isSelectState =
            weaponSprite.CurState == ResolveState("Select");

        bool isLowReadyState =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowerToLowReady")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("LowReady")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReady")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReadyToRack")
            );

        bool isRackState =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RackWait")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("HipRack")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RackCycle")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RackReturn")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("PostFire")
            );

        if (
            isReadyState
            || isFireState
            || isReloadState
            || isLowReadyState
            || isRackState
        )
        {
            spriteAnimator.Apply(
                weaponSprite,
                debugSpriteX,
                debugSpriteY,
                debugSpriteRot
            );

            return;
        }

        if (isDeselectState || isSelectState)
        {
            spriteAnimator.ApplyTransition(
                weaponSprite,
                debugSpriteX,
                debugSpriteY,
                debugSpriteRot
            );
        }
    }

    virtual int GetWeaponHand()
    {
        return Hand_Right;
    }

    virtual int GetWeaponArchetype()
    {
        return ARCHETYPE_Default;
    }

    Actor SpawnCasing(
        class<Actor> casingClass,
        double forwardDistance,
        double angleOffset,
        double heightFraction,
        double speedMin,
        double speedMax,
        double upwardImpulseMin,
        double upwardImpulseMax,
        bool setCasingAngle = false
    )
    {
        if (owner == null)
        {
            return null;
        }

        double resolvedAngle = owner.angle + angleOffset;
        Vector3 spawnPos = owner.Vec3Angle(
            forwardDistance,
            resolvedAngle,
            owner.height * heightFraction
        );

        Actor casing = Spawn(casingClass, spawnPos);
        if (casing == null)
        {
            return null;
        }

        double speed = (speedMin == speedMax)
            ? speedMin
            : FRandom(speedMin, speedMax);

        double upwardImpulse = (upwardImpulseMin == upwardImpulseMax)
            ? upwardImpulseMin
            : FRandom(upwardImpulseMin, upwardImpulseMax);

        casing.vel = owner.vel;
        casing.vel.x += Cos(resolvedAngle) * speed;
        casing.vel.y += Sin(resolvedAngle) * speed;
        casing.vel.z += upwardImpulse;

        if (setCasingAngle)
        {
            casing.angle = resolvedAngle;
        }

        return casing;
    }

    action void DoDA_SpawnPistolCasing()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        let pistol = (invoker is "DoDAPistol")
            ? DoDAPistol(invoker)
            : DoDAPistol(invoker.owner.player.ReadyWeapon);

        if (pistol == null)
        {
            return;
        }

        bool isLeftPistol = pistol.GetWeaponHand() == Hand_Left;

        let agent = FieldAgent(invoker.owner);

        bool deadzoneActive =
            agent != null
            && agent.IsDeadzoneAimActive();

        double yawOffset = deadzoneActive
            ? agent.GetDeadzoneYawGap()
            : 0.0;

        double angleOffset = yawOffset
            + (isLeftPistol ? 45.0 : -45.0);

        invoker.SpawnCasing(
            "DoDAPistolCasing",
            10.0,
            angleOffset,
            0.60,
            5.0,
            5.0,
            2.0,
            3.0,
            true
        );
    }

    bool FireDeadzoneHitscanRay(
        double localYawOffset,
        double localPitchOffset,
        out FLineTraceData trace,
        double maxRange = 2048.0
    )
    {
        if (
            owner == null
            || owner.player == null
            || owner.player.mo == null
            || owner.health <= 0
        )
        {
            return false;
        }

        let agent = FieldAgent(owner);

        bool deadzoneActive =
            agent != null
            && agent.IsDeadzoneAimActive();

        double yawOffset = deadzoneActive
            ? agent.GetDeadzoneYawGap()
            : 0.0;

        double pitchOffset = deadzoneActive
            ? agent.GetDeadzonePitchGap()
            : 0.0;

        double fireYaw = owner.angle + yawOffset + localYawOffset;
        double firePitch = owner.pitch + pitchOffset + localPitchOffset;

        double attackZ =
            owner.height * 0.5
            - owner.floorclip
            + owner.player.mo.AttackZOffset
                * owner.player.crouchFactor;

        double leanOffset = leanController != null
            ? leanController.GetAppliedOffset()
            : 0.0;

        return owner.LineTrace(
            fireYaw,
            maxRange,
            firePitch,
            0,
            attackZ,
            0.0,
            leanOffset,
            trace
        );
    }

    action void DoDA_FireTrace()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
            || invoker.owner.player.mo == null
        )
        {
            return;
        }

        let pistol = (invoker is "DoDAPistol")
            ? DoDAPistol(invoker)
            : DoDAPistol(invoker.owner.player.ReadyWeapon);

        if (pistol == null || !pistol.ConsumeFiredRound())
        {
            return;
        }

        invoker.fireLockTics = 9;

        let agent = FieldAgent(invoker.owner);

        bool deadzoneActive =
            agent != null
            && agent.IsDeadzoneAimActive();

        bool isLeftHand = pistol.GetWeaponHand() == Hand_Left;

        double spread = invoker.hipfireSpread;

        let playerBase = DoDAPlayerBase(invoker.owner);
        let handState = playerBase ? playerBase.GetHandState() : null;
        bool isAkimbo = (handState != null)
            ? handState.IsAkimboActive()
            : DoDA.IsAkimboActive();

        if (deadzoneActive)
        {
            spread = 0.0;
        }
        else if (isAkimbo)
        {
            bool isLeaning = (invoker.leanController != null && abs(invoker.leanController.GetLeanAmount()) > 0.1) || (agent != null && abs(agent.LeanOffset) > 0.1);
            if (isLeaning)
            {
                spread = 2.0; // Focused B92 Akimbo lean hipfire spread: 2.0 degrees
            }
            else
            {
                spread = 2.5; // Neutral B92 Akimbo symmetric hipfire spread: 2.5 degrees (identical for Left and Right)
            }
        }
        else if (isLeftHand)
        {
            spread *= invoker.offhandSpreadMult;
        }

        double randomAngle = Random(0.0, 360.0);
        double randomRadius = Random(0.0, spread);

        double localYawOffset = Cos(randomAngle) * randomRadius;
        double localPitchOffset = Sin(randomAngle) * randomRadius;

        pistol.DoDA_PlayFireSound();

        FLineTraceData trace;

        bool hit = invoker.FireDeadzoneHitscanRay(
            localYawOffset,
            localPitchOffset,
            trace,
            2048.0
        );

        if (!hit)
        {
            return;
        }

        if (
            trace.HitType == TRACE_HitWall
            || trace.HitType == TRACE_HitFloor
            || trace.HitType == TRACE_HitCeiling
        )
        {
            Spawn("BulletPuff", trace.HitLocation);
            return;
        }

        if (trace.HitType != TRACE_HitActor || !trace.HitActor)
        {
            return;
        }

        let target = trace.HitActor;

        double targetTop = target.Pos.Z + target.Height;
        double headBandStart = targetTop - target.Height * 0.33;

        int damage = trace.HitLocation.Z >= headBandStart
            ? 35
            : 20;

        target.DamageMobj(
            invoker.owner,
            invoker.owner,
            damage,
            'Hitscan'
        );

        Spawn("BulletPuff", trace.HitLocation);
    }
}