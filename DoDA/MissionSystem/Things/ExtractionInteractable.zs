/*//////////////////////////|
// DoDA/MissionSystem/Things/ExtractionInteractable.zs
*///////////////////////////|*/

class DoDAExtractionInteractable : Actor
{
    Default
    {
        Radius 22;
        Height 32;

        +SOLID;
        +USESPECIAL;
    }

    override bool Used(Actor user)
    {
        if (user == null)
        {
            return false;
        }

        DoDAMissionDirector director =
            DoDAMissionDirector(EventHandler.Find("DoDAMissionDirector"));

        if (director == null)
        {
            Console.Printf("DoDA: Extraction denied. MissionDirector missing.");

            Console.MidPrint(
                Font.GetFont("DoDAPalmFont"),
                "$DODA_EXTRACTION_LOCKED",
                true
            );

            SetStateLabel("Locked");
            return false;
        }

        if (director.GetMissionResult() != MISSION_SUCCESS)
        {
            Console.Printf("DoDA: Extraction denied. Mission not complete.");

            Console.MidPrint(
                Font.GetFont("DoDAPalmFont"),
                "$DODA_EXTRACTION_LOCKED",
                true
            );

            SetStateLabel("Locked");
            return false;
        }

        Console.Printf("DoDA: Extraction authorized.");

        Console.MidPrint(
            Font.GetFont("DoDAPalmFont"),
            "$DODA_EXTRACTION_AUTHORIZED",
            true
        );

        SetStateLabel("Authorized");
        return true;
    }

    States
    {
    Spawn:
    Locked:
        DCAR A -1;
        Stop;

Authorized:
    DCAR B 35;
    Goto Exit;

Exit:
    DCAR B -1
    {
        level.ExitLevel(0, false);
    }
    Stop;
    }
}