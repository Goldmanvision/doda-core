class DoDAMP5KSD : DoDAWeapon
{
    const MagazineCapacity = 30;
    const TotalCapacity = 31;

    const Fire_Semi = 0;
    const Fire_Burst = 1;
    const Fire_Auto = 2;

    int magazineRounds;
    bool chamberLoaded;
    bool mp5Initialized;

    int fireMode;
    int burstShotsRemaining;
    bool burstInProgress;

    bool isReloading;
    bool reloadWasEmpty;
    bool wasMP5AttackHeld;

    Default
    {
        Weapon.SelectionOrder 700;
        Weapon.SlotNumber 4;
        Weapon.AmmoType "Clip";
        Weapon.AmmoUse 0;
        Weapon.AmmoGive 30;

        Inventory.PickupMessage "You got the MP5kSD";
        Obituary "%o was mowed down by %k's MP5kSD.";
        Tag "MP5kSD";

        +WEAPON.NOAUTOFIRE;
        +WEAPON.NOAUTOAIM;
        +WEAPON.NOALERT;
    }

    override bool ShouldStartFire(bool holdingFire, bool firePressed)
    {
        if (fireMode == Fire_Auto)
        {
            return holdingFire;
        }

        return firePressed;
    }

    override bool UsesManualFireDispatch()
    {
        return true;
    }

    override bool IsMP5Weapon()
    {
        return true;
    }

    override State GetFireState(bool holdingFire, bool firePressed)
    {
        if (isReloading || burstInProgress)
        {
            return null;
        }

        if (IsEmpty())
        {
            return ResolveState("DryFire");
        }

        if (fireMode == Fire_Burst)
        {
            State burstState = ResolveState("BurstFire");

            if (burstState == null)
            {
                burstShotsRemaining = 0;
                burstInProgress = false;
                return null;
            }

            burstShotsRemaining = Min(3, GetLoadedRoundCount());
            burstInProgress = true;
            return burstState;
        }

        return ResolveState("Fire");
    }

    override void Tick()
    {
        Super.Tick();
        EnsureFirearmState();

        if (!owner || !owner.player)
        {
            return;
        }

        if (owner.player.ReadyWeapon != self)
        {
            burstShotsRemaining = 0;
            burstInProgress = false;
            isReloading = false;
            wasMP5AttackHeld = false;
            return;
        }

        bool attackDown = (owner.player.cmd.buttons & BT_ATTACK) != 0;
        wasMP5AttackHeld = attackDown;
    }

    clearscope int GetFireMode()
    {
        return fireMode;
    }

    void CycleFireMode()
    {
        fireMode = (fireMode + 1) % 3;

        A_StartSound("doda/mp5/click", CHAN_WEAPON);
    }

    void EnsureFirearmState()
    {
        if (mp5Initialized)
        {
            return;
        }

        magazineRounds = MagazineCapacity;
        chamberLoaded = true;
        mp5Initialized = true;
    }

    clearscope int GetMagazineRoundCount()
    {
        return magazineRounds;
    }

    clearscope int GetMagazineCapacity()
    {
        return MagazineCapacity;
    }

    clearscope bool IsChamberLoaded()
    {
        return chamberLoaded;
    }

    clearscope int GetLoadedRoundCount()
    {
        return magazineRounds + (chamberLoaded ? 1 : 0);
    }

    clearscope bool IsEmpty()
    {
        return !chamberLoaded && magazineRounds == 0;
    }

    bool CanReload()
    {
        if (!owner)
        {
            return false;
        }

        let reserveAmmo = Ammo(owner.FindInventory("Clip"));

        return GetLoadedRoundCount() < TotalCapacity
            && reserveAmmo != null
            && reserveAmmo.Amount > 0;
    }

    void TryReload()
    {
        if (isReloading || burstInProgress)
        {
            return;
        }

        if (magazineRounds >= MagazineCapacity)
        {
            return;
        }

        if (!owner || !owner.player)
        {
            return;
        }

        let reserveAmmo = Ammo(owner.FindInventory("Clip"));

        if (!reserveAmmo || reserveAmmo.Amount <= 0)
        {
            return;
        }

        reloadWasEmpty = IsEmpty();

        State reloadState = reloadWasEmpty
            ? ResolveState("ReloadEmpty")
            : ResolveState("ReloadTactical");

        if (!reloadState)
        {
            return;
        }

        isReloading = true;
        owner.player.SetPSprite(PSP_WEAPON, reloadState);
    }

    void PerformReloadTransfer()
    {
        if (!owner)
        {
            return;
        }

        let reserveAmmo = Ammo(owner.FindInventory("Clip"));

        if (!reserveAmmo)
        {
            return;
        }

        int amount = Min(
            MagazineCapacity - magazineRounds,
            reserveAmmo.Amount
        );

        magazineRounds += amount;
        reserveAmmo.Amount -= amount;
    }

    bool ConsumeFiredRound()
    {
        if (!chamberLoaded)
        {
            return false;
        }

        chamberLoaded = false;

        if (magazineRounds > 0)
        {
            magazineRounds--;
            chamberLoaded = true;
        }

        return true;
    }

    void LoadChamberFromMagazine()
    {
        if (!chamberLoaded && magazineRounds > 0)
        {
            magazineRounds--;
            chamberLoaded = true;
        }
    }

    bool CanCock()
    {
        return !chamberLoaded && magazineRounds > 0;
    }

    override void HandleManualWeaponControl()
    {
        if (!owner || !owner.player)
        {
            return;
        }

        if (isReloading || burstInProgress)
        {
            return;
        }

        if (
            InStateSequence(curstate, ResolveState("Fire"))
            || InStateSequence(curstate, ResolveState("BurstFire"))
            || InStateSequence(curstate, ResolveState("ReloadTactical"))
            || InStateSequence(curstate, ResolveState("ReloadEmpty"))
            || InStateSequence(curstate, ResolveState("Cock"))
        )
        {
            return;
        }

        if (CanCock())
        {
            SetStateLabel("Cock");
        }
    }

    void FireDeadzoneAwareTrace()
    {
        if (
            owner == null
            || owner.player == null
            || owner.health <= 0
            || owner.player.mo == null
        )
        {
            return;
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

        double fireYaw = owner.angle + yawOffset;
        double firePitch = owner.pitch + pitchOffset;

        double attackZ =
            owner.height * 0.5
            - owner.floorclip
            + owner.player.mo.AttackZOffset
                * owner.player.crouchFactor;

        double leanOffset = leanController != null
            ? leanController.GetAppliedOffset()
            : 0.0;

        FLineTraceData trace;

        bool hit = owner.LineTrace(
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

        trace.HitActor.DamageMobj(
            owner,
            owner,
            10,
            'Hitscan'
        );

        Spawn("BulletPuff", trace.HitLocation);
    }

    void SpawnDeadzoneAwareTracer()
    {
        if (owner == null || owner.player == null || owner.player.mo == null)
        {
            return;
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

        double attackZ =
            owner.height * 0.5
            - owner.floorclip
            + owner.player.mo.AttackZOffset
                * owner.player.crouchFactor;

        double leanOffset = leanController != null
            ? leanController.GetAppliedOffset()
            : 0.0;

        double firePitch = owner.pitch + pitchOffset;

        A_SpawnProjectile(
            "DoDATracer",
            attackZ,
            leanOffset,
            yawOffset,
            CMF_AIMDIRECTION | CMF_SAVEPITCH,
            firePitch
        );
    }

    action void MP5KSD_Fire()
    {
        let mp5 = DoDAMP5KSD(invoker);

        if (!mp5 || !mp5.ConsumeFiredRound())
        {
            return;
        }

        mp5.FireDeadzoneAwareTrace();
        A_StartSound("doda/mp5/fire", CHAN_WEAPON);
        mp5.SpawnDeadzoneAwareTracer();

        mp5.fireLockTics = 4;
    }

    action void MP5KSD_BurstFire()
    {
        let mp5 = DoDAMP5KSD(invoker);

        if (!mp5)
        {
            return;
        }

        if (mp5.burstShotsRemaining <= 0)
        {
            return;
        }

        if (!mp5.ConsumeFiredRound())
        {
            mp5.burstShotsRemaining = 0;
            return;
        }

        mp5.FireDeadzoneAwareTrace();
        A_StartSound("doda/mp5/fire", CHAN_WEAPON);
        mp5.SpawnDeadzoneAwareTracer();

        mp5.fireLockTics = 4;
        mp5.burstShotsRemaining--;
    }

    States
    {
    Spawn:
        MP5G A -1;
        Stop;

    Ready:
        MP5A A 1 A_WeaponReady(WRF_ALLOWZOOM | WRF_NOFIRE);
        Loop;

    Select:
        MP5A A 1 A_Raise;
        Loop;

    Deselect:
        MP5A A 1
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.burstShotsRemaining = 0;
                mp5.burstInProgress = false;
                mp5.isReloading = false;
                mp5.wasMP5AttackHeld = false;
            }

            A_Lower();
        }
        Loop;

    Fire:
        MP5A A 1 Bright MP5KSD_Fire;
        MP5A B 1;
        MP5A C 1;
        MP5A D 1;
        Goto Ready;

    BurstFire:
        MP5A A 1 Bright MP5KSD_BurstFire;
        MP5A B 1;
        MP5A C 1;
        MP5A D 1;

        MP5A A 1 Bright MP5KSD_BurstFire;
        MP5A B 1;
        MP5A C 1;
        MP5A D 1;

        MP5A A 1 Bright MP5KSD_BurstFire;
        MP5A B 1;
        MP5A C 1;
        MP5A D 1;

        TNT1 A 0
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.burstShotsRemaining = 0;
                mp5.burstInProgress = false;
            }
        }
        Goto Ready;

    DryFire:
        MP5R A 1 A_StartSound("doda/mp5/dryfire", CHAN_WEAPON);
        Goto Ready;

    ReloadTactical:
        MP5R A 2;
        MP5R B 2;
        MP5R C 2;
        MP5R D 2 A_StartSound("doda/mp5/open", CHAN_WEAPON);
        MP5R E 2;
        MP5R F 2;
        MP5R G 2;
        MP5R H 2;
        MP5R I 2;
        MP5R J 2
        {
            A_StartSound("doda/mp5/close", CHAN_WEAPON);

            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.PerformReloadTransfer();
            }
        }
        TNT1 A 0
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.isReloading = false;
            }
        }
        Goto Ready;

    ReloadEmpty:
        MP5R A 2;
        MP5R B 2;
        MP5R C 2;
        MP5R D 2 A_StartSound("doda/mp5/open", CHAN_WEAPON);
        MP5R E 2;
        MP5R F 2;
        MP5R G 2;
        MP5R H 2;
        MP5R I 2;
        MP5R J 2
        {
            A_StartSound("doda/mp5/close", CHAN_WEAPON);

            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.PerformReloadTransfer();
            }
        }
        MPSL A 2 A_StartSound("doda/mp5/cock", CHAN_WEAPON);
        MPSL B 2;
        MPSL C 2;
        MPSL D 2;
        MPSL E 2
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.LoadChamberFromMagazine();
            }
        }
        MPSL F 2;
        TNT1 A 0
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.isReloading = false;
            }
        }
        Goto Ready;

    Cock:
        MP5R A 5 A_StartSound("doda/mp5/cock", CHAN_WEAPON);
        MP5R A 5
        {
            let mp5 = DoDAMP5KSD(invoker);

            if (mp5)
            {
                mp5.LoadChamberFromMagazine();
            }
        }
        Goto Ready;
    }
}