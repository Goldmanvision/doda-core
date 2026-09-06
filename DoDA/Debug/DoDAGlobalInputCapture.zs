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
    override void OnRegister()
    {
        Console.Printf(
            "[DoDA-INPUT-CAPTURE] event=register mode=keydown-only consume=0"
        );
    }

    override bool InputProcess(InputEvent e)
    {
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