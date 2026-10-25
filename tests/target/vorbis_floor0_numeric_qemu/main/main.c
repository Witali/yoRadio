// Public owned arithmetic only. Captured numbers require an independent oracle.
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_floor0.h"
#include "cases.h"

_Static_assert(sizeof(double) == 8 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024,
               "The captured bit representation requires IEEE binary64");
#if CONFIG_IDF_TARGET_ESP32
enum { worker_core = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { worker_core = 0 };
#else
#error "Unsupported arithmetic fixture target"
#endif
#define GUARD UINT64_C(0xa69c5e03f184b72d)
typedef struct { uint64_t pre; native_vorbis_scaled_t value; uint64_t post; } guarded_scaled_t;
typedef struct { uint64_t pre; native_vorbis_floor0_gain_t value; uint64_t post; } guarded_gain_t;
static struct { uint64_t pre; double value[255]; uint64_t post; } coefficients;
static uint64_t coefficient_before[255];
static struct { uint64_t pre; uint16_t value[4096]; uint64_t post; } bark_values;
static uint16_t bark_before[4096];
static unsigned api_index;

static double number(uint64_t bits) { double value; memcpy(&value, &bits, 8); return value; }
static uint64_t bits(double value) { uint64_t result; memcpy(&result, &value, 8); return result; }
static bool scaled_equal(native_vorbis_scaled_t a, native_vorbis_scaled_t b) {
    return bits(a.mantissa) == bits(b.mantissa) && a.exponent == b.exponent;
}
static bool gain_equal(native_vorbis_floor0_gain_t a, native_vorbis_floor0_gain_t b) {
    return a.kind == b.kind && scaled_equal(a.log2_gain, b.log2_gain);
}
static bool normalized(native_vorbis_scaled_t value) {
    return isfinite(value.mantissa) && (value.mantissa == 0.0 ? value.exponent == 0 :
        fabs(value.mantissa) >= 0.5 && fabs(value.mantissa) < 1.0);
}
static void stop(const char *status) {
    printf("FLOOR0_NUMERIC_STOP status=%s\n", status); fflush(stdout); esp_restart();
}
static void require(bool condition, int line) {
    if (!condition) {
        printf("FLOOR0_NUMERIC_FAILURE line=%d core=%d\n", line, xPortGetCoreID());
        stop("FAIL");
    }
}
#define REQUIRE(condition) require((condition), __LINE__)
static void api(const char *name) {
    printf("FLOOR0_NUMERIC_API index=%u name=%s ok=1 core=%d\n", api_index++, name, xPortGetCoreID());
}

static void api_checks(void) {
    double angles[3] = {0.0, 0.0, 0.0};
    double prepared[5] = {7, 7, 7, 7, 7};
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 3, prepared+1, 3) == 0);
    REQUIRE(prepared[0] == 7 && prepared[4] == 7 && prepared[1] == 2 && prepared[2] == 2 && prepared[3] == 2);
    REQUIRE(angles[0] == 0 && angles[1] == 0 && angles[2] == 0); api("prepare_valid");
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 3, angles, 3) == 0);
    REQUIRE(angles[0] == 2 && angles[1] == 2 && angles[2] == 2); api("prepare_in_place");
    angles[0] = 1.0; angles[1] = 0.0; angles[2] = NAN;
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 3, prepared+1, 3) == -1);
    REQUIRE(native_vorbis_floor0_prepare_cosines(NULL, 3, prepared+1, 3) == -1);
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 0, prepared+1, 3) == -1);
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 256, prepared+1, 3) == -1);
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 3, prepared+1, 2) == -1);
    REQUIRE(native_vorbis_floor0_prepare_cosines(angles, 3, NULL, 3) == -1);
    REQUIRE(prepared[0] == 7 && prepared[4] == 7 && prepared[1] == 2 && prepared[2] == 2 && prepared[3] == 2);
    api("prepare_invalid");
    double c = 0;
    guarded_scaled_t d = {GUARD, {0.75, 17}, GUARD};
    native_vorbis_scaled_t d_before = d.value;
    REQUIRE(native_vorbis_floor0_denominator(&c, 0, 0, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator(&c, 256, 0, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator(NULL, 1, 0, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator(&c, 1, NAN, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator(&c, 1, 3, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator(&c, 1, 0, NULL) == -1);
    c = NAN; REQUIRE(native_vorbis_floor0_denominator(&c, 1, 0, &d.value) == -1); c = 0;
    REQUIRE(d.pre == GUARD && d.post == GUARD && scaled_equal(d.value, d_before)); api("denominator_invalid");
    native_vorbis_floor0_amplitude_t amplitude = {1, 1, 1};
    guarded_gain_t g = {GUARD, {NATIVE_VORBIS_FLOOR0_INDETERMINATE, {0.75, 17}}, GUARD};
    native_vorbis_floor0_gain_t g_before = g.value;
    native_vorbis_scaled_t invalid = {0.25, 0};
    REQUIRE(native_vorbis_floor0_gain_from_denominator(NULL, &d.value, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, NULL, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &invalid, &g.value) == -1);
    amplitude.amplitude_bits = 64; REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == -1);
    amplitude.amplitude_bits = 1; amplitude.raw_amplitude = 2;
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == -1);
    amplitude.raw_amplitude = 1; amplitude.amplitude_offset = 256;
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == -1);
    REQUIRE(g.pre == GUARD && g.post == GUARD && gain_equal(g.value, g_before)); api("gain_invalid");
    amplitude = (native_vorbis_floor0_amplitude_t){0, 0, 255};
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, NULL, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_ABSENT && g.value.log2_gain.mantissa == 0 && g.value.log2_gain.exponent == 0); api("gain_absent");
    amplitude = (native_vorbis_floor0_amplitude_t){1, 1, 1}; d.value = (native_vorbis_scaled_t){0, 0};
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_POLE); api("gain_pole");
    amplitude.amplitude_offset = 0;
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_INDETERMINATE); api("gain_indeterminate");
    d.value = (native_vorbis_scaled_t){0.5, 1};
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_PRESENT && g.value.log2_gain.mantissa == 0 && g.value.log2_gain.exponent == 0); api("gain_unity");
    amplitude = (native_vorbis_floor0_amplitude_t){0, 0, 0};
    REQUIRE(native_vorbis_floor0_gain_at_cosine(&amplitude, NULL, 1, NAN, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_ABSENT); api("gain_at_cosine_absent");
    bark_values.pre = bark_values.post = GUARD;
    for (unsigned i = 0; i < 4096; ++i) bark_values.value[i] = 123;
    const uint32_t rates[] = {1, 44101, 65535};
    for (unsigned i = 0; i < 3; ++i) {
        REQUIRE(native_vorbis_floor0_bark_map(rates[i], 4096, 65535, bark_values.value, 4096) == 0);
        REQUIRE(bark_values.value[0] == 0);
        for (unsigned j = 1; j < 4096; ++j) REQUIRE(bark_values.value[j] >= bark_values.value[j-1] && bark_values.value[j] < 65535);
    }
    REQUIRE(bark_values.pre == GUARD && bark_values.post == GUARD); api("bark_valid");
    memcpy(bark_before, bark_values.value, sizeof(bark_before));
    REQUIRE(native_vorbis_floor0_bark_map(0, 4096, 65535, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(65536, 4096, 65535, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 0, 65535, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 4097, 65535, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 4096, 0, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 4096, 65536, bark_values.value, 4096) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 4096, 65535, bark_values.value, 4095) == -1);
    REQUIRE(native_vorbis_floor0_bark_map(44100, 4096, 65535, NULL, 4096) == -1);
    REQUIRE(!memcmp(bark_before, bark_values.value, sizeof(bark_before)) && bark_values.pre == GUARD && bark_values.post == GUARD); api("bark_invalid");
    double w = 3;
    REQUIRE(native_vorbis_floor0_bin_cosine(0, 6, &w) == 0 && w == 2);
    REQUIRE(native_vorbis_floor0_bin_cosine(1, 3, &w) == 0 && w == 1);
    REQUIRE(native_vorbis_floor0_bin_cosine(1, 2, &w) == 0 && w == 0);
    REQUIRE(native_vorbis_floor0_bin_cosine(2, 3, &w) == 0 && w == -1);
    REQUIRE(native_vorbis_floor0_bin_cosine(65534, 65535, &w) == 0 && isfinite(w) && w >= -2 && w <= 2); api("bin_cardinals");
    w = 3; REQUIRE(native_vorbis_floor0_bin_cosine(0, 0, &w) == -1 && w == 3);
    REQUIRE(native_vorbis_floor0_bin_cosine(0, 65536, &w) == -1 && w == 3);
    REQUIRE(native_vorbis_floor0_bin_cosine(2, 2, &w) == -1 && w == 3);
    REQUIRE(native_vorbis_floor0_bin_cosine(0, 2, NULL) == -1); api("bin_invalid");
    amplitude = (native_vorbis_floor0_amplitude_t){1, 1, 1};
    REQUIRE(native_vorbis_floor0_gain_at_bin(&amplitude, &c, 1, 1, 2, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_PRESENT && g.value.log2_gain.mantissa == 0 && g.value.log2_gain.exponent == 0); api("gain_at_bin_valid");
    g_before = g.value;
    REQUIRE(native_vorbis_floor0_gain_at_bin(&amplitude, &c, 1, 2, 2, &g.value) == -1);
    REQUIRE(gain_equal(g.value, g_before) && g.pre == GUARD && g.post == GUARD); api("gain_at_bin_invalid");
}

static void capture(uint32_t index) {
    const floor0_numeric_case_t *test = &floor0_numeric_cases[index];
    coefficients.pre = coefficients.post = GUARD;
    for (unsigned i = 0; i < 255; ++i) coefficients.value[i] = 1.25;
    for (unsigned i = 0; i < test->order; ++i) coefficients.value[i] = number(test->coefficients[i]);
    memcpy(coefficient_before, coefficients.value, sizeof(coefficient_before));
    native_vorbis_floor0_amplitude_t amplitude = {test->raw_amplitude, test->amplitude_bits, test->amplitude_offset};
    unsigned char amplitude_before[sizeof(amplitude)]; memcpy(amplitude_before, &amplitude, sizeof(amplitude));
    guarded_scaled_t d = {GUARD, {number(test->denominator_bits), test->denominator_exponent}, GUARD};
    guarded_gain_t g = {GUARD, {NATIVE_VORBIS_FLOOR0_INDETERMINATE, {0.75, 17}}, GUARD};
    native_vorbis_scaled_t d_before_gain;
    int ds = -99, gs;
    if (test->operation == 1) {
        ds = native_vorbis_floor0_denominator(coefficients.value, test->order, number(test->w_bits), &d.value);
        REQUIRE(ds == 0);
        d_before_gain = d.value;
        gs = native_vorbis_floor0_gain_at_cosine(&amplitude, coefficients.value, test->order, number(test->w_bits), &g.value);
        native_vorbis_floor0_gain_t composed;
        REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &composed) == gs);
        REQUIRE(gs == 0 && gain_equal(g.value, composed));
    } else {
        REQUIRE(test->operation == 2 && test->order == 0);
        d_before_gain = d.value;
        gs = native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &g.value);
        REQUIRE(gs == 0);
    }
    bool guards = coefficients.pre == GUARD && coefficients.post == GUARD && d.pre == GUARD && d.post == GUARD && g.pre == GUARD && g.post == GUARD;
    bool unchanged = !memcmp(coefficient_before, coefficients.value, sizeof(coefficient_before)) && !memcmp(amplitude_before, &amplitude, sizeof(amplitude)) && scaled_equal(d.value, d_before_gain);
    REQUIRE(guards && unchanged && normalized(d.value) && d.value.mantissa >= 0 && normalized(g.value.log2_gain));
    REQUIRE(g.value.kind >= NATIVE_VORBIS_FLOOR0_PRESENT && g.value.kind <= NATIVE_VORBIS_FLOOR0_INDETERMINATE);
    printf("FLOOR0_NUMERIC_CASE case=%" PRIu32 " id=%s operation=%" PRIu32 " order=%" PRIu32
           " ds=%d denominator_bits=%016" PRIx64 " denominator_exponent=%" PRId32
           " gs=%d kind=%d log2_bits=%016" PRIx64 " log2_exponent=%" PRId32
           " guards=%u unchanged=%u core=%d\n", index, test->id, test->operation, test->order, ds,
           bits(d.value.mantissa), d.value.exponent, gs, (int)g.value.kind,
           bits(g.value.log2_gain.mantissa), g.value.log2_gain.exponent, (unsigned)guards, (unsigned)unchanged, xPortGetCoreID());
}

static void worker(void *unused) {
    (void)unused;
    printf("FLOOR0_NUMERIC_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    api_checks();
    for (uint32_t i = 0; i < FLOOR0_NUMERIC_CASE_COUNT; ++i) {
        REQUIRE(xPortGetCoreID() == worker_core); capture(i);
        if ((i & 15U) == 15U) vTaskDelay(1);
    }
    printf("FLOOR0_NUMERIC_COMPLETE cases=%u api=%u core=%d\n", (unsigned)FLOOR0_NUMERIC_CASE_COUNT, api_index, xPortGetCoreID());
    stop("CAPTURED");
}

void app_main(void) {
    printf("FLOOR0_NUMERIC_BEGIN cases=%u coordinator=%d worker=%d data=%s\n", (unsigned)FLOOR0_NUMERIC_CASE_COUNT, xPortGetCoreID(), worker_core, FLOOR0_NUMERIC_CASES_SHA256);
    fflush(stdout);
    if (xTaskCreatePinnedToCore(worker, "floor0_num", 16384, NULL, 3, NULL, worker_core) != pdPASS) stop("TASK_CREATE_FAILED");
}
