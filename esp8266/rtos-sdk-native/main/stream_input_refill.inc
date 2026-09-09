/* Included by audio_service.c after the socket and metadata helpers.
 * No waits here: once playback has started, queued frames take precedence
 * over waiting for the network, including a partially received ICY block. */
enum {
    STREAM_FILL_ERROR = -1,
    STREAM_FILL_CANCELLED = -2,
    STREAM_FILL_AGAIN = 0,
    STREAM_FILL_FULL,
    STREAM_FILL_YIELD,
    STREAM_FILL_EOF,
    STREAM_FILL_TIMEOUT,
};

static void stream_buffer_metadata(size_t size, void *context) {
    const output_context_t *output = (const output_context_t *)context;
    if (generation_current(output->generation)) parse_icy_title(size);
}

static int stream_input_refill(http_stream_t *stream, helix_codec_t *codec,
        stream_icy_t *icy, output_context_t *output) {
    int64_t started = esp_timer_get_time();
    size_t raw_bytes = 0;
    for (;;) {
        if (!generation_current(output->generation)) return STREAM_FILL_CANCELLED;
        size_t capacity = 0;
        uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
        if (!destination) return STREAM_FILL_ERROR;
        if (!capacity) return STREAM_FILL_FULL;
        /* Bound even a continuously readable metadata-only stream. A caller
         * may resume filling on the next turn, after yielding/decoding. */
        if (raw_bytes >= 8192U || esp_timer_get_time() - started >= 2000)
            return STREAM_FILL_YIELD;
        size_t wanted = capacity > 1024U ? 1024U : capacity;
        int received = stream_receive(stream, destination, wanted);
        if (received > 0) {
            if (!generation_current(output->generation)) return STREAM_FILL_CANCELLED;
            raw_bytes += (size_t)received;
            size_t audio = stream_icy_audio(icy, destination, (size_t)received,
                s_work, sizeof(s_work) - 1U, stream_buffer_metadata, output);
            if (helix_codec_buffer_commit(codec, audio) != 0)
                return STREAM_FILL_ERROR;
            output->measured_bytes += audio;
        } else if (!received) {
            return STREAM_FILL_EOF;
        } else if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return STREAM_FILL_AGAIN;
        } else {
            return errno == ETIMEDOUT ? STREAM_FILL_TIMEOUT : STREAM_FILL_ERROR;
        }
    }
}
