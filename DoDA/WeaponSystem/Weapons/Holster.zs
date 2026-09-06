class DoDAHolster : Weapon
{
    Default
    {
        Weapon.SelectionOrder 0;
        Weapon.SlotNumber 1;
        +WEAPON.NOAUTOFIRE;
        +WEAPON.NOAUTOAIM;
    }

    States
    {
    Spawn:
        TNT1 A -1;
        Stop;

    Ready:
        TNT1 A 1 A_WeaponReady(WRF_NOFIRE);
        Loop;

    Select:
        TNT1 A 1 A_Raise;
        Loop;

    Deselect:
        TNT1 A 1 A_Lower;
        Loop;

    Fire:
        TNT1 A 0;
        Goto Ready;

    AltFire:
        TNT1 A 0;
        Goto Ready;
    }
}
