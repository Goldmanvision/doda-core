/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXSnapshotRefreshState.zs
//
// FOIMS-X Shared Snapshot Refresh State Bookkeeping.
//
// Narrow shared helper for tracking last-applied revision text and evaluating
// whether a snapshot rebuild is required based on force flags or changed revision tokens.
//
// Scope & Boundary:
//   - Owns only common refresh bookkeeping (last-applied revision, initialized flag, should-refresh decision).
//   - Zero domain knowledge: does not know Personnel, Assignment, models, adapters, view-states, or renderers.
//   - Zero native calls: does not call DoDA native queries.
//   - Zero lifecycle, input, tick, timer, or rendering operations.
*///////////////////////////|

class DoDAFOIMSXSnapshotRefreshState : Object
{
    private String mLastAppliedRevisionText;
    private bool mHasAppliedRevision;

    // Factory method for creating an initialized refresh state object.
    static DoDAFOIMSXSnapshotRefreshState Create()
    {
        let state = new("DoDAFOIMSXSnapshotRefreshState");
        state.Reset();
        return state;
    }

    // Resets refresh state to uninitialized.
    void Reset()
    {
        mLastAppliedRevisionText = "";
        mHasAppliedRevision = false;
    }

    // Evaluates whether a snapshot rebuild is needed.
    // Returns true if force is set, if no revision has been applied, or if the current revision differs from the last applied revision.
    // Pure query: does not mutate internal state.
    bool ShouldRefresh(String currentRevisionText, bool force = false) const
    {
        if (force || !mHasAppliedRevision || mLastAppliedRevisionText != currentRevisionText)
        {
            return true;
        }

        return false;
    }

    // Marks a revision as successfully applied.
    // Must only be called after successful snapshot acquisition and view-state population.
    void MarkApplied(String currentRevisionText)
    {
        mLastAppliedRevisionText = currentRevisionText;
        mHasAppliedRevision = true;
    }

    // Read-only accessors for diagnostics / inspection.
    String GetLastAppliedRevisionText() const
    {
        return mLastAppliedRevisionText;
    }

    bool HasAppliedRevision() const
    {
        return mHasAppliedRevision;
    }
}
