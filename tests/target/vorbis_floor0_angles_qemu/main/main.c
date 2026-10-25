// Original finite-angle inputs, not rounded cosine coefficients.
// Captured values require a separate independent numerical comparison.
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
#error "Unsupported original-angle fixture target"
#endif
#define GUARD UINT64_C(0xa69c5e03f184b72d)
typedef struct { uint64_t pre; native_vorbis_scaled_t value; uint64_t post; } guarded_scaled_t;
typedef struct { uint64_t pre; native_vorbis_floor0_gain_t value; uint64_t post; } guarded_gain_t;
static struct { uint64_t pre; double value[255]; uint64_t post; } angles;
static uint64_t angle_before[255];
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
    printf("FLOOR0_ANGLES_STOP status=%s\n", status); fflush(stdout); esp_restart();
}
static void require(bool condition, int line) {
    if (!condition) {
        printf("FLOOR0_ANGLES_FAILURE line=%d core=%d\n", line, xPortGetCoreID()); stop("FAIL");
    }
}
#define REQUIRE(condition) require((condition), __LINE__)
static void api(const char *name) {
    printf("FLOOR0_ANGLES_API index=%u name=%s ok=1 core=%d\n", api_index++, name, xPortGetCoreID());
}

static void api_checks(void) {
    angles.pre = angles.post = GUARD;
    for (unsigned i = 0; i < 255; ++i) angles.value[i] = 0.0;
    guarded_scaled_t d = {GUARD, {0.75, 17}, GUARD};
    guarded_gain_t g = {GUARD, {NATIVE_VORBIS_FLOOR0_INDETERMINATE, {0.75, 17}}, GUARD};
    native_vorbis_floor0_amplitude_t amplitude = {1, 1, 1};
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 1, 2, &d.value) == 0);
    REQUIRE(normalized(d.value) && d.value.mantissa > 0 && d.pre == GUARD && d.post == GUARD);
    api("denominator_unit");
    native_vorbis_scaled_t d_before = d.value;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 1, 2, &g.value) == 0);
    guarded_gain_t composed = {GUARD, {NATIVE_VORBIS_FLOOR0_ABSENT, {0, 0}}, GUARD};
    REQUIRE(native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &composed.value) == 0);
    REQUIRE(gain_equal(g.value, composed.value) && scaled_equal(d.value, d_before));
    REQUIRE(g.pre == GUARD && g.post == GUARD && composed.pre == GUARD && composed.post == GUARD);
    api("gain_composition");
    double tiny_angle = 1e-12, rounded;
    native_vorbis_scaled_t rounded_d;
    REQUIRE(native_vorbis_floor0_prepare_cosines(&tiny_angle, 1, &rounded, 1) == 0 && rounded == 2.0);
    REQUIRE(native_vorbis_floor0_denominator(&rounded, 1, 2.0, &rounded_d) == 0 && rounded_d.mantissa == 0);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(&tiny_angle, 1, 0, 6, &d.value) == 0);
    REQUIRE(normalized(d.value) && d.value.mantissa > 0 && d.value.exponent < 0);
    REQUIRE(tiny_angle == 1e-12); api("tiny_angles_survive_rounding");
    angles.value[0] = DBL_MAX; angles.value[1] = -DBL_MAX;
    angles.value[2] = 0.0; angles.value[3] = -0.0;
    angles.value[4] = number(UINT64_C(1)); angles.value[5] = number(UINT64_C(0x8000000000000001));
    memcpy(angle_before, angles.value, sizeof(angle_before));
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 6, 1, 3, &d.value) == 0);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 6, 1, 3, &g.value) == 0);
    REQUIRE(normalized(d.value) && d.value.mantissa >= 0 && normalized(g.value.log2_gain));
    REQUIRE(!memcmp(angle_before, angles.value, sizeof(angle_before)) && angles.pre == GUARD && angles.post == GUARD);
    api("full_finite_inputs");
    angles.value[0] = 0;
    d.value = (native_vorbis_scaled_t){0.75, 17}; d_before = d.value;
    REQUIRE(native_vorbis_floor0_denominator_at_bin(NULL, 1, 0, 1, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 0, 1, NULL) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 0, 0, 1, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 256, 0, 1, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 0, 0, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 0, 65536, &d.value) == -1);
    REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 1, 1, &d.value) == -1);
    angles.value[0] = NAN; REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 0, 1, &d.value) == -1);
    angles.value[0] = INFINITY; REQUIRE(native_vorbis_floor0_denominator_at_bin(angles.value, 1, 0, 1, &d.value) == -1);
    REQUIRE(scaled_equal(d.value, d_before) && d.pre == GUARD && d.post == GUARD); api("denominator_invalid");
    g.value = (native_vorbis_floor0_gain_t){NATIVE_VORBIS_FLOOR0_INDETERMINATE, {0.75, 17}};
    native_vorbis_floor0_gain_t g_before = g.value;
    angles.value[0] = 0;
    REQUIRE(native_vorbis_floor0_gain_from_angles(NULL, angles.value, 1, 0, 1, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 1, NULL) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, NULL, 1, 0, 1, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 0, 0, 1, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 256, 0, 1, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 1, 1, &g.value) == -1);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 65536, &g.value) == -1);
    amplitude.amplitude_bits = 64;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 1, &g.value) == -1);
    amplitude.amplitude_bits = 1; amplitude.raw_amplitude = 2;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 1, &g.value) == -1);
    amplitude.raw_amplitude = 1; amplitude.amplitude_offset = 256;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 1, &g.value) == -1);
    amplitude.amplitude_offset = 1; angles.value[0] = NAN;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 1, &g.value) == -1);
    REQUIRE(gain_equal(g.value, g_before) && g.pre == GUARD && g.post == GUARD); api("gain_invalid");
    amplitude = (native_vorbis_floor0_amplitude_t){0, 0, 255};
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, NULL, 1, 0, 3, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_ABSENT && g.value.log2_gain.mantissa == 0 && g.value.log2_gain.exponent == 0);
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 3, &g.value) == 0);
    angles.value[0] = 0; amplitude = (native_vorbis_floor0_amplitude_t){1, 1, 1};
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 3, &g.value) == 0 && g.value.kind == NATIVE_VORBIS_FLOOR0_POLE);
    amplitude.amplitude_offset = 0;
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 0, 3, &g.value) == 0 && g.value.kind == NATIVE_VORBIS_FLOOR0_INDETERMINATE);
    api("absent_pole_indeterminate");
    REQUIRE(native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, 1, 1, 2, &g.value) == 0);
    REQUIRE(g.value.kind == NATIVE_VORBIS_FLOOR0_PRESENT && g.value.log2_gain.mantissa == 0 && g.value.log2_gain.exponent == 0);
    api("zero_offset_unity");
}

static void capture(uint32_t index) {
    const floor0_angles_case_t *test = &floor0_angles_cases[index];
    angles.pre = angles.post = GUARD;
    for (unsigned i = 0; i < 255; ++i) angles.value[i] = 1.25;
    for (unsigned i = 0; i < test->order; ++i) angles.value[i] = number(test->angles[i]);
    memcpy(angle_before, angles.value, sizeof(angle_before));
    native_vorbis_floor0_amplitude_t amplitude = {test->raw_amplitude, test->amplitude_bits, test->amplitude_offset};
    unsigned char amplitude_before[sizeof(amplitude)]; memcpy(amplitude_before, &amplitude, sizeof(amplitude));
    guarded_scaled_t d = {GUARD, {0.75, 17}, GUARD};
    guarded_gain_t g = {GUARD, {NATIVE_VORBIS_FLOOR0_INDETERMINATE, {0.75, 17}}, GUARD};
    guarded_gain_t composed = {GUARD, {NATIVE_VORBIS_FLOOR0_ABSENT, {0, 0}}, GUARD};
    int ds = native_vorbis_floor0_denominator_at_bin(angles.value, test->order, test->bin, test->map_size, &d.value);
    REQUIRE(ds == 0);
    native_vorbis_scaled_t d_before = d.value;
    int gs = native_vorbis_floor0_gain_from_angles(&amplitude, angles.value, test->order, test->bin, test->map_size, &g.value);
    REQUIRE(gs == 0 && native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &composed.value) == gs);
    REQUIRE(gain_equal(g.value, composed.value));
    bool guards = angles.pre == GUARD && angles.post == GUARD && d.pre == GUARD && d.post == GUARD &&
        g.pre == GUARD && g.post == GUARD && composed.pre == GUARD && composed.post == GUARD;
    bool unchanged = !memcmp(angle_before, angles.value, sizeof(angle_before)) &&
        !memcmp(amplitude_before, &amplitude, sizeof(amplitude)) && scaled_equal(d.value, d_before);
    REQUIRE(guards && unchanged && normalized(d.value) && d.value.mantissa >= 0 && normalized(g.value.log2_gain));
    REQUIRE(g.value.kind >= NATIVE_VORBIS_FLOOR0_PRESENT && g.value.kind <= NATIVE_VORBIS_FLOOR0_INDETERMINATE);
    printf("FLOOR0_ANGLES_CASE case=%" PRIu32 " id=%s order=%" PRIu32 " bin=%" PRIu32 " map_size=%" PRIu32
           " ds=%d denominator_bits=%016" PRIx64 " denominator_exponent=%" PRId32
           " gs=%d kind=%d log2_bits=%016" PRIx64 " log2_exponent=%" PRId32
           " guards=%u unchanged=%u core=%d\n", index, test->id, test->order, test->bin, test->map_size,
           ds, bits(d.value.mantissa), d.value.exponent, gs, (int)g.value.kind,
           bits(g.value.log2_gain.mantissa), g.value.log2_gain.exponent, (unsigned)guards, (unsigned)unchanged, xPortGetCoreID());
}

static void worker(void *unused) {
    (void)unused;
    printf("FLOOR0_ANGLES_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    api_checks();
    for (uint32_t i = 0; i < FLOOR0_ANGLES_CASE_COUNT; ++i) {
        REQUIRE(xPortGetCoreID() == worker_core); capture(i);
        if ((i & 15U) == 15U) vTaskDelay(1);
    }
    printf("FLOOR0_ANGLES_COMPLETE cases=%u api=%u core=%d\n", (unsigned)FLOOR0_ANGLES_CASE_COUNT, api_index, xPortGetCoreID());
    stop("CAPTURED");
}

void app_main(void) {
    printf("FLOOR0_ANGLES_BEGIN cases=%u coordinator=%d worker=%d data=%s\n", (unsigned)FLOOR0_ANGLES_CASE_COUNT,
           xPortGetCoreID(), worker_core, FLOOR0_ANGLES_CASES_SHA256); fflush(stdout);
    if (xTaskCreatePinnedToCore(worker, "floor0_angles", 16384, NULL, 3, NULL, worker_core) != pdPASS) stop("TASK_CREATE_FAILED");
}
