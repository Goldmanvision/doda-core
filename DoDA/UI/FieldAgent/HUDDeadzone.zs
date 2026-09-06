///////////////////////////
// DoDA/UI/FieldAgent/HUDDeadzone.zs
///////////////////////////

class DoDAHUDDeadzone : Object
{
    void DrawDeadzone(
        bool active,
        double yawGap,
        double pitchGap,
        double yawLimit,
        double pitchLimit,
        double fov,
        int screenWidth,
        int screenHeight,
        double leanOffset
    )
    {
        if (!active)
        {
            return;
        }

        if (screenWidth <= 0 || screenHeight <= 0)
        {
            return;
        }

        if (fov <= 1.0)
        {
            fov = 90.0;
        }

        let [viewX, viewY, viewWidth, viewHeight] =
            Screen.GetViewWindow();

        if (viewWidth <= 0 || viewHeight <= 0)
        {
            return;
        }

        double halfViewWidth = viewWidth * 0.5;
        double halfViewHeight = viewHeight * 0.5;

        double cx = viewX + halfViewWidth;
        double cy = viewY + halfViewHeight;

        double aspect = viewWidth / double(viewHeight);
        double refAspect = 4.0 / 3.0;

        double halfFovBase = fov * 0.5;
        double halfFovYaw = ATan(
            Tan(halfFovBase) * (aspect / refAspect)
        );

        double halfFovPitch = ATan(
            Tan(halfFovYaw) / aspect
        );

        // Signed FieldAgent/fire-trace contract:
        // negative yaw = right on screen;
        // positive pitch = down on screen.
        double dotX = cx
            - (Tan(yawGap) / Tan(halfFovYaw)) * halfViewWidth;

        double dotY = cy
            + (Tan(pitchGap) / Tan(halfFovPitch)) * halfViewHeight;

        double boxHalfX = (
            Tan(yawLimit) / Tan(halfFovYaw)
        ) * halfViewWidth;

        double boxHalfY = (
            Tan(pitchLimit) / Tan(halfFovPitch)
        ) * halfViewHeight;

        int left = int(cx - boxHalfX);
        int top = int(cy - boxHalfY);
        int width = int(boxHalfX * 2.0);
        int height = int(boxHalfY * 2.0);

        Screen.Dim(Color(0, 255, 0), 0.20, left, top, width, 2);
        Screen.Dim(
            Color(0, 255, 0),
            0.20,
            left,
            top + height - 2,
            width,
            2
        );

        Screen.Dim(Color(0, 255, 0), 0.15, left, top, 2, height);
        Screen.Dim(
            Color(0, 255, 0),
            0.15,
            left + width - 2,
            top,
            2,
            height
        );

        // Bright, small red X reticle.
        int reticleX = int(dotX);
        int reticleY = int(dotY);
        Color reticleColor = Color(255, 32, 32);

        Screen.DrawThickLine(
            reticleX - 4,
            reticleY - 4,
            reticleX + 4,
            reticleY + 4,
            2,
            reticleColor
        );

        Screen.DrawThickLine(
            reticleX + 4,
            reticleY - 4,
            reticleX - 4,
            reticleY + 4,
            2,
            reticleColor
        );
    }
}