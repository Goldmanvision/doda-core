class Map03RangeStartHandler : EventHandler
{
    override void WorldLoaded(WorldEvent e)
    {
        if (Level.MapName != "MAP03")
        {
            return;
        }

        for (int i = 0; i < MAXPLAYERS; i++)
        {
            if (playeringame[i])
            {
                let p = players[i].mo;
                if (p)
                {
                    p.TakeInventory("DoDAB92Left", 1);
                    p.TakeInventory("DoDAB92Right", 1);
                    p.TakeInventory("Clip", 1000);
                }
            }
        }
    }
}
