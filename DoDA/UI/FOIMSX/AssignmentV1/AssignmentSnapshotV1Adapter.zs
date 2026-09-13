///////////////////////////
// DoDA/UI/FOIMSX/AssignmentV1/AssignmentSnapshotV1Adapter.zs
///////////////////////////

// Authorized read-only ZScript adapter for acquiring Assignment Snapshot V1
// records from the native DoDA strategic simulation bridge.
// Owns exactly one bounded acquisition transaction; no auxiliary polling methods.
class DoDAAssignmentSnapshotV1Adapter : Object
{
    const EXPECTED_API_VERSION = 1;
    const MAX_ASSIGNMENTS = 1024;
    const MAX_TASK_STATUS = 3;
    const MAX_BASE_COST = 10000;

    // Read-only query for the current native Assignment snapshot revision text.
    static String GetCurrentRevisionText()
    {
        return DoDA.GetAssignmentSnapshotRevisionText();
    }

    // Helper: Validates that a string is non-empty and contains only decimal digits [0-9].
    static bool IsDecimalString(String str)
    {
        int len = str.Length();
        if (len == 0)
        {
            return false;
        }

        for (int i = 0; i < len; i++)
        {
            int b = str.ByteAt(i);
            if (b < 48 || b > 57) // '0'..'9'
            {
                return false;
            }
        }
        return true;
    }

    // Acquires a complete, validated read-only Assignment Snapshot V1 from native C++.
    // Fully validates bounded rows and pre/post revision equality before acceptance.
    static DoDAAssignmentSnapshotV1 AcquireSnapshot()
    {
        // 1. Create a new candidate snapshot.
        let snapshot = new("DoDAAssignmentSnapshotV1");
        snapshot.Clear();

        // 2. Read Assignment Snapshot API Version.
        int apiVersion = DoDA.GetAssignmentSnapshotApiVersion();
        snapshot.ApiVersion = apiVersion;

        // 3. Reject if API Version is not exactly 1.
        if (apiVersion != EXPECTED_API_VERSION)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_UNSUPPORTED_VERSION;
            snapshot.ValidationReason = VALIDATION_UNSUPPORTED_API_VERSION;
            return snapshot;
        }

        // 4. Read revision text before data acquisition.
        String revBefore = DoDA.GetAssignmentSnapshotRevisionText();

        // 5. Reject if revision text is empty or not decimal text.
        if (!IsDecimalString(revBefore))
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
            snapshot.ValidationReason = VALIDATION_INVALID_REVISION_TOKEN;
            return snapshot;
        }

        // 6. Read strategic minutes text.
        String stratMin = DoDA.GetAssignmentSnapshotStrategicMinutesText();

        // 7. Read row count.
        int count = DoDA.GetAssignmentSnapshotCount();

        // 8. Reject if count is less than 0 or greater than 1024.
        if (count < 0 || count > MAX_ASSIGNMENTS)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_COUNT;
            snapshot.ValidationReason = VALIDATION_INVALID_COUNT;
            return snapshot;
        }

        // 9. For every row from 0 through Count minus 1, read all ten approved native row fields.
        Array<DoDAAssignmentRecordV1> candidateRecords;
        for (int i = 0; i < count; i++)
        {
            String assignId = DoDA.GetAssignmentIdText(i);
            String personId = DoDA.GetAssignmentPersonIdText(i);
            String personName = DoDA.GetAssignmentPersonDisplayName(i);
            String taskId = DoDA.GetAssignmentTaskIdText(i);
            String taskTitle = DoDA.GetAssignmentTaskTitle(i);
            String locId = DoDA.GetAssignmentLocationIdText(i);
            String locName = DoDA.GetAssignmentLocationDisplayName(i);
            int taskStatus = DoDA.GetAssignmentTaskStatus(i);
            int taskProgress = DoDA.GetAssignmentTaskProgress(i);
            int cost = DoDA.GetAssignmentCost(i);

            // 10. Validate each complete row.
            // Validate AssignmentId is non-empty decimal string
            if (!IsDecimalString(assignId))
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_ASSIGNMENT_ID;
                return snapshot;
            }

            // Validate PersonId is non-empty decimal string
            if (!IsDecimalString(personId))
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_PERSON_ID;
                return snapshot;
            }

            // Validate TaskId is non-empty decimal string
            if (!IsDecimalString(taskId))
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_TASK_ID;
                return snapshot;
            }

            // Validate LocationId is non-empty decimal string
            if (!IsDecimalString(locId))
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_LOCATION_ID;
                return snapshot;
            }

            // Validate non-blank PersonDisplayName
            if (personName == "")
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_MISSING_PERSON_DISPLAY_NAME;
                return snapshot;
            }

            // Validate non-blank TaskTitle
            if (taskTitle == "")
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_MISSING_TASK_TITLE;
                return snapshot;
            }

            // Validate non-blank LocationDisplayName
            if (locName == "")
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_MISSING_LOCATION_DISPLAY_NAME;
                return snapshot;
            }

            // Validate TaskStatus in source-confirmed range [0, 3] (Pending, Assigned, Completed, Failed)
            if (taskStatus < 0 || taskStatus > MAX_TASK_STATUS)
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_TASK_STATUS;
                return snapshot;
            }

            // Validate TaskProgress in range [0, 100]
            if (taskProgress < 0 || taskProgress > 100)
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_TASK_PROGRESS;
                return snapshot;
            }

            // Validate Cost in range [0, 10000]
            if (cost < 0 || cost > MAX_BASE_COST)
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                snapshot.ValidationReason = VALIDATION_INVALID_COST;
                return snapshot;
            }

            // Validate unique AssignmentId across all snapshot rows
            for (int j = 0; j < candidateRecords.Size(); j++)
            {
                if (candidateRecords[j].AssignmentIdText == assignId)
                {
                    snapshot.IsValid = false;
                    snapshot.AcquisitionState = ACQUISITION_INVALID_ROW;
                    snapshot.ValidationReason = VALIDATION_DUPLICATE_ASSIGNMENT_ID;
                    return snapshot;
                }
            }

            let record = new("DoDAAssignmentRecordV1");
            record.AssignmentIdText = assignId;
            record.PersonIdText = personId;
            record.PersonDisplayName = personName;
            record.TaskIdText = taskId;
            record.TaskTitle = taskTitle;
            record.LocationIdText = locId;
            record.LocationDisplayName = locName;
            record.TaskStatus = taskStatus;
            record.TaskProgress = taskProgress;
            record.Cost = cost;

            candidateRecords.Push(record);
        }

        // Validate candidate array size matches declared count
        if (candidateRecords.Size() != count)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_COUNT;
            snapshot.ValidationReason = VALIDATION_INVALID_COUNT;
            return snapshot;
        }

        // 12. Read revision text after all metadata and row reads.
        String revAfter = DoDA.GetAssignmentSnapshotRevisionText();

        // 13. Reject if revision changed during acquisition.
        if (revAfter != revBefore)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ASSIGNMENT_ACQUISITION_REVISION_CHANGED;
            snapshot.ValidationReason = ASSIGNMENT_VALIDATION_REVISION_CHANGED_DURING_ACQUISITION;
            return snapshot;
        }

        // 14. Mark the snapshot valid only after all validation passes.
        snapshot.RevisionText = revBefore;
        snapshot.StrategicMinutesText = stratMin;
        snapshot.Count = count;
        for (int k = 0; k < candidateRecords.Size(); k++)
        {
            snapshot.Records.Push(candidateRecords[k]);
        }

        snapshot.IsValid = true;
        snapshot.ValidationReason = ASSIGNMENT_VALIDATION_NONE;
        if (count == 0)
        {
            snapshot.AcquisitionState = ASSIGNMENT_ACQUISITION_EMPTY;
        }
        else
        {
            snapshot.AcquisitionState = ASSIGNMENT_ACQUISITION_POPULATED;
        }

        // 15. Return candidate snapshot.
        return snapshot;
    }
}
