class DoDAAkimboInputHandler : StaticEventHandler
{
    bool enteredFromLeft;

    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name == "DoDA_ToggleAkimbo")
        {
            let p = players[e.Player];
            if (p == null || p.mo == null) return;

            if (DoDA.IsAkimboActive())
            {
                DoDA.ExitAkimbo();
                p.SetPSprite(2, null);

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
                        p.SetPSprite(2, leftW.ResolveState("SecondaryReady"));
                        let psp = p.GetPSprite(2);
                        if (psp != null)
                        {
                            psp.x = -48.0;
                            psp.y = 8.0;
                            psp.bMirror = false;
                            psp.bAddBob = true;
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
}
