/*//////////////////////////|
// DoDA/MissionSystem/MissionOverlay.zs
*///////////////////////////|

class DoDAMissionOverlay : EventHandler
{
    override void RenderOverlay(RenderEvent e)
    {
        Font font = Font.GetFont("DoDAPalmFont");
        int white = Font.FindFontColor("White");

        String titleText = "DoDA overlay probe";
        String missionText = "MISSION: UNKNOWN";

        DoDAMissionDirector director = DoDAMissionDirector(EventHandler.Find("DoDAMissionDirector"));
        if (director != null)
        {
            switch (director.GetMissionResult())
            {
            case MISSION_PENDING:
                missionText = "MISSION: PENDING";
                break;

            case MISSION_IN_PROGRESS:
                missionText = "MISSION: IN PROGRESS";
                break;

            case MISSION_SUCCESS:
                missionText = "MISSION: SUCCESS";
                break;

            case MISSION_FAILURE:
                missionText = "MISSION: FAILURE";
                break;

            case MISSION_ABORTED:
                missionText = "MISSION: ABORTED";
                break;
            }
        }

        int margin = 0;
        int screenW = Screen.GetWidth();
        int lineH = font.GetHeight();

        int rightEdge = screenW - margin;

        int titleX = rightEdge - font.StringWidth(titleText);
        int missionX = rightEdge - font.StringWidth(missionText);

        int titleY = margin;
        int missionY = titleY + lineH + 2;

        Screen.DrawText(font, white, titleX, titleY, titleText);
        Screen.DrawText(font, white, missionX, missionY, missionText);
    }
}