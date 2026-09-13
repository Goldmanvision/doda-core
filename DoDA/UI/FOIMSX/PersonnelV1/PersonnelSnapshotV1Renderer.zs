/*//////////////////////////|
// DoDA/UI/FOIMSX/PersonnelV1/PersonnelSnapshotV1Renderer.zs
//
// FOIMS-X Dedicated Personnel Directory V1 Presentation Renderer.
//
// Temporary input-recovery capture scope:
//   - Logs keyScan and keyChar received from the active FOIMS-X Host.
//   - Preserves current drawing, snapshot, ViewState, focus, and selection behavior.
//   - Keeps existing navigation mappings temporarily so the UI remains testable.
//   - Remove the diagnostic and replace speculative mappings after capture.
*///////////////////////////|

class DoDAFOIMSXDirectoryRenderer : EventHandler
{
    private ui DoDAPersonnelSnapshotV1ViewState mViewState;
    private ui DoDAAssignmentSnapshotV1ViewState mAssignmentViewState;
    private ui DoDAFOIMSXSnapshotRefreshState mPersonnelRefreshState;
    private ui DoDAFOIMSXSnapshotRefreshState mAssignmentRefreshState;
    private ui int mFocusedIndex;

    ui void RefreshPersonnelData(bool force = false)
    {
        if (mViewState == null)
        {
            mViewState = DoDAPersonnelSnapshotV1ViewState.Create();
        }

        if (mPersonnelRefreshState == null)
        {
            mPersonnelRefreshState = DoDAFOIMSXSnapshotRefreshState.Create();
        }

        String currentRev = DoDAPersonnelSnapshotV1Adapter.GetCurrentRevisionText();

        if (mPersonnelRefreshState.ShouldRefresh(currentRev, force))
        {
            let snapshot = DoDAPersonnelSnapshotV1Adapter.AcquireSnapshot();
            mViewState.UpdateFromSnapshot(snapshot);

            if (snapshot != null && snapshot.IsValid && snapshot.AcquireStatus == FOIMSX_ACQUIRE_SUCCESS)
            {
                mPersonnelRefreshState.MarkApplied(snapshot.RevisionText);
            }

            int rowCount = mViewState.GetDisplayRowCount();
            if (rowCount > 0)
            {
                if (mFocusedIndex < 0 || mFocusedIndex >= rowCount)
                {
                    mFocusedIndex = 0;
                }
            }
            else
            {
                mFocusedIndex = -1;
            }
        }
    }

    ui void RefreshAssignmentData(bool force = false)
    {
        if (mAssignmentViewState == null)
        {
            mAssignmentViewState = DoDAAssignmentSnapshotV1ViewState.Create();
        }

        if (mAssignmentRefreshState == null)
        {
            mAssignmentRefreshState = DoDAFOIMSXSnapshotRefreshState.Create();
        }

        String currentRev = DoDAAssignmentSnapshotV1Adapter.GetCurrentRevisionText();

        if (mAssignmentRefreshState.ShouldRefresh(currentRev, force))
        {
            let assignSnapshot = DoDAAssignmentSnapshotV1Adapter.AcquireSnapshot();
            mAssignmentViewState.UpdateFromSnapshot(assignSnapshot);

            if (assignSnapshot != null && assignSnapshot.IsValid && assignSnapshot.AcquireStatus == FOIMSX_ACQUIRE_SUCCESS)
            {
                mAssignmentRefreshState.MarkApplied(assignSnapshot.RevisionText);
            }
        }
    }

    ui void RefreshSessionData(bool force = false)
    {
        RefreshPersonnelData(force);
        RefreshAssignmentData(force);
    }

    ui bool HandleNavInput(int keyScan, int keyChar)
    {
        if (mViewState == null)
        {
            return false;
        }

        int rowCount = mViewState.GetDisplayRowCount();

        if (rowCount <= 0)
        {
            mFocusedIndex = -1;
            return false;
        }

        if (mFocusedIndex < 0)
        {
            mFocusedIndex = 0;
        }

        // Temporary existing mappings retained for diagnostic continuity.
        if (keyScan == 0xc8 ||
            keyScan == 0x48 ||
            keyScan == 0x26 ||
            keyScan == 11 ||
            keyChar == 11 ||
            keyChar == 56 ||
            keyChar == 119 ||
            keyChar == 87)
        {
            mFocusedIndex--;

            if (mFocusedIndex < 0)
            {
                mFocusedIndex = 0;
            }

            return true;
        }

        if (keyScan == 0xd0 ||
            keyScan == 0x50 ||
            keyScan == 0x28 ||
            keyScan == 10 ||
            keyChar == 10 ||
            keyChar == 50 ||
            keyChar == 115 ||
            keyChar == 83)
        {
            mFocusedIndex++;

            if (mFocusedIndex >= rowCount)
            {
                mFocusedIndex = rowCount - 1;
            }

            return true;
        }

        if (keyScan == 0xc9 ||
            keyScan == 0x49 ||
            keyScan == 0x21 ||
            keyScan == 2 ||
            keyChar == 2 ||
            keyChar == 57)
        {
            mFocusedIndex -= 5;

            if (mFocusedIndex < 0)
            {
                mFocusedIndex = 0;
            }

            return true;
        }

        if (keyScan == 0xd1 ||
            keyScan == 0x51 ||
            keyScan == 0x22 ||
            keyScan == 1 ||
            keyChar == 1 ||
            keyChar == 51)
        {
            mFocusedIndex += 5;

            if (mFocusedIndex >= rowCount)
            {
                mFocusedIndex = rowCount - 1;
            }

            return true;
        }

        if (keyScan == 0xc7 ||
            keyScan == 0x47 ||
            keyScan == 0x24 ||
            keyScan == 3 ||
            keyChar == 3 ||
            keyChar == 55)
        {
            mFocusedIndex = 0;
            return true;
        }

        if (keyScan == 0xcf ||
            keyScan == 0x4f ||
            keyScan == 0x23 ||
            keyScan == 4 ||
            keyChar == 4 ||
            keyChar == 49)
        {
            mFocusedIndex = rowCount - 1;
            return true;
        }

        if (keyScan == 0xcb ||
            keyScan == 0x4b ||
            keyScan == 0x25 ||
            keyScan == 5 ||
            keyChar == 5 ||
            keyChar == 52 ||
            keyChar == 97 ||
            keyChar == 65)
        {
            mFocusedIndex--;

            if (mFocusedIndex < 0)
            {
                mFocusedIndex = 0;
            }

            return true;
        }

        if (keyScan == 0xcd ||
            keyScan == 0x4d ||
            keyScan == 0x27 ||
            keyScan == 6 ||
            keyChar == 6 ||
            keyChar == 54 ||
            keyChar == 100 ||
            keyChar == 68)
        {
            mFocusedIndex++;

            if (mFocusedIndex >= rowCount)
            {
                mFocusedIndex = rowCount - 1;
            }

            return true;
        }

        if (keyScan == 0x1c ||
            keyScan == 0x9c ||
            keyScan == 0x39 ||
            keyScan == 13 ||
            keyScan == 10 ||
            keyScan == 32 ||
            keyChar == 13 ||
            keyChar == 10 ||
            keyChar == 32)
        {
            if (mFocusedIndex >= 0 && mFocusedIndex < rowCount)
            {
                String personIdText =
                    mViewState.GetPersonIdByDisplayIndex(mFocusedIndex);

                if (personIdText.Length() > 0)
                {
                    mViewState.SelectById(personIdText);
                }
            }

            return true;
        }

        if (keyScan == 0x0e ||
            keyScan == 0xd3 ||
            keyScan == 8 ||
            keyScan == 26 ||
            keyScan == 127 ||
            keyChar == 8 ||
            keyChar == 26 ||
            keyChar == 127)
        {
            mViewState.ClearSelection();
            return true;
        }

        return false;
    }

    override void RenderOverlay(RenderEvent e)
    {
        if (Level == null ||
            Level.MapName != "MAP01" ||
            !DoDAFOIMSXSessionController.IsSessionActive())
        {
            mFocusedIndex = -1;
            return;
        }

        Screen.Dim(0xFF000814, 1.0, 0, 0, Screen.GetWidth(), Screen.GetHeight());

        DoDAFOIMSXDrawingHelpers.DrawRaisedPanel(10, 10, 620, 460, 0xFF182234);

        DoDAFOIMSXDrawingHelpers.DrawVirtualRect(14, 14, 612, 20, 0xFF0A3678);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_WHITE, 20, 18,
            "FOIMS-X STRATEGIC INTERFACE");

        DoDAFOIMSXDrawingHelpers.DrawVirtualRect(14, 36, 612, 18, 0xFF121B2A);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_GRAY, 20, 40,
            "FILE   DIRECTORY   CASES   OPERATIONS   SYSTEM");

        DoDAFOIMSXDrawingHelpers.DrawSunkenPanel(16, 58, 286, 356, 0xFF0A101C);
        DoDAFOIMSXDrawingHelpers.DrawVirtualRect(18, 60, 282, 18, 0xFF1A2638);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_GOLD, 24, 64,
            "PERSONNEL DIRECTORY");

        RenderPersonnelDirectory();

        DoDAFOIMSXDrawingHelpers.DrawSunkenPanel(308, 58, 318, 356, 0xFF0A101C);
        DoDAFOIMSXDrawingHelpers.DrawVirtualRect(310, 60, 314, 18, 0xFF1A2638);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_GOLD, 316, 64,
            "SELECTED PERSON");

        RenderSelectedPerson();

        if (mAssignmentViewState != null)
        {
            DoDAAssignmentSnapshotV1Renderer.Render(mAssignmentViewState);
        }

        DoDAFOIMSXDrawingHelpers.DrawSunkenPanel(16, 420, 610, 24, 0xFF121B2A);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_WHITE, 22, 426,
            "UP/DOWN FOCUS   ENTER SELECT   BACKSPACE CLEAR   O/ESC EXIT");
    }

    private ui void RenderSelectedPerson()
    {
        int clipLeft, clipTop, clipRight, clipBottom;
        DoDAFOIMSXDrawingHelpers.GetRealClipRect(
            312, 80, 310, 330, clipLeft, clipTop, clipRight, clipBottom
        );

        if (mViewState == null || !mViewState.HasSelection)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 210,
                "NO AGENT SELECTED",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 330, 224,
                "PRESS ENTER TO INSPECT",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        String nameText =
            (mViewState.SelectedDisplayName.Length() > 0)
            ? mViewState.SelectedDisplayName.MakeUpper()
            : "UNKNOWN AGENT";

        String statusText = GetStatusString(mViewState.SelectedStatusCode);
        int statusColor = GetStatusColor(mViewState.SelectedStatusCode);

        int assignClass = int(mViewState.SelectedAssignmentClassification);
        String assignText = GetAssignmentString(assignClass);
        int assignColor = GetAssignmentColor(assignClass);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 330, 90, nameText,
            clipLeft, clipTop, clipRight, clipBottom, 32);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 114, "STATUS:",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, statusColor, 410, 114, statusText,
            clipLeft, clipTop, clipRight, clipBottom, 18);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 132, "ASSIGNMENT:",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, assignColor, 410, 132, assignText,
            clipLeft, clipTop, clipRight, clipBottom, 18);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 150, "SKILL:",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 410, 150,
            String.Format("%d", mViewState.SelectedSkill),
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 168, "WORKLOAD:",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 410, 168,
            String.Format("%d%%", mViewState.SelectedWorkload),
            clipLeft, clipTop, clipRight, clipBottom);

        if (mViewState.SelectedAssignmentClassification ==
                ASSIGNMENT_ASSIGNED &&
            mViewState.SelectedTaskTitle.Length() > 0)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 190, "TASK:",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_CYAN, 410, 190,
                mViewState.SelectedTaskTitle.MakeUpper(),
                clipLeft, clipTop, clipRight, clipBottom, 18);
        }
    }
    private ui void RenderPersonnelDirectory()
    {
        int clipLeft, clipTop, clipRight, clipBottom;
        DoDAFOIMSXDrawingHelpers.GetRealClipRect(
            18, 80, 282, 330, clipLeft, clipTop, clipRight, clipBottom
        );

        if (mViewState == null ||
            mViewState.CurrentViewState == VIEWSTATE_UNAVAILABLE)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_RED, 20, 104,
                "[DIRECTORY UNAVAILABLE]",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "AWAITING SNAPSHOT",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        if (mViewState.CurrentViewState == VIEWSTATE_INVALID_VERSION)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_RED, 20, 104,
                "[SNAPSHOT VERSION ERROR]",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "DIRECTORY OFFLINE",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        if (mViewState.CurrentViewState == VIEWSTATE_EMPTY)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 20, 104,
                "[NO PERSONNEL RECORDS]",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "DIRECTORY EMPTY",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        int totalRecords = mViewState.GetDisplayRowCount();

        if (totalRecords <= 0)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 20, 104,
                "NO DATA",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 20, 82,
            "  NAME                         STATUS         ASSIGNMENT",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 20, 92,
            "------------------------------------------------------------",
            clipLeft, clipTop, clipRight, clipBottom);

        int maxRows = 29;
        int renderCount = (totalRecords < maxRows) ? totalRecords : maxRows;

        for (int i = 0; i < renderCount; i++)
        {
            let rec = mViewState.GetDisplayRecord(i);

            if (rec == null)
            {
                continue;
            }

            double rowY = 104 + (i * 10);

            bool isFocused = (i == mFocusedIndex);
            bool isSelected = mViewState != null &&
                              mViewState.HasSelection &&
                              rec.PersonIdText.Length() > 0 &&
                              rec.PersonIdText == mViewState.SelectedPersonIdText;

            if (isFocused)
            {
                DoDAFOIMSXDrawingHelpers.DrawVirtualRect(19, rowY - 1, 280, 10, 0xFF183868);

                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GOLD, 20.0, rowY, ">",
                    clipLeft, clipTop, clipRight, clipBottom);
            }

            if (isSelected)
            {
                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_CYAN, 24.5, rowY, "*",
                    clipLeft, clipTop, clipRight, clipBottom);
            }

            String nameText =
                (rec.DisplayName.Length() > 0)
                ? rec.DisplayName.MakeUpper()
                : "UNKNOWN AGENT";

            String statusText = GetStatusString(rec.Status);
            int statusColor = GetStatusColor(rec.Status);
            int assignClass = int(rec.GetAssignmentClassification());
            String assignText = GetAssignmentString(assignClass);
            int assignColor = GetAssignmentColor(assignClass);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 29.0, rowY, nameText,
                clipLeft, clipTop, clipRight, clipBottom, 28);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, statusColor, 159.5, rowY, statusText,
                clipLeft, clipTop, clipRight, clipBottom, 14);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, assignColor, 227.0, rowY, assignText,
                clipLeft, clipTop, clipRight, clipBottom, 15);
        }

        if (totalRecords > maxRows)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 20, 396,
                "[DIRECTORY TRUNCATED]",
                clipLeft, clipTop, clipRight, clipBottom);
        }
    }

    private static ui String GetStatusString(int status)
    {
        switch (status)
        {
        case 0:
            return "AVAILABLE";
        case 1:
            return "ASSIGNED";
        case 2:
            return "UNAVAILABLE";
        default:
            return "UNKNOWN";
        }
    }

    private static ui int GetStatusColor(int status)
    {
        switch (status)
        {
        case 0:
            return Font.CR_GREEN;
        case 1:
            return Font.CR_YELLOW;
        case 2:
            return Font.CR_RED;
        default:
            return Font.CR_DARKGRAY;
        }
    }

    private static ui String GetAssignmentString(int assignment)
    {
        switch (assignment)
        {
        case ASSIGNMENT_UNASSIGNED:
            return "UNASSIGNED";
        case ASSIGNMENT_ASSIGNED:
            return "ASSIGNED";
        default:
            return "INVALID";
        }
    }

    private static ui int GetAssignmentColor(int assignment)
    {
        switch (assignment)
        {
        case ASSIGNMENT_UNASSIGNED:
            return Font.CR_DARKGRAY;
        case ASSIGNMENT_ASSIGNED:
            return Font.CR_CYAN;
        default:
            return Font.CR_RED;
        }
    }
}
