/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionPickupMarkers.zs
*///////////////////////////|*/

class DoDAObjectivePickupMarker : Inventory
{
    Default
    {
        Inventory.Amount 1;
        Inventory.MaxAmount 255;

        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNCLEARABLE;
    }
}

class DoDAMissionPickupMarker : Inventory
{
    Default
    {
        Inventory.Amount 1;
        Inventory.MaxAmount 255;

        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNCLEARABLE;
    }
}