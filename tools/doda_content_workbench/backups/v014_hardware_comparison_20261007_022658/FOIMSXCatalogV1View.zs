/*//////////////////////////|
// DoDA/UI/FOIMSX/CatalogV1/FOIMSXCatalogV1View.zs
//
// FOIMS-X Workbench Catalog V1 — read-only browser for the generated
// DoDAWorkbenchCatalog (network tiers, hardware, equipment families/models).
//
// Scope:
//   - Presentation only. No native calls, no persistence, no rule logic.
//   - Owned and driven by DoDAFOIMSXDirectoryRenderer (Tab cycles pages).
//   - Data source is generated ZScript (Option B stopgap); the native layer
//     remains the future authority for simulation rules.
*///////////////////////////|

class DoDAFOIMSXCatalogV1View : Object
{
    const SECTION_TIERS = 0;
    const SECTION_HARDWARE = 1;
    const SECTION_FAMILIES = 2;
    const SECTION_MODELS = 3;
    const SECTION_COUNT = 4;
    const MAX_VISIBLE_ROWS = 29;

    private ui int mSection;
    private ui int mFocusedIndex;

    static ui DoDAFOIMSXCatalogV1View Create()
    {
        let v = new("DoDAFOIMSXCatalogV1View");
        v.mSection = SECTION_TIERS;
        v.mFocusedIndex = 0;
        return v;
    }

    ui void SetSection(int section)
    {
        if (section < 0 || section >= SECTION_COUNT)
        {
            section = SECTION_TIERS;
        }

        mSection = section;
        mFocusedIndex = (GetRowCount() > 0) ? 0 : -1;
    }

    ui int GetSection()
    {
        return mSection;
    }

    ui int GetRowCount()
    {
        switch (mSection)
        {
        case SECTION_TIERS: return DoDAWorkbenchCatalog.TIER_COUNT;
        case SECTION_HARDWARE: return DoDAWorkbenchCatalog.HARDWARE_COUNT;
        case SECTION_FAMILIES: return DoDAWorkbenchCatalog.FAMILY_COUNT;
        case SECTION_MODELS: return DoDAWorkbenchCatalog.MODEL_COUNT;
        default: return 0;
        }
    }

    ui String GetSectionTitle()
    {
        switch (mSection)
        {
        case SECTION_TIERS: return "NETWORK TIERS";
        case SECTION_HARDWARE: return "MODEMS / ROUTERS";
        case SECTION_FAMILIES: return "EQUIPMENT FAMILIES";
        case SECTION_MODELS: return "EQUIPMENT MODELS";
        default: return "CATALOG";
        }
    }

    // Uses the shared FOIMS-X navigation classification; selection is implicit
    // (detail pane follows focus), so Select and Clear are accepted no-ops.
    ui bool HandleNav(EDoDAFOIMSXNavCommand cmd)
    {
        int rowCount = GetRowCount();

        if (rowCount <= 0)
        {
            mFocusedIndex = -1;
            return false;
        }

        if (mFocusedIndex < 0)
        {
            mFocusedIndex = 0;
        }

        switch (cmd)
        {
        case FOIMSX_NAV_PREVIOUS: mFocusedIndex--; break;
        case FOIMSX_NAV_NEXT: mFocusedIndex++; break;
        case FOIMSX_NAV_PAGE_PREVIOUS: mFocusedIndex -= 5; break;
        case FOIMSX_NAV_PAGE_NEXT: mFocusedIndex += 5; break;
        case FOIMSX_NAV_FIRST: mFocusedIndex = 0; break;
        case FOIMSX_NAV_LAST: mFocusedIndex = rowCount - 1; break;
        case FOIMSX_NAV_SELECT: return true;
        case FOIMSX_NAV_CLEAR_SELECTION: return true;
        default: return false;
        }

        if (mFocusedIndex < 0)
        {
            mFocusedIndex = 0;
        }

        if (mFocusedIndex >= rowCount)
        {
            mFocusedIndex = rowCount - 1;
        }

        return true;
    }

    private ui String RowPrimary(int i)
    {
        switch (mSection)
        {
        case SECTION_TIERS: return DoDAWorkbenchCatalog.TierDisplayName(i);
        case SECTION_HARDWARE: return DoDAWorkbenchCatalog.HardwareDisplayName(i);
        case SECTION_FAMILIES: return DoDAWorkbenchCatalog.FamilyDisplayName(i);
        case SECTION_MODELS: return DoDAWorkbenchCatalog.ModelDisplayName(i);
        default: return "";
        }
    }

    private ui String RowSecondary(int i)
    {
        switch (mSection)
        {
        case SECTION_TIERS: return DoDAWorkbenchCatalog.TierNetworkType(i);
        case SECTION_HARDWARE: return DoDAWorkbenchCatalog.HardwareKind(i);
        case SECTION_FAMILIES: return DoDAWorkbenchCatalog.FamilyOwnership(i);
        case SECTION_MODELS: return DoDAWorkbenchCatalog.ModelFamilyId(i);
        default: return "";
        }
    }

    private static ui String OrNone(String value)
    {
        return (value.Length() > 0) ? value : "-";
    }

    private static ui String IntOrNone(int value)
    {
        return (value >= 0) ? String.Format("%d", value) : "-";
    }

    ui void RenderList()
    {
        int clipLeft, clipTop, clipRight, clipBottom;
        DoDAFOIMSXDrawingHelpers.GetRealClipRect(
            18, 80, 282, 330, clipLeft, clipTop, clipRight, clipBottom
        );

        int rowCount = GetRowCount();

        if (rowCount <= 0)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 20, 104,
                "[NO CATALOG RECORDS]",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 20, 82,
            "  NAME                         KIND",
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 20, 92,
            "------------------------------------------------------------",
            clipLeft, clipTop, clipRight, clipBottom);

        int first = 0;
        if (mFocusedIndex >= MAX_VISIBLE_ROWS)
        {
            first = mFocusedIndex - MAX_VISIBLE_ROWS + 1;
        }

        for (int row = 0; row < MAX_VISIBLE_ROWS; row++)
        {
            int i = first + row;
            if (i >= rowCount)
            {
                break;
            }

            double rowY = 104 + (row * 10);
            bool isFocused = (i == mFocusedIndex);

            if (isFocused)
            {
                DoDAFOIMSXDrawingHelpers.DrawVirtualRect(19, rowY - 1, 280, 10, 0xFF183868);
                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GOLD, 20.0, rowY, ">",
                    clipLeft, clipTop, clipRight, clipBottom);
            }

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont,
                isFocused ? Font.CR_WHITE : Font.CR_GRAY, 30.0, rowY,
                RowPrimary(i).MakeUpper(),
                clipLeft, clipTop, clipRight, clipBottom, 26);

            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_CYAN, 172.0, rowY,
                RowSecondary(i),
                clipLeft, clipTop, clipRight, clipBottom, 14);
        }
    }

    private ui void DetailLine(int line, String label, String value,
        int clipLeft, int clipTop, int clipRight, int clipBottom)
    {
        double y = 114 + (line * 18);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, y, label,
            clipLeft, clipTop, clipRight, clipBottom);

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 430, y, value,
            clipLeft, clipTop, clipRight, clipBottom, 20);
    }

    ui void RenderDetail()
    {
        int clipLeft, clipTop, clipRight, clipBottom;
        DoDAFOIMSXDrawingHelpers.GetRealClipRect(
            312, 80, 310, 330, clipLeft, clipTop, clipRight, clipBottom
        );

        int i = mFocusedIndex;

        if (i < 0 || i >= GetRowCount())
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 210,
                "NO RECORD FOCUSED",
                clipLeft, clipTop, clipRight, clipBottom);
            return;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 330, 90,
            RowPrimary(i).MakeUpper(),
            clipLeft, clipTop, clipRight, clipBottom, 32);

        switch (mSection)
        {
        case SECTION_TIERS:
            DetailLine(0, "ID:", DoDAWorkbenchCatalog.TierId(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "TYPE:", DoDAWorkbenchCatalog.TierNetworkType(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "GENERATION:", IntOrNone(DoDAWorkbenchCatalog.TierGeneration(i)), clipLeft, clipTop, clipRight, clipBottom);
            break;

        case SECTION_HARDWARE:
            DetailLine(0, "ID:", DoDAWorkbenchCatalog.HardwareId(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "KIND:", DoDAWorkbenchCatalog.HardwareKind(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "TIER:", DoDAWorkbenchCatalog.HardwareTierId(i), clipLeft, clipTop, clipRight, clipBottom);
            break;

        case SECTION_FAMILIES:
            DetailLine(0, "ID:", DoDAWorkbenchCatalog.FamilyId(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "OWNERSHIP:", DoDAWorkbenchCatalog.FamilyOwnership(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "STORAGE:", DoDAWorkbenchCatalog.FamilyStorageKind(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(3, "CONNECTION:", DoDAWorkbenchCatalog.FamilyConnectionKind(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(4, "PER TASK:", IntOrNone(DoDAWorkbenchCatalog.FamilyPerTaskLimit(i)), clipLeft, clipTop, clipRight, clipBottom);
            break;

        case SECTION_MODELS:
            DetailLine(0, "ID:", DoDAWorkbenchCatalog.ModelId(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "FAMILY:", DoDAWorkbenchCatalog.ModelFamilyId(i), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "PHONE LINE:", OrNone(DoDAWorkbenchCatalog.ModelPhoneLineKind(i)), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(3, "NETWORK TIER:", OrNone(DoDAWorkbenchCatalog.ModelNetworkTierId(i)), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(4, "CONNECTION:", OrNone(DoDAWorkbenchCatalog.ModelConnectionOverride(i)), clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(5, "GENERATION:", IntOrNone(DoDAWorkbenchCatalog.ModelGeneration(i)), clipLeft, clipTop, clipRight, clipBottom);
            break;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 330, 380,
            String.Format("RECORD %d OF %d   READ-ONLY CATALOG", i + 1, GetRowCount()),
            clipLeft, clipTop, clipRight, clipBottom);
    }
}
