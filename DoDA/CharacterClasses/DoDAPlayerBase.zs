///////////////////////////
// DoDA/CharacterClasses/DoDAPlayerBase.zs
///////////////////////////

class DoDAPlayerBase : DoomPlayer
{
    bool DeadzoneAimActive;
    DoDAHandState HandState;

    // Sole authority for the signed angular gap between actor aim and red-dot aim.
    double ReticleYawOffset;
    double ReticlePitchOffset;

    double DeadzoneYawLimit;
    double DeadzonePitchLimit;

    // Smoothed per-tick deadzone input, used for light trackball inertia.
    double SmoothedMouseX;
    double SmoothedMouseY;

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();

        DeadzoneYawLimit = 12.0;
        DeadzonePitchLimit = 8.0;

        if (HandState == null)
        {
            HandState = new("DoDAHandState");
            HandState.Init(self);
        }
    }

    DoDAHandState GetHandState()
    {
        if (HandState == null)
        {
            HandState = new("DoDAHandState");
            HandState.Init(self);
        }
        return HandState;
    }

    override void Die(Actor source, Actor inflictor, int dmgflags, Name MeansOfDeath)
    {
        ResetDeadzoneAim();
        if (HandState != null && player != null)
        {
            HandState.ClearLayer2(player);
        }
        Super.Die(source, inflictor, dmgflags, MeansOfDeath);
    }

    void ResetDeadzoneAim()
    {
        DeadzoneAimActive = false;
        ReticleYawOffset = 0.0;
        ReticlePitchOffset = 0.0;
        SmoothedMouseX = 0.0;
        SmoothedMouseY = 0.0;

        if (player == null)
        {
            return;
        }

        DoDAInputUtility.SafeWriteFloat(player, 'doda_raw_mouse_x', 0.0);
        DoDAInputUtility.SafeWriteFloat(player, 'doda_raw_mouse_y', 0.0);
    }

    virtual bool ShouldActivateDeadzoneAim()
    {
        if (player == null)
        {
            return false;
        }

        bool realAltFire = (player.cmd.buttons & BT_ALTATTACK) != 0;
        bool forceDeadzone = DoDAInputUtility.ReadBoolSetting(player, 'doda_debug_force_deadzone', false);

        return realAltFire || forceDeadzone;
    }

    override void Tick()
    {
        Super.Tick();

        if (player == null)
        {
            return;
        }

        if (HandState != null)
        {
            HandState.ValidateLayer2(player);
        }

        if (health <= 0)
        {
            ResetDeadzoneAim();
            if (HandState != null)
            {
                HandState.ClearLayer2(player);
            }
            return;
        }

        bool deadzoneActive = ShouldActivateDeadzoneAim();
        bool justActivated = deadzoneActive && !DeadzoneAimActive;

        DeadzoneAimActive = deadzoneActive;

        if (!deadzoneActive)
        {
            ResetDeadzoneAim();
            return;
        }

        if (justActivated)
        {
            ReticleYawOffset = 0.0;
            ReticlePitchOffset = 0.0;
            SmoothedMouseX = 0.0;
            SmoothedMouseY = 0.0;
        }

        double rawMouseX = DoDAInputUtility.ConsumeFloatBuffer(player, 'doda_raw_mouse_x', 0.0);
        double rawMouseY = DoDAInputUtility.ConsumeFloatBuffer(player, 'doda_raw_mouse_y', 0.0);

        // Lower default sensitivity for slower, more deliberate reticle motion.
        double sensitivity = DoDAInputUtility.ReadFloatSetting(player, 'doda_aim_sensitivity', 0.12);

        double trackballResponse = 0.30;

        // Smooth input toward the latest mouse impulse. This adds modest,
        // controllable inertia while naturally decaying to zero after motion.
        SmoothedMouseX += (
            rawMouseX - SmoothedMouseX
        ) * trackballResponse;

        SmoothedMouseY += (
            rawMouseY - SmoothedMouseY
        ) * trackballResponse;

        // Signed coordinate contract:
        // Mouse right -> negative yaw -> dot right.
        // Mouse down  -> negative pitch -> dot up.
        double deltaYaw = -SmoothedMouseX * sensitivity;
        double deltaPitch = -SmoothedMouseY * sensitivity;

        double requestedYaw = ReticleYawOffset + deltaYaw;
        double requestedPitch = ReticlePitchOffset + deltaPitch;

        double overflowYaw = 0.0;
        double overflowPitch = 0.0;

        if (requestedYaw > DeadzoneYawLimit)
        {
            overflowYaw = requestedYaw - DeadzoneYawLimit;
            requestedYaw = DeadzoneYawLimit;
        }
        else if (requestedYaw < -DeadzoneYawLimit)
        {
            overflowYaw = requestedYaw + DeadzoneYawLimit;
            requestedYaw = -DeadzoneYawLimit;
        }

        if (requestedPitch > DeadzonePitchLimit)
        {
            overflowPitch = requestedPitch - DeadzonePitchLimit;
            requestedPitch = DeadzonePitchLimit;
        }
        else if (requestedPitch < -DeadzonePitchLimit)
        {
            overflowPitch = requestedPitch + DeadzonePitchLimit;
            requestedPitch = -DeadzonePitchLimit;
        }

        ReticleYawOffset = requestedYaw;
        ReticlePitchOffset = requestedPitch;

        // Transfer only input beyond the deadzone limits to camera rotation.
        if (overflowYaw != 0.0)
        {
            angle += overflowYaw;
        }

        if (overflowPitch != 0.0)
        {
            pitch = Clamp(pitch + overflowPitch, -89.0, 89.0);
        }
    }

    clearscope bool IsDeadzoneAimActive()
    {
        return DeadzoneAimActive;
    }

    clearscope double GetDeadzoneYawGap()
    {
        return ReticleYawOffset;
    }

    clearscope double GetDeadzonePitchGap()
    {
        return ReticlePitchOffset;
    }

    clearscope double GetDeadzoneYawLimit()
    {
        return DeadzoneYawLimit;
    }

    clearscope double GetDeadzonePitchLimit()
    {
        return DeadzonePitchLimit;
    }
}
