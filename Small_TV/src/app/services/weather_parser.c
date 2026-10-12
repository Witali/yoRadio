#include "services.h"
#include "cJSON.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static bool number(const cJSON *object, const char *name, double minimum, double maximum,
                   double *value)
{
    /* Accept finite, bounded JSON numbers before using them in the renderer. */
    const cJSON *item = cJSON_GetObjectItemCaseSensitive(object, name);
    if (!cJSON_IsNumber(item) || !isfinite(item->valuedouble) || item->valuedouble < minimum ||
        item->valuedouble > maximum)
        return false;
    *value = item->valuedouble;
    return true;
}

bool weather_parse_response(const char *body, size_t length, const tv_settings_t *s,
                            weather_snapshot_t *out)
{
    /* Decode the original Kelvin payload and preserve its display conversions. */
    cJSON *root = cJSON_ParseWithLength(body, length);
    if (!root)
        return false;
    const cJSON *main = cJSON_GetObjectItemCaseSensitive(root, "main"),
                *wind = cJSON_GetObjectItemCaseSensitive(root, "wind");
    const cJSON *weather = cJSON_GetArrayItem(cJSON_GetObjectItemCaseSensitive(root, "weather"), 0);
    const cJSON *icon = cJSON_GetObjectItemCaseSensitive(weather, "icon");
    double temperature, humidity, speed, zone = 0;
    bool valid = number(main, "temp", 173.15, 373.15, &temperature) &&
                 number(main, "humidity", 0, 100, &humidity) &&
                 number(wind, "speed", 0, 150, &speed) && cJSON_IsString(icon) &&
                 strlen(icon->valuestring) == 3;
    if (valid)
    {
        memset(out, 0, sizeof(*out));
        out->valid = true;
        /* 0x4200fd94 subtracts the double Kelvin offset; 0x4200fda0 calls
         * ROM __fixdfsi (truncate toward zero) BEFORE Fahrenheit conversion. */
        out->temperature_c = (int)(temperature - 273.15);
        out->humidity = humidity;
        out->wind_mps = speed;
        number(root, "timezone", -50400, 50400, &zone);
        out->timezone_seconds = zone;
        double minimum, maximum;
        out->temperature_min_c =
            (number(main, "temp_min", 173.15, 373.15, &minimum) ? minimum : temperature) - 273.15;
        out->temperature_max_c =
            (number(main, "temp_max", 173.15, 373.15, &maximum) ? maximum : temperature) - 273.15;
        memcpy(out->icon, icon->valuestring, 4);
        strcpy(out->city, s->city);
        strcpy(out->country, s->country);
        const cJSON *description = cJSON_GetObjectItemCaseSensitive(weather, "description");
        const cJSON *summary = cJSON_GetObjectItemCaseSensitive(weather, "main");
        if (cJSON_IsString(description))
            snprintf(out->description, sizeof(out->description), "%.15s", description->valuestring);
        if (cJSON_IsString(summary))
            snprintf(out->main, sizeof(out->main), "%.15s", summary->valuestring);
        double bearing;
        if (number(wind, "deg", 0, 360, &bearing))
        {
            /* 0x4200fe82..0x4201082c compares doubles against sixteen half-open
             * sectors. A bearing exactly at 11.25 belongs to North Northeast. */
            static const char *directions[] = {
                "North", "North Northeast", "Northeast", "East Northeast",
                "East",  "East Southeast",  "Southeast", "South Southeast",
                "South", "South Southwest", "Southwest", "West Southwest",
                "West",  "West Northwest",  "Northwest", "North Northwest"};
            unsigned index = (unsigned)((bearing + 11.25) / 22.5) % 16;
            snprintf(out->wind_direction, sizeof(out->wind_direction), "%s", directions[index]);
        }
    }
    cJSON_Delete(root);
    return valid;
}
