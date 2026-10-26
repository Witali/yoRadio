// Reuse only the unchanged generic fixture's guarded refusal helpers.
#define main floor1_host_fixture_main_not_executed
#include "host-fixture.c"
#undef main
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "cases.h"

#ifdef NDEBUG
#error "Native product qualification requires active assertions"
#endif
#if CONFIG_IDF_TARGET_ESP32
enum { WORKER_CORE = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { WORKER_CORE = 0 };
#else
#error "Unsupported target"
#endif

static uint8_t index_at(const f1_case_t *test, uint32_t bin) {
    uint32_t original = test->offset + test->step * bin;
    switch (test->index_kind) {
        case 0: return (uint8_t)(original / 2);
        case 1: return (uint8_t)(original / 7);
        case 2: return (uint8_t)test->constant;
        case 3: return test->indices[original];
        default: CHECK(false); return 0;
    }
}

static void negate(uint32_t *words, uint32_t count) {
    uint64_t carry = 1;
    for (uint32_t i = 0; i < count; ++i) {
        uint64_t value = (uint64_t)(~words[i]) + carry;
        words[i] = (uint32_t)value; carry = value >> 32;
    }
}

static void maximum(uint32_t *words, uint32_t limbs, uint32_t bits) {
    for (uint32_t i = 0; i < limbs; ++i) {
        uint32_t bottom = i * 32;
        words[i] = bottom >= bits ? 0 : bits - bottom >= 32 ? UINT32_MAX :
            (UINT32_C(1) << (bits - bottom)) - 1;
    }
}

static void random_pattern(uint32_t *words, uint32_t limbs, uint32_t width, uint32_t bin) {
    // The test witness is ((bin+1)*K*2^max(width-64,0)+C) mod2^width.
    uint64_t low = (uint64_t)(bin + 1) * UINT32_C(0x7f4a7c15);
    uint64_t high = (uint64_t)(bin + 1) * UINT32_C(0x9e3779b9) + (low >> 32);
    uint32_t product[3] = {(uint32_t)low, (uint32_t)high, (uint32_t)(high >> 32)};
    uint32_t shift = width > 64 ? width - 64 : 0;
    uint32_t word_shift = shift / 32, bit_shift = shift % 32;
    memset(words, 0, limbs * sizeof(*words));
    for (uint32_t i = 0; i < 3; ++i) {
        if (i + word_shift < limbs) words[i + word_shift] |= product[i] << bit_shift;
        if (bit_shift && i + word_shift + 1 < limbs)
            words[i + word_shift + 1] |= product[i] >> (32 - bit_shift);
    }
    const uint32_t constant[2] = {UINT32_C(0x89abcdef), UINT32_C(0x01234567)};
    uint64_t carry = 0;
    for (uint32_t i = 0; i < limbs; ++i) {
        uint64_t value = (uint64_t)words[i] + (i < 2 ? constant[i] : 0) + carry;
        words[i] = (uint32_t)value; carry = value >> 32;
    }
    uint32_t last = width / 32, remainder = width % 32;
    if (remainder) words[last] &= (UINT32_C(1) << remainder) - 1;
    else words[last] = 0;
    for (uint32_t i = last + 1; i < limbs; ++i) words[i] = 0;
    negate(words, limbs);
}

static void source_sample(const f1_case_t *test, uint32_t bin, uint32_t channel,
                          uint32_t *words, uint32_t limbs) {
    memset(words, 0, limbs * sizeof(*words));
    if (!limbs) return;
    if (channel != test->channel) {
        words[0] = 1;
        if (channel & 1) negate(words, limbs);
        return;
    }
    uint32_t original = test->offset + test->step * bin;
    if (test->pattern == 2) { words[0] = 1; return; }
    if (test->pattern == 3 && original == test->original_bins - 1) {
        words[test->width / 32] = UINT32_C(1) << (test->width % 32);
        if (test->invalid_sign < 0) negate(words, limbs);
        return;
    }
    if (test->pattern == 0) {
        maximum(words, limbs, test->width);
        if (original & 1) negate(words, limbs);
        return;
    }
    switch (original % 7) {
        case 0: break;
        case 1: words[0] = 1; break;
        case 2: words[0] = 1; negate(words, limbs); break;
        case 3: maximum(words, limbs, test->width); break;
        case 4: maximum(words, limbs, test->width); negate(words, limbs); break;
        case 5: maximum(words, limbs, test->width - 1); break;
        case 6: random_pattern(words, limbs, test->width, original); break;
        default: CHECK(false);
    }
}

static void emit_words(uint32_t row, const uint32_t *words, uint32_t count) {
    enum { CHUNK = 128 };
    char runs[2048];
    uint32_t start = 0;
    do {
        uint32_t n = count - start;
        if (n > CHUNK) n = CHUNK;
        size_t at = 0;
        for (uint32_t i = 0; i < n;) {
            uint32_t length = 1;
            while (i + length < n && words[start + i + length] == words[start + i]) ++length;
            int written = snprintf(runs + at, sizeof(runs) - at, "%s%08" PRIx32 ":%" PRIu32,
                i ? "," : "", words[start + i], length);
            CHECK(written > 0 && (size_t)written < sizeof(runs) - at);
            at += (size_t)written; i += length;
        }
        if (!n) { runs[0] = '-'; runs[1] = 0; }
        printf("F1_WORDS row=%" PRIu32 " start=%" PRIu32 " total=%" PRIu32
            " count=%" PRIu32 " runs=%s core=%d\n", row, start, count, n, runs, xPortGetCoreID());
        start += n;
        // This new standalone fixture yields at every bounded output chunk.
        vTaskDelay(1);
    } while (start < count);
}

static void capture(uint32_t row) {
    const f1_case_t *test = &f1_cases[row];
    uint64_t before_checks = checks, before_refusals = refusals;
    native_vorbis_residue_layout_t source = {.mapping=UINT32_MAX,
        .bins=test->bins, .channels=test->channels,
        .limbs=test->width ? (test->width + 32) / 32 : 0,
        .magnitude_bits=test->width, .exponent=test->exponent,
        .classification_count=UINT64_MAX};
    source.sample_count = (uint64_t)source.bins * source.channels;
    source.limb_count = source.sample_count * source.limbs;
    unsigned char source_before[sizeof(source)]; memcpy(source_before, &source, sizeof(source));
    size_t source_count = (size_t)source.limb_count;
    size_t max_output = source.limbs ? (size_t)source.bins * 36 : 0;
    uint32_t *input = malloc((source_count + 2) * sizeof(*input));
    uint32_t *output = malloc((max_output + 2) * sizeof(*output));
    uint8_t *indices = malloc(source.bins + 2);
    CHECK(input && output && indices);
    input[0] = output[0] = UINT32_C(0x13579bdf);
    input[source_count + 1] = output[max_output + 1] = UINT32_C(0x2468ace0);
    indices[0] = 0x37; indices[source.bins + 1] = 0xb9;
    for (uint32_t bin = 0; bin < source.bins; ++bin) indices[bin + 1] = index_at(test, bin);
    for (uint32_t channel = 0; source.limbs && channel < source.channels; ++channel)
        for (uint32_t bin = 0; bin < source.bins; ++bin)
            source_sample(test, bin, channel,
                input + 1 + ((size_t)channel * source.bins + bin) * source.limbs, source.limbs);
    for (size_t i = 0; i < max_output; ++i) output[i + 1] = UINT32_C(0xa5a5a5a5);
    native_vorbis_floor1_product_layout_t layout;
    unsigned char layout_before[sizeof(layout)]; memset(&layout, 0x5a, sizeof(layout));
    memcpy(layout_before, &layout, sizeof(layout));
    const uint8_t *curve = source.limbs ? indices + 1 : NULL;
    int measured = native_vorbis_floor1_scale_measure(&source, curve, source.bins, &layout);
    if (measured) CHECK(!memcmp(layout_before, &layout, sizeof(layout)));
    native_vorbis_floor1_product_t product;
    unsigned char product_before[sizeof(product)]; memset(&product, 0x5a, sizeof(product));
    memcpy(product_before, &product, sizeof(product));
    size_t capacity = measured ? max_output : (size_t)layout.limb_count;
    int status = native_vorbis_floor1_scale(&source, source.limbs ? input + 1 : NULL,
        source_count, test->channel, curve, source.bins, source.limbs ? output + 1 : NULL,
        capacity, &product);
    printf("F1_CASE row=%" PRIu32 " id=%s measure=%d product=%d core=%d\n",
        row, test->id, measured, status, xPortGetCoreID());
    uint32_t used = 0;
    if (!status) {
        CHECK(!measured && same_layout(&layout, &product.layout));
        CHECK(product.samples == (source.limbs ? output + 1 : NULL));
        if (test->controls) controls(&source, input + 1, curve, test->channel, output + 1, &product);
        printf("F1_LAYOUT row=%" PRIu32 " bins=%" PRIu32 " limbs=%" PRIu32
            " magnitude_bits=%" PRIu32 " exponent=%" PRId32 " limb_count=%" PRIu64 " core=%d\n",
            row, layout.bins, layout.limbs, layout.magnitude_bits, layout.exponent, layout.limb_count, xPortGetCoreID());
        used = (uint32_t)layout.limb_count;
    } else CHECK(!memcmp(product_before, &product, sizeof(product)));
    emit_words(row, output + 1, used);
    for (size_t i = used; i < max_output; ++i) CHECK(output[i + 1] == UINT32_C(0xa5a5a5a5));
    uint32_t expected[34];
    for (uint32_t channel = 0; source.limbs && channel < source.channels; ++channel)
        for (uint32_t bin = 0; bin < source.bins; ++bin) {
            source_sample(test, bin, channel, expected, source.limbs);
            CHECK(!memcmp(expected, input + 1 + ((size_t)channel * source.bins + bin) * source.limbs,
                          source.limbs * sizeof(*expected)));
        }
    for (uint32_t bin = 0; bin < source.bins; ++bin) CHECK(indices[bin + 1] == index_at(test, bin));
    CHECK(!memcmp(source_before, &source, sizeof(source)));
    CHECK(input[0] == UINT32_C(0x13579bdf) && input[source_count + 1] == UINT32_C(0x2468ace0));
    CHECK(output[0] == UINT32_C(0x13579bdf) && output[max_output + 1] == UINT32_C(0x2468ace0));
    CHECK(indices[0] == 0x37 && indices[source.bins + 1] == 0xb9);
    free(indices); free(output); free(input);
    printf("F1_END row=%" PRIu32 " guards=1 unchanged=1 refusals=%" PRIu64
        " checks=%" PRIu64 " core=%d\n", row, refusals - before_refusals, checks - before_checks, xPortGetCoreID());
}

static void worker(void *unused) {
    (void)unused;
    printf("F1_WORKER core=%d priority=%u stack=16384\n", xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    for (uint32_t row = 0; row < F1_CASE_COUNT; ++row) {
        CHECK(xPortGetCoreID() == WORKER_CORE);
        capture(row);
        vTaskDelay(1);
    }
    printf("F1_COMPLETE cases=%u refusals=%" PRIu64 " checks=%" PRIu64 " core=%d\n",
        (unsigned)F1_CASE_COUNT, refusals, checks, xPortGetCoreID());
    printf("F1_STOP status=CAPTURED\n"); fflush(stdout); esp_restart();
}

void app_main(void) {
    printf("F1_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",
        (unsigned)F1_CASE_COUNT, xPortGetCoreID(), WORKER_CORE, F1_CASES_SHA256);
    fflush(stdout);
    // Only the worker mutates the inherited assertion counter on dual-core ESP32.
    assert(xTaskCreatePinnedToCore(worker, "floor1product", 16384, NULL, 3, NULL, WORKER_CORE) == pdPASS);
}
