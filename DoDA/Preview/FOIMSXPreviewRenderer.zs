/*//////////////////////////|
// DoDA/Preview/FOIMSXPreviewRenderer.zs
//
// FOIMS-X Standalone Preview: read-only faux telemetry renderer.
//
// Boundary:
//   - Draws only standalone preview telemetry.
//   - Reads only DoDAFOIMSXPreviewSession and DoDAFOIMSXPreviewModel.
//   - Does not call native DoDA.
//   - Does not persist state.
//   - Does not handle input.
//   - Does not define a terminal actor.
//   - Does not alter the existing MAP01 FOIMS-X renderer.
*///////////////////////////|

class DoDAFOIMSXPreviewRenderer : EventHandler
{
    override void RenderOverlay(RenderEvent e)
    {
        if (!DoDAFOIMSXPreviewSession.IsPreviewActive())
        {
            return;
        }

        int elapsedTics = DoDAFOIMSXPreviewSession.GetPreviewElapsedTics();
        int focusedMetric = DoDAFOIMSXPreviewSession.GetFocusedMetric();

        // 1. Fullscreen Opaque Background Fill
        Screen.Dim(
            0xFF000814,
            1.0,
            0,
            0,
            Screen.GetWidth(),
            Screen.GetHeight()
        );

        // 2. 640x480 Virtual Outer Frame
        DrawRaisedPanel(10, 10, 620, 460, 0xFF182234);

        // 3. Title Bar (Active Navy Banner)
        DrawVirtualRect(14, 14, 612, 20, 0xFF0A3678);
        Screen.DrawText(
            SmallFont,
            Font.CR_WHITE,
            20,
            18,
            "FOIMS-X   |   " .. DoDAFOIMSXPreviewConstants.GetModeLabel() .. "   |   " .. DoDAFOIMSXPreviewConstants.GetAuthorityWarning(),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        // 4. Inert Top Menu Strip
        DrawVirtualRect(14, 36, 612, 18, 0xFF121B2A);
        Screen.DrawText(
            SmallFont,
            Font.CR_GRAY,
            20,
            40,
            DoDAFOIMSXPreviewConstants.GetTopMenuLabel(),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        // 5. Three Telemetry Columns (Y: 58..350, Height: 292)
        // Column 1: Operations (X: 16, Width: 198)
        RenderColumn(
            16, 58, 198, 292,
            DoDAFOIMSXPreviewConstants.GetOperationsTitle(),
            DoDAFOIMSXPreviewModel.METRIC_OPERATIONAL_PRESSURE,
            DoDAFOIMSXPreviewModel.METRIC_THREAT_SIGNAL,
            elapsedTics,
            focusedMetric
        );

        // Column 2: Analysis (X: 220, Width: 198)
        RenderColumn(
            220, 58, 198, 292,
            DoDAFOIMSXPreviewConstants.GetAnalysisTitle(),
            DoDAFOIMSXPreviewModel.METRIC_INCOMING_REPORTS,
            DoDAFOIMSXPreviewModel.METRIC_RESEARCH_BACKLOG,
            elapsedTics,
            focusedMetric
        );

        // Column 3: Logistics (X: 424, Width: 202)
        RenderColumn(
            424, 58, 202, 292,
            DoDAFOIMSXPreviewConstants.GetLogisticsTitle(),
            DoDAFOIMSXPreviewModel.METRIC_ASSET_AVAILABILITY,
            DoDAFOIMSXPreviewModel.METRIC_NETWORK_STATUS,
            elapsedTics,
            focusedMetric
        );

        // 6. Bottom Notice Feed & Status Area (Y: 356..444)
        DrawSunkenPanel(16, 356, 610, 88, 0xFF0A101C);
        DrawVirtualRect(18, 358, 606, 18, 0xFF1A2638);
        Screen.DrawText(
            SmallFont,
            Font.CR_GOLD,
            24,
            362,
            DoDAFOIMSXPreviewConstants.GetNoticeTitle(),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        // Notice message
        String noticeText = DoDAFOIMSXPreviewModel.GetSystemNotice(elapsedTics);
        Screen.DrawText(
            SmallFont,
            Font.CR_GREEN,
            24,
            384,
            ">> " .. noticeText,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        int seconds = DoDAFOIMSXPreviewModel.GetElapsedSeconds(elapsedTics);
        int nextNotice = 9 - (seconds % 9);
        if (nextNotice <= 0) nextNotice = 9;

        Screen.DrawText(
            NewSmallFont,
            Font.CR_DARKGRAY,
            24,
            404,
            String.Format("FEED CYCLE: 9 SEC   |   NEXT NOTICE: %d SEC   |   UPTIME: %d SEC", nextNotice, seconds),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );

        Screen.DrawText(
            NewSmallFont,
            Font.CR_GRAY,
            24,
            422,
            DoDAFOIMSXPreviewConstants.GetNavigationHint(),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );

        // 7. Footer Status Line
        DrawSunkenPanel(16, 448, 610, 18, 0xFF121B2A);
        Screen.DrawText(
            NewSmallFont,
            Font.CR_DARKGRAY,
            20,
            452,
            DoDAFOIMSXPreviewConstants.GetStatusLine(),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );
    }

    private ui void RenderColumn(
        double colX,
        double colY,
        double colW,
        double colH,
        String colTitle,
        int startMetric,
        int endMetric,
        int elapsedTics,
        int focusedMetric
    )
    {
        DrawSunkenPanel(colX, colY, colW, colH, 0xFF0A101C);
        DrawVirtualRect(colX + 2, colY + 2, colW - 4, 18, 0xFF1A2638);

        Screen.DrawText(
            SmallFont,
            Font.CR_GOLD,
            colX + 8,
            colY + 6,
            colTitle,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        double cardY = colY + 24;
        double cardH = 84;

        for (int m = startMetric; m <= endMetric; m++)
        {
            RenderMetricCard(colX + 4, cardY, colW - 8, cardH, m, elapsedTics, (m == focusedMetric));
            cardY += cardH + 4;
        }
    }

    private ui void RenderMetricCard(
        double cardX,
        double cardY,
        double cardW,
        double cardH,
        int metric,
        int elapsedTics,
        bool isFocused
    )
    {
        Color bg = isFocused ? 0xFF142236 : 0xFF0F1826;
        DrawVirtualRect(cardX, cardY, cardW, cardH, bg);
        DrawCardBorder(cardX, cardY, cardW, cardH, isFocused ? 0xFF386090 : 0xFF1E2D42);

        String label = DoDAFOIMSXPreviewModel.GetMetricLabel(metric);
        int value = DoDAFOIMSXPreviewModel.GetValue(metric, elapsedTics);
        String unit = DoDAFOIMSXPreviewModel.GetMetricUnit(metric);
        String trend = DoDAFOIMSXPreviewModel.GetTrendLabel(metric, elapsedTics);
        int trendColor = GetTrendColor(trend);
        int updateBand = DoDAFOIMSXPreviewModel.GetUpdateBandSeconds(metric);

        // Metric Label
        Screen.DrawText(
            NewSmallFont,
            Font.CR_WHITE,
            cardX + 6,
            cardY + 6,
            label,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );

        // Value Readout
        String valueStr = String.Format("%d%s", value, unit);
        Screen.DrawText(
            SmallFont,
            Font.CR_CYAN,
            cardX + 6,
            cardY + 20,
            valueStr,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480
        );

        // State / Trend
        Screen.DrawText(
            NewSmallFont,
            trendColor,
            cardX + cardW - 74,
            cardY + 22,
            trend,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );

        // Progress / Pulse Bar
        int barPercent = GetMetricBarPercent(metric, value, elapsedTics);
        DrawVirtualRect(cardX + 6, cardY + 42, cardW - 12, 8, 0xFF060B12);
        DrawVirtualRect(
            cardX + 7,
            cardY + 43,
            int((cardW - 14) * barPercent / 100.0),
            6,
            GetBarColor(metric, barPercent, elapsedTics)
        );

        // Rate & Detail Footer
        Screen.DrawText(
            NewSmallFont,
            Font.CR_DARKGRAY,
            cardX + 6,
            cardY + 56,
            String.Format("RATE: %ds   |   %s", updateBand, DoDAFOIMSXPreviewModel.GetMetricDetail(metric)),
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, 0.5,
            DTA_ScaleY, 0.5,
            DTA_Monospace, 1,
            DTA_Spacing, 9
        );
    }

    private static ui int GetMetricBarPercent(int metric, int value, int elapsedTics)
    {
        if (metric == DoDAFOIMSXPreviewModel.METRIC_COMMUNICATIONS)
        {
            // Communications Pulse: sub-second sine-like pulse
            int subTics = elapsedTics % 35;
            double pulse = sin(subTics * (360.0 / 35.0));
            int pulseOffset = int(pulse * 15.0);
            return ClampValue(value + pulseOffset, 10, 100);
        }

        switch (metric)
        {
            case DoDAFOIMSXPreviewModel.METRIC_INCOMING_REPORTS:
                return ClampValue(value * 14, 0, 100);

            case DoDAFOIMSXPreviewModel.METRIC_ANALYSIS_QUEUE:
            case DoDAFOIMSXPreviewModel.METRIC_RESEARCH_BACKLOG:
                return ClampValue(value * 6, 0, 100);
        }

        return ClampValue(value, 0, 100);
    }

    private static ui Color GetBarColor(int metric, int percent, int elapsedTics)
    {
        if (metric == DoDAFOIMSXPreviewModel.METRIC_COMMUNICATIONS)
        {
            int subTics = elapsedTics % 35;
            if (subTics < 18)
            {
                return 0xFF00D0FF; // High cyan pulse
            }
            return 0xFF0070AA; // Medium cyan
        }

        if (percent >= 75)
        {
            return 0xFFC00000;
        }

        if (percent >= 50)
        {
            return 0xFFC0A000;
        }

        return 0xFF00A040;
    }

    private static ui int GetTrendColor(String trend)
    {
        if (trend == "CRITICAL")
        {
            return Font.CR_RED;
        }

        if (trend == "ELEVATED" ||
            trend == "RISING" ||
            trend == "DECLINING" ||
            trend == "LIMITED" ||
            trend == "GUARDED" ||
            trend == "REROUTING")
        {
            return Font.CR_YELLOW;
        }

        if (trend == "LOW" ||
            trend == "NOMINAL" ||
            trend == "OPTIMAL" ||
            trend == "RECOVERING" ||
            trend == "CLEARING" ||
            trend == "DRAINING")
        {
            return Font.CR_GREEN;
        }

        if (trend == "ACTIVE" ||
            trend == "BUILDING" ||
            trend == "ACCUMULATING" ||
            trend == "ALLOCATING" ||
            trend == "RECEIVING" ||
            trend == "ELEVATING" ||
            trend == "PROCESSING" ||
            trend == "REVIEWING")
        {
            return Font.CR_CYAN;
        }

        return Font.CR_GRAY;
    }

    private static ui int ClampValue(int value, int minimum, int maximum)
    {
        if (value < minimum)
        {
            return minimum;
        }

        if (value > maximum)
        {
            return maximum;
        }

        return value;
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
            (vx, vy),
            (vw, vh),
            (640, 480),
            false,
            true
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

    private static ui void DrawCardBorder(
        double vx,
        double vy,
        double vw,
        double vh,
        Color borderCol
    )
    {
        Vector2 realPos, realSize;
        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy),
            (vw, vh),
            (640, 480),
            false,
            true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x1, y0, borderCol);
        Screen.DrawLine(x0, y0, x0, y1, borderCol);
        Screen.DrawLine(x0, y1, x1, y1, borderCol);
        Screen.DrawLine(x1, y0, x1, y1, borderCol);
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
            (vx, vy),
            (vw, vh),
            (640, 480),
            false,
            true
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
            (vx, vy),
            (vw, vh),
            (640, 480),
            false,
            true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x0, y1, 0xFF080D14);
        Screen.DrawLine(x0, y0, x1, y0, 0xFF080D14);
        Screen.DrawLine(x0, y1, x1, y1, 0xFF364860);
        Screen.DrawLine(x1, y0, x1, y1, 0xFF364860);
    }
}
