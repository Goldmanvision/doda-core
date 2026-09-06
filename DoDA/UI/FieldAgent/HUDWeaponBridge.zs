///////////////////////////
// DoDA/UI/FieldAgent/HUDWeaponBridge.zs
///////////////////////////

// A reference class is used instead of a struct because the status-bar
// bridge returns weapon data to the HUD.
class DoDAWeaponHUDData : Object
{
    bool Available;
    bool Equipped;
    bool IsShotgun;
    bool IsMP5;

    String Label;
    String ChamberStatus;

    int MagazineRounds;
    int MagazineCapacity;
    bool ChamberLoaded;
    int FireMode;
}

class DoDAWeaponHUDBridge : Object
{
    static ui DoDAWeaponHUDData GetWeaponData(
        Weapon weapon,
        Weapon readyWeapon
    )
    {
        if (weapon == null)
        {
            return null;
        }

        let shotgun = DoDAShotgun(weapon);

        if (shotgun != null)
        {
            let shotgunData = new("DoDAWeaponHUDData");

            shotgunData.Available = true;
            shotgunData.Equipped = weapon == readyWeapon;
            shotgunData.IsShotgun = true;
            shotgunData.Label = "SHOTGUN";

            shotgunData.MagazineRounds =
                shotgun.GetTubeShellCount();

            shotgunData.MagazineCapacity =
                shotgun.GetTubeCapacity();

            shotgunData.ChamberLoaded =
                shotgun.IsChamberLoaded();

            shotgunData.ChamberStatus =
                shotgun.GetChamberStatusText();

            return shotgunData;
        }

        let pistol = DoDAPistol(weapon);

        if (pistol == null || !pistol.UsesWeaponHUD())
        {
            let mp5 = DoDAMP5KSD(weapon);
            if (mp5 != null)
            {
                let mp5Data = new("DoDAWeaponHUDData");
                mp5Data.Available = true;
                mp5Data.Equipped = weapon == readyWeapon;
                mp5Data.IsShotgun = false;
                mp5Data.IsMP5 = true;
                mp5Data.Label = "MP5KSD";
                mp5Data.MagazineRounds = mp5.magazineRounds;
                mp5Data.MagazineCapacity = mp5.MagazineCapacity;
                mp5Data.ChamberLoaded = mp5.chamberLoaded;
                mp5Data.FireMode = mp5.GetFireMode();
                return mp5Data;
            }
            return null;
        }

        let pistolData = new("DoDAWeaponHUDData");

        pistolData.Available = true;
        pistolData.Equipped = weapon == readyWeapon;
        pistolData.IsShotgun = false;

        pistolData.MagazineRounds =
            pistol.GetMagazineRounds();

        pistolData.MagazineCapacity =
            pistol.GetMagazineCapacity();

        pistolData.ChamberLoaded =
            pistol.IsChamberLoaded();

        if (DoDAB92Left(weapon) != null)
        {
            pistolData.Label = "LEFT B92";
        }
        else if (DoDAB92Right(weapon) != null)
        {
            pistolData.Label = "RIGHT B92";
        }
        else
        {
            pistolData.Label = "B92";
        }

        return pistolData;
    }

    static ui DoDAWeaponHUDData GetActiveWeaponData(
        Weapon readyWeapon
    )
    {
        return GetWeaponData(
            readyWeapon,
            readyWeapon
        );
    }

    static ui DoDAWeaponHUDData GetCompanionWeaponData(
        Actor pawn,
        Weapon readyWeapon
    )
    {
        if (pawn == null || readyWeapon == null)
        {
            return null;
        }

        Name companionClass = 'None';

        if (DoDAB92Left(readyWeapon) != null)
        {
            companionClass = 'DoDAB92Right';
        }
        else if (DoDAB92Right(readyWeapon) != null)
        {
            companionClass = 'DoDAB92Left';
        }

        if (companionClass == 'None')
        {
            return null;
        }

        let companionWeapon = Weapon(
            pawn.FindInventory(companionClass)
        );

        return GetWeaponData(
            companionWeapon,
            readyWeapon
        );
    }

    static ui int GetReserveRounds(
        Weapon readyWeapon
    )
    {
        let shotgun = DoDAShotgun(readyWeapon);

        if (shotgun != null)
        {
            return shotgun.GetReserveShellCount();
        }

        let pistol = DoDAPistol(readyWeapon);

        if (pistol != null && pistol.UsesWeaponHUD())
        {
            return pistol.GetReserveRounds();
        }

        let mp5 = DoDAMP5KSD(readyWeapon);
        if (mp5 != null && mp5.owner != null)
        {
            let reserveAmmo = Ammo(mp5.owner.FindInventory('Clip'));
            return reserveAmmo ? reserveAmmo.Amount : 0;
        }

        return 0;
    }
}