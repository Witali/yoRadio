// Public raw codec API only. Handles remain opaque; no decoder-private headers.
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "esp_vorbis_dec.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "fixture.h"

#ifdef LIMIT_TO_64kHz
#error This format test requires the normal unrestricted build
#endif
#ifndef FORMAT_EXPECT_LOW_RATE_REJECTION
#error Select baseline reproduction (1) or repaired acceptance (0) explicitly
#endif

// --wrap aliases expose the original implementation of the same public API.
extern esp_audio_err_t __real_esp_vorbis_dec_open(void *, uint32_t, void **);
extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);

static void *vendor, *checked;
typedef struct { uint8_t before[16], data[16384], after[16]; } guarded_pcm_t;
static guarded_pcm_t vendor_pcm, checked_pcm;
static unsigned high_exact, low_exact, low_rejected, normal_exact, invalid_rejected;

static void stop(const char *reason) {
    if (reason) printf("C3_VORBIS_FORMAT_FAILURE %s\n", reason);
    if (vendor) { esp_vorbis_dec_close(vendor); vendor = NULL; }
    if (checked) { esp_vorbis_dec_close(checked); checked = NULL; }
    fflush(stdout);
    esp_restart();
}

static void check(bool condition, const char *reason) {
    if (!condition) stop(reason);
}

static void arm(guarded_pcm_t *pcm, uint8_t fill) {
    memset(pcm->before, 0xa5, sizeof(pcm->before));
    memset(pcm->data, fill, sizeof(pcm->data));
    memset(pcm->after, 0x5a, sizeof(pcm->after));
}

static void guards(const guarded_pcm_t *pcm) {
    for (unsigned i = 0; i < 16; ++i)
        check(pcm->before[i] == 0xa5 && pcm->after[i] == 0x5a, "public_output_canaries");
}

static void identification(uint8_t *out, uint32_t rate, unsigned short_bits, unsigned long_bits) {
    memcpy(out, fixture_info, sizeof(fixture_info));
    // Public identification payload: version[4], channels[1], rate[4],
    // three bitrate fields[12], packed short/long block exponents[1].
    for (unsigned i = 0; i < 4; ++i) out[5+i] = (uint8_t)(rate >> (8*i));
    out[21] = (uint8_t)(short_bits | (long_bits << 4));
}

static esp_vorbis_dec_cfg_t config(uint8_t *info) {
    return (esp_vorbis_dec_cfg_t){
        .info_header = info, .info_size = sizeof(fixture_info),
        .setup_header = (uint8_t *)fixture_setup, .setup_size = sizeof(fixture_setup),
    };
}

static uint32_t expected_bytes(unsigned packet, unsigned long_bits) {
    if (!packet) return 0;
    unsigned before = 1U << (fixture_long_mode[packet-1] ? long_bits : FIXTURE_SHORT_BITS);
    unsigned current = 1U << (fixture_long_mode[packet] ? long_bits : FIXTURE_SHORT_BITS);
    return ((before + current) / 4U) * 2U * sizeof(int16_t);
}

static void close_handles(void) {
    if (vendor) { void *handle = vendor; vendor = NULL; check(esp_vorbis_dec_close(handle) == ESP_AUDIO_ERR_OK, "vendor_close"); }
    if (checked) { void *handle = checked; checked = NULL; check(esp_vorbis_dec_close(handle) == ESP_AUDIO_ERR_OK, "checked_close"); }
}

static void vendor_probe(void) {
    uint8_t header[sizeof(fixture_info)];
    identification(header, 192000, FIXTURE_SHORT_BITS, 13);
    esp_vorbis_dec_cfg_t cfg = config(header);
    int result = __real_esp_vorbis_dec_open(&cfg, sizeof(cfg), &vendor);
    printf("C3_VORBIS_FORMAT_VENDOR_OPEN rate=192000 long=8192 result=%d handle=%u\n", result, vendor != NULL);
    check(result == ESP_AUDIO_ERR_OK && vendor, "vendor_high8192_open_required");
    uint32_t total = 0, nonzero = 0, full = 0;
    esp_audio_dec_info_t info = {0}; // Retain public metadata for this opened handle.
    for (unsigned packet = 0; packet < FIXTURE_PACKETS; ++packet) {
        uint32_t size = fixture_offsets[packet+1] - fixture_offsets[packet];
        esp_audio_dec_in_raw_t raw = {.buffer=(uint8_t *)fixture_packets+fixture_offsets[packet], .len=size};
        esp_audio_dec_out_frame_t out = {.buffer=vendor_pcm.data, .len=sizeof(vendor_pcm.data)};
        arm(&vendor_pcm, 0);
        result = __real_esp_vorbis_dec_decode(vendor, &raw, &out, &info);
        guards(&vendor_pcm);
        check(result == ESP_AUDIO_ERR_OK && raw.consumed == size && out.decoded_size == expected_bytes(packet, 13),
              "vendor_high8192_complete_packet");
        check(out.decoded_size <= sizeof(vendor_pcm.data), "vendor_high8192_public_output_bound");
        bool valid = info.sample_rate == 192000 && info.channel == 2 && info.bits_per_sample == 16;
        if (!valid) printf("C3_VORBIS_FORMAT_VENDOR_METADATA packet=%u result=%d consumed=%" PRIu32
            " decoded=%" PRIu32 " sample_rate=%" PRIu32 " channel=%u bits=%u\n", packet, result,
            raw.consumed, out.decoded_size, info.sample_rate, (unsigned)info.channel, (unsigned)info.bits_per_sample);
        check(valid, "vendor_high8192_metadata"); // Includes zero-output priming packet.
        for (unsigned i = 0; i < out.decoded_size; ++i) nonzero += vendor_pcm.data[i] != 0;
        full += out.decoded_size == sizeof(vendor_pcm.data);
        total += out.decoded_size;
        printf("C3_VORBIS_FORMAT_VENDOR_PACKET packet=%u consumed=%" PRIu32 " pcm=%" PRIu32
               " sample_rate=%" PRIu32 " channel=%u bits=%u canaries=1 core=0\n",
               packet, raw.consumed, out.decoded_size, info.sample_rate, (unsigned)info.channel, (unsigned)info.bits_per_sample);
        if (!(packet & 15U)) vTaskDelay(1);
    }
    check(total == FIXTURE_RAW8192_BYTES && nonzero && full == FIXTURE_FULL8192_PACKETS,
          "vendor_high8192_real_long_pcm");
    close_handles();
    printf("C3_VORBIS_FORMAT_VENDOR_COMPLETE packets=%u pcm=%" PRIu32 " nonzero=%" PRIu32 " full8192=%" PRIu32 "\n",
           FIXTURE_PACKETS, total, nonzero, full);
}

static void compare(uint32_t rate, unsigned long_bits, bool expect_rejection) {
    uint8_t reference_header[sizeof(fixture_info)], candidate_header[sizeof(fixture_info)];
    uint32_t reference_rate = long_bits == 13 ? 192000 : rate;
    identification(reference_header, reference_rate, FIXTURE_SHORT_BITS, long_bits);
    identification(candidate_header, rate, FIXTURE_SHORT_BITS, long_bits);
    esp_vorbis_dec_cfg_t ref_cfg = config(reference_header), cfg = config(candidate_header);
    check(__real_esp_vorbis_dec_open(&ref_cfg, sizeof(ref_cfg), &vendor) == ESP_AUDIO_ERR_OK && vendor,
          "pair_vendor_open");
    int result = esp_vorbis_dec_open(&cfg, sizeof(cfg), &checked);
    if (expect_rejection) {
        check(result == ESP_AUDIO_ERR_FAIL && !checked, "baseline_low_rate_header_rejection_required");
        ++low_rejected;
        close_handles();
        printf("C3_VORBIS_FORMAT_LEGAL_REJECT rate=%" PRIu32 " long=%u result=%d header_error=1\n", rate, 1U << long_bits, result);
        return;
    }
    check(result == ESP_AUDIO_ERR_OK && checked, "legal_candidate_open_required");
    uint32_t total = 0, nonzero = 0, full = 0;
    esp_audio_dec_info_t ai = {0}, bi = {0}; // One metadata object per opened handle.
    for (unsigned packet = 0; packet < FIXTURE_PACKETS; ++packet) {
        uint8_t *data = (uint8_t *)fixture_packets + fixture_offsets[packet];
        uint32_t size = fixture_offsets[packet+1] - fixture_offsets[packet];
        esp_audio_dec_in_raw_t a = {.buffer=data, .len=size}, b = a;
        esp_audio_dec_out_frame_t ao = {.buffer=vendor_pcm.data, .len=sizeof(vendor_pcm.data)};
        esp_audio_dec_out_frame_t bo = {.buffer=checked_pcm.data, .len=sizeof(checked_pcm.data)};
        arm(&vendor_pcm, 0xa7);
        int ar = __real_esp_vorbis_dec_decode(vendor, &a, &ao, &ai);
        guards(&vendor_pcm);
        arm(&checked_pcm, 0xc9);
        int br = esp_vorbis_dec_decode(checked, &b, &bo, &bi);
        guards(&checked_pcm);
        check(ar == ESP_AUDIO_ERR_OK && br == ar && a.consumed == size && b.consumed == a.consumed,
              "pair_result_and_full_consumption");
        check(ao.decoded_size == expected_bytes(packet, long_bits) && bo.decoded_size == ao.decoded_size &&
              bo.decoded_size <= sizeof(checked_pcm.data), "pair_exact_long_block_size");
        check(!memcmp(vendor_pcm.data, checked_pcm.data, bo.decoded_size), "pair_byte_exact_vendor_pcm");
        bool valid = ai.sample_rate == reference_rate && bi.sample_rate == rate &&
            ai.channel == 2 && bi.channel == 2 && ai.bits_per_sample == 16 && bi.bits_per_sample == 16;
        if (!valid) {
            printf("C3_VORBIS_FORMAT_PAIR_METADATA side=vendor packet=%u result=%d consumed=%" PRIu32
                " decoded=%" PRIu32 " expected_rate=%" PRIu32 " sample_rate=%" PRIu32 " channel=%u bits=%u\n",
                packet, ar, a.consumed, ao.decoded_size, reference_rate, ai.sample_rate,
                (unsigned)ai.channel, (unsigned)ai.bits_per_sample);
            printf("C3_VORBIS_FORMAT_PAIR_METADATA side=checked packet=%u result=%d consumed=%" PRIu32
                " decoded=%" PRIu32 " expected_rate=%" PRIu32 " sample_rate=%" PRIu32 " channel=%u bits=%u\n",
                packet, br, b.consumed, bo.decoded_size, rate, bi.sample_rate,
                (unsigned)bi.channel, (unsigned)bi.bits_per_sample);
        }
        check(valid, "pair_public_metadata"); // Includes zero-output priming packet.
        for (unsigned i = 0; i < bo.decoded_size; ++i) nonzero += checked_pcm.data[i] != 0;
        full += bo.decoded_size == sizeof(checked_pcm.data);
        total += bo.decoded_size;
        printf("C3_VORBIS_FORMAT_PAIR_PACKET rate=%" PRIu32 " long=%u packet=%u consumed=%" PRIu32 " pcm=%" PRIu32
               " vendor_expected_rate=%" PRIu32 " vendor_rate=%" PRIu32 " checked_expected_rate=%" PRIu32 " checked_rate=%" PRIu32
               " expected_channel=2 vendor_channel=%u checked_channel=%u expected_bits=16 vendor_bits=%u checked_bits=%u exact=1 canaries=1 core=0\n",
               rate, 1U << long_bits, packet, b.consumed, bo.decoded_size, reference_rate, ai.sample_rate, rate, bi.sample_rate,
               (unsigned)ai.channel, (unsigned)bi.channel, (unsigned)ai.bits_per_sample, (unsigned)bi.bits_per_sample);
        if (!(packet & 15U)) vTaskDelay(1);
    }
    check(nonzero && total == (long_bits == 13 ? FIXTURE_RAW8192_BYTES : FIXTURE_RAW2048_BYTES),
          "pair_complete_nonzero_pcm");
    if (long_bits == 13) check(full == FIXTURE_FULL8192_PACKETS, "pair_real8192_packets");
    close_handles();
    if (long_bits != 13) ++normal_exact;
    else if (rate < 64000) ++low_exact;
    else ++high_exact;
    printf("C3_VORBIS_FORMAT_EXACT rate=%" PRIu32 " long=%u packets=%u pcm=%" PRIu32 " full8192=%" PRIu32 "\n",
           rate, 1U << long_bits, FIXTURE_PACKETS, total, full);
}

static void reject(const char *name, uint32_t rate, unsigned short_bits, unsigned long_bits) {
    uint8_t header[sizeof(fixture_info)];
    identification(header, rate, short_bits, long_bits);
    esp_vorbis_dec_cfg_t cfg = config(header);
    int result = esp_vorbis_dec_open(&cfg, sizeof(cfg), &checked);
    check(result == ESP_AUDIO_ERR_FAIL && !checked, "invalid_identification_header_rejection_required");
    ++invalid_rejected;
    printf("C3_VORBIS_FORMAT_INVALID_REJECT case=%s result=%d header_error=1\n", name, result);
}

static void task(void *unused) {
    (void)unused;
    check(xPortGetCoreID() == 0, "public_decode_core0");
    vendor_probe(); // This is a prerequisite, never assumed from the source guard.
    compare(48000, FIXTURE_ENCODER_LONG_BITS, false);
    compare(192000, 13, false);
    compare(64000, 13, false);
    compare(63999, 13, FORMAT_EXPECT_LOW_RATE_REJECTION);
    compare(48000, 13, FORMAT_EXPECT_LOW_RATE_REJECTION);
    reject("zero_rate", 0, FIXTURE_SHORT_BITS, 13);
    reject("short32", 192000, 5, 13);
    reject("long16384", 192000, FIXTURE_SHORT_BITS, 14);
    reject("short_exceeds_long", 192000, 13, 12);
    check(high_exact == 2 && normal_exact == 1 && invalid_rejected == 4, "complete_controls");
#if FORMAT_EXPECT_LOW_RATE_REJECTION
    check(low_rejected == 2 && !low_exact, "baseline_reproduces_both_legal_rejections");
    puts("C3_VORBIS_FORMAT_BASELINE low_rejected=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=0");
#else
    check(low_exact == 2 && !low_rejected, "all_legal_rates_byte_exact");
    puts("C3_VORBIS_FORMAT_COMPLETE low_exact=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=0");
#endif
    stop(NULL);
}

void app_main(void) {
    check(xPortGetCoreID() == 0, "coordinator_core0");
    printf("C3_VORBIS_FORMAT_BEGIN expected_rejection=%d coordinator=0\n", FORMAT_EXPECT_LOW_RATE_REJECTION);
    check(xTaskCreatePinnedToCore(task, "public_format", 16384, NULL, 3, NULL, 0) == pdPASS,
          "create_core0_format_task");
}
