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
    private ui bool mLastActiveState;
    private ui int mFocusedIndex;

    ui bool HandleNavInput(int keyScan, int keyChar)
    {
if (mViewState == null)
        {
            mViewState = DoDAPersonnelSnapshotV1ViewState.Create();

            let snapshot = DoDAPersonnelSnapshotV1Adapter.AcquireSnapshot();
            mViewState.UpdateFromSnapshot(snapshot);
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
            mLastActiveState = false;
            mFocusedIndex = -1;
            return;
        }

        if (!mLastActiveState)
        {
            if (mViewState == null)
            {
                mViewState = DoDAPersonnelSnapshotV1ViewState.Create();
            }

            let snapshot = DoDAPersonnelSnapshotV1Adapter.AcquireSnapshot();
            mViewState.UpdateFromSnapshot(snapshot);

            if (mAssignmentViewState == null)
            {
                mAssignmentViewState = DoDAAssignmentSnapshotV1ViewState.Create();
            }

            let assignSnapshot = DoDAAssignmentSnapshotV1Adapter.AcquireSnapshot();
            mAssignmentViewState.UpdateFromSnapshot(assignSnapshot);

            if (mViewState.GetDisplayRowCount() > 0)
            {
                mFocusedIndex = 0;
            }
            else
            {
                mFocusedIndex = -1;
            }

            mLastActiveState = true;
        }

        Screen.Dim(0xFF000814, 1.0, 0, 0, Screen.GetWidth(), Screen.GetHeight());

        DrawRaisedPanel(10, 10, 620, 460, 0xFF182234);

        DrawVirtualRect(14, 14, 612, 20, 0xFF0A3678);
        Screen.DrawText(SmallFont, Font.CR_WHITE, 20, 18,
            "FOIMS-X STRATEGIC INTERFACE",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);

        DrawVirtualRect(14, 36, 612, 18, 0xFF121B2A);
        Screen.DrawText(SmallFont, Font.CR_GRAY, 20, 40,
            "FILE   DIRECTORY   CASES   OPERATIONS   SYSTEM",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);

        DrawSunkenPanel(16, 58, 286, 356, 0xFF0A101C);
        DrawVirtualRect(18, 60, 282, 18, 0xFF1A2638);
        Screen.DrawText(SmallFont, Font.CR_GOLD, 24, 64,
            "PERSONNEL DIRECTORY",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);

        RenderPersonnelDirectory();

        DrawSunkenPanel(308, 58, 318, 356, 0xFF0A101C);
        DrawVirtualRect(310, 60, 314, 18, 0xFF1A2638);
        Screen.DrawText(SmallFont, Font.CR_GOLD, 316, 64,
            "SELECTED PERSON",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);

        RenderSelectedPerson();

        if (mAssignmentViewState != null)
        {
            DoDAAssignmentSnapshotV1Renderer.Render(mAssignmentViewState);
        }

        DrawSunkenPanel(16, 420, 610, 24, 0xFF121B2A);
        Screen.DrawText(SmallFont, Font.CR_WHITE, 22, 426,
            "UP/DOWN FOCUS   ENTER SELECT   BACKSPACE CLEAR   O/ESC EXIT",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);
    }

    private ui void RenderSelectedPerson()
    {
        Vector2 realClipPos, realClipSize;
        [realClipPos, realClipSize] = Screen.VirtualToRealCoords(
            (312, 80), (310, 330), (640, 480), false, true
        );

        int clipLeft = int(realClipPos.x);
        int clipTop = int(realClipPos.y);
        int clipRight = int(realClipPos.x + realClipSize.x);
        int clipBottom = int(realClipPos.y + realClipSize.y);

        if (mViewState == null || !mViewState.HasSelection)
        {
            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 210,
                "NO AGENT SELECTED",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_DARKGRAY, 330, 224,
                "PRESS ENTER TO INSPECT",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
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

        Screen.DrawText(NewSmallFont, Font.CR_WHITE, 330, 90, nameText,
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_TextLen, 32,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 114, "STATUS:",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, statusColor, 410, 114, statusText,
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_TextLen, 18,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 132, "ASSIGNMENT:",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, assignColor, 410, 132, assignText,
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_TextLen, 18,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 150, "SKILL:",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_WHITE, 410, 150,
            String.Format("%d", mViewState.SelectedSkill),
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 168, "WORKLOAD:",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_WHITE, 410, 168,
            String.Format("%d%%", mViewState.SelectedWorkload),
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        if (mViewState.SelectedAssignmentClassification ==
                ASSIGNMENT_ASSIGNED &&
            mViewState.SelectedTaskTitle.Length() > 0)
        {
            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 330, 190, "TASK:",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_CYAN, 410, 190,
                mViewState.SelectedTaskTitle.MakeUpper(),
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 18,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
        }
    }
    private ui void RenderPersonnelDirectory()
    {
        Vector2 realClipPos, realClipSize;
        [realClipPos, realClipSize] = Screen.VirtualToRealCoords(
            (18, 80), (282, 330), (640, 480), false, true
        );

        int clipLeft = int(realClipPos.x);
        int clipTop = int(realClipPos.y);
        int clipRight = int(realClipPos.x + realClipSize.x);
        int clipBottom = int(realClipPos.y + realClipSize.y);

        if (mViewState == null ||
            mViewState.CurrentViewState == VIEWSTATE_UNAVAILABLE)
        {
            Screen.DrawText(NewSmallFont, Font.CR_RED, 20, 104,
                "[DIRECTORY UNAVAILABLE]",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "AWAITING SNAPSHOT",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        if (mViewState.CurrentViewState == VIEWSTATE_INVALID_VERSION)
        {
            Screen.DrawText(NewSmallFont, Font.CR_RED, 20, 104,
                "[SNAPSHOT VERSION ERROR]",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "DIRECTORY OFFLINE",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        if (mViewState.CurrentViewState == VIEWSTATE_EMPTY)
        {
            Screen.DrawText(NewSmallFont, Font.CR_YELLOW, 20, 104,
                "[NO PERSONNEL RECORDS]",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 20, 116,
                "DIRECTORY EMPTY",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        int totalRecords = mViewState.GetDisplayRowCount();

        if (totalRecords <= 0)
        {
            Screen.DrawText(NewSmallFont, Font.CR_GRAY, 20, 104,
                "NO DATA",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        Screen.DrawText(NewSmallFont, Font.CR_WHITE, 20, 82,
            "  NAME                         STATUS         ASSIGNMENT",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_DARKGRAY, 20, 92,
            "------------------------------------------------------------",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

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
                DrawVirtualRect(19, rowY - 1, 280, 10, 0xFF183868);

                Screen.DrawText(NewSmallFont, Font.CR_GOLD, 20.0, rowY, ">",
                    DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                    DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                    DTA_Monospace, 1, DTA_Spacing, 9,
                    DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                    DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            }

            if (isSelected)
            {
                Screen.DrawText(NewSmallFont, Font.CR_CYAN, 24.5, rowY, "*",
                    DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                    DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                    DTA_Monospace, 1, DTA_Spacing, 9,
                    DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                    DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
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

            Screen.DrawText(NewSmallFont, Font.CR_WHITE, 29.0, rowY, nameText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 28,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, statusColor, 159.5, rowY, statusText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 14,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, assignColor, 227.0, rowY, assignText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 15,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
        }

        if (totalRecords > maxRows)
        {
            Screen.DrawText(NewSmallFont, Font.CR_DARKGRAY, 20, 396,
                "[DIRECTORY TRUNCATED]",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
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

    private static ui void DrawVirtualRect(
        double vx,
        double vy,
        double vw,
        double vh,
        Color col
    )
    {
        Vector2 realPos, realSize;

        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        Screen.Dim(
            col,
            1.0,
            int(realPos.x),
            int(realPos.y),
            int(realSize.x),
            int(realSize.y)
        );
    }

    private static ui void DrawRaisedPanel(
        double vx,
        double vy,
        double vw,
        double vh,
        Color bgCol
    )
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);

        Vector2 realPos, realSize;

        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x1, y0, 0xFF5A7292);
        Screen.DrawLine(x0, y0, x0, y1, 0xFF5A7292);
        Screen.DrawLine(x0, y1, x1, y1, 0xFF080D14);
        Screen.DrawLine(x1, y0, x1, y1, 0xFF080D14);
    }

    private static ui void DrawSunkenPanel(
        double vx,
        double vy,
        double vw,
        double vh,
        Color bgCol
    )
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);

        Vector2 realPos, realSize;

        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x1, y0, 0xFF080D14);
        Screen.DrawLine(x0, y0, x0, y1, 0xFF080D14);
        Screen.DrawLine(x0, y1, x1, y1, 0xFF364860);
        Screen.DrawLine(x1, y0, x1, y1, 0xFF364860);
    }
}
