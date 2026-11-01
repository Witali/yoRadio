#ifndef YORADIO_OPUS_PCM_TRIM_H
#define YORADIO_OPUS_PCM_TRIM_H

/* Clip raw, untrimmed decoder output in 48 kHz frames PER CHANNEL.
 * This does not derive container metadata or change samples. The caller must
 * establish raw-output alignment independently, then configure CRC-verified
 * headers/end bounds BEFORE decoding the corresponding page. Buffer views
 * borrow the caller's PCM only for its current synchronous send operation.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    OPT_OK = 0, OPT_INVALID = -1, OPT_UNALIGNED = -2, OPT_LIMIT = -3
} opus_pcm_trim_status;

typedef struct {
    uint64_t raw_position, emitted_end, end, total;
    uint32_t generation;
    uint16_t pre_skip;
    uint8_t channels;
    bool active, end_known;
} opus_pcm_trim;

typedef struct { size_t offset, size; } opus_pcm_span;

static inline void opt_reset(opus_pcm_trim *s)
{
    memset(s, 0, sizeof(*s));
}

static inline opus_pcm_trim_status opt_begin(opus_pcm_trim *s,
    uint32_t generation, uint16_t pre_skip, uint8_t channels)
{
    if (!channels || s->active) return OPT_INVALID;
    opt_reset(s);
    s->active = true;
    s->generation = generation;
    s->pre_skip = pre_skip;
    s->channels = channels;
    return OPT_OK;
}

static inline opus_pcm_trim_status opt_end(opus_pcm_trim *s,
    uint32_t generation, uint64_t raw_end, uint64_t raw_total)
{
    if (!s->active || s->generation != generation || s->end_known ||
        raw_end > raw_total) return OPT_INVALID;
    if (s->emitted_end > raw_end || s->raw_position > raw_total)
        return OPT_UNALIGNED;
    s->end = raw_end;
    s->total = raw_total;
    s->end_known = true;
    return OPT_OK;
}

/* On error state and span are unchanged. On success raw_position advances by
 * ALL decoded frames, including skipped/padded frames, never only sent frames.
 * A failed/cancelled downstream send must terminate/reset this decoder owner;
 * it must not replay the same PCM through this advancing function.
 */
static inline opus_pcm_trim_status opt_clip(opus_pcm_trim *s,
    uint32_t generation, uint32_t rate, uint8_t channels, uint8_t bits,
    size_t bytes, opus_pcm_span *span)
{
    if (!span || !s->active || generation != s->generation || !channels ||
        channels != s->channels || rate != 48000 ||
        (bits != 8 && bits != 16 && bits != 24 && bits != 32))
        return OPT_INVALID;
    size_t width = (size_t)channels * (bits / 8u);
    if (bytes % width) return OPT_UNALIGNED;
    uint64_t frames = bytes / width;
    if (frames > UINT64_MAX - s->raw_position) return OPT_LIMIT;
    uint64_t next = s->raw_position + frames;
    if (s->end_known && next > s->total) return OPT_UNALIGNED;
    uint64_t first = s->raw_position > s->pre_skip ?
                     s->raw_position : s->pre_skip;
    uint64_t last = s->end_known && s->end < next ? s->end : next;
    opus_pcm_span result = {0, 0};
    if (first < last) {
        result.offset = (size_t)(first - s->raw_position) * width;
        result.size = (size_t)(last - first) * width;
        s->emitted_end = last;
    }
    s->raw_position = next;
    *span = result;
    return OPT_OK;
}

static inline opus_pcm_trim_status opt_finish(const opus_pcm_trim *s,
                                              uint32_t generation)
{
    if (!s->active || generation != s->generation || !s->end_known)
        return OPT_INVALID;
    return s->raw_position == s->total ? OPT_OK : OPT_UNALIGNED;
}

#endif
