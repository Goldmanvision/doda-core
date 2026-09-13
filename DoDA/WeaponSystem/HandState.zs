///////////////////////////
// DoDA/WeaponSystem/HandState.zs
///////////////////////////

enum EDoDACombatMode
{
    DODA_MODE_SINGLE = 0,
    DODA_MODE_AKIMBO = 1,
    DODA_MODE_DUALWIELD = 2
};

enum EDoDAHand
{
    DODA_HAND_LEFT = 0,
    DODA_HAND_RIGHT = 1
};

class DoDAHandState : Object play
{
    // Minimal foundation state
    Weapon LeftWeapon;
    Weapon RightWeapon;
    int CombatMode;
    bool Layer2Active;
    int FocusedHand;

    const PSP_DODA_SECONDARY = 2;

    void Init(Actor ownerActor)
    {
        ResetState();
    }

    void ResetState()
    {
        LeftWeapon = null;
        RightWeapon = null;
        CombatMode = DODA_MODE_SINGLE;
        Layer2Active = false;
        FocusedHand = DODA_HAND_RIGHT;
    }

    // Centralized Layer 2 setup path for companion weapon (B92 Akimbo)
    bool SetupB92CompanionLayer(PlayerInfo p, State readyState, Weapon leftW, Weapon rightW)
    {
        if (p == null || readyState == null)
        {
            return false;
        }

        p.SetPSprite(PSP_DODA_SECONDARY, readyState);
        let psp = p.GetPSprite(PSP_DODA_SECONDARY);
        if (psp != null)
        {
            psp.x = -48.0;
            psp.y = 8.0;
            psp.bMirror = false;
            psp.bAddBob = true;
            psp.bAddWeapon = false; // MANDATORY INVARIANT
        }

        Layer2Active = true;
        CombatMode = DODA_MODE_AKIMBO;
        LeftWeapon = leftW;
        RightWeapon = rightW;
        FocusedHand = DODA_HAND_RIGHT;

        return true;
    }

    // Centralized Layer 2 teardown path
    void ClearLayer2(PlayerInfo p)
    {
        if (p != null)
        {
            p.SetPSprite(PSP_DODA_SECONDARY, null);
        }

        if (DoDA.IsAkimboActive())
        {
            DoDA.ExitAkimbo();
        }

        Layer2Active = false;
        CombatMode = DODA_MODE_SINGLE;
        LeftWeapon = null;
        RightWeapon = null;
        FocusedHand = DODA_HAND_RIGHT;
    }

    // Validates whether current Layer 2 owner remains valid (e.g. during weapon switch, deselect, or death)
    void ValidateLayer2(PlayerInfo p)
    {
        if (p == null)
        {
            return;
        }

        // If Layer 2 is active or akimbo is active, verify that the active ReadyWeapon is a valid companion owner
        if (Layer2Active || DoDA.IsAkimboActive() || p.GetPSprite(PSP_DODA_SECONDARY) != null)
        {
            // Check if player is dead
            if (p.mo != null && p.mo.health <= 0)
            {
                ClearLayer2(p);
                return;
            }

            // If switching away (PendingWeapon is set to a non-akimbo weapon)
            if (p.PendingWeapon != WP_NOCHANGE && p.PendingWeapon != null)
            {
                if (!(p.PendingWeapon is "DoDAPistol"))
                {
                    ClearLayer2(p);
                    return;
                }
            }

            // Check if current ready weapon is not a valid akimbo weapon (and not currently switching to another valid one)
            if (!(p.ReadyWeapon is "DoDAPistol") && (p.PendingWeapon == WP_NOCHANGE || p.PendingWeapon == null))
            {
                ClearLayer2(p);
                return;
            }
        }
    }

    // Full lifecycle reset (death, respawn, map load/unload)
    void ResetLifecycle(PlayerInfo p)
    {
        ClearLayer2(p);
        ResetState();
    }

    clearscope bool IsLayer2Active() const
    {
        return Layer2Active;
    }

    clearscope int GetCombatMode() const
    {
        return CombatMode;
    }

    clearscope Weapon GetLeftWeapon() const
    {
        return LeftWeapon;
    }

    clearscope Weapon GetRightWeapon() const
    {
        return RightWeapon;
    }

    clearscope int GetFocusedHand() const
    {
        return FocusedHand;
    }
}
