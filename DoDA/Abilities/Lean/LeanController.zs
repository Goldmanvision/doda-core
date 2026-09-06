///////////////////////////
// DoDA/Abilities/Lean/LeanController.zs
///////////////////////////

class DoDALeanController : Object
{
    double LeanAmount;
    double LeanDistance;
    double AppliedOffset;

    bool WasScrollUp;
    bool WasScrollDown;

    bool LeanLock;
    int LockedHand;

    void Reset()
    {
        LeanAmount = 0.0;
        LeanDistance = 20.0;
        AppliedOffset = 0.0;
        LeanLock = false;
        LockedHand = -1;

        WasScrollUp = false;
        WasScrollDown = false;
    }

    play void Update(
        PlayerPawn owner,
        bool leaningLeft,
        bool leaningRight,
        bool scrollUp,
        bool scrollDown
    )
    {
        if (owner == null)
        {
            return;
        }

        if (LeanDistance <= 0.0)
        {
            LeanDistance = 20.0;
        }

        double leanSmoothing = 0.25;
        double scrollStep = 2.0;
        double minLeanDistance = 8.0;
        double maxLeanDistance = 40.0;

        // Q+E simultaneously = no lean.
        bool isLeaning = (leaningLeft || leaningRight) && !(leaningLeft && leaningRight);

        if (isLeaning)
        {
            if (scrollUp && !WasScrollUp)
            {
                LeanDistance = Clamp(
                    LeanDistance + scrollStep,
                    minLeanDistance,
                    maxLeanDistance
                );
            }

            if (scrollDown && !WasScrollDown)
            {
                LeanDistance = Clamp(
                    LeanDistance - scrollStep,
                    minLeanDistance,
                    maxLeanDistance
                );
            }
        }

        WasScrollUp = scrollUp;
        WasScrollDown = scrollDown;

        double targetLean = 0.0;

        bool wasLeanLocked = LeanLock;

        if (leaningLeft && !leaningRight)
        {
            targetLean = -1.0;
            LeanLock = true;
            if (!wasLeanLocked)
            {
                LockedHand = DoDAHandSwapController.Hand_Left;
            }
        }
        else if (leaningRight && !leaningLeft)
        {
            targetLean = 1.0;
            LeanLock = true;
            if (!wasLeanLocked)
            {
                LockedHand = DoDAHandSwapController.Hand_Right;
            }
        }
        else
        {
            LeanLock = false;
            LockedHand = -1;
        }

        LeanAmount += (targetLean - LeanAmount) * leanSmoothing;

        AppliedOffset = LeanAmount * LeanDistance;

        let agent = FieldAgent(owner);
        if (agent != null)
        {
            agent.LeanOffset = AppliedOffset;
        }

        double rightX = Cos(owner.angle - 90.0);
        double rightY = Sin(owner.angle - 90.0);

        owner.SetViewPos(
            (
                rightX * AppliedOffset,
                rightY * AppliedOffset,
                0.0
            ),
            VPSF_ABSOLUTEOFFSET
        );
    }

    clearscope bool IsLeanLocked()
    {
        return LeanLock;
    }

    clearscope int GetLockedHand()
    {
        return LockedHand;
    }

    void SetLockedHand(int hand)
    {
        LockedHand = hand;
    }

    clearscope double GetLeanAmount()
    {
        return LeanAmount;
    }

    clearscope double GetLeanDistance()
    {
        return LeanDistance;
    }

    clearscope double GetAppliedOffset()
    {
        return AppliedOffset;
    }
}