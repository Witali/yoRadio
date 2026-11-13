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
#include "opus_family1_playback.h"
#include "pcm_channel_layout.h"

enum {
    OGP_INITIAL_PCM_BYTES = 12288,
    /* Opus family 0 has at most two channels. Start with 20 ms of stereo
     * S16 PCM at 48 kHz and use the public resize path for longer packets. */
    OGP_OPUS_INITIAL_PCM_BYTES = 960 * 2 * sizeof(int16_t),
};

typedef struct {
    ogg_page_input input;
    opus_pcm_trim trim;
    opus_family1_playback family1;
    int16_t header_gain_q8;
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
                   const uint8_t *pcm, size_t bytes, int16_t header_gain_q8);
    void (*yield)(void *context);
    void *context;
    /* Required for family1. The bytes are borrowed only until this callback
     * returns; the application must copy PCM and both metadata fields into
     * its ordered queue, independently of later public stream-info updates. */
    bool (*output_layout)(void *context, const esp_audio_simple_dec_info_t *info,
                          const uint8_t *pcm, size_t bytes,
                          int16_t header_gain_q8, pcm_channel_layout layout);
} ogg_playback_callbacks;

/* A real raw close refusal retains its cfg/handle, page and packet ownership.
 * The task must yield/retry before reset, generation release or maintenance ACK.
 * Initialize at a stable address with {0}; never copy a live playback owner. */
static inline bool ogp_reset(ogg_playback *s, uint32_t generation)
{
    if (!s) return false;
    ofp_result abandoned = ofp_abandon(&s->family1);
    if (abandoned.code != OFP_OK || abandoned.cleanup_pending) return false;
    opi_reset(&s->input, generation);
    opt_reset(&s->trim);
    s->header_gain_q8 = 0;
    s->generation = generation;
    s->calls = 0;
    return true;
}

static inline bool ogp_has_input(const ogg_playback *s)
{
    return s->input.size || s->input.timeline.active || s->input.ready ||
           ofp_has_input(&s->family1);
}

typedef struct {
    const ogg_playback_callbacks *callbacks;
} ogp_family1_context;

static inline bool ogp_family1_cancelled(void *user)
{
    const ogp_family1_context *context = user;
    return context->callbacks->cancelled(context->callbacks->context);
}

static inline void ogp_family1_yield(void *user)
{
    const ogp_family1_context *context = user;
    if (context->callbacks->yield)
        context->callbacks->yield(context->callbacks->context);
}

static inline bool ogp_family1_output(void *user, uint32_t generation,
    const opus_family1_plan *plan, const uint8_t *pcm, size_t bytes)
{
    (void)generation;
    const ogp_family1_context *context = user;
    esp_audio_simple_dec_info_t info = {
        .sample_rate = 48000, .bits_per_sample = 16, .channel = plan->channels,
    };
    return context->callbacks->output_layout(context->callbacks->context,
        &info, pcm, bytes, plan->header_gain_q8, PCM_CHANNEL_LAYOUT_VORBIS);
}

static inline ogg_playback_status ogp_family1_page(ogg_playback *s,
    const ogg_playback_callbacks *callbacks, int32_t *cause)
{
    if (!callbacks->output_layout) {
        *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
        return OGP_INFO;
    }
    ogp_family1_context context = {.callbacks = callbacks};
    const ofp_callbacks selected = {
        .cancelled = ogp_family1_cancelled, .output48_s16le = ogp_family1_output,
        .yield = ogp_family1_yield, .context = &context,
    };
    for (;;) {
        ofp_result result = ofp_page(&s->family1, &s->input, &selected, NULL);
        if (result.code == OFP_OK) return OGP_OK;
        if (result.code == OFP_CLEANUP && result.cleanup_pending && callbacks->yield) {
            callbacks->yield(callbacks->context);
            if (callbacks->cancelled(callbacks->context)) return OGP_CANCELLED;
            continue;
        }
        *cause = result.decoder.public_error_known ? result.decoder.public_error :
                 result.detail ? result.detail : ESP_AUDIO_ERR_FAIL;
        if (result.code == OFP_CANCELLED) return OGP_CANCELLED;
        if (result.code == OFP_MEMORY) return OGP_MEMORY;
        if (result.code == OFP_OUTPUT) return OGP_OUTPUT;
        if (result.code == OFP_CONTAINER || result.code == OFP_HEADER ||
            result.code == OFP_PACKET || result.code == OFP_PACKET_POLICY ||
            result.code == OFP_TRIM) return OGP_CONTAINER;
        return OGP_DECODER;
    }
}

static inline ogg_playback_status ogp_decode_page(ogg_playback *s,
    esp_audio_simple_dec_handle_t *decoder, uint8_t **output, size_t *capacity,
    decoder_pending_input_t *pending, const ogg_playback_callbacks *callbacks,
    int32_t *cause)
{
    const oopt_event *page = &s->input.event;
    bool eos = (page->flags & OOPT_LINK_END) != 0;
    if (page->opus && page->mapping == 1) {
        if (page->flags & OOPT_HEAD) {
            /* A caller may have prepared a simple Ogg handle before HEAD.
             * Its public void close is complete before the raw path starts.
             * No selected raw handle/config/page is moved or overwritten. */
            if (*decoder) esp_audio_simple_dec_close(*decoder);
            *decoder = NULL;
            decoder_pending_input_clear(pending);
            free(*output);
            *output = NULL;
            *capacity = 0;
        } else if (*decoder) {
            *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
            return OGP_DECODER;
        }
        return ogp_family1_page(s, callbacks, cause);
    }
    if ((page->flags & OOPT_HEAD) && page->opus) {
        /* OpusHead is the sole completed packet on the verified BOS page.
         * Its signed gain field is always at bytes 16..17 of that packet,
         * including compatible header extensions and other mapping families.
         */
        size_t payload = 27u + s->input.page[26];
        if (payload > s->input.size || s->input.size - payload < 19) {
            *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
            return OGP_CONTAINER;
        }
        unsigned encoded_gain = s->input.page[payload + 16] |
                                (unsigned)s->input.page[payload + 17] << 8;
        int32_t gain = encoded_gain < 32768u ? (int32_t)encoded_gain :
                       (int32_t)encoded_gain - 65536;
        if (opt_begin(&s->trim, s->generation, page->pre_skip, page->channels) != OPT_OK) {
            *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
            return OGP_CONTAINER;
        }
        s->header_gain_q8 = (int16_t)gain;
    }
    if (eos && page->opus && (!page->raw_end_known ||
        opt_end(&s->trim, s->generation, page->raw_end, page->raw_completed) != OPT_OK)) {
        *cause = ESP_AUDIO_ERR_INVALID_PARAMETER;
        return OGP_CONTAINER;
    }
    if (!*decoder) {
        if (!*capacity) {
            size_t initial = OGP_INITIAL_PCM_BYTES;
#if CONFIG_YORADIO_TLS_STATIC_RX_RESERVE
            if (page->opus && page->mapping == 0)
                initial = OGP_OPUS_INITIAL_PCM_BYTES;
#endif
            uint8_t *prepared = realloc(*output, initial);
            if (!prepared) { *cause = ESP_AUDIO_ERR_MEM_LACK; return OGP_MEMORY; }
            *output = prepared;
            *capacity = initial;
        }
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
        if (result != ESP_AUDIO_ERR_OK) {
            *cause = result;
            return result == ESP_AUDIO_ERR_MEM_LACK ? OGP_MEMORY : OGP_DECODER;
        }
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
                    *output + span.offset, span.size,
                    page->opus ? s->header_gain_q8 : 0)) {
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
        s->header_gain_q8 = 0;
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
