///////////////////////////
// DoDA/UI/FieldAgent/HUDTapline.zs
///////////////////////////

class DoDAHUDTapline : Object
{
    private String LastLoggedKey;
    private String LastLoggedSource;

    void LogHUDSelection(
        string sourceLabel,
        String missionText,
        String statusText,
        String progressText,
        String phaseText,
        String objectiveText
    )
    {
        String key =
            level.MapName .. "|" ..
            sourceLabel .. "|" ..
            missionText .. "|" ..
            statusText .. "|" ..
            progressText .. "|" ..
            phaseText .. "|" ..
            objectiveText;

        if (LastLoggedKey == key && LastLoggedSource == sourceLabel)
        {
            return;
        }

        LastLoggedKey = key;
        LastLoggedSource = sourceLabel;

        Console.Printf(
            "DoDA HUD Snapshot [Draw source change] Source=%s Map=%s %s | %s | %s | %s | %s",
            sourceLabel,
            level.MapName,
            missionText,
            statusText,
            progressText,
            phaseText,
            objectiveText
        );
    }

    void DrawTapline(PlayerInfo currentPlayer)
    {
        Font font = Font.GetFont("DoDAPalmFont");
        int black = Font.FindFontColor("Black");

        String titleText = "FBI: DODA TAPLINE CONNECTED";
        String missionText = "MISSION: UNKNOWN";
        String statusText = "STATUS: UNKNOWN";
        String progressText = "PROGRESS: 0%";
        String phaseText = "PHASE: UNKNOWN";
        String objectiveText = "OBJECTIVE: UNKNOWN";
        String sourceLabel = "None";

        DoDAMissionDirector director =
            DoDAMissionDirector(EventHandler.Find("DoDAMissionDirector"));

        PlayerPawn playerPawn = currentPlayer != null ? currentPlayer.mo : null;
        DoDALastMissionReport report = null;

        if (playerPawn != null)
        {
            report = DoDALastMissionReport(
                playerPawn.FindInventory("DoDALastMissionReport")
            );
        }

        bool hasReport = report != null && report.GetHasReport();

        if (level.MapName == "MAP02")
        {
            if (hasReport)
            {
                sourceLabel = "LastMissionReport";

                missionText = "MISSION: " .. report.GetReportMissionName();
                progressText = "PROGRESS: " .. report.GetReportPercentComplete() .. "%";
                objectiveText = "OBJECTIVE: " .. report.GetReportObjective();

                switch (report.GetReportResult())
                {
                case MISSION_PENDING:
                    statusText = "STATUS: PENDING";
                    break;

                case MISSION_IN_PROGRESS:
                    statusText = "STATUS: IN PROGRESS";
                    break;

                case MISSION_SUCCESS:
                    statusText = "STATUS: SUCCESS";
                    break;

                case MISSION_FAILURE:
                    statusText = "STATUS: FAILURE";
                    break;

                case MISSION_ABORTED:
                    statusText = "STATUS: ABORTED";
                    break;

                default:
                    statusText = "STATUS: UNKNOWN";
                    break;
                }

                switch (report.GetReportPhase())
                {
                case 1:
                    phaseText = "PHASE: OBJECTIVE";
                    break;

                case 2:
                    phaseText = "PHASE: EXTRACTION";
                    break;

                default:
                    phaseText = "PHASE: UNKNOWN";
                    break;
                }
            }
            else
            {
                sourceLabel = "DebriefCleared";
                missionText = "MISSION: DEBRIEF CLOSED";
                statusText = "STATUS: RETURNED TO FIELD";
                progressText = "PROGRESS: 0%";
                phaseText = "PHASE: COMPLETE";
                objectiveText = "OBJECTIVE: await new deployment.";
            }
        }
        else if (director != null)
        {
            sourceLabel = "MissionDirector";

            missionText = "MISSION: " .. director.GetMissionName();
            progressText = "PROGRESS: " .. director.GetMissionPercentComplete() .. "%";
            objectiveText = "OBJECTIVE: " .. director.GetMissionDescription();

            switch (director.GetMissionResult())
            {
            case MISSION_PENDING:
                statusText = "STATUS: PENDING";
                break;

            case MISSION_IN_PROGRESS:
                statusText = "STATUS: IN PROGRESS";
                break;

            case MISSION_SUCCESS:
                statusText = "STATUS: SUCCESS";
                break;

            case MISSION_FAILURE:
                statusText = "STATUS: FAILURE";
                break;

            case MISSION_ABORTED:
                statusText = "STATUS: ABORTED";
                break;

            default:
                statusText = "STATUS: UNKNOWN";
                break;
            }

            switch (director.GetMissionPhase())
            {
            case 1:
                phaseText = "PHASE: OBJECTIVE";
                break;

            case 2:
                phaseText = "PHASE: EXTRACTION";
                break;

            default:
                phaseText = "PHASE: UNKNOWN";
                break;
            }
        }
        else
        {
            sourceLabel = "MissionDirectorUnavailable";
            missionText = "MISSION: TAPLINE OFFLINE";
            statusText = "STATUS: WAITING FOR DIRECTOR";
            progressText = "PROGRESS: 0%";
            phaseText = "PHASE: UNKNOWN";
            objectiveText = "OBJECTIVE: awaiting mission director.";
        }

        LogHUDSelection(
            sourceLabel,
            missionText,
            statusText,
            progressText,
            phaseText,
            objectiveText
        );

        int panelWidth = 540;
        int panelHeight = 225;
        int margin = 24;
        int padding = 16;
        int lineGap = 2;

        int panelX = Screen.GetWidth() - panelWidth - margin;
        int panelY = margin;

        int textX = panelX + padding + 4;

        int titleY = panelY + padding;
        int missionY = titleY + font.GetHeight() + lineGap;
        int statusY = missionY + font.GetHeight() + lineGap;
        int progressY = statusY + font.GetHeight() + lineGap;
        int phaseY = progressY + font.GetHeight() + lineGap;
        int objectiveY = phaseY + font.GetHeight() + lineGap;

        Screen.Clear(
            panelX,
            panelY,
            panelX + panelWidth,
            panelY + panelHeight,
            Color(196, 207, 163)
        );

        Screen.DrawThickLine(panelX, panelY, panelX + panelWidth, panelY, 8.0, Color(0, 0, 0));
        Screen.DrawThickLine(panelX, panelY + panelHeight, panelX + panelWidth, panelY + panelHeight, 8.0, Color(0, 0, 0));
        Screen.DrawThickLine(panelX, panelY, panelX, panelY + panelHeight, 8.0, Color(0, 0, 0));
        Screen.DrawThickLine(panelX + panelWidth, panelY, panelX + panelWidth, panelY + panelHeight, 8.0, Color(0, 0, 0));

        int inner = 6;
        Color innerBorderColor = Color(155, 188, 15);

        Screen.DrawThickLine(panelX + inner, panelY + inner, panelX + panelWidth - inner, panelY + inner, 8.0, innerBorderColor);
        Screen.DrawThickLine(panelX + inner, panelY + panelHeight - inner, panelX + panelWidth - inner, panelY + panelHeight - inner, 8.0, innerBorderColor);
        Screen.DrawThickLine(panelX + inner, panelY + inner, panelX + inner, panelY + panelHeight - inner, 8.0, innerBorderColor);
        Screen.DrawThickLine(panelX + panelWidth - inner, panelY + inner, panelX + panelWidth - inner, panelY + panelHeight - inner, 8.0, innerBorderColor);

        Screen.DrawText(font, black, textX, titleY, titleText);
        Screen.DrawText(font, black, textX, missionY, missionText);
        Screen.DrawText(font, black, textX, statusY, statusText);
        Screen.DrawText(font, black, textX, progressY, progressText);
        Screen.DrawText(font, black, textX, phaseY, phaseText);
        Screen.DrawText(font, black, textX, objectiveY, objectiveText);
    }
}