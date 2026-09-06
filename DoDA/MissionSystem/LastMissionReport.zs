/*//////////////////////////|
// DoDA/MissionSystem/LastMissionReport.zs
*///////////////////////////|

class DoDALastMissionReport : Inventory
{
    bool HasReport;
    bool WasLoggedThisMap;

    DoDAMissionResult ReportResult;
    int ReportPercentComplete;
    int ReportPhase;
    string ReportMissionName;
    string ReportObjective;

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

        if (!HasReport)
        {
            return;
        }

        if (WasLoggedThisMap)
        {
            return;
        }

        WasLoggedThisMap = true;

        Console.Printf(
            "DoDA LastMissionReport observed: Map=%s Mission=%s Status=%d Progress=%d Phase=%d Objective=%s OwnerClass=%s",
            level.MapName,
            ReportMissionName,
            ReportResult,
            ReportPercentComplete,
            ReportPhase,
            ReportObjective,
            Owner.GetClassName()
        );
    }

    void StoreFromDirector(DoDAMissionDirector director)
    {
        if (director == null)
        {
            return;
        }

        HasReport = true;
        WasLoggedThisMap = false;

        ReportResult = director.GetMissionResult();
        ReportPercentComplete = director.GetMissionPercentComplete();
        ReportPhase = director.GetMissionPhase();
        ReportMissionName = director.GetMissionName();
        ReportObjective = director.GetMissionDescription();

        Console.Printf(
            "DoDA LastMissionReport stored: Map=%s Mission=%s Status=%d Progress=%d Phase=%d Objective=%s",
            level.MapName,
            ReportMissionName,
            ReportResult,
            ReportPercentComplete,
            ReportPhase,
            ReportObjective
        );
    }

    void ClearReport()
    {
        if (!HasReport)
        {
            Console.Printf("DoDA LastMissionReport clear requested, but no active report existed on Map=%s", level.MapName);
            return;
        }

        Console.Printf(
            "DoDA LastMissionReport cleared: Map=%s Mission=%s Status=%d Progress=%d Phase=%d Objective=%s",
            level.MapName,
            ReportMissionName,
            ReportResult,
            ReportPercentComplete,
            ReportPhase,
            ReportObjective
        );

        HasReport = false;
        WasLoggedThisMap = false;

        ReportResult = MISSION_UNKNOWN;
        ReportPercentComplete = 0;
        ReportPhase = 0;
        ReportMissionName = "";
        ReportObjective = "";
    }

    clearscope bool GetHasReport()
    {
        return HasReport;
    }

    clearscope DoDAMissionResult GetReportResult()
    {
        return ReportResult;
    }

    clearscope int GetReportPercentComplete()
    {
        return ReportPercentComplete;
    }

    clearscope int GetReportPhase()
    {
        return ReportPhase;
    }

    clearscope String GetReportMissionName()
    {
        return ReportMissionName;
    }

    clearscope String GetReportObjective()
    {
        return ReportObjective;
    }
}