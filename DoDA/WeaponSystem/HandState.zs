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
    bool EnteredFromLeft;
    int PendingLeftSlot;
    int PendingRightSlot;

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
        EnteredFromLeft = false;
        PendingLeftSlot = 0;
        PendingRightSlot = 0;
    }

    clearscope bool IsAkimboActive() const
    {
        return CombatMode == DODA_MODE_AKIMBO && Layer2Active;
    }

    clearscope bool IsLayer2Active() const
    {
        return Layer2Active;
    }

    clearscope int GetCombatMode() const
    {
        return CombatMode;
    }

    Weapon GetLeftWeapon(Actor ownerActor = null)
    {
        if (LeftWeapon != null)
        {
            return LeftWeapon;
        }
        if (ownerActor != null)
        {
            return Weapon(ownerActor.FindInventory('DoDAB92Left'));
        }
        return null;
    }

    Weapon GetRightWeapon(Actor ownerActor = null)
    {
        if (RightWeapon != null)
        {
            return RightWeapon;
        }
        if (ownerActor != null)
        {
            return Weapon(ownerActor.FindInventory('DoDAB92Right'));
        }
        return null;
    }

    DoDAPistol GetLeftPistol(Actor ownerActor = null)
    {
        return DoDAPistol(GetLeftWeapon(ownerActor));
    }

    DoDAPistol GetRightPistol(Actor ownerActor = null)
    {
        return DoDAPistol(GetRightWeapon(ownerActor));
    }

    clearscope int GetFocusedHand() const
    {
        return FocusedHand;
    }

    clearscope bool WasEnteredFromLeft() const
    {
        return EnteredFromLeft;
    }

    void SetEnteredFromLeft(bool fromLeft)
    {
        EnteredFromLeft = fromLeft;
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
            psp.Caller = leftW;
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
        PendingLeftSlot = 0;
        PendingRightSlot = 0;

        return true;
    }

    // Centralized Layer 2 setup path for companion MP5KSD (Mixed Akimbo)
    bool SetupMP5CompanionLayer(PlayerInfo p, Weapon leftW, Weapon rightW)
    {
        if (p == null || leftW == null || rightW == null)
        {
            return false;
        }

        p.SetPSprite(PSP_DODA_SECONDARY, leftW.ResolveState("SecondaryReady"));
        let psp = p.GetPSprite(PSP_DODA_SECONDARY);
        if (psp != null)
        {
            psp.Caller = leftW;
            psp.x = -48.0;
            psp.y = 8.0;
            psp.bMirror = true; // Temporarily mirror Layer 2 MP5 placeholder
            psp.bAddBob = true;
            psp.bAddWeapon = false; // MANDATORY INVARIANT
        }

        Layer2Active = true;
        CombatMode = DODA_MODE_AKIMBO;
        LeftWeapon = leftW;
        RightWeapon = rightW;
        FocusedHand = DODA_HAND_RIGHT;
        PendingLeftSlot = 0;
        PendingRightSlot = 0;

        return true;
    }

    // Authoritative Akimbo entry for B92 pistols
    bool EnterB92Akimbo(PlayerInfo p)
    {
        if (p == null || p.mo == null)
        {
            return false;
        }

        let leftW = DoDAB92Left(p.mo.FindInventory('DoDAB92Left'));
        let rightW = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));

        if (leftW != null && rightW != null && (p.ReadyWeapon == leftW || p.ReadyWeapon == rightW))
        {
            EnteredFromLeft = (p.ReadyWeapon == leftW);

            if (p.ReadyWeapon != rightW)
            {
                p.ReadyWeapon = rightW;
                p.PendingWeapon = WP_NOCHANGE;
                p.SetPSprite(PSP_WEAPON, rightW.ResolveState("Ready"));
            }

            bool ok = DoDA.EnterAkimbo();
            if (ok)
            {
                SetupB92CompanionLayer(p, leftW.ResolveState("SecondaryReady"), leftW, rightW);
                return true;
            }
        }

        return false;
    }

    // Authoritative Akimbo entry for Left MP5KSD / Right B92
    bool EnterMixedAkimbo(PlayerInfo p)
    {
        if (p == null || p.mo == null)
        {
            return false;
        }

        let leftW = DoDAMP5KSD(p.mo.FindInventory('DoDAMP5KSD'));
        let rightW = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));

        if (leftW == null || rightW == null)
        {
            return false;
        }

        if (p.ReadyWeapon != rightW)
        {
            p.ReadyWeapon = rightW;
            p.PendingWeapon = WP_NOCHANGE;
            p.SetPSprite(PSP_WEAPON, rightW.ResolveState("Ready"));
        }

        bool ok = DoDA.EnterAkimbo();
        if (ok)
        {
            SetupMP5CompanionLayer(p, leftW, rightW);
            return true;
        }

        return false;
    }

    // Authoritative handler for Z/X modifier + slot weapon requests
    void HandleHandWeaponRequest(PlayerInfo p, int hand, int slot)
    {
        if (p == null || p.mo == null || p.mo.health <= 0)
        {
            return;
        }

        if (hand == DODA_HAND_LEFT)
        {
            if (slot != 4)
            {
                return; // Unsupported left-hand slot in Phase 4A
            }

            let mp5 = DoDAMP5KSD(p.mo.FindInventory('DoDAMP5KSD'));
            if (mp5 == null)
            {
                return; // MP5KSD not owned
            }

            let b92Right = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));
            if (b92Right == null)
            {
                return; // B92 not owned
            }

            bool rightIsB92 = (p.ReadyWeapon is "DoDAPistol") || (PendingRightSlot == 2);
            if (rightIsB92)
            {
                EnterMixedAkimbo(p);
            }
            else
            {
                PendingLeftSlot = 4;
            }
        }
        else if (hand == DODA_HAND_RIGHT)
        {
            if (slot != 2)
            {
                return; // Unsupported right-hand slot in Phase 4A
            }

            let b92Right = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));
            if (b92Right == null)
            {
                return; // B92 not owned
            }

            let mp5 = DoDAMP5KSD(p.mo.FindInventory('DoDAMP5KSD'));
            if (mp5 == null)
            {
                return; // MP5 not owned
            }

            bool leftIsMP5 = (p.ReadyWeapon is "DoDAMP5KSD") || (PendingLeftSlot == 4) || (LeftWeapon is "DoDAMP5KSD");
            if (leftIsMP5)
            {
                EnterMixedAkimbo(p);
            }
            else
            {
                PendingRightSlot = 2;
            }
        }
    }

    // Authoritative Akimbo exit for B92 pistols
    bool ExitB92Akimbo(PlayerInfo p)
    {
        if (p == null || p.mo == null)
        {
            return false;
        }

        bool wasFromLeft = EnteredFromLeft;
        let leftW = LeftWeapon ? LeftWeapon : Weapon(p.mo.FindInventory('DoDAB92Left'));
        let rightW = RightWeapon ? RightWeapon : Weapon(p.mo.FindInventory('DoDAB92Right'));

        ClearLayer2(p);

        if (wasFromLeft && leftW != null)
        {
            p.ReadyWeapon = leftW;
            p.PendingWeapon = WP_NOCHANGE;
            p.SetPSprite(PSP_WEAPON, leftW.ResolveState("Ready"));
        }
        else if (rightW != null)
        {
            p.ReadyWeapon = rightW;
            p.PendingWeapon = WP_NOCHANGE;
            p.SetPSprite(PSP_WEAPON, rightW.ResolveState("Ready"));
        }

        EnteredFromLeft = false;
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
        PendingLeftSlot = 0;
        PendingRightSlot = 0;
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

            // If switching away (PendingWeapon is set to any weapon)
            if (p.PendingWeapon != WP_NOCHANGE && p.PendingWeapon != null)
            {
                if (LeftWeapon is "DoDAMP5KSD")
                {
                    ClearLayer2(p);
                    return;
                }
                else if (!(p.PendingWeapon is "DoDAPistol"))
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
}
