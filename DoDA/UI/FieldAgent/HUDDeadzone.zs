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

        // In UZDoom/DOOM, player FOV is defined for a 4:3 reference display (Hor+ projection).
        // The vertical half-FOV tangent is constant for a given base FOV:
        double refAspect = 4.0 / 3.0;
        double halfFovBase = fov * 0.5;
        double tanHalfFovY = Tan(halfFovBase) / refAspect;

        // Viewport focal length in physical pixels:
        double focalLength = halfViewHeight / tanHalfFovY;

        // Signed FieldAgent/fire-trace contract:
        // negative yaw = right on screen;
        // positive pitch = down on screen.
        double cosYaw = Cos(yawGap);
        double safeCosYaw = (Abs(cosYaw) > 0.0001) ? cosYaw : 0.0001;

        double dotX = cx - Tan(yawGap) * focalLength;
        double dotY = cy + (Tan(pitchGap) / safeCosYaw) * focalLength;

        double boxHalfX = Tan(yawLimit) * focalLength;
        double boxHalfY = Tan(pitchLimit) * focalLength;

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