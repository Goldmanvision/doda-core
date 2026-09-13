///////////////////////`////
// DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1ViewState.zs
///////////////////////////

// Explicit FOIMS-X Personnel V1 presentation states.
enum EDoDAPersonnelViewState
{
    VIEWSTATE_UNAVAILABLE,
    VIEWSTATE_INVALID_VERSION,
    VIEWSTATE_EMPTY,
    VIEWSTATE_STALE,
    VIEWSTATE_OUT_OF_RANGE,
    VIEWSTATE_SELECTED_PERSON_DISAPPEARED,
    VIEWSTATE_UNASSIGNED,
    VIEWSTATE_POPULATED
};

// Pure presentation view-state model for FOIMS-X Personnel V1 UI.
// Does not call native methods directly; selection is keyed by persistent PersonIdText only.
class DoDAPersonnelSnapshotV1ViewState : Object
{
    EDoDAPersonnelViewState CurrentViewState;

    // Selection key is canonical persistent PersonIdText only (never row index)
    String SelectedPersonIdText;
    String PreviousSelectedPersonIdText;

    // Projected presentation fields for currently selected record
    bool HasSelection;
    String SelectedDisplayName;
    int SelectedStatusCode;
    int SelectedSkill;
    int SelectedWorkload;
    String SelectedAssignmentIdText;
    String SelectedTaskIdText;
    String SelectedTaskTitle;
    EDoDAPersonAssignmentClassification SelectedAssignmentClassification;

    // Projected snapshot summary info
    int TotalCount;
    String ActiveRevisionText;
    String ActiveStrategicMinutesText;

    // Retained last accepted snapshot for stale display retention
    DoDAPersonnelSnapshotV1 LastAcceptedSnapshot;

    // Factory method for creating an initialized view state object.
    static DoDAPersonnelSnapshotV1ViewState Create()
    {
        let vs = new("DoDAPersonnelSnapshotV1ViewState");
        vs.Reset();
        return vs;
    }

    // Resets view state to default initial state.
    void Reset()
    {
        CurrentViewState = VIEWSTATE_UNAVAILABLE;
        SelectedPersonIdText = "";
        PreviousSelectedPersonIdText = "";
        HasSelection = false;
        ClearSelectedFields();
        TotalCount = 0;
        ActiveRevisionText = "";
        ActiveStrategicMinutesText = "";
        LastAcceptedSnapshot = null;
    }

    // Clears selection state and selected fields.
    void ClearSelection()
    {
        SelectedPersonIdText = "";
        PreviousSelectedPersonIdText = "";
        HasSelection = false;
        ClearSelectedFields();
    }

    private void ClearSelectedFields()
    {
        SelectedDisplayName = "";
        SelectedStatusCode = -1;
        SelectedSkill = 0;
        SelectedWorkload = 0;
        SelectedAssignmentIdText = "";
        SelectedTaskIdText = "";
        SelectedTaskTitle = "";
        SelectedAssignmentClassification = ASSIGNMENT_UNASSIGNED;
    }

    // Updates view state projection from an acquired snapshot.
    // Handles accepted, rejected, stale, empty, populated, and disappeared states.
    void UpdateFromSnapshot(DoDAPersonnelSnapshotV1 newSnapshot)
    {
        // Handle unacquired or rejected candidate snapshot
        if (newSnapshot == null || !newSnapshot.IsValid || newSnapshot.AcquireStatus != FOIMSX_ACQUIRE_SUCCESS)
        {
            // If a valid snapshot was previously accepted, retain display data and mark STALE
            if (LastAcceptedSnapshot != null && LastAcceptedSnapshot.IsValid)
            {
                CurrentViewState = VIEWSTATE_STALE;
                return;
            }

            // No prior accepted snapshot held
            if (newSnapshot != null && (newSnapshot.AcquireStatus == FOIMSX_ACQUIRE_INCOMPATIBLE_VERSION ||
                                        newSnapshot.AcquisitionState == ACQUISITION_INVALID_VERSION))
            {
                CurrentViewState = VIEWSTATE_INVALID_VERSION;
            }
            else
            {
                CurrentViewState = VIEWSTATE_UNAVAILABLE;
            }

            ClearSelection();
            TotalCount = 0;
            ActiveRevisionText = "";
            ActiveStrategicMinutesText = "";
            LastAcceptedSnapshot = null;
            return;
        }

        // Accept validated snapshot
        LastAcceptedSnapshot = newSnapshot;
        TotalCount = newSnapshot.Count;
        ActiveRevisionText = newSnapshot.RevisionText;
        ActiveStrategicMinutesText = newSnapshot.StrategicMinutesText;

        if (newSnapshot.Count == 0)
        {
            CurrentViewState = VIEWSTATE_EMPTY;
            ClearSelection();
            return;
        }

        // Reconcile prior selection by persistent PersonIdText only
        if (SelectedPersonIdText != "")
        {
            let rec = newSnapshot.FindRecordById(SelectedPersonIdText);
            if (rec != null)
            {
                PreviousSelectedPersonIdText = "";
                ApplySelectedRecord(rec);
            }
            else
            {
                // Previously selected person is absent in newly accepted snapshot
                PreviousSelectedPersonIdText = SelectedPersonIdText;
                SelectedPersonIdText = "";
                HasSelection = false;
                ClearSelectedFields();
                CurrentViewState = VIEWSTATE_SELECTED_PERSON_DISAPPEARED;
            }
        }
        else
        {
            // No prior selection; do not choose an automatic fallback record
            HasSelection = false;
            ClearSelectedFields();
            CurrentViewState = VIEWSTATE_POPULATED;
        }
    }

    // Returns the number of visible personnel rows in the currently active/retained snapshot.
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
    DoDAPersonRecordV1 GetDisplayRecord(int index) const
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

    // Resolves and returns the canonical persistent PersonIdText for the specified display row index.
    // Returns "" if the record is null or index is invalid. Does not select the record.
    String GetPersonIdByDisplayIndex(int index) const
    {
        let rec = GetDisplayRecord(index);
        if (rec != null)
        {
            return rec.PersonIdText;
        }
        return "";
    }

    // Selects a person record by canonical persistent PersonIdText (exact string equality).
    bool SelectById(String personIdText)
    {
        if (personIdText == "")
        {
            ClearSelection();
            if (LastAcceptedSnapshot != null && LastAcceptedSnapshot.IsValid)
            {
                CurrentViewState = (LastAcceptedSnapshot.Count == 0) ? VIEWSTATE_EMPTY : VIEWSTATE_POPULATED;
            }
            return false;
        }

        if (LastAcceptedSnapshot == null || !LastAcceptedSnapshot.IsValid)
        {
            return false;
        }

        let rec = LastAcceptedSnapshot.FindRecordById(personIdText);
        if (rec == null)
        {
            // Missing ID in current snapshot returns false without changing view state to OUT_OF_RANGE
            return false;
        }

        SelectedPersonIdText = personIdText;
        PreviousSelectedPersonIdText = "";
        ApplySelectedRecord(rec);
        return true;
    }

    private void ApplySelectedRecord(DoDAPersonRecordV1 rec)
    {
        HasSelection = true;
        SelectedDisplayName = rec.DisplayName;
        SelectedStatusCode = rec.Status;
        SelectedSkill = rec.Skill;
        SelectedWorkload = rec.Workload;
        SelectedAssignmentIdText = rec.CurrentAssignmentIdText;
        SelectedTaskIdText = rec.CurrentTaskIdText;
        SelectedTaskTitle = rec.CurrentTaskTitle;
        SelectedAssignmentClassification = rec.GetAssignmentClassification();

        if (SelectedAssignmentClassification == ASSIGNMENT_ASSIGNED)
        {
            CurrentViewState = VIEWSTATE_POPULATED;
        }
        else
        {
            CurrentViewState = VIEWSTATE_UNASSIGNED;
        }
    }
}
