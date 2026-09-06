class DoDAAmmoDispenser : Actor
{
    Default
    {
        Radius 16;
        Height 32;
        +SOLID;
        +USESPECIAL;
    }

    States
    {
    Spawn:
        TNT1 A -1;
        Stop;
    }

    override bool Used(Actor user)
    {
        if (user.player)
        {
            user.GiveInventory("Clip", 15);
            return true;
        }
        return false;
    }
}
