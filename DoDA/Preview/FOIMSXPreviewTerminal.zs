/*//////////////////////////|
// DoDA/Preview/FOIMSXPreviewTerminal.zs
//
// Reusable placeable FOIMS-X standalone-preview terminal.
//
// Boundary:
//   - A map-placeable ZScript actor for level-development preview.
//   - Opens only the separate FOIMS-X preview session.
//   - Does not call native DoDA.
//   - Does not persist strategic state.
//   - Does not modify missions, maps, HUD, FOIMS-X Personnel V1,
//     the MAP01 host proof, or the native simulation.
//
// Placement:
//   - Place DoDAFOIMSXPreviewTerminal in any map or prefab.
//   - Face the terminal and press the normal Use key.
//   - O or Escape closes an active preview session.
*///////////////////////////|

class DoDAFOIMSXPreviewTerminal : Actor
{
    Default
    {
        Radius 16;
        Height 28;
        Scale 0.5;

        +SOLID;
        +USESPECIAL;
    }

    override bool Used(Actor user)
    {
        if (user == null)
        {
            Console.Printf(
                "[DoDA-FOIMSX-Preview] event=open-refused reason=no-user"
            );
            return false;
        }

        if (DoDAFOIMSXPreviewSession.IsPreviewActive())
        {
            Console.Printf(
                "[DoDA-FOIMSX-Preview] event=open-refused reason=already-active"
            );
            return false;
        }

        Console.Printf(
            "[DoDA-FOIMSX-Preview] event=terminal-used class=%s",
            GetClassName()
        );

        // The session controller owns temporary freeze state, input capture,
        // preview uptime, close handling, and safe world-lifecycle cleanup.
        EventHandler.SendNetworkEvent("DoDAFOIMSXPreviewOpen");

        return true;
    }

    States
    {
    Spawn:
    Idle:
        DCSV A 4;
        DCSV B 4;
        DCSV C 4;
        DCSV D 4;
        DCSV E 4;
        DCSV F 4;
        DCSV G 4;
        DCSV H 4;
        DCSV I 4;
        DCSV J 4;
        DCSV K 4;
        DCSV L 4;
        DCSV M 4;
        DCSV N 4;
        DCSV O 4;
        DCSV P 4;
        DCSV Q 4;
        DCSV R 4;
        DCSV S 4;
        DCSV T 4;
        DCSV U 4;
        DCSV V 4;
        DCSV W 4;
        DCSV X 4;
        DCSV Y 4;
        DCSV Z 4;
        Loop;
    }
}