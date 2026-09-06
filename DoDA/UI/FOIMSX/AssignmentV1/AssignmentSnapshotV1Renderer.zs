// ===========================================================================
// DoDA Assignment Snapshot V1 Renderer (Milestone C Presentation)
//
// Read-only presentation of accepted Assignment Snapshot V1 data within
// the FOIMS-X strategic interface session.
// ===========================================================================

class DoDAAssignmentSnapshotV1Renderer : Object
{
    const PANEL_X = 308;
    const PANEL_Y = 230;
    const PANEL_W = 318;
    const PANEL_H = 184;
    const MAX_VISIBLE_ROWS = 10;

    static ui void DrawVirtualRect(int vx, int vy, int vw, int vh, int col)
    {
        Vector2 vpos = (vx, vy);
        Vector2 vsize = (vw, vh);
        Vector2 rpos, rsize;
        [rpos, rsize] = Screen.VirtualToRealCoords(vpos, vsize, (640, 480), false, true);
        Screen.Dim(col, 1.0, int(rpos.x), int(rpos.y), int(rsize.x), int(rsize.y));
    }

    static ui void DrawSunkenPanel(int vx, int vy, int vw, int vh, int bgCol)
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);
        DrawVirtualRect(vx, vy, vw, 1, 0xFF080D14);
        DrawVirtualRect(vx, vy, 1, vh, 0xFF080D14);
        DrawVirtualRect(vx + vw - 1, vy, 1, vh, 0xFF2A3A52);
        DrawVirtualRect(vx, vy + vh - 1, vw, 1, 0xFF2A3A52);
    }

    static ui void DrawRaisedPanel(int vx, int vy, int vw, int vh, int bgCol)
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);
        DrawVirtualRect(vx, vy, vw, 1, 0xFF2A3A52);
        DrawVirtualRect(vx, vy, 1, vh, 0xFF2A3A52);
        DrawVirtualRect(vx + vw - 1, vy, 1, vh, 0xFF080D14);
        DrawVirtualRect(vx, vy + vh - 1, vw, 1, 0xFF080D14);
    }

    static ui void Render(DoDAAssignmentSnapshotV1ViewState viewState)
    {
        if (viewState == null)
        {
            return;
        }

        DrawSunkenPanel(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, 0xFF0A101C);

        DrawVirtualRect(PANEL_X + 2, PANEL_Y + 2, PANEL_W - 4, 18, 0xFF1A2638);
        Screen.DrawText(SmallFont, Font.CR_GOLD, PANEL_X + 8, PANEL_Y + 6, "ASSIGNMENT STATUS",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480);

        Vector2 realClipPos, realClipSize;
        [realClipPos, realClipSize] = Screen.VirtualToRealCoords((PANEL_X + 4, PANEL_Y + 22), (PANEL_W - 8, PANEL_H - 26), (640, 480), false, true);
        int clipLeft = int(realClipPos.x);
        int clipTop = int(realClipPos.y);
        int clipRight = int(realClipPos.x + realClipSize.x);
        int clipBottom = int(realClipPos.y + realClipSize.y);

        int state = viewState.CurrentViewState;

        if (state == EDoDAAssignmentViewState.VIEWSTATE_UNAVAILABLE)
        {
            Screen.DrawText(NewSmallFont, Font.CR_RED, PANEL_X + 8, PANEL_Y + 30, "ASSIGNMENT DATA UNAVAILABLE",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 44, "AWAITING STRATEGIC SNAPSHOT",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        if (state == EDoDAAssignmentViewState.VIEWSTATE_INCOMPATIBLE_VERSION)
        {
            Screen.DrawText(NewSmallFont, Font.CR_RED, PANEL_X + 8, PANEL_Y + 30, "ASSIGNMENT DATA VERSION INCOMPATIBLE",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 44, "NATIVE API VERSION MISMATCH",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        if (state == EDoDAAssignmentViewState.VIEWSTATE_STALE)
        {
            Screen.DrawText(NewSmallFont, Font.CR_YELLOW, PANEL_X + 8, PANEL_Y + 24, "ASSIGNMENT DATA STALE",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            if (viewState.GetDisplayRowCount() <= 0)
            {
                Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 38, "NO PREVIOUS SNAPSHOT RECORD",
                    DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                    DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                    DTA_Monospace, 1, DTA_Spacing, 9,
                    DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                    DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
                return;
            }
        }
        else
        {
            String metaText = String.Format("STRATEGIC TIME: %s MIN   ACTIVE: %d", viewState.ActiveStrategicMinutesText, viewState.TotalCount);
            Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 24, metaText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
        }

        if (viewState.TotalCount == 0 || viewState.GetDisplayRowCount() == 0)
        {
            Screen.DrawText(NewSmallFont, Font.CR_YELLOW, PANEL_X + 8, PANEL_Y + 40, "NO ACTIVE ASSIGNMENTS",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 54, "ALL PERSONNEL STANDING BY",
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
            return;
        }

        Screen.DrawText(NewSmallFont, Font.CR_WHITE, PANEL_X + 8, PANEL_Y + 36, "AGENT             TASK                  LOCATION        PROG",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        Screen.DrawText(NewSmallFont, Font.CR_DARKGRAY, PANEL_X + 8, PANEL_Y + 44, "------------------------------------------------------------",
            DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
            DTA_Monospace, 1, DTA_Spacing, 9,
            DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
            DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

        int displayCount = min(viewState.GetDisplayRowCount(), MAX_VISIBLE_ROWS);
        for (int i = 0; i < displayCount; i++)
        {
            let rec = viewState.GetDisplayRecord(i);
            if (rec == null) continue;

            double rowY = (PANEL_Y + 54) + (i * 11);

            String pName = rec.PersonDisplayName.MakeUpper();
            Screen.DrawText(NewSmallFont, Font.CR_WHITE, PANEL_X + 8, rowY, pName,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 17,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            String tTitle = rec.TaskTitle.MakeUpper();
            Screen.DrawText(NewSmallFont, Font.CR_CYAN, PANEL_X + 90, rowY, tTitle,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 21,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            String lName = rec.LocationDisplayName.MakeUpper();
            Screen.DrawText(NewSmallFont, Font.CR_GRAY, PANEL_X + 190, rowY, lName,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 15,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);

            String progText = String.Format("%d%%", rec.TaskProgress);
            int progCol = Font.CR_CYAN;
            if (rec.TaskProgress >= 100)
            {
                progCol = Font.CR_GREEN;
            }
            else if (rec.TaskProgress > 0)
            {
                progCol = Font.CR_YELLOW;
            }

            Screen.DrawText(NewSmallFont, progCol, PANEL_X + 266, rowY, progText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_TextLen, 5,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
        }

        if (viewState.GetDisplayRowCount() > MAX_VISIBLE_ROWS)
        {
            int overflow = viewState.GetDisplayRowCount() - MAX_VISIBLE_ROWS;
            String overflowText = String.Format("+%d ADDITIONAL ACTIVE ASSIGNMENTS", overflow);
            Screen.DrawText(NewSmallFont, Font.CR_DARKGRAY, PANEL_X + 8, PANEL_Y + 168, overflowText,
                DTA_VirtualWidth, 640, DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5, DTA_ScaleY, 0.5,
                DTA_Monospace, 1, DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft, DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop, DTA_ClipBottom, clipBottom);
        }
    }
}
