/*//////////////////////////|
// DoDA/MissionSystem/DebugTrigger.zs
*///////////////////////////|

class DoDADebugTrigger : Actor
{
    Default
    {
        +NOBLOCKMAP;
        +NOSECTOR;
        +NOGRAVITY;
        +FLOAT;
        Radius 8;
        Height 8;
    }

    States
    {
    Spawn:
        TNT1 A 1;
        Stop;
    }
}