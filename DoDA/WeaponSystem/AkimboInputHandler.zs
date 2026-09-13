class DoDAAkimboInputHandler : StaticEventHandler
{
    bool enteredFromLeft;
    ui bool leftSelectorHeld;
    ui bool rightSelectorHeld;

    private ui int ResolveSlotFromBinding(String bind)
    {
        if (bind == "") return -1;

        if (bind.Left(5) ~== "slot ")
        {
            String slotStr = bind.Mid(5);
            int s = slotStr.ToInt(10);
            if (s >= 0 && s <= 9) return s;
        }

        if (bind ~== "doda_select_b92") return 2;
        if (bind ~== "doda_select_shotgun") return 3;
        if (bind ~== "doda_select_mp5") return 4;
        if (bind ~== "doda_holster" || bind ~== "use dodaholster") return 1;

        if (bind ~== "use dodab92right" || bind ~== "use dodab92left") return 2;
        if (bind ~== "use dodashotgun") return 3;
        if (bind ~== "use dodamp5ksd") return 4;

        return -1;
    }

    override bool InputProcess(InputEvent e)
    {
        if (menuactive != 0 || ConsoleState != 0 || gamestate != GS_LEVEL)
        {
            leftSelectorHeld = false;
            rightSelectorHeld = false;
            return false;
        }

        String bind = Bindings.GetBinding(e.KeyScan);
        if (bind == "")
        {
            return false;
        }

        // Detect held left-hand weapon selector state on key-down and clear on key-up
        if (
            bind ~== "+doda_equip_left"
            || bind ~== "+doda_mod_left"
        )
        {
            leftSelectorHeld = (e.Type == InputEvent.Type_KeyDown);
            return false;
        }

        // Detect held right-hand weapon selector state on key-down and clear on key-up
        if (
            bind ~== "+doda_equip_right"
            || bind ~== "+doda_mod_right"
        )
        {
            rightSelectorHeld = (e.Type == InputEvent.Type_KeyDown);
            return false;
        }

        if (e.Type == InputEvent.Type_KeyDown)
        {
            int slot = ResolveSlotFromBinding(bind);
            if (slot != -1)
            {
                // Only consume and route when EXACTLY ONE selector is held
                if (leftSelectorHeld && !rightSelectorHeld)
                {
                    Console.Printf("[DoDA Hand Routing] Request left hand weapon: Slot %d", slot);
                    EventHandler.SendNetworkEvent("DoDA_HandWeaponRequest", 0, slot);
                    return true;
                }
                else if (!leftSelectorHeld && rightSelectorHeld)
                {
                    Console.Printf("[DoDA Hand Routing] Request right hand weapon: Slot %d", slot);
                    EventHandler.SendNetworkEvent("DoDA_HandWeaponRequest", 1, slot);
                    return true;
                }
                // With neither selector held, or if both selectors are held,
                // ordinary slot input continues through without modification.
            }
        }

        return false;
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name == "DoDA_HandWeaponRequest")
        {
            int hand = e.Args[0];
            int slot = e.Args[1];
            String handName = (hand == 0) ? "left hand" : "right hand";
            Console.Printf("[DoDA Hand Routing] Hand assignment request received for %s: slot %d (routing proof only)", handName, slot);
            return;
        }

        if (e.Name == "DoDA_ToggleAkimbo")
        {
            let p = players[e.Player];
            if (p == null || p.mo == null) return;

            let playerBase = DoDAPlayerBase(p.mo);
            let handState = (playerBase != null) ? playerBase.GetHandState() : null;

            if (DoDA.IsAkimboActive())
            {
                if (handState != null)
                {
                    handState.ClearLayer2(p);
                }
                else
                {
                    DoDA.ExitAkimbo();
                    p.SetPSprite(2, null);
                }

                let leftW = DoDAB92Left(p.mo.FindInventory('DoDAB92Left'));
                let rightW = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));

                if (enteredFromLeft && leftW != null)
                {
                    p.ReadyWeapon = leftW;
                    p.PendingWeapon = WP_NOCHANGE;
                    p.SetPSprite(PSP_WEAPON, leftW.ResolveState("Ready"));
                }
                else if (rightW != null)
                {
                    p.ReadyWeapon = rightW;
                    p.PendingWeapon = WP_NOCHANGE;
                    p.SetPSprite(PSP_WEAPON, rightW.ResolveState("Ready"));
                }

                enteredFromLeft = false;
                Console.Printf("[DoDA Akimbo] Akimbo mode exited via toggle action");
            }
            else
            {
                let leftW = DoDAB92Left(p.mo.FindInventory('DoDAB92Left'));
                let rightW = DoDAB92Right(p.mo.FindInventory('DoDAB92Right'));

                if (leftW != null && rightW != null && (p.ReadyWeapon == leftW || p.ReadyWeapon == rightW))
                {
                    enteredFromLeft = (p.ReadyWeapon == leftW);

                    if (p.ReadyWeapon != rightW)
                    {
                        p.ReadyWeapon = rightW;
                        p.PendingWeapon = WP_NOCHANGE;
                        p.SetPSprite(PSP_WEAPON, rightW.ResolveState("Ready"));
                    }

                    bool ok = DoDA.EnterAkimbo();
                    if (ok)
                    {
                        if (handState != null)
                        {
                            handState.SetupB92CompanionLayer(p, leftW.ResolveState("SecondaryReady"), leftW, rightW);
                        }
                        else
                        {
                            p.SetPSprite(2, leftW.ResolveState("SecondaryReady"));
                            let psp = p.GetPSprite(2);
                            if (psp != null)
                            {
                                psp.x = -48.0;
                                psp.y = 8.0;
                                psp.bMirror = false;
                                psp.bAddBob = true;
                                psp.bAddWeapon = false;
                            }
                        }
                        Console.Printf("[DoDA Akimbo] Akimbo mode entered via toggle action");
                    }
                    else
                    {
                        Console.Printf("[DoDA Akimbo] Akimbo mode enter failed: Pair validation rejected");
                    }
                }
                else
                {
                    Console.Printf("[DoDA Akimbo] Akimbo mode enter failed: Pair validation rejected");
                }
            }
            return;
        }

        if (e.Name == "DoDA_ToggleDualWield")
        {
            Console.Printf("[DoDA] Dual Wield toggle is not implemented in this proof.");
            return;
        }
    }

    override void WorldLoaded(WorldEvent e)
    {
        for (int i = 0; i < MAXPLAYERS; i++)
        {
            if (playeringame[i] && players[i] != null && players[i].mo != null)
            {
                let pb = DoDAPlayerBase(players[i].mo);
                if (pb != null)
                {
                    let hs = pb.GetHandState();
                    if (hs != null)
                    {
                        hs.ResetLifecycle(players[i]);
                    }
                }
            }
        }
        enteredFromLeft = false;
    }

    override void WorldUnloaded(WorldEvent e)
    {
        for (int i = 0; i < MAXPLAYERS; i++)
        {
            if (playeringame[i] && players[i] != null && players[i].mo != null)
            {
                let pb = DoDAPlayerBase(players[i].mo);
                if (pb != null)
                {
                    let hs = pb.GetHandState();
                    if (hs != null)
                    {
                        hs.ResetLifecycle(players[i]);
                    }
                }
            }
        }
        enteredFromLeft = false;
    }

    override void PlayerEntered(PlayerEvent e)
    {
        if (e.PlayerNumber >= 0 && e.PlayerNumber < MAXPLAYERS && players[e.PlayerNumber] != null && players[e.PlayerNumber].mo != null)
        {
            let pb = DoDAPlayerBase(players[e.PlayerNumber].mo);
            if (pb != null)
            {
                let hs = pb.GetHandState();
                if (hs != null)
                {
                    hs.ResetLifecycle(players[e.PlayerNumber]);
                }
            }
        }
        enteredFromLeft = false;
    }

    override void PlayerRespawned(PlayerEvent e)
    {
        if (e.PlayerNumber >= 0 && e.PlayerNumber < MAXPLAYERS && players[e.PlayerNumber] != null && players[e.PlayerNumber].mo != null)
        {
            let pb = DoDAPlayerBase(players[e.PlayerNumber].mo);
            if (pb != null)
            {
                let hs = pb.GetHandState();
                if (hs != null)
                {
                    hs.ResetLifecycle(players[e.PlayerNumber]);
                }
            }
        }
        enteredFromLeft = false;
    }

    override void PlayerDied(PlayerEvent e)
    {
        if (e.PlayerNumber >= 0 && e.PlayerNumber < MAXPLAYERS && players[e.PlayerNumber] != null && players[e.PlayerNumber].mo != null)
        {
            let pb = DoDAPlayerBase(players[e.PlayerNumber].mo);
            if (pb != null)
            {
                let hs = pb.GetHandState();
                if (hs != null)
                {
                    hs.ClearLayer2(players[e.PlayerNumber]);
                }
            }
        }
        enteredFromLeft = false;
    }
}
