/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionPickupMarkers.zs
*///////////////////////////|*/

class DoDAMissionPickupMarkerBase : Inventory
{
    Default
    {
        Inventory.Amount 1;
        Inventory.MaxAmount 255;

        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNCLEARABLE;
    }
}

class DoDAObjectivePickupMarker : DoDAMissionPickupMarkerBase
{
}

class DoDAMissionPickupMarker : DoDAMissionPickupMarkerBase
{
}