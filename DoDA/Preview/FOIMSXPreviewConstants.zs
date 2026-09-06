/*//////////////////////////|
// DoDA/Preview/FOIMSXPreviewConstants.zs
//
// FOIMS-X Standalone Preview: shared presentation vocabulary.
//
// Boundary:
//   - Preview-package-only labels and layout constants.
//   - No native DoDA calls.
//   - No persistence.
//   - No input handling.
//   - No rendering.
//   - No actor definitions.
*///////////////////////////|

class DoDAFOIMSXPreviewConstants : Object
{
    const VIRTUAL_WIDTH  = 640;
    const VIRTUAL_HEIGHT = 480;

    const FIRST_METRIC_INDEX = 0;
    const LAST_METRIC_INDEX  = 8;

    static String GetProductTitle()
    {
        return "FOIMS-X";
    }

    static String GetModeLabel()
    {
        return "MODE: STANDALONE PREVIEW";
    }

    static String GetAuthorityWarning()
    {
        return "NON-AUTHORITATIVE DEMONSTRATION DATA";
    }

    static String GetTopMenuLabel()
    {
        return "FILE   DIRECTORY   CASES   OPERATIONS   SYSTEM";
    }

    static String GetOperationsTitle()
    {
        return "OPERATIONS";
    }

    static String GetAnalysisTitle()
    {
        return "ANALYSIS";
    }

    static String GetLogisticsTitle()
    {
        return "LOGISTICS";
    }

    static String GetNoticeTitle()
    {
        return "DEPARTMENT NOTICES";
    }

    static String GetStatusLine()
    {
        return "FOIMS-X PREVIEW -- READ ONLY -- NON-AUTHORITATIVE DATA";
    }

    static String GetNavigationHint()
    {
        return "ESCAPE / O CLOSE TERMINAL";
    }
}
