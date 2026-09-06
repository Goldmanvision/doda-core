/*//////////////////////////|
// DoDA/MissionSystem/MissionTransferProbe.zs
*///////////////////////////|

class DoDAMissionTransferProbe : Inventory
{
    int StoredMissionResult;
    string LastReportedMap;

    Default
    {
        Inventory.Amount 1;
        Inventory.MaxAmount 1;

        +INVENTORY.UNDROPPABLE;
        +INVENTORY.UNCLEARABLE;
    }

    override void Tick()
    {
        Super.Tick();

        if (Owner == null)
        {
            return;
        }

        if (LastReportedMap == level.MapName)
        {
            return;
        }

        LastReportedMap = level.MapName;

        Console.Printf(
            "DoDA TransferProbe observed: Map=%s Value=%d OwnerClass=%s",
            level.MapName,
            StoredMissionResult,
            Owner.GetClassName()
        );
    }

    void StoreMissionResult(DoDAMissionResult result)
    {
        StoredMissionResult = result;

        Console.Printf(
            "DoDA TransferProbe stored: Map=%s Value=%d",
            level.MapName,
            StoredMissionResult
        );
    }
}