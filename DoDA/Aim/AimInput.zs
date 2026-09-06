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

        CVar mouseXCVar = CVar.GetCVar(
            'doda_raw_mouse_x',
            players[consoleplayer]
        );

        CVar mouseYCVar = CVar.GetCVar(
            'doda_raw_mouse_y',
            players[consoleplayer]
        );

        if (mouseXCVar)
        {
            mouseXCVar.SetFloat(
                mouseXCVar.GetFloat() + e.MouseX
            );
        }

        if (mouseYCVar)
        {
            mouseYCVar.SetFloat(
                mouseYCVar.GetFloat() + e.MouseY
            );
        }

        // FieldAgent consumes these values and applies deadzone/overflow motion.
        return true;
    }
}