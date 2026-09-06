class MP5ModeHandler : StaticEventHandler
{
    override bool InputProcess(InputEvent e)
    {
        if (e.Type != InputEvent.Type_KeyDown)
        {
            return false;
        }

        // C key: cycle SEMI -> BURST -> AUTO.
        if (
            e.KeyString == "c"
            || e.KeyString == "C"
            || e.KeyChar == 99
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

        // R key: request MP5 tactical or empty reload.
        if (
            e.KeyString == "r"
            || e.KeyString == "R"
            || e.KeyChar == 114
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

                return true;
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
        }
    }
}