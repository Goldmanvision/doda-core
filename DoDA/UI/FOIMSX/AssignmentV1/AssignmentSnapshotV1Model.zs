///////////////////////////
// DoDA/UI/FOIMSX/AssignmentV1/AssignmentSnapshotV1Model.zs
///////////////////////////

// Structured outcome of an assignment snapshot acquisition transaction.
enum EDoDAAssignmentAcquisitionState
{
    ASSIGNMENT_ACQUISITION_UNAVAILABLE,
    ACQUISITION_SUCCEEDED,
    ACQUISITION_UNSUPPORTED_VERSION,
    ACQUISITION_INVALID_COUNT,
    ACQUISITION_INVALID_ROW,
    ASSIGNMENT_ACQUISITION_REVISION_CHANGED,
    ASSIGNMENT_ACQUISITION_EMPTY,
    ASSIGNMENT_ACQUISITION_POPULATED
};

// Structured reason code for assignment candidate validation rejection.
enum EDoDAAssignmentValidationReason
{
    ASSIGNMENT_VALIDATION_NONE,
    VALIDATION_UNSUPPORTED_API_VERSION,
    VALIDATION_INVALID_REVISION_TOKEN,
    VALIDATION_INVALID_COUNT,
    VALIDATION_INVALID_ASSIGNMENT_ID,
    VALIDATION_INVALID_PERSON_ID,
    VALIDATION_INVALID_TASK_ID,
    VALIDATION_INVALID_LOCATION_ID,
    VALIDATION_MISSING_PERSON_DISPLAY_NAME,
    VALIDATION_MISSING_TASK_TITLE,
    VALIDATION_MISSING_LOCATION_DISPLAY_NAME,
    VALIDATION_INVALID_TASK_STATUS,
    VALIDATION_INVALID_TASK_PROGRESS,
    VALIDATION_INVALID_COST,
    VALIDATION_DUPLICATE_ASSIGNMENT_ID,
    ASSIGNMENT_VALIDATION_REVISION_CHANGED_DURING_ACQUISITION
};

// Pure data model for a single Assignment V1 record.
// Does not call native methods directly; AssignmentIdText is the canonical persistent key.
class DoDAAssignmentRecordV1 : Object
{
    String AssignmentIdText;
    String PersonIdText;
    String PersonDisplayName;
    String TaskIdText;
    String TaskTitle;
    String LocationIdText;
    String LocationDisplayName;
    int TaskStatus;
    int TaskProgress;
    int Cost;
}

// Pure data model representing a collection-level Assignment Snapshot V1.
// All metadata tokens are preserved as exact Strings without numeric parsing.
class DoDAAssignmentSnapshotV1 : Object
{
    int ApiVersion;
    String RevisionText;
    String StrategicMinutesText;
    int Count;
    Array<DoDAAssignmentRecordV1> Records;

    bool IsValid;
    EDoDAAssignmentAcquisitionState AcquisitionState;
    EDoDAAssignmentValidationReason ValidationReason;

    // Finds a record by its exact canonical persistent AssignmentIdText.
    DoDAAssignmentRecordV1 FindRecordById(String assignmentIdText) const
    {
        if (assignmentIdText == "")
        {
            return null;
        }

        for (int i = 0; i < Records.Size(); i++)
        {
            if (Records[i] != null && Records[i].AssignmentIdText == assignmentIdText)
            {
                return Records[i];
            }
        }
        return null;
    }

    // Returns record at display array index (for bounded iteration only).
    DoDAAssignmentRecordV1 GetRecordByIndex(int index) const
    {
        if (index >= 0 && index < Records.Size())
        {
            return Records[index];
        }
        return null;
    }

    // Clears all records and resets snapshot metadata to initial unacquired state.
    void Clear()
    {
        ApiVersion = 0;
        RevisionText = "";
        StrategicMinutesText = "";
        Count = 0;
        Records.Clear();
        IsValid = false;
        AcquisitionState = ASSIGNMENT_ACQUISITION_UNAVAILABLE;
        ValidationReason = ASSIGNMENT_VALIDATION_NONE;
    }
}
