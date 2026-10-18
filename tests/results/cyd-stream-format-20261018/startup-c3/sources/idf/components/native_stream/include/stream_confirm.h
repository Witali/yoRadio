#pragma once

#include "stream_frames.h"
#include "stream_probe.h"

// Startup/recovery candidate inspection over caller-owned, potentially split
// storage. This is NOT the aligned frame walker: it may scan candidate payload
// only after a claimed next boundary has failed. No pointer is retained.
// Caller selects whether initial container signatures are allowed. Once an
// elementary stream is established, recovery searches only MP3/ADTS frames.
typedef bool (*stream_confirm_read_fn)(void *context, size_t offset,
                                      uint8_t *destination, size_t count);
typedef enum {
    STREAM_CONFIRM_MORE,
    STREAM_CONFIRM_READY,
    STREAM_CONFIRM_INVALID,
    STREAM_CONFIRM_REMOVE_TAG,
    STREAM_CONFIRM_FREE_FORMAT,
} stream_confirm_result_t;

typedef struct {
    // Discard this many leading junk bytes before the next call. Charge them
    // against the connection's remaining search budget, including on MORE.
    size_t discard;
    // Minimum retained-window length needed next, AFTER discard.
    size_t needed;
    stream_probe_result_t codec;
    uint16_t first_frame_bytes;
    bool single_frame_eof;
    // REMOVE_TAG: remove this envelope without storing its body; offset is
    // relative to the window AFTER discard. Preserve earlier candidate bytes.
    size_t tag_offset;
    uint32_t tag_bytes;
} stream_confirm_info_t;

static inline stream_confirm_result_t stream_confirm_window_mode(
        stream_confirm_read_fn read, void *context, size_t bytes, bool eof,
        size_t search_left, uint32_t tag_budget, bool containers,
        stream_confirm_info_t *out) {
    *out = (stream_confirm_info_t){0};
    size_t start = 0;
    while (true) {
        uint8_t header[STREAM_ID3_HEADER_BYTES];
        size_t count = bytes - start;
        if (count > sizeof(header)) count = sizeof(header);
        out->discard = start;
        if (!count) {
            out->needed = 1;
            return eof ? STREAM_CONFIRM_INVALID : STREAM_CONFIRM_MORE;
        }
        if (!read(context, start, header, count)) return STREAM_CONFIRM_INVALID;
        if (stream_id3_prefix(header, count)) {
            if (count < STREAM_ID3_HEADER_BYTES) {
                if (!eof) {out->needed=STREAM_ID3_HEADER_BYTES;return STREAM_CONFIRM_MORE;}
            } else {
                uint32_t total;
                if (!stream_id3_size(header,&total) || total>tag_budget)
                    return STREAM_CONFIRM_INVALID;
                out->tag_bytes=total;
                return STREAM_CONFIRM_REMOVE_TAG;
            }
        }
        stream_probe_result_t probe = stream_probe_header(header,count);
        if (containers && (probe==STREAM_PROBE_FLAC || probe==STREAM_PROBE_OGG)) {
            out->codec=probe;
            return STREAM_CONFIRM_READY; // Container parser owns further validation.
        }
        stream_frame_info_t first;
        stream_frame_result_t parsed=stream_frame_header(header,count,&first);
        if (parsed==STREAM_FRAME_FREE_FORMAT) {
            out->codec=STREAM_PROBE_MP3;
            return STREAM_CONFIRM_FREE_FORMAT; // Never invent a free-format length.
        }
        if (parsed==STREAM_FRAME_MORE || stream_probe_needs_more(header,count)) {
            if (!eof) {out->needed=count+1;return STREAM_CONFIRM_MORE;}
        } else if (parsed==STREAM_FRAME_READY) {
            // Addition is bounded by the retained window before any offset read.
            if (first.bytes > bytes-start) {
                if (!eof) {out->needed=first.bytes;return STREAM_CONFIRM_MORE;}
            } else {
                size_t next=start+first.bytes;
                size_t available=bytes-next;
                if (!available && eof) {
                    out->codec=first.codec==STREAM_FRAME_MP3 ? STREAM_PROBE_MP3 : STREAM_PROBE_AAC;
                    out->first_frame_bytes=first.bytes;
                    out->single_frame_eof=true;
                    return STREAM_CONFIRM_READY;
                }
                size_t look=available<sizeof(header) ? available : sizeof(header);
                if (look && !read(context,next,header,look)) return STREAM_CONFIRM_INVALID;
                bool id3=look && stream_id3_prefix(header,look);
                bool tail=look && first.codec==STREAM_FRAME_MP3 && stream_id3v1_prefix(header,look);
                if (id3 || tail) {
                    size_t minimum=tail ? STREAM_ID3V1_MAGIC_BYTES : STREAM_ID3_HEADER_BYTES;
                    if (look<minimum) {
                        if (!eof) {out->needed=first.bytes+minimum;return STREAM_CONFIRM_MORE;}
                    } else {
                        uint32_t total=STREAM_ID3V1_TAG_BYTES;
                        if ((!tail && !stream_id3_size(header,&total)) || total>tag_budget)
                            return STREAM_CONFIRM_INVALID;
                        out->tag_offset=first.bytes;
                        out->tag_bytes=total;
                        return STREAM_CONFIRM_REMOVE_TAG;
                    }
                } else {
                    stream_frame_info_t second;
                    stream_frame_result_t result=stream_frame_header(header,look,&second);
                    if (result==STREAM_FRAME_READY || result==STREAM_FRAME_FREE_FORMAT) {
                        // Rate, channels, bitrate and even codec family may change
                        // at a real boundary; these are not synchronization keys.
                        out->codec=first.codec==STREAM_FRAME_MP3 ? STREAM_PROBE_MP3 : STREAM_PROBE_AAC;
                        out->first_frame_bytes=first.bytes;
                        return STREAM_CONFIRM_READY;
                    }
                    if (result==STREAM_FRAME_MORE && !eof) {
                        out->needed=first.bytes+look+1;
                        return STREAM_CONFIRM_MORE;
                    }
                }
            }
        }
        if (start>=search_left) return STREAM_CONFIRM_INVALID;
        ++start;
    }
}

static inline stream_confirm_result_t stream_confirm_window(
        stream_confirm_read_fn read, void *context, size_t bytes, bool eof,
        size_t search_left, uint32_t tag_budget, stream_confirm_info_t *out) {
    return stream_confirm_window_mode(read, context, bytes, eof, search_left,
                                     tag_budget, true, out);
}
