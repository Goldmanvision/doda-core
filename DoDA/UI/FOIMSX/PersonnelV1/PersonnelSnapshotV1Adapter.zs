///////////////////////////
// DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Adapter.zs
///////////////////////////

// Authorized read-only ZScript adapter for acquiring Personnel Snapshot V1
// records from the native DoDA strategic simulation bridge.
// Owns exactly one bounded acquisition transaction; no auxiliary polling methods.
class DoDAPersonnelSnapshotV1Adapter : Object
{
    const EXPECTED_API_VERSION = 1;

    // Read-only query for the current native Personnel snapshot revision text.
    static String GetCurrentRevisionText()
    {
        return DoDA.GetPersonnelSnapshotRevisionText();
    }

    // Acquires a complete, validated read-only Personnel Snapshot V1 from native C++.
    // Fully validates bounded rows and pre/post revision equality before acceptance.
    static DoDAPersonnelSnapshotV1 AcquireSnapshot()
    {
        let snapshot = new("DoDAPersonnelSnapshotV1");
        snapshot.Clear();

        int apiVersion = DoDA.GetPersonnelSnapshotApiVersion();
        snapshot.ApiVersion = apiVersion;

        if (apiVersion != EXPECTED_API_VERSION)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_VERSION;
            snapshot.ValidationReason = VALIDATION_INCOMPATIBLE_API_VERSION;
            return snapshot;
        }

        String revBefore = DoDA.GetPersonnelSnapshotRevisionText();
        String stratMin = DoDA.GetPersonnelSnapshotStrategicMinutesText();
        int count = DoDA.GetPersonnelSnapshotCount();

        if (count < 0)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
            snapshot.ValidationReason = VALIDATION_NEGATIVE_COUNT;
            return snapshot;
        }

        Array<DoDAPersonRecordV1> candidateRecords;
        for (int i = 0; i < count; i++)
        {
            String personId = DoDA.GetPersonnelPersonIdText(i);
            String displayName = DoDA.GetPersonnelDisplayName(i);
            int status = DoDA.GetPersonnelStatus(i);
            int skill = DoDA.GetPersonnelSkill(i);
            int workload = DoDA.GetPersonnelWorkload(i);
            String assignId = DoDA.GetPersonnelCurrentAssignmentIdText(i);
            String taskId = DoDA.GetPersonnelCurrentTaskIdText(i);
            String taskTitle = DoDA.GetPersonnelCurrentTaskTitle(i);

            // Validate non-blank PersonId
            if (personId == "")
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
                snapshot.ValidationReason = VALIDATION_BLANK_PERSON_ID;
                return snapshot;
            }

            // Validate non-blank DisplayName
            if (displayName == "")
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
                snapshot.ValidationReason = VALIDATION_BLANK_DISPLAY_NAME;
                return snapshot;
            }

            // Validate no duplicate PersonId
            for (int j = 0; j < candidateRecords.Size(); j++)
            {
                if (candidateRecords[j].PersonIdText == personId)
                {
                    snapshot.IsValid = false;
                    snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
                    snapshot.ValidationReason = VALIDATION_DUPLICATE_PERSON_ID;
                    return snapshot;
                }
            }

            // Validate status in source-confirmed range [0, 2]
            if (status < 0 || status > 2)
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
                snapshot.ValidationReason = VALIDATION_INVALID_STATUS_VALUE;
                return snapshot;
            }

            // Validate assignment triple coherence (all empty or all non-empty)
            bool hasAssign = (assignId != "");
            bool hasTask = (taskId != "");
            bool hasTitle = (taskTitle != "");
            bool allEmpty = (!hasAssign && !hasTask && !hasTitle);
            bool allNonEmpty = (hasAssign && hasTask && hasTitle);

            if (!allEmpty && !allNonEmpty)
            {
                snapshot.IsValid = false;
                snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
                snapshot.ValidationReason = VALIDATION_MIXED_ASSIGNMENT_TRIPLE;
                return snapshot;
            }

            let record = new("DoDAPersonRecordV1");
            record.PersonIdText = personId;
            record.DisplayName = displayName;
            record.Status = status;
            record.Skill = skill;
            record.Workload = workload;
            record.CurrentAssignmentIdText = assignId;
            record.CurrentTaskIdText = taskId;
            record.CurrentTaskTitle = taskTitle;

            candidateRecords.Push(record);
        }

        // Validate candidate array size matches declared count
        if (candidateRecords.Size() != count)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_INVALID_SNAPSHOT;
            snapshot.ValidationReason = VALIDATION_COUNT_SIZE_MISMATCH;
            return snapshot;
        }

        // Validate pre/post revision equality; reject candidate if revision changed
        String revAfter = DoDA.GetPersonnelSnapshotRevisionText();
        if (revAfter != revBefore)
        {
            snapshot.IsValid = false;
            snapshot.AcquisitionState = ACQUISITION_REVISION_CHANGED;
            snapshot.ValidationReason = VALIDATION_REVISION_CHANGED_DURING_ACQUISITION;
            return snapshot;
        }

        // Accept validated snapshot
        snapshot.RevisionText = revBefore;
        snapshot.StrategicMinutesText = stratMin;
        snapshot.Count = count;
        for (int k = 0; k < candidateRecords.Size(); k++)
        {
            snapshot.Records.Push(candidateRecords[k]);
        }

        snapshot.IsValid = true;
        snapshot.ValidationReason = VALIDATION_NONE;
        if (count == 0)
        {
            snapshot.AcquisitionState = ACQUISITION_EMPTY;
        }
        else
        {
            snapshot.AcquisitionState = ACQUISITION_POPULATED;
        }

        return snapshot;
    }
}
