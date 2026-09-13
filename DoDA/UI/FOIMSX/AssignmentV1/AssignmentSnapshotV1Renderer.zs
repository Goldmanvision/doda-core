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

    static ui void Render(DoDAAssignmentSnapshotV1ViewState viewState)
    {
        if (viewState == null)
        {
            return;
        }

        DoDAFOIMSXDrawingHelpers.DrawSunkenPanel(PANEL_X, PANEL_Y, PANEL_W, PANEL_H, 0xFF0A101C);

        DoDAFOIMSXDrawingHelpers.DrawVirtualRect(PANEL_X + 2, PANEL_Y + 2, PANEL_W - 4, 18, 0xFF1A2638);
        DoDAFOIMSXDrawingHelpers.DrawVirtualText(SmallFont, Font.CR_GOLD, PANEL_X + 8, PANEL_Y + 6, "ASSIGNMENT STATUS", 0.5, 0.5);

        int clipLeft, clipTop, clipRight, clipBottom;
        DoDAFOIMSXDrawingHelpers.GetRealClipRect(PANEL_X + 4, PANEL_Y + 22, PANEL_W - 8, PANEL_H - 26, clipLeft, clipTop, clipRight, clipBottom);

        int state = viewState.CurrentViewState;

        if (state == ASSIGNMENT_VIEWSTATE_UNAVAILABLE)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_RED, PANEL_X + 8, PANEL_Y + 30, "ASSIGNMENT DATA UNAVAILABLE",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 44, "AWAITING STRATEGIC SNAPSHOT",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        if (state == VIEWSTATE_INCOMPATIBLE_VERSION)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_RED, PANEL_X + 8, PANEL_Y + 30, "ASSIGNMENT DATA VERSION INCOMPATIBLE",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 44, "NATIVE API VERSION MISMATCH",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        if (state == ASSIGNMENT_VIEWSTATE_STALE)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, PANEL_X + 8, PANEL_Y + 24, "ASSIGNMENT DATA STALE",
                clipLeft, clipTop, clipRight, clipBottom);

            if (viewState.GetDisplayRowCount() <= 0)
            {
                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 38, "NO PREVIOUS SNAPSHOT RECORD",
                    clipLeft, clipTop, clipRight, clipBottom);
                return;
            }
        }
        else
        {
            String metaText = String.Format("STRATEGIC TIME: %s MIN   ACTIVE: %d", viewState.ActiveStrategicMinutesText, viewState.TotalCount);
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 24, metaText,
                clipLeft, clipTop, clipRight, clipBottom);
        }

        if (viewState.TotalCount == 0 || viewState.GetDisplayRowCount() == 0)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, PANEL_X + 8, PANEL_Y + 40, "NO ACTIVE ASSIGNMENTS",
                clipLeft, clipTop, clipRight, clipBottom);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 8, PANEL_Y + 54, "ALL PERSONNEL STANDING BY",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, PANEL_X + 8, PANEL_Y + 36, "AGENT             TASK                  LOCATION        PROG",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, PANEL_X + 8, PANEL_Y + 44, "------------------------------------------------------------",
            clipLeft, clipTop, clipRight, clipBottom);

        int displayCount = min(viewState.GetDisplayRowCount(), MAX_VISIBLE_ROWS);
        for (int i = 0; i < displayCount; i++)
        {
            let rec = viewState.GetDisplayRecord(i);
            if (rec == null) continue;

            double rowY = (PANEL_Y + 54) + (i * 11);

            String pName = rec.PersonDisplayName.MakeUpper();
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, PANEL_X + 8, rowY, pName,
                clipLeft, clipTop, clipRight, clipBottom, 17);

            String tTitle = rec.TaskTitle.MakeUpper();
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_CYAN, PANEL_X + 90, rowY, tTitle,
                clipLeft, clipTop, clipRight, clipBottom, 21);

            String lName = rec.LocationDisplayName.MakeUpper();
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, PANEL_X + 190, rowY, lName,
                clipLeft, clipTop, clipRight, clipBottom, 15);

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

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, progCol, PANEL_X + 266, rowY, progText,
                clipLeft, clipTop, clipRight, clipBottom, 5);
        }

        if (viewState.GetDisplayRowCount() > MAX_VISIBLE_ROWS)
        {
            int overflow = viewState.GetDisplayRowCount() - MAX_VISIBLE_ROWS;
            String overflowText = String.Format("+%d ADDITIONAL ACTIVE ASSIGNMENTS", overflow);
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, PANEL_X + 8, PANEL_Y + 168, overflowText,
                clipLeft, clipTop, clipRight, clipBottom);
        }
    }
}
