/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXSessionController.zs
//
// FOIMS-X Dedicated Session Controller.
//
// Central production owner for:
//   - Active / Inactive session state
//   - Bound host actor tracking and lifecycle validation
//   - Central freeze / unfreeze orchestration via NetworkProcess
//   - FOIMS-X input arbitration and consumption
//   - Safe lifecycle cleanup (map transition, player death/respawn, host loss)
//
// Confirmed UZDoom input representation for this build:
//   - O:      KeyScan 24, KeyChar 111
//   - Escape: KeyScan 219
//
// Scope:
//   - MAP01-only FOIMS-X session control.
//   - Zero native or persistence mutation.
*///////////////////////////|

class DoDAFOIMSXSessionController : StaticEventHandler
{
    private int mWorldLoadGeneration;
    private bool mFOIMSXAppliedFreeze;

    private ui int mObservedWorldLoadGeneration;
    private ui bool mActive;
    private ui Actor mBoundHost;

    private ui void ReconcileObservedGeneration()
    {
        if (mObservedWorldLoadGeneration != mWorldLoadGeneration)
        {
            mActive = false;
            mBoundHost = null;
            mObservedWorldLoadGeneration = mWorldLoadGeneration;
        }

        if (mBoundHost != null && mBoundHost.bDestroyed)
        {
            mBoundHost = null;
            mActive = false;
        }
    }

    static clearScope DoDAFOIMSXSessionController GetInstance()
    {
        return DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );
    }

    static ui bool IsSessionActive()
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl == null || Level == null || Level.MapName != "MAP01")
        {
            return false;
        }

        ctrl.ReconcileObservedGeneration();
        return ctrl.mActive;
    }

    static ui bool IsFOIMSXActive()
    {
        return IsSessionActive();
    }

    static ui Actor GetBoundHost()
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl == null)
        {
            return null;
        }

        ctrl.ReconcileObservedGeneration();
        return ctrl.mBoundHost;
    }

    static ui void OpenSession(Actor host = null)
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.ActivateSession(host);
        }
    }

    static ui void CloseSession()
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.DeactivateSession();
        }
    }

    static ui void Toggle(Actor host = null)
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.ToggleSession(host);
        }
    }

    static ui void RequestRefresh(bool force = false)
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.RefreshSessionData(force);
        }
    }

    static ui void RequestPersonnelRefresh(bool force = false)
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.RefreshPersonnelData(force);
        }
    }

    static ui void RequestAssignmentRefresh(bool force = false)
    {
        let ctrl = DoDAFOIMSXSessionController(
            StaticEventHandler.Find("DoDAFOIMSXSessionController")
        );

        if (ctrl != null)
        {
            ctrl.RefreshAssignmentData(force);
        }
    }

    ui void ActivateSession(Actor host = null)
    {
        if (Level == null || Level.MapName != "MAP01")
        {
            return;
        }

        mActive = true;
        mBoundHost = host;
        EventHandler.SendNetworkEvent("DoDAFOIMSXFreeze");
        RefreshSessionData(true);
    }

    ui void DeactivateSession()
    {
        mActive = false;
        mBoundHost = null;
        EventHandler.SendNetworkEvent("DoDAFOIMSXUnfreeze");
    }

    ui void ToggleSession(Actor host = null)
    {
        if (mActive)
        {
            DeactivateSession();
        }
        else
        {
            ActivateSession(host);
        }
    }

    ui void RefreshSessionData(bool force = false)
    {
        let renderer = DoDAFOIMSXDirectoryRenderer(
            EventHandler.Find("DoDAFOIMSXDirectoryRenderer")
        );

        if (renderer != null)
        {
            renderer.RefreshSessionData(force);
        }
    }

    ui void RefreshPersonnelData(bool force = false)
    {
        let renderer = DoDAFOIMSXDirectoryRenderer(
            EventHandler.Find("DoDAFOIMSXDirectoryRenderer")
        );

        if (renderer != null)
        {
            renderer.RefreshPersonnelData(force);
        }
    }

    ui void RefreshAssignmentData(bool force = false)
    {
        let renderer = DoDAFOIMSXDirectoryRenderer(
            EventHandler.Find("DoDAFOIMSXDirectoryRenderer")
        );

        if (renderer != null)
        {
            renderer.RefreshAssignmentData(force);
        }
    }

    override void OnRegister()
    {
        Console.Printf(
            "[DoDA-FOIMSX-SessionController] event=register scope=static "
            .. "input=session-control"
        );
    }

    override void WorldLoaded(WorldEvent e)
    {
        mWorldLoadGeneration++;
        ReleaseFOIMSXFreeze(consoleplayer);

        Console.Printf(
            "[DoDA-FOIMSX-SessionController] event=worldloaded scope=static "
            .. "map=%s hqEligible=no input=session-control",
            Level.MapName
        );
    }

    override void WorldUnloaded(WorldEvent e)
    {
        mWorldLoadGeneration++;
        ReleaseFOIMSXFreeze(consoleplayer);
    }

    override void PlayerDied(PlayerEvent e)
    {
        if (e.PlayerNumber == consoleplayer)
        {
            mWorldLoadGeneration++;
            ReleaseFOIMSXFreeze(e.PlayerNumber);
        }
    }

    override void PlayerRespawned(PlayerEvent e)
    {
        if (e.PlayerNumber == consoleplayer)
        {
            ReleaseFOIMSXFreeze(e.PlayerNumber);
        }
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Player != consoleplayer || e.Player < 0 || e.Player >= MAXPLAYERS)
        {
            return;
        }

        PlayerInfo plr = players[e.Player];

        if (plr == null || plr.mo == null)
        {
            return;
        }

        if (e.Name == "DoDAFOIMSXFreeze")
        {
            if ((plr.cheats & CF_TOTALLYFROZEN) == 0)
            {
                plr.cheats |= CF_TOTALLYFROZEN;
                mFOIMSXAppliedFreeze = true;
                plr.mo.Vel = (0, 0, 0);
            }
            else
            {
                // Do not release a freeze that existed before FOIMS-X opened.
                mFOIMSXAppliedFreeze = false;
            }

            return;
        }

        if (e.Name == "DoDAFOIMSXUnfreeze")
        {
            ReleaseFOIMSXFreeze(e.Player);
            return;
        }

        if (e.Name == "DoDAFOIMSXDataChanged" || e.Name == "DoDAFOIMSXRefresh")
        {
            EventHandler.SendInterfaceEvent(consoleplayer, e.Name);
            return;
        }

        if (e.Name == "DoDAFOIMSXRefreshPersonnel")
        {
            EventHandler.SendInterfaceEvent(consoleplayer, e.Name);
            return;
        }

        if (e.Name == "DoDAFOIMSXRefreshAssignment")
        {
            EventHandler.SendInterfaceEvent(consoleplayer, e.Name);
            return;
        }
    }

    override void InterfaceProcess(ConsoleEvent e)
    {
        if (e.Name == "DoDAFOIMSXDataChanged" || e.Name == "DoDAFOIMSXRefresh")
        {
            if (mActive)
            {
                RefreshSessionData(false);
            }
        }
        else if (e.Name == "DoDAFOIMSXRefreshPersonnel")
        {
            if (mActive)
            {
                RefreshPersonnelData(false);
            }
        }
        else if (e.Name == "DoDAFOIMSXRefreshAssignment")
        {
            if (mActive)
            {
                RefreshAssignmentData(false);
            }
        }
    }

    private void ReleaseFOIMSXFreeze(int playerNum)
    {
        if (mFOIMSXAppliedFreeze &&
            playerNum >= 0 &&
            playerNum < MAXPLAYERS)
        {
            PlayerInfo plr = players[playerNum];

            if (plr != null && plr.mo != null)
            {
                plr.cheats &= ~CF_TOTALLYFROZEN;
            }
        }

        mFOIMSXAppliedFreeze = false;
    }

    private ui bool IsFOIMSXToggleKey(InputEvent e)
    {
        return int(e.KeyScan) == 24 && int(e.KeyChar) == 111;
    }

    private ui bool IsFOIMSXCloseKey(InputEvent e)
    {
        return IsFOIMSXToggleKey(e) || int(e.KeyScan) == 219;
    }

    override bool InputProcess(InputEvent e)
    {
        // FOIMS-X is eligible only in the MAP01 proof environment.
        if (Level == null || Level.MapName != "MAP01")
        {
            mActive = false;
            mBoundHost = null;
            return false;
        }

        // Map transitions and save/load generation changes invalidate active UI.
        ReconcileObservedGeneration();

        // Inactive: pass normal gameplay input through, except confirmed O.
        if (!mActive)
        {
            if (e.Type == InputEvent.Type_KeyDown && IsFOIMSXToggleKey(e))
            {
                ActivateSession();
                return true;
            }

            return false;
        }

        // While active, suppress every non-keydown input event.
        if (e.Type != InputEvent.Type_KeyDown)
        {
            return true;
        }

        // O toggles closed; Escape closes.
        if (IsFOIMSXCloseKey(e))
        {
            DeactivateSession();
            return true;
        }

        // Preserve renderer-local navigation ownership.
        let renderer = DoDAFOIMSXDirectoryRenderer(
            EventHandler.Find("DoDAFOIMSXDirectoryRenderer")
        );

        if (renderer != null)
        {
            renderer.HandleNavInput(
                int(e.KeyScan),
                int(e.KeyChar)
            );
        }

        // Consume every active FOIMS-X key, including Page Up, End, and Delete.
        return true;
    }
}

// Backward compatibility bridge for existing call sites (such as DoDAHUD.ProcessNotify)
class DoDAFOIMSXHostLifecycleProbe : Object
{
    static ui bool IsFOIMSXActive()
    {
        return DoDAFOIMSXSessionController.IsSessionActive();
    }
}
