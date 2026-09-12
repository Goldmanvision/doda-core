/*//////////////////////////|
// DoDA/MissionSystem/Things/MissionPickupBase.zs
*///////////////////////////|*/

class DoDAMissionPickupBase : CustomInventory
{
    Default
    {
        Radius 20;
        Height 16;

        +COUNTITEM;
        +INVENTORY.INVBAR;
    }

    States
    {
    Spawn:
        EVI1 A -1;
        Stop;
    }
}
