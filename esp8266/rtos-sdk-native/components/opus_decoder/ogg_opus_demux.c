#include "ogg_opus_demux.h"

#include <string.h>

enum { PHASE_HEADER, PHASE_LACING, PHASE_BODY };
enum { FLAG_CONTINUED = 1, FLAG_BOS = 2, FLAG_EOS = 4 };

/* MSB-first Ogg CRC, polynomial 0x04c11db7, zero initial/final xor.
 * Word entries also avoid byte loads from a flash-resident lookup table. */
static const uint32_t crc_nibbles[16] = {
    0x00000000u, 0x04c11db7u, 0x09823b6eu, 0x0d4326d9u,
    0x130476dcu, 0x17c56b6bu, 0x1a864db2u, 0x1e475005u,
    0x2608edb8u, 0x22c9f00fu, 0x2f8ad6d6u, 0x2b4bcb61u,
    0x350c9b64u, 0x31cd86d3u, 0x3c8ea00au, 0x384fbdbdu
};

static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static uint32_t crc_byte(uint32_t crc, uint8_t value) {
    crc ^= (uint32_t)value << 24;
    crc = (crc << 4) ^ crc_nibbles[crc >> 28];
    return (crc << 4) ^ crc_nibbles[crc >> 28];
}

static uint32_t crc_bytes(uint32_t crc, const uint8_t *data, size_t size) {
    for (size_t i = 0; i < size; ++i) crc = crc_byte(crc, data[i]);
    return crc;
}

static int fail(ogg_opus_demux_t *d, int error) {
    d->error = error;
    return error;
}

void ogg_opus_demux_init(ogg_opus_demux_t *d) {
    if (d) memset(d, 0, sizeof(*d));
}

static int begin_page(ogg_opus_demux_t *d) {
    const uint8_t *h = d->header;
    if (memcmp(h, "OggS", 4) != 0 || h[4] != 0 || (h[5] & ~7u))
        return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    const uint32_t serial = read32(h + 14);
    const uint32_t sequence = read32(h + 18);
    d->page_flags = h[5];
    d->segment_count = h[26];
    d->page_granule = (uint64_t)read32(h + 6) |
                      ((uint64_t)read32(h + 10) << 32);
    if (!d->stream_seen || d->stream_ended) {
        if (!(h[5] & FLAG_BOS) || (h[5] & (FLAG_EOS | FLAG_CONTINUED)))
            return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
        if (d->stream_seen && serial == d->serial)
            return fail(d, OGG_OPUS_DEMUX_ERR_SERIAL);
        if (sequence != 0) return fail(d, OGG_OPUS_DEMUX_ERR_SEQUENCE);
        d->stream_seen = true;
        d->stream_ended = false;
        d->serial = serial;
        d->packet_index = 0;
    } else {
        if (serial != d->serial) return fail(d, OGG_OPUS_DEMUX_ERR_SERIAL);
        if (h[5] & FLAG_BOS) return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
        if (sequence != d->next_sequence)
            return fail(d, OGG_OPUS_DEMUX_ERR_SEQUENCE);
    }
    /* Empty pages carry no first packet and do not change continuation. */
    if (d->segment_count && !!(h[5] & FLAG_CONTINUED) != d->packet_open)
        return fail(d, OGG_OPUS_DEMUX_ERR_CONTINUATION);
    d->next_sequence = sequence + 1u; /* Ogg sequence wraps modulo 2^32. */
    d->expected_crc = read32(h + 22);
    d->crc = 0;
    for (size_t i = 0; i < sizeof(d->header); ++i)
        d->crc = crc_byte(d->crc, i >= 22 && i < 26 ? 0 : h[i]);
    d->lacing_used = d->segment_index = d->segment_used = 0;
    d->phase = PHASE_LACING;
    return 0;
}

static int begin_body(ogg_opus_demux_t *d) {
    unsigned completed = 0;
    d->last_complete_segment = UINT16_MAX;
    for (uint16_t i = 0; i < d->segment_count; ++i) {
        if (d->lacing[i] < 255) {
            ++completed;
            d->last_complete_segment = i;
        }
    }
    const bool complete_end = d->segment_count &&
        d->last_complete_segment == (uint16_t)(d->segment_count - 1u);
    /* RFC 7845 section 3: Head is alone on BOS; Tags finish their page. */
    if (d->packet_index == 0 && (completed != 1 || !complete_end))
        return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    if (d->packet_index == 1 && completed &&
        (completed != 1 || !complete_end))
        return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    if ((!completed && d->page_granule != UINT64_MAX) ||
        (completed && (d->page_granule >> 63)) ||
        (completed && d->packet_index < 2 && d->page_granule != 0))
        return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    if (d->page_flags & FLAG_EOS) {
        if ((d->segment_count && !complete_end) ||
            (!d->segment_count && d->packet_open))
            return fail(d, OGG_OPUS_DEMUX_ERR_CONTINUATION);
        if (d->packet_index < 2) return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    }
    d->crc = crc_bytes(d->crc, d->lacing, d->segment_count);
    d->phase = PHASE_BODY;
    return 0;
}

static int finish_page(ogg_opus_demux_t *d) {
    if (d->crc != d->expected_crc) return fail(d, OGG_OPUS_DEMUX_ERR_CRC);
    if (d->page_flags & FLAG_EOS) d->stream_ended = true;
    d->phase = PHASE_HEADER;
    d->header_used = 0;
    return 0;
}

static int deliver_packet(ogg_opus_demux_t *d, uint16_t segment,
                          ogg_opus_packet_callback callback, void *context) {
    if ((d->packet_index == 0 &&
         (d->packet_size < 19 || memcmp(d->packet, "OpusHead", 8) != 0)) ||
        (d->packet_index == 1 &&
         (d->packet_size < 16 || memcmp(d->packet, "OpusTags", 8) != 0 ||
          read32(d->packet + 8) > d->packet_size - 16u)) ||
        d->packet_size == 0 || d->packet_index == UINT32_MAX)
        return fail(d, OGG_OPUS_DEMUX_ERR_FORMAT);
    const ogg_opus_packet_t packet = {
        .data = d->packet,
        .size = d->packet_size,
        .stored_size = d->packet_index == 1 &&
            d->packet_size > OGG_OPUS_TAG_PREFIX_BYTES ?
            OGG_OPUS_TAG_PREFIX_BYTES : d->packet_size,
        .packet_index = d->packet_index,
        .serial = d->serial,
        .page_granule = d->page_granule,
        .page_last_packet = segment == d->last_complete_segment,
        .page_eos = !!(d->page_flags & FLAG_EOS),
        .stream_start = d->packet_index == 0
    };
    ++d->packet_index;
    d->packet_size = 0;
    d->packet_open = false;
    const int result = callback(context, &packet);
    return result < 0 ? fail(d, result) : OGG_OPUS_DEMUX_PACKET;
}

int ogg_opus_demux_feed(ogg_opus_demux_t *d, const uint8_t *data,
                       size_t length, size_t *consumed,
                       ogg_opus_packet_callback callback, void *context) {
    if (consumed) *consumed = 0;
    if (!d || !consumed || !callback || (!data && length))
        return OGG_OPUS_DEMUX_ERR_ARGUMENT;
    if (d->error) return d->error;
    for (;;) {
        if (d->phase == PHASE_HEADER) {
            size_t take = sizeof(d->header) - d->header_used;
            if (take > length - *consumed) take = length - *consumed;
            if (!take) return OGG_OPUS_DEMUX_NEED_INPUT;
            memcpy(d->header + d->header_used, data + *consumed, take);
            d->header_used += (uint16_t)take;
            *consumed += take;
            if (d->header_used != sizeof(d->header)) continue;
            const int result = begin_page(d);
            if (result < 0) return result;
        }
        if (d->phase == PHASE_LACING) {
            size_t take = (size_t)d->segment_count - d->lacing_used;
            if (take > length - *consumed) take = length - *consumed;
            if (take) {
                memcpy(d->lacing + d->lacing_used, data + *consumed, take);
                d->lacing_used += (uint16_t)take;
                *consumed += take;
            }
            if (d->lacing_used != d->segment_count)
                return OGG_OPUS_DEMUX_NEED_INPUT;
            const int result = begin_body(d);
            if (result < 0) return result;
        }
        if (d->segment_index == d->segment_count) {
            const int result = finish_page(d);
            if (result < 0) return result;
            continue;
        }
        const uint8_t lace = d->lacing[d->segment_index];
        size_t take = (size_t)lace - d->segment_used;
        const uint32_t limit = d->packet_index == 1 ?
            OGG_OPUS_TAG_MAX_BYTES : OGG_OPUS_PACKET_BYTES;
        if (take > limit - d->packet_size)
            return fail(d, OGG_OPUS_DEMUX_ERR_PACKET_TOO_LARGE);
        if (take > length - *consumed) take = length - *consumed;
        if (take) {
            const uint8_t *input = data + *consumed;
            size_t store = take;
            if (d->packet_index == 1) {
                store = d->packet_size >= OGG_OPUS_TAG_PREFIX_BYTES ? 0 :
                    OGG_OPUS_TAG_PREFIX_BYTES - d->packet_size;
                if (store > take) store = take;
            }
            if (store) memcpy(d->packet + d->packet_size, input, store);
            d->packet_size += (uint32_t)take;
            d->segment_used += (uint16_t)take;
            d->crc = crc_bytes(d->crc, input, take);
            *consumed += take;
        }
        if (d->segment_used != lace) return OGG_OPUS_DEMUX_NEED_INPUT;
        const uint16_t finished_segment = d->segment_index++;
        d->segment_used = 0;
        if (lace == 255) {
            d->packet_open = true;
            continue;
        }
        if (d->segment_index == d->segment_count) {
            const int result = finish_page(d);
            if (result < 0) return result;
        }
        return deliver_packet(d, finished_segment, callback, context);
    }
}

int ogg_opus_demux_finish(const ogg_opus_demux_t *d) {
    if (!d) return OGG_OPUS_DEMUX_ERR_ARGUMENT;
    if (d->error) return d->error;
    return d->stream_ended && d->phase == PHASE_HEADER &&
        !d->header_used && !d->packet_open && !d->packet_size ?
        0 : OGG_OPUS_DEMUX_ERR_TRUNCATED;
}
