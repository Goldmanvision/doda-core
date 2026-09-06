/*//////////////////////////|
// DoDA/Preview/FOIMSXPreviewModel.zs
//
// FOIMS-X Standalone Preview: deterministic faux telemetry model.
//
// Boundary:
//   - Presentation-only placeholder data.
//   - No native DoDA calls.
//   - No persistence.
//   - No randomness.
//   - No actor, map, player, input, or renderer ownership.
//
// Every output is a deterministic function of elapsed preview tics.
// Passing the same elapsed-tic value always produces the same output.
*///////////////////////////|

enum EDoDAPreviewMetrics
{
    METRIC_OPERATIONAL_PRESSURE = 0, // 4s
    METRIC_FIELD_READINESS      = 1, // 7s
    METRIC_THREAT_SIGNAL        = 2, // 3s

    METRIC_INCOMING_REPORTS     = 3, // 6s
    METRIC_ANALYSIS_QUEUE       = 4, // 10s
    METRIC_RESEARCH_BACKLOG     = 5, // 8s

    METRIC_ASSET_AVAILABILITY   = 6, // 12s
    METRIC_COMMUNICATIONS       = 7, // 1s (pulse)
    METRIC_NETWORK_STATUS       = 8, // 5s

    METRIC_COUNT                = 9
};

class DoDAFOIMSXPreviewModel : Object
{
    const TICRATE = 35;

    static int GetMetricCount()
    {
        return METRIC_COUNT;
    }

    static int GetElapsedSeconds(int elapsedTics)
    {
        if (elapsedTics <= 0)
        {
            return 0;
        }
        return elapsedTics / TICRATE;
    }

    private static int ClampValue(int value, int minimum, int maximum)
    {
        if (value < minimum)
        {
            return minimum;
        }
        if (value > maximum)
        {
            return maximum;
        }
        return value;
    }

    private static int GetCycleIndex(int value, int count)
    {
        if (count <= 0)
        {
            return 0;
        }
        int result = value % count;
        if (result < 0)
        {
            result += count;
        }
        return result;
    }

    static String GetMetricLabel(int metric)
    {
        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
                return "OPERATIONAL PRESSURE";
            case METRIC_FIELD_READINESS:
                return "FIELD READINESS";
            case METRIC_THREAT_SIGNAL:
                return "THREAT SIGNAL";

            case METRIC_INCOMING_REPORTS:
                return "INCOMING REPORTS";
            case METRIC_ANALYSIS_QUEUE:
                return "ANALYSIS QUEUE";
            case METRIC_RESEARCH_BACKLOG:
                return "RESEARCH BACKLOG";

            case METRIC_ASSET_AVAILABILITY:
                return "ASSET AVAILABILITY";
            case METRIC_COMMUNICATIONS:
                return "COMMUNICATIONS TRAFFIC";
            case METRIC_NETWORK_STATUS:
                return "NETWORK STATUS";
        }
        return "UNKNOWN METRIC";
    }

    static String GetMetricUnit(int metric)
    {
        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
            case METRIC_FIELD_READINESS:
            case METRIC_THREAT_SIGNAL:
            case METRIC_ASSET_AVAILABILITY:
            case METRIC_COMMUNICATIONS:
            case METRIC_NETWORK_STATUS:
                return "%";

            case METRIC_INCOMING_REPORTS:
                return " REPORTS";

            case METRIC_ANALYSIS_QUEUE:
            case METRIC_RESEARCH_BACKLOG:
                return " ITEMS";
        }
        return "";
    }

    static int GetUpdateBandSeconds(int metric)
    {
        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
                return 4;
            case METRIC_FIELD_READINESS:
                return 7;
            case METRIC_THREAT_SIGNAL:
                return 3;

            case METRIC_INCOMING_REPORTS:
                return 6;
            case METRIC_ANALYSIS_QUEUE:
                return 10;
            case METRIC_RESEARCH_BACKLOG:
                return 8;

            case METRIC_ASSET_AVAILABILITY:
                return 12;
            case METRIC_COMMUNICATIONS:
                return 1;
            case METRIC_NETWORK_STATUS:
                return 5;
        }
        return 1;
    }

    static int GetValue(int metric, int elapsedTics)
    {
        int seconds = GetElapsedSeconds(elapsedTics);

        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
                return GetOperationalPressure(seconds);
            case METRIC_FIELD_READINESS:
                return GetFieldReadiness(seconds);
            case METRIC_THREAT_SIGNAL:
                return GetThreatSignal(seconds);

            case METRIC_INCOMING_REPORTS:
                return GetIncomingReports(seconds);
            case METRIC_ANALYSIS_QUEUE:
                return GetAnalysisQueue(seconds);
            case METRIC_RESEARCH_BACKLOG:
                return GetResearchBacklog(seconds);

            case METRIC_ASSET_AVAILABILITY:
                return GetAssetAvailability(seconds);
            case METRIC_COMMUNICATIONS:
                return GetCommunicationsTraffic(seconds);
            case METRIC_NETWORK_STATUS:
                return GetNetworkStatus(seconds);
        }
        return 0;
    }

    static String GetTrendLabel(int metric, int elapsedTics)
    {
        int seconds = GetElapsedSeconds(elapsedTics);

        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
                return GetOperationalPressureTrend(seconds);
            case METRIC_FIELD_READINESS:
                return GetFieldReadinessTrend(seconds);
            case METRIC_THREAT_SIGNAL:
                return GetThreatSignalTrend(seconds);

            case METRIC_INCOMING_REPORTS:
                return "RECEIVING";
            case METRIC_ANALYSIS_QUEUE:
                return GetAnalysisQueueTrend(seconds);
            case METRIC_RESEARCH_BACKLOG:
                return GetResearchBacklogTrend(seconds);

            case METRIC_ASSET_AVAILABILITY:
                return GetAssetAvailabilityTrend(seconds);
            case METRIC_COMMUNICATIONS:
                return GetCommunicationsTrend(seconds);
            case METRIC_NETWORK_STATUS:
                return GetNetworkStatusTrend(seconds);
        }
        return "UNKNOWN";
    }

    static String GetMetricDetail(int metric)
    {
        switch (metric)
        {
            case METRIC_OPERATIONAL_PRESSURE:
                return "NETWORK LOAD ACROSS ACTIVE OPERATIONS";
            case METRIC_FIELD_READINESS:
                return "DEPLOYMENT CAPACITY ESTIMATE";
            case METRIC_THREAT_SIGNAL:
                return "REMOTE OBSERVATION ALERT INDEX";

            case METRIC_INCOMING_REPORTS:
                return "UNCLASSIFIED FIELD INTAKE";
            case METRIC_ANALYSIS_QUEUE:
                return "PENDING REVIEW AND CORRELATION";
            case METRIC_RESEARCH_BACKLOG:
                return "UNRESOLVED REFERENCE MATERIAL";

            case METRIC_ASSET_AVAILABILITY:
                return "GENERAL SUPPORT RESOURCE ESTIMATE";
            case METRIC_COMMUNICATIONS:
                return "FIELD-TO-HQ TRAFFIC VOLUME";
            case METRIC_NETWORK_STATUS:
                return "GRID SYNCHRONIZATION AND INTEGRITY";
        }
        return "NO DETAIL AVAILABLE";
    }

    // Rolling Notice Feed: updates every 9 real seconds
    static String GetSystemNotice(int elapsedTics)
    {
        int seconds = GetElapsedSeconds(elapsedTics);
        int notice = GetCycleIndex(seconds / 9, 7);

        switch (notice)
        {
            case 0:
                return "Field report received.";
            case 1:
                return "Analysis queue updated.";
            case 2:
                return "Remote observation cycle completed.";
            case 3:
                return "Communications traffic elevated.";
            case 4:
                return "Asset dispatch window opened.";
            case 5:
                return "Department readiness review pending.";
            case 6:
                return "Threat signal recalculated.";
        }
        return "System telemetry nominal.";
    }

    // 1. Operational Pressure: updates every 4s (rises from 30% to 75%)
    private static int GetOperationalPressure(int seconds)
    {
        int band = GetCycleIndex(seconds / 4, 16);
        return ClampValue(30 + band * 3, 0, 100);
    }

    private static String GetOperationalPressureTrend(int seconds)
    {
        int band = GetCycleIndex(seconds / 4, 16);
        if (band >= 13) return "CRITICAL";
        if (band >= 8) return "RISING";
        return "ELEVATING";
    }

    // 2. Field Readiness: updates every 7s (falls from 88% down to 61%)
    private static int GetFieldReadiness(int seconds)
    {
        int band = GetCycleIndex(seconds / 7, 10);
        return ClampValue(88 - band * 3, 0, 100);
    }

    private static String GetFieldReadinessTrend(int seconds)
    {
        int band = GetCycleIndex(seconds / 7, 10);
        if (band >= 8) return "LIMITED";
        if (band >= 4) return "DECLINING";
        return "NOMINAL";
    }

    // 3. Threat Signal: updates every 3s
    private static int GetThreatSignal(int seconds)
    {
        int pattern = GetCycleIndex(seconds / 3, 10);
        switch (pattern)
        {
            case 0: return 18;
            case 1: return 26;
            case 2: return 39;
            case 3: return 52;
            case 4: return 67;
            case 5: return 74;
            case 6: return 61;
            case 7: return 46;
            case 8: return 32;
            case 9: return 23;
        }
        return 18;
    }

    private static String GetThreatSignalTrend(int seconds)
    {
        int threat = GetThreatSignal(seconds);
        if (threat >= 70) return "CRITICAL";
        if (threat >= 50) return "ELEVATED";
        if (threat >= 30) return "GUARDED";
        return "LOW";
    }

    // 4. Incoming Reports: updates every 6s
    private static int GetIncomingReports(int seconds)
    {
        int pattern = GetCycleIndex(seconds / 6, 7);
        switch (pattern)
        {
            case 0: return 2;
            case 1: return 3;
            case 2: return 5;
            case 3: return 4;
            case 4: return 7;
            case 5: return 5;
            case 6: return 3;
        }
        return 2;
    }

    // 5. Analysis Queue: updates every 10s
    private static int GetAnalysisQueue(int seconds)
    {
        int band = GetCycleIndex(seconds / 10, 12);
        if (band < 6)
        {
            return 4 + band * 2;
        }
        return 16 - (band - 6) * 2;
    }

    private static String GetAnalysisQueueTrend(int seconds)
    {
        int band = GetCycleIndex(seconds / 10, 12);
        if (band < 6) return "BUILDING";
        if (band == 6) return "PROCESSING";
        return "DRAINING";
    }

    // 6. Research Backlog: updates every 8s
    private static int GetResearchBacklog(int seconds)
    {
        int band = GetCycleIndex(seconds / 8, 10);
        if (band < 5)
        {
            return 5 + band * 2;
        }
        return 15 - (band - 5) * 2;
    }

    private static String GetResearchBacklogTrend(int seconds)
    {
        int band = GetCycleIndex(seconds / 8, 10);
        if (band < 5) return "ACCUMULATING";
        if (band == 5) return "REVIEWING";
        return "CLEARING";
    }

    // 7. Asset Availability: updates every 12s
    private static int GetAssetAvailability(int seconds)
    {
        int band = GetCycleIndex(seconds / 12, 8);
        if (band < 4)
        {
            return 92 - band * 7;
        }
        return 64 + (band - 4) * 7;
    }

    private static String GetAssetAvailabilityTrend(int seconds)
    {
        int band = GetCycleIndex(seconds / 12, 8);
        if (band < 4) return "ALLOCATING";
        if (band == 4) return "LIMITED";
        return "RECOVERING";
    }

    // 8. Communications Traffic: updates every 1s
    private static int GetCommunicationsTraffic(int seconds)
    {
        int pattern = GetCycleIndex(seconds, 8);
        switch (pattern)
        {
            case 0: return 42;
            case 1: return 57;
            case 2: return 71;
            case 3: return 89;
            case 4: return 94;
            case 5: return 76;
            case 6: return 61;
            case 7: return 48;
        }
        return 42;
    }

    private static String GetCommunicationsTrend(int seconds)
    {
        int traffic = GetCommunicationsTraffic(seconds);
        if (traffic >= 85) return "ELEVATED";
        if (traffic >= 65) return "ACTIVE";
        return "NOMINAL";
    }

    // 9. Network Status: updates every 5s
    private static int GetNetworkStatus(int seconds)
    {
        int pattern = GetCycleIndex(seconds / 5, 6);
        switch (pattern)
        {
            case 0: return 98;
            case 1: return 95;
            case 2: return 91;
            case 3: return 88;
            case 4: return 94;
            case 5: return 99;
        }
        return 98;
    }

    private static String GetNetworkStatusTrend(int seconds)
    {
        int status = GetNetworkStatus(seconds);
        if (status >= 95) return "OPTIMAL";
        if (status >= 90) return "NOMINAL";
        return "REROUTING";
    }
}
