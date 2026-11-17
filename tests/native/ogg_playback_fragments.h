/* Characterize encoded-byte identity and ownership through the actual wrapper.
 * This public decoder seam consumes synthetic CRC-valid non-Opus pages; it
 * makes no claim about synthesis or validity of their artificial setup data. */
static struct {
    uint8_t source[2 * OGG_PAGE_INPUT_MAX];
    size_t size, consumed;
    unsigned mode, word_calls;
    bool delayed, resized, refuse_word;
} fragments;

static void *fragment_word_allocate(size_t bytes)
{
    return fragments.refuse_word ? NULL : tracked_realloc(NULL, bytes);
}

static const ogg_page_word_allocator fragment_words = {
    .allocate = fragment_word_allocate, .release = tracked_free,
};

static void fragment_page(unsigned sequence, unsigned flags, size_t bytes)
{
    size_t segments = bytes == 65025 ? 255 : bytes / 255u + 1u;
    assert(segments <= 255 && fragments.size + 27u + segments + bytes <= sizeof(fragments.source));
    uint8_t *page = fragments.source + fragments.size;
    size_t header = 27u + segments, total = header + bytes;
    memset(page, 0, header);
    memcpy(page, "OggS", 4);
    page[5] = (uint8_t)flags;
    put32(page + 6, flags & 4u ? 4 : 0);
    put32(page + 14, 123);
    put32(page + 18, sequence);
    page[26] = (uint8_t)segments;
    for (size_t i = 0; i < segments; ++i)
        page[27 + i] = i + 1u == segments && bytes != 65025 ? (uint8_t)(bytes % 255u) : 255;
    for (size_t i = 0; i < bytes; ++i) page[header + i] = (uint8_t)(sequence + 17u * i);
    if (!sequence) {
        memcpy(page + header, "\x01vorbis\0\0\0\0", 11);
        page[header + 11] = 2;
        put32(page + header + 12, 48000);
    }
    put32(page + 22, crc(page, total));
    fragments.size += total;
}

static esp_audio_err_t consume_fragment(esp_audio_simple_dec_raw_t *raw,
                                       esp_audio_simple_dec_out_t *frame)
{
    assert(fragments.consumed <= fragments.size && raw->len <= fragments.size - fragments.consumed);
    assert(!raw->len || !memcmp(raw->buffer, fragments.source + fragments.consumed, raw->len));
    assert(raw->eos == ((state.owner->input.event.flags & OOPT_LINK_END) &&
                       fragments.consumed + raw->len == fragments.size));
    if (state.owner->input.word_page) {
        uint8_t guard[16];
        memset(guard, 0xa5, sizeof(guard));
        assert(!opi_copy_page(&state.owner->input, state.owner->input.size, guard, 1));
        assert(!opi_copy_page(&state.owner->input, SIZE_MAX, guard, 1));
        assert(!opi_copy_page(&state.owner->input, 0, NULL, 1));
        assert(opi_copy_page(&state.owner->input, 0, NULL, 0));
        for (size_t i = 0; i < sizeof(guard); ++i) assert(guard[i] == 0xa5);
        ++fragments.word_calls;
        if (fragments.mode == 1 && !fragments.delayed) {
            fragments.delayed = true;
            return ESP_AUDIO_ERR_OK;
        }
        if (fragments.mode >= 2 && fragments.mode <= 4 && !fragments.resized) {
            fragments.resized = true;
            frame->needed_size = 16384;
            raw->consumed = fragments.mode == 3 ? 1 : fragments.mode == 4 ? raw->len : 0;
            fragments.consumed += raw->consumed;
            return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
        }
        if (fragments.mode == 5) {
            state.cancelled = true;
            return ESP_AUDIO_ERR_OK;
        }
        if (fragments.mode == 6 && !fragments.delayed) {
            fragments.delayed = true;
            fail_allocation = allocations + 1;
            return ESP_AUDIO_ERR_OK;
        }
    }
    raw->consumed = raw->len;
    fragments.consumed += raw->consumed;
    if (raw->eos && raw->len) {
        memset(frame->buffer, 0, 16);
        frame->decoded_size = 16;
    }
    return ESP_AUDIO_ERR_OK;
}

static void fragmented_pages(void)
{
    const size_t chunks[] = {1, 257, 2048, 0};
    for (unsigned mode = 0; mode < 10; ++mode) for (unsigned split = 0; split < 4; ++split) {
        assert(!live_allocations);
        allocations = fail_allocation = 0;
        memset(&fragments, 0, sizeof(fragments));
        fragments.mode = mode;
        fragments.refuse_word = mode == 7;
        fragment_page(0, 2, 30);
        fragment_page(1, 0, mode == 9 ? 65025 : 65024);
        fragment_page(2, mode == 9 ? 5 : 4, 5001);
        const size_t original_size = fragments.size;
        uint8_t *encoded_copy = malloc(original_size);
        assert(encoded_copy);
        memcpy(encoded_copy, fragments.source, original_size);
        if (mode == 8) encoded_copy[58 + 300] ^= 1;
        ogg_playback owner = {0};
        assert(ogp_reset(&owner, 42));
        assert(opi_set_word_allocator(&owner.input, &fragment_words));
        memset(&state, 0, sizeof(state));
        state.owner = &owner;
        fragment_process = consume_fragment;
        esp_audio_simple_dec_handle_t decoder = NULL;
        uint8_t *pcm = NULL;
        size_t capacity = 0, at = 0;
        int32_t cause = 0;
        decoder_pending_input_t pending = {0};
        const ogg_playback_callbacks cb = {.cancelled=cancelled,.output=output,.yield=yield,.context=&state};
        ogg_playback_status status = OGP_OK;
        while (at < original_size && status == OGP_OK) {
            size_t take = original_size - at;
            if (chunks[split] && take > chunks[split]) take = chunks[split];
            status = ogp_feed(&owner, encoded_copy + at, take, false,
                &decoder, &pcm, &capacity, &pending, &cb, &cause);
            at += take;
        }
        if (status == OGP_OK) status = ogp_feed(&owner, NULL, 0, true,
            &decoder, &pcm, &capacity, &pending, &cb, &cause);
        assert(status == (mode == 5 ? OGP_CANCELLED : mode == 6 ? OGP_MEMORY : mode == 8 ? OGP_CONTAINER : OGP_OK));
        if (status == OGP_OK) {
            assert(fragments.consumed == original_size && !decoder && !pending.size);
            assert(state.opens == 1 && state.closes == 1 && state.outputs == 1 && state.bytes == 16);
            assert((fragments.word_calls > 0) == !fragments.refuse_word);
            if (mode == 1) assert(fragments.delayed);
            if (mode >= 2 && mode <= 4) assert(fragments.resized && capacity == 16384);
        }
        if (mode == 8) assert(fragments.consumed == 58 && !fragments.word_calls);
        clear(&owner, &decoder, &pcm, &pending);
        fragment_process = NULL;
        free(encoded_copy);
        printf("{\"case\":%u,\"mode\":\"word-fragments\",\"control\":%u,\"chunk\":%zu,\"encoded_bytes\":%zu,\"passed\":true}\n",
               cases++, mode, chunks[split], original_size);
    }
}
