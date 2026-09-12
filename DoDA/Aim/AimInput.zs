///////////////////////////
// DoDA/Aim/AimInput.zs
///////////////////////////

class DoDAAimInput : EventHandler
{
    override void OnRegister()
    {
        RequireMouse = true;
        SetOrder(-100);
    }

    override bool InputProcess(InputEvent e)
    {
        if (e.Type != InputEvent.Type_Mouse)
        {
            return false;
        }

        if (e.MouseX == 0 && e.MouseY == 0)
        {
            return false;
        }

        let agent = FieldAgent(players[consoleplayer].mo);

        if (agent == null || !agent.IsDeadzoneAimActive())
        {
            return false;
        }

        PlayerInfo pi = players[consoleplayer];

        double curX = DoDAInputUtility.ReadFloatSetting(pi, 'doda_raw_mouse_x', 0.0);
        double curY = DoDAInputUtility.ReadFloatSetting(pi, 'doda_raw_mouse_y', 0.0);

        DoDAInputUtility.SafeWriteFloat(pi, 'doda_raw_mouse_x', curX + e.MouseX);
        DoDAInputUtility.SafeWriteFloat(pi, 'doda_raw_mouse_y', curY + e.MouseY);

        // FieldAgent consumes these values and applies deadzone/overflow motion.
        return true;
    }
}