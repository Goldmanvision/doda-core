/*//////////////////////////|
// DoDA/UI/FOIMSX/CatalogV1/FOIMSXCatalogV1View.zs
//
// FOIMS-X Workbench Catalog V1 — read-only browser for the generated
// DoDAWorkbenchCatalog (network/equipment, facilities/capabilities, authored staffing).
//
// Scope:
//   - Presentation only. No native calls, persistence, or gameplay enforcement.
//   - Hardware pair comparison is a temporary display proof of NET-01.
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
    const SECTION_FACILITIES = 4;
    const SECTION_CAPABILITIES = 5;
    const SECTION_STAFFING_DEFAULTS = 6;
    const SECTION_FACILITY_STAFFING = 7;
    const SECTION_COUNT = 8;
    const MAX_VISIBLE_ROWS = 29;

    private ui int mSection;
    private ui int mFocusedIndex;
    private ui String mComparisonModemId;
    private ui String mComparisonRouterId;

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
        case SECTION_FACILITIES: return DoDAWorkbenchCatalog.FACILITY_COUNT;
        case SECTION_CAPABILITIES: return DoDAWorkbenchCatalog.CAPABILITY_COUNT;
        case SECTION_STAFFING_DEFAULTS: return DoDAWorkbenchCatalog.STAFFING_DEFAULT_COUNT;
        case SECTION_FACILITY_STAFFING: return DoDAWorkbenchCatalog.FACILITY_STAFFING_COUNT;
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
        case SECTION_FACILITIES: return "FACILITIES";
        case SECTION_CAPABILITIES: return "CAPABILITIES";
        case SECTION_STAFFING_DEFAULTS: return "STAFFING DEFAULTS";
        case SECTION_FACILITY_STAFFING: return "FACILITY STAFFING";
        default: return "CATALOG";
        }
    }

    // Uses the shared FOIMS-X navigation classification; selection is implicit
    // (detail pane follows focus). On hardware only, Select chooses a comparison
    // candidate by stable ID and Clear clears both candidates.
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
        case FOIMSX_NAV_SELECT:
            if (mSection == SECTION_HARDWARE)
            {
                String kind = DoDAWorkbenchCatalog.HardwareKind(mFocusedIndex);
                String id = DoDAWorkbenchCatalog.HardwareId(mFocusedIndex);
                if (kind == "MODEM") mComparisonModemId = id;
                else if (kind == "ROUTER") mComparisonRouterId = id;
            }
            return true;
        case FOIMSX_NAV_CLEAR_SELECTION:
            if (mSection == SECTION_HARDWARE)
            {
                mComparisonModemId = "";
                mComparisonRouterId = "";
            }
            return true;
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
        case SECTION_FACILITIES: return DoDAWorkbenchCatalog.FacilityDisplayName(i);
        case SECTION_CAPABILITIES: return DoDAWorkbenchCatalog.CapabilityDisplayName(i);
        case SECTION_STAFFING_DEFAULTS: return DoDAWorkbenchCatalog.StaffingDefaultQualificationName(i);
        case SECTION_FACILITY_STAFFING: return DoDAWorkbenchCatalog.FacilityStaffingQualificationName(i);
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
        case SECTION_FACILITIES: return "FACILITY";
        case SECTION_CAPABILITIES: return "CAPABILITY";
        case SECTION_STAFFING_DEFAULTS: return "GLOBAL";
        case SECTION_FACILITY_STAFFING: return DoDAWorkbenchCatalog.FacilityStaffingSource(i);
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
            mSection >= SECTION_STAFFING_DEFAULTS
                ? "  QUALIFICATION                SOURCE"
                : "  NAME                         KIND",
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
            clipLeft, clipTop, clipRight, clipBottom);
    }

    private ui void RenderHardwareComparison(
        int clipLeft, int clipTop, int clipRight, int clipBottom)
    {
        int modem = DoDAWorkbenchCatalog.FindHardware(mComparisonModemId);
        int router = DoDAWorkbenchCatalog.FindHardware(mComparisonRouterId);
        String modemTier = "";
        String routerTier = "";
        String result = "SELECT A MODEM AND ROUTER";
        int resultColor = Font.CR_GRAY;

        // Unknown/stale IDs, wrong kinds, or missing tier references cannot
        // report a successful match. No fallback by name or row position.
        bool validModem = modem >= 0 &&
            DoDAWorkbenchCatalog.HardwareKind(modem) == "MODEM";
        bool validRouter = router >= 0 &&
            DoDAWorkbenchCatalog.HardwareKind(router) == "ROUTER";

        if (validModem) modemTier = DoDAWorkbenchCatalog.HardwareTierId(modem);
        if (validRouter) routerTier = DoDAWorkbenchCatalog.HardwareTierId(router);

        if (validModem && validRouter)
        {
            if (DoDAWorkbenchCatalog.FindTier(modemTier) < 0 ||
                DoDAWorkbenchCatalog.FindTier(routerTier) < 0)
            {
                result = "INVALID TIER REFERENCE";
                resultColor = Font.CR_RED;
            }
            else if (modemTier == routerTier)
            {
                result = "MATCH: EXACT SAME TIER";
                resultColor = Font.CR_CYAN;
            }
            else
            {
                result = "MISMATCH: DIFFERENT TIERS";
                resultColor = Font.CR_RED;
            }
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GOLD, 330, 194,
            "MODEM / ROUTER COMPARISON",
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 330, 208,
            "TEMPORARY DISPLAY PROOF ONLY",
            clipLeft, clipTop, clipRight, clipBottom);

        // Full-width lines preserve IDs that exceed the normal value column.
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 330, 232,
            "MODEM: " .. OrNone(mComparisonModemId),
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 246,
            "TIER:  " .. OrNone(modemTier),
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE, 330, 266,
            "ROUTER: " .. OrNone(mComparisonRouterId),
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 280,
            "TIER:   " .. OrNone(routerTier),
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, resultColor, 330, 306,
            result, clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 330,
            "ENTER CHOOSE   BACKSPACE CLEAR",
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 330, 348,
            "NO EQUIPPING OR CAMPAIGN CHANGES",
            clipLeft, clipTop, clipRight, clipBottom);
    }

    private ui void RenderDepartmentDetail(int i,
        int clipLeft, int clipTop, int clipRight, int clipBottom)
    {
        bool facilityPage = mSection == SECTION_FACILITIES;
        String id = facilityPage ? DoDAWorkbenchCatalog.FacilityId(i)
                                 : DoDAWorkbenchCatalog.CapabilityId(i);
        String description = facilityPage ? DoDAWorkbenchCatalog.FacilityDescription(i)
                                          : DoDAWorkbenchCatalog.CapabilityDescription(i);
        DetailLine(0, "ID:", id, clipLeft, clipTop, clipRight, clipBottom);
        if (facilityPage)
        {
            DetailLine(1, "TRACK:", DoDAWorkbenchCatalog.FacilityTrackName(i),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "HQ ZONE:", DoDAWorkbenchCatalog.FacilityZoneId(i),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(3, "CAPACITY:", IntOrNone(DoDAWorkbenchCatalog.FacilityCapacity(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(4, "INITIAL TIER:", DoDAWorkbenchCatalog.FacilityInitialTier(i),
                clipLeft, clipTop, clipRight, clipBottom);
        }
        else
        {
            DetailLine(1, "STANDING LABEL:", DoDAWorkbenchCatalog.CapabilityStandingLabel(i),
                clipLeft, clipTop, clipRight, clipBottom);
        }

        // Three fixed-width description lines; explicit ellipsis if truncated.
        for (int line = 0; line < 3; line++)
        {
            if (description.Length() <= line * 56) break;
            String text = description.Mid(line * 56, 56);
            if (line == 2 && description.Length() > 168) text = text.Left(53) .. "...";
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY,
                330, 208 + line * 10, text, clipLeft, clipTop, clipRight, clipBottom);
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GOLD, 330, 248,
            facilityPage ? "AUTHORED CAPABILITIES" : "SUPPORTING FACILITIES",
            clipLeft, clipTop, clipRight, clipBottom);
        int count = 0;
        for (int link = 0; link < DoDAWorkbenchCatalog.FACILITY_CAPABILITY_COUNT; link++)
        {
            String linkedId = facilityPage
                ? DoDAWorkbenchCatalog.FacilityCapabilityFacilityId(link)
                : DoDAWorkbenchCatalog.FacilityCapabilityCapabilityId(link);
            if (linkedId != id) continue;
            if (count < 3)
            {
                String label = DoDAWorkbenchCatalog.FacilityCapabilityDisplayName(link);
                if (!facilityPage)
                {
                    int facilityIndex = DoDAWorkbenchCatalog.FindFacility(
                        DoDAWorkbenchCatalog.FacilityCapabilityFacilityId(link));
                    label = DoDAWorkbenchCatalog.FacilityDisplayName(facilityIndex);
                }
                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_WHITE,
                    330, 266 + count * 26, label, clipLeft, clipTop, clipRight, clipBottom);
                DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY,
                    330, 278 + count * 26,
                    "INITIAL: " .. DoDAWorkbenchCatalog.FacilityCapabilityInitialTier(link),
                    clipLeft, clipTop, clipRight, clipBottom);
            }
            count++;
        }
        if (count == 0)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 266,
                facilityPage ? "NO AUTHORED CAPABILITIES" : "NO LINKED FACILITIES",
                clipLeft, clipTop, clipRight, clipBottom);
        }
        if (count > 3)
        {
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 330, 348,
                String.Format("+%d MORE LINKS (SEE WORKBENCH)", count - 3),
                clipLeft, clipTop, clipRight, clipBottom);
        }
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 330, 364,
            "AUTHORED DEFAULTS - NOT LIVE STATUS",
            clipLeft, clipTop, clipRight, clipBottom);
    }

    private ui void RenderStaffingDetail(int i,
        int clipLeft, int clipTop, int clipRight, int clipBottom)
    {
        if (mSection == SECTION_STAFFING_DEFAULTS)
        {
            int capabilityIndex = DoDAWorkbenchCatalog.FindCapability(
                DoDAWorkbenchCatalog.StaffingDefaultCapabilityId(i));
            DetailLine(0, "CAPABILITY:", DoDAWorkbenchCatalog.CapabilityDisplayName(capabilityIndex),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "QUALIFICATION:", DoDAWorkbenchCatalog.StaffingDefaultQualificationId(i),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "MINIMUM:", IntOrNone(DoDAWorkbenchCatalog.StaffingDefaultMin(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(3, "PREFERRED:", IntOrNone(DoDAWorkbenchCatalog.StaffingDefaultPreferred(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(4, "MAXIMUM:", IntOrNone(DoDAWorkbenchCatalog.StaffingDefaultMax(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(5, "SOURCE:", "GLOBAL DEFAULT",
                clipLeft, clipTop, clipRight, clipBottom);
        }
        else
        {
            int facilityIndex = DoDAWorkbenchCatalog.FindFacility(
                DoDAWorkbenchCatalog.FacilityStaffingFacilityId(i));
            DetailLine(0, "FACILITY:", DoDAWorkbenchCatalog.FacilityDisplayName(facilityIndex),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(1, "CAPABILITY:", DoDAWorkbenchCatalog.FacilityStaffingCapabilityName(i),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(2, "QUALIFICATION:", DoDAWorkbenchCatalog.FacilityStaffingQualificationId(i),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(3, "GLOBAL:", String.Format("%d / %d / %d",
                DoDAWorkbenchCatalog.FacilityStaffingGlobalMin(i),
                DoDAWorkbenchCatalog.FacilityStaffingGlobalPreferred(i),
                DoDAWorkbenchCatalog.FacilityStaffingGlobalMax(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            DetailLine(4, "EFFECTIVE:", String.Format("%d / %d / %d",
                DoDAWorkbenchCatalog.FacilityStaffingMin(i),
                DoDAWorkbenchCatalog.FacilityStaffingPreferred(i),
                DoDAWorkbenchCatalog.FacilityStaffingMax(i)),
                clipLeft, clipTop, clipRight, clipBottom);
            String source = DoDAWorkbenchCatalog.FacilityStaffingSource(i);
            DetailLine(5, "SOURCE:", source == "OVERRIDE" ? "FACILITY OVERRIDE" : "INHERITED GLOBAL",
                clipLeft, clipTop, clipRight, clipBottom);
            DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 248,
                "RANGES: MINIMUM / PREFERRED / MAXIMUM",
                clipLeft, clipTop, clipRight, clipBottom);
        }
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 314,
            "COUNTS ARE PER QUALIFICATION ROW",
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_GRAY, 330, 330,
            "NO SUMMED HEADCOUNT OR LIVE READINESS",
            clipLeft, clipTop, clipRight, clipBottom);
        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_YELLOW, 330, 364,
            "AUTHORED REQUIREMENTS - NOT LIVE STATUS",
            clipLeft, clipTop, clipRight, clipBottom);
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
            RenderHardwareComparison(clipLeft, clipTop, clipRight, clipBottom);
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
        case SECTION_FACILITIES:
        case SECTION_CAPABILITIES:
            RenderDepartmentDetail(i, clipLeft, clipTop, clipRight, clipBottom);
            break;
        case SECTION_STAFFING_DEFAULTS:
        case SECTION_FACILITY_STAFFING:
            RenderStaffingDetail(i, clipLeft, clipTop, clipRight, clipBottom);
            break;
        }

        DoDAFOIMSXDrawingHelpers.DrawClippedText(NewSmallFont, Font.CR_DARKGRAY, 330, 380,
            String.Format("RECORD %d OF %d   READ-ONLY CATALOG", i + 1, GetRowCount()),
            clipLeft, clipTop, clipRight, clipBottom);
    }
}
