///////////////////////////
// DoDA/WeaponSystem/HandSwapController.zs
///////////////////////////

class DoDAHandSwapController : Object
{
    const Hand_Left = 0;
    const Hand_Right = 1;

    int CurrentHand;
    int DesiredHand;

    bool ManualHandLock;
    int ManualLockedHand;
    bool pistolSwapLocked;

    bool Initialized;

    void Reset(int initialHand)
    {
        CurrentHand = initialHand;
        DesiredHand = initialHand;
        ManualHandLock = false;
        ManualLockedHand = initialHand;
        pistolSwapLocked = false;
        Initialized = true;
    }

    void SetCurrentHand(int hand)
    {
        if (!Initialized)
        {
            Reset(hand);
            return;
        }

        CurrentHand = hand;
    }

    int GetOppositeHand(int hand)
    {
        return hand == Hand_Left
            ? Hand_Right
            : Hand_Left;
    }

    void ClearManualHandLock()
    {
        ManualHandLock = false;
        ManualLockedHand = CurrentHand;
    }

    int ResolveDesiredHand(
        bool deadzoneActive,
        double yawGap,
        double yawLimit,
        bool leaningLeftPressed,
        bool leaningRightPressed,
        bool isLeaning,
        bool swapBerettaPressed,
        bool leanLock,
        int lockedHand
    )
    {
        if (!Initialized)
        {
            Reset(Hand_Right);
        }

        // Tactical lean lock has highest priority.
        if (leanLock && !swapBerettaPressed)
        {
            DesiredHand = lockedHand;
            ClearManualHandLock();
            return DesiredHand;
        }

        // V always toggles between B92s. When Deadzone Aim is active, the
        // choice is locked against reticle-side auto-selection until release.
        if (swapBerettaPressed)
        {
            DesiredHand = GetOppositeHand(CurrentHand);

            if (deadzoneActive)
            {
                ManualLockedHand = DesiredHand;
                ManualHandLock = true;
            }
            else
            {
                ClearManualHandLock();
            }

            return DesiredHand;
        }

        // Manual selection is scoped only to the current Deadzone Aim hold.
        if (!deadzoneActive)
        {
            ClearManualHandLock();
            DesiredHand = CurrentHand;
            return DesiredHand;
        }

        // Preserve the player's V-selected hand while Deadzone Aim is held.
        // Do not alter reticle position, yawGap, pitchGap, or aim math.
        if (ManualHandLock)
        {
            DesiredHand = ManualLockedHand;
            return DesiredHand;
        }

        // Directional thresholds deliberately leave a broad center hold band.
        // A weapon remains selected through that band instead of oscillating
        // whenever the reticle crosses the exact center of the deadzone.
        double switchToRightAt = -yawLimit * 0.30;
        double switchToLeftAt = yawLimit * 0.30;

        DesiredHand = CurrentHand;

        // Existing lean behavior is retained unchanged.
        if (leaningLeftPressed)
        {
            DesiredHand = Hand_Left;
            return DesiredHand;
        }

        if (leaningRightPressed)
        {
            DesiredHand = Hand_Right;
            return DesiredHand;
        }

        if (isLeaning)
        {
            return DesiredHand;
        }

        // Negative yawGap is screen-right under the current coordinate contract.
        if (yawGap <= switchToRightAt)
        {
            DesiredHand = Hand_Right;
        }
        else if (yawGap >= switchToLeftAt)
        {
            DesiredHand = Hand_Left;
        }

        return DesiredHand;
    }

    clearscope int GetCurrentHand()
    {
        return CurrentHand;
    }

    clearscope int GetDesiredHand()
    {
        return DesiredHand;
    }

    clearscope bool IsManualHandLocked()
    {
        return ManualHandLock;
    }

    clearscope int GetManualLockedHand()
    {
        return ManualLockedHand;
    }

    void TogglePistolSwapLock()
    {
        pistolSwapLocked = !pistolSwapLocked;
    }

    clearscope bool IsPistolSwapLocked()
    {
        return pistolSwapLocked;
    }

    clearscope bool NeedsWeaponSwap()
    {
        return DesiredHand != CurrentHand;
    }
}