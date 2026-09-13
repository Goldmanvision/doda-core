class MP5ModeHandler : StaticEventHandler
{
    override bool InputProcess(InputEvent e)
    {
        if (menuactive != 0 || ConsoleState != 0 || gamestate != GS_LEVEL)
        {
            return false;
        }

        if (e.Type != InputEvent.Type_KeyDown)
        {
            return false;
        }

        String bind = Bindings.GetBinding(e.KeyScan);
        if (bind == "")
        {
            return false;
        }

        // Cycle Left-Hand Fire Mode (default C): in single-weapon mode, cycles
        // the selected weapon's fire mode when supported.
        if (
            bind ~== "+doda_cycle_firemode_left"
            || bind ~== "doda_cycle_firemode_left"
            || bind ~== "+doda_firemode"
            || bind ~== "+user3"
        )
        {
            let player = players[consoleplayer];

            if (!player || !player.mo)
            {
                return false;
            }

            let mp5 = DoDAMP5KSD(player.ReadyWeapon);

            if (mp5)
            {
                EventHandler.SendNetworkEvent(
                    "DoDA_MP5CycleFireMode"
                );

                return true;
            }
        }

        // Cycle Right-Hand Fire Mode (default B): in single-weapon mode, harmless no-op.
        if (
            bind ~== "doda_cycle_firemode_right"
            || bind ~== "+doda_cycle_firemode_right"
        )
        {
            return true;
        }

        // Reload weapon action (default R).
        if (
            bind ~== "+reload"
            || bind ~== "reload"
        )
        {
            let player = players[consoleplayer];

            if (!player || !player.mo)
            {
                return false;
            }

            let mp5 = DoDAMP5KSD(player.ReadyWeapon);

            if (mp5)
            {
                EventHandler.SendNetworkEvent(
                    "DoDA_MP5Reload"
                );

                return false;
            }
        }

        return false;
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name == "DoDA_MP5CycleFireMode")
        {
            let player = players[e.Player];

            if (!player || !player.mo)
            {
                return;
            }

            let mp5 = DoDAMP5KSD(player.ReadyWeapon);

            if (mp5)
            {
                mp5.CycleFireMode();
            }

            return;
        }

        if (e.Name == "DoDA_MP5Reload")
        {
            let player = players[e.Player];

            if (!player || !player.mo)
            {
                return;
            }

            let mp5 = DoDAMP5KSD(player.ReadyWeapon);

            if (mp5)
            {
                mp5.TryReload();
            }

            return;
        }

        if (e.Name == "DoDA_CycleRightFireMode")
        {
            // Harmless no-op in single-weapon mode.
            return;
        }
    }
}