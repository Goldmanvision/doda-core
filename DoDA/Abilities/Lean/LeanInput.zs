///////////////////////////
// DoDA/Abilities/Lean/LeanInput.zs
///////////////////////////

class DoDALeanInput : Object
{
    bool LeaningLeft;
    bool LeaningRight;
    bool ScrollUp;
    bool ScrollDown;

    bool LeaningLeftPressed;
    bool LeaningRightPressed;

    bool PreviousLeaningLeft;
    bool PreviousLeaningRight;

    void Update(PlayerPawn owner)
    {
        LeaningLeft = false;
        LeaningRight = false;
        ScrollUp = false;
        ScrollDown = false;

        LeaningLeftPressed = false;
        LeaningRightPressed = false;

        if (owner == null || owner.player == null)
        {
            PreviousLeaningLeft = false;
            PreviousLeaningRight = false;
            return;
        }

        int buttons = owner.player.cmd.buttons;

        LeaningLeft = (buttons & BT_USER1) != 0;
        LeaningRight = (buttons & BT_USER2) != 0;
        // ScrollUp = (buttons & BT_USER3) != 0;
        ScrollUp = false;
        ScrollDown = (buttons & BT_USER4) != 0;

        LeaningLeftPressed = LeaningLeft && !PreviousLeaningLeft;
        LeaningRightPressed = LeaningRight && !PreviousLeaningRight;

        PreviousLeaningLeft = LeaningLeft;
        PreviousLeaningRight = LeaningRight;
    }

    clearscope bool IsLeaningLeft()
    {
        return LeaningLeft;
    }

    clearscope bool IsLeaningRight()
    {
        return LeaningRight;
    }

    clearscope bool IsLeaning()
    {
        return LeaningLeft || LeaningRight;
    }

    clearscope bool IsScrollUp()
    {
        return ScrollUp;
    }

    clearscope bool IsScrollDown()
    {
        return ScrollDown;
    }

    clearscope bool WasLeaningLeftPressed()
    {
        return LeaningLeftPressed;
    }

    clearscope bool WasLeaningRightPressed()
    {
        return LeaningRightPressed;
    }
}