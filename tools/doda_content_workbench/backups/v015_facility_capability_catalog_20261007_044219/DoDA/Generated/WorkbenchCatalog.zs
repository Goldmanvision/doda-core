/*//////////////////////////|
// DoDA/Generated/WorkbenchCatalog.zs
*///////////////////////////|
// GENERATED FILE - DO NOT EDIT. Regenerate with
//   tools/doda_content_workbench/doda_zscript_catalog.py
// Generator 0.1.1; network content sha256 ca30bb147d2525c2d7ba9aeab9360fb3e53be65dd639812bee4f51ec8d0dfa36
// equipment content sha256 52bf81d446b00a3f0c808618224c12ed629738d5cd819ae0e6b5c800a9c39cab
// Read-only display/lookup catalog (Option B stopgap). No simulation rules.

class DoDAWorkbenchCatalog : Object
{
    const TIER_COUNT = 5;
    const HARDWARE_COUNT = 10;
    const FAMILY_COUNT = 5;
    const MODEL_COUNT = 7;
    const TOTAL_PERSONAL_DEVICE_LIMIT = 8;

    static String GeneratorVersion() { return "0.1.1"; }
    static String NetworkSourceHash() { return "ca30bb147d2525c2"; }
    static String EquipmentSourceHash() { return "52bf81d446b00a3f"; }

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

}

// Console: netevent DoDA_CatalogDump
class DoDAWorkbenchCatalogProbe : EventHandler
{
    override void NetworkProcess(ConsoleEvent e)
    {
        if (e.Name != "DoDA_CatalogDump") return;
        Console.PrintF("DODA_CATALOG BEGIN gen=%s net=%s eq=%s", DoDAWorkbenchCatalog.GeneratorVersion(), DoDAWorkbenchCatalog.NetworkSourceHash(), DoDAWorkbenchCatalog.EquipmentSourceHash());
        Console.PrintF("DODA_CATALOG COUNTS tiers=%d hardware=%d families=%d models=%d limit=%d", DoDAWorkbenchCatalog.TIER_COUNT, DoDAWorkbenchCatalog.HARDWARE_COUNT, DoDAWorkbenchCatalog.FAMILY_COUNT, DoDAWorkbenchCatalog.MODEL_COUNT, DoDAWorkbenchCatalog.TOTAL_PERSONAL_DEVICE_LIMIT);
        for (int t = 0; t < DoDAWorkbenchCatalog.TIER_COUNT; t++)
            Console.PrintF("DODA_CATALOG TIER %s", DoDAWorkbenchCatalog.TierId(t));
        for (int h = 0; h < DoDAWorkbenchCatalog.HARDWARE_COUNT; h++)
            Console.PrintF("DODA_CATALOG HW %s %s", DoDAWorkbenchCatalog.HardwareId(h), DoDAWorkbenchCatalog.HardwareTierId(h));
        for (int f = 0; f < DoDAWorkbenchCatalog.FAMILY_COUNT; f++)
            Console.PrintF("DODA_CATALOG FAMILY %s", DoDAWorkbenchCatalog.FamilyId(f));
        for (int m = 0; m < DoDAWorkbenchCatalog.MODEL_COUNT; m++)
            Console.PrintF("DODA_CATALOG MODEL %s %s", DoDAWorkbenchCatalog.ModelId(m), DoDAWorkbenchCatalog.ModelFamilyId(m));
        Console.PrintF("DODA_CATALOG END");
    }
}
