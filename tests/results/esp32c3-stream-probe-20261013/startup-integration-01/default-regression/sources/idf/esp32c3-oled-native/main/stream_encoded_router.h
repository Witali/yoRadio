#pragma once

// Private audio_service adapter, included after send_encoded. One producer
// (stream_task) owns this state. No lease survives a send_stream_audio call.
#include "stream_frames.h"

static struct {
    stream_frames_t frames;
    bool started;
    bool bypass; // MP3 free-format needs a decoder-owned boundary parser.
} s_frame_router;

typedef struct {
    uint32_t generation;
    native_codec_t *codec;
    encoded_packet_t *packet;
    // Nonzero only when replaying unpublished candidate storage. The caller
    // attaches control storage of at least header + this payload capacity.
    // Small copies into that separate FIFO node avoid waiting for a fifth
    // full data slot while all four candidate leases are held.
    size_t control_payload_bytes;
} stream_route_context_t;

static void stream_route_reset(void) {
    memset(&s_frame_router, 0, sizeof(s_frame_router));
}

static void stream_route_cancel(stream_route_context_t *ctx) {
    if (ctx->packet) {
        adaptive_input_cancel(s_encoded, ctx->packet);
        ctx->packet = NULL;
    }
}

static bool stream_route_flush(stream_route_context_t *ctx) {
    if (!ctx->packet) return true;
    if (atomic_load(&s_generation) != ctx->generation ||
        encoded_commit(s_encoded, ctx->packet) != pdTRUE) {
        stream_route_cancel(ctx);
        return false;
    }
    ctx->packet = NULL;
    return true;
}

static bool stream_route_acquire(stream_route_context_t *ctx) {
    if (ctx->packet) return true;
    size_t capacity = ctx->control_payload_bytes ? ctx->control_payload_bytes : STREAM_CHUNK_SIZE;
    while (atomic_load(&s_generation) == ctx->generation) {
        BaseType_t acquired = ctx->control_payload_bytes
            ? adaptive_input_acquire_control(s_encoded, (void **)&ctx->packet,
                sizeof(encoded_packet_t) + capacity, pdMS_TO_TICKS(250))
            : encoded_acquire(s_encoded, (void **)&ctx->packet,
                sizeof(encoded_packet_t) + capacity, pdMS_TO_TICKS(250));
        if (acquired != pdTRUE) continue;
        if (atomic_load(&s_generation) != ctx->generation) {
            stream_route_cancel(ctx);
            return false;
        }
        ctx->packet->generation = ctx->generation;
        ctx->packet->codec = *ctx->codec;
        ctx->packet->end_of_stream = AUDIO_CONTINUE;
        ctx->packet->data_size = 0;
        return true;
    }
    return false;
}

static bool stream_route_emit(void *opaque, const uint8_t *data, size_t size) {
    stream_route_context_t *ctx = opaque;
    while (size) {
        if (atomic_load(&s_generation) != ctx->generation) return false;
        if (!stream_route_acquire(ctx)) return false;
        size_t capacity = ctx->control_payload_bytes ? ctx->control_payload_bytes : STREAM_CHUNK_SIZE;
        size_t count = capacity - ctx->packet->data_size;
        if (count > size) count = size;
        memcpy(ctx->packet->data + ctx->packet->data_size, data, count);
        ctx->packet->data_size += count;
        data += count;
        size -= count;
        if (ctx->packet->data_size == capacity && !stream_route_flush(ctx))
            return false;
    }
    return true;
}

static bool stream_route_begin(void *opaque, const stream_frame_info_t *info) {
    stream_route_context_t *ctx = opaque;
    native_codec_t next = info->codec == STREAM_FRAME_MP3 ? NATIVE_CODEC_MP3 : NATIVE_CODEC_AAC;
    if (s_frame_router.started && next != *ctx->codec) {
        if (!stream_route_flush(ctx)) return false;
        if (ctx->control_payload_bytes) {
            if (!stream_route_acquire(ctx)) return false;
            ctx->packet->end_of_stream = AUDIO_DRAIN_CODEC;
            if (!stream_route_flush(ctx)) return false;
        } else if (!send_encoded(ctx->generation, *ctx->codec, NULL, 0, AUDIO_DRAIN_CODEC)) {
            return false;
        }
    }
    *ctx->codec = next;
    s_frame_router.started = true;
    return true;
}

static bool stream_route_feed(stream_route_context_t *ctx, const uint8_t *data, size_t size) {
    if (*ctx->codec != NATIVE_CODEC_MP3 && *ctx->codec != NATIVE_CODEC_AAC)
        return !size || (ctx->control_payload_bytes ? stream_route_emit(ctx, data, size)
            : send_encoded(ctx->generation, *ctx->codec, data, size, AUDIO_CONTINUE));
    if (s_frame_router.bypass) {
        if (stream_route_emit(ctx, data, size)) return true;
    } else {
        size_t consumed;
        stream_frame_result_t result = stream_frames_feed(&s_frame_router.frames,
            data, size, &consumed, stream_route_begin, stream_route_emit, ctx);
        if (result == STREAM_FRAME_MORE) return true;
        if (result == STREAM_FRAME_FREE_FORMAT) {
            // Preserve the unresolved header and all subsequent bytes. The
            // existing MP3 decoder owns free-format support; stop walking this
            // connection instead of rejecting a legal zero bitrate index.
            stream_frame_info_t info;
            if (stream_frame_header(s_frame_router.frames.header,
                    s_frame_router.frames.used, &info) == STREAM_FRAME_FREE_FORMAT &&
                stream_route_begin(ctx, &info) &&
                stream_route_emit(ctx, s_frame_router.frames.header, s_frame_router.frames.used) &&
                stream_route_emit(ctx, data + consumed, size - consumed)) {
                s_frame_router.bypass = true;
                return true;
            }
        }
    }
    stream_route_cancel(ctx);
    return false;
}

static bool stream_route_complete(native_codec_t codec) {
    return (codec != NATIVE_CODEC_MP3 && codec != NATIVE_CODEC_AAC) ||
           s_frame_router.bypass || stream_frames_complete(&s_frame_router.frames);
}

static uint8_t stream_route_end(native_codec_t codec, uint8_t reason) {
    return reason == AUDIO_END_EOF && !stream_route_complete(codec)
        ? AUDIO_END_FRAME_TRUNCATED : reason;
}
