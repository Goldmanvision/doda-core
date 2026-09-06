/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionTerminal.zs
*///////////////////////////|*/

class DoDAMissionTerminal : Actor
{
    bool Activated;

    Default
    {
        Radius 8;
        Height 8;
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

        DoDACampaignState campaignState =
            DoDACampaignState(user.FindInventory("DoDACampaignState"));

        if (campaignState == null)
        {
            Console.Printf("DoDA: CampaignState missing during terminal use.");
            return false;
        }

        int missionId = campaignState.NextMissionIndex;

        if (!DoDAMissionDefs.IsObjectiveActive(
            missionId,
            DODTerminal,
            level.MapName
        ))
        {
            Console.Printf(
                "DoDA: Terminal inactive for mission index %d.",
                missionId
            );

            Console.MidPrint(
                Font.GetFont("DoDAPalmFont"),
                "$DODA_TERMINAL_INACTIVE",
                true
            );

            return false;
        }

        if (Activated)
        {
            Console.Printf("DoDA: Terminal already used.");
            SetStateLabel("Activated");
            return false;
        }

        DoDAMissionDirector director =
            DoDAMissionDirector(EventHandler.Find("DoDAMissionDirector"));

        if (director == null)
        {
            Console.Printf("DoDA: MissionDirector not found during terminal use.");
            return false;
        }

        Activated = true;

        Console.Printf("DoDA: Mission terminal used.");
        SetStateLabel("Activated");
        director.CompleteMission();

        return true;
    }

    States
    {
    Spawn:
    Idle:
        DCSV K 4;
        DCSV L 4;
        DCSV M 4;
        DCSV N 4;
        DCSV O 4;
        DCSV P 4;
        DCSV Q 4;
        DCSV R 4;
        DCSV S 4;
        DCSV T 4;
        DCSV U 4;
        DCSV V 4;
        DCSV W 4;
        DCSV X 4;
        DCSV Y 4;
        DCSV Z 4;
        DCSW A 4;
        DCSW B 4;
        DCSW C 4;
        DCSW D 4;
        DCSW E 4;
        DCSW F 4;
        DCSW G 4;
        DCSW H 4;
        DCSW I 4;
        DCSW J 4;
        DCSW K 4;
        DCSW L 4;
        Loop;

    Activated:
        DCSR A -1;
        Stop;
    }
}