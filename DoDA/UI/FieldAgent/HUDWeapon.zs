///////////////////////////
// DoDA/UI/FieldAgent/HUDWeapon.zs
///////////////////////////

class DoDAHUDWeapon : Object
{
    void DrawWeaponSlot(
        DoDAWeaponHUDData data,
        int y
    )
    {
        if (data == null)
        {
            return;
        }

        int textColor = data.Equipped
            ? Font.CR_GREEN
            : Font.CR_WHITE;

        if (!data.IsShotgun && !data.IsMP5 && (data.MagazineRounds + (data.ChamberLoaded ? 1 : 0)) == 0)
        {
            textColor = Font.CR_RED;
        }

        String text;

        if (!data.Available)
        {
            textColor = Font.CR_RED;

            text = String.Format(
                "%s: UNAVAILABLE",
                data.Label
            );
        }
        else if (data.IsShotgun)
        {
            if (data.ChamberStatus == "SPENT / UNRACKED")
            {
                textColor = Font.CR_GOLD;
            }
            else if (data.ChamberStatus == "EMPTY")
            {
                textColor = Font.CR_RED;
            }

            text = String.Format(
                "%s%s  TUBE %02d/%02d  CH %s",
                data.Equipped ? ">" : " ",
                data.Label,
                data.MagazineRounds,
                data.MagazineCapacity,
                data.ChamberStatus
            );
        }
        else if (data.IsMP5)
        {
            text = String.Format(
                "%s%s  %02d + %d  %s",
                data.Equipped ? ">" : " ",
                data.Label,
                data.MagazineRounds,
                data.ChamberLoaded ? 1 : 0,
                data.FireMode == 0 ? "SEMI" : (data.FireMode == 1 ? "BURST" : "AUTO")
            );
        }
        else if (data.MagazineCapacity <= 0)
        {
            text = String.Format(
                "%s%s  NO MAGAZINE",
                data.Equipped ? ">" : " ",
                data.Label
            );
        }
        else
        {
            text = String.Format(
                "%s%s  MAG %02d/%02d  CH %d",
                data.Equipped ? ">" : " ",
                data.Label,
                data.MagazineRounds,
                data.MagazineCapacity,
                data.ChamberLoaded ? 1 : 0
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
        DoDAWeaponHUDData primary,
        DoDAWeaponHUDData companion,
        int reserveRounds
    )
    {
        if (primary == null)
        {
            return;
        }

        int bottomMargin = 20;
        int lineGap = 6;
        int lineHeight = SmallFont.GetHeight();
        int lineStep = lineHeight + lineGap;

        int reserveY = Screen.GetHeight()
            - bottomMargin
            - lineHeight;

        int companionY = reserveY - lineStep;

        bool companionAvailable = companion != null && companion.Available;

        int primaryY = companionAvailable
            ? companionY - lineStep
            : companionY;

        DrawWeaponSlot(
            primary,
            primaryY
        );

        if (companionAvailable)
        {
            DrawWeaponSlot(
                companion,
                companionY
            );
        }

        String reserveLabel = primary.IsShotgun
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