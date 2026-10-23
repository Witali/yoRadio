// Public raw API only. No decoder-private headers or handle dereferences.
#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "esp_vorbis_dec.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "corpus_case.h"
#include "data.h"

#ifdef LIMIT_TO_64kHz
#error This corpus requires the normal unrestricted format profile
#endif
_Static_assert(CORPUS_CASE_COUNT >= 1 && CORPUS_CASE_COUNT <= 31, "Bounded named corpus cases");

#define P "C3_VORBIS_CHECKED_CORPUS_"
#define PACKETS 14U
#define PCM_CAPACITY 16384U
#define INPUT_CAPACITY 512U
typedef struct { uint8_t before[16], data[PCM_CAPACITY], after[16]; } guarded_pcm_t;
static guarded_pcm_t checked_pcm;
static uint8_t checked_input[INPUT_CAPACITY];
static char pcm_hex[2U * PCM_CAPACITY + 1U]; // Test-only capture; worker stack is unchanged.
static void *checked;
static unsigned current_case, current_packet;

static void stop(const char *reason) {
    if (reason) printf(P "FAILURE case=%u packet=%u reason=%s core=%d\n",
                       current_case, current_packet, reason, xPortGetCoreID());
    if (checked) { esp_vorbis_dec_close(checked); checked = NULL; }
    fflush(stdout);
    esp_restart();
    for (;;) vTaskDelay(1);
}
static void need(bool condition, const char *reason) { if (!condition) stop(reason); }
static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}
static bool block_ok(unsigned n) { return n >= 64 && n <= 8192 && !(n & (n - 1)); }
static void arm(guarded_pcm_t *p, uint8_t fill) {
    memset(p->before, 0xa5, sizeof(p->before));
    memset(p->data, fill, sizeof(p->data));
    memset(p->after, 0x5a, sizeof(p->after));
}
static bool guards(const guarded_pcm_t *p) {
    for (unsigned i = 0; i < 16; ++i)
        if (p->before[i] != 0xa5 || p->after[i] != 0x5a) return false;
    return true;
}
static uint32_t expected_pcm(const corpus_case_t *c, unsigned packet) {
    if (!packet) return 0;
    unsigned previous = c->modes[packet - 1] ? c->long_block : c->short_block;
    unsigned current = c->modes[packet] ? c->long_block : c->short_block;
    return ((previous + current) / 4U) * c->channels * sizeof(int16_t);
}
static void descriptor(const corpus_case_t *c) {
    need(c->id && *c->id && c->identification && c->setup && c->audio && c->offsets && c->modes,
         "descriptor_pointers");
    for (const char *p = c->id; *p; ++p)
        need((*p >= 'a' && *p <= 'z') || (*p >= '0' && *p <= '9') || *p == '-' || *p == '_',
             "descriptor_id_token");
    need(c->identification_size == 30 && !memcmp(c->identification, "\x01vorbis", 7), "identification_prefix");
    need(c->setup_size > 7 && c->setup_size <= UINT32_MAX && !memcmp(c->setup, "\x05vorbis", 7), "setup_prefix");
    const uint8_t *id = c->identification;
    need(le32(id + 7) == 0 && c->channels == 2 && id[11] == c->channels && c->rate &&
         le32(id + 12) == c->rate && (id[29] & 1U), "identification_fields");
    need(block_ok(c->short_block) && block_ok(c->long_block) && c->short_block <= c->long_block &&
         (1U << (id[28] & 15U)) == c->short_block && (1U << (id[28] >> 4)) == c->long_block,
         "identification_blocks");
    need(c->mode_count == PACKETS && c->offset_count == PACKETS + 1 &&
         c->audio_size <= UINT32_MAX && c->offsets[0] == 0 &&
         c->offsets[PACKETS] == c->audio_size, "descriptor_offsets_shape");
    uint32_t total = 0;
    unsigned transitions = 0;
    for (unsigned i = 0; i < PACKETS; ++i) {
        need(c->modes[i] <= 1 && c->offsets[i] < c->offsets[i + 1] && c->offsets[i + 1] <= c->audio_size &&
             c->offsets[i + 1] - c->offsets[i] <= INPUT_CAPACITY, "descriptor_packet_bounds");
        uint8_t first = c->audio[c->offsets[i]];
        need(!(first & 1U) && ((first >> 1) & 1U) == c->modes[i], "descriptor_packet_mode");
        if (c->modes[i]) need(i > 0 && i + 1 < PACKETS && ((first >> 2) & 1U) == c->modes[i - 1] &&
                            ((first >> 3) & 1U) == c->modes[i + 1], "descriptor_window_flags");
        if (i) transitions |= 1U << (c->modes[i - 1] * 2U + c->modes[i]);
        need(expected_pcm(c, i) <= PCM_CAPACITY, "descriptor_ample_output");
        total += expected_pcm(c, i);
    }
    need(transitions == 15 && total == c->expected_pcm_bytes, "descriptor_overlap_total");
}
static esp_vorbis_dec_cfg_t config(const corpus_case_t *c) {
    return (esp_vorbis_dec_cfg_t){
        .info_header = (uint8_t *)c->identification + 7, .info_size = c->identification_size - 7,
        .setup_header = (uint8_t *)c->setup + 7, .setup_size = c->setup_size - 7,
    };
}
static void nonzero(const uint8_t *pcm, uint32_t bytes, uint32_t *left, uint32_t *right) {
    *left = *right = 0;
    for (uint32_t i = 0; i < bytes; i += 4) {
        *left += (pcm[i] | pcm[i + 1]) != 0;
        *right += (pcm[i + 2] | pcm[i + 3]) != 0;
    }
}
static uint32_t run_case(const corpus_case_t *c, unsigned index) {
    current_case = index; current_packet = 0;
    descriptor(c);
    need(!checked, "fresh_checked_handle");
    esp_vorbis_dec_cfg_t cc = config(c);
    int cr = esp_vorbis_dec_open(&cc, sizeof(cc), &checked);
    printf(P "OPEN case=%u id=%s checked_rc=%d checked_handle=%u core=%d\n",
        index, c->id, cr, checked != NULL, xPortGetCoreID());
    need(cr == ESP_AUDIO_ERR_OK && checked, "checked_public_open");
    esp_audio_dec_info_t ci = {0}; // Persistent public metadata for this handle, including primer.
    uint32_t total = 0, nz_left = 0, nz_right = 0;
    unsigned transition_mask = 0;
    for (unsigned packet = 0; packet < PACKETS; ++packet) {
        current_packet = packet;
        uint32_t size = c->offsets[packet + 1] - c->offsets[packet], expected = expected_pcm(c, packet);
        memcpy(checked_input, c->audio + c->offsets[packet], size);
        esp_audio_dec_in_raw_t b = {.buffer=checked_input, .len=size};
        esp_audio_dec_out_frame_t bo = {.buffer=checked_pcm.data, .len=sizeof(checked_pcm.data)};
        arm(&checked_pcm, 0xc9);
        cr = esp_vorbis_dec_decode(checked, &b, &bo, &ci);
        bool cg = guards(&checked_pcm), bounded = bo.decoded_size <= PCM_CAPACITY;
        uint32_t nl = 0, nr = 0;
        if (bounded && !(bo.decoded_size % 4U)) nonzero(checked_pcm.data, bo.decoded_size, &nl, &nr);
        unsigned transition = packet ? c->modes[packet - 1] * 2U + c->modes[packet] : 4U;
        int core = xPortGetCoreID();
        printf(P "PACKET case=%u packet=%u size=%" PRIu32 " checked_rc=%d checked_consumed=%" PRIu32
            " expected_pcm=%" PRIu32 " checked_pcm=%" PRIu32 " checked_rate=%" PRIu32
            " checked_channels=%u checked_bits=%u checked_canary=%u transition=%u nz_l=%" PRIu32 " nz_r=%" PRIu32 " core=%d\n",
            index, packet, size, cr, b.consumed, expected, bo.decoded_size, ci.sample_rate,
            (unsigned)ci.channel, (unsigned)ci.bits_per_sample, cg, transition, nl, nr, core);
        need(core == 0 && cr == ESP_AUDIO_ERR_OK && b.consumed == size,
             "checked_result_full_consumption_core");
        need(bounded && bo.decoded_size == expected && cg, "checked_pcm_size_and_canaries");
        need(ci.sample_rate == c->rate && ci.channel == 2 && ci.bits_per_sample == 16,
             "checked_retained_public_metadata");
        need(!packet ? !nl && !nr : nl && nr, "checked_nonzero_each_channel_transition");
        static const char digits[] = "0123456789abcdef";
        for (uint32_t i = 0; i < bo.decoded_size; ++i) {
            pcm_hex[2U * i] = digits[checked_pcm.data[i] >> 4];
            pcm_hex[2U * i + 1U] = digits[checked_pcm.data[i] & 15U];
        }
        pcm_hex[2U * bo.decoded_size] = 0;
        printf(P "PCM_HEX case=%u packet=%u bytes=%" PRIu32 " core=%d hex=%s\n",
               index, packet, bo.decoded_size, xPortGetCoreID(), pcm_hex);
        total += bo.decoded_size; nz_left += nl; nz_right += nr;
        if (packet) transition_mask |= 1U << transition;
        vTaskDelay(1);
    }
    void *ch = checked; checked = NULL;
    cr = esp_vorbis_dec_close(ch);
    printf(P "CLOSE case=%u checked_rc=%d core=%d\n", index, cr, xPortGetCoreID());
    need(cr == ESP_AUDIO_ERR_OK && total == c->expected_pcm_bytes && transition_mask == 15,
         "checked_public_close_and_case_total");
    printf(P "CASE case=%u id=%s packets=%u pcm=%" PRIu32 " nz_l=%" PRIu32 " nz_r=%" PRIu32 " transitions_mask=%u core=%d\n",
        index, c->id, PACKETS, total, nz_left, nz_right, transition_mask, xPortGetCoreID());
    return total;
}
static void task(void *unused) {
    (void)unused;
    int core = xPortGetCoreID(); unsigned priority = (unsigned)uxTaskPriorityGet(NULL);
    printf(P "WORKER core=%d priority=%u configured_stack=16384\n", core, priority);
    need(core == 0 && priority == 3, "worker_core_priority");
    uint64_t total = 0; uint32_t mask = 0;
    for (unsigned i = 0; i < CORPUS_CASE_COUNT; ++i) { total += run_case(corpus_cases + i, i); mask |= 1U << i; }
    need(total == CORPUS_EXPECTED_PCM_BYTES && mask == ((UINT32_C(1) << CORPUS_CASE_COUNT) - 1U), "complete_corpus_total");
    printf(P "COMPLETE cases=%u packets=%u pcm=%" PRIu64 " cases_mask=%" PRIu32 " core=%d\n",
        CORPUS_CASE_COUNT, CORPUS_CASE_COUNT * PACKETS, total, mask, xPortGetCoreID());
    stop(NULL);
}
void app_main(void) {
    need(xPortGetCoreID() == 0, "coordinator_core0");
    need(strlen(CORPUS_CONTRACT_SHA256) == 64, "contract_hash_length");
    printf(P "BEGIN contract=%s cases=%u packets=%u coordinator=%d\n", CORPUS_CONTRACT_SHA256,
        CORPUS_CASE_COUNT, CORPUS_CASE_COUNT * PACKETS, xPortGetCoreID());
    need(xTaskCreatePinnedToCore(task, "public_corpus", 16384, NULL, 3, NULL, 0) == pdPASS, "create_worker_core0");
}
