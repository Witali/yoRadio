#include "timezones.h"
#include <limits.h>
#include <stddef.h>
#include <string.h>

typedef struct
{
    int64_t utc;
    int32_t offset;
    bool daylight;
} timezone_transition_t;
typedef struct
{
    unsigned month, week, weekday;
    int32_t seconds;
} timezone_rule_t;
typedef struct
{
    const timezone_transition_t *transitions;
    unsigned count;
    int32_t initial_offset;
    bool initial_daylight;
    int32_t standard_offset, daylight_offset;
    bool has_daylight;
    timezone_rule_t start, end;
} timezone_data_t;
#include "timezone_data.h"

static const timezone_data_t *country_zone(const char *country)
{
    /* Retain the factory case-sensitive country defaults and unknown-key GB fallback. */
    if (country)
        for (unsigned i = 0; i < sizeof(timezone_countries)/sizeof(timezone_countries[0]); ++i)
            if (!strcmp(country, timezone_countries[i].country))
                return &timezone_zones[timezone_countries[i].zone];
    return &timezone_zones[TIMEZONE_DEFAULT_INDEX];
}

static int64_t calendar_days(int64_t year, unsigned month, unsigned day)
{
    /* Convert a proleptic Gregorian date to signed days since 1970-01-01.
     * March-based eras include the Gregorian 100/400-year exceptions and floor
     * division keeps the same calculation valid before the POSIX epoch. */
    year -= month <= 2;
    int64_t era = (year >= 0 ? year : year-399)/400;
    unsigned within_era = (unsigned)(year-era*400);
    unsigned march_month = month > 2 ? month-3 : month+9;
    unsigned day_of_year = (153*march_month+2)/5+day-1;
    return era*146097+within_era*365+within_era/4-within_era/100+day_of_year-719468;
}

static int64_t transition_time(int64_t year, const timezone_rule_t *rule, int32_t before_offset)
{
    /* Interpret wall time using the offset BEFORE the transition.
     * Week five means the last matching weekday; signed/extended seconds may
     * cross midnight (Greenland -1h, Israel 26h, Egypt and Chile 24h). */
    int64_t first_day = calendar_days(year, rule->month, 1);
    int weekday = (int)((first_day+4)%7);
    if (weekday < 0)
        weekday += 7;
    unsigned day = 1+(rule->weekday+7-(unsigned)weekday)%7+7*(rule->week-1);
    int64_t next_month = rule->month == 12 ? calendar_days(year+1, 1, 1)
                                         : calendar_days(year, rule->month+1, 1);
    if (first_day+day-1 >= next_month)
        day -= 7;
    return (first_day+day-1)*86400+rule->seconds-before_offset;
}

static bool calendar_matches(time_t epoch, const struct tm *calendar)
{
    /* Reject libc overflow that can wrap a calendar field without returning NULL. */
    if ((unsigned)calendar->tm_mon > 11 || calendar->tm_mday < 1 || calendar->tm_mday > 31 ||
        (unsigned)calendar->tm_hour > 23 || (unsigned)calendar->tm_min > 59 ||
        (unsigned)calendar->tm_sec > 59)
        return false;
    int64_t days = calendar_days((int64_t)calendar->tm_year+1900,
                                 (unsigned)calendar->tm_mon+1, (unsigned)calendar->tm_mday);
    return days*86400+calendar->tm_hour*3600+calendar->tm_min*60+calendar->tm_sec == (int64_t)epoch;
}

bool timezone_utc_offset(const char *country, time_t utc, int32_t *offset, bool *daylight)
{
    /* Select historical transitions or the explicit future recurrence.
     * FIXED_FACTORY: 0x42010a06 supplies implicit DST strings that Newlib applies
     * with US defaults, including Europe and the southern hemisphere. Pinned
     * IANA rules also preserve irregular transitions and non-hour offsets. */
    if (!offset || !daylight)
        return false;
    const timezone_data_t *zone = country_zone(country);
    int64_t epoch = (int64_t)utc;
    if (zone->count && epoch <= zone->transitions[zone->count-1].utc)
    {
        unsigned low = 0, high = zone->count;
        while (low < high)
        {
            unsigned middle = low+(high-low)/2;
            if (zone->transitions[middle].utc <= epoch)
                low = middle+1;
            else
                high = middle;
        }
        *offset = low ? zone->transitions[low-1].offset : zone->initial_offset;
        *daylight = low ? zone->transitions[low-1].daylight : zone->initial_daylight;
        return true;
    }
    *offset = zone->standard_offset;
    *daylight = false;
    if (!zone->has_daylight)
        return true;
    struct tm universal;
    if (!gmtime_r(&utc, &universal) || !calendar_matches(utc, &universal))
        return false;
    int64_t year = (int64_t)universal.tm_year+1900, latest = INT64_MIN;
    /* Select the latest event across adjacent years rather than assuming the
     * northern start-before-end order. This also handles Ireland's negative DST. */
    for (int delta = -1; delta <= 1; ++delta)
    {
        int64_t start = transition_time(year+delta, &zone->start, zone->standard_offset);
        int64_t end = transition_time(year+delta, &zone->end, zone->daylight_offset);
        if (start <= epoch && start > latest)
        {
            latest = start;
            *offset = zone->daylight_offset;
            *daylight = true;
        }
        if (end <= epoch && end > latest)
        {
            latest = end;
            *offset = zone->standard_offset;
            *daylight = false;
        }
    }
    return latest != INT64_MIN;
}

bool timezone_local_time(const char *country, time_t utc, struct tm *local)
{
    /* Produce a complete local calendar without racing a process-global TZ change.
     * Preserve the caller's output when the epoch or libc conversion is invalid. */
    int32_t offset;
    bool daylight;
    if (!local || !timezone_utc_offset(country, utc, &offset, &daylight))
        return false;
    int64_t epoch = (int64_t)utc;
    if ((offset > 0 && epoch > INT64_MAX-offset) ||
        (offset < 0 && epoch < INT64_MIN-offset))
        return false;
    time_t shifted = (time_t)(epoch+offset);
    if ((int64_t)shifted != epoch+offset)
        return false;
    struct tm result;
    if (!gmtime_r(&shifted, &result) || !calendar_matches(shifted, &result))
        return false;
    result.tm_isdst = daylight;
    *local = result;
    return true;
}
