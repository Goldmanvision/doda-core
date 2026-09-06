/*//////////////////////////|
// DoDA/MissionSystem/CampaignState.zs
*///////////////////////////|*/

class DoDACampaignState : Inventory
{
    int NextMissionIndex;

    int ObjectivePickupCount;
    int ObjectivePickupRequired;

    int ObservedObjectivePickupMarkerCount;
    int ObservedMissionPickupMarkerCount;

    DoDAEvidenceLedger EvidenceLedger;

    bool WasLoggedThisMap;

    Default
    {
        Inventory.Amount 1;
        Inventory.MaxAmount 1;

        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNCLEARABLE;
    }

    override void Tick()
    {
        Super.Tick();

        if (Owner == null)
        {
            return;
        }

        ProcessObjectivePickupMarkers();
        ProcessMissionPickupMarkers();

        if (WasLoggedThisMap)
        {
            return;
        }

        WasLoggedThisMap = true;

        Console.Printf(
            "DoDA CampaignState observed: Map=%s NextMissionIndex=%d OwnerClass=%s ObjectiveCount=%d ObjectiveRequired=%d ObjectiveMarkers=%d MissionMarkers=%d",
            level.MapName,
            NextMissionIndex,
            Owner.GetClassName(),
            ObjectivePickupCount,
            ObjectivePickupRequired,
            ObservedObjectivePickupMarkerCount,
            ObservedMissionPickupMarkerCount
        );
    }

    void ProcessObjectivePickupMarkers()
    {
        DoDAObjectivePickupMarker marker =
            DoDAObjectivePickupMarker(
                Owner.FindInventory("DoDAObjectivePickupMarker")
            );

        if (marker == null)
        {
            return;
        }

        while (ObservedObjectivePickupMarkerCount < marker.Amount)
        {
            ObservedObjectivePickupMarkerCount =
                ObservedObjectivePickupMarkerCount + 1;

            RecordObjectivePickup();
        }
    }

    void ProcessMissionPickupMarkers()
    {
        DoDAMissionPickupMarker marker =
            DoDAMissionPickupMarker(
                Owner.FindInventory("DoDAMissionPickupMarker")
            );

        if (marker == null)
        {
            return;
        }

        while (ObservedMissionPickupMarkerCount < marker.Amount)
        {
            ObservedMissionPickupMarkerCount =
                ObservedMissionPickupMarkerCount + 1;

            if (!CanCompleteCurrentObjective())
            {
                Console.Printf(
                    "DoDA: Mission pickup recorded, but objective threshold is not met."
                );

                continue;
            }

            DoDAMissionDirector director =
                DoDAMissionDirector(
                    EventHandler.Find("DoDAMissionDirector")
                );

            if (director == null)
            {
                Console.Printf(
                    "DoDA: Mission pickup recorded, but MissionDirector is unavailable."
                );

                continue;
            }

            if (director.GetMissionPercentComplete() >= 100)
            {
                Console.Printf(
                    "DoDA: Mission pickup ignored because mission is already complete."
                );

                continue;
            }

            ConsumeObjectiveProgress();
            director.CompleteMission();

            Console.Printf(
                "DoDA: Mission objective completed by mission pickup."
            );
        }
    }

    void MarkMapSeen()
    {
        WasLoggedThisMap = false;
    }

    clearscope int GetNextMissionIndex()
    {
        return NextMissionIndex;
    }

    clearscope int GetObjectivePickupCount()
    {
        return ObjectivePickupCount;
    }

    clearscope int GetObjectivePickupRequired()
    {
        return ObjectivePickupRequired;
    }

    clearscope bool CanCompleteCurrentObjective()
    {
        return ObjectivePickupCount >= ObjectivePickupRequired;
    }

    void EnsureInitialized()
    {
        if (ObjectivePickupRequired < 1)
        {
            ObjectivePickupRequired = 1;
        }

        Console.Printf(
            "DoDA CampaignState initialized: Map=%s NextMissionIndex=%d ObjectiveCount=%d ObjectiveRequired=%d",
            level.MapName,
            NextMissionIndex,
            ObjectivePickupCount,
            ObjectivePickupRequired
        );
    }

    void RecordObjectivePickup()
    {
        ObjectivePickupCount = ObjectivePickupCount + 1;

        Console.Printf(
            "DoDA CampaignState objective pickup recorded: Count=%d Required=%d",
            ObjectivePickupCount,
            ObjectivePickupRequired
        );
    }

    void ConsumeObjectiveProgress()
    {
        ObjectivePickupCount = 0;

        Console.Printf(
            "DoDA CampaignState objective progress consumed: Count=%d Required=%d",
            ObjectivePickupCount,
            ObjectivePickupRequired
        );
    }

    void AdvanceToNextMission()
    {
        NextMissionIndex = NextMissionIndex + 1;

        ObjectivePickupCount = 0;
        ObjectivePickupRequired = 1;

        WasLoggedThisMap = false;

        Console.Printf(
            "DoDA CampaignState advanced: Map=%s NextMissionIndex=%d ObjectiveCount=%d ObjectiveRequired=%d",
            level.MapName,
            NextMissionIndex,
            ObjectivePickupCount,
            ObjectivePickupRequired
        );
    }
}