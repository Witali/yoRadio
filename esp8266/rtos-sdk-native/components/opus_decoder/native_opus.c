#include "native_opus.h"
#include "opus.h"
#include "opus_memory.h"

#include <string.h>

static uint16_t read16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int fail(native_opus_t *s, int error) {
    if (s->decoder_ready) {
        /* An arena OOM can follow updates to history or energy state. Never
         * allow a partially decoded packet to become the next prediction. */
        (void)opus_decoder_ctl((OpusDecoder *)s->config.decoder_state,
                               OPUS_RESET_STATE);
    }
    s->last_error = error;
    return error;
}

size_t native_opus_decoder_size(void) {
    return (size_t)opus_decoder_get_size(1);
}

static bool valid_memory(native_opus_t *s, const native_opus_config_t *c) {
    if (!c->decoder_state || !c->scratch || !c->iram || !c->pcm || !c->output ||
        c->decoder_state_bytes < native_opus_decoder_size() ||
        !c->scratch_bytes || c->iram_bytes < NATIVE_OPUS_IRAM_BYTES ||
        c->pcm_samples < NATIVE_OPUS_MAX_SAMPLES ||
        ((uintptr_t)c->decoder_state & 7u) || ((uintptr_t)c->scratch & 7u) ||
        ((uintptr_t)c->iram & 7u) || ((uintptr_t)c->pcm & 1u)) return false;
    const uintptr_t bases[] = {(uintptr_t)s, (uintptr_t)c->decoder_state,
        (uintptr_t)c->scratch, (uintptr_t)c->iram, (uintptr_t)c->pcm};
    const size_t sizes[] = {sizeof(*s), c->decoder_state_bytes,
        c->scratch_bytes, NATIVE_OPUS_IRAM_BYTES,
        NATIVE_OPUS_MAX_SAMPLES * sizeof(int16_t)};
    for (size_t i = 0; i < 5; ++i) {
        if (sizes[i] > UINTPTR_MAX - bases[i]) return false;
        for (size_t j = 0; j < i; ++j)
            if (bases[i] < bases[j] + sizes[j] &&
                bases[j] < bases[i] + sizes[i]) return false;
    }
    return true;
}

int native_opus_init(native_opus_t *s, const native_opus_config_t *config) {
    if (!s || !config) return NATIVE_OPUS_ERR_ARGUMENT;
    const native_opus_config_t copy = *config;
    /* Validate before clearing: an accidentally overlapping object must not
     * clear a caller's PCM, history, or state buffer. */
    if (!valid_memory(s, &copy)) return NATIVE_OPUS_ERR_MEMORY;
    memset(s, 0, sizeof(*s));
    s->config = copy;
    ogg_opus_demux_init(&s->demux);
    yoradio_opus_memory_bind(copy.scratch, copy.scratch_bytes,
                             copy.iram, NATIVE_OPUS_IRAM_BYTES);
    s->libopus_error = opus_decoder_init((OpusDecoder *)copy.decoder_state,
                                         NATIVE_OPUS_SAMPLE_RATE, 1);
    if (s->libopus_error != OPUS_OK) return fail(s, NATIVE_OPUS_ERR_MEMORY);
    s->decoder_ready = true;
    return 0;
}

int native_opus_reset(native_opus_t *s) {
    if (!s || !s->decoder_ready) return NATIVE_OPUS_ERR_ARGUMENT;
    return native_opus_init(s, &s->config);
}

static int read_head(native_opus_t *s, const ogg_opus_packet_t *p) {
    /* The demux already checks EOS before each chained BOS. */
    if (!p->stream_start || p->stored_size < 19 ||
        memcmp(p->data, "OpusHead", 8))
        return fail(s, NATIVE_OPUS_ERR_HEADER);
    if (p->data[8] > 15) return fail(s, NATIVE_OPUS_ERR_VERSION);
    if (p->data[9] < 1 || p->data[9] > 2 || p->data[18] != 0)
        return fail(s, NATIVE_OPUS_ERR_MAPPING);
    if (p->data[8] <= 1 && p->size != 19)
        return fail(s, NATIVE_OPUS_ERR_HEADER);
    s->libopus_error = opus_decoder_ctl((OpusDecoder *)s->config.decoder_state,
                                        OPUS_RESET_STATE);
    if (s->libopus_error != OPUS_OK) return fail(s, NATIVE_OPUS_ERR_DECODE);
    const uint16_t gain_bits = read16(p->data + 16);
    const int gain = gain_bits >= 32768u ? (int)gain_bits - 65536 : gain_bits;
    s->libopus_error = opus_decoder_ctl((OpusDecoder *)s->config.decoder_state,
                                        OPUS_SET_GAIN(gain));
    if (s->libopus_error != OPUS_OK) return fail(s, NATIVE_OPUS_ERR_DECODE);
    s->input_channels = p->data[9];
    s->pre_skip = read16(p->data + 10);
    s->skip_remaining = s->pre_skip;
    s->chain_decoded = s->granule_offset = s->previous_granule = 0;
    s->granule_known = s->chain_eos = false;
    s->stage = 1;
    ++s->chains;
    return 0;
}

static int packet_received(void *context, const ogg_opus_packet_t *p) {
    native_opus_t *s = context;
    if (p->packet_index == 0) return read_head(s, p);
    if (p->packet_index == 1) {
        if (s->stage != 1 || p->stored_size < 16 ||
            memcmp(p->data, "OpusTags", 8)) return fail(s, NATIVE_OPUS_ERR_HEADER);
        s->stage = 2;
        return 0;
    }
    if (s->stage != 2 || s->chain_eos) return fail(s, NATIVE_OPUS_ERR_HEADER);
    if (p->size > NATIVE_OPUS_MAX_PACKET)
        return fail(s, NATIVE_OPUS_ERR_PACKET_SIZE);
    if (!p->size || p->stored_size != p->size)
        return fail(s, NATIVE_OPUS_ERR_DECODE);
    const int samples = opus_packet_get_nb_samples(p->data, (opus_int32)p->size,
                                                   NATIVE_OPUS_SAMPLE_RATE);
    if (samples <= 0) return fail(s, NATIVE_OPUS_ERR_DECODE);
    if (samples > (int)NATIVE_OPUS_MAX_SAMPLES)
        return fail(s, NATIVE_OPUS_ERR_DURATION);
    if (s->chain_decoded > INT64_MAX - (uint64_t)samples)
        return fail(s, NATIVE_OPUS_ERR_GRANULE);
    const uint64_t begin = s->chain_decoded;
    const uint64_t end = begin + (unsigned)samples;
    uint64_t keep_end = end;

    /* RFC 7845 4.4/4.5: initial page granule can include an arbitrary
     * positive offset. Pre-skip always applies to decoded samples, not to
     * this offset. The first EOS page instead starts at zero if trimmed. */
    if (p->page_eos) {
        if (p->page_granule > INT64_MAX || p->page_granule < s->pre_skip ||
            (s->granule_known && p->page_granule < s->previous_granule))
            return fail(s, NATIVE_OPUS_ERR_GRANULE);
        const uint64_t limit = p->page_granule - s->granule_offset;
        if (keep_end > limit) keep_end = limit;
    }
    if (p->page_last_packet) {
        if (p->page_granule > INT64_MAX) return fail(s, NATIVE_OPUS_ERR_GRANULE);
        if (!s->granule_known) {
            if (p->page_granule < end && !p->page_eos)
                return fail(s, NATIVE_OPUS_ERR_GRANULE);
            s->granule_offset = p->page_granule > end ? p->page_granule - end : 0;
            s->granule_known = true;
        } else {
            if (s->granule_offset > INT64_MAX - end)
                return fail(s, NATIVE_OPUS_ERR_GRANULE);
            const uint64_t expected = s->granule_offset + end;
            if (p->page_eos ? p->page_granule > expected : p->page_granule != expected)
                return fail(s, NATIVE_OPUS_ERR_GRANULE);
        }
        s->previous_granule = p->page_granule;
    }

    s->libopus_error = yoradio_opus_decode_bounded(s->config.decoder_state,
        p->data, (int)p->size, s->config.pcm, NATIVE_OPUS_MAX_SAMPLES);
    if (s->libopus_error < 0)
        return fail(s, s->libopus_error == OPUS_ALLOC_FAIL ?
                    NATIVE_OPUS_ERR_MEMORY : NATIVE_OPUS_ERR_DECODE);
    if (s->libopus_error != samples) return fail(s, NATIVE_OPUS_ERR_DECODE);
    s->chain_decoded = end;
    s->decoded_samples += (unsigned)samples;
    ++s->audio_packets;
    s->bitrate_bps = (uint32_t)((uint64_t)p->size * 8u *
                               NATIVE_OPUS_SAMPLE_RATE / (unsigned)samples);
    const size_t skip = s->skip_remaining < (unsigned)samples ?
                        s->skip_remaining : (unsigned)samples;
    s->skip_remaining -= (uint32_t)skip;
    const uint64_t output_begin = begin + skip;
    const size_t output = keep_end > output_begin ? (size_t)(keep_end - output_begin) : 0;
    if (output && !s->config.output(s->config.output_ctx, s->config.pcm + skip,
                                     output, s->bitrate_bps))
        return fail(s, NATIVE_OPUS_ERR_CANCELLED);
    s->output_samples += output;
    if (p->page_eos && p->page_last_packet) {
        if (s->skip_remaining) return fail(s, NATIVE_OPUS_ERR_GRANULE);
        s->chain_eos = true;
    }
    return 0;
}

int native_opus_feed(native_opus_t *s, const uint8_t *data, size_t length,
                     size_t *consumed) {
    if (consumed) *consumed = 0;
    if (!s || !s->decoder_ready || !consumed || (!data && length))
        return NATIVE_OPUS_ERR_ARGUMENT;
    if (s->last_error) return s->last_error;
    const int result = ogg_opus_demux_feed(&s->demux, data, length, consumed,
                                          packet_received, s);
    if (result < 0) {
        if (s->last_error) return s->last_error;
        s->demux_error = result;
        return fail(s, result == OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE ?
                    NATIVE_OPUS_ERR_PACKET_SIZE : NATIVE_OPUS_ERR_DEMUX);
    }
    return result == OGG_OPUS_DEMUX_PACKET ? NATIVE_OPUS_PACKET : NATIVE_OPUS_NEED_INPUT;
}

int native_opus_finish(native_opus_t *s) {
    if (!s || !s->decoder_ready) return NATIVE_OPUS_ERR_ARGUMENT;
    if (s->last_error) return s->last_error;
    s->demux_error = ogg_opus_demux_finish(&s->demux);
    if (s->demux_error || s->stage != 2 || !s->granule_known || s->skip_remaining)
        return fail(s, NATIVE_OPUS_ERR_TRUNCATED);
    return 0;
}

const char *native_opus_error_string(int error) {
    switch (error) {
        case NATIVE_OPUS_NEED_INPUT: return "need input";
        case NATIVE_OPUS_PACKET: return "packet decoded";
        case NATIVE_OPUS_ERR_ARGUMENT: return "invalid argument";
        case NATIVE_OPUS_ERR_MEMORY: return "insufficient or invalid codec memory";
        case NATIVE_OPUS_ERR_HEADER: return "invalid Opus header";
        case NATIVE_OPUS_ERR_VERSION: return "unsupported Opus header version";
        case NATIVE_OPUS_ERR_MAPPING: return "unsupported Opus channel mapping";
        case NATIVE_OPUS_ERR_DURATION: return "Opus packet exceeds 20 ms";
        case NATIVE_OPUS_ERR_DECODE: return "invalid Opus audio packet";
        case NATIVE_OPUS_ERR_GRANULE: return "invalid Opus granule position";
        case NATIVE_OPUS_ERR_CANCELLED: return "PCM output cancelled";
        case NATIVE_OPUS_ERR_DEMUX: return "invalid Ogg stream";
        case NATIVE_OPUS_ERR_TRUNCATED: return "truncated Ogg Opus stream";
        case NATIVE_OPUS_ERR_PACKET_SIZE: return "Ogg Opus packet exceeds configured limit";
        default: return "unknown Opus error";
    }
}
