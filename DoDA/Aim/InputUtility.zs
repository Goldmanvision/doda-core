///////////////////////////
// DoDA/Aim/InputUtility.zs
///////////////////////////

class DoDAInputUtility
{
    static double ConsumeFloatBuffer(PlayerInfo player, Name cvarName, double fallback = 0.0)
    {
        if (player == null)
        {
            return fallback;
        }

        CVar cv = CVar.GetCVar(cvarName, player);
        if (cv == null)
        {
            return fallback;
        }

        double val = cv.GetFloat();
        cv.SetFloat(0.0);
        return val;
    }

    static double ReadFloatSetting(PlayerInfo player, Name cvarName, double fallback = 0.0)
    {
        if (player == null)
        {
            return fallback;
        }

        CVar cv = CVar.GetCVar(cvarName, player);
        if (cv == null)
        {
            return fallback;
        }

        return cv.GetFloat();
    }

    static bool ReadBoolSetting(PlayerInfo player, Name cvarName, bool fallback = false)
    {
        if (player == null)
        {
            return fallback;
        }

        CVar cv = CVar.GetCVar(cvarName, player);
        if (cv == null)
        {
            return fallback;
        }

        return cv.GetBool();
    }

    static bool SafeWriteFloat(PlayerInfo player, Name cvarName, double value)
    {
        if (player == null)
        {
            return false;
        }

        CVar cv = CVar.GetCVar(cvarName, player);
        if (cv == null)
        {
            return false;
        }

        cv.SetFloat(value);
        return true;
    }
}
