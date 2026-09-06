///////////////////////////
// DoDA/UI/FieldAgent/DeadzoneHUDBridge.zs
///////////////////////////

class DeadzoneHUDBridge : Object
{
    static double GetLeanOffset(PlayerPawn owner)
    {
        let agent = FieldAgent(owner);
        return agent != null ? agent.LeanOffset : 0.0;
    }
}