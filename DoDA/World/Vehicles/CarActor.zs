/*//////////////////////////|
// DoDA/World/Vehicles/CarActor.zs
*///////////////////////////|*/

class DoDACarActor : Actor
{
    bool Activated;

    Default
    {
        Radius 28;
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
            SetStateLabel("On");
        }
        else
        {
            SetStateLabel("Off");
        }

        return true;
    }

    States
    {
    Spawn:
    Off:
        DCAR A -1;
        Stop;

    On:
        DCAR B -1;
        Stop;
    }
}