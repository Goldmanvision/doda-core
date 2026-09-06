class DoDACasing : Actor
{
    int kickCooldown;
    bool resting;

    Default
    {
        Radius 2;
        Height 2;
        Gravity 0.5;
        BounceType "Doom";
        BounceFactor 0.35;
        Mass 2;
        +NOTELEPORT
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
    }

    override void Tick()
    {
        Super.Tick();

        if (kickCooldown > 0)
        {
            kickCooldown--;
        }

        if (Pos.Z <= FloorZ + 0.1)
        {
            BlockThingsIterator it = BlockThingsIterator.Create(self, 32);
            while (it.Next())
            {
                Actor other = it.thing;
                if (other == self || other.vel.length() == 0)
                {
                    continue;
                }

                if (Distance3D(other) < 32 && other.vel.xy.length() > 0.2)
                {
                    if (kickCooldown == 0)
                    {
                        double transferFactor = 0.85;
                        Vector2 pusherVel = other.vel.xy;
                        Vector2 targetVel = pusherVel * transferFactor;

                        // Add lateral variation (approx 5-10 degrees)
                        double angle = VectorAngle(targetVel.x, targetVel.y) + FRandom(-7.5, 7.5);
                        double speed = targetVel.length();
                        Vector2 finalVel = (Cos(angle) * speed, Sin(angle) * speed);

                        // If same direction, take stronger; if opposite, replace.
                        if (Vel.XY.X * pusherVel.X + Vel.XY.Y * pusherVel.Y > 0)
                        {
                            if (Vel.XY.length() < finalVel.length())
                            {
                                Vel.XY = finalVel;
                            }
                        }
                        else
                        {
                            Vel.XY = finalVel;
                        }

                        // Upward impulse
                        Vel.Z = Max(Vel.Z, 1.0);

                        kickCooldown = 8;
                        resting = false;
                        SetState(ResolveState("Spawn"));
                    }
                }
            }
        }

        if (
            !resting
            && Vel.Length() < 0.1
            && Pos.Z <= FloorZ + 0.1
        )
        {
            resting = true;
            SetState(ResolveState("Rest"));
        }
    }

    States
    {
    Spawn:
        "####" A 1;
        Loop;

    Rest:
        "####" A -1;
        Stop;
    }
}

class DoDAPistolCasing : DoDACasing
{
    Default
    {
        Tag "Pistol Casing";
        Scale 0.25;
    }

    States
    {
    Spawn:
        C4S1 A 1;
        C4S1 B 1;
        C4S1 C 1;
        C4S1 D 1;
        C4S1 E 1;
        C4S1 F 1;
        C4S1 G 1;
        C4S1 H 1;
        Loop;

    Rest:
        C4S1 M -1;
        Stop;
    }
}

class DoDAShotgunCasing : DoDACasing
{
    Default
    {
        Tag "Shotgun Casing";
        Scale 0.25;
        Radius 0.75;
        Height 0.75;
    }

    States
    {
    Spawn:
        C4S2 A 1;
        C4S2 B 1;
        C4S2 C 1;
        C4S2 D 1;
        C4S2 E 1;
        C4S2 F 1;
        C4S2 G 1;
        C4S2 H 1;
        Loop;

    Rest:
        C4S2 I 2;
        C4S2 J 2;
        C4S2 K 2;
        C4S2 L 2;
        C4S2 M 2;
        C4S2 N 2;
        Loop;
    }
}