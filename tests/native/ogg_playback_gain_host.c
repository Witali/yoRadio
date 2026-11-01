/* Actual wrapper with explicit public decoder/allocator/output seams. */
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned allocations, fail_allocation, live_allocations;
static void *tracked_realloc(void *p, size_t bytes)
{
    ++allocations;
    if (allocations == fail_allocation) return NULL;
    bool fresh = !p;
    void *next = realloc(p, bytes);
    assert(next);
    if (fresh) ++live_allocations;
    return next;
}
static void tracked_free(void *p)
{
    if (p) { assert(live_allocations); --live_allocations; }
    free(p);
}
#define realloc tracked_realloc
#define free tracked_free
#include "ogg_playback.h"
#undef realloc
#undef free

enum mode {
    NORMAL, RESIZE_ZERO, RESIZE_PARTIAL, RESIZE_ALL, STALL_HEAD,
    CANCEL_BEFORE, CANCEL_AFTER, YIELD_CANCEL, OPEN_MEMORY, PROCESS_FAIL,
    INFO_FAIL, BAD_RATE, BAD_CHANNEL, BAD_BITS, BAD_PCM_SIZE, BAD_CONSUMED,
    BAD_DECODED, BAD_NEEDED, BAD_RESIZE_OUTPUT, OUTPUT_FAIL, MODES
};
static const char *names[] = {
    "normal","resize_zero","resize_partial","resize_all_nonterminal","retained_head",
    "cancel_before","cancel_after","yield_cancel","open_memory","process_fail",
    "info_fail","bad_rate","bad_channel","bad_bits","bad_pcm_size","bad_consumed",
    "bad_decoded","bad_needed","bad_resize_output","output_failure"
};
typedef struct {
    enum mode mode;
    ogg_playback *owner;
    unsigned opens, closes, calls, outputs, yields, retries, stage, audio;
    unsigned first_sample, last_sample;
    int16_t expected_gain;
    size_t bytes;
    bool live, cancelled, stalled, resized, cached, cleanup;
    uint8_t *retry_pointer;
    uint32_t retry_bytes;
    bool retry_eos;
} model;
static model state;

esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,
                                         esp_audio_simple_dec_handle_t *handle)
{
    assert(!state.live && cfg->dec_type == ESP_AUDIO_SIMPLE_DEC_TYPE_OGG &&
           !cfg->use_frame_dec && !cfg->dec_cfg && !cfg->cfg_size);
    assert(state.owner->input.ready && state.owner->input.event.crc_verified);
    ++state.opens;
    if (state.mode == OPEN_MEMORY) return ESP_AUDIO_ERR_MEM_LACK;
    state.live = true;
    state.stage = state.audio = 0;
    const uint8_t *page=state.owner->input.page;
    size_t payload=27u+page[26];
    assert(state.owner->input.size>=payload+19 && !memcmp(page+payload,"OpusHead",8));
    unsigned gain=page[payload+16]|(unsigned)page[payload+17]<<8;
    state.expected_gain=(int16_t)(gain<32768u?(int32_t)gain:(int32_t)gain-65536);
    *handle = &state;
    return ESP_AUDIO_ERR_OK;
}

static uint32_t first_page_size(const esp_audio_simple_dec_raw_t *raw)
{
    assert(raw->len >= 27 && !memcmp(raw->buffer, "OggS", 4));
    uint32_t n = 27 + raw->buffer[26];
    assert(n <= raw->len);
    for (unsigned i = 27; i < 27u + raw->buffer[26]; ++i) n += raw->buffer[i];
    assert(n <= raw->len);
    return n;
}

esp_audio_err_t esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *frame)
{
    assert(handle == &state && state.live && ++state.calls < 200);
    assert(state.owner->input.ready && state.owner->input.event.crc_verified);
    if (state.mode == CANCEL_AFTER) state.cancelled = true;
    if (state.mode == PROCESS_FAIL) return ESP_AUDIO_ERR_FAIL;
    if (state.mode == BAD_CONSUMED) { raw->consumed = raw->len + 1; return ESP_AUDIO_ERR_OK; }
    if (state.mode == BAD_DECODED) { frame->decoded_size = frame->len + 1; return ESP_AUDIO_ERR_OK; }
    if (state.stage < 2) {
        if (state.mode == STALL_HEAD && !state.stalled) {
            state.stalled = true;
            return ESP_AUDIO_ERR_OK;
        }
        raw->consumed = first_page_size(raw);
        ++state.stage;
        return ESP_AUDIO_ERR_OK;
    }
    if (state.cached) {
        assert(raw->buffer == state.retry_pointer && raw->len == state.retry_bytes && raw->eos == state.retry_eos);
        assert(frame->len >= 3840);
        ++state.retries;
        state.cached = false;
    } else if (!raw->len) {
        assert(raw->eos);
        return ESP_AUDIO_ERR_OK;
    } else if (!state.resized &&
               (state.mode == RESIZE_ZERO || state.mode == RESIZE_PARTIAL ||
                state.mode == RESIZE_ALL || state.mode == BAD_NEEDED || state.mode == BAD_RESIZE_OUTPUT)) {
        state.resized = state.cached = true;
        frame->needed_size = state.mode == BAD_NEEDED ? frame->len : 3840;
        if (state.mode == BAD_RESIZE_OUTPUT) frame->decoded_size = 4;
        raw->consumed = state.mode == RESIZE_PARTIAL ? 2 : state.mode == RESIZE_ALL ? raw->len : 0;
        state.retry_pointer = raw->buffer + raw->consumed;
        state.retry_bytes = raw->len - raw->consumed;
        state.retry_eos = raw->eos;
        return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
    }
    assert(frame->len >= 3840);
    raw->consumed = raw->len;
    frame->decoded_size = state.mode == BAD_PCM_SIZE ? 3839 : 3840;
    for (unsigned i = 0; i < 960; ++i) {
        int16_t pair[2] = {(int16_t)(state.audio * 960 + i), (int16_t)(state.audio * 960 + i)};
        memcpy(frame->buffer + i * 4u, pair, sizeof(pair));
    }
    ++state.audio;
    return ESP_AUDIO_ERR_OK;
}

esp_audio_err_t esp_audio_simple_dec_get_info(esp_audio_simple_dec_handle_t handle,
                                             esp_audio_simple_dec_info_t *info)
{
    assert(handle == &state && state.live);
    if (state.mode == INFO_FAIL) return ESP_AUDIO_ERR_FAIL;
    *info = (esp_audio_simple_dec_info_t){.sample_rate=state.mode == BAD_RATE ? 24000 : 48000,
        .channel=state.mode == BAD_CHANNEL ? 1 : 2, .bits_per_sample=state.mode == BAD_BITS ? 12 : 16};
    return ESP_AUDIO_ERR_OK;
}

void esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle)
{
    assert(handle == &state && state.live);
    if (!state.cleanup) assert(state.owner->input.ready &&
        (state.owner->input.event.flags & OOPT_LINK_END) && state.owner->input.timeline.pending);
    ++state.closes;
    state.live = false;
}

static bool cancelled(void *context)
{
    assert(context == &state);
    return state.cancelled || state.mode == CANCEL_BEFORE;
}
static bool output(void *context, const esp_audio_simple_dec_info_t *info,
                   const uint8_t *pcm, size_t bytes, int16_t header_gain_q8)
{
    assert(context == &state && state.owner->input.ready && state.owner->input.event.crc_verified);
    assert(info->sample_rate == 48000 && info->channel == 2 && info->bits_per_sample == 16 && bytes && !(bytes % 4));
    assert(header_gain_q8==state.expected_gain);
    int16_t first, last;
    memcpy(&first, pcm, sizeof(first));
    memcpy(&last, pcm + bytes - 4, sizeof(last));
    if (!state.outputs) state.first_sample = (unsigned)first;
    state.last_sample = (unsigned)last;
    state.bytes += bytes;
    ++state.outputs;
    return state.mode != OUTPUT_FAIL;
}
static void yield(void *context)
{
    assert(context == &state);
    ++state.yields;
    if (state.mode == YIELD_CANCEL) state.cancelled = true;
}

typedef struct { uint8_t p[4096]; size_t n; } encoded;
static uint32_t crc(const uint8_t *p, size_t n)
{
    uint32_t value = 0;
    for (size_t i = 0; i < n; ++i) {
        unsigned byte = i >= 22 && i < 26 ? 0 : p[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            bool a = (value >> 31) != 0, b = (byte & (0x80u >> bit)) != 0;
            value <<= 1;
            if (a != b) value ^= UINT32_C(0x04c11db7);
        }
    }
    return value;
}
static void put32(uint8_t *p, uint32_t v)
{
    for (unsigned i = 0; i < 4; ++i) p[i] = (uint8_t)(v >> (8u * i));
}
static size_t add_page(encoded *b, unsigned serial, unsigned seq, unsigned flags,
                       unsigned gp, const uint8_t *payload, size_t n)
{
    size_t at = b->n;
    assert(n < 255 && 28 + n <= sizeof(b->p) - at);
    uint8_t *p = b->p + at;
    memset(p, 0, 28);
    memcpy(p, "OggS", 4);
    p[5] = (uint8_t)flags;
    put32(p + 6, gp);
    put32(p + 14, serial);
    put32(p + 18, seq);
    p[26] = 1; p[27] = (uint8_t)n;
    memcpy(p + 28, payload, n);
    b->n += 28 + n;
    put32(p + 22, crc(p, 28 + n));
    return at;
}
static int16_t test_gain_q8;
static size_t add_link(encoded *b, unsigned serial, bool two_audio)
{
    uint8_t head[19] = "OpusHead", tags[16] = "OpusTags", audio = 0xf8;
    head[8] = 1; head[9] = 2; head[10] = 56; head[11] = 1; /* pre-skip312 */
    put32(head + 12, 48000);
    int32_t gain=(serial-77u)%3u==0 ? test_gain_q8 : (serial-77u)%3u==1 ? -(int32_t)test_gain_q8 : 0;
    if (gain>32767) gain=32767;
    unsigned field=(unsigned)(uint16_t)(int16_t)gain;
    head[16]=(uint8_t)field;head[17]=(uint8_t)(field>>8);
    add_page(b, serial, 0, 2, 0, head, sizeof(head));
    add_page(b, serial, 1, 0, 0, tags, sizeof(tags));
    size_t final;
    if (two_audio) {
        add_page(b, serial, 2, 0, 960, &audio, 1);
        final = add_page(b, serial, 3, 4, 1500, &audio, 1);
    } else final = add_page(b, serial, 2, 4, 700, &audio, 1);
    return final;
}

static void clear(ogg_playback *s, esp_audio_simple_dec_handle_t *decoder,
                   uint8_t **pcm, decoder_pending_input_t *pending)
{
    state.cleanup = true;
    if (*decoder) esp_audio_simple_dec_close(*decoder);
    *decoder = NULL;
    decoder_pending_input_clear(pending);
    tracked_free(*pcm); *pcm = NULL;
    ogp_reset(s, s->generation + 1);
    assert(!state.live && !live_allocations && !pending->data && !s->input.page && !s->trim.active && !ogp_has_input(s));
}

static unsigned cases;
static unsigned run_case(enum mode mode, size_t chunk, unsigned fail_at, bool crc_bad, unsigned links)
{
    assert(!live_allocations);
    allocations = 0; fail_allocation = 0;
    ogg_playback s = {0};
    ogp_reset(&s, 9);
    state = (model){.mode=mode, .owner=&s};
    decoder_pending_input_t pending = {0};
    esp_audio_simple_dec_handle_t decoder = NULL;
    size_t capacity = mode == RESIZE_ZERO || mode == RESIZE_PARTIAL || mode == RESIZE_ALL ||
                      mode == BAD_NEEDED || mode == BAD_RESIZE_OUTPUT ? 512 : 4096;
    uint8_t *pcm = tracked_realloc(NULL, capacity);
    fail_allocation = fail_at;
    encoded bytes = {{0}, 0};
    size_t final = 0;
    for (unsigned i = 0; i < links; ++i) final = add_link(&bytes, i + 77, mode == RESIZE_ALL);
    if (crc_bad) bytes.p[final + 22] ^= 1;
    ogg_playback_callbacks cb = {.cancelled=cancelled,.output=output,.yield=yield,.context=&state};
    ogg_playback_status status = OGP_OK;
    int32_t cause = 0;
    for (size_t at = 0; at < bytes.n && status == OGP_OK;) {
        size_t n = chunk ? chunk : bytes.n;
        if (n > bytes.n - at) n = bytes.n - at;
        status = ogp_feed(&s, bytes.p + at, n, false, &decoder, &pcm, &capacity, &pending, &cb, &cause);
        memset(bytes.p + at, 0xa5, n);
        at += n;
    }
    if (status == OGP_OK) status = ogp_feed(&s, NULL, 0, true, &decoder, &pcm, &capacity, &pending, &cb, &cause);
    ogg_playback_status expected = OGP_OK;
    if (fail_at) expected = OGP_MEMORY;
    else if (crc_bad) expected = OGP_CONTAINER;
    else if (mode == CANCEL_BEFORE || mode == CANCEL_AFTER || mode == YIELD_CANCEL) expected = OGP_CANCELLED;
    else if (mode == OPEN_MEMORY) expected = OGP_MEMORY;
    else if (mode == PROCESS_FAIL || mode == BAD_CONSUMED || mode == BAD_DECODED || mode == BAD_NEEDED || mode == BAD_RESIZE_OUTPUT) expected = OGP_DECODER;
    else if (mode == INFO_FAIL || mode == BAD_RATE || mode == BAD_CHANNEL || mode == BAD_BITS || mode == BAD_PCM_SIZE) expected = OGP_INFO;
    else if (mode == OUTPUT_FAIL) expected = OGP_OUTPUT;
    printf("{\"case\":%u,\"mode\":\"%s\",\"chunk\":%zu,\"oom\":%u,\"crc_bad\":%s,"
           "\"status\":%d,\"expected\":%d,\"cause\":%" PRId32 ",\"opens\":%u,\"closes\":%u,"
           "\"calls\":%u,\"outputs\":%u,\"bytes\":%zu,\"retries\":%u,\"yields\":%u,\"passed\":%s}\n",
           cases, names[mode], chunk, fail_at, crc_bad ? "true" : "false", status, expected, cause,
           state.opens, state.closes, state.calls, state.outputs, state.bytes, state.retries, state.yields,
           status == expected ? "true" : "false");
    assert(fflush(stdout) == 0 && status == expected);
    if (status == OGP_OK) {
        assert(!decoder && !pending.size && !s.input.ready && s.input.timeline.link == links);
        assert(state.opens == links && state.closes == links && state.first_sample == 312);
        assert(state.last_sample == (mode == RESIZE_ALL ? 1499 : 699));
        assert(state.bytes == (mode == RESIZE_ALL ? 4752u : 1552u) * links);
        if (mode == RESIZE_ZERO || mode == RESIZE_PARTIAL || mode == RESIZE_ALL) assert(state.retries == 1 && capacity == 3840);
    }
    if (crc_bad) assert(!state.outputs && state.calls == 2);
    if (mode == YIELD_CANCEL && !fail_at) assert(state.yields == 1 && s.calls == 32);
    unsigned used_allocations = allocations;
    clear(&s, &decoder, &pcm, &pending);
    ++cases;
    return used_allocations;
}

int main(void)
{
    const size_t chunks[] = {0, 1, 27, 257};
    for (unsigned mode = NORMAL; mode < MODES; ++mode)
    for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i)
        run_case((enum mode)mode, chunks[i], 0, false, mode == YIELD_CANCEL ? 8 : 1);
    for (unsigned i = 0; i < sizeof(chunks) / sizeof(chunks[0]); ++i) {
        run_case(NORMAL, chunks[i], 0, true, 1);
        run_case(NORMAL, chunks[i], 0, false, 2);
    }
    unsigned baseline = run_case(RESIZE_ZERO, 0, 0, false, 1);
    for (unsigned ordinal = 2; ordinal <= baseline; ++ordinal) {
        run_case(RESIZE_ZERO, 0, ordinal, false, 1);
        run_case(RESIZE_ZERO, 0, 0, false, 1);
    }
    baseline = run_case(STALL_HEAD, 0, 0, false, 1);
    for (unsigned ordinal = 2; ordinal <= baseline; ++ordinal) {
        run_case(STALL_HEAD, 0, ordinal, false, 1);
        run_case(STALL_HEAD, 0, 0, false, 1);
    }
    const int16_t gains[]={0,1536,-1536,5120,12288,32767,-32768};
    for (unsigned g=0;g<sizeof(gains)/sizeof(gains[0]);++g) {
        test_gain_q8=gains[g];
        for (unsigned i=0;i<sizeof(chunks)/sizeof(chunks[0]);++i) run_case(NORMAL,chunks[i],0,false,3);
    }
    printf("{\"suite\":\"ogg-playback-gain-host\",\"cases\":%u,\"passed\":true,\"actual_wrapper\":true,"
           "\"vendor_executed\":false,\"production_selected\":false,\"live_allocations\":%u}\n", cases, live_allocations);
    return 0;
}
