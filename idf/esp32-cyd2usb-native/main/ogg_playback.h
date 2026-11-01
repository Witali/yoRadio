#ifndef YORADIO_OGG_PLAYBACK_H
#define YORADIO_OGG_PLAYBACK_H

/* Public Espressif synthesis, one CRC-verified encoded page at a time.
 * No decoder-private state. A logical EOS drains/closes its decoder before
 * acknowledging the page and accepting another link. The caller owns the
 * generation, public handle/output/pending owners and synchronous callbacks.
 */
#include "esp_audio_simple_dec.h"
#include "decoder_pending_input.h"
#include "ogg_page_input.h"
#include "opus_pcm_trim.h"

typedef struct {
    ogg_page_input input;
    opus_pcm_trim trim;
    uint32_t generation;
    uint32_t calls;
} ogg_playback;

typedef enum {
    OGP_OK = 0, OGP_CANCELLED, OGP_MEMORY, OGP_CONTAINER, OGP_DECODER,
    OGP_INFO, OGP_OUTPUT
} ogg_playback_status;

typedef struct {
    bool (*cancelled)(void *context);
    bool (*output)(void *context, const esp_audio_simple_dec_info_t *info,
                   const uint8_t *pcm, size_t bytes);
    void (*yield)(void *context);
    void *context;
} ogg_playback_callbacks;

static inline void ogp_reset(ogg_playback *s, uint32_t generation)
{
    opi_reset(&s->input, generation);
    opt_reset(&s->trim);
    s->generation = generation;
    s->calls = 0;
}

static inline bool ogp_has_input(const ogg_playback *s)
{
    return s->input.size || s->input.timeline.active || s->input.ready;
}

static inline ogg_playback_status ogp_decode_page(ogg_playback *s,
    esp_audio_simple_dec_handle_t *decoder, uint8_t **output, size_t *capacity,
    decoder_pending_input_t *pending, const ogg_playback_callbacks *callbacks,
    int32_t *cause)
{
    const oopt_event *page = &s->input.event;
    bool eos = (page->flags & OOPT_LINK_END) != 0;
    if ((page->flags & OOPT_HEAD) && page->opus &&
        opt_begin(&s->trim, s->generation, page->pre_skip, page->channels) != OPT_OK) {
        *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
        return OGP_CONTAINER;
    }
    if (eos && page->opus && (!page->raw_end_known ||
        opt_end(&s->trim, s->generation, page->raw_end, page->raw_completed) != OPT_OK)) {
        *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
        return OGP_CONTAINER;
    }
    if (!*decoder) {
        esp_audio_simple_dec_cfg_t config = {
            .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_OGG,
            .dec_cfg = NULL, .cfg_size = 0, .use_frame_dec = false,
        };
        esp_audio_err_t result = esp_audio_simple_dec_open(&config, decoder);
        if (result != ESP_AUDIO_ERR_OK) {
            *cause = result;
            return result == ESP_AUDIO_ERR_MEM_LACK ? OGP_MEMORY : OGP_DECODER;
        }
    }
    uint8_t *input;
    uint32_t bytes;
    bool owned;
    decoder_pending_input_status_t prepared = decoder_pending_input_prepare(
        pending, s->input.page, s->input.size, &input, &bytes, &owned);
    if (prepared != DECODER_PENDING_INPUT_OK) {
        *cause = prepared == DECODER_PENDING_INPUT_NO_MEMORY ?
                 ESP_AUDIO_ERR_MEM_LACK : ESP_AUDIO_ERR_INVALID_PARAMETER;
        return prepared == DECODER_PENDING_INPUT_NO_MEMORY ? OGP_MEMORY : OGP_CONTAINER;
    }
    esp_audio_simple_dec_raw_t raw = {.buffer = input, .len = bytes, .eos = eos};
    for (;;) {
        if (callbacks->cancelled(callbacks->context)) return OGP_CANCELLED;
        if (*capacity > UINT32_MAX) { *cause = ESP_AUDIO_ERR_INVALID_PARAMETER; return OGP_DECODER; }
        esp_audio_simple_dec_out_t frame = {.buffer = *output, .len = (uint32_t)*capacity};
        raw.consumed = 0;
        esp_audio_err_t result = esp_audio_simple_dec_process(*decoder, &raw, &frame);
        if ((++s->calls & 31u) == 0u) callbacks->yield(callbacks->context);
        if (callbacks->cancelled(callbacks->context)) return OGP_CANCELLED;
        if (raw.consumed > raw.len || frame.decoded_size > *capacity) {
            *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
            return OGP_DECODER;
        }
        raw.buffer += raw.consumed;
        raw.len -= raw.consumed;
        if (result == ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            if (frame.decoded_size || frame.needed_size <= *capacity) {
                *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
                return OGP_DECODER;
            }
            uint8_t *larger = realloc(*output, frame.needed_size);
            if (!larger) { *cause = ESP_AUDIO_ERR_MEM_LACK; return OGP_MEMORY; }
            *output = larger;
            *capacity = frame.needed_size;
            /* Retry also when input was fully consumed into the public
             * decoder's cache. No original byte is fed to the observer twice.
             */
            continue;
        }
        if (result != ESP_AUDIO_ERR_OK) { *cause = result; return OGP_DECODER; }
        if (frame.decoded_size) {
            esp_audio_simple_dec_info_t info = {0};
            result = esp_audio_simple_dec_get_info(*decoder, &info);
            if (result != ESP_AUDIO_ERR_OK) { *cause = result; return OGP_INFO; }
            opus_pcm_span span = {0, frame.decoded_size};
            if (page->opus && opt_clip(&s->trim, s->generation,
                    info.sample_rate, info.channel, info.bits_per_sample,
                    frame.decoded_size, &span) != OPT_OK) {
                *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
                return OGP_INFO;
            }
            if (span.size && !callbacks->output(callbacks->context, &info,
                    *output + span.offset, span.size)) {
                *cause = ESP_AUDIO_ERR_FAIL;
                return callbacks->cancelled(callbacks->context) ? OGP_CANCELLED : OGP_OUTPUT;
            }
        }
        if (!raw.consumed && !frame.decoded_size && raw.len) {
            if (eos) { *cause = ESP_AUDIO_ERR_DATA_LACK; return OGP_DECODER; }
            prepared = decoder_pending_input_retain(pending, raw.buffer, raw.len, owned);
            if (prepared != DECODER_PENDING_INPUT_OK) {
                *cause = prepared == DECODER_PENDING_INPUT_NO_MEMORY ?
                         ESP_AUDIO_ERR_MEM_LACK : ESP_AUDIO_ERR_INVALID_PARAMETER;
                return prepared == DECODER_PENDING_INPUT_NO_MEMORY ? OGP_MEMORY : OGP_CONTAINER;
            }
            break;
        }
        if (eos ? (!raw.len && !raw.consumed && !frame.decoded_size) : !raw.len) break;
    }
    if (eos) {
        if (page->opus && opt_finish(&s->trim, s->generation) != OPT_OK) {
            *cause = ESP_AUDIO_ERR_DATA_LACK;
            return OGP_DECODER;
        }
        esp_audio_simple_dec_close(*decoder);
        *decoder = NULL;
        decoder_pending_input_clear(pending);
        opt_reset(&s->trim);
    }
    return opi_ack(&s->input, page->generation, page->token) ? OGP_OK : OGP_CONTAINER;
}

static inline ogg_playback_status ogp_feed(ogg_playback *s,
    const uint8_t *data, size_t bytes, bool end_of_input,
    esp_audio_simple_dec_handle_t *decoder, uint8_t **output, size_t *capacity,
    decoder_pending_input_t *pending, const ogg_playback_callbacks *callbacks,
    int32_t *cause)
{
    size_t at = 0;
    for (;;) {
        if (callbacks->cancelled(callbacks->context)) return OGP_CANCELLED;
        size_t used;
        ogg_page_input_status status = opi_feed(&s->input,
            bytes ? data + at : NULL, bytes - at, &used);
        if (used > bytes - at) { *cause = OPI_INVALID; return OGP_CONTAINER; }
        at += used;
        if (status < 0) {
            *cause = (int32_t)status;
            return status == OPI_NO_MEMORY ? OGP_MEMORY : OGP_CONTAINER;
        }
        if (status == OPI_PAGE) {
            ogg_playback_status decoded = ogp_decode_page(s, decoder, output,
                capacity, pending, callbacks, cause);
            if (decoded != OGP_OK) return decoded;
            continue;
        }
        if (at == bytes) break;
        if (!used) { *cause = OPI_INVALID; return OGP_CONTAINER; }
    }
    if (end_of_input) {
        ogg_page_input_status status = opi_finish(&s->input);
        if (status != OPI_FINISHED) { *cause = (int32_t)status; return OGP_CONTAINER; }
    }
    return OGP_OK;
}

#endif
