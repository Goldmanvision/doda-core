/*//////////////////////////|
// DoDA/Generated/WorkbenchCatalog.zs
*///////////////////////////|
// GENERATED FILE - DO NOT EDIT. Regenerate with
//   tools/doda_content_workbench/doda_zscript_catalog.py
// Generator 0.4.0; network content sha256 ca30bb147d2525c2d7ba9aeab9360fb3e53be65dd639812bee4f51ec8d0dfa36
// equipment content sha256 52bf81d446b00a3f0c808618224c12ed629738d5cd819ae0e6b5c800a9c39cab
// department catalog content sha256 e00c18e3e36a0b6f8b78e2ab04057f3a41fb656c1212d6f9abe358e69b84a02f
// Read-only display/lookup catalog (Option B stopgap). No simulation rules.

class DoDAWorkbenchCatalog : Object
{
    const TIER_COUNT = 5;
    const HARDWARE_COUNT = 10;
    const FAMILY_COUNT = 5;
    const MODEL_COUNT = 7;
    const FACILITY_COUNT = 6;
    const CAPABILITY_COUNT = 2;
    const FACILITY_CAPABILITY_COUNT = 2;
    const STAFFING_DEFAULT_COUNT = 4;
    const FACILITY_STAFFING_COUNT = 4;
    const STAFFING_OVERRIDE_COUNT = 3;
    const TASK_TEMPLATE_COUNT = 2;
    const TOTAL_PERSONAL_DEVICE_LIMIT = 8;

    static String GeneratorVersion() { return "0.4.0"; }
    static String NetworkSourceHash() { return "ca30bb147d2525c2"; }
    static String EquipmentSourceHash() { return "52bf81d446b00a3f"; }
    static String DepartmentSourceHash() { return "e00c18e3e36a0b6f"; }

    // Network tiers
    static String TierId(int i)
    {
        switch (i)
        {
        case 0: return "NET_DIALUP_G1";
        case 1: return "NET_DIALUP_G2";
        case 2: return "NET_LEASED_G1";
        case 3: return "NET_LEASED_G2";
        case 4: return "NET_FIBER_G1";
        default: return "";
        }
    }

    static String TierDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "14.4KB/s Dial-up";
        case 1: return "56K Dial-up";
        case 2: return "1.5MB/s Leased Line (T1)";
        case 3: return "44MB/s Leased Line (T3)";
        case 4: return "2GB/s Fiber";
        default: return "";
        }
    }

    static String TierNetworkType(int i)
    {
        switch (i)
        {
        case 0: return "DIALUP";
        case 1: return "DIALUP";
        case 2: return "LEASED_LINE";
        case 3: return "LEASED_LINE";
        case 4: return "FIBER";
        default: return "";
        }
    }

    static int TierGeneration(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 2;
        case 2: return 1;
        case 3: return 2;
        case 4: return 1;
        default: return -2;
        }
    }

    static int FindTier(String id)
    {
        for (int i = 0; i < TIER_COUNT; i++)
        {
            if (TierId(i) == id) return i;
        }
        return -1;
    }

    // Network hardware (modems / routers)
    static String HardwareId(int i)
    {
        switch (i)
        {
        case 0: return "MODEM_DIALUP_G1";
        case 1: return "ROUTER_DIALUP_G1";
        case 2: return "MODEM_DIALUP_G2";
        case 3: return "ROUTER_DIALUP_G2";
        case 4: return "MODEM_LEASED_G1";
        case 5: return "ROUTER_LEASED_G1";
        case 6: return "MODEM_LEASED_G2";
        case 7: return "ROUTER_LEASED_G2";
        case 8: return "MODEM_FIBER_G1";
        case 9: return "ROUTER_FIBER_G1";
        default: return "";
        }
    }

    static String HardwareDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "14.4KB/s Dial-up Modem";
        case 1: return "14.4KB/s Dial-up Router";
        case 2: return "56K Dial-up Modem";
        case 3: return "56K Dial-up Router";
        case 4: return "1.5MB/s Leased Line (T1) Modem";
        case 5: return "1.5MB/s Leased Line (T1) Router";
        case 6: return "44MB/s Leased Line (T3) Modem";
        case 7: return "44MB/s Leased Line (T3) Router";
        case 8: return "2GB/s Fiber Modem";
        case 9: return "2GB/s Fiber Router";
        default: return "";
        }
    }

    static String HardwareKind(int i)
    {
        switch (i)
        {
        case 0: return "MODEM";
        case 1: return "ROUTER";
        case 2: return "MODEM";
        case 3: return "ROUTER";
        case 4: return "MODEM";
        case 5: return "ROUTER";
        case 6: return "MODEM";
        case 7: return "ROUTER";
        case 8: return "MODEM";
        case 9: return "ROUTER";
        default: return "";
        }
    }

    static String HardwareTierId(int i)
    {
        switch (i)
        {
        case 0: return "NET_DIALUP_G1";
        case 1: return "NET_DIALUP_G1";
        case 2: return "NET_DIALUP_G2";
        case 3: return "NET_DIALUP_G2";
        case 4: return "NET_LEASED_G1";
        case 5: return "NET_LEASED_G1";
        case 6: return "NET_LEASED_G2";
        case 7: return "NET_LEASED_G2";
        case 8: return "NET_FIBER_G1";
        case 9: return "NET_FIBER_G1";
        default: return "";
        }
    }

    static int FindHardware(String id)
    {
        for (int i = 0; i < HARDWARE_COUNT; i++)
        {
            if (HardwareId(i) == id) return i;
        }
        return -1;
    }

    // Equipment families
    static String FamilyId(int i)
    {
        switch (i)
        {
        case 0: return "DESKTOP";
        case 1: return "LAPTOP";
        case 2: return "PDA";
        case 3: return "PHONE";
        case 4: return "FAX";
        default: return "";
        }
    }

    static String FamilyDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Desktop Computers";
        case 1: return "Laptop Computers";
        case 2: return "PDA Devices";
        case 3: return "Phones";
        case 4: return "Fax Machines";
        default: return "";
        }
    }

    static String FamilyOwnership(int i)
    {
        switch (i)
        {
        case 0: return "PERSONAL";
        case 1: return "PERSONAL";
        case 2: return "PERSONAL";
        case 3: return "PERSONAL";
        case 4: return "LOCATION";
        default: return "";
        }
    }

    static String FamilyStorageKind(int i)
    {
        switch (i)
        {
        case 0: return "HDD";
        case 1: return "HDD";
        case 2: return "SC";
        case 3: return "NONE";
        case 4: return "NONE";
        default: return "";
        }
    }

    static String FamilyConnectionKind(int i)
    {
        switch (i)
        {
        case 0: return "NETWORK";
        case 1: return "NETWORK";
        case 2: return "NETWORK";
        case 3: return "PHONE_LINE";
        case 4: return "PHONE_LINE";
        default: return "";
        }
    }

    static int FamilyPerTaskLimit(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        case 2: return 2;
        case 3: return 2;
        case 4: return -1;
        default: return -2;
        }
    }

    static int FindFamily(String id)
    {
        for (int i = 0; i < FAMILY_COUNT; i++)
        {
            if (FamilyId(i) == id) return i;
        }
        return -1;
    }

    // Equipment models
    static String ModelId(int i)
    {
        switch (i)
        {
        case 0: return "PHONE_ROTARY";
        case 1: return "PHONE_TOUCH_TONE";
        case 2: return "PHONE_CORDLESS_SYSTEM";
        case 3: return "PHONE_MULTI_LINE_SYSTEM";
        case 4: return "PHONE_MOBILE";
        case 5: return "FAX_MACHINE";
        case 6: return "PDA_CELLULAR";
        default: return "";
        }
    }

    static String ModelDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Rotary Phone";
        case 1: return "Touch Tone Phone";
        case 2: return "Cordless Phone System";
        case 3: return "Multi-Line Phone System";
        case 4: return "Mobile Phone";
        case 5: return "Fax Machine";
        case 6: return "Cellular Device";
        default: return "";
        }
    }

    static String ModelFamilyId(int i)
    {
        switch (i)
        {
        case 0: return "PHONE";
        case 1: return "PHONE";
        case 2: return "PHONE";
        case 3: return "PHONE";
        case 4: return "PHONE";
        case 5: return "FAX";
        case 6: return "PDA";
        default: return "";
        }
    }

    static String ModelPhoneLineKind(int i)
    {
        switch (i)
        {
        case 0: return "LANDLINE";
        case 1: return "LANDLINE";
        case 2: return "LANDLINE";
        case 3: return "LANDLINE";
        case 4: return "MOBILE";
        case 5: return "";
        case 6: return "";
        default: return "";
        }
    }

    static String ModelNetworkTierId(int i)
    {
        switch (i)
        {
        case 0: return "";
        case 1: return "";
        case 2: return "";
        case 3: return "";
        case 4: return "";
        case 5: return "";
        case 6: return "";
        default: return "";
        }
    }

    static String ModelConnectionOverride(int i)
    {
        switch (i)
        {
        case 0: return "";
        case 1: return "";
        case 2: return "";
        case 3: return "";
        case 4: return "";
        case 5: return "";
        case 6: return "MOBILE_INTERNET";
        default: return "";
        }
    }

    static int ModelGeneration(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 2;
        case 2: return 3;
        case 3: return 4;
        case 4: return 1;
        case 5: return 1;
        case 6: return 1;
        default: return -2;
        }
    }

    static int FindModel(String id)
    {
        for (int i = 0; i < MODEL_COUNT; i++)
        {
            if (ModelId(i) == id) return i;
        }
        return -1;
    }

    // Authored facilities/capabilities. Initial tiers are NOT campaign status.
    static String FacilityId(int i)
    {
        switch (i)
        {
        case 0: return "EVIDENCE_LAB";
        case 1: return "FIELD_OPERATIONS_ROOM";
        case 2: return "INTELLIGENCE_CELL";
        case 3: return "OVERSIGHT_WING";
        case 4: return "PUBLIC_LIAISON_OFFICE";
        case 5: return "TECHOPS_HUB";
        default: return "";
        }
    }

    static String FacilityDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Evidence Laboratory";
        case 1: return "Field Operations Room";
        case 2: return "Intelligence Cell";
        case 3: return "Oversight Wing";
        case 4: return "Public Liaison Office";
        case 5: return "Technical Operations Hub";
        default: return "";
        }
    }

    static String FacilityDescription(int i)
    {
        switch (i)
        {
        case 0: return "Processes physical and digital evidence through documented custody procedures";
        case 1: return "Coordinates deployments readiness and field support";
        case 2: return "Links case records field reports signals and leads";
        case 3: return "Reviews conduct risk patterns compromise and accountability failures";
        case 4: return "Coordinates witness care disclosure and public-facing institutional work";
        case 5: return "Maintains secure information systems specialized tools and FOIMS-X infrastructure";
        default: return "";
        }
    }

    static String FacilityTrackId(int i)
    {
        switch (i)
        {
        case 0: return "EVIDENCE_HANDLING";
        case 1: return "FIELD_OPERATIONS";
        case 2: return "INTELLIGENCE";
        case 3: return "INTERNAL_AFFAIRS";
        case 4: return "PUBLIC_COMMUNICATION";
        case 5: return "TECHNICAL_INFRASTRUCTURE";
        default: return "";
        }
    }

    static String FacilityZoneId(int i)
    {
        switch (i)
        {
        case 0: return "HQ_LAB";
        case 1: return "HQ_OPERATIONS";
        case 2: return "HQ_ANALYSIS";
        case 3: return "HQ_OVERSIGHT";
        case 4: return "HQ_LIAISON";
        case 5: return "HQ_TECHOPS";
        default: return "";
        }
    }

    static String FacilityInitialTier(int i)
    {
        switch (i)
        {
        case 0: return "UNBUILT";
        case 1: return "OPERATIONAL";
        case 2: return "UNBUILT";
        case 3: return "UNBUILT";
        case 4: return "UNBUILT";
        case 5: return "OPERATIONAL";
        default: return "";
        }
    }

    static String FacilityTrackName(int i)
    {
        switch (i)
        {
        case 0: return "Evidence Handling";
        case 1: return "Field Operations";
        case 2: return "Intelligence and Analysis";
        case 3: return "Internal Affairs and Ethics";
        case 4: return "Public Communication and Liaison";
        case 5: return "Technical Infrastructure";
        default: return "";
        }
    }

    static int FacilityCapacity(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        case 2: return 2;
        case 3: return 2;
        case 4: return 2;
        case 5: return 3;
        default: return -2;
        }
    }

    static int FindFacility(String id)
    {
        for (int i = 0; i < FACILITY_COUNT; i++)
        {
            if (FacilityId(i) == id) return i;
        }
        return -1;
    }

    static String CapabilityId(int i)
    {
        switch (i)
        {
        case 0: return "ELECTRONIC_SURVEILLANCE";
        case 1: return "OCCULT_RESPONSE";
        default: return "";
        }
    }

    static String CapabilityDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Electronic Surveillance";
        case 1: return "Occult Response";
        default: return "";
        }
    }

    static String CapabilityDescription(int i)
    {
        switch (i)
        {
        case 0: return "Authorized collection and analysis of electronic signals.";
        case 1: return "Specialized investigation and containment of anomalous threats.";
        default: return "";
        }
    }

    static String CapabilityStandingLabel(int i)
    {
        switch (i)
        {
        case 0: return "Signal Monitoring";
        case 1: return "Response Readiness";
        default: return "";
        }
    }

    static int FindCapability(String id)
    {
        for (int i = 0; i < CAPABILITY_COUNT; i++)
        {
            if (CapabilityId(i) == id) return i;
        }
        return -1;
    }

    static String FacilityCapabilityFacilityId(int i)
    {
        switch (i)
        {
        case 0: return "FIELD_OPERATIONS_ROOM";
        case 1: return "TECHOPS_HUB";
        default: return "";
        }
    }

    static String FacilityCapabilityCapabilityId(int i)
    {
        switch (i)
        {
        case 0: return "OCCULT_RESPONSE";
        case 1: return "ELECTRONIC_SURVEILLANCE";
        default: return "";
        }
    }

    static String FacilityCapabilityInitialTier(int i)
    {
        switch (i)
        {
        case 0: return "UNBUILT";
        case 1: return "UNBUILT";
        default: return "";
        }
    }

    static String FacilityCapabilityDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Occult Task Force";
        case 1: return "Electronic Surveillance";
        default: return "";
        }
    }

    static int FacilityCapabilityCapacity(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        default: return -2;
        }
    }

    // Resolved authored staffing only. No personnel assignment or readiness.
    static String StaffingDefaultCapabilityId(int i)
    {
        switch (i)
        {
        case 0: return "ELECTRONIC_SURVEILLANCE";
        case 1: return "ELECTRONIC_SURVEILLANCE";
        case 2: return "OCCULT_RESPONSE";
        case 3: return "OCCULT_RESPONSE";
        default: return "";
        }
    }

    static String StaffingDefaultQualificationId(int i)
    {
        switch (i)
        {
        case 0: return "SIGNALS_ANALYSIS";
        case 1: return "DATA_SYSTEMS";
        case 2: return "FIELD_RESPONSE";
        case 3: return "OCCULT_RESPONSE";
        default: return "";
        }
    }

    static String StaffingDefaultQualificationName(int i)
    {
        switch (i)
        {
        case 0: return "Signals Analysis";
        case 1: return "Data Systems";
        case 2: return "Field Response";
        case 3: return "Occult Response";
        default: return "";
        }
    }

    static int StaffingDefaultMin(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 0;
        case 2: return 1;
        case 3: return 0;
        default: return -2;
        }
    }

    static int StaffingDefaultPreferred(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 1;
        case 2: return 2;
        case 3: return 1;
        default: return -2;
        }
    }

    static int StaffingDefaultMax(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 1;
        case 2: return 2;
        case 3: return 2;
        default: return -2;
        }
    }

    static String FacilityStaffingCapabilityId(int i)
    {
        switch (i)
        {
        case 0: return "OCCULT_RESPONSE";
        case 1: return "OCCULT_RESPONSE";
        case 2: return "ELECTRONIC_SURVEILLANCE";
        case 3: return "ELECTRONIC_SURVEILLANCE";
        default: return "";
        }
    }

    static String FacilityStaffingQualificationId(int i)
    {
        switch (i)
        {
        case 0: return "FIELD_RESPONSE";
        case 1: return "OCCULT_RESPONSE";
        case 2: return "SIGNALS_ANALYSIS";
        case 3: return "DATA_SYSTEMS";
        default: return "";
        }
    }

    static String FacilityStaffingFacilityId(int i)
    {
        switch (i)
        {
        case 0: return "FIELD_OPERATIONS_ROOM";
        case 1: return "FIELD_OPERATIONS_ROOM";
        case 2: return "TECHOPS_HUB";
        case 3: return "TECHOPS_HUB";
        default: return "";
        }
    }

    static String FacilityStaffingSource(int i)
    {
        switch (i)
        {
        case 0: return "INHERITED";
        case 1: return "OVERRIDE";
        case 2: return "OVERRIDE";
        case 3: return "OVERRIDE";
        default: return "";
        }
    }

    static String FacilityStaffingCapabilityName(int i)
    {
        switch (i)
        {
        case 0: return "Occult Task Force";
        case 1: return "Occult Task Force";
        case 2: return "Electronic Surveillance";
        case 3: return "Electronic Surveillance";
        default: return "";
        }
    }

    static String FacilityStaffingQualificationName(int i)
    {
        switch (i)
        {
        case 0: return "Field Response";
        case 1: return "Occult Response";
        case 2: return "Signals Analysis";
        case 3: return "Data Systems";
        default: return "";
        }
    }

    static int FacilityStaffingMin(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 1;
        case 2: return 1;
        case 3: return 0;
        default: return -2;
        }
    }

    static int FacilityStaffingGlobalMin(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 0;
        case 2: return 1;
        case 3: return 0;
        default: return -2;
        }
    }

    static int FacilityStaffingPreferred(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        case 2: return 2;
        case 3: return 1;
        default: return -2;
        }
    }

    static int FacilityStaffingGlobalPreferred(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 1;
        case 2: return 2;
        case 3: return 1;
        default: return -2;
        }
    }

    static int FacilityStaffingMax(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        case 2: return 2;
        case 3: return 1;
        default: return -2;
        }
    }

    static int FacilityStaffingGlobalMax(int i)
    {
        switch (i)
        {
        case 0: return 2;
        case 1: return 2;
        case 2: return 2;
        case 3: return 1;
        default: return -2;
        }
    }

    // Authored task templates only; no task creation, allocation, or scheduling.
    static String TaskTemplateId(int i)
    {
        switch (i)
        {
        case 0: return "SIGNAL_REVIEW";
        case 1: return "OCCULT_INCIDENT_RESPONSE";
        default: return "";
        }
    }

    static String TaskTemplateDisplayName(int i)
    {
        switch (i)
        {
        case 0: return "Priority Signal Review";
        case 1: return "Occult Incident Response";
        default: return "";
        }
    }

    static String TaskTemplateDescription(int i)
    {
        switch (i)
        {
        case 0: return "Analyze and classify urgent signal interference.";
        case 1: return "Coordinate specialized response to an anomalous field incident.";
        default: return "";
        }
    }

    static String TaskTemplateCapabilityId(int i)
    {
        switch (i)
        {
        case 0: return "ELECTRONIC_SURVEILLANCE";
        case 1: return "OCCULT_RESPONSE";
        default: return "";
        }
    }

    static String TaskTemplatePriority(int i)
    {
        switch (i)
        {
        case 0: return "HIGH";
        case 1: return "CRITICAL";
        default: return "";
        }
    }

    static int TaskTemplateTargetEffortMinutes(int i)
    {
        switch (i)
        {
        case 0: return 240;
        case 1: return 360;
        default: return -2;
        }
    }

    static int TaskTemplateDeadlineMinutes(int i)
    {
        switch (i)
        {
        case 0: return 120;
        case 1: return 180;
        default: return -2;
        }
    }

    static int TaskTemplateAutoAllocate(int i)
    {
        switch (i)
        {
        case 0: return 1;
        case 1: return 1;
        default: return -2;
        }
    }

    static int FindTaskTemplate(String id)
    {
        for (int i = 0; i < TASK_TEMPLATE_COUNT; i++)
        {
            if (TaskTemplateId(i) == id) return i;
        }
        return -1;
    }

}

// Console: netevent DoDA_CatalogDump
class DoDAWorkbenchCatalogProbe : EventHandler
{
    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name != "DoDA_CatalogDump") return;
        Console.PrintF("DODA_CATALOG BEGIN gen=%s net=%s eq=%s dept=%s", DoDAWorkbenchCatalog.GeneratorVersion(), DoDAWorkbenchCatalog.NetworkSourceHash(), DoDAWorkbenchCatalog.EquipmentSourceHash(), DoDAWorkbenchCatalog.DepartmentSourceHash());
        Console.PrintF("DODA_CATALOG COUNTS tiers=%d hardware=%d families=%d models=%d limit=%d", DoDAWorkbenchCatalog.TIER_COUNT, DoDAWorkbenchCatalog.HARDWARE_COUNT, DoDAWorkbenchCatalog.FAMILY_COUNT, DoDAWorkbenchCatalog.MODEL_COUNT, DoDAWorkbenchCatalog.TOTAL_PERSONAL_DEVICE_LIMIT);
        for (int t = 0; t < DoDAWorkbenchCatalog.TIER_COUNT; t++)
            Console.PrintF("DODA_CATALOG TIER %s", DoDAWorkbenchCatalog.TierId(t));
        for (int h = 0; h < DoDAWorkbenchCatalog.HARDWARE_COUNT; h++)
            Console.PrintF("DODA_CATALOG HW %s %s", DoDAWorkbenchCatalog.HardwareId(h), DoDAWorkbenchCatalog.HardwareTierId(h));
        for (int f = 0; f < DoDAWorkbenchCatalog.FAMILY_COUNT; f++)
            Console.PrintF("DODA_CATALOG FAMILY %s", DoDAWorkbenchCatalog.FamilyId(f));
        for (int m = 0; m < DoDAWorkbenchCatalog.MODEL_COUNT; m++)
            Console.PrintF("DODA_CATALOG MODEL %s %s", DoDAWorkbenchCatalog.ModelId(m), DoDAWorkbenchCatalog.ModelFamilyId(m));
        Console.PrintF("DODA_CATALOG DEPARTMENT facilities=%d capabilities=%d links=%d", DoDAWorkbenchCatalog.FACILITY_COUNT, DoDAWorkbenchCatalog.CAPABILITY_COUNT, DoDAWorkbenchCatalog.FACILITY_CAPABILITY_COUNT);
        for (int fi = 0; fi < DoDAWorkbenchCatalog.FACILITY_COUNT; fi++)
            Console.PrintF("DODA_CATALOG FACILITY %s", DoDAWorkbenchCatalog.FacilityId(fi));
        for (int ca = 0; ca < DoDAWorkbenchCatalog.CAPABILITY_COUNT; ca++)
            Console.PrintF("DODA_CATALOG CAPABILITY %s", DoDAWorkbenchCatalog.CapabilityId(ca));
        for (int li = 0; li < DoDAWorkbenchCatalog.FACILITY_CAPABILITY_COUNT; li++)
            Console.PrintF("DODA_CATALOG LINK %s %s", DoDAWorkbenchCatalog.FacilityCapabilityFacilityId(li), DoDAWorkbenchCatalog.FacilityCapabilityCapabilityId(li));
        Console.PrintF("DODA_CATALOG STAFFING defaults=%d effective=%d overrides=%d", DoDAWorkbenchCatalog.STAFFING_DEFAULT_COUNT, DoDAWorkbenchCatalog.FACILITY_STAFFING_COUNT, DoDAWorkbenchCatalog.STAFFING_OVERRIDE_COUNT);
        for (int sd = 0; sd < DoDAWorkbenchCatalog.STAFFING_DEFAULT_COUNT; sd++)
            Console.PrintF("DODA_CATALOG STAFFING_DEFAULT %s %s %d/%d/%d", DoDAWorkbenchCatalog.StaffingDefaultCapabilityId(sd), DoDAWorkbenchCatalog.StaffingDefaultQualificationId(sd), DoDAWorkbenchCatalog.StaffingDefaultMin(sd), DoDAWorkbenchCatalog.StaffingDefaultPreferred(sd), DoDAWorkbenchCatalog.StaffingDefaultMax(sd));
        for (int se = 0; se < DoDAWorkbenchCatalog.FACILITY_STAFFING_COUNT; se++)
            Console.PrintF("DODA_CATALOG STAFFING_EFFECTIVE %s %s %s global=%d/%d/%d effective=%d/%d/%d source=%s", DoDAWorkbenchCatalog.FacilityStaffingFacilityId(se), DoDAWorkbenchCatalog.FacilityStaffingCapabilityId(se), DoDAWorkbenchCatalog.FacilityStaffingQualificationId(se), DoDAWorkbenchCatalog.FacilityStaffingGlobalMin(se), DoDAWorkbenchCatalog.FacilityStaffingGlobalPreferred(se), DoDAWorkbenchCatalog.FacilityStaffingGlobalMax(se), DoDAWorkbenchCatalog.FacilityStaffingMin(se), DoDAWorkbenchCatalog.FacilityStaffingPreferred(se), DoDAWorkbenchCatalog.FacilityStaffingMax(se), DoDAWorkbenchCatalog.FacilityStaffingSource(se));
        Console.PrintF("DODA_CATALOG TASK_TEMPLATES count=%d", DoDAWorkbenchCatalog.TASK_TEMPLATE_COUNT);
        for (int tt = 0; tt < DoDAWorkbenchCatalog.TASK_TEMPLATE_COUNT; tt++)
            Console.PrintF("DODA_CATALOG TASK_TEMPLATE %s %s priority=%s effort=%d deadline=%d auto=%d", DoDAWorkbenchCatalog.TaskTemplateId(tt), DoDAWorkbenchCatalog.TaskTemplateCapabilityId(tt), DoDAWorkbenchCatalog.TaskTemplatePriority(tt), DoDAWorkbenchCatalog.TaskTemplateTargetEffortMinutes(tt), DoDAWorkbenchCatalog.TaskTemplateDeadlineMinutes(tt), DoDAWorkbenchCatalog.TaskTemplateAutoAllocate(tt));
        Console.PrintF("DODA_CATALOG END");
    }
}
