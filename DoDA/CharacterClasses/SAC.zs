///////////////////////////
// DoDA/CharacterClasses/Analyst.zs
///////////////////////////

class SAC : DoomPlayer
{
    bool DeadzoneAimActive;

    // Sole authority for the signed angular gap between actor aim and red-dot aim.
    double ReticleYawOffset;
    double ReticlePitchOffset;

    double DeadzoneYawLimit;
    double DeadzonePitchLimit;

    // Smoothed per-tick deadzone input, used for light trackball inertia.
    double SmoothedMouseX;
    double SmoothedMouseY;

    Default
    {
        Player.DisplayName "SAC";
        Player.StartItem "DoDAB92Left";
        Player.StartItem "DoDAB92Right";
        Player.StartItem "Clip", 100;
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();

        DeadzoneYawLimit = 12.0;
        DeadzonePitchLimit = 8.0;
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

        CVar mouseXCVar = CVar.GetCVar('doda_raw_mouse_x', player);
        CVar mouseYCVar = CVar.GetCVar('doda_raw_mouse_y', player);

        if (mouseXCVar)
        {
            mouseXCVar.SetFloat(0.0);
        }

        if (mouseYCVar)
        {
            mouseYCVar.SetFloat(0.0);
        }
    }

    override void Tick()
    {
        Super.Tick();

        if (player == null)
        {
            return;
        }

        if (health <= 0)
        {
            ResetDeadzoneAim();
            return;
        }

        bool realAltFire = (player.cmd.buttons & BT_ALTATTACK) != 0;

        CVar debugForceCVar = CVar.GetCVar(
            'doda_debug_force_deadzone',
            player
        );

        bool forceDeadzone = debugForceCVar
            ? debugForceCVar.GetBool()
            : false;

        bool deadzoneActive = realAltFire || forceDeadzone;
        bool justActivated = deadzoneActive && !DeadzoneAimActive;

        DeadzoneAimActive = deadzoneActive;

        CVar mouseXCVar = CVar.GetCVar('doda_raw_mouse_x', player);
        CVar mouseYCVar = CVar.GetCVar('doda_raw_mouse_y', player);

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

        double rawMouseX = mouseXCVar
            ? mouseXCVar.GetFloat()
            : 0.0;

        double rawMouseY = mouseYCVar
            ? mouseYCVar.GetFloat()
            : 0.0;

        if (mouseXCVar)
        {
            mouseXCVar.SetFloat(0.0);
        }

        if (mouseYCVar)
        {
            mouseYCVar.SetFloat(0.0);
        }

        CVar sensitivityCVar = CVar.GetCVar(
            'doda_aim_sensitivity',
            player
        );

        // Lower default sensitivity for slower, more deliberate reticle motion.
        double sensitivity = sensitivityCVar
            ? sensitivityCVar.GetFloat()
            : 0.12;

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