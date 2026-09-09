#ifndef YORADIO_OGG_OPUS_DEMUX_H
#define YORADIO_OGG_OPUS_DEMUX_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OGG_OPUS_PACKET_BYTES 1536u
#define OGG_OPUS_TAG_PREFIX_BYTES 16u
#define OGG_OPUS_TAG_MAX_BYTES (1024u * 1024u)

enum {
    OGG_OPUS_DEMUX_PACKET = 0,
    OGG_OPUS_DEMUX_NEED_INPUT = 1,
    OGG_OPUS_DEMUX_ERR_ARGUMENT = -1,
    OGG_OPUS_DEMUX_ERR_FORMAT = -2,
    OGG_OPUS_DEMUX_ERR_CRC = -3,
    OGG_OPUS_DEMUX_ERR_SEQUENCE = -4,
    OGG_OPUS_DEMUX_ERR_SERIAL = -5,
    OGG_OPUS_DEMUX_ERR_CONTINUATION = -6,
    OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE = -7,
    OGG_OPUS_DEMUX_ERR_TRUNCATED = -8
};

typedef struct {
    /* Valid only during the callback. Tags retain their first 16 bytes only. */
    const uint8_t *data;
    size_t size;
    size_t stored_size;
    uint32_t packet_index; /* 0: OpusHead, 1: OpusTags, 2+: audio. */
    uint32_t serial;
    /* Raw page granule, in 48 kHz samples; belongs to page_last_packet. */
    uint64_t page_granule;
    bool page_last_packet; /* Last COMPLETE packet, even with a partial tail. */
    bool page_eos;
    bool stream_start; /* True on each OpusHead, including chained streams. */
} ogg_opus_packet_t;

typedef int (*ogg_opus_packet_callback)(void *context,
                                       const ogg_opus_packet_t *packet);

/* Fixed storage: no allocation, seeking, or full-page buffer. Members are
 * implementation state, exposed only so callers can embed the object. */
typedef struct {
    uint64_t page_granule;
    uint32_t serial;
    uint32_t next_sequence;
    uint32_t packet_index;
    uint32_t packet_size;
    uint32_t crc;
    uint32_t expected_crc;
    int error;
    uint16_t header_used;
    uint16_t lacing_used;
    uint16_t segment_index;
    uint16_t segment_used;
    uint16_t last_complete_segment;
    uint8_t segment_count;
    uint8_t page_flags;
    uint8_t phase;
    bool stream_seen;
    bool stream_ended;
    bool packet_open;
    bool allow_live_join;
    bool live_join_pending;
    uint8_t header[27];
    uint8_t lacing[255];
    uint8_t packet[OGG_OPUS_PACKET_BYTES];
} ogg_opus_demux_t;

void ogg_opus_demux_init(ogg_opus_demux_t *demux);
/* Strict by default. The opt-in live mode supports cached Head/Tags followed
 * by a later complete audio page (RFC 7845 section 3). Only that first page
 * may establish a new sequence baseline, with sequence >= 2, the same serial,
 * no continued packet and no unfinished tail. Later holes remain errors.
 * A live join whose first audio page starts with a continued packet remains
 * unsupported: never join an incomplete audio packet onto OpusTags. */
void ogg_opus_demux_init_ex(ogg_opus_demux_t *demux, bool allow_live_join);

/* Consume arbitrary input fragments and deliver at most one packet per call.
 * Return PACKET after delivery, NEED_INPUT when all supplied bytes are used,
 * or a negative error. *consumed is exact, including on error. PACKET can
 * consume zero bytes (a zero terminating lace after a previous callback).
 * data may be NULL only when length == 0; callback and consumed are required.
 * Negative callback results propagate and permanently stop this stream;
 * init() is required to recover from any parsing/callback error.
 *
 * CRC is checked at the END of each page. A packet ending at that boundary
 * is checked before delivery. Earlier packets may already have been handed
 * to the decoder, INCLUDING the last complete packet followed by a partial
 * next packet. Their PCM cannot be recalled on a later CRC failure. This
 * deliberate streaming tradeoff avoids a second packet/full-page buffer.
 *
 * The two header signatures, minimum sizes, Ogg framing and header page
 * placement are checked here. The decoder must validate OpusHead version,
 * channel mapping, pre-skip, gain and audio packet contents. Tags are opaque
 * metadata: their body is skipped, not parsed or exposed as trusted text.
 * Concurrent streams, sequence holes, reused adjacent chain serials and
 * malformed continuations are rejected; sequential EOS/BOS chains reset the
 * packet index. Granule-to-duration checks and trimming belong to the codec.
 */
int ogg_opus_demux_feed(ogg_opus_demux_t *demux, const uint8_t *data,
                       size_t length, size_t *consumed,
                       ogg_opus_packet_callback callback, void *context);

/* Strict finite-stream EOF check: requires EOS and no partial next page.
 * Live callers need not call this while waiting for more network data. */
int ogg_opus_demux_finish(const ogg_opus_demux_t *demux);

#ifdef __cplusplus
}
#endif
#endif
