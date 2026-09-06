/*//////////////////////////|
// DoDA/MissionSystem/MissionDefs.zs
*///////////////////////////|

class DoDAMissionDef : Object
{
    EDoDAMissionId MissionId;
    EDoDAObjectiveId ObjectiveId;
    String MissionNameKey;
    String ObjectiveKey;
    String FieldMap;
}

class DoDAMissionDefs : Object
{
    static DoDAMissionDef CreateDef(
        EDoDAMissionId missionId,
        EDoDAObjectiveId objectiveId,
        String missionNameKey,
        String objectiveKey,
        String fieldMap
    )
    {
        DoDAMissionDef def = new("DoDAMissionDef");
        def.MissionId = missionId;
        def.ObjectiveId = objectiveId;
        def.MissionNameKey = missionNameKey;
        def.ObjectiveKey = objectiveKey;
        def.FieldMap = fieldMap;
        return def;
    }

    static DoDAMissionDef GetDef(EDoDAMissionId missionId)
    {
        switch (missionId)
        {
        case DMDMission01:
            return CreateDef(
                DMDMission01,
                DODInformant,
                "DODA_MISSION_01_NAME",
                "DODA_MISSION_01_OBJECTIVE",
                "MAP01"
            );

        case DMDMission02:
            return CreateDef(
                DMDMission02,
                DODTerminal,
                "DODA_MISSION_02_NAME",
                "DODA_MISSION_02_OBJECTIVE",
                "MAP01"
            );

        case DMDMission03:
            return CreateDef(
                DMDMission03,
                DODInformant,
                "DODA_MISSION_03_NAME",
                "DODA_MISSION_03_OBJECTIVE",
                "MAP03"
            );
        }

        return null;
    }

    static DoDAMissionDef GetDefForIndex(int missionIndex)
    {
        switch (missionIndex)
        {
        case 0:
            return GetDef(DMDMission01);

        case 1:
            return GetDef(DMDMission02);

        case 2:
            return GetDef(DMDMission03);
        }

        return null;
    }

    static bool IsObjectiveActive(
        int missionIndex,
        EDoDAObjectiveId objectiveId,
        String mapName
    )
    {
        DoDAMissionDef missionDef = GetDefForIndex(missionIndex);

        if (missionDef == null)
        {
            return false;
        }

        if (missionDef.ObjectiveId != objectiveId)
        {
            return false;
        }

        if (missionDef.FieldMap != mapName)
        {
            return false;
        }

        return true;
    }
}