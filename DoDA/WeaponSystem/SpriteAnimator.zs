class DoDASpriteAnimator : Object
{
    double FinalX;
    double FinalY;
    double FinalRotation;

    void Update(
        int hand,
        double yawGap,
        double pitchGap,
        double leanAmount,
        double handDipAmount,
        bool isLeaning,
        bool leaningLeft,
        int archetype = ARCHETYPE_Default
    )
    {
        // B92L and B92R are distinct authored sprite sets. Do not apply a
        // second hand-specific baseline offset on top of their art offsets.
        double leftHandRestX = 0.0;
        double rightHandRestX = 0.0;
        double weaponRestY = 32.0;

        // B92L needs more outward travel at the left deadzone boundary.
        // Keep B92R unchanged because its right-edge placement is correct.
        double leftYawSpriteScale = 4.5;
        double rightYawSpriteScale = 3.0;

        double pitchSpriteScale = 0.6;
        double mp5BottomPitchSpriteScale = 4.5;
        double leanSpriteShift = 8.0;
        double dipDistance = 40.0;

        double tiltStartThreshold = 3.0;
        double tiltScale = 1.4;
        double maxTilt = 18.0;
        double leanTiltAmount = 10.0;

        bool rightHand = hand == DoDAHandSwapController.Hand_Right;

        double restX = rightHand
            ? rightHandRestX
            : leftHandRestX;

        double yawSpriteScale = rightHand
            ? rightYawSpriteScale
            : leftYawSpriteScale;

        // Expand MP5kSD opposite horizontal travel limit when crosshair is at left deadzone boundary
        if (archetype == ARCHETYPE_SMG && yawGap > 0.0)
        {
            yawSpriteScale = leftYawSpriteScale;
        }

        // Expand MP5kSD lower vertical travel limit when crosshair is at bottom deadzone boundary
        if (archetype == ARCHETYPE_SMG && pitchGap > 0.0)
        {
            pitchSpriteScale = mp5BottomPitchSpriteScale;
        }

        double rawTilt = Max(
            0.0,
            Abs(yawGap) - tiltStartThreshold
        ) * tiltScale;

        rawTilt = Clamp(rawTilt, 0.0, maxTilt);

        double tiltMagnitude = isLeaning
            ? Max(leanTiltAmount, rawTilt)
            : rawTilt;

        double tiltSign;

        if (isLeaning)
        {
            tiltSign = leaningLeft ? 1.0 : -1.0;
        }
        else
        {
            tiltSign = yawGap < 0.0 ? -1.0 : 1.0;
        }

        FinalRotation = -tiltMagnitude * tiltSign;

        if (rightHand)
        {
            FinalRotation = -FinalRotation;
        }

        FinalX = restX
            - yawGap * yawSpriteScale
            + leanAmount * leanSpriteShift;

        FinalY = weaponRestY
            + pitchGap * pitchSpriteScale
            + handDipAmount * dipDistance;
    }

    play void Apply(
        PSprite weaponSprite,
        double debugX,
        double debugY,
        double debugRotation
    )
    {
        if (weaponSprite == null)
        {
            return;
        }

        weaponSprite.x = FinalX + debugX;
        weaponSprite.y = FinalY + debugY;

        weaponSprite.bFlip = false;
        weaponSprite.rotation = FinalRotation + debugRotation;

        weaponSprite.HAlign = PSPA_CENTER;
        weaponSprite.VAlign = PSPA_CENTER;
        weaponSprite.bPivotPercent = true;
        weaponSprite.pivot = (0.5, 0.5);
    }

    // Used only while native A_Lower/A_Raise owns weaponSprite.y.
    // debugY is accepted to match the common WeaponBase call signature,
    // but is intentionally ignored so native transition motion is preserved.
    play void ApplyTransition(
        PSprite weaponSprite,
        double debugX,
        double debugY,
        double debugRotation
    )
    {
        if (weaponSprite == null)
        {
            return;
        }

        weaponSprite.x = FinalX + debugX;

        weaponSprite.bFlip = false;
        weaponSprite.rotation = FinalRotation + debugRotation;

        weaponSprite.HAlign = PSPA_CENTER;
        weaponSprite.VAlign = PSPA_CENTER;
        weaponSprite.bPivotPercent = true;
        weaponSprite.pivot = (0.5, 0.5);
    }

    clearscope double GetFinalX()
    {
        return FinalX;
    }

    clearscope double GetFinalY()
    {
        return FinalY;
    }

    clearscope double GetFinalRotation()
    {
        return FinalRotation;
    }
}