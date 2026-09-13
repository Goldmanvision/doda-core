///////////////////////////
// DoDA/UI/FieldAgent/HUD.zs
///////////////////////////

class DoDAHUD : BaseStatusBar
{
    private DoDAHUDTapline m_Tapline;
    private DoDAHUDDeadzone m_Deadzone;
    private DoDAHUDWeapon m_Weapon;

    override void Init()
    {
        Super.Init();

        m_Tapline = new("DoDAHUDTapline");
        m_Deadzone = new("DoDAHUDDeadzone");
        m_Weapon = new("DoDAHUDWeapon");
    }

    void DrawWeaponHUD()
    {
        if (
            m_Weapon == null
            || CPlayer == null
            || CPlayer.mo == null
        )
        {
            return;
        }

        Weapon readyWeapon = CPlayer.ReadyWeapon;

        let primary = DoDAWeaponHUDBridge.GetActiveWeaponData(
            readyWeapon
        );

        if (primary == null || !primary.Available)
        {
            return;
        }

        let companion = DoDAWeaponHUDBridge.GetCompanionWeaponData(
            CPlayer.mo,
            readyWeapon
        );

        int reserveRounds =
            DoDAWeaponHUDBridge.GetReserveRounds(
                readyWeapon
            );

        m_Weapon.DrawWeaponReadout(
            primary,
            companion,
            reserveRounds
        );
    }

    override void Draw(int state, double ticFrac)
    {
        Super.Draw(state, ticFrac);

        if (m_Tapline != null)
        {
            m_Tapline.DrawTapline(CPlayer);
        }

        if (CPlayer == null || CPlayer.mo == null)
        {
            return;
        }

        DrawWeaponHUD();

        let agent = FieldAgent(CPlayer.mo);

        if (agent == null || !agent.IsDeadzoneAimActive())
        {
            return;
        }

        if (m_Deadzone == null)
        {
            return;
        }

        m_Deadzone.DrawDeadzone(
            true,
            agent.GetDeadzoneYawGap(),
            agent.GetDeadzonePitchGap(),
            agent.GetDeadzoneYawLimit(),
            agent.GetDeadzonePitchLimit(),
            CPlayer.FOV,
            Screen.GetWidth(),
            Screen.GetHeight(),
            DeadzoneHUDBridge.GetLeanOffset(CPlayer.mo)
        );
    }

    override bool ProcessNotify(EPrintLevel printlevel, String outline)
    {
        if (DoDAFOIMSXHostLifecycleProbe.IsFOIMSXActive())
        {
            return true; // Suppress top-left on-screen notify string drawing while FOIMS-X is active
        }

        return Super.ProcessNotify(printlevel, outline);
    }
}