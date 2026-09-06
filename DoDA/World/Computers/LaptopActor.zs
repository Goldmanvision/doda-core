/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionInteractable.zs
*///////////////////////////|*/

class DoDAMissionInteractable : Actor
{
    bool HasBeenUsed;

    Default
    {
        Radius 8;
        Height 28;
        Scale 0.5;

        +SOLID;
        +USESPECIAL;
    }

    override bool Used(Actor user)
    {
        if (user == null)
        {
            return false;
        }

        if (HasBeenUsed)
        {
            Console.Printf("DoDA: Informant already used.");
            return false;
        }

        HasBeenUsed = true;

        Console.Printf("DoDA: Informant visual interaction test passed.");

        Console.MidPrint(
            Font.GetFont("DoDAPalmFont"),
            "INFORMANT: I have what you need.",
            true
        );

        SetStateLabel("InformantUsed");
        return true;
    }

    States
    {
    Spawn:
    InformantIdle:
        DSUI A 6;
        DSUI B 6;
        DSUI C 6;
        DSUI D 6;
        DSUI E 6;
        DSUI F 6;
        DSUI I 6;
        DSUI J 6;
        Loop;

    InformantUsed:
        DSUI K 8;
        DSUI L 8;
        DSUI P -1;
        Stop;
    }
}