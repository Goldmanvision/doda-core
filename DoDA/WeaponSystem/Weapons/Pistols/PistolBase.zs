///////////////////////////
// DoDA/WeaponSystem/Weapons/Pistols/PistolBase.zs
///////////////////////////

class DoDAPistol : DoDAWeapon
{
    const MagazineCapacity = 15;

    bool adsActive;

    DoDADetachableMagState magState;

    bool reloadQueued;
    bool reloadInProgress;

    Default
    {
        Weapon.Kickback 100;
        Weapon.SlotNumber 2;
        +WEAPON.NOAUTOFIRE;

        Tag "DoDA Pistol Base";
        Inventory.PickupMessage "Picked up the DoDA Pistol";
    }

    void EnsureFirearmState()
    {
        magState.Initialize(MagazineCapacity, true);
    }

    Ammo GetReserveAmmo()
    {
        if (owner == null)
        {
            return null;
        }

        return Ammo(owner.FindInventory('Clip'));
    }

    bool IsADSActive()
    {
        return adsActive;
    }

    void SetADSActive(bool active)
    {
        adsActive = active;
    }

    clearscope bool UsesWeaponHUD()
    {
        return true;
    }

    clearscope String GetHUDWeaponLabel()
    {
        return "B92";
    }

    clearscope int GetMagazineRounds()
    {
        return magState.magazineRounds;
    }

    clearscope int GetMagazineCapacity()
    {
        return MagazineCapacity;
    }

    clearscope bool IsChamberLoaded()
    {
        return magState.chamberLoaded;
    }

    bool IsEmpty()
    {
        EnsureFirearmState();
        return magState.IsEmpty();
    }

    bool CanReload()
    {
        EnsureFirearmState();

        let reserveAmmo = GetReserveAmmo();
        int reserveCount = (reserveAmmo != null) ? reserveAmmo.Amount : 0;

        return magState.CanReload(MagazineCapacity, reserveCount);
    }

    bool TryReload()
    {
        return CommitReload();
    }

    clearscope int GetReserveRounds()
    {
        if (owner == null)
        {
            return 0;
        }

        let reserveAmmo = Ammo(owner.FindInventory('Clip'));

        return reserveAmmo != null
            ? reserveAmmo.Amount
            : 0;
    }

    int GetLoadedRoundCount()
    {
        EnsureFirearmState();
        return magState.GetLoadedRoundCount();
    }

    bool IsFullyLoaded()
    {
        EnsureFirearmState();
        return magState.magazineRounds >= MagazineCapacity && magState.chamberLoaded;
    }

    bool NeedsReload()
    {
        return !IsFullyLoaded();
    }

    bool CanFireRound()
    {
        EnsureFirearmState();
        return magState.CanFireRound();
    }

    bool ConsumeFiredRound()
    {
        EnsureFirearmState();
        return magState.ConsumeFiredRound();
    }

    void QueueReload()
    {
        if (CanReload())
        {
            reloadQueued = true;
        }
    }

    bool IsReloadQueued()
    {
        return reloadQueued;
    }

    void ClearReloadQueue()
    {
        reloadQueued = false;
        reloadInProgress = false;
    }

    bool CommitReload()
    {
        EnsureFirearmState();

        if (!CanReload())
        {
            return false;
        }

        let reserveAmmo = GetReserveAmmo();

        if (reserveAmmo == null)
        {
            return false;
        }

        return magState.CommitReplacementReload(MagazineCapacity, reserveAmmo.Amount);
    }

    action void DoDA_PlayFireSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        int soundVariant = Random(1, 3);

        if (soundVariant == 1)
        {
            invoker.owner.A_StartSound(
                "doda/pistol/fire1",
                CHAN_WEAPON
            );
        }
        else if (soundVariant == 2)
        {
            invoker.owner.A_StartSound(
                "doda/pistol/fire2",
                CHAN_WEAPON
            );
        }
        else
        {
            invoker.owner.A_StartSound(
                "doda/pistol/fire3",
                CHAN_WEAPON
            );
        }
    }

    action void DoDA_PlayDryFireSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/pistol/dryfire",
            CHAN_BODY
        );
    }

    action void DoDA_PlayMagazineEjectSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/pistol/mag_eject",
            CHAN_BODY
        );
    }

    action void DoDA_PlayMagazineLoadSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/pistol/mag_load",
            CHAN_BODY
        );
    }

    action void DoDA_PlaySlideSound()
    {
        if (invoker == null || invoker.owner == null)
        {
            return;
        }

        A_StartSound(
            "doda/pistol/slide",
            CHAN_BODY
        );
    }

    action void DoDA_BeginReload()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol == null || !pistol.reloadQueued || !pistol.CanReload())
        {
            if (invoker != null)
            {
                invoker.SetStateLabel("Ready");
            }

            return;
        }

        pistol.reloadQueued = false;
        pistol.reloadInProgress = true;
    }

    action State A_DoDA_Ready()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol && !pistol.IsChamberLoaded())
        {
            return ResolveState("ReadyEmpty");
        }

        int readyFlags = WRF_ALLOWZOOM | WRF_NOSECONDARY;
        if (DoDA.IsAkimboActive())
        {
            readyFlags |= WRF_NOBOB | WRF_NOPRIMARY;
        }

        A_WeaponReady(readyFlags);
        return null;
    }

    action State A_DoDA_Fire()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol && !pistol.IsChamberLoaded())
        {
            return ResolveState("DryFire");
        }

        return null;
    }

    action void DoDA_CommitReload()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol == null || !pistol.reloadInProgress)
        {
            return;
        }

        pistol.CommitReload();
        pistol.reloadInProgress = false;
        if (DoDA.IsAkimboActive())
        {
            DoDA.SetReloadLock(false);
        }
    }

    action State A_DoDA_SecondaryReady()
    {
        let pistol = DoDAPistol(invoker);
        if (pistol && !pistol.IsChamberLoaded())
        {
            return ResolveState("SecondaryReadyEmpty");
        }
        return null;
    }

    action State A_DoDA_SecondaryFire()
    {
        let pistol = DoDAPistol(invoker);
        if (pistol && !pistol.IsChamberLoaded())
        {
            return ResolveState("SecondaryDryFire");
        }
        return null;
    }

    action void DoDA_BeginSecondaryReload()
    {
        let pistol = DoDAPistol(invoker);
        if (pistol != null)
        {
            pistol.reloadInProgress = true;
            DoDA.SetReloadLock(true);
        }
    }

    action void DoDA_CommitSecondaryReload()
    {
        let pistol = DoDAPistol(invoker);
        if (pistol != null)
        {
            pistol.CommitReload();
            pistol.reloadInProgress = false;
            DoDA.SetReloadLock(false);
        }
    }

    override int GetWeaponHand()
    {
        return DoDAHandSwapController.Hand_Right;
    }

    Weapon GetOppositeHandWeapon()
    {
        if (owner == null)
        {
            return null;
        }

        if (GetWeaponHand() == DoDAHandSwapController.Hand_Left)
        {
            return Weapon(owner.FindInventory('DoDAB92Right'));
        }

        return Weapon(owner.FindInventory('DoDAB92Left'));
    }

    bool RequestHandSwap(
        int requestedHand,
        bool isManualRequest = false
    )
    {
        if (owner == null || owner.player == null)
        {
            return false;
        }

        if (
            !isManualRequest
            && handSwapController
            && handSwapController.IsPistolSwapLocked()
        )
        {
            return false;
        }

        if (requestedHand == GetWeaponHand())
        {
            return false;
        }

        if (owner.player.ReadyWeapon != self)
        {
            return false;
        }

        if (owner.player.PendingWeapon != WP_NOCHANGE)
        {
            return false;
        }

        Weapon targetWeapon = GetOppositeHandWeapon();

        if (targetWeapon == null)
        {
            return false;
        }

        owner.player.PendingWeapon = targetWeapon;
        return true;
    }

    override void Tick()
    {
        Super.Tick();
        EnsureFirearmState();
    }
}