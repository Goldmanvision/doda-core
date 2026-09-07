/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXHostLifecycleProbe.zs
//
// FOIMS-X Active Session-Control Host & Lifecycle Manager.
//
// Confirmed UZDoom input representation for this proof build:
//   - O:      KeyScan 24, KeyChar 111
//   - Escape: KeyScan 219
//
// Scope:
//   - MAP01-only FOIMS-X activation, close, freeze ownership, and input capture.
//   - Zero native or persistence mutation.
*///////////////////////////|

class DoDAFOIMSXHostLifecycleProbe : StaticEventHandler
{
    private int mWorldLoadGeneration;
    private bool mFOIMSXAppliedFreeze;

    private ui int mObservedWorldLoadGeneration;
    private ui bool mActive;
    private ui bool mLastAssignmentActiveState;

    private ui DoDAAssignmentSnapshotV1ViewState mAssignmentViewState;

    private ui void ReconcileObservedGeneration()
    {
        if (mObservedWorldLoadGeneration != mWorldLoadGeneration)
        {
            mActive = false;
            mLastAssignmentActiveState = false;
            mObservedWorldLoadGeneration = mWorldLoadGeneration;
        }
    }

    static ui bool IsFOIMSXActive()
    {
        let handler = DoDAFOIMSXHostLifecycleProbe(
            StaticEventHandler.Find("DoDAFOIMSXHostLifecycleProbe")
        );

        if (handler == null || Level == null || Level.MapName != "MAP01")
        {
            return false;
        }

        handler.ReconcileObservedGeneration();
        return handler.mActive;
    }

    override void OnRegister()
    {
        Console.Printf(
            "[DoDA-FOIMSX-Host-Lifecycle] event=register scope=static "
            .. "input=host-session-control"
        );
    }

    override void WorldLoaded(WorldEvent e)
    {
        mWorldLoadGeneration++;
        ReleaseFOIMSXFreeze(consoleplayer);

        Console.Printf(
            "[DoDA-FOIMSX-Host-Lifecycle] event=worldloaded scope=static "
            .. "map=%s hqEligible=no input=host-session-control",
            Level.MapName
        );
    }

    override void WorldUnloaded(WorldEvent e)
    {
        ReleaseFOIMSXFreeze(consoleplayer);
    }

    override void RenderOverlay(RenderEvent e)
    {
        if (Level == null ||
            Level.MapName != "MAP01" ||
            !mActive)
        {
            mLastAssignmentActiveState = false;
            return;
        }

        if (!mLastAssignmentActiveState)
        {
            if (mAssignmentViewState == null)
            {
                mAssignmentViewState = DoDAAssignmentSnapshotV1ViewState.Create();
            }

            let snapshot = DoDAAssignmentSnapshotV1Adapter.AcquireSnapshot();
            mAssignmentViewState.UpdateFromSnapshot(snapshot);
            mLastAssignmentActiveState = true;
        }

        if (mAssignmentViewState != null)
        {
            DoDAAssignmentSnapshotV1Renderer.Render(mAssignmentViewState);
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
            return false;
        }

        // Map transitions and save/load generation changes invalidate active UI.
        ReconcileObservedGeneration();

        // Inactive: pass normal gameplay input through, except confirmed O.
        if (!mActive)
        {
            if (e.Type == InputEvent.Type_KeyDown && IsFOIMSXToggleKey(e))
            {
                mActive = true;
                EventHandler.SendNetworkEvent("DoDAFOIMSXFreeze");
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
            mActive = false;
            EventHandler.SendNetworkEvent("DoDAFOIMSXUnfreeze");
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
