///////////////////////////
// DoDA/WeaponSystem/Weapons/Pistols/B92Right.zs
///////////////////////////

class DoDAB92Right : DoDAPistol
{
    override int GetWeaponHand()
    {
        return DoDAHandSwapController.Hand_Right;
    }

    action State A_DoDA_Ready()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol && !pistol.chamberLoaded)
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

    // The standard Reload state starts here. If no left-hand B92 exists in
    // the player's inventory, redirect immediately to the solo sequence.
    action state DoDA_SelectRightReloadAnimation()
    {
        let pistol = DoDAPistol(invoker);

        if (
            pistol == null
            || pistol.owner == null
            || pistol.owner.FindInventory('DoDAB92Left') == null
            || DoDA.IsAkimboActive()
        )
        {
            return ResolveState("ReloadSolo");
        }

        return null;
    }

    States
    {
    Spawn:
        B92R T -1;
        Stop;

    // Reload is controlled by DoDAWeapon.RequestLowestLoadedPistolReload().
    Ready:
        B92R G 1 A_DoDA_Ready;
        Loop;

    ReadyEmpty:
        B92R D 1 A_WeaponReady(WRF_NOFIRE | WRF_ALLOWZOOM);
        Loop;

    AltFire:
        Goto Ready;

    // Dual-Beretta reload. This runs only when the player owns DoDAB92Left.
    Reload:
        TNT1 A 0 DoDA_SelectRightReloadAnimation;
        R92R A 2 DoDA_BeginReload;
        R92R B 2;
        R92R C 2 DoDA_PlayMagazineEjectSound;
        R92R D 2;
        R92R E 2;
        R92R F 2;
        R92R G 2;
        R92R H 2;
        R92R I 2;
        R92R J 2;
        R92R K 2;
        R92R L 2;
        B92R D 2;
        B92R E 2 DoDA_PlayMagazineLoadSound;
        B92R E 0 DoDA_CommitReload;
        B92R F 2;
        B92R G 2 DoDA_PlaySlideSound;
        Goto Ready;

    // Solo-right Beretta reload. This runs only when the player does not
    // own DoDAB92Left. B92RE0 remains the magazine-seat/chamber moment.
    ReloadSolo:
        S92R A 2 DoDA_BeginReload;
        S92R B 2;
        S92R C 2 DoDA_PlayMagazineEjectSound;
        S92R D 2;
        S92R E 2;
        S92R F 2;
        S92R G 2;
        S92R H 2;
        S92R I 2;
        S92R J 2;
        S92R K 2;
        S92R L 2;
        B92R D 2;
        B92R E 2 DoDA_PlayMagazineLoadSound;
        B92R E 0 DoDA_CommitReload;
        B92R F 2;
        B92R G 2 DoDA_PlaySlideSound;
        Goto Ready;

    Deselect:
        B92R G 0 A_Lower;
        B92R G 0 A_Lower;
        B92R G 1 A_Lower;
        Loop;

    Select:
        B92R G 0 A_Raise;
        B92R G 0 A_Raise;
        B92R G 1 A_Raise;
        Loop;

    Fire:
        B92R G 1 A_DoDA_Fire;
        B92R A 1 Bright;
        B92R B 1 Bright DoDA_FireTrace;
        B92R B 0 Bright DoDA_SpawnPistolCasing();
        B92R C 1;
        B92R D 1;
        B92R E 1;
        B92R F 1;
        Goto Ready;

    DryFire:
        TNT1 A 0 DoDA_PlayDryFireSound;
        B92R D 2;
        Goto ReadyEmpty;

    }
}