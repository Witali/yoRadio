// QEMU-only paired PCM comparison for esp_audio_codec 2.6.2 / ESP32-C3.
// BFP16 uses the analysis boundary; packed 14+14+4 uses retained frame history.
// These numerical roundtrips do not reduce live allocations.
#include "qemu_aac_bfp16.h"
#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_audio_codec_version.h"
#include "esp_log.h"
#include "esp_partition.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define FIXTURE(name, symbol) \
    extern const uint8_t name##_start[] asm("_binary_" symbol "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" symbol "_aac_end")
FIXTURE(lc44, "lc_44100_stereo");
FIXTURE(lc22, "lc_22050_mono");
FIXTURE(lc48, "lc_48000_stereo");
FIXTURE(he44, "he_44100_stereo");
FIXTURE(he48, "he_48000_stereo");
FIXTURE(hev2, "hev2_44100_stereo");

// Shared paired-decoder harness. The alternative experiment touches history
// only; the original BFP16 analysis-row experiment and its log ABI are retained.
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
#include "qemu_aac_packed_history.h"
#define PCM_ERROR_LIMIT CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_ERROR_LIMIT
#ifdef CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST
#define TEST_LABEL "SBRLAYOUT"
#elif defined(CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST)
#define TEST_LABEL "PSPORT"
#elif defined(CONFIG_YORADIO_QEMU_AAC_PC16_HISTORY_TEST)
#define TEST_LABEL "PCX16"
#else
#define TEST_LABEL "PCX14"
#endif
#define VARIANT_LABEL "variant"
#define CANDIDATE_LABEL "packed"
#if defined(CONFIG_YORADIO_QEMU_AAC_PS_HISTORY_PORT_TEST) || defined(CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST)
static const unsigned groups[] = {7, 1, 0};
#else
static const unsigned groups[] = {1, 2, 3, 4, 5, 6, 7, 0};
#endif
#else
#define PCM_ERROR_LIMIT 1
#define TEST_LABEL "BFP16"
#define VARIANT_LABEL "bands"
#define CANDIDATE_LABEL "bfp"
static const unsigned groups[] = {32, 8, 1, 0};
#endif
static const char *TAG = "aac_compare";
#ifndef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
static unsigned group_bands; // Zero means the unmodified reference path.
#endif
static uint32_t complex_rows, real_rows, changed_values;
static unsigned max_shift;
static unsigned fixture_repeats = 2;
static bool detailed_statistics;
#ifdef CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST
void aac_sbr_layout_assert_idle(void);
#endif

// Exact absolute-error bins 0..4095, then 4096-wide bins up to 65535.
// Two channels use 32,888 bytes, allocated only for external recordings.
#define ERROR_BINS (4096 + 15)
typedef struct {
    uint64_t samples, absolute_sum, square_sum, signal_square_sum, over_one, over_two, over_limit;
    int64_t signed_sum;
    uint32_t maximum, clipped_ref, clipped_bfp;
    uint64_t max_at;
    int16_t max_ref, max_bfp;
} error_stats_t;

static void accumulate_error(error_stats_t *s, uint32_t *hist, int16_t ref, int16_t bfp) {
    int32_t delta = (int32_t)bfp - ref;
    uint32_t error = delta < 0 ? -delta : delta;
    s->signed_sum += delta;
    s->absolute_sum += error;
    s->square_sum += (uint64_t)error * error;
    s->signal_square_sum += (uint64_t)((int64_t)ref * ref);
    s->over_one += error > 1;
    s->over_two += error > 2;
    s->over_limit += error > PCM_ERROR_LIMIT;
    s->clipped_ref += ref == INT16_MIN || ref == INT16_MAX;
    s->clipped_bfp += bfp == INT16_MIN || bfp == INT16_MAX;
    if (error > s->maximum) {
        s->maximum = error; s->max_at = s->samples;
        s->max_ref = ref; s->max_bfp = bfp;
    }
    ++s->samples;
    unsigned bin = error < 4096 ? error : 4096 + (error - 4096) / 4096;
    assert(bin < ERROR_BINS);
    ++hist[bin];
}

static void print_statistics(const char *name, unsigned bands, unsigned run,
                             unsigned channel, const error_stats_t *s, const uint32_t *hist) {
    ESP_LOGI(TAG, TEST_LABEL "_STATS case=%s " VARIANT_LABEL "=%u run=%u channel=%u samples=%" PRIu64
             " abs_sum=%" PRIu64 " square_sum=%" PRIu64 " signal_square_sum=%" PRIu64
             " signed_sum=%" PRId64 " over_one=%" PRIu64 " over_two=%" PRIu64
             " over_limit=%" PRIu64 " maximum=%" PRIu32
             " max_at=%" PRIu64 " max_ref=%d max_bfp=%d clipped_ref=%" PRIu32 " clipped_bfp=%" PRIu32,
             name, bands, run, channel, s->samples, s->absolute_sum, s->square_sum,
             s->signal_square_sum, s->signed_sum, s->over_one, s->over_two, s->over_limit, s->maximum, s->max_at,
             s->max_ref, s->max_bfp, s->clipped_ref, s->clipped_bfp);
    char text[512];
    unsigned used = 0, entries = 0;
    for (unsigned bin = 0; bin < ERROR_BINS; ++bin) {
        if (!hist[bin]) continue;
        int n = snprintf(text + used, sizeof(text) - used, "%u:%" PRIu32 ",", bin, hist[bin]);
        assert(n > 0 && n < sizeof(text) - used);
        used += n;
        if (++entries == 32) {
            ESP_LOGI(TAG, TEST_LABEL "_HIST case=%s " VARIANT_LABEL "=%u run=%u channel=%u bins=%s",
                     name, bands, run, channel, text);
            used = entries = 0;
        }
    }
    if (entries) ESP_LOGI(TAG, TEST_LABEL "_HIST case=%s " VARIANT_LABEL "=%u run=%u channel=%u bins=%s",
                         name, bands, run, channel, text);
}

#ifndef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
// Complementing negative values permits the asymmetric signed range, including
// INT32_MIN, without abs(INT32_MIN) or implementation-defined signed shifts.
static unsigned block_shift(const int32_t *real, const int32_t *imag, unsigned n) {
    uint32_t peak = 0;
    for (unsigned i = 0; i < n; ++i) {
        uint32_t r = real[i] < 0 ? ~(uint32_t)real[i] : (uint32_t)real[i];
        if (r > peak) peak = r;
        if (imag) {
            uint32_t q = imag[i] < 0 ? ~(uint32_t)imag[i] : (uint32_t)imag[i];
            if (q > peak) peak = q;
        }
    }
    unsigned shift = 0;
    while (peak > INT16_MAX) { peak >>= 1; ++shift; }
    assert(shift <= 16);
    return shift;
}

// Nearest, ties away from zero; saturate a rounding carry at the int16 boundary.
// This also keeps reconstruction in int32 range, even at INT32_MIN/MAX.
static int16_t pack_value(int32_t value, unsigned shift) {
    uint32_t magnitude = value < 0 ? 0u - (uint32_t)value : (uint32_t)value;
    if (shift) magnitude = (magnitude + (1u << (shift - 1))) >> shift;
    uint32_t limit = value < 0 ? 32768u : 32767u;
    if (magnitude > limit) magnitude = limit;
    return (int16_t)(value < 0 ? -(int32_t)magnitude : (int32_t)magnitude);
}

static int32_t unpack_value(int16_t value, unsigned shift) {
    // Multiplication of these bounded operands is defined, unlike left-shifting
    // a negative signed number. One exponent step means multiplying by two.
    return (int32_t)value * (int32_t)(1u << shift);
}

static void roundtrip_row(int32_t *real, int32_t *imag) {
    struct {
        uint32_t before;
        int16_t real[32], imag[32];
        uint32_t after;
    } packed = {.before = 0x1234abcd, .after = 0x9876dcba};
    for (unsigned base = 0; base < 32; base += group_bands) {
        unsigned shift = block_shift(real + base, imag ? imag + base : NULL, group_bands);
        if (shift > max_shift) max_shift = shift;
        for (unsigned i = base; i < base + group_bands; ++i) {
            packed.real[i] = pack_value(real[i], shift);
            if (imag) packed.imag[i] = pack_value(imag[i], shift);
        }
        for (unsigned i = base; i < base + group_bands; ++i) {
            int32_t value = unpack_value(packed.real[i], shift);
            changed_values += value != real[i];
            real[i] = value;
            if (imag) {
                value = unpack_value(packed.imag[i], shift);
                changed_values += value != imag[i];
                imag[i] = value;
            }
        }
    }
    assert(packed.before == 0x1234abcd && packed.after == 0x9876dcba);
}

void __real_calc_sbr_anafilterbank(int32_t *, int32_t *, const int16_t *, int32_t *, int32_t);
void __real_calc_sbr_anafilterbank_LC(int32_t *, const int16_t *, int32_t *, int32_t);

void __wrap_calc_sbr_anafilterbank(int32_t *real, int32_t *imag,
                                 const int16_t *input, int32_t *scratch, int32_t bands) {
    __real_calc_sbr_anafilterbank(real, imag, input, scratch, bands);
    if (group_bands) { ++complex_rows; roundtrip_row(real, imag); }
}

void __wrap_calc_sbr_anafilterbank_LC(int32_t *real, const int16_t *input,
                                    int32_t *scratch, int32_t bands) {
    __real_calc_sbr_anafilterbank_LC(real, input, scratch, bands);
    if (group_bands) { ++real_rows; roundtrip_row(real, NULL); }
}

static void check_value(int32_t value, unsigned shift) {
    int64_t scale = (int64_t)1 << shift;
    int64_t magnitude = value < 0 ? -(int64_t)value : (int64_t)value;
    int64_t expected = (magnitude + scale / 2) / scale;
    int64_t limit = value < 0 ? 32768 : 32767;
    if (expected > limit) expected = limit;
    if (value < 0) expected = -expected;
    int16_t packed = pack_value(value, shift);
    assert(packed == expected);
    int32_t reconstructed = unpack_value(packed, shift);
    assert(reconstructed == expected * scale);
    int64_t error = (int64_t)reconstructed - value;
    if (error < 0) error = -error;
    // Boundary saturation can cost just under one step; otherwise half a step.
    assert(error <= (shift ? scale - 1 : 0));
}

static void arithmetic_tests(void) {
    for (int32_t v = INT16_MIN; v <= INT16_MAX; ++v) {
        assert(block_shift(&v, NULL, 1) == 0);
        check_value(v, 0);
    }
    const int32_t edges[] = {INT32_MIN, INT32_MIN + 1, INT32_MAX, INT32_MAX - 1,
                            -65536, -32769, -32768, -1, 0, 1, 32767, 32768, 65535};
    for (unsigned i = 0; i < sizeof(edges) / sizeof(edges[0]); ++i)
        check_value(edges[i], block_shift(edges + i, NULL, 1));
    uint32_t rng = 0x51bfc316;
    for (unsigned k = 0; k < 4096; ++k) {
        int32_t row[64];
        for (unsigned i = 0; i < 64; ++i) {
            rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
            memcpy(row + i, &rng, sizeof(rng));
        }
        for (unsigned n = 1; n <= 32; n *= 2) {
            unsigned shift = block_shift(row, row + 32, n);
            for (unsigned i = 0; i < n; ++i) {
                check_value(row[i], shift);
                check_value(row[32 + i], shift);
            }
        }
        if (!(k % 128)) vTaskDelay(1);
    }
    ESP_LOGI(TAG, TEST_LABEL "_ARITHMETIC_PASS int16-exhaustive int32-edges random-blocks=4096");
}

#endif

static inline uint32_t instructions(void) {
    uint32_t count;
    __asm__ volatile("csrr %0, minstret" : "=r"(count) :: "memory");
    return count;
}

static void check_counter(void) {
    portMUX_TYPE lock = portMUX_INITIALIZER_UNLOCKED;
    uint32_t before, after;
    taskENTER_CRITICAL(&lock);
    __asm__ volatile("csrr %0, minstret\n.rept 1024\n nop\n.endr\ncsrr %1, minstret\n"
                     : "=r"(before), "=r"(after) :: "memory");
    taskEXIT_CRITICAL(&lock);
    assert(after - before == 1025);
    ESP_LOGI(TAG, TEST_LABEL "_COUNTER_PASS nop1024=%" PRIu32, after - before);
}

typedef struct {
    const char *name;
    const uint8_t *start, *end;
    uint32_t rate;
    uint8_t channels;
    bool sbr;
} fixture_t;

static void compare_fixture(const fixture_t *f, unsigned bands, unsigned run) {
    native_aac_decoder_t *dec[2] = {native_aac_decoder_create(), native_aac_decoder_create()};
    uint8_t *pcm[2] = {malloc(NATIVE_AAC_PCM_FRAME_BYTES + 16),
                       malloc(NATIVE_AAC_PCM_FRAME_BYTES + 16)};
    assert(dec[0] && dec[1] && pcm[0] && pcm[1]);
    uint32_t *hist = detailed_statistics ? calloc(f->channels * ERROR_BINS, sizeof(uint32_t)) : NULL;
    error_stats_t stats[2] = {0};
    assert(!detailed_statistics || hist);
    for (unsigned leg = 0; leg < 2; ++leg)
        memset(pcm[leg] + NATIVE_AAC_PCM_FRAME_BYTES, 0xa5, 16);
    uint64_t work[2] = {0}, samples = 0, different = 0, over_one = 0, over_two = 0, over_limit = 0;
    uint32_t worst_call[2] = {0}, max_error[2] = {0}, frames = 0;
    uint64_t first_bad = UINT64_MAX;
    int first_ref = 0, first_candidate = 0;
    complex_rows = real_rows = changed_values = max_shift = 0;
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
    packed_history_reset(run);
#endif
    // A second pass through the fixture exercises retained filter/PS histories.
    // Both passes (including decoder startup) contribute to fidelity and timing.
    for (unsigned repeat = 0; repeat < fixture_repeats; ++repeat) {
        for (const uint8_t *p = f->start; p < f->end;) {
            size_t count = (size_t)(f->end - p);
            if (count > 997) count = 997;
            esp_audio_simple_dec_raw_t raw[2] = {
                {.buffer = (uint8_t *)p, .len = count},
                {.buffer = (uint8_t *)p, .len = count}};
            while (raw[0].len) {
                esp_audio_simple_dec_out_t output[2] = {
                    {.buffer = pcm[0], .len = NATIVE_AAC_PCM_FRAME_BYTES},
                    {.buffer = pcm[1], .len = NATIVE_AAC_PCM_FRAME_BYTES}};
                for (unsigned order = 0; order < 2; ++order) {
                    unsigned leg = order ^ (run & 1);
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
                    packed_history_select(leg ? bands : 0);
#else
                    group_bands = leg ? bands : 0;
#endif
                    uint32_t before = instructions();
                    esp_audio_err_t result = native_aac_decoder_process(dec[leg], &raw[leg], &output[leg]);
                    uint32_t elapsed = instructions() - before;
                    work[leg] += elapsed;
                    if (elapsed > worst_call[leg]) worst_call[leg] = elapsed;
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
                    packed_history_select(0);
#else
                    group_bands = 0;
#endif
                    assert(result == ESP_AUDIO_ERR_OK);
                    assert(raw[leg].consumed <= raw[leg].len);
                    assert(raw[leg].consumed || output[leg].decoded_size);
                    assert(output[leg].decoded_size <= NATIVE_AAC_PCM_FRAME_BYTES);
                    for (unsigned i = 0; i < 16; ++i)
                        assert(pcm[leg][NATIVE_AAC_PCM_FRAME_BYTES + i] == 0xa5);
                }
                assert(raw[0].consumed == raw[1].consumed);
                assert(output[0].decoded_size == output[1].decoded_size);
                for (unsigned leg = 0; leg < 2; ++leg) {
                    raw[leg].buffer += raw[leg].consumed;
                    raw[leg].len -= raw[leg].consumed;
                    if (output[leg].decoded_size) {
                        esp_audio_simple_dec_info_t info;
                        assert(native_aac_decoder_get_info(dec[leg], &info) == ESP_AUDIO_ERR_OK);
                        assert(info.sample_rate == f->rate && info.channel == f->channels && info.bits_per_sample == 16);
                    }
                }
                assert(output[0].decoded_size % (2 * f->channels) == 0);
                const int16_t *reference = (const int16_t *)pcm[0];
                const int16_t *candidate = (const int16_t *)pcm[1];
                for (unsigned i = 0; i < output[0].decoded_size / 2; ++i) {
                    int32_t delta = (int32_t)candidate[i] - reference[i];
                    uint32_t error = delta < 0 ? -delta : delta;
                    unsigned channel = i % f->channels;
                    if (hist) accumulate_error(stats + channel, hist + channel * ERROR_BINS,
                                               reference[i], candidate[i]);
                    if (error > max_error[channel]) max_error[channel] = error;
                    different += error != 0;
                    over_one += error > 1;
                    over_two += error > 2;
                    over_limit += error > PCM_ERROR_LIMIT;
                    if (error > PCM_ERROR_LIMIT && first_bad == UINT64_MAX) {
                        first_bad = samples + i;
                        first_ref = reference[i]; first_candidate = candidate[i];
                    }
                }
                samples += output[0].decoded_size / 2;
                frames += output[0].decoded_size != 0;
            }
            p += count;
            vTaskDelay(1);
        }
    }
    assert(frames > 10 && samples >= f->rate * f->channels / 2);
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
    packed_history_report(f->name, bands, run, &complex_rows, &changed_values, &max_shift);
    if (!bands || bands == 7 || !f->sbr) assert(!different && !changed_values);
    if (!complex_rows) assert(!different && !changed_values);
#else
    if (f->sbr && bands) assert(complex_rows + real_rows > 0 && changed_values > 0);
    else assert(!complex_rows && !real_rows && !different);
#endif
    ESP_LOGI(TAG, TEST_LABEL "_RESULT case=%s " VARIANT_LABEL "=%u run=%u samples=%" PRIu64
             " frames=%" PRIu32 " max_l=%" PRIu32 " max_r=%" PRIu32
             " different=%" PRIu64 " over_one=%" PRIu64 " over_two=%" PRIu64
             " over_limit=%" PRIu64 " complex_rows=%" PRIu32
             " real_rows=%" PRIu32 " changed_qmf=%" PRIu32 " max_shift=%u"
             " ref_work=%" PRIu64 " " CANDIDATE_LABEL "_work=%" PRIu64 " ref_max_call=%" PRIu32
             " " CANDIDATE_LABEL "_max_call=%" PRIu32 " precision=%s",
             f->name, bands, run, samples, frames, max_error[0], max_error[1], different,
             over_one, over_two, over_limit, complex_rows, real_rows, changed_values, max_shift,
             work[0], work[1], worst_call[0], worst_call[1], over_limit ? "FAIL" : "PASS");
    if (over_limit)
        ESP_LOGI(TAG, TEST_LABEL "_FIRST_ERROR case=%s " VARIANT_LABEL "=%u run=%u sample=%" PRIu64
                 " ref=%d " CANDIDATE_LABEL "=%d", f->name, bands, run, first_bad, first_ref, first_candidate);
    if (hist) {
        for (unsigned channel = 0; channel < f->channels; ++channel)
            print_statistics(f->name, bands, run, channel, stats + channel, hist + channel * ERROR_BINS);
        free(hist);
    }
    for (unsigned leg = 0; leg < 2; ++leg) {
        native_aac_decoder_destroy(dec[leg]); free(pcm[leg]);
    }
#ifdef CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST
    aac_sbr_layout_assert_idle();
#endif
}

#ifdef CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST
void aac_sbr_layout_fail_next(size_t);
void aac_sbr_layout_assert_idle(void);

static void layout_lifecycle(void) {
    const fixture_t sequence[] = {
        {"v2",hev2_start,hev2_end,44100,2,true},
        {"he44",he44_start,he44_end,44100,2,true},
        {"lc48",lc48_start,lc48_end,48000,2,false},
        {"he48",he48_start,he48_end,48000,2,true},
        {"lc22",lc22_start,lc22_end,22050,1,false},
        {"lc44",lc44_start,lc44_end,44100,2,false},
        {"v2",hev2_start,hev2_end,44100,2,true},
    };
    uint8_t *pcm[2]={malloc(NATIVE_AAC_PCM_FRAME_BYTES),malloc(NATIVE_AAC_PCM_FRAME_BYTES)};
    assert(pcm[0] && pcm[1]);
    uint64_t samples=0;
    for (unsigned trial=0;trial<3;++trial) {
        packed_history_reset(0);
        native_aac_decoder_t *dec[2]={native_aac_decoder_create(),native_aac_decoder_create()};
        assert(dec[0] && dec[1]);
        size_t failed=trial==1 ? 55128 : trial==2 ? 1180 : 0;
        for (unsigned cycle=0;cycle<(failed?1:3);++cycle) {
            for (unsigned f=0;f<(failed?1:sizeof(sequence)/sizeof(sequence[0]));++f) {
                const fixture_t *input=sequence+f;
                unsigned injected=0;
                for (const uint8_t *p=input->start;p<input->end;) {
                    size_t count=(size_t)(input->end-p); if(count>193)count=193;
                    esp_audio_simple_dec_raw_t raw[2]={{.buffer=(uint8_t*)p,.len=count},{.buffer=(uint8_t*)p,.len=count}};
                    while(raw[0].len) {
                        esp_audio_simple_dec_out_t out[2]={{.buffer=pcm[0],.len=NATIVE_AAC_PCM_FRAME_BYTES},{.buffer=pcm[1],.len=NATIVE_AAC_PCM_FRAME_BYTES}};
                        esp_audio_err_t status[2];
                        for(unsigned leg=0;leg<2;++leg) {
                            packed_history_select(leg);
                            if(failed && !(injected&(1u<<leg))) { aac_sbr_layout_fail_next(failed); injected|=1u<<leg; }
                            status[leg]=native_aac_decoder_process(dec[leg],&raw[leg],&out[leg]);
                            // An injected request may occur only when a full ADTS frame arrives.
                            // Pending injections are tracked separately for both decoder legs.
                        }
                        packed_history_select(0);
                        assert(status[0]==status[1] && status[0]==ESP_AUDIO_ERR_OK);
                        assert(raw[0].consumed==raw[1].consumed && out[0].decoded_size==out[1].decoded_size);
                        assert(raw[0].consumed || out[0].decoded_size);
                        assert(!memcmp(pcm[0],pcm[1],out[0].decoded_size));
                        for(unsigned leg=0;leg<2;++leg) {
                            if(out[leg].decoded_size) {
                                esp_audio_simple_dec_info_t info;
                                assert(native_aac_decoder_get_info(dec[leg],&info)==ESP_AUDIO_ERR_OK);
                                assert(info.bits_per_sample==16);
                                assert(info.sample_rate==(failed?22050:input->rate));
                                assert(info.channel==(failed?1:input->channels));
                            }
                            raw[leg].buffer+=raw[leg].consumed; raw[leg].len-=raw[leg].consumed;
                        }
                        samples+=out[0].decoded_size/2;
                    }
                    p+=count;
                }
            }
        }
        for(unsigned leg=0;leg<2;++leg) native_aac_decoder_destroy(dec[leg]);
        aac_sbr_layout_assert_idle();
        ESP_LOGI(TAG,"SBRLAYOUT_LIFECYCLE_PASS trial=%u allocation_failure=%u PCM=exact cleanup=complete",trial,(unsigned)failed);
    }
    free(pcm[0]);free(pcm[1]);
    ESP_LOGI(TAG,"SBRLAYOUT_LIFECYCLE_COMPLETE samples=%"PRIu64" segments=21 failure_paths=2",samples);
}
#endif

static bool external_fixture(void) {
    const esp_partition_t *partition = esp_partition_find_first(
        ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_OTA_1, NULL);
    assert(partition);
    uint32_t header[8];
    assert(esp_partition_read(partition, 0, header, sizeof(header)) == ESP_OK);
    if (header[0] != 0x31504642) return false;
    assert(header[1] && header[1] <= partition->size - sizeof(header));
    assert(header[2] >= 8000 && header[2] <= 96000);
    assert(header[3] >= 1 && header[3] <= 2 && header[4] <= 1);
    assert(header[5] == 1 && header[6] == 3 && header[7] == 1);
    const void *mapped;
    esp_partition_mmap_handle_t handle;
    assert(esp_partition_mmap(partition, 0, sizeof(header) + header[1],
                              ESP_PARTITION_MMAP_DATA, &mapped, &handle) == ESP_OK);
    const uint8_t *start = (const uint8_t *)mapped + sizeof(header);
    fixture_t fixture = {"external", start, start + header[1], header[2], header[3], header[4]};
    fixture_repeats = 1; // One continuous recording; no looping at the boundary.
    detailed_statistics = true;
    ESP_LOGI(TAG, TEST_LABEL "_EXTERNAL bytes=%" PRIu32 " rate=%" PRIu32 " channels=%u sbr=%u runs=3 repeats=1",
             header[1], header[2], fixture.channels, fixture.sbr);
    for (unsigned g = 0; g < sizeof(groups) / sizeof(groups[0]); ++g)
        for (unsigned run = 1; run <= 3; ++run)
            compare_fixture(&fixture, groups[g], run);
    esp_partition_munmap(handle);
    detailed_statistics = false;
    fixture_repeats = 2;
    return true;
}

void qemu_aac_bfp16_test(void) {
#ifdef CONFIG_YORADIO_QEMU_AAC_RESET_TEST
    void qemu_aac_reset_test(void);
    qemu_aac_reset_test();
    return;
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_SBR_LAYOUT_TEST
    layout_lifecycle();
#endif
    check_counter();
#ifdef CONFIG_YORADIO_QEMU_AAC_PACKED_HISTORY_TEST
    ESP_LOGI(TAG, TEST_LABEL "_LIMIT development=%u production=2", PCM_ERROR_LIMIT);
    packed_history_arithmetic_tests();
#else
    arithmetic_tests();
#endif
    if (external_fixture()) {
        ESP_LOGI(TAG, TEST_LABEL "_EXPERIMENT_COMPLETE external recording; inspect precision per case");
        return;
    }
    ESP_LOGI(TAG, TEST_LABEL "_ENV codec=%s control=0 runs=3 repeats=2 baseline=wrap-bypass RAM_saved=0",
             esp_audio_codec_get_version());
    const fixture_t fixtures[] = {
        {"lc44100_stereo", lc44_start, lc44_end, 44100, 2, false},
        {"lc22050_mono", lc22_start, lc22_end, 22050, 1, false},
        {"lc48000_stereo", lc48_start, lc48_end, 48000, 2, false},
        {"he44100_stereo", he44_start, he44_end, 44100, 2, true},
        {"he48000_stereo", he48_start, he48_end, 48000, 2, true},
        {"hev2_44100_stereo", hev2_start, hev2_end, 44100, 2, true}};
    for (unsigned i = 0; i < sizeof(fixtures) / sizeof(fixtures[0]); ++i)
        for (unsigned g = 0; g < (fixtures[i].sbr ? sizeof(groups) / sizeof(groups[0]) : 1); ++g)
            for (unsigned run = 1; run <= 3; ++run)
                compare_fixture(fixtures + i, groups[g], run);
    ESP_LOGI(TAG, TEST_LABEL "_EXPERIMENT_COMPLETE inspect precision per case; no production approval");
}
