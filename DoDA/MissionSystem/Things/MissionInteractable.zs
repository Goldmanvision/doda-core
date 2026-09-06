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
        Scale 0.4;

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

            Console.MidPrint(
                Font.GetFont("DoDAPalmFont"),
                "INFORMANT: We already spoke.",
                true
            );

            SetStateLabel("InformantAlreadyUsed");
            return false;
        }

        DoDACampaignState campaignState =
            DoDACampaignState(user.FindInventory("DoDACampaignState"));

        if (campaignState == null)
        {
            Console.Printf("DoDA: CampaignState missing during informant use.");
            return false;
        }

        int missionId = campaignState.NextMissionIndex;

        if (!DoDAMissionDefs.IsObjectiveActive(
            missionId,
            DODInformant,
            level.MapName
        ))
        {
            Console.Printf(
                "DoDA: Informant inactive. Map=%s MissionId=%d",
                level.MapName,
                missionId
            );

            Console.MidPrint(
                Font.GetFont("DoDAPalmFont"),
                "$DODA_INACTIVE_OBJECTIVE",
                true
            );

            return false;
        }

        DoDAMissionDirector director = DoDAMissionDirector(
            EventHandler.Find("DoDAMissionDirector")
        );

        if (director == null)
        {
            Console.Printf("DoDA: MissionDirector not found during informant use.");
            return false;
        }

        HasBeenUsed = true;

        Console.Printf("DoDA: Informant used.");

        Console.MidPrint(
            Font.GetFont("DoDAPalmFont"),
            "INFORMANT: I have what you need.",
            true
        );

        SetStateLabel("InformantUsed");
        director.CompleteMission();

        return true;
    }

    States
    {
    Spawn:
    InformantIdle:
        DSUI P 100;
        DSUI B 100;
        DSUI C 20;
        DSUI D 10;
        DSUI E 100;
        DSUI C 10;
        DSUI D 20;
        DSUI F 100;
        DSUI C 10;
        DSUI D 20;
        Loop;

    InformantUsed:
        DSUI L 10;
        DSUI A 5;
        DSUI P 10;
        DSUI A 5;
        DSUI I 20;
        DSUI K -1;
        Stop;

    InformantAlreadyUsed:
        DSUI J 100;
        DSUI K -1;
        Stop;
    }
}