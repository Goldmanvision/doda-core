/*//////////////////////////|
// DoDA/MissionSystem/Things/DeployMissionInteractable.zs
*///////////////////////////|*/

class DoDADeployMissionInteractable : Actor
{
    bool Activated;
    String DeploymentMap;

    Default
    {
        Radius 8;
        Height 8;

        +SOLID;
        +USESPECIAL;
    }

    override bool Used(Actor user)
    {
        if (user == null)
        {
            return false;
        }

        if (Activated)
        {
            return false;
        }

        Activated = true;

        DoDALastMissionReport report =
            DoDALastMissionReport(user.FindInventory("DoDALastMissionReport"));

        if (report != null)
        {
            report.ClearReport();
        }
        else
        {
            Console.Printf(
                "DoDA: No LastMissionReport found to clear on return to field."
            );
        }

        DoDACampaignState campaignState =
            DoDACampaignState(user.FindInventory("DoDACampaignState"));

        if (campaignState == null)
        {
            user.GiveInventory("DoDACampaignState", 1);
            campaignState = DoDACampaignState(
                user.FindInventory("DoDACampaignState")
            );
        }

        if (campaignState != null)
        {
            campaignState.AdvanceToNextMission();

            if (campaignState.GetNextMissionIndex() == 2)
            {
                DeploymentMap = "MAP03";
            }
            else
            {
                DeploymentMap = "MAP01";
            }

            Console.Printf(
                "DoDA: Deployment destination selected: Index=%d Map=%s",
                campaignState.GetNextMissionIndex(),
                DeploymentMap
            );
        }
        else
        {
            DeploymentMap = "MAP01";

            Console.Printf("DoDA: CampaignState not found during mission advance.");
        }

        Console.Printf("DoDA: Returning to field.");

        Console.MidPrint(
            Font.GetFont("DoDAPalmFont"),
            "$DODA_RETURNING_TO_FIELD",
            true
        );

        SetStateLabel("Activated");
        return true;
    }

    States
    {
    Spawn:
    Idle:
        DLP1 A 4;
        DLP1 B 4;
        DLP1 C 4;
        DLP1 D 4;
        DLP1 E 4;
        DLP1 F 4;
        DLP1 G 4;
        DLP1 H 4;
        DLP1 I 4;
        DLP1 J 4;
        DLP1 K 4;
        DLP1 L 4;
        Loop;

    Activated:
        DLP2 A 3;
        DLP2 B 3;
        DLP2 C 3;
        DLP2 D 3;
        DLP2 E 3;
        DLP2 F 3;
        DLP2 G 3;
        DLP2 H 3;
        DLP2 I 3;
        DLP2 J 3;
        DLP2 K 3;
        DLP2 L 3;
        DLP2 M 3;
        DLP2 N 3;
        DLP2 O 8;
        DLPO A -1
        {
            level.ChangeLevel(DeploymentMap);
        }
        Stop;
    }
}