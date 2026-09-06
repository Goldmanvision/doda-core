/*//////////////////////////|
// DoDA/Preview/FOIMSXPreviewSession.zs
//
// FOIMS-X Standalone Preview: session and input controller.
//
// Boundary:
//   - Owns preview-session lifecycle, temporary player freeze ownership,
//     standalone preview uptime, and preview-local navigation state.
//   - Does not call native DoDA.
//   - Does not persist state.
//   - Does not draw.
//   - Does not define a map actor.
//   - Does not alter the existing MAP01 FOIMS-X host proof.
//
// Open seam reserved for the later placed terminal actor:
//   EventHandler.SendNetworkEvent("DoDAFOIMSXPreviewOpen");
//
// This package only releases CF_TOTALLYFROZEN when it applied that freeze.
*///////////////////////////|

class DoDAFOIMSXPreviewSession : StaticEventHandler
{
    const EVENT_OPEN  = "DoDAFOIMSXPreviewOpen";
    const EVENT_CLOSE = "DoDAFOIMSXPreviewClose";

    // Play/network scope state.
    private int mWorldLoadGeneration;
    private int mOpenGeneration;
    private int mPreviewElapsedTics;
    private bool mSessionOpen;
    private bool mAppliedFreeze;

    // UI scope state.
    private ui int mObservedWorldLoadGeneration;
    private ui int mObservedOpenGeneration;
    private ui bool mActive;
    private ui int mFocusedMetric;
    private ui bool mHasSelection;

    override void OnRegister()
    {
        Console.Printf(
            "[DoDA-FOIMSX-Preview] event=register scope=static "
            .. "mode=standalone authority=none draw=external input=session"
        );
    }

    override void WorldLoaded(WorldEvent e)
    {
        mWorldLoadGeneration++;
        mSessionOpen = false;
        mPreviewElapsedTics = 0;
        ReleasePreviewFreeze(consoleplayer);

        Console.Printf(
            "[DoDA-FOIMSX-Preview] event=worldloaded scope=static map=%s "
            .. "mode=standalone authority=none",
            Level.MapName
        );
    }

    override void WorldUnloaded(WorldEvent e)
    {
        mSessionOpen = false;
        mPreviewElapsedTics = 0;
        ReleasePreviewFreeze(consoleplayer);
    }

    override void WorldTick()
    {
        if (mSessionOpen)
        {
            mPreviewElapsedTics++;
        }
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Player != consoleplayer ||
            e.Player < 0 ||
            e.Player >= MAXPLAYERS)
        {
            return;
        }

        PlayerInfo plr = players[e.Player];

        if (plr == null || plr.mo == null)
        {
            return;
        }

        if (e.Name == EVENT_OPEN)
        {
            if (mSessionOpen)
            {
                Console.Printf(
                    "[DoDA-FOIMSX-Preview] event=open-refused reason=already-active"
                );
                return;
            }

            mSessionOpen = true;
            mPreviewElapsedTics = 0;
            mOpenGeneration++;

            if ((plr.cheats & CF_TOTALLYFROZEN) == 0)
            {
                plr.cheats |= CF_TOTALLYFROZEN;
                plr.mo.Vel = (0, 0, 0);
                mAppliedFreeze = true;
            }
            else
            {
                // Respect freezes already owned by a different system.
                mAppliedFreeze = false;
            }

            Console.Printf(
                "[DoDA-FOIMSX-Preview] event=open-requested mode=standalone"
            );
            return;
        }

        if (e.Name == EVENT_CLOSE)
        {
            mSessionOpen = false;
            ReleasePreviewFreeze(e.Player);

            Console.Printf(
                "[DoDA-FOIMSX-Preview] event=closed mode=standalone uptime-tics=%d",
                mPreviewElapsedTics
            );
        }
    }

    override bool InputProcess(InputEvent e)
    {
        ReconcileObservedState();

        if (!mActive)
        {
            return false;
        }

        // The preview owns all non-keydown input while it is active.
        if (e.Type != InputEvent.Type_KeyDown)
        {
            return true;
        }

        // Close on 'o' / 'O' or Escape
        if (e.KeyScan == InputEvent.Key_Escape ||
            e.KeyScan == 0x01 ||
            e.KeyScan == 219 ||
            e.KeyScan == 0x18 ||
            e.KeyChar == 111 ||
            e.KeyChar == 79 ||
            e.KeyChar == 'o' ||
            e.KeyChar == 'O')
        {
            ClosePreviewSession();
            return true;
        }

        if (IsBackKey(e))
        {
            mHasSelection = false;
            return true;
        }

        if (IsConfirmKey(e))
        {
            mHasSelection = true;
            return true;
        }

        if (IsUpKey(e))
        {
            mFocusedMetric--;

            if (mFocusedMetric < DoDAFOIMSXPreviewConstants.FIRST_METRIC_INDEX)
            {
                mFocusedMetric = DoDAFOIMSXPreviewConstants.LAST_METRIC_INDEX;
            }

            return true;
        }

        if (IsDownKey(e))
        {
            mFocusedMetric++;

            if (mFocusedMetric > DoDAFOIMSXPreviewConstants.LAST_METRIC_INDEX)
            {
                mFocusedMetric = DoDAFOIMSXPreviewConstants.FIRST_METRIC_INDEX;
            }

            return true;
        }

        // A and D are reserved now for eventual multi-pane navigation.
        // The first preview page has one selectable metric list.
        if (IsLeftKey(e) || IsRightKey(e))
        {
            return true;
        }

        return true;
    }

    static ui bool IsPreviewActive()
    {
        let handler = GetPreviewHandler();

        if (handler == null)
        {
            return false;
        }

        handler.ReconcileObservedState();
        return handler.mActive;
    }

    static ui int GetPreviewElapsedTics()
    {
        let handler = GetPreviewHandler();

        if (handler == null)
        {
            return 0;
        }

        handler.ReconcileObservedState();

        if (!handler.mActive)
        {
            return 0;
        }

        return handler.mPreviewElapsedTics;
    }

    static ui int GetFocusedMetric()
    {
        let handler = GetPreviewHandler();

        if (handler == null)
        {
            return DoDAFOIMSXPreviewConstants.FIRST_METRIC_INDEX;
        }

        handler.ReconcileObservedState();
        return handler.mFocusedMetric;
    }

    static ui bool HasMetricSelection()
    {
        let handler = GetPreviewHandler();

        if (handler == null)
        {
            return false;
        }

        handler.ReconcileObservedState();
        return handler.mHasSelection;
    }

    static ui void RequestCloseFromRenderer()
    {
        let handler = GetPreviewHandler();

        if (handler == null)
        {
            return;
        }

        handler.ReconcileObservedState();
        handler.ClosePreviewSession();
    }

    private static ui DoDAFOIMSXPreviewSession GetPreviewHandler()
    {
        return DoDAFOIMSXPreviewSession(
            StaticEventHandler.Find("DoDAFOIMSXPreviewSession")
        );
    }

    private ui void ReconcileObservedState()
    {
        if (mObservedWorldLoadGeneration != mWorldLoadGeneration)
        {
            mActive = false;
            mFocusedMetric = DoDAFOIMSXPreviewConstants.FIRST_METRIC_INDEX;
            mHasSelection = false;
            mObservedWorldLoadGeneration = mWorldLoadGeneration;
            mObservedOpenGeneration = mOpenGeneration;
        }

        if (mObservedOpenGeneration != mOpenGeneration)
        {
            mObservedOpenGeneration = mOpenGeneration;
            mActive = mSessionOpen;
            mFocusedMetric = DoDAFOIMSXPreviewConstants.FIRST_METRIC_INDEX;
            mHasSelection = false;
        }

        if (!mSessionOpen && mActive)
        {
            mActive = false;
            mHasSelection = false;
        }
    }

    private ui void ClosePreviewSession()
    {
        if (!mActive)
        {
            return;
        }

        mActive = false;
        mHasSelection = false;

        EventHandler.SendNetworkEvent(EVENT_CLOSE);
    }

    private void ReleasePreviewFreeze(int playerNum)
    {
        if (mAppliedFreeze &&
            playerNum >= 0 &&
            playerNum < MAXPLAYERS)
        {
            PlayerInfo plr = players[playerNum];

            if (plr != null && plr.mo != null)
            {
                plr.cheats &= ~CF_TOTALLYFROZEN;
            }
        }

        mAppliedFreeze = false;
    }

    private ui bool IsToggleKey(InputEvent e)
    {
        // Confirmed current FOIMS-X proof mapping:
        // O = KeyScan 24, KeyChar 111.
        return int(e.KeyScan) == 24 && int(e.KeyChar) == 111;
    }

    private ui bool IsCloseKey(InputEvent e)
    {
        // Escape = KeyScan 219 in the existing FOIMS-X proof.
        return IsToggleKey(e) || int(e.KeyScan) == 219;
    }

    private ui bool IsBackKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x0e ||
            int(e.KeyScan) == 8 ||
            int(e.KeyChar) == 8;
    }

    private ui bool IsConfirmKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x1c ||
            int(e.KeyScan) == 0x9c ||
            int(e.KeyScan) == 0x39 ||
            int(e.KeyScan) == 13 ||
            int(e.KeyScan) == 32 ||
            int(e.KeyChar) == 13 ||
            int(e.KeyChar) == 32;
    }

    private ui bool IsUpKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x11 ||
            int(e.KeyChar) == 119 ||
            int(e.KeyChar) == 87;
    }

    private ui bool IsDownKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x1f ||
            int(e.KeyChar) == 115 ||
            int(e.KeyChar) == 83;
    }

    private ui bool IsLeftKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x1e ||
            int(e.KeyChar) == 97 ||
            int(e.KeyChar) == 65;
    }

    private ui bool IsRightKey(InputEvent e)
    {
        return int(e.KeyScan) == 0x20 ||
            int(e.KeyChar) == 100 ||
            int(e.KeyChar) == 68;
    }
}