/*//////////////////////////|
// DoDA/MissionSystem/Things/ObjectivePickup.zs
*///////////////////////////|*/

class DoDAMissionObjectivePickup : CustomInventory
{
    Default
    {
        Radius 20;
        Height 16;
        Scale 0.3;

        Inventory.Amount 1;
        Inventory.MaxAmount 1;
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
        TNT1 A 0 A_GiveInventory("DoDAObjectivePickupMarker", 1);
        Stop;
    }
}