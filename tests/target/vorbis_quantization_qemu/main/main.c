// Capture original packed fields, exact affine VQ values and optional floor math.
#include <assert.h>
#include <float.h>
#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "native_vorbis_quant.h"
#include "cases.h"
#ifdef NDEBUG
#error "The copied owned API controls require active assertions"
#endif
_Static_assert(sizeof(double) == 8 && DBL_MANT_DIG == 53 && DBL_MAX_EXP == 1024,
               "Exact IEEE binary64 output capture required");
_Static_assert(sizeof(native_vorbis_affine_t) == 16, "Four exact uint32 fields required");
#include "controls.h"
#if CONFIG_IDF_TARGET_ESP32
enum { worker_core = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { worker_core = 0 };
#else
#error "Unsupported quantization fixture target"
#endif
enum { CAPACITY = 255, PACKET_CAPACITY = 1024 };
static struct { uint64_t pre; uint8_t value[PACKET_CAPACITY]; uint64_t post; } packet;
static struct { uint64_t pre; uint32_t value[CAPACITY+1]; uint64_t post; } entries;
static struct { uint64_t pre; uint16_t value[CAPACITY+1]; uint64_t post; } storage;
static struct { uint64_t pre; native_vorbis_affine_t value[CAPACITY+1]; uint64_t post; } values;
static uint8_t packet_before[PACKET_CAPACITY];
static uint32_t entries_before[CAPACITY+1];
static uint16_t storage_before[CAPACITY+1];
static native_vorbis_affine_t values_before[CAPACITY+1];
static char hex_buffer[32*CAPACITY+1];
typedef struct { uint64_t pre; native_vorbis_quant_layout_t value; uint64_t post; } guarded_layout_t;
typedef struct { uint64_t pre; native_vorbis_quantization_t value; uint64_t post; } guarded_book_t;
typedef struct { uint64_t pre; native_vorbis_scaled_t value; uint64_t post; } guarded_scaled_t;
typedef struct { uint64_t pre; native_vorbis_floor0_gain_t value; uint64_t post; } guarded_gain_t;

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
    printf("QUANTIZATION_STOP status=%s\n", status); fflush(stdout); esp_restart();
}
static void require(bool condition, int line) {
    if (!condition) { printf("QUANTIZATION_FAILURE line=%d core=%d\n", line, xPortGetCoreID()); stop("FAIL"); }
}
#define REQUIRE(condition) require((condition), __LINE__)
static void hex_word(char *out, uint32_t value, unsigned digits) {
    static const char table[] = "0123456789abcdef";
    for (unsigned i = 0; i < digits; ++i) out[i] = table[(value >> (4*(digits-1-i))) & 15U];
}
static bool same_layout(const native_vorbis_quant_layout_t *a, const native_vorbis_quant_layout_t *b) {
    return a->dimensions == b->dimensions && a->entries == b->entries && a->lookup_type == b->lookup_type &&
        a->minimum_bits == b->minimum_bits && a->delta_bits == b->delta_bits && a->value_bits == b->value_bits &&
        a->sequence_p == b->sequence_p && a->multiplicand_count == b->multiplicand_count &&
        a->start_bit == b->start_bit && a->multiplicand_bit == b->multiplicand_bit && a->end_bit == b->end_bit;
}
static void capture(uint32_t index) {
    const quantization_case_t *test = &quantization_cases[index];
    REQUIRE(test->packet_bytes <= PACKET_CAPACITY && test->entry_count <= CAPACITY && test->length <= CAPACITY);
    packet.pre = packet.post = entries.pre = entries.post = storage.pre = storage.post = values.pre = values.post = CANARY;
    memset(packet.value, 0xa5, sizeof(packet.value)); memset(entries.value, 0xa5, sizeof(entries.value));
    memset(storage.value, 0xa5, sizeof(storage.value)); memset(values.value, 0xa5, sizeof(values.value));
    if (test->packet_bytes) memcpy(packet.value, test->packet, test->packet_bytes);
    if (test->entry_count) memcpy(entries.value, test->entry_numbers, test->entry_count*sizeof(uint32_t));
    memcpy(packet_before, packet.value, sizeof(packet_before)); memcpy(entries_before, entries.value, sizeof(entries_before));
    guarded_layout_t layout = {.pre=CANARY, .post=CANARY};
    guarded_book_t book = {.pre=CANARY, .post=CANARY};
    int measured = -99, materialized = -99, decoded = -99;
    if (test->operation != 3) {
        measured = native_vorbis_quantization_measure(packet.value, test->packet_bytes, test->packet_bits,
            test->start_bit, test->dimensions, test->entries, &layout.value);
        REQUIRE(measured == 0 && layout.value.multiplicand_count <= CAPACITY);
        materialized = native_vorbis_quantization_materialize(packet.value, test->packet_bytes,
            test->packet_bits, &layout.value, storage.value, CAPACITY, &book.value);
        REQUIRE(materialized == 0 && same_layout(&layout.value, &book.value.layout));
    }
    unsigned char layout_before[sizeof(layout.value)], book_before[sizeof(book.value)];
    memcpy(layout_before, &layout.value, sizeof(layout.value)); memcpy(book_before, &book.value, sizeof(book.value));
    memcpy(storage_before, storage.value, sizeof(storage_before));
    if (test->operation == 1) {
        REQUIRE(test->entry_count == 1);
        decoded = native_vorbis_quantization_vector(&book.value, entries.value[0], test->length, values.value, CAPACITY);
    } else if (test->operation == 2) {
        decoded = native_vorbis_floor0_lsp_from_entries(&book.value, entries.value, test->entry_count, test->length, values.value, CAPACITY);
    } else if (test->operation == 3) {
        REQUIRE(test->affine_count == test->length);
        if (test->length) memcpy(values.value, test->affine, test->length*sizeof(native_vorbis_affine_t));
    } else {
        REQUIRE(test->operation == 4 && test->entry_count == 1 && test->length == 1);
        decoded = native_vorbis_quantization_scalar(&book.value, entries.value[0], test->component, &values.value[0]);
    }
    REQUIRE(test->operation == 3 ? decoded == -99 : decoded == 0);
    for (size_t i = test->length; i <= CAPACITY; ++i) {
        REQUIRE(values.value[i].minimum_bits == UINT32_C(0xa5a5a5a5) && values.value[i].delta_bits == UINT32_C(0xa5a5a5a5) &&
            values.value[i].minimum_multiplier == UINT32_C(0xa5a5a5a5) && values.value[i].delta_multiplier == UINT32_C(0xa5a5a5a5));
    }
    if (test->operation != 3) for (size_t i = (size_t)layout.value.multiplicand_count; i <= CAPACITY; ++i) REQUIRE(storage.value[i] == UINT16_C(0xa5a5));
    memcpy(values_before, values.value, sizeof(values_before));
    guarded_scaled_t d = {.pre=CANARY, .post=CANARY};
    guarded_gain_t g = {.pre=CANARY, .post=CANARY}, composed = {.pre=CANARY, .post=CANARY};
    native_vorbis_floor0_amplitude_t amplitude = {test->raw_amplitude, test->amplitude_bits, test->amplitude_offset};
    unsigned char amplitude_before[sizeof(amplitude)]; memcpy(amplitude_before, &amplitude, sizeof(amplitude));
    int ds=-99, gs=-99, kind=-99;
    if (test->bridge) {
        REQUIRE(test->length >= 1);
        ds = native_vorbis_floor0_denominator_from_affine(values.value, test->length, test->bin, test->map_size, &d.value);
        REQUIRE(ds == 0);
        native_vorbis_scaled_t d_before = d.value;
        gs = native_vorbis_floor0_gain_from_affine(&amplitude, values.value, test->length, test->bin, test->map_size, &g.value);
        REQUIRE(gs == 0 && native_vorbis_floor0_gain_from_denominator(&amplitude, &d.value, &composed.value) == gs);
        REQUIRE(gain_equal(g.value, composed.value) && scaled_equal(d.value, d_before));
        REQUIRE(normalized(d.value) && d.value.mantissa >= 0 && normalized(g.value.log2_gain));
        kind = (int)g.value.kind; REQUIRE(kind >= 0 && kind <= 3);
    }
    bool guards = packet.pre == CANARY && packet.post == CANARY && entries.pre == CANARY && entries.post == CANARY &&
        storage.pre == CANARY && storage.post == CANARY && values.pre == CANARY && values.post == CANARY &&
        layout.pre == CANARY && layout.post == CANARY && book.pre == CANARY && book.post == CANARY &&
        d.pre == CANARY && d.post == CANARY && g.pre == CANARY && g.post == CANARY && composed.pre == CANARY && composed.post == CANARY;
    bool unchanged = !memcmp(packet_before, packet.value, sizeof(packet_before)) && !memcmp(entries_before, entries.value, sizeof(entries_before)) &&
        !memcmp(layout_before, &layout.value, sizeof(layout.value)) && !memcmp(book_before, &book.value, sizeof(book.value)) &&
        !memcmp(storage_before, storage.value, sizeof(storage_before)) && !memcmp(values_before, values.value, sizeof(values_before)) &&
        !memcmp(amplitude_before, &amplitude, sizeof(amplitude));
    REQUIRE(guards && unchanged);
    printf("QUANTIZATION_CASE case=%" PRIu32 " id=%s operation=%" PRIu32 " length=%" PRIu32 " bridge=%" PRIu32
        " measure_status=%d materialize_status=%d decode_status=%d core=%d\n", index, test->id, test->operation,
        test->length, test->bridge, measured, materialized, decoded, xPortGetCoreID());
    if (test->operation != 3) {
        const native_vorbis_quant_layout_t *l = &layout.value;
        printf("QUANTIZATION_LAYOUT case=%" PRIu32 " dimensions=%" PRIu32 " entries=%" PRIu32 " lookup_type=%" PRIu32
            " minimum_bits=%08" PRIx32 " delta_bits=%08" PRIx32 " value_bits=%" PRIu32 " sequence_p=%" PRIu32
            " multiplicand_count=%" PRIu64 " start_bit=%" PRIu64 " multiplicand_bit=%" PRIu64 " end_bit=%" PRIu64 " core=%d\n",
            index,l->dimensions,l->entries,l->lookup_type,l->minimum_bits,l->delta_bits,l->value_bits,l->sequence_p,
            l->multiplicand_count,l->start_bit,l->multiplicand_bit,l->end_bit,xPortGetCoreID());
        size_t count = (size_t)l->multiplicand_count;
        for (size_t i = 0; i < count; ++i) hex_word(hex_buffer+4*i, storage.value[i], 4);
        hex_buffer[4*count] = 0;
        printf("QUANTIZATION_MULT case=%" PRIu32 " count=%u hex=%s core=%d\n", index, (unsigned)count, count ? hex_buffer : "-", xPortGetCoreID());
    }
    for (size_t i = 0; i < test->length; ++i) {
        native_vorbis_affine_t value = values.value[i];
        hex_word(hex_buffer+32*i, value.minimum_bits, 8); hex_word(hex_buffer+32*i+8, value.delta_bits, 8);
        hex_word(hex_buffer+32*i+16, value.minimum_multiplier, 8); hex_word(hex_buffer+32*i+24, value.delta_multiplier, 8);
    }
    hex_buffer[32*test->length] = 0;
    printf("QUANTIZATION_VALUES case=%" PRIu32 " count=%" PRIu32 " hex=%s core=%d\n", index, test->length, test->length ? hex_buffer : "-", xPortGetCoreID());
    printf("QUANTIZATION_MATH case=%" PRIu32 " ds=%d denominator_bits=%016" PRIx64 " denominator_exponent=%" PRId32
        " gs=%d kind=%d log2_bits=%016" PRIx64 " log2_exponent=%" PRId32 " core=%d\n", index, ds,
        bits(d.value.mantissa), d.value.exponent, gs, kind, bits(g.value.log2_gain.mantissa), g.value.log2_gain.exponent, xPortGetCoreID());
    printf("QUANTIZATION_END case=%" PRIu32 " guards=%u unchanged=%u core=%d\n", index, (unsigned)guards, (unsigned)unchanged, xPortGetCoreID());
}
static void worker(void *unused) {
    (void)unused;
    printf("QUANTIZATION_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    unsigned checked = controls(); REQUIRE(checked == 152);
    printf("QUANTIZATION_CONTROLS checks=%u core=%d\n", checked, xPortGetCoreID());
    for (uint32_t i = 0; i < QUANTIZATION_CASE_COUNT; ++i) {
        REQUIRE(xPortGetCoreID() == worker_core); capture(i); if ((i & 15U) == 15U) vTaskDelay(1);
    }
    printf("QUANTIZATION_COMPLETE cases=%u controls=%u core=%d\n", (unsigned)QUANTIZATION_CASE_COUNT, checked, xPortGetCoreID()); stop("CAPTURED");
}
void app_main(void) {
    printf("QUANTIZATION_BEGIN cases=%u coordinator=%d worker=%d data=%s\n", (unsigned)QUANTIZATION_CASE_COUNT,
        xPortGetCoreID(),worker_core,QUANTIZATION_CASES_SHA256); fflush(stdout);
    if (xTaskCreatePinnedToCore(worker,"quantization",16384,NULL,3,NULL,worker_core) != pdPASS) stop("TASK_CREATE_FAILED");
}
