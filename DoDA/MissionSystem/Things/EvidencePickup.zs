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
	DODAfilmFinancial
	DODAfilmOccult,
	DODAfilmCorrupt,
	DODAfilmAssault,
	DODAphotoFinancial,
	DODAphotoAssault,
	DODAphotoClue
}


class EvidencePickup : CustomInventory
{
    Default
    {
		bool randomizeEvidence = false;
		
        Radius 20;
        Height 16;
		Scale 0.08;

        +COUNTITEM;
        +INVENTORY.INVBAR;
    }

	if (evidenceType=DODApaperFinancial)
	{
		Inventory.Icon "EVI1A0";
		Inventory.Max = 20;
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