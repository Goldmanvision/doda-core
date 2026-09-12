/*//////////////////////////|
// DoDA/MissionSystem/Evidence/EvidenceLedger.zs
*///////////////////////////|

class DoDAEvidenceLedger : Object
{
    int WeaponEvidencePoints;
    int AmmoEvidencePoints;
    int TotalEvidencePoints;

    bool RecordResource(String category, int value)
    {
        if (value <= 0)
        {
            Console.Printf(
                "DoDA EvidenceLedger rejected: Invalid value %d for Category=%s (must be positive).",
                value,
                category
            );
            return false;
        }

        if (category == "Weapon")
        {
            WeaponEvidencePoints += value;
            TotalEvidencePoints += value;

            Console.Printf(
                "DoDA EvidenceLedger recorded: Category=Weapon Value=%d WeaponTotal=%d AmmoTotal=%d GrandTotal=%d",
                value,
                WeaponEvidencePoints,
                AmmoEvidencePoints,
                TotalEvidencePoints
            );
            return true;
        }
        else if (category == "Ammo")
        {
            AmmoEvidencePoints += value;
            TotalEvidencePoints += value;

            Console.Printf(
                "DoDA EvidenceLedger recorded: Category=Ammo Value=%d WeaponTotal=%d AmmoTotal=%d GrandTotal=%d",
                value,
                WeaponEvidencePoints,
                AmmoEvidencePoints,
                TotalEvidencePoints
            );
            return true;
        }
        else
        {
            Console.Printf(
                "DoDA EvidenceLedger rejected: Unsupported category '%s' with Value=%d.",
                category,
                value
            );
            return false;
        }
    }

    void Reset()
    {
        WeaponEvidencePoints = 0;
        AmmoEvidencePoints = 0;
        TotalEvidencePoints = 0;

        Console.Printf("DoDA EvidenceLedger reset: WeaponTotal=0 AmmoTotal=0 GrandTotal=0");
    }

    clearscope int GetTotalEvidencePoints()
    {
        return TotalEvidencePoints;
    }

    clearscope int GetWeaponEvidencePoints()
    {
        return WeaponEvidencePoints;
    }

    clearscope int GetAmmoEvidencePoints()
    {
        return AmmoEvidencePoints;
    }
}
