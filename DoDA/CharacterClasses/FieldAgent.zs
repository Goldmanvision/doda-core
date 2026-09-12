///////////////////////////
// DoDA/CharacterClasses/FieldAgent.zs
///////////////////////////

class FieldAgent : DoDAPlayerBase
{
    double LeanOffset;

    Default
    {
        Player.DisplayName "Field Agent";
		Player.StartItem "DoDAB92Right";
		Player.StartItem "Fist";
        Player.StartItem "DoDAHolster";
        Player.StartItem "Clip", 45;
    }

    override bool ShouldActivateDeadzoneAim()
    {
        if (player == null)
        {
            return false;
        }

        bool isAkimbo = DoDA.IsAkimboActive();
        bool leaningLeft = (player.cmd.buttons & BT_USER1) != 0;
        bool leaningRight = (player.cmd.buttons & BT_USER2) != 0;
        bool isLeaning = (leaningLeft || leaningRight) && !(leaningLeft && leaningRight);

        bool realAltFire = (!isAkimbo || isLeaning) && ((player.cmd.buttons & BT_ALTATTACK) != 0);
        bool forceDeadzone = DoDAInputUtility.ReadBoolSetting(player, 'doda_debug_force_deadzone', false);

        return realAltFire || forceDeadzone || isLeaning;
    }
}