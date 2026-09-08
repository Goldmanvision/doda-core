/*//////////////////////////|
// DoDA/POC/LocationMaterializationProof.zs
//
// One-Location Materialization Proof (TEMPORARY / READ-ONLY).
//
// Scope:
//   - MAP01 only.
//   - Materializes canonical native Location 1 ("Morrow Point Waterworks")
//     as a temporary field-side GZDoom actor representation.
//   - Carries stable PersistentLocationIdText = "1".
//   - Native C++ remains the sole authoritative strategic-state owner.
//   - Zero native or persistence mutation.
*///////////////////////////|

class DoDATemporaryLocationAnchor : Actor
{
    string PersistentLocationIdText;
    string LocationDisplayName;

    Default
    {
        +NOINTERACTION;
        +NOGRAVITY;
        Radius 16;
        Height 32;
    }
}

class DoDALocationMaterializationProof : StaticEventHandler
{
    override void OnRegister()
    {
        Console.Printf("[DoDA-Location-Proof] event=register scope=static");
    }

    override void WorldLoaded(WorldEvent e)
    {
        if (Level == null || Level.MapName != "MAP01")
        {
            return;
        }

        Console.Printf(
            "[DoDA-Location-Proof] event=worldloaded map=%s save=%d",
            Level.MapName,
            e.IsSaveGame
        );

        // Duplicate-spawn guard: check if anchor already exists in the world
        let it = ThinkerIterator.Create("DoDATemporaryLocationAnchor");
        DoDATemporaryLocationAnchor existingAnchor = DoDATemporaryLocationAnchor(it.Next());
        if (existingAnchor != null)
        {
            Console.Printf(
                "[DoDA-Location-Proof] event=retained locationId=%s locationName=%s scope=temporary-field-actor persistentAuthority=native-cpp duplicateCheck=passed",
                existingAnchor.PersistentLocationIdText,
                existingAnchor.LocationDisplayName
            );
            return;
        }

        // Query canonical native C++ location records using stable Location ID "1"
        int locCount = DoDA.GetLocationCount();
        string locId = "";
        string locName = "";
        for (int i = 0; i < locCount; i++)
        {
            if (DoDA.GetLocationIdText(i) == "1")
            {
                locId = DoDA.GetLocationIdText(i);
                locName = DoDA.GetLocationDisplayName(i);
                break;
            }
        }

        if (locId == "")
        {
            Console.Printf("[DoDA-Location-Proof] event=materialize-failed reason=location-not-found id=1");
            return;
        }

        // Spawn temporary field-side anchor actor
        Vector3 spawnPos = (0, 0, 0);
        let player = players[consoleplayer].mo;
        if (player != null)
        {
            spawnPos = player.Pos;
        }

        let anchor = DoDATemporaryLocationAnchor(Actor.Spawn("DoDATemporaryLocationAnchor", spawnPos));
        if (anchor != null)
        {
            anchor.PersistentLocationIdText = locId;
            anchor.LocationDisplayName = locName;

            Console.Printf(
                "[DoDA-Location-Proof] event=materialize locationId=%s locationName=%s scope=temporary-field-actor persistentAuthority=native-cpp",
                anchor.PersistentLocationIdText,
                anchor.LocationDisplayName
            );
        }
    }
}
