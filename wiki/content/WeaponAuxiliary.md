# Weapon Auxiliary Systems

## HandSwapController
Manages hand swap logic, including locking and swap restrictions.
- `Hand_Left`/`Hand_Right`: Constants for hand identification.
- `ResolveDesiredHand(...)`: Determines the desired hand based on lean, swap inputs, and deadzone aim.
- `IsPistolSwapLocked()`: Checks if the swap is locked (e.g., during active Deadzone Aim).

## SpriteAnimator
Manages procedural weapon sprite animation for sway, tilt, and lean effects.
- `Update(...)`: Calculates `FinalX`, `FinalY`, and `FinalRotation` based on yaw/pitch gap, lean amount, and hand dip amount.
- `Apply(...)`: Applies the calculated procedural offsets to the weapon sprite (`PSprite`).

## AmmoDispenser
A simple interactable actor for acquiring ammunition.
- `Used(Actor user)`: Adds 15 rounds of `Clip` ammunition to the player upon interaction.
