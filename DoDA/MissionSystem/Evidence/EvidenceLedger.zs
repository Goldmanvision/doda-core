class DoDAEvidenceLedger : Object
{
    int WeaponEvidencePoints;
    int AmmoEvidencePoints;
    int TotalEvidencePoints;

    void RecordResource(String category, int value)
    {
        if (category == "Weapon") WeaponEvidencePoints += value;
        else if (category == "Ammo") AmmoEvidencePoints += value;
    }
}
