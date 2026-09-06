///////////////////////////
// DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Model.zs
///////////////////////////

// Structural classification of the Personnel V1 assignment triple
// (CurrentAssignmentIdText, CurrentTaskIdText, CurrentTaskTitle).
enum EDoDAPersonAssignmentClassification
{
    ASSIGNMENT_UNASSIGNED,
    ASSIGNMENT_ASSIGNED,
    ASSIGNMENT_INVALID
};

// Structured outcome of a snapshot acquisition transaction.
enum EDoDAPersonnelAcquisitionState
{
    ACQUISITION_UNAVAILABLE,
    ACQUISITION_INVALID_VERSION,
    ACQUISITION_INVALID_SNAPSHOT,
    ACQUISITION_REVISION_CHANGED,
    ACQUISITION_EMPTY,
    ACQUISITION_POPULATED
};

// Structured reason code for candidate validation rejection.
enum EDoDAPersonnelValidationReason
{
    VALIDATION_NONE,
    VALIDATION_INCOMPATIBLE_API_VERSION,
    VALIDATION_NEGATIVE_COUNT,
    VALIDATION_COUNT_SIZE_MISMATCH,
    VALIDATION_BLANK_PERSON_ID,
    VALIDATION_BLANK_DISPLAY_NAME,
    VALIDATION_DUPLICATE_PERSON_ID,
    VALIDATION_INVALID_STATUS_VALUE,
    VALIDATION_MIXED_ASSIGNMENT_TRIPLE,
    VALIDATION_REVISION_CHANGED_DURING_ACQUISITION
};

// Pure data model for a single Personnel V1 record.
// Does not call native methods directly; PersonIdText is the canonical persistent key.
class DoDAPersonRecordV1 : Object
{
    String PersonIdText;
    String DisplayName;
    int Status;
    int Skill;
    int Workload;
    String CurrentAssignmentIdText;
    String CurrentTaskIdText;
    String CurrentTaskTitle;

    // Evaluates structural classification from the complete V1 assignment triple.
    // Does not infer assignment from raw Status.
    EDoDAPersonAssignmentClassification GetAssignmentClassification() const
    {
        bool hasAssign = (CurrentAssignmentIdText != "");
        bool hasTask = (CurrentTaskIdText != "");
        bool hasTitle = (CurrentTaskTitle != "");

        if (!hasAssign && !hasTask && !hasTitle)
        {
            return ASSIGNMENT_UNASSIGNED;
        }
        if (hasAssign && hasTask && hasTitle)
        {
            return ASSIGNMENT_ASSIGNED;
        }
        return ASSIGNMENT_INVALID;
    }
}

// Pure data model representing a collection-level Personnel Snapshot V1.
// All metadata tokens are preserved as exact Strings without numeric parsing.
class DoDAPersonnelSnapshotV1 : Object
{
    int ApiVersion;
    String RevisionText;
    String StrategicMinutesText;
    int Count;
    Array<DoDAPersonRecordV1> Records;

    bool IsValid;
    EDoDAPersonnelAcquisitionState AcquisitionState;
    EDoDAPersonnelValidationReason ValidationReason;

    // Finds a record by its exact canonical persistent PersonIdText.
    DoDAPersonRecordV1 FindRecordById(String personIdText) const
    {
        if (personIdText == "")
        {
            return null;
        }

        for (int i = 0; i < Records.Size(); i++)
        {
            if (Records[i] != null && Records[i].PersonIdText == personIdText)
            {
                return Records[i];
            }
        }
        return null;
    }

    // Returns record at display array index (for bounded iteration only).
    DoDAPersonRecordV1 GetRecordByIndex(int index) const
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
        AcquisitionState = ACQUISITION_UNAVAILABLE;
        ValidationReason = VALIDATION_NONE;
    }
}
