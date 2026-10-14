#include "factory_ui.h"
#include "display.h"
#include "media.h"
#include "network.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

typedef struct
{
    char text[65];
    int x, y, width;
    uint16_t color;
    unsigned length, offset, pause;
    bool returning, completed;
} scrolling_label_t;

static scrolling_label_t scrolling_labels[3];

static void paint_scrolling_label(const scrolling_label_t *label)
{
    /* Erase and redraw only the label's own 24-row window at its current offset. */

    display_fill(label->x, label->y, label->width, 24, 0);
    if (label->length > (unsigned)label->width)
        display_factory_text_window(label->x, label->y, label->width, label->offset,
                                     label->text, 24, label->color, 0);
    else
    {
        int margin = (label->width - label->length) / 2;
        display_factory_text_bounded(label->x + margin, label->y, label->width - margin,
                                     label->text, 24, label->color, 0, false);
    }
}

static void scrolling_label(unsigned index, int x, int y, int width, const char *text,
                             uint16_t color, bool reset)
{
    /* Cache one field's text and restart its motion on content or theme changes.
     * REQUESTED_CHANGE: long city/description/weather labels move independently;
     * strings that fit remain centered and stationary. */

    scrolling_label_t *label = &scrolling_labels[index];
    if (reset || strcmp(text, label->text))
    {
        snprintf(label->text, sizeof(label->text), "%s", text);
        label->length = display_factory_text_width(label->text, 24);
        label->offset = 0;
        label->pause = 15;
        label->returning = false;
        label->completed = false;
    }
    label->x = x;
    label->y = y;
    label->width = width;
    label->color = color;
    paint_scrolling_label(label);
}

void factory_scroll_tick(void)
{
    /* Advance overflowing fields by two pixels per active 100-ms display loop.
     * REQUESTED_CHANGE: pause for 15 steps at each end, then reverse direction.
     * Blocking uploads/weather requests suspend drawing and therefore motion. */

    for (unsigned i = 0; i < 3; ++i)
    {
        scrolling_label_t *label = &scrolling_labels[i];
        if (label->width <= 0 || label->length <= (unsigned)label->width)
            continue;
        if (label->pause)
        {
            --label->pause;
            continue;
        }
        unsigned limit = label->length - label->width;
        if (label->returning)
            label->offset = label->offset > 2 ? label->offset - 2 : 0;
        else
            label->offset = label->offset + 2 < limit ? label->offset + 2 : limit;
        if (!label->offset || label->offset == limit)
        {
            if (!label->offset)
                label->completed = true;
            label->returning = !label->returning;
            label->pause = 15;
        }
        paint_scrolling_label(label);
    }
}

bool factory_scroll_description_ready(void)
{
    /* Permit message rotation after a long description has traveled there and back.
     * REQUESTED_CHANGE: preserve the pending rotation event until the whole label
     * has been visible; fitting labels retain the original message cadence. */

    const scrolling_label_t *label = &scrolling_labels[1];
    return label->width <= 0 || label->length <= (unsigned)label->width || label->completed;
}

static const char *weekday(int day)
{
    /* Return the three-letter factory weekday label. */

    static const char *names[] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};
    return names[day >= 0 && day < 7 ? day : 0];
}

static void date_label(const tv_settings_t *s, const struct tm *local, char out[24])
{
    /* Format the selected factory date order without padding month or day. */

    unsigned year = ((unsigned)local->tm_year + 1900) % 10000;
    unsigned month = (unsigned)local->tm_mon % 12 + 1, day = (unsigned)local->tm_mday % 32;
    if (s->date_format == 0)
        snprintf(out, 24, "%u/%u/%u", month, day, year);
    else if (s->date_format == 1)
        snprintf(out, 24, "%u/%u/%u", day, month, year);
    else
        snprintf(out, 24, "%u/%u/%u", year, month, day);
}

static int displayed_hour(const tv_settings_t *s, const struct tm *local)
{
    /* Apply the original 12-hour display rule to the local hour. */

    return s->hour12 && local->tm_hour > 12 ? local->tm_hour - 12 : local->tm_hour;
}

static bool calendar_changed(const struct tm *current, const struct tm *previous)
{
    /* Compare full dates after timezone/SNTP jumps, retaining day-of-year changes.
     * FIXED_RECONSTRUCTION: the earlier rollover fix compared only tm_yday;
     * equal day numbers in different years left the date and weekday stale. */

    return current->tm_year != previous->tm_year || current->tm_mon != previous->tm_mon ||
           current->tm_mday != previous->tm_mday || current->tm_yday != previous->tm_yday;
}

static void centered_at(int x, int width, int y, const char *text, uint16_t color)
{
    /* Center the visible prefix of a 24-pixel label within its field.
     * FIXED_FACTORY: capping the centering length alone still draws the whole
     * string; also avoid the original city's eight-bit width wraparound. */

    unsigned length = display_factory_text_width(text, 24);
    if (length > (unsigned)width)
        length = width / 12 * 12;
    int offset = (width - length) / 2;
    display_factory_text_bounded(x + offset, y, width - offset, text, 24, color, 0, false);
}

static void centered(int width, int y, const char *text, uint16_t color)
{
    /* Draw a centered factory label in a field starting at the left panel edge. */

    centered_at(0, width, y, text, color);
}

void factory_draw_setup(void)
{
    /* Draw the six original Wi-Fi setup instruction lines. */

    display_fill(0, 0, 240, 240, 0);
    centered(240, 36, "1.Open your phone", 0xffff);
    centered(240, 64, "2.Setting->WLAN", 0xffff);
    centered(240, 92, "3.Connect to wifi:", 0xffff);
    centered(240, 120, "Small_TV", 0xffe0);
    centered(240, 148, "4.Use browser link", 0xffff);
    centered(240, 176, "192.168.43.1", 0xffe0);
}

void factory_draw_startup(const char *address, unsigned progress)
{
    /* Draw the connection screen, version label and progress indicator. */

    display_fill(0, 0, 240, 240, 0);
    display_factory_symbol(20, 140, TV_SYMBOL_STARTUP_BORDER, 0xffff, 0);
    display_factory_text(120, 190, "Ver:0.0.2", 24, 0xffff, 0, false);
    display_factory_text(20, 160, "Connecting to WiFi", 24, 0x07e0, 0, false);
    if (address && address[0])
        display_factory_text(29, 114, address, 24, 0xffff, 0, false);
    if (progress > 180)
        progress = 180;
    if (progress)
        display_fill(29, 142, progress, 11, 0xffff);
    display_factory_symbol(29 + progress, 142, TV_SYMBOL_STARTUP_CAP, 0xffff, 0);
}

static double temperature(const tv_settings_t *s, double celsius)
{
    /* Apply the factory Celsius/Fahrenheit display conversion. */

    return s->fahrenheit ? celsius * 1.8 + 32 : celsius;
}

static void description_label(char out[65], const tv_settings_t *s,
                              const weather_snapshot_t *weather, const char *address, unsigned step)
{
    /* Select the next label in the ten-step weather/IP message cycle. */

    if (!weather->valid)
    {
        strcpy(out, "Getting Weather");
        return;
    }
    switch (step % 10)
    {
    case 1:
        snprintf(out, 65, "%s", weather->wind_direction);
        break;
    case 3:
        strcpy(out, "Wind Speed");
        break;
    case 4:
        snprintf(out, 65, s->miles ? "%.1fkm/h" : "%.1fmile/h",
                 (double)weather->wind_mps * (s->miles ? 3.6 : 2.24));
        break;
    case 6:
        snprintf(out, 65, "%s", weather->description);
        break;
    case 7:
        snprintf(out, 65, "Temp min %.0f%s", temperature(s, weather->temperature_min_c),
                 s->fahrenheit ? "\xa8\x48" : "\xa1\xe6");
        break;
    case 9:
        snprintf(out, 65, "Temp max %.0f%s", temperature(s, weather->temperature_max_c),
                 s->fahrenheit ? "\xa8\x48" : "\xa1\xe6");
        break;
    default:
        snprintf(out, 65, "%s", address);
        break;
    }
}

static void draw_classic_status(const tv_settings_t *s, const weather_snapshot_t *weather, bool reset)
{
    /* Redraw the city, weather title/icon and temperature/humidity fields.
     * FIXED_FACTORY: 0x4200aefc clears only y=0..23 although its city glyphs
     * occupy y=10..33. 0x4200b340 leaves old title margins and unavailable icons.
     * Clear each complete field, including partial icon output after a read error. */

    char text[65];
    display_fill(0, 0, 180, 34, 0);
    scrolling_label(0, 0, 10, 180, s->city, 0x07e0, reset);
    scrolling_label(2, 160, 83, 80, weather->valid ? weather->main : "", 0xffe0, reset);
    if (weather->valid)
    {
        if (media_draw_weather(weather->icon, 180, 10) != ESP_OK)
            display_fill(180, 10, 60, 60, 0);
    }
    else
        display_fill(180, 10, 60, 60, 0);
    media_draw_jpeg(0x3ba800, 0x3c00, 10, 180);
    media_draw_jpeg(0x3c2000, 0x3c00, 40, 186);
    media_draw_jpeg(0x3be400, 0x3c00, 12, 210);
    media_draw_jpeg(0x3c5c00, 0x3c00, 40, 216);
    display_fill(80, 180, 72, 24, 0);
    const char *unit = s->fahrenheit ? "\xa8\x48" : "\xa1\xe6";
    if (weather->valid)
        snprintf(text, sizeof(text), " %.0f%s", temperature(s, weather->temperature_c), unit);
    else
        snprintf(text, sizeof(text), " --%s", unit);
    display_factory_text_bounded(80, 180, 72, text, 24, 0xffff, 0, false);
    display_fill(80, 210, 72, 24, 0);
    if (weather->valid)
        snprintf(text, sizeof(text), " %d%%", weather->humidity);
    else
        strcpy(text, " --%");
    display_factory_text_bounded(80, 210, 72, text, 24, 0xffff, 0, false);
}

void factory_draw_classic(const tv_settings_t *s, const struct tm *local,
                          const weather_snapshot_t *weather, unsigned description_step,
                          unsigned animation_frame, bool reset, bool force_status)
{
    /* Update the classic fields selected by the original renderer at 0x4200b738.
     * FIXED_FACTORY: route status updates through complete field clearing so
     * shorter labels or missing weather cannot preserve old text/icon pixels.
     * FIXED_RECONSTRUCTION: refresh the date on complete calendar changes,
     * including a year jump at unchanged hour/minute/second and tm_yday. */

    static tv_settings_t previous_settings;
    static struct tm previous_time;
    static uint32_t previous_weather;
    static char previous_description[65];
    bool preferences = reset || memcmp(s, &previous_settings, sizeof(*s));
    bool minute = reset || local->tm_min != previous_time.tm_min ||
                  local->tm_hour != previous_time.tm_hour ||
                  calendar_changed(local, &previous_time);
    bool status = force_status || preferences || minute || weather->generation != previous_weather;
    char text[65], date[24], address[20];
    network_address(address, sizeof(address));
    description_label(text, s, weather, address, description_step);
    if (reset || strcmp(text, previous_description))
    {
        scrolling_label(1, 0, 40, 180, text, 0xffff, reset);
        strcpy(previous_description, text);
    }
    /* 0x4200afcc redraws hours/colon each second, but minutes/date only on a
     * minute or forced update. Repainting every label caused visible blanking. */
    snprintf(text, sizeof(text), "%02d", displayed_hour(s, local));
    display_factory_text(0, 80, text, 64, s->colors[0], 0, false);
    display_factory_text(64, 80, local->tm_sec & 1 ? " " : ":", 64, local->tm_sec & 1 ? 0 : 0xffff,
                         0, false);
    if (preferences || minute)
    {
        snprintf(text, sizeof(text), "%02d", local->tm_min);
        display_factory_text(96, 80, text, 64, s->colors[1], 0, false);
        display_factory_text(176, 110, weekday(local->tm_wday), 32, s->colors[2], 0, false);
        date_label(s, local, date);
        display_fill(0, 150, 120, 24, 0);
        display_factory_text_bounded(0, 150, 120, date, 24, 0xffff, 0, false);
    }
    if (status)
        draw_classic_status(s, weather, reset);
    unsigned count = media_animation_frames(s->animation);
    if (count)
        media_draw_animation(s->animation, animation_frame % count, 160, 160);
    previous_settings = *s;
    previous_time = *local;
    previous_weather = weather->generation;
}

void factory_draw_simple(const tv_settings_t *s, const struct tm *local, const char *address,
                         bool reset, bool second_update, bool minute_update)
{
    /* Update the simple clock using the factory 0x4200bd26/0x4200bd8c split.
     * FIXED_FACTORY: 0x4200bf9c repeats the date for standard Sunday (tm_wday=0);
     * render Sun instead. Also update digits on real minute/hour/date changes,
     * because 0x4200bd8c's 66-second flag leaves stale time on screen. Erase the
     * complete date band before shorter text replaces a longer date.
     * FIXED_RECONSTRUCTION: include year/month/day rather than only tm_yday. */

    static struct tm previous_time;
    static uint8_t previous_hour12, previous_date;
    bool minute = reset || minute_update || local->tm_min != previous_time.tm_min ||
                  local->tm_hour != previous_time.tm_hour ||
                  calendar_changed(local, &previous_time) || s->hour12 != previous_hour12 ||
                  s->date_format != previous_date;
    char text[24];
    if (reset)
    {
        display_fill(0, 0, 240, 240, 0);
        display_factory_symbol(0, 70, TV_SYMBOL_SIMPLE_PLATE, 0xc618, 0);
        display_factory_symbol(140, 70, TV_SYMBOL_SIMPLE_PLATE, 0xc618, 0);
        display_factory_text(5, 225, address, 16, 0xffff, 0, true);
    }
    /* The timer at 0x4200826a sets this update flag after eleven 100-ms ticks. */
    if (reset || second_update)
        display_factory_text(100, 80, local->tm_sec & 1 ? " " : ":", 80,
                             local->tm_sec & 1 ? 0 : 0xffff, 0, false);
    if (minute)
    {
        snprintf(text, sizeof(text), "%02d", displayed_hour(s, local));
        display_factory_text(10, 80, text, 80, 0xffff, 0xc618, false);
        snprintf(text, sizeof(text), "%02d", local->tm_min);
        display_factory_text(150, 80, text, 80, 0xffff, 0xc618, false);
        date_label(s, local, text);
        display_fill(0, 180, 240, 24, 0);
        centered(240, 180, text, 0xffff);
        /* 0x4200bf9c omits standard tm_wday==0 and mistakenly repeats the
         * date on Sundays. Correct this confirmed factory bug; retain 7 as
         * the factory's alternate Sunday value for compatibility. */
        snprintf(text, sizeof(text), "%s", weekday(local->tm_wday));
        display_factory_text(102, 204, text, 24, 0x07e0, 0, false);
    }
    previous_time = *local;
    previous_hour12 = s->hour12;
    previous_date = s->date_format;
}

static void circle(int x, int y, int radius, uint16_t color)
{
    /* Fill a clipped integer-radius circle for the analog hands and center cap. */

    for (int dy = -radius; dy <= radius; ++dy)
        for (int dx = -radius; dx <= radius; ++dx)
            if (dx * dx + dy * dy <= radius * radius)
                display_fill(x + dx, y + dy, 1, 1, color);
}

static void thick_line(int x0, int y0, int x1, int y1, unsigned width, uint16_t color)
{
    /* Draw the parallel strokes used by the factory analog clock.
     * FIXED_FACTORY: 0x42009644 swaps sin/cos after rotating by pi/2, collapsing
     * axis-aligned thick strokes. Use the perpendicular cos/sin offset pair. */

    /* Retain the float narrowing and rounding at 0x42009644, but correct
     * its swapped sin/cos offsets: after adding pi/2, cos/sin moves strokes
     * perpendicular to the line. The vendor bug collapses axis-aligned
     * thick strokes into overlapping one-pixel lines. */
    double angle = (float)atan2(y1 - y0, x1 - x0) + 1.5707963267948966;
    for (int offset = -(int)(width / 2); offset <= (int)(width / 2); ++offset)
    {
        int dx = (int)round(offset * cos(angle)), dy = (int)round(offset * sin(angle));
        display_line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, color);
    }
}

static void hand(double angle, int radius, unsigned width, uint16_t color)
{
    /* Draw one analog hand and its rounded outer endpoint. */

    int x = (int)(120 + radius * sin(angle)), y = (int)(120 - radius * cos(angle));
    thick_line(120, 120, x, y, width, color);
    if (width > 2)
        circle(x, y, width / 2, color);
}

void factory_draw_dial(const struct tm *local, const char *address, bool reset)
{
    /* Initialize the dial or erase/move its hands as the factory renderer does. */

    static float previous[3];
    const double pi = 3.141592653589793;
    const int radii[] = {50, 70, 90};
    const uint16_t colors[] = {0xf800, 0xffe0, 0xffff};
    const unsigned widths[] = {5, 5, 3};
    float angles[] = {((float)(local->tm_hour % 12) + (float)local->tm_min / 60.0f) * pi / 6,
                      ((float)local->tm_min + (float)local->tm_sec / 60.0f) * pi / 30,
                      local->tm_sec * pi / 30};
    if (reset)
    {
        display_fill(0, 0, 240, 240, 0);
        for (unsigned hour = 0; hour < 12; ++hour)
        {
            if (hour % 3 == 0)
                continue;
            /* 0x42009b32 narrows each tick angle to float before sin/cos. */
            double angle = (float)(hour * pi / 6);
            thick_line((int)(120 + 105 * sin(angle)), (int)(120 - 105 * cos(angle)),
                       (int)(120 + 120 * sin(angle)), (int)(120 - 120 * cos(angle)), 4, 0xffff);
        }
    }
    else
    {
        /* Stock erases only hands whose integer endpoints changed, using a
         * five-stroke black brush even for the narrow second hand. It does not
         * repaint the dial marks under them on every tick. */
        for (unsigned i = 0; i < 3; ++i)
            if ((int)(120 + radii[i] * sin(previous[i])) !=
                    (int)(120 + radii[i] * sin(angles[i])) ||
                (int)(120 - radii[i] * cos(previous[i])) != (int)(120 - radii[i] * cos(angles[i])))
                hand(previous[i], radii[i], 5, 0);
    }
    for (unsigned i = 0; i < 3; ++i)
    {
        hand(angles[i], radii[i], widths[i], colors[i]);
        previous[i] = angles[i];
    }
    if (!reset)
        circle(120, 120, 6, 0xffff);
    if (reset)
    {
        display_factory_text(104, 0, "12", 32, 0xffff, 0, false);
        display_factory_text(0, 104, "9", 32, 0xffff, 0, false);
        display_factory_text(224, 104, "3", 32, 0xffff, 0, false);
        display_factory_text(104, 208, "6", 32, 0xffff, 0, false);
    }
    display_factory_text(5, 225, address, 16, 0xffff, 0, true);
}

void factory_draw_photo(unsigned slot, const char *address)
{
    /* Draw one full-screen photo and the original transparent IP footer. */

    display_fill(0, 0, 240, 240, 0);
    media_draw_photo(slot);
    display_factory_text(5, 225, address, 16, 0xffff, 0, true);
}
