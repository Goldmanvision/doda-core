/*//////////////////////////|
// DoDA/Debug/WeaponTestHarness.zs
//
// Development-only, explicitly gated weapon observability harness.
//
// Scope & Constraints:
//   - Disabled by default (DEV_GATE_ENABLED = 0).
//   - When disabled: strictly inert, emits 0 logs, consumes 0 input, executes 0 per-tick logic.
//   - When enabled (DEV_GATE_ENABLED = 1): emits registration marker on startup, provides read-only
//     weapon state snapshot on-demand via ConsoleEvent (netevent DoDA_WeaponHarnessSample / netevent doda_weapon_status).
//   - Read-only observation only: does not alter weapon state, ammunition, chamber state,
//     inventory, player movement, deadzone values, firing, reload, or gameplay behavior.
*///////////////////////////|

class DoDAWeaponTestHarness : StaticEventHandler
{
    // Explicit development gate: 0 = disabled for ordinary play, 1 = enabled for developer diagnostics.
    const DEV_GATE_ENABLED = 1;

    override void OnRegister()
    {
        if (!DEV_GATE_ENABLED)
        {
            return;
        }

        Console.Printf(
            "[DoDA-WEAPON-HARNESS] event=register status=dev-gate-active run=%u mode=read-only-observer",
            uint(MSTime())
        );
    }

    override void NetworkProcess(ConsoleEvent e)
    {
        if (!DEV_GATE_ENABLED)
        {
            return;
        }

        if (e.Name == "DoDA_WeaponHarnessSample" || e.Name == "doda_weapon_status")
        {
            SampleWeaponState(e.Player);
        }
    }

    static void SampleWeaponState(int playerNum)
    {
        if (playerNum < 0 || playerNum >= MAXPLAYERS || !playeringame[playerNum])
        {
            return;
        }

        let p = players[playerNum];
        if (p == null || p.mo == null)
        {
            return;
        }

        let readyW = p.ReadyWeapon;
        String weaponClass = (readyW != null) ? ("" .. readyW.GetClassName()) : "None";
        bool akimboActive = DoDA.IsAkimboActive();
        bool reloadLocked = DoDA.IsReloadLocked();

        let agent = DoDAPlayerBase(p.mo);
        bool deadzoneActive = (agent != null && agent.IsDeadzoneAimActive());
        double yawGap = (agent != null) ? agent.GetDeadzoneYawGap() : 0.0;
        double pitchGap = (agent != null) ? agent.GetDeadzonePitchGap() : 0.0;

        String details = "none";

        if (readyW is "DoDAPistol")
        {
            let pistol = DoDAPistol(readyW);
            int hand = pistol.GetWeaponHand();
            String handName = (hand == DoDAHandSwapController.Hand_Left) ? "Left" : "Right";
            int mag = pistol.GetMagazineRounds();
            int cap = pistol.GetMagazineCapacity();
            int reserve = pistol.GetReserveRounds();
            bool chamber = pistol.IsChamberLoaded();

            details = String.Format(
                "Pistol hand=%s mag=%d/%d chamber=%d reserve=%d",
                handName,
                mag,
                cap,
                chamber ? 1 : 0,
                reserve
            );
        }
        else if (readyW is "DoDAMP5KSD")
        {
            let mp5 = DoDAMP5KSD(readyW);
            int mode = mp5.GetFireMode();
            String modeName = (mode == DoDAMP5KSD.Fire_Auto) ? "Auto" : ((mode == DoDAMP5KSD.Fire_Burst) ? "Burst" : "Semi");
            int mag = mp5.GetMagazineRoundCount();
            int cap = mp5.GetMagazineCapacity();
            int loaded = mp5.GetLoadedRoundCount();
            bool chamber = mp5.IsChamberLoaded();

            details = String.Format(
                "MP5 mode=%s mag=%d/%d chamber=%d loaded=%d",
                modeName,
                mag,
                cap,
                chamber ? 1 : 0,
                loaded
            );
        }
        else if (readyW is "DoDAShotgun")
        {
            let shotgun = DoDAShotgun(readyW);
            int tube = shotgun.GetTubeShellCount();
            int cap = shotgun.GetTubeCapacity();
            bool chamber = shotgun.IsChamberLoaded();
            bool rack = shotgun.IsRackPending();
            int reserve = shotgun.GetReserveShellCount();
            String chamberStatus = shotgun.GetChamberStatusText();

            details = String.Format(
                "Shotgun tube=%d/%d chamber=%d (%s) rackPending=%d reserve=%d",
                tube,
                cap,
                chamber ? 1 : 0,
                chamberStatus,
                rack ? 1 : 0,
                reserve
            );
        }
        else if (readyW is "DoDAWeapon")
        {
            let dw = DoDAWeapon(readyW);
            details = String.Format("DoDAWeapon hand=%d", dw.GetWeaponHand());
        }

        Console.Printf(
            "[DoDA-WEAPON-HARNESS] player=%d ready=%s akimbo=%d reloadLock=%d deadzone=%d(yaw=%.2f,pitch=%.2f) details=[%s]",
            playerNum,
            weaponClass,
            akimboActive ? 1 : 0,
            reloadLocked ? 1 : 0,
            deadzoneActive ? 1 : 0,
            yawGap,
            pitchGap,
            details
        );
    }
}
