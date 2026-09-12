/*//////////////////////////|
// DoDA/MissionSystem/MissionManager.zs
*///////////////////////////|

// Deprecated compatibility wrapper: DoDAMissionDirector is the single authoritative
// live mission-state owner. DoDAMissionManager delegates all queries to MissionDirector.
class DoDAMissionManager : Object
{
    play void InitMission(int index, string name, string description)
    {
        Console.Printf("DoDA: Warning: DoDAMissionManager.InitMission is deprecated; DoDAMissionDirector owns live mission initialization.");
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        if (director != null)
        {
            director.ConfigureMissionForIndex(index);
        }
    }

    play void SetMissionResult(DoDAMissionResult result)
    {
        Console.Printf("DoDA: Warning: DoDAMissionManager.SetMissionResult is deprecated; DoDAMissionDirector owns live mission state.");
    }

    play void SetMissionProgress(int percent, int phase)
    {
        Console.Printf("DoDA: Warning: DoDAMissionManager.SetMissionProgress is deprecated; DoDAMissionDirector owns live mission state.");
    }

    clearscope DoDAMissionResult GetMissionResult()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionResult() : MISSION_UNKNOWN;
    }

    clearscope int GetMissionIndex()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionIndex() : 0;
    }

    clearscope int GetMissionPercentComplete()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionPercentComplete() : 0;
    }

    clearscope int GetMissionPhase()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionPhase() : 0;
    }

    clearscope string GetMissionName()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionName() : "";
    }

    clearscope string GetMissionDescription()
    {
        DoDAMissionDirector director = DoDAMissionDirector.GetInstance();
        return director != null ? director.GetMissionDescription() : "";
    }
}