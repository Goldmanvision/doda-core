class DoDAShotgun : DoDAWeapon
{
    const TubeCapacity = 7;
    const LowReadyDelayTics = 105;

    int tubeShells;
    bool chamberLoaded;
    bool chamberHasSpentShell;
    bool pendingRack;

    bool wasShotgunAttackHeld;
    bool wasShotgunReloadHeld;
    bool shotgunInitialized;

    int lowReadyIdleTics;

    Default
    {
        Weapon.SelectionOrder 1300;
        Weapon.AmmoType "Shell";
        Weapon.SlotNumber 3;
        Weapon.AmmoUse 0;
        Weapon.AmmoGive 12;
        Inventory.PickupMessage "$GOTSHOTGUN";
        Obituary "$OB_MPSHOTGUN";
        Tag "$TAG_SHOTGUN";
        +WEAPON.NOAUTOFIRE;
		DamageFunction random(5, 10);
    }

    override void Tick()
    {
        Super.Tick();

        if (owner == null || owner.player == null)
        {
            return;
        }

        if (!shotgunInitialized)
        {
            tubeShells = TubeCapacity;
            chamberLoaded = true;
            chamberHasSpentShell = false;
            pendingRack = false;
            lowReadyIdleTics = 0;
            shotgunInitialized = true;
        }

        bool attackDown =
            (owner.player.cmd.buttons & BT_ATTACK) != 0;

        bool attackPressed =
            attackDown && !wasShotgunAttackHeld;

        wasShotgunAttackHeld = attackDown;

        bool reloadDown =
            (owner.player.cmd.buttons & BT_RELOAD) != 0;

        bool reloadPressed =
            reloadDown && !wasShotgunReloadHeld;

        wasShotgunReloadHeld = reloadDown;

        if (owner.player.ReadyWeapon != self)
        {
            lowReadyIdleTics = 0;
            return;
        }

        PSprite weaponSprite = owner.player.GetPSprite(
            PSP_WEAPON
        );

        if (
            weaponSprite == null
            || weaponSprite.CurState == null
        )
        {
            lowReadyIdleTics = 0;
            return;
        }

        let agent = FieldAgent(owner);

        bool deadzoneActive = agent != null
            && agent.IsDeadzoneAimActive();

        bool inLowerToLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowerToLowReady")
            );

        bool inLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowReady")
            ); 

        bool inRaiseFromLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReady")
            );

        bool inRaiseFromLowReadyToRack =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReadyToRack")
            );

        bool isInLowReadyFamily =
            inLowerToLowReady
            || inLowReady
            || inRaiseFromLowReady
            || inRaiseFromLowReadyToRack;

        if (deadzoneActive && isInLowReadyFamily)
        {
            lowReadyIdleTics = 0;
        }

        bool isReady =
            weaponSprite.CurState == ResolveState("Ready");

        bool isRackWait =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RackWait")
            );

        bool isPostReload =
            weaponSprite.CurState.InStateSequence(
                ResolveState("PostReload")
            );

        let reserveShells = Ammo(
            owner.FindInventory('Shell')
        );

        bool hasReserveShells =
            reserveShells != null
            && reserveShells.Amount > 0;

        if (pendingRack && isRackWait)
        {
            lowReadyIdleTics++;

            if (
                deadzoneActive
                || lowReadyIdleTics >= LowReadyDelayTics
            )
            {
                lowReadyIdleTics = 0;

                owner.player.SetPSprite(
                    PSP_WEAPON,
                    ResolveState("LowerToLowReady")
                );

                return;
            }
        }
        else
        {
            lowReadyIdleTics = 0;
        }

        if (
            reloadPressed
            && isPostReload
            && tubeShells < TubeCapacity
            && hasReserveShells
        )
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("Reload")
            );

            return;
        }

        if (attackPressed && isReady)
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                chamberLoaded
                    ? ResolveState("Fire")
                    : ResolveState("DryFire")
            );

            return;
        }

        if (
            reloadPressed
            && isReady
            && !pendingRack
            && tubeShells < TubeCapacity
            && hasReserveShells
        )
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("PreReload")
            );
        }
    }

    override void HandleManualWeaponControl()
    {
        if (owner == null || owner.player == null)
        {
            return;
        }

        PSprite weaponSprite = owner.player.GetPSprite(
            PSP_WEAPON
        );

        if (
            weaponSprite == null
            || weaponSprite.CurState == null
        )
        {
            return;
        }

        if (
            weaponSprite.CurState.InStateSequence(
                ResolveState("HipRackApproach")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReadyToRack")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RackFromPreRack")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RackFromReady")
            )
            || weaponSprite.CurState.InStateSequence(
                ResolveState("RackReturn")
            )
        )
        {
            return;
        }

        lowReadyIdleTics = 0;

        bool inLowerToLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowerToLowReady")
            );

        bool inLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowReady")
            );

        bool inRaiseFromLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReady")
            );

        if (
            inLowerToLowReady
            || inLowReady
            || inRaiseFromLowReady
        )
        {
            pendingRack = true;

            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("RaiseFromLowReadyToRack")
            );

            return;
        }

        if (
            weaponSprite.CurState.InStateSequence(
                ResolveState("RackWait")
            )
        )
        {
            pendingRack = true;

            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("RackFromPreRack")
            );

            return;
        }

        if (weaponSprite.CurState == ResolveState("Ready"))
        {
            pendingRack = true;

            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("HipRackApproach")
            );
        }
    }

    override void HandleSecondaryWeaponAction()
    {
        if (owner == null || owner.player == null)
        {
            return;
        }

        PSprite weaponSprite = owner.player.GetPSprite(
            PSP_WEAPON
        );

        if (
            weaponSprite == null
            || weaponSprite.CurState == null
        )
        {
            return;
        }

        lowReadyIdleTics = 0;

        bool isRackWait =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RackWait")
            );

        bool inLowerToLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowerToLowReady")
            );

        bool inLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowReady")
            );

        bool inRaiseFromLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReady")
            );

        bool inRaiseFromLowReadyToRack =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReadyToRack")
            );

        if (pendingRack && isRackWait)
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("LowerToLowReady")
            );

            return;
        }

        if (
            pendingRack
            && (
                inLowerToLowReady
                || inLowReady
                || inRaiseFromLowReady
                || inRaiseFromLowReadyToRack
            )
        )
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("RaiseFromLowReady")
            );
        }
    }

    override void HandleDeadzoneAimActivated()
    {
        if (owner == null || owner.player == null)
        {
            return;
        }

        lowReadyIdleTics = 0;

        PSprite weaponSprite = owner.player.GetPSprite(
            PSP_WEAPON
        );

        if (
            weaponSprite == null
            || weaponSprite.CurState == null
        )
        {
            return;
        }

        bool inLowerToLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowerToLowReady")
            );

        bool inLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("LowReady")
            );

        bool inRaiseFromLowReady =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReady")
            );

        bool inRaiseFromLowReadyToRack =
            weaponSprite.CurState.InStateSequence(
                ResolveState("RaiseFromLowReadyToRack")
            );

        bool isInLowReadyFamily =
            inLowerToLowReady
            || inLowReady
            || inRaiseFromLowReady
            || inRaiseFromLowReadyToRack;

        if (
            (pendingRack || !chamberLoaded)
            && !isInLowReadyFamily
        )
        {
            owner.player.SetPSprite(
                PSP_WEAPON,
                ResolveState("LowerToLowReady")
            );
        }
    }

    clearscope int GetTubeShellCount()
    {
        return tubeShells;
    }

    clearscope int GetTubeCapacity()
    {
        return TubeCapacity;
    }

    clearscope bool IsChamberLoaded()
    {
        return chamberLoaded;
    }

    clearscope bool IsRackPending()
    {
        return pendingRack;
    }

    clearscope int GetReserveShellCount()
    {
        if (owner == null)
        {
            return 0;
        }

        let reserveShells = Ammo(
            owner.FindInventory('Shell')
        );

        return reserveShells != null
            ? reserveShells.Amount
            : 0;
    }

    clearscope String GetChamberStatusText()
    {
        if (chamberLoaded)
        {
            return "LIVE";
        }

        if (pendingRack)
        {
            return "SPENT / UNRACKED";
        }

        return "EMPTY";
    }

    action void A_Shotgun_EjectChamberShell()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
        )
        {
            return;
        }

        if (!invoker.chamberLoaded && !invoker.chamberHasSpentShell)
        {
            return;
        }

        invoker.chamberLoaded = false;
        invoker.chamberHasSpentShell = false;

        invoker.A_Shotgun_ShellEjectSound();
        invoker.DoDA_SpawnShotgunCasing();
    }

    action void DoDA_SpawnShotgunCasing()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        // Right side, forward of the camera, and below eye height.
        Vector3 spawnPos = invoker.owner.Vec3Angle(
            10.0,
            invoker.owner.angle - 55.0,
            invoker.owner.height * 0.42
        );

        Actor casing = Spawn("DoDAShotgunCasing", spawnPos);

        if (casing == null)
        {
            return;
        }

        double ejectAngle = invoker.owner.angle - 55.0;
        double ejectSpeed = FRandom(6.0, 8.0);

        casing.vel = invoker.owner.vel;
        casing.vel.x += Cos(ejectAngle) * ejectSpeed;
        casing.vel.y += Sin(ejectAngle) * ejectSpeed;
        casing.vel.z += FRandom(1.5, 2.5);
    }

    action void A_Shotgun_DryFireSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/shotgun/dryfire",
            CHAN_BODY
        );
    }

    action void A_Shotgun_RackSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/shotgun/rack",
            CHAN_BODY
        );
    }

    action void A_Shotgun_ShellEjectSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        int soundVariant = Random(1, 7);

        if (soundVariant == 1)
        {
            A_StartSound(
                "doda/shotgun/shell_eject1",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else if (soundVariant == 2)
        {
            A_StartSound(
                "doda/shotgun/shell_eject2",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else if (soundVariant == 3)
        {
            A_StartSound(
                "doda/shotgun/shell_eject3",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else if (soundVariant == 4)
        {
            A_StartSound(
                "doda/shotgun/shell_eject4",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else if (soundVariant == 5)
        {
            A_StartSound(
                "doda/shotgun/shell_eject5",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else if (soundVariant == 6)
        {
            A_StartSound(
                "doda/shotgun/shell_eject6",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
        else
        {
            A_StartSound(
                "doda/shotgun/shell_eject7",
                CHAN_BODY,
                CHANF_OVERLAP
            );
        }
    }

    action void A_Shotgun_LoadShellSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        if (Random(1, 2) == 1)
        {
            A_StartSound(
                "doda/shotgun/shell_load1",
                CHAN_BODY
            );
        }
        else
        {
            A_StartSound(
                "doda/shotgun/shell_load2",
                CHAN_BODY
            );
        }
    }

    action State A_Shotgun_BeginFire()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
        )
        {
            return ResolveState("Ready");
        }

        if (
            invoker.pendingRack
            || !invoker.chamberLoaded
        )
        {
            return ResolveState("DryFire");
        }

        return ResolveState("HipFire");
    }

    action void A_Shotgun_FireTrace()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
            || invoker.owner.player.mo == null
            || invoker.owner.health <= 0
        )
        {
            return;
        }

        A_StartSound(
            "doda/shotgun/fire",
            CHAN_WEAPON
        );

        for (int pellet = 0; pellet < 7; pellet++)
        {
            double randomAngle = Random(0.0, 360.0);
            double randomRadius = Random(0.0, 5.0);

            double localYawOffset = Cos(randomAngle) * randomRadius;
            double localPitchOffset = Sin(randomAngle) * randomRadius;

            FLineTraceData trace;

            bool hit = invoker.FireDeadzoneHitscanRay(
                localYawOffset,
                localPitchOffset,
                trace,
                2048.0
            );

            if (!hit)
            {
                continue;
            }

            if (
                trace.HitType == TRACE_HitWall
                || trace.HitType == TRACE_HitFloor
                || trace.HitType == TRACE_HitCeiling
            )
            {
                Spawn("BulletPuff", trace.HitLocation);
                continue;
            }

            if (
                trace.HitType != TRACE_HitActor
                || !trace.HitActor
            )
            {
                continue;
            }

            trace.HitActor.DamageMobj(
                invoker.owner,
                invoker.owner,
                5,
                'Hitscan'
            );

            Spawn("BulletPuff", trace.HitLocation);
        }
    }

    action State A_Shotgun_AfterShot()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
        )
        {
            return ResolveState("Ready");
        }

        invoker.chamberLoaded = false;
        invoker.chamberHasSpentShell = true;
        invoker.pendingRack = true;
        invoker.lowReadyIdleTics = 0;

        return ResolveState("PostFire");
    }

    action State A_Shotgun_LoadSingleShell()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
        )
        {
            return ResolveState("Ready");
        }

        let reserveShells = Ammo(
            invoker.owner.FindInventory('Shell')
        );

        if (invoker.tubeShells >= invoker.TubeCapacity)
        {
            Console.Printf(
                "[DODA/SHOTGUN] reload blocked: tube full"
            );

            return ResolveState("Ready");
        }

        if (
            reserveShells == null
            || reserveShells.Amount <= 0
        )
        {
            Console.Printf(
                "[DODA/SHOTGUN] reload blocked: no reserve Shell"
            );

            return ResolveState("Ready");
        }

        reserveShells.Amount--;
        invoker.tubeShells++;

        invoker.A_Shotgun_LoadShellSound();

        Console.Printf(
            "[DODA/SHOTGUN] reload success: tube=%d/%d reserve=%d",
            invoker.tubeShells,
            invoker.TubeCapacity,
            reserveShells.Amount
        );

        return ResolveState("PostReload");
    }

    action State A_Shotgun_FinishRack()
    {
        if (
            invoker == null
            || invoker.owner == null
            || invoker.owner.player == null
        )
        {
            return ResolveState("Ready");
        }

        invoker.chamberLoaded = false;
        invoker.chamberHasSpentShell = false;

        if (invoker.tubeShells > 0)
        {
            invoker.tubeShells--;
            invoker.chamberLoaded = true;
        }

        invoker.pendingRack = false;
        invoker.lowReadyIdleTics = 0;

        invoker.wasShotgunAttackHeld =
            (invoker.owner.player.cmd.buttons & BT_ATTACK) != 0;

        return ResolveState("RackReturn");
    }

    States
    {
    Spawn:
        SHTC C -1;
        Stop;

    Ready:
        SHTN A 1 A_WeaponReady(WRF_NOFIRE);
        Loop;

    Deselect:
        SHTN A 1 A_Lower;
        Loop;

    Select:
        SHTN A 1 A_Raise;
        Loop;

    Fire:
        TNT1 A 0 A_Shotgun_BeginFire;
        Stop;

    DryFire:
        TNT1 A 0 A_Shotgun_DryFireSound;
        SHTN A 4;
        Goto Ready;

    HipFire:
        SHTA A 1 Bright A_Shotgun_FireTrace;
        SHTA B 1;
        SHTA C 1;
        SHTA D 1;
        SHTA E 1 A_Shotgun_AfterShot;
        Stop;

    PostFire:
        SHTN A 1;
        SHTN B 1;
        SHTN C 1;
        SHTN D 1;
        SHTN E 1;
        SHTN F 1;
        SHTN G 1;
        Goto RackWait;

    RackWait:
        SHTN G 1 A_WeaponReady(WRF_NOFIRE);
        Loop;

    PreReload:
        SHTN A 1;
        SHTN B 1;
        SHTN C 1;
        SHTN D 1;
        SHTN E 1;
        SHTN F 1;
        SHTN G 1;
        Goto Reload;

    Reload:
        SHTN S 1;
        SHTN T 1;
        SHTN U 1;
        SHTN V 1;
        SHTN W 1;
        SHTN X 1;
        SHTN Y 1;
        SHTN Z 1;
        SHTN [ 1;
        SHTN ] 1 A_Shotgun_LoadSingleShell;
        Goto PostReload;

    PostReload:
        SHTN G 1;
        SHTN F 1;
        SHTN E 1;
        SHTN D 1;
        SHTN C 1;
        SHTN B 1;
        SHTN A 1;
        Goto Ready;

    LowerToLowReady:
        SGUP A 2;
        SGUP B 2;
        SGUP C 2;
        SGUP D 2;
        Goto LowReady;

    LowReady:
        SGUP D 1 A_WeaponReady(WRF_NOFIRE);
        Loop;

    RaiseFromLowReady:
        SGUP D 2;
        SGUP C 2;
        SGUP B 2;
        SGUP A 2;
        Goto RackWait;

    RaiseFromLowReadyToRack:
        SGUP D 2;
        SGUP C 2;
        SGUP B 2;
        SGUP A 2;
        Goto RackFromPreRack;

    HipRackApproach:
        SHTN A 1;
        SHTN B 1;
        SHTN C 1;
        SHTN D 1;
        SHTN E 1;
        SHTN F 1;
        SHTN G 1;
        Goto RackFromReady;

    RackFromPreRack:
        TNT1 A 0 A_Shotgun_RackSound;
        SHTN H 1;
        SHTN I 1;
        SHTN J 1;
        SHTN K 1;
        SHTN L 1;
        SHTN M 1 A_Shotgun_EjectChamberShell;
        SHTN N 1;
        SHTN O 1;
        SHTN P 1;
        SHTN Q 1;
        SHTN R 1 A_Shotgun_FinishRack;
        Stop;

    RackFromReady:
        TNT1 A 0 A_Shotgun_RackSound;
        SHTN H 1;
        SHTN I 1;
        SHTN J 1;
        SHTN K 1;
        SHTN L 1;
        SHTN M 1 A_Shotgun_EjectChamberShell;
        SHTN N 1;
        SHTN O 1;
        SHTN P 1;
        SHTN Q 1;
        SHTN R 1 A_Shotgun_FinishRack;
        Stop;

    RackReturn:
        SHTN G 1;
        SHTN F 1;
        SHTN E 1;
        SHTN D 1;
        SHTN C 1;
        SHTN B 1;
        SHTN A 1;
        Goto Ready;
    }
}