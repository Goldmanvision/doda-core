/*//////////////////////////|
// DoDA/UI/FOIMSX/FOIMSXCampaignClock.zs
//
// Canonical FOIMS-X campaign-clock presentation utility.
//
// Boundary:
//   - Converts the native strategic-minute authority to a Gregorian
//     date/time display beginning 1992-02-01 00:00:00.
//   - Performs no persistence, state mutation, native mutation, input,
//     scheduling, or session lifecycle handling.
//   - The native DoDA strategic simulation remains the sole time authority.
*///////////////////////////|

class DoDAFOIMSXCampaignClock : Object
{
    const EPOCH_YEAR = 1992;
    const EPOCH_MONTH = 2;
    const EPOCH_DAY = 1;

    const MINUTES_PER_HOUR = 60;
    const HOURS_PER_DAY = 24;
    const MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY;

    static ui bool IsLeapYear(int year)
    {
        if ((year % 400) == 0)
        {
            return true;
        }

        if ((year % 100) == 0)
        {
            return false;
        }

        return (year % 4) == 0;
    }

    static ui int DaysInMonth(int year, int month)
    {
        switch (month)
        {
            case 1:  return 31;
            case 2:  return IsLeapYear(year) ? 29 : 28;
            case 3:  return 31;
            case 4:  return 30;
            case 5:  return 31;
            case 6:  return 30;
            case 7:  return 31;
            case 8:  return 31;
            case 9:  return 30;
            case 10: return 31;
            case 11: return 30;
            case 12: return 31;
        }

        return 31;
    }

    static ui String Pad2(int value)
    {
        if (value < 10)
        {
            return "0" .. String.Format("%d", value);
        }

        return String.Format("%d", value);
    }

    static ui String Pad3(int value)
    {
        if (value < 10)
        {
            return "00" .. String.Format("%d", value);
        }

        if (value < 100)
        {
            return "0" .. String.Format("%d", value);
        }

        return String.Format("%d", value);
    }

    static ui String GetAssignmentMetaText(int strategicMinutes, int activeCount)
    {
        // FOIMS_X_CANONICAL_CLOCK_1992_02_01
        int safeMinutes = strategicMinutes;

        if (safeMinutes < 0)
        {
            safeMinutes = 0;
        }

        int elapsedDays = safeMinutes / MINUTES_PER_DAY;
        int minuteOfDay = safeMinutes % MINUTES_PER_DAY;

        int year = EPOCH_YEAR;
        int month = EPOCH_MONTH;
        int day = EPOCH_DAY;

        while (elapsedDays > 0)
        {
            int daysRemainingInMonth = DaysInMonth(year, month) - day + 1;

            if (elapsedDays < daysRemainingInMonth)
            {
                day += elapsedDays;
                elapsedDays = 0;
            }
            else
            {
                elapsedDays -= daysRemainingInMonth;
                day = 1;
                month++;

                if (month > 12)
                {
                    month = 1;
                    year++;
                }
            }
        }

        int hour = minuteOfDay / MINUTES_PER_HOUR;
        int minute = minuteOfDay % MINUTES_PER_HOUR;
        int campaignDay = safeMinutes / MINUTES_PER_DAY + 1;

        return (
            "DATE: "
            .. String.Format("%d", year)
            .. "-"
            .. Pad2(month)
            .. "-"
            .. Pad2(day)
            .. "  TIME: "
            .. Pad2(hour)
            .. ":"
            .. Pad2(minute)
            .. "  DAY: "
            .. Pad3(campaignDay)
            .. "  ACTIVE: "
            .. String.Format("%d", activeCount)
        );
    }
}
