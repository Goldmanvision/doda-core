/*//////////////////////////|
// DoDA/World/Computers/DesktopActor.zs
*///////////////////////////|*/

class DoDADesktopActor : Actor
{
    bool Activated;

    Default
    {
        Radius 20;
        Height 20;

        +SOLID;
        +USESPECIAL;
    }

    override bool Used(Actor user)
    {
        if (user == null)
        {
            return false;
        }

        Activated = !Activated;

        if (Activated)
        {
            SetStateLabel("Ready");
        }
        else
        {
            SetStateLabel("ScreenSaver");
        }

        return true;
    }

    States
    {
    Spawn:
    ScreenSaver:
        DCSV A-] 4;
        DCSW A-I 4;
        Loop;

    Ready:
        DCSR A -1;
        Stop;
    }
}