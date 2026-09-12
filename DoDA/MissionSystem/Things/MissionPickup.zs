/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionPickup.zs
*///////////////////////////|*/

class DoDAMissionPickup : DoDAMissionPickupBase
{
    Default
    {
        Scale 0.1;

        Inventory.Amount 1;
        Inventory.MaxAmount 1;
        Inventory.Icon "EVI1A0";
    }

    States
    {
    Pickup:
        TNT1 A 0 A_GiveInventory("DoDAMissionPickupMarker", 1);
        Stop;
    }
}