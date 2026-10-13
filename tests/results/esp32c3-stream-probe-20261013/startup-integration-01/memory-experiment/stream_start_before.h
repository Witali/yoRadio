#pragma once

#include "stream_confirm.h"
#include "stream_staging.h"

// Private stream_task startup adapter. No decoder pointer refers to the held
// window: replay copies short spans into independent control FIFO storage.
enum { STREAM_START_CONTROL_PAYLOAD = 128 };
static _Alignas(encoded_packet_t) uint8_t s_start_control[
    sizeof(encoded_packet_t)+STREAM_START_CONTROL_PAYLOAD];
static bool s_start_control_attached;
static struct {
    stream_staging_t window;
    int64_t deadline_us;
    size_t search_left, tag_anchor;
    uint32_t skip, tag_bytes;
    bool active, tail_seen;
} s_stream_start;

static bool stream_start_eligible(native_codec_t codec) {
    return codec == NATIVE_CODEC_AUTO || codec == NATIVE_CODEC_MP3 || codec == NATIVE_CODEC_AAC;
}

static void stream_start_abort(void) {
    if (s_stream_start.active) stream_staging_cancel(&s_stream_start.window);
    memset(&s_stream_start, 0, sizeof(s_stream_start));
}

static bool stream_start_publish(uint32_t generation, native_codec_t *codec,
                                 stream_probe_result_t selected) {
    switch (selected) {
        case STREAM_PROBE_MP3: *codec=NATIVE_CODEC_MP3; break;
        case STREAM_PROBE_AAC: *codec=NATIVE_CODEC_AAC; break;
        case STREAM_PROBE_FLAC: *codec=NATIVE_CODEC_FLAC; break;
        case STREAM_PROBE_OGG: *codec=NATIVE_CODEC_OGG; break;
        default: return false;
    }
    stream_route_context_t route = {.generation=generation, .codec=codec,
        .control_payload_bytes=STREAM_START_CONTROL_PAYLOAD};
    size_t bytes=stream_staging_size(&s_stream_start.window);
    bool ok=true;
    for (size_t offset=0; offset<bytes && ok;) {
        size_t count;
        const uint8_t *span=stream_staging_span(&s_stream_start.window,offset,&count);
        ok=stream_route_feed(&route,span,count);
        offset+=count;
    }
    if (ok) ok=stream_route_flush(&route);
    if (!ok) stream_route_cancel(&route);
    return ok;
}

// MORE retains only owned queue leases; READY replayed every retained byte.
// consumed identifies the unhandled suffix of the caller's current read.
static stream_confirm_result_t stream_start_feed(uint32_t generation,
        native_codec_t *codec, const uint8_t *data, size_t size, size_t *consumed,
        bool eof) {
    *consumed=0;
    if (!s_stream_start.active) {
        if (!s_start_control_attached) {
            if (!adaptive_input_attach_control(s_encoded,s_start_control,sizeof(s_start_control)))
                return STREAM_CONFIRM_INVALID;
            s_start_control_attached=true;
        }
        if (!stream_staging_init(&s_stream_start.window,s_encoded,
                sizeof(encoded_packet_t),STREAM_CHUNK_SIZE)) return STREAM_CONFIRM_INVALID;
        s_stream_start.active=true;
        s_stream_start.search_left=STREAM_PROBE_SEARCH_BYTES;
        s_stream_start.deadline_us=esp_timer_get_time()+(int64_t)STREAM_PROBE_TIMEOUT_MS*1000;
    }
    while (atomic_load(&s_generation)==generation &&
           esp_timer_get_time()<s_stream_start.deadline_us) {
        if (s_stream_start.skip) {
            size_t skip=size-*consumed;
            if (skip>s_stream_start.skip) skip=s_stream_start.skip;
            *consumed+=skip; s_stream_start.skip-=skip;
            if (s_stream_start.skip) return eof ? STREAM_CONFIRM_INVALID : STREAM_CONFIRM_MORE;
        }
        size_t bytes=stream_staging_size(&s_stream_start.window);
        stream_confirm_info_t info;
        stream_confirm_result_t result=stream_confirm_window(stream_staging_read,
            &s_stream_start.window,bytes,eof && *consumed==size,
            s_stream_start.search_left,STREAM_ID3_RUN_BYTES,&info);
        if (info.discard) {
            if (!stream_staging_erase(&s_stream_start.window,0,info.discard)) break;
            s_stream_start.search_left-=info.discard;
            s_stream_start.tag_bytes=0; s_stream_start.tag_anchor=0; s_stream_start.tail_seen=false;
            bytes-=info.discard;
        }
        if (result==STREAM_CONFIRM_READY || result==STREAM_CONFIRM_FREE_FORMAT) {
            return stream_start_publish(generation,codec,info.codec)
                ? STREAM_CONFIRM_READY : STREAM_CONFIRM_INVALID;
        }
        if (result==STREAM_CONFIRM_REMOVE_TAG) {
            if (info.tag_offset!=s_stream_start.tag_anchor) {
                s_stream_start.tag_anchor=info.tag_offset;
                s_stream_start.tag_bytes=0; s_stream_start.tail_seen=false;
            }
            uint8_t magic[STREAM_ID3V1_MAGIC_BYTES];
            if (!stream_staging_read(&s_stream_start.window,info.tag_offset,magic,sizeof(magic))) break;
            bool tail=stream_id3v1_prefix(magic,sizeof(magic));
            if ((tail && s_stream_start.tail_seen) ||
                info.tag_bytes>STREAM_ID3_RUN_BYTES-s_stream_start.tag_bytes) break;
            if (tail) s_stream_start.tail_seen=true;
            s_stream_start.tag_bytes+=info.tag_bytes;
            size_t remove=bytes-info.tag_offset;
            if (remove>info.tag_bytes) remove=info.tag_bytes;
            if (!stream_staging_erase(&s_stream_start.window,info.tag_offset,remove)) break;
            s_stream_start.skip=info.tag_bytes-remove;
            continue;
        }
        if (result!=STREAM_CONFIRM_MORE || info.needed<=bytes ||
            info.needed>STREAM_STAGING_SLOTS*STREAM_CHUNK_SIZE+STREAM_STAGING_LOOKAHEAD) break;
        if (*consumed==size) return STREAM_CONFIRM_MORE;
        size_t count=info.needed-bytes;
        if (count>size-*consumed) count=size-*consumed;
        size_t accepted=stream_staging_append(&s_stream_start.window,data+*consumed,count);
        *consumed+=accepted;
        if (!accepted) vTaskDelay(pdMS_TO_TICKS(1)); // Bounded by generation and deadline above.
    }
    return STREAM_CONFIRM_INVALID;
}
