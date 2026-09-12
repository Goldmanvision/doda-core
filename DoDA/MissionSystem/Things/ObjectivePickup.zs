/*//////////////////////////|
// DoDA/MissionSystem/Things/ObjectivePickup.zs
*///////////////////////////|*/

class DoDAMissionObjectivePickup : DoDAMissionPickupBase
{
    Default
    {
        Scale 0.3;

        Inventory.Amount 1;
        Inventory.MaxAmount 1;
        Inventory.Icon "EVI1A0";
    }

    States
    {
    Pickup:
        TNT1 A 0 A_GiveInventory("DoDAObjectivePickupMarker", 1);
        Stop;
    }
}