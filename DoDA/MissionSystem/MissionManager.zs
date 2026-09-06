/*//////////////////////////|
// DoDA/MissionSystem/MissionManager.zs
*///////////////////////////|

class DoDAMissionManager
{
    DoDAMissionResult MissionResult;
    int MissionIndex;
    int MissionPercentComplete;
    int MissionPhase;
    string MissionName;
    string MissionDescription;

    void InitMission(int index, string name, string description)
    {
        MissionResult = MISSION_PENDING;
        MissionIndex = index;
        MissionPercentComplete = 0;
        MissionPhase = 0;
        MissionName = name;
        MissionDescription = description;
    }

    void SetMissionResult(DoDAMissionResult result)
    {
        MissionResult = result;
    }

    void SetMissionProgress(int percent, int phase)
    {
        MissionPercentComplete = percent;
        MissionPhase = phase;
    }

    DoDAMissionResult GetMissionResult()
    {
        return MissionResult;
    }

    int GetMissionIndex()
    {
        return MissionIndex;
    }

    int GetMissionPercentComplete()
    {
        return MissionPercentComplete;
    }

    int GetMissionPhase()
    {
        return MissionPhase;
    }

    string GetMissionName()
    {
        return MissionName;
    }

    string GetMissionDescription()
    {
        return MissionDescription;
    }
}