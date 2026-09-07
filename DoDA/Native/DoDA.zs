struct DoDA native
{
    native static int GetNativeApiVersion();
    native static bool DebugResetFixture();
    native static bool DebugAdvanceMinutes(int delta);
    native static bool DebugRunAssignment();
    native static int GetStrategicMinutes();
    native static int GetPersonCount();
    native static int GetTaskCount();
    native static int GetAssignmentCount();
    native static String GetAssignmentDebugText(int index);
    native static int GetPersonnelSnapshotApiVersion();
    native static String GetPersonnelSnapshotRevisionText();
    native static String GetPersonnelSnapshotStrategicMinutesText();
    native static int GetPersonnelSnapshotCount();
    native static String GetPersonnelPersonIdText(int index);
    native static String GetPersonnelDisplayName(int index);
    native static int GetPersonnelStatus(int index);
    native static int GetPersonnelSkill(int index);
    native static int GetPersonnelWorkload(int index);
    native static String GetPersonnelCurrentAssignmentIdText(int index);
    native static String GetPersonnelCurrentTaskIdText(int index);
    native static String GetPersonnelCurrentTaskTitle(int index);

    // Location & Task Queries
    native static int GetLocationCount();
    native static String GetLocationIdText(int index);
    native static String GetLocationDisplayName(int index);
    native static String GetTaskIdText(int index);
    native static String GetTaskTitle(int index);
    native static int GetTaskStatus(int index);
    native static int GetTaskProgress(int index);
    native static String GetTaskLocationIdText(int index);
}