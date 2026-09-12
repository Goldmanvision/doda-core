/*//////////////////////////|
// DoDA/MissionSystem/Things/EvidencePickup.zs
*///////////////////////////|*/

enum EdodaEvidenceTypes
{
    DODAInvalid = -1,
    DODAPaperFinancial,
    DODAPaperOccult,
    DODAPaperCorrupt,
    DODAPaperClue,
    DODAfloppyFinancial,
    DODAfloppyCorrupt,
    DODAfloppyOccult,
    DODAcdFinancial,
    DODAcdOccult,
    DODAfilmFinancial,
    DODAfilmOccult,
    DODAfilmCorrupt,
    DODAfilmAssault,
    DODAphotoFinancial,
    DODAphotoAssault,
    DODAphotoClue
};

class EvidencePickup : CustomInventory
{
    bool randomizeEvidence;
    int evidenceType;

    Default
    {
        Radius 20;
        Height 16;
        Scale 0.08;

        Inventory.Amount 1;
        Inventory.MaxAmount 20;
        Inventory.Icon "EVI1A0";

        +COUNTITEM;
        +INVENTORY.INVBAR;
    }

    States
    {
    Spawn:
        EVI1 A -1;
        Stop;

    Pickup:
        TNT1 A 0 A_GiveInventory("DoDAMissionPickupMarker", 1);
        Stop;
    }
}