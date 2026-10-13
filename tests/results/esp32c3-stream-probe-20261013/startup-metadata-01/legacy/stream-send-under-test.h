static bool send_stream_audio(uint32_t generation, native_codec_t *codec,
                              const uint8_t *data, size_t size,
                              bool *first_chunk, stream_probe_t *probe) {
    if (!size) return true;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    stream_route_context_t route = {.generation = generation, .codec = codec};
#endif
    if (*first_chunk) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
        if (stream_start_eligible(*codec)) {
            size_t consumed;
            stream_confirm_result_t result=stream_start_feed(generation,codec,data,size,&consumed,false);
            if (result==STREAM_CONFIRM_MORE) return true;
            stream_start_abort();
            if (result!=STREAM_CONFIRM_READY) {probe->result=STREAM_PROBE_INVALID;return false;}
            data+=consumed;size-=consumed;
            *first_chunk = false; // stream_start_publish already set the provisional status.
        } else
#endif
        if (*codec == NATIVE_CODEC_AUTO) {
            size_t consumed = 0;
            switch (stream_probe_feed(probe, data, size, &consumed)) {
                case STREAM_PROBE_MORE: return true;
                case STREAM_PROBE_MP3: *codec = NATIVE_CODEC_MP3; break;
                case STREAM_PROBE_AAC: *codec = NATIVE_CODEC_AAC; break;
                case STREAM_PROBE_FLAC: *codec = NATIVE_CODEC_FLAC; break;
                case STREAM_PROBE_OGG: *codec = NATIVE_CODEC_OGG; break;
                default: return false;
            }
            state_set_audio(generation, true, codec_name(*codec));
            // Replay the assembled header exactly once, before this read's tail.
#ifdef CONFIG_YORADIO_FRAME_ROUTER
            if (!stream_route_feed(&route, probe->header, probe->used))
#else
            if (!send_encoded(generation, *codec, probe->header, probe->used, false))
#endif
                return false;
            *first_chunk = false;
            data += consumed;
            size -= consumed;
        }
        if (*first_chunk) state_set_audio(generation, true, codec_name(*codec));
        *first_chunk = false;
    }
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    return stream_route_feed(&route, data, size) && stream_route_flush(&route);
#else
    return !size || send_encoded(generation, *codec, data, size, false);
#endif
}

static inline uint8_t finish_stream_audio(uint32_t generation, native_codec_t *codec,
        bool *first_chunk, uint8_t reason) {
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if (*first_chunk && stream_start_eligible(*codec) && reason==AUDIO_END_EOF) {
        // EOF rescan can discard the incomplete candidate. Preserve its
        // presence before finalization so truncation is not reported as empty.
        bool incomplete=s_stream_start.skip || stream_staging_size(&s_stream_start.window);
        size_t consumed;
        stream_confirm_result_t result=stream_start_feed(generation,codec,NULL,0,&consumed,true);
        if (result==STREAM_CONFIRM_READY) {
            *first_chunk=false;
        } else {
            reason=incomplete || s_stream_start.skip || stream_staging_size(&s_stream_start.window)
                ? AUDIO_END_FRAME_TRUNCATED : AUDIO_END_FORMAT_UNKNOWN;
        }
    }
    stream_start_abort();
#else
    (void)generation;(void)first_chunk;
#endif
    if (*codec==NATIVE_CODEC_AUTO &&
        (reason==AUDIO_END_EOF || reason==AUDIO_END_BUFFER_STALLED)) reason=AUDIO_END_FORMAT_UNKNOWN;
#ifdef CONFIG_YORADIO_FRAME_ROUTER
    reason=stream_route_end(*codec,reason);
#endif
    return reason;
}

