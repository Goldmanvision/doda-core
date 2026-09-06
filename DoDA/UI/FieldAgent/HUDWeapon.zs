///////////////////////////
// DoDA/UI/FieldAgent/HUDWeapon.zs
///////////////////////////

class DoDAHUDWeapon : Object
{
    void DrawWeaponSlot(
        String label,
        bool available,
        bool equipped,
        bool isShotgun,
        bool isMP5,
        int magazineRounds,
        int magazineCapacity,
        bool chamberLoaded,
        String chamberStatus,
        int fireMode,
        int y
    )
    {
        int textColor = equipped
            ? Font.CR_GREEN
            : Font.CR_WHITE;

        if (!isShotgun && !isMP5 && (magazineRounds + (chamberLoaded ? 1 : 0)) == 0)
        {
            textColor = Font.CR_RED;
        }

        String text;

        if (!available)
        {
            textColor = Font.CR_RED;

            text = String.Format(
                "%s: UNAVAILABLE",
                label
            );
        }
        else if (isShotgun)
        {
            if (chamberStatus == "SPENT / UNRACKED")
            {
                textColor = Font.CR_GOLD;
            }
            else if (chamberStatus == "EMPTY")
            {
                textColor = Font.CR_RED;
            }

            text = String.Format(
                "%s%s  TUBE %02d/%02d  CH %s",
                equipped ? ">" : " ",
                label,
                magazineRounds,
                magazineCapacity,
                chamberStatus
            );
        }
        else if (isMP5)
        {
            text = String.Format(
                "%s%s  %02d + %d  %s",
                equipped ? ">" : " ",
                label,
                magazineRounds,
                chamberLoaded ? 1 : 0,
                fireMode == 0 ? "SEMI" : (fireMode == 1 ? "BURST" : "AUTO")
            );
        }
        else if (magazineCapacity <= 0)
        {
            text = String.Format(
                "%s%s  NO MAGAZINE",
                equipped ? ">" : " ",
                label
            );
        }
        else
        {
            text = String.Format(
                "%s%s  MAG %02d/%02d  CH %d",
                equipped ? ">" : " ",
                label,
                magazineRounds,
                magazineCapacity,
                chamberLoaded ? 1 : 0
            );
        }

        Screen.DrawText(
            SmallFont,
            textColor,
            16,
            y,
            text,
            DTA_CleanNoMove,
            true
        );
    }

    void DrawWeaponReadout(
        String primaryLabel,
        bool primaryAvailable,
        bool primaryEquipped,
        bool primaryIsShotgun,
        bool primaryIsMP5,
        int primaryMagazineRounds,
        int primaryMagazineCapacity,
        bool primaryChamberLoaded,
        String primaryChamberStatus,
        int primaryFireMode,
        String companionLabel,
        bool companionAvailable,
        bool companionEquipped,
        bool companionIsShotgun,
        int companionMagazineRounds,
        int companionMagazineCapacity,
        bool companionChamberLoaded,
        String companionChamberStatus,
        int reserveRounds
    )
    {
        int bottomMargin = 20;
        int lineGap = 6;
        int lineHeight = SmallFont.GetHeight();
        int lineStep = lineHeight + lineGap;

        int reserveY = Screen.GetHeight()
            - bottomMargin
            - lineHeight;

        int companionY = reserveY - lineStep;

        int primaryY = companionAvailable
            ? companionY - lineStep
            : companionY;

        DrawWeaponSlot(
            primaryLabel,
            primaryAvailable,
            primaryEquipped,
            primaryIsShotgun,
            primaryIsMP5, // New
            primaryMagazineRounds,
            primaryMagazineCapacity,
            primaryChamberLoaded,
            primaryChamberStatus,
            primaryFireMode, // New
            primaryY
        );

        if (companionAvailable)
        {
            DrawWeaponSlot(
                companionLabel,
                true,
                companionEquipped,
                companionIsShotgun,
                false, // companionIsMP5
                companionMagazineRounds,
                companionMagazineCapacity,
                companionChamberLoaded,
                companionChamberStatus,
                0, // companionFireMode
                companionY
            );
        }

        String reserveLabel = primaryIsShotgun
            ? "SHELLS"
            : "RESERVE";

        Screen.DrawText(
            SmallFont,
            Font.CR_GOLD,
            16,
            reserveY,
            String.Format(
                "%s  %03d",
                reserveLabel,
                reserveRounds
            ),
            DTA_CleanNoMove,
            true
        );
    }
}