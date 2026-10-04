// Checked Ogg simple-decoder initialization and memory-error propagation.
// Private layouts are verified against the pinned 2.6.2 RV32 objects. No DSP
// arithmetic or parser state machine is replaced here.
#include "esp_audio_simple_dec.h"
#include "esp_audio_simple_dec_reg.h"
#include "esp_audio_dec.h"
#include <stddef.h>

typedef struct simple_registration {
    esp_audio_dec_ops_t operations;
    esp_audio_type_t decoder_type;
    esp_es_parse_type_t parser_type;
    esp_audio_simple_dec_type_t container_type;
    struct simple_registration *next;
} simple_registration;
typedef struct {
    esp_audio_type_t decoder_type;
    void *parser;
    esp_audio_dec_handle_t decoder;
    uint8_t *pending_data;
    uint32_t pending_bytes, pending_consumed;
    uint32_t padding_start, output_bytes, padding_end;
    bool decoder_ready;
    uint8_t reserved;
    uint16_t errors, error_limit, alignment;
    esp_audio_simple_dec_type_t container_type;
} simple_state;
_Static_assert(sizeof(simple_registration) == 32, "registration ABI");
_Static_assert(offsetof(simple_registration, parser_type) == 20, "parser type ABI");
_Static_assert(sizeof(simple_state) == 48, "simple decoder ABI");
_Static_assert(offsetof(simple_state, decoder_ready) == 36, "ready ABI");
_Static_assert(offsetof(simple_state, errors) == 38, "error counter ABI");
_Static_assert(offsetof(simple_state, container_type) == 44, "container ABI");

extern void *media_lib_module_calloc(const char *, size_t, size_t);
extern void media_lib_free(void *);
extern simple_registration *audio_simple_dec_get_register_map(esp_audio_simple_dec_type_t);
extern esp_audio_type_t audio_simple_dec_get_default_decoder(esp_audio_simple_dec_type_t);
extern esp_es_parse_err_t esp_es_parse_open(esp_es_parse_type_t, void **);
extern esp_es_parse_err_t esp_es_parse_set_decode_config(void *, void *);
extern esp_es_parse_err_t esp_es_parse_set_search_limit(void *, uint32_t);
extern esp_es_parse_err_t esp_es_parse_close(void *);
extern esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *, esp_audio_simple_dec_handle_t *);
extern esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,
    esp_audio_simple_dec_raw_t *, esp_audio_simple_dec_out_t *);

esp_audio_err_t __wrap_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,
                                                esp_audio_simple_dec_handle_t *handle) {
    if (!cfg || !handle) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    *handle = NULL;
    if (cfg->dec_type != ESP_AUDIO_SIMPLE_DEC_TYPE_OGG)
        return __real_esp_audio_simple_dec_open(cfg, handle);
    if (cfg->use_frame_dec) return ESP_AUDIO_ERR_NOT_SUPPORT;
    simple_registration *registered = audio_simple_dec_get_register_map(cfg->dec_type);
    if (!registered) return ESP_AUDIO_ERR_NOT_SUPPORT;
    simple_state *state = media_lib_module_calloc("ADEC_Simple", 1, sizeof(*state));
    if (!state) return ESP_AUDIO_ERR_MEM_LACK;
    state->container_type = cfg->dec_type;
    state->decoder_type = registered->decoder_type;
    esp_audio_err_t result = ESP_AUDIO_ERR_MEM_LACK;
    if (esp_es_parse_open(registered->parser_type, &state->parser) != ESP_ES_PARSE_ERR_OK ||
        !state->parser) goto failed;
    if (cfg->cfg_size && esp_es_parse_set_decode_config(state->parser, cfg->dec_cfg)) {
        result = ESP_AUDIO_ERR_INVALID_PARAMETER;
        goto failed;
    }
    // Container decoders are opened by the original process() after their
    // parser supplies configuration. Ogg has no default frame decoder.
    if (audio_simple_dec_get_default_decoder(cfg->dec_type)) {
        esp_audio_dec_cfg_t decoder_cfg = {
            .type = state->decoder_type, .cfg = cfg->dec_cfg, .cfg_sz = cfg->cfg_size,
        };
        result = esp_audio_dec_open(&decoder_cfg, &state->decoder);
        if (result != ESP_AUDIO_ERR_OK) goto failed;
    }
    enum { OGG_DECODE_ERROR_LIMIT = 50, OGG_HEADER_SEARCH_BYTES = 512000 };
    state->error_limit = OGG_DECODE_ERROR_LIMIT;
    esp_es_parse_set_search_limit(state->parser, OGG_HEADER_SEARCH_BYTES);
    *handle = state;
    return ESP_AUDIO_ERR_OK;
failed:
    if (state->decoder) esp_audio_dec_close(state->decoder);
    if (state->parser) esp_es_parse_close(state->parser);
    media_lib_free(state);
    return result;
}

// The vendor parser reports NO_MEM, but its caller can swallow that error;
// parse_vorbis_header also drops realloc failure. Capture those two signals
// for the duration of one Ogg process call. Task-local state isolates separate
// decoders and preserves nested scopes without modifying the private handle.
typedef struct { bool allocation_failed; } failure_scope;
static _Thread_local failure_scope *active_scope;
extern void *__real_media_lib_module_realloc(const char *, void *, size_t);
void *__wrap_media_lib_module_realloc(const char *module, void *old, size_t size) {
    void *next = __real_media_lib_module_realloc(module, old, size);
    if (!next && size && active_scope) active_scope->allocation_failed = true;
    return next;
}
extern esp_es_parse_err_t __real_esp_es_parse_frame(void *, void *, void *);
esp_es_parse_err_t __wrap_esp_es_parse_frame(void *parser, void *input, void *output) {
    esp_es_parse_err_t result = __real_esp_es_parse_frame(parser, input, output);
    if (result == ESP_ES_PARSE_ERR_NO_MEM && active_scope)
        active_scope->allocation_failed = true;
    return result;
}
extern esp_es_parse_err_t __real_esp_ogg_parse_frame(esp_es_parse_raw_t *, esp_es_parse_frame_info_t *);
esp_es_parse_err_t __wrap_esp_ogg_parse_frame(esp_es_parse_raw_t *input, esp_es_parse_frame_info_t *output) {
    esp_es_parse_err_t result = __real_esp_ogg_parse_frame(input, output);
    if (result == ESP_ES_PARSE_ERR_NO_MEM && active_scope)
        active_scope->allocation_failed = true;
    return result;
}
esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *out) {
    if (!handle || !raw || !out) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    simple_state *state = handle;
    if (state->container_type != ESP_AUDIO_SIMPLE_DEC_TYPE_OGG)
        return __real_esp_audio_simple_dec_process(handle, raw, out);
    failure_scope scope = {0};
    failure_scope *previous = active_scope;
    active_scope = &scope;
    esp_audio_err_t result = __real_esp_audio_simple_dec_process(handle, raw, out);
    active_scope = previous;
    if (scope.allocation_failed) {
        out->decoded_size = 0;
        return ESP_AUDIO_ERR_MEM_LACK;
    }
    return result;
}
