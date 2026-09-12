/*//////////////////////////|
// DoDA/MissionSystem/MissionState.zs
*///////////////////////////|

enum DoDAMissionResult
{
    MISSION_UNKNOWN,
    MISSION_PENDING,
    MISSION_IN_PROGRESS,
    MISSION_SUCCESS,
    MISSION_FAILURE,
    MISSION_ABORTED
}

class DoDAMissionState : Object
{
    DoDAMissionResult Result;
    int Index;
    int PercentComplete;
    int Phase;
    String Name;
    String Description;

    static DoDAMissionState Create(
        DoDAMissionResult result = MISSION_UNKNOWN,
        int index = 0,
        int percent = 0,
        int phase = 0,
        String name = "",
        String description = ""
    )
    {
        DoDAMissionState mState = new("DoDAMissionState");
        mState.Result = result;
        mState.Index = index;
        mState.PercentComplete = percent;
        mState.Phase = phase;
        mState.Name = name;
        mState.Description = description;
        return mState;
    }
}