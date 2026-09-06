///////////////////////////
// DoDA/WeaponSystem/WeaponBase.zs
///////////////////////////

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
    bool wasSwapBerettaHeld;
    bool wasWeaponSecondaryHeld;
    bool wasDeadzoneAimActive;
    bool wasHoldingFire;
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

        let leftPistol = DoDAPistol(
            owner.FindInventory('DoDAB92Left')
        );

        let rightPistol = DoDAPistol(
            owner.FindInventory('DoDAB92Right')
        );

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

        if (swapBerettaPressed)
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

        if (leanLocked && swapBerettaPressed)
        {
            leanController.SetLockedHand(requestedHand);
        }

        if (deadzoneAimJustActivated && readyWasSelf)
        {
            HandleDeadzoneAimActivated();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            secondaryActionPressed
            && readyWasSelf
        )
        {
            HandleSecondaryWeaponAction();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            swapBerettaPressed
            && readyWasSelf
        )
        {
            HandleManualWeaponControl();
            weaponSprite = owner.player.GetPSprite(PSP_WEAPON);
        }

        if (
            readyWasSelf
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
            readyWasSelf
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
            readyWasSelf
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
            pistol != null
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
            IsMP5Weapon()
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

    virtual bool IsMP5Weapon()
    {
        return false;
    }

    action void DoDA_SpawnPistolCasing()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol == null || invoker.owner == null)
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

        double weaponFacingAngle = invoker.owner.angle + yawOffset;

        double ejectAngle = weaponFacingAngle
            + (isLeftPistol ? 45.0 : -45.0);

        vector2 ejectDirection = AngleToVector(ejectAngle, 1.0);

        double PistolCasingForwardDiagonalSpawnOffset = 10.0;
        double PistolCasingSpawnZFraction = 0.60;

        vector2 spawnXY =
            invoker.owner.Pos.XY
            + ejectDirection * PistolCasingForwardDiagonalSpawnOffset;

        vector3 spawnPos = (
            spawnXY.X,
            spawnXY.Y,
            invoker.owner.Pos.Z
                + invoker.owner.height * PistolCasingSpawnZFraction
        );

        Actor casing = Spawn("DoDAPistolCasing", spawnPos);

        if (casing)
        {
            double PistolCasingEjectSpeed = 5.0;

            casing.vel = invoker.owner.vel;
            casing.vel.x += ejectDirection.X * PistolCasingEjectSpeed;
            casing.vel.y += ejectDirection.Y * PistolCasingEjectSpeed;
            casing.vel.z += FRandom(2.0, 3.0);
            casing.angle = ejectAngle;
        }
    }

    action void DoDA_SpawnCasing(class<Actor> casingType)
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        Vector3 spawnPos = invoker.owner.Vec3Angle(
            4.0,
            invoker.owner.angle + 90.0,
            invoker.owner.height * 0.7
        );

        Actor casing = Spawn(casingType, spawnPos);

        if (casing)
        {
            casing.vel = invoker.owner.vel;
            casing.vel.xy += (
                Random(-1.0, 1.0),
                Random(-1.0, 1.0)
            );
            casing.vel.z += 2.0;
        }
    }

    action void DoDA_FireTrace()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
            || invoker.owner.health <= 0
            || invoker.owner.player.mo == null
        )
        {
            return;
        }

        let pistol = DoDAPistol(
            invoker.owner.player.ReadyWeapon
        );

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

        if (deadzoneActive)
        {
            spread = 0.0;
        }
        else if (isLeftHand)
        {
            spread *= invoker.offhandSpreadMult;
        }

        double randomAngle = Random(0.0, 360.0);
        double randomRadius = Random(0.0, spread);

        double yawOffset = deadzoneActive
            ? agent.GetDeadzoneYawGap()
            : 0.0;

        double pitchOffset = deadzoneActive
            ? agent.GetDeadzonePitchGap()
            : 0.0;

        double fireYaw = invoker.owner.angle
            + yawOffset
            + Cos(randomAngle) * randomRadius;

        double firePitch = invoker.owner.pitch
            + pitchOffset
            + Sin(randomAngle) * randomRadius;

        pistol.DoDA_PlayFireSound();

        FLineTraceData trace;

        double attackZ =
            invoker.owner.height * 0.5
            - invoker.owner.floorclip
            + invoker.owner.player.mo.AttackZOffset
                * invoker.owner.player.crouchFactor;

        double leanOffset = invoker.leanController != null
            ? invoker.leanController.GetAppliedOffset()
            : 0.0;

        bool hit = invoker.owner.LineTrace(
            fireYaw,
            2048.0,
            firePitch,
            0,
            attackZ,
            0.0,
            leanOffset,
            trace
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