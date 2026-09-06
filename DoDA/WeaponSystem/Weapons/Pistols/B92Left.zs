///////////////////////////
// DoDA/WeaponSystem/Weapons/Pistols/B92Left.zs
///////////////////////////

class DoDAB92Left : DoDAPistol
{
    override int GetWeaponHand()
    {
        return DoDAHandSwapController.Hand_Left;
    }

    action State A_DoDA_Ready()
    {
        let pistol = DoDAPistol(invoker);

        if (pistol && !pistol.chamberLoaded)
        {
            return ResolveState("ReadyEmpty");
        }

        A_WeaponReady(WRF_ALLOWZOOM | WRF_NOSECONDARY);
        return null;
    }

    States
    {
    Spawn:
        B92L T -1;
        Stop;

    // Reload is controlled by DoDAWeapon.RequestLowestLoadedPistolReload().
    // Do not add WRF_ALLOWRELOAD here: native reload would bypass DoDA's
    // lowest-loaded-pistol selection and full-magazine validation.
    Ready:
        B92L G 1 A_DoDA_Ready;
        Loop;

    ReadyEmpty:
        B92L D 1 A_WeaponReady(WRF_NOFIRE | WRF_ALLOWZOOM);
        Loop;

    AltFire:
        Goto Ready;

    // Magazine eject sound occurs at the start of the reload motion.
    // Magazine load sound and ammo transfer occur at B92LE0.
    // Slide sound occurs after the reload has completed.
    Reload:
        R92L A 2 DoDA_BeginReload;
        R92L B 2;
        R92L C 2 DoDA_PlayMagazineEjectSound;
        R92L D 2;
        R92L E 2;
        R92L F 2;
        R92L G 2;
        R92L H 2;
        R92L I 2;
        R92L J 2;
        R92L K 2;
        R92L L 2;
        B92L D 2;
        B92L E 2 DoDA_PlayMagazineLoadSound;
        B92L E 0 DoDA_CommitReload;
        B92L F 2;
        B92L G 2 DoDA_PlaySlideSound;
        Goto Ready;

    Deselect:
        B92L G 0 A_Lower;
        B92L G 0 A_Lower;
        B92L G 1 A_Lower;
        Loop;

    Select:
        B92L G 0 A_Raise;
        B92L G 0 A_Raise;
        B92L G 1 A_Raise;
        Loop;

    Fire:
        B92L G 1 A_DoDA_Fire;
        B92L B 1 Bright DoDA_FireTrace;
        B92L B 0 Bright DoDA_SpawnPistolCasing();
        B92L A 1 Bright;
        B92L C 1;
        B92L D 1;
        B92L E 1;
        B92L F 1;
        Goto Ready;

    DryFire:
        TNT1 A 0 DoDA_PlayDryFireSound;
        B92L D -1;
        Goto ReadyEmpty;

    }
}