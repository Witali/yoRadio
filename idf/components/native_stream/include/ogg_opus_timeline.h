#ifndef YORADIO_OGG_OPUS_TIMELINE_H
#define YORADIO_OGG_OPUS_TIMELINE_H

/* Application-owned metadata observer; no audio synthesis or decoder state.
 * RFC 3533 sections 5-6, RFC 7845 sections 3-6, RFC 6716 section 3.1.
 *
 * Initialize storage with {0}, then reset it before use. Feed each ORIGINAL
 * encoded byte once; decoder retries must never be fed again. No input pointer
 * is retained. feed stops at one pending event: acknowledge its generation and
 * token before feeding the unconsumed suffix. A link-end acknowledgement means
 * the caller has saved/drained the old link's metadata, not that a decoder has.
 *
 * All time values count 48 kHz frames PER CHANNEL. PROVISIONAL_END is derived
 * from an unverified page header and must not be called CRC-validated. PAGE
 * events are emitted only after the complete page's CRC and timeline checks.
 * Already emitted provisional data is invalidated by any later error. Caller
 * output ordering/buffering, rate conversion and actual trimming are separate.
 *
 * This is not a complete Ogg/Opus validator. It supports sequential logical
 * links and known mapping families 0/1/2/3/255 (RFC 8486). Concurrent serials
 * and unknown mapping families are UNSUPPORTED; sequence gaps/missing prefixes and
 * unknown completed-audio granules are UNALIGNED. It does not resynchronize,
 * validate compressed frame lengths, tags contents, or historical serial
 * uniqueness across unbounded chaining. Non-Opus links are observed as BYPASS.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    OOPT_MORE = 0, OOPT_EVENT = 1, OOPT_FINISHED = 2,
    OOPT_INVALID = -1, OOPT_UNSUPPORTED = -2, OOPT_UNALIGNED = -3,
    OOPT_TRUNCATED = -4, OOPT_LIMIT = -5
} oopt_status;

enum {
    OOPT_PAGE = 1u, OOPT_PROVISIONAL_END = 2u, OOPT_LINK_END = 4u,
    OOPT_HEAD = 8u, OOPT_TAGS = 16u
};

typedef struct {
    uint64_t token;
    uint32_t generation, link, serial, sequence, flags;
    bool crc_verified, opus, pre_skip_known, granule_known;
    bool initial_offset_known, raw_end_known;
    uint16_t pre_skip;
    uint8_t mapping, channels, streams, coupled;
    uint64_t granule, page_frames, raw_completed, initial_offset, raw_end;
} oopt_event;

/* Fields below are implementation storage, not a committed-metadata API.
 * A failed page can leave tentative packet/header state here; use events only.
 */
typedef struct {
    uint64_t token_sequence;
    uint32_t generation, link;
    oopt_status fault;
    bool pending, active, have_retired, seen_eos;
    oopt_event event;
    uint8_t header[27], lacing[255], prefix[19];
    uint16_t header_used, lace_used, segment;
    uint32_t crc, expected_crc, payload_left, segment_left;
    uint32_t serial, next_sequence, retired_serial, page_sequence;
    uint8_t page_flags, phase, prefix_used;
    uint8_t mapping, channels, streams, coupled;
    bool bad_mapping;
    bool ready, packet_open, page_head, page_tags;
    bool head_known, first_audio, offset_known, previous_gp_known;
    uint16_t pre_skip;
    uint64_t packet_bytes, page_frames, page_packets;
    uint64_t raw_completed, previous_gp, offset;
} ogg_opus_timeline;

enum { OOPT_ID = 0, OOPT_COMMENT = 1, OOPT_AUDIO = 2, OOPT_BYPASS = 3 };

static inline uint32_t oopt_le32(const uint8_t *p)
{
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}

static inline uint64_t oopt_le64(const uint8_t *p)
{
    return (uint64_t)oopt_le32(p) | (uint64_t)oopt_le32(p + 4) << 32;
}

static inline uint32_t oopt_crc_byte(uint32_t crc, uint8_t byte)
{
    crc ^= (uint32_t)byte << 24;
    for (unsigned i = 0; i < 8; ++i)
        crc = (crc << 1) ^ ((crc & UINT32_C(0x80000000)) ?
                           UINT32_C(0x04c11db7) : 0);
    return crc;
}

static inline bool oopt_add(uint64_t a, uint64_t b, uint64_t *result)
{
    if (b > UINT64_MAX - a) return false;
    *result = a + b;
    return true;
}

/* Code 3's second byte is needed only for its count, not stored frame bodies.
 * One-byte code-0/code-1 PLC requests are allowed. Coded framing validation
 * (including self-delimited streams) remains the actual decoder's job.
 */
static inline bool oopt_packet_frames(const uint8_t *prefix, size_t bytes,
                                      uint64_t *frames)
{
    if (!bytes) return false;
    unsigned config = prefix[0] >> 3;
    unsigned code = prefix[0] & 3u;
    unsigned duration, count;
    if (config < 12) {
        static const unsigned silk[4] = {480, 960, 1920, 2880};
        duration = silk[config & 3u];
    } else if (config < 16) {
        duration = (config & 1u) ? 960u : 480u;
    } else {
        duration = 120u << (config & 3u);
    }
    if (code == 3) {
        if (bytes < 2) return false;
        count = prefix[1] & 63u;
        if (!count || count > 48) return false;
    } else {
        count = code ? 2u : 1u;
        if (code == 2 && bytes < 2) return false;
    }
    if (duration * count > 5760u) return false;
    *frames = (uint64_t)duration * count;
    return true;
}

/* Reset requires initialized storage. The token counter survives even a reset
 * to the SAME generation, so an old acknowledgement cannot release new data.
 */
static inline void oopt_reset(ogg_opus_timeline *s, uint32_t generation)
{
    uint64_t sequence = s->token_sequence;
    memset(s, 0, sizeof(*s));
    s->generation = generation;
    s->token_sequence = sequence;
    if (sequence == UINT64_MAX) s->fault = OOPT_LIMIT;
}

static inline oopt_status oopt_emit(ogg_opus_timeline *s, uint32_t flags,
                                     bool verified, oopt_event *event)
{
    if (s->token_sequence == UINT64_MAX) return s->fault = OOPT_LIMIT;
    oopt_event e;
    memset(&e, 0, sizeof(e));
    e.token = ++s->token_sequence;
    e.generation = s->generation;
    e.link = s->link;
    e.serial = s->serial;
    e.sequence = s->page_sequence;
    e.flags = flags;
    e.crc_verified = verified;
    e.opus = s->head_known && s->phase != OOPT_BYPASS;
    e.pre_skip_known = e.opus;
    e.pre_skip = s->pre_skip;
    e.mapping = s->mapping;
    e.channels = s->channels;
    e.streams = s->streams;
    e.coupled = s->coupled;
    e.granule = oopt_le64(s->header + 6);
    e.granule_known = e.granule != UINT64_MAX;
    e.page_frames = verified ? s->page_frames : 0;
    e.raw_completed = s->raw_completed;
    e.initial_offset_known = s->offset_known;
    e.initial_offset = s->offset;
    s->event = e;
    s->pending = true;
    *event = e;
    return OOPT_EVENT;
}

static inline bool oopt_ack(ogg_opus_timeline *s, uint32_t generation,
                            uint64_t token)
{
    if (!s->pending || generation != s->generation || token != s->event.token)
        return false;
    if (s->event.flags & OOPT_LINK_END) {
        s->active = false;
        s->seen_eos = true;
        s->have_retired = true;
        s->retired_serial = s->serial;
    }
    s->pending = false;
    return true;
}

static inline oopt_status oopt_header(ogg_opus_timeline *s)
{
    const uint8_t *h = s->header;
    if (memcmp(h, "OggS", 4) || h[4] || (h[5] & ~7u))
        return OOPT_INVALID;
    uint32_t serial = oopt_le32(h + 14), seq = oopt_le32(h + 18);
    bool bos = (h[5] & 2u) != 0, continued = (h[5] & 1u) != 0;
    if (bos) {
        if (s->active) return OOPT_UNSUPPORTED;
        if (continued || seq || (s->have_retired && serial == s->retired_serial))
            return OOPT_INVALID;
        if (s->link == UINT32_MAX) return OOPT_LIMIT;
        ++s->link;
        s->active = true;
        s->seen_eos = false;
        s->serial = serial;
        s->phase = OOPT_ID;
        s->head_known = s->first_audio = s->offset_known = false;
        s->previous_gp_known = false;
        s->pre_skip = 0;
        s->mapping = s->channels = s->streams = s->coupled = 0;
        s->bad_mapping = false;
        s->packet_bytes = s->raw_completed = s->previous_gp = s->offset = 0;
        s->prefix_used = 0;
        s->packet_open = false;
    } else {
        if (!s->active) return OOPT_UNALIGNED;
        if (serial != s->serial) return OOPT_UNSUPPORTED;
        if (seq != s->next_sequence || continued != s->packet_open)
            return OOPT_UNALIGNED;
    }
    s->next_sequence = seq + UINT32_C(1);
    s->page_sequence = seq;
    s->page_flags = h[5];
    s->expected_crc = oopt_le32(h + 22);
    s->page_frames = s->page_packets = 0;
    s->page_head = s->page_tags = false;
    return OOPT_MORE;
}

static inline oopt_status oopt_packet_end(ogg_opus_timeline *s)
{
    if (s->phase == OOPT_ID) {
        if (s->prefix_used >= 8 && !memcmp(s->prefix, "OpusHead", 8)) {
            if (s->packet_bytes < 19 || !(s->page_flags & 2u) ||
                s->segment + 1u != s->header[26]) return OOPT_INVALID;
            if (s->prefix[8] & 0xf0u) return OOPT_UNSUPPORTED;
            s->channels = s->prefix[9];
            s->mapping = s->prefix[18];
            if (!s->channels) return OOPT_INVALID;
            if (!s->mapping) {
                if (s->channels > 2) return OOPT_INVALID;
                s->streams = 1;
                s->coupled = s->channels - 1u;
            } else {
                if (s->mapping != 1 && s->mapping != 2 && s->mapping != 3 &&
                    s->mapping != 255) return OOPT_UNSUPPORTED;
                if (s->packet_bytes < 21 || !s->streams ||
                    s->coupled > s->streams || s->bad_mapping)
                    return OOPT_INVALID;
                unsigned decoded = (unsigned)s->streams + s->coupled;
                if (s->mapping != 3 && decoded > 255) return OOPT_INVALID;
                uint64_t required = s->mapping == 3 ?
                    21u + UINT64_C(2) * s->channels * decoded :
                    21u + (uint64_t)s->channels;
                if (s->packet_bytes < required) return OOPT_INVALID;
                if (s->mapping == 1 && s->channels > 8) return OOPT_INVALID;
                if (s->mapping == 2 || s->mapping == 3) {
                    bool allowed = false;
                    for (unsigned n = 1; n <= 15; ++n)
                        if (s->channels == n * n || s->channels == n * n + 2u)
                            allowed = true;
                    if (!allowed) return OOPT_INVALID;
                }
            }
            s->pre_skip = (uint16_t)((unsigned)s->prefix[10] |
                                     (unsigned)s->prefix[11] << 8);
            s->head_known = true;
            s->page_head = true;
            s->phase = OOPT_COMMENT;
        } else {
            s->head_known = true;
            s->phase = OOPT_BYPASS;
        }
    } else if (s->phase == OOPT_COMMENT) {
        if (s->packet_bytes < 16 || s->prefix_used < 8 ||
            memcmp(s->prefix, "OpusTags", 8) ||
            s->segment + 1u != s->header[26]) return OOPT_INVALID;
        s->phase = OOPT_AUDIO;
        s->page_tags = true;
    } else if (s->phase == OOPT_AUDIO) {
        uint64_t frames;
        if (!oopt_packet_frames(s->prefix, s->prefix_used, &frames))
            return OOPT_INVALID;
        if (!oopt_add(s->page_frames, frames, &s->page_frames) ||
            s->page_packets == UINT64_MAX) return OOPT_LIMIT;
        ++s->page_packets;
    }
    s->packet_bytes = 0;
    s->prefix_used = 0;
    s->packet_open = false;
    return OOPT_MORE;
}

static inline oopt_status oopt_page_end(ogg_opus_timeline *s, oopt_event *event)
{
    if (s->crc != s->expected_crc) return OOPT_INVALID;
    bool eos = (s->page_flags & 4u) != 0;
    uint64_t gp = oopt_le64(s->header + 6), raw_end = 0;
    bool raw_end_known = false;
    if (s->phase != OOPT_BYPASS) {
        if ((s->page_head || s->page_tags) && gp != 0) return OOPT_INVALID;
        if ((s->page_flags & 2u) && s->phase == OOPT_ID &&
            s->prefix_used >= 8 && !memcmp(s->prefix, "OpusHead", 8))
            return OOPT_INVALID; /* OpusHead must complete on its BOS page. */
        if (eos && (s->phase != OOPT_AUDIO || s->packet_open))
            return OOPT_TRUNCATED;
        if (s->page_packets) {
            uint64_t total;
            if (!oopt_add(s->raw_completed, s->page_frames, &total))
                return OOPT_LIMIT;
            if (gp == UINT64_MAX) return OOPT_UNALIGNED;
            if (!s->first_audio) {
                if (eos && gp < s->pre_skip) return OOPT_INVALID;
                if (!eos && gp < s->page_frames) return OOPT_INVALID;
                s->offset = gp >= s->page_frames ? gp - s->page_frames : 0;
                s->offset_known = true;
                if (eos) {
                    raw_end = gp < total ? gp : total;
                    raw_end_known = true;
                }
            } else {
                uint64_t expected;
                if (!s->previous_gp_known || gp < s->previous_gp)
                    return OOPT_INVALID;
                if (!oopt_add(s->previous_gp, s->page_frames, &expected))
                    return OOPT_LIMIT;
                if ((!eos && gp != expected) || (eos && gp > expected))
                    return OOPT_INVALID;
                if (eos) {
                    if (!oopt_add(s->raw_completed, gp - s->previous_gp,
                                  &raw_end)) return OOPT_LIMIT;
                    raw_end_known = true;
                }
            }
            s->raw_completed = total;
            s->previous_gp = gp;
            s->previous_gp_known = s->first_audio = true;
        } else if (!s->page_head && !s->page_tags) {
            if (s->packet_open && gp != UINT64_MAX) return OOPT_INVALID;
            if (!s->packet_open && gp != UINT64_MAX &&
                gp != (s->previous_gp_known ? s->previous_gp : 0))
                return OOPT_UNALIGNED;
            if (eos) {
                if (gp == UINT64_MAX) return OOPT_UNALIGNED;
                raw_end = s->raw_completed;
                raw_end_known = true;
            }
        } else if (eos) {
            raw_end = 0; /* An empty link ending on its completed tags page. */
            raw_end_known = true;
        }
    } else if (eos && s->packet_open) {
        return OOPT_TRUNCATED;
    }
    uint32_t flags = OOPT_PAGE | (eos ? OOPT_LINK_END : 0u) |
                     (s->page_head ? OOPT_HEAD : 0u) |
                     (s->page_tags ? OOPT_TAGS : 0u);
    oopt_status result = oopt_emit(s, flags, true, event);
    if (result == OOPT_EVENT) {
        s->event.raw_end_known = raw_end_known;
        s->event.raw_end = raw_end;
        *event = s->event;
        s->header_used = s->lace_used = 0;
        s->ready = false;
        s->crc = 0;
    }
    return result;
}

/* A successful event may consume zero bytes (e.g. a nil EOS page's verified
 * event after acknowledging its provisional header). used always identifies
 * the ORIGINAL byte prefix consumed by this call, including on errors.
 */
static inline oopt_status oopt_feed(ogg_opus_timeline *s, const uint8_t *bytes,
                                    size_t size, size_t *used, oopt_event *event)
{
    if (!used || !event) return OOPT_INVALID;
    *used = 0;
    if (s->pending) { *event = s->event; return OOPT_EVENT; }
    if (s->fault) return s->fault;
    if (size && !bytes) return OOPT_INVALID;
    oopt_status result = OOPT_MORE;
    for (;;) {
        if (s->header_used < 27) {
            if (*used == size) return OOPT_MORE;
            unsigned at = s->header_used++;
            uint8_t byte = bytes[(*used)++];
            s->header[at] = byte;
            s->crc = oopt_crc_byte(s->crc, at >= 22 && at < 26 ? 0 : byte);
            if (s->header_used < 27) continue;
            result = oopt_header(s);
            if (result < 0) break;
        }
        if (s->lace_used < s->header[26]) {
            if (*used == size) return OOPT_MORE;
            uint8_t byte = bytes[(*used)++];
            s->lacing[s->lace_used++] = byte;
            s->payload_left += byte; /* At most 255 * 255. */
            s->crc = oopt_crc_byte(s->crc, byte);
            continue;
        }
        if (!s->ready) {
            s->ready = true;
            s->segment = 0;
            s->segment_left = s->header[26] ? s->lacing[0] : 0;
            if ((s->page_flags & 4u) && s->phase == OOPT_AUDIO) {
                uint64_t gp = oopt_le64(s->header + 6), end;
                uint64_t previous = s->previous_gp_known ? s->previous_gp : 0;
                if (gp != UINT64_MAX && gp >= previous &&
                    oopt_add(s->raw_completed, gp - previous, &end)) {
                    result = oopt_emit(s, OOPT_PROVISIONAL_END, false, event);
                    if (result < 0) break;
                    s->event.raw_end_known = true;
                    s->event.raw_end = end;
                    *event = s->event;
                    return OOPT_EVENT;
                }
            }
        }
        if (s->segment == s->header[26]) {
            result = oopt_page_end(s, event);
            if (result == OOPT_EVENT) return result;
            break;
        }
        if (!s->segment_left) {
            if (s->lacing[s->segment] < 255) {
                result = oopt_packet_end(s);
                if (result < 0) break;
            } else {
                s->packet_open = true;
            }
            ++s->segment;
            s->segment_left = s->segment < s->header[26] ?
                              s->lacing[s->segment] : 0;
            continue;
        }
        if (*used == size) return OOPT_MORE;
        uint8_t byte = bytes[(*used)++];
        s->crc = oopt_crc_byte(s->crc, byte);
        --s->payload_left;
        --s->segment_left;
        if (s->packet_bytes == UINT64_MAX) { result = OOPT_LIMIT; break; }
        uint64_t index = s->packet_bytes++;
        s->packet_open = true;
        if (s->phase == OOPT_ID && s->prefix_used == sizeof(s->prefix) &&
            !memcmp(s->prefix, "OpusHead", 8)) {
            if (index == 19) s->streams = byte;
            if (index == 20) s->coupled = byte;
            unsigned mapping = s->prefix[18];
            if ((mapping == 1 || mapping == 2 || mapping == 255) &&
                index >= 21 && index < 21u + (unsigned)s->prefix[9] &&
                byte != 255 && byte >= (unsigned)s->streams + s->coupled)
                s->bad_mapping = true;
        }
        unsigned prefix_limit = s->phase == OOPT_AUDIO ? 2u :
                                s->phase == OOPT_COMMENT ? 8u :
                                s->phase == OOPT_ID ? sizeof(s->prefix) : 0u;
        if (s->prefix_used < prefix_limit) s->prefix[s->prefix_used++] = byte;
    }
    s->fault = result;
    return result;
}

/* finish drains zero-byte internal work, then distinguishes an acknowledged
 * EOS boundary from missing EOS, partial headers/lacing/payload/packets.
 */
static inline oopt_status oopt_finish(ogg_opus_timeline *s, oopt_event *event)
{
    size_t used;
    oopt_status result = oopt_feed(s, NULL, 0, &used, event);
    if (result != OOPT_MORE) return result;
    if (!s->active && s->seen_eos && !s->header_used) return OOPT_FINISHED;
    return OOPT_TRUNCATED;
}

#endif
