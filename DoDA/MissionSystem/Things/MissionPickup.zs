/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionPickup.zs
*///////////////////////////|*/

class DoDAMissionPickup : CustomInventory
{
    Default
    {
        Radius 20;
        Height 16;
        Scale 0.1;

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
        TNT1 A 0 A_GiveInventory("DoDAMissionPickupMarker", 1);
        Stop;
    }
}