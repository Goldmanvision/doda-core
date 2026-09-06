/*//////////////////////////|
// DoDA/POC/BackgroundSimPOC.zs
//
// Real-Time Background Simulation POC (TEMPORARY / DEBUG ONLY).
//
// Scope:
//   - MAP01 only.
//   - One location, one task, Brian C. Gordon and Michelle C. Thomas
//     (supplied by the native default fixture).
//   - 25% task progress per 60 strategic minutes (native rule).
//   - Throttled five-second idle steps.
//   - Temporary keypad / arrow debug controls.
//
// This harness is read-only with respect to FOIMS-X, TAB/TAPLINE, KEYCONF,
// MENUDEF, HUD, maps, weapons, missions, FONTDEFS, LibColony and persistence.
// It drives only the already-approved native debug entry points.
*///////////////////////////|

class DoDABackgroundSimPOC : EventHandler
{
    // Raw DIK scancodes for the numeric keypad; the engine exposes named
    // constants for arrows only, so the keypad codes are spelled out here.
    const KEYPAD_MINUS = 0x4A;
    const KEYPAD_PLUS  = 0x4E;
    const KEYPAD_0     = 0x52;
    const KEYPAD_1     = 0x4F;
    const KEYPAD_2     = 0x50;
    const KEYPAD_3     = 0x51;

    // Five real seconds at 35 tics per second.
    const IDLE_STEP_TICS = 175;

    // One idle step advances a full strategic hour, i.e. 25% task progress.
    const IDLE_STEP_MINUTES = 60;

    // Network event names forwarded from InputProcess to NetworkProcess.
    const EVENT_START     = "DoDAPOCStart";
    const EVENT_PAUSE     = "DoDAPOCPause";
    const EVENT_STEP      = "DoDAPOCStep";
    const EVENT_SMALLSTEP = "DoDAPOCSmallStep";
    const EVENT_RESET     = "DoDAPOCReset";
    const EVENT_STATUS    = "DoDAPOCStatus";
    const EVENT_PERSONNEL = "DoDAPOCPersonnel";
    const EVENT_CONTROLS  = "DoDAPOCControls";

    private bool mActive;
    private bool mRunning;
    private int mTicAccum;

    override void WorldLoaded(WorldEvent e)
    {
        mActive = (Level.MapName == "MAP01");
        mRunning = mActive;
        mTicAccum = 0;

        if (!mActive)
        {
            return;
        }

        Console.Printf("[DoDA-POC] Real-Time Background Simulation POC active on MAP01.");
        Console.Printf("[DoDA-POC] Idle stepping auto-started: %d strategic minute(s) every 5 seconds.",
            IDLE_STEP_MINUTES);
        Console.Printf("[DoDA-POC] Native API version: %d, personnel snapshot API version: %d.",
            DoDA.GetNativeApiVersion(), DoDA.GetPersonnelSnapshotApiVersion());
        PrintControls();
        PrintStatus();
    }

    override void WorldUnloaded(WorldEvent e)
    {
        mActive = false;
        mRunning = false;
        mTicAccum = 0;
    }

    override void WorldTick()
    {
        if (!mActive || !mRunning)
        {
            return;
        }

        mTicAccum++;
        if (mTicAccum < IDLE_STEP_TICS)
        {
            return;
        }

        mTicAccum = 0;

        if (IsSoleTaskComplete())
        {
            mRunning = false;
            Console.Printf("[DoDA-POC] Task complete; idle stepping stopped.");
            PrintStatus();
            return;
        }

        Step(IDLE_STEP_MINUTES);
    }

    // InputProcess is UI scope and may not mutate play-side state, so every
    // debug key is forwarded to NetworkProcess as a named event instead.
    override bool InputProcess(InputEvent e)
    {
        if (!mActive || e.Type != InputEvent.Type_KeyDown)
        {
            return false;
        }

        String command = "";

        switch (e.KeyScan)
        {
            case InputEvent.KEY_UPARROW:
                command = EVENT_START;
                break;

            case InputEvent.KEY_DOWNARROW:
                command = EVENT_PAUSE;
                break;

            case InputEvent.KEY_RIGHTARROW:
            case KEYPAD_PLUS:
                command = EVENT_STEP;
                break;

            case InputEvent.KEY_LEFTARROW:
            case KEYPAD_MINUS:
                command = EVENT_SMALLSTEP;
                break;

            case KEYPAD_0:
                command = EVENT_RESET;
                break;

            case KEYPAD_1:
                command = EVENT_STATUS;
                break;

            case KEYPAD_2:
                command = EVENT_PERSONNEL;
                break;

            case KEYPAD_3:
                command = EVENT_CONTROLS;
                break;
        }

        if (command == "")
        {
            return false;
        }

        EventHandler.SendNetworkEvent(command);
        return true;
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (!mActive)
        {
            return;
        }

        if (e.Name == EVENT_START)
        {
            mRunning = true;
            mTicAccum = 0;
            Console.Printf("[DoDA-POC] Idle stepping STARTED (%d strategic minute(s) every 5 seconds).",
                IDLE_STEP_MINUTES);
        }
        else if (e.Name == EVENT_PAUSE)
        {
            mRunning = false;
            Console.Printf("[DoDA-POC] Idle stepping PAUSED.");
        }
        else if (e.Name == EVENT_STEP)
        {
            Step(IDLE_STEP_MINUTES);
        }
        else if (e.Name == EVENT_SMALLSTEP)
        {
            Step(IDLE_STEP_MINUTES / 4);
        }
        else if (e.Name == EVENT_RESET)
        {
            mRunning = false;
            mTicAccum = 0;
            DoDA.DebugResetFixture();
            Console.Printf("[DoDA-POC] Fixture reset; idle stepping stopped.");
            PrintStatus();
            PrintPersonnel();
        }
        else if (e.Name == EVENT_STATUS)
        {
            PrintStatus();
        }
        else if (e.Name == EVENT_PERSONNEL)
        {
            PrintPersonnel();
        }
        else if (e.Name == EVENT_CONTROLS)
        {
            PrintControls();
        }
    }

    private void Step(int minutes)
    {
        if (minutes <= 0)
        {
            return;
        }

        if (!DoDA.DebugAdvanceMinutes(minutes))
        {
            Console.Printf("[DoDA-POC] Native refused the %d minute advance.", minutes);
            return;
        }

        PrintStatus();
    }

    private bool IsSoleTaskComplete()
    {
        if (DoDA.GetTaskCount() <= 0)
        {
            return true;
        }

        return DoDA.GetTaskProgress(0) >= 100;
    }

    private void PrintControls()
    {
        Console.Printf("[DoDA-POC] Controls (temporary): Up = start idle stepping, Down = pause,");
        Console.Printf("[DoDA-POC]   Right / Keypad + = step %d min, Left / Keypad - = step %d min,",
            IDLE_STEP_MINUTES, IDLE_STEP_MINUTES / 4);
        Console.Printf("[DoDA-POC]   Keypad 0 = reset fixture, Keypad 1 = status, Keypad 2 = personnel, Keypad 3 = controls.");
    }

    private void PrintStatus()
    {
        Console.Printf("[DoDA-POC] Strategic minutes: %s (revision %s).",
            DoDA.GetPersonnelSnapshotStrategicMinutesText(),
            DoDA.GetPersonnelSnapshotRevisionText());

        if (DoDA.GetLocationCount() > 0)
        {
            Console.Printf("[DoDA-POC] Location %s: %s.",
                DoDA.GetLocationIdText(0), DoDA.GetLocationDisplayName(0));
        }

        if (DoDA.GetTaskCount() > 0)
        {
            Console.Printf("[DoDA-POC] Task %s '%s': progress %d%%, status %d.",
                DoDA.GetTaskIdText(0), DoDA.GetTaskTitle(0),
                DoDA.GetTaskProgress(0), DoDA.GetTaskStatus(0));
        }
    }

    private void PrintPersonnel()
    {
        int count = DoDA.GetPersonnelSnapshotCount();
        for (int i = 0; i < count; i++)
        {
            String name = DoDA.GetPersonnelDisplayName(i);
            if (name != "Brian C. Gordon" && name != "Michelle C. Thomas")
            {
                continue;
            }

            Console.Printf("[DoDA-POC] %s (id %s): status %d, workload %d, task '%s'.",
                name,
                DoDA.GetPersonnelPersonIdText(i),
                DoDA.GetPersonnelStatus(i),
                DoDA.GetPersonnelWorkload(i),
                DoDA.GetPersonnelCurrentTaskTitle(i));
        }
    }
}
