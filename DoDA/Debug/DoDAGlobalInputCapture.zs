/*//////////////////////////|
// DoDA/Debug/DoDAGlobalInputCapture.zs
//
// Temporary global raw-input capture handler.
//
// Scope:
//   - Logs every key-down InputEvent on all maps and UI states.
//   - Does not consume input.
//   - Does not change FOIMS-X, gameplay, HUD, weapons, native simulation,
//     persistence, or map behavior.
//
// Remove this file and its zscript.txt include after recording the key map.
*///////////////////////////|

class DoDAGlobalInputCapture : StaticEventHandler
{
    // Explicit development gate: 0 = disabled for ordinary play, 1 = enabled for developer diagnostic capture.
    const DEV_GATE_ENABLED = 0;

    override void OnRegister()
    {
        if (!DEV_GATE_ENABLED)
        {
            return;
        }

        Console.Printf(
            "[DoDA-INPUT-CAPTURE] event=register status=dev-gate-active run=%u mode=keydown-only consume=0",
            uint(MSTime())
        );
    }

    override bool InputProcess(InputEvent e)
    {
        if (!DEV_GATE_ENABLED)
        {
            return false;
        }

        if (e.Type == InputEvent.Type_KeyDown)
        {
            Console.Printf(
                "[DoDA-INPUT-CAPTURE] scan=%d char=%d keyString=\"%s\"",
                int(e.KeyScan),
                int(e.KeyChar),
                e.KeyString
            );
        }

        return false;
    }
}