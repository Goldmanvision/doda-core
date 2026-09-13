/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXDrawingHelpers.zs
//
// FOIMS-X Stateless Drawing Helpers.
//
// Shared rendering primitives for FOIMS-X UI presentation renderers.
//
// Scope & Boundary:
//   - Pure stateless drawing helpers: receives all coordinates, colors, fonts,
//     and text explicitly as parameters.
//   - Zero domain knowledge: does not know Personnel or Assignment models, records, or fields.
//   - Zero native calls: does not call DoDA native queries.
//   - Zero lifecycle, input, tick, timer, or state management.
*///////////////////////////|

class DoDAFOIMSXDrawingHelpers : Object
{
    // Draws a filled rectangle in virtual 640x480 coordinate space.
    static ui void DrawVirtualRect(
        double vx,
        double vy,
        double vw,
        double vh,
        Color col
    )
    {
        Vector2 realPos, realSize;
        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        Screen.Dim(
            col,
            1.0,
            int(realPos.x),
            int(realPos.y),
            int(realSize.x),
            int(realSize.y)
        );
    }

    // Computes real screen clip rectangle bounds from virtual 640x480 coordinates.
    static ui void GetRealClipRect(
        double vx,
        double vy,
        double vw,
        double vh,
        out int clipLeft,
        out int clipTop,
        out int clipRight,
        out int clipBottom
    )
    {
        Vector2 realClipPos, realClipSize;
        [realClipPos, realClipSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        clipLeft = int(realClipPos.x);
        clipTop = int(realClipPos.y);
        clipRight = int(realClipPos.x + realClipSize.x);
        clipBottom = int(realClipPos.y + realClipSize.y);
    }

    // Draws a raised panel in virtual 640x480 coordinate space with highlight and shadow borders.
    static ui void DrawRaisedPanel(
        double vx,
        double vy,
        double vw,
        double vh,
        Color bgCol
    )
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);

        Vector2 realPos, realSize;
        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x1, y0, 0xFF5A7292);
        Screen.DrawLine(x0, y0, x0, y1, 0xFF5A7292);
        Screen.DrawLine(x0, y1, x1, y1, 0xFF080D14);
        Screen.DrawLine(x1, y0, x1, y1, 0xFF080D14);
    }

    // Draws a sunken panel in virtual 640x480 coordinate space with shadow and highlight borders.
    static ui void DrawSunkenPanel(
        double vx,
        double vy,
        double vw,
        double vh,
        Color bgCol
    )
    {
        DrawVirtualRect(vx, vy, vw, vh, bgCol);

        Vector2 realPos, realSize;
        [realPos, realSize] = Screen.VirtualToRealCoords(
            (vx, vy), (vw, vh), (640, 480), false, true
        );

        double x0 = realPos.x;
        double y0 = realPos.y;
        double x1 = realPos.x + realSize.x;
        double y1 = realPos.y + realSize.y;

        Screen.DrawLine(x0, y0, x1, y0, 0xFF080D14);
        Screen.DrawLine(x0, y0, x0, y1, 0xFF080D14);
        Screen.DrawLine(x0, y1, x1, y1, 0xFF364860);
        Screen.DrawLine(x1, y0, x1, y1, 0xFF364860);
    }

    // Draws virtual text (e.g. headers and footer hints) in 640x480 coordinate space.
    static ui void DrawVirtualText(
        Font font,
        int fontColor,
        double x,
        double y,
        String text,
        double scaleX = 1.0,
        double scaleY = 1.0
    )
    {
        Screen.DrawText(
            font,
            fontColor,
            x,
            y,
            text,
            DTA_VirtualWidth, 640,
            DTA_VirtualHeight, 480,
            DTA_ScaleX, scaleX,
            DTA_ScaleY, scaleY
        );
    }

    // Draws scaled, monospaced text clipped to the specified real screen bounds.
    static ui void DrawClippedText(
        Font font,
        int fontColor,
        double x,
        double y,
        String text,
        int clipLeft,
        int clipTop,
        int clipRight,
        int clipBottom,
        int textLen = 0
    )
    {
        if (textLen > 0)
        {
            Screen.DrawText(
                font,
                fontColor,
                x,
                y,
                text,
                DTA_VirtualWidth, 640,
                DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5,
                DTA_ScaleY, 0.5,
                DTA_Monospace, 1,
                DTA_Spacing, 9,
                DTA_TextLen, textLen,
                DTA_ClipLeft, clipLeft,
                DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop,
                DTA_ClipBottom, clipBottom
            );
        }
        else
        {
            Screen.DrawText(
                font,
                fontColor,
                x,
                y,
                text,
                DTA_VirtualWidth, 640,
                DTA_VirtualHeight, 480,
                DTA_ScaleX, 0.5,
                DTA_ScaleY, 0.5,
                DTA_Monospace, 1,
                DTA_Spacing, 9,
                DTA_ClipLeft, clipLeft,
                DTA_ClipRight, clipRight,
                DTA_ClipTop, clipTop,
                DTA_ClipBottom, clipBottom
            );
        }
    }
}
