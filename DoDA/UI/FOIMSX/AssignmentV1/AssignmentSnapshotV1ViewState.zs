///////////////////////////
// DoDA/UI/FOIMSX/AssignmentV1/AssignmentSnapshotV1ViewState.zs
///////////////////////////

// Explicit FOIMS-X Assignment V1 presentation states.
enum EDoDAAssignmentViewState
{
    VIEWSTATE_UNAVAILABLE,
    VIEWSTATE_INCOMPATIBLE_VERSION,
    VIEWSTATE_EMPTY,
    VIEWSTATE_STALE,
    VIEWSTATE_VALID
};

// Pure presentation view-state model for FOIMS-X Assignment V1 data.
// Does not call native methods directly; stores no pointers, actors, TIDs, or numeric uint64 IDs.
class DoDAAssignmentSnapshotV1ViewState : Object
{
    EDoDAAssignmentViewState CurrentViewState;

    // Projected snapshot summary info
    int TotalCount;
    String ActiveRevisionText;
    String ActiveStrategicMinutesText;

    // Retained last accepted snapshot for stale display retention
    DoDAAssignmentSnapshotV1 LastAcceptedSnapshot;

    // Factory method for creating an initialized view state object.
    static DoDAAssignmentSnapshotV1ViewState Create()
    {
        let vs = new("DoDAAssignmentSnapshotV1ViewState");
        vs.Reset();
        return vs;
    }

    // Resets view state to default initial state.
    void Reset()
    {
        CurrentViewState = VIEWSTATE_UNAVAILABLE;
        TotalCount = 0;
        ActiveRevisionText = "";
        ActiveStrategicMinutesText = "";
        LastAcceptedSnapshot = null;
    }

    // Updates view state projection from an acquired snapshot.
    // Handles accepted, rejected, stale, empty, and incompatible-version states.
    void UpdateFromSnapshot(DoDAAssignmentSnapshotV1 newSnapshot)
    {
        // Handle unacquired or rejected candidate snapshot
        if (newSnapshot == null || !newSnapshot.IsValid)
        {
            // If a valid snapshot was previously accepted, retain display data and mark STALE
            if (LastAcceptedSnapshot != null && LastAcceptedSnapshot.IsValid)
            {
                CurrentViewState = VIEWSTATE_STALE;
                return;
            }

            // No prior accepted snapshot held
            if (newSnapshot != null && (newSnapshot.AcquisitionState == ACQUISITION_UNSUPPORTED_VERSION ||
                                        newSnapshot.ValidationReason == VALIDATION_UNSUPPORTED_API_VERSION))
            {
                CurrentViewState = VIEWSTATE_INCOMPATIBLE_VERSION;
            }
            else
            {
                CurrentViewState = VIEWSTATE_UNAVAILABLE;
            }

            TotalCount = 0;
            ActiveRevisionText = "";
            ActiveStrategicMinutesText = "";
            LastAcceptedSnapshot = null;
            return;
        }

        // Accept validated candidate snapshot
        LastAcceptedSnapshot = newSnapshot;
        TotalCount = newSnapshot.Count;
        ActiveRevisionText = newSnapshot.RevisionText;
        ActiveStrategicMinutesText = newSnapshot.StrategicMinutesText;

        if (newSnapshot.Count == 0)
        {
            CurrentViewState = VIEWSTATE_EMPTY;
        }
        else
        {
            CurrentViewState = VIEWSTATE_VALID;
        }
    }

    // Requests new candidate snapshot through the Assignment Snapshot V1 adapter and updates view state.
    void Refresh()
    {
        let candidate = DoDAAssignmentSnapshotV1Adapter.AcquireSnapshot();
        UpdateFromSnapshot(candidate);
    }

    // Returns the number of visible assignment rows in the currently active/retained snapshot.
    // Returns 0 if ViewState is unavailable, empty, invalid, or has no accepted snapshot.
    int GetDisplayRowCount() const
    {
        if (LastAcceptedSnapshot == null || !LastAcceptedSnapshot.IsValid)
        {
            return 0;
        }
        return LastAcceptedSnapshot.Records.Size();
    }

    // Returns the record at the bounded display index through the snapshot's existing bounded query method.
    // Returns null if no valid accepted snapshot is held, index < 0, or index >= GetDisplayRowCount().
    DoDAAssignmentRecordV1 GetDisplayRecord(int index) const
    {
        if (LastAcceptedSnapshot == null || !LastAcceptedSnapshot.IsValid)
        {
            return null;
        }
        if (index < 0 || index >= GetDisplayRowCount())
        {
            return null;
        }
        return LastAcceptedSnapshot.GetRecordByIndex(index);
    }

    // Resolves and returns the canonical persistent AssignmentIdText for the specified display row index.
    // Returns "" if the record is null or index is invalid.
    String GetAssignmentIdByDisplayIndex(int index) const
    {
        let rec = GetDisplayRecord(index);
        if (rec != null)
        {
            return rec.AssignmentIdText;
        }
        return "";
    }
}
