
class DoDATracer : FastProjectile
{
    Default {
        Damage 0;
        Speed 60;
        Height 1;
        Radius 1;
        +NOCLIP;
        +NOINTERACTION;
        +BLOODLESSIMPACT;
        +NOBLOOD;
    }
    States {
        Spawn:
            TNT1 A 1;
            Loop;
        Death:
            TNT1 A 0;
            Stop;
    }
}
