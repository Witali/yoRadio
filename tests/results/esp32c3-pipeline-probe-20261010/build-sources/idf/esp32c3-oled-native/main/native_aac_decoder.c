#include "native_aac_decoder.h"

#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
#include <assert.h>
#include "esp_heap_caps.h"
#endif
#include <stdlib.h>
#include <string.h>
#include "aac_decoder_config.h"
#include "aac_profile.h"
#include "codec_memory_trace.h"
#include "aac_pointer_audit.h"
#include "decoder_pcm.h"
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
#include "aac_compact_owner.h"
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
#include "aac_sbr_reserve.h"
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
#include "aac_scratch_reserve.h"
#endif
#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
#include "cpu_profiler.h"
#define AAC_MEMORY(stage) cpu_profiler_memory(stage)
#else
#define AAC_MEMORY(stage) ((void)0)
#endif

// ADTS has a 13-bit frame length. Grow to fit one complete frame, retaining
// capacity until close. Network chunks never become decoder reset boundaries.
#define ADTS_FRAME_MAX 8191
#if defined(YORADIO_AAC_PROFILE_METADATA) && !defined(CONFIG_YORADIO_AAC_COMPACT_SBR) && \
    !defined(CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE) && !defined(CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE)
#define AAC_PROFILE_DIRECT_SCOPE 1
#endif
struct native_aac_decoder {
    esp_audio_simple_dec_handle_t codec;
    size_t used;
    size_t capacity;
    uint8_t *data;
    uint16_t signature;
    uint8_t header[7];
#ifdef AAC_PROFILE_DIRECT_SCOPE
    aac_profile_state_t profile;
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    aac_compact_owner_t compact;
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
    aac_sbr_reserve_t reserve;
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
    aac_scratch_reserve_t scratch;
#endif
};

#ifdef YORADIO_AAC_PROFILE_METADATA
static aac_profile_state_t *profile_state(native_aac_decoder_t *decoder) {
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    return &decoder->compact.profile;
#elif defined(CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE)
    return &decoder->scratch.profile;
#elif defined(CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE)
    return &decoder->reserve.profile;
#else
    return &decoder->profile;
#endif
}
#endif

static void clear_profile(native_aac_decoder_t *decoder) {
#ifdef YORADIO_AAC_PROFILE_METADATA
    *profile_state(decoder)=AAC_PROFILE_UNKNOWN;
#else
    (void)decoder;
#endif
}

static void close_codec(native_aac_decoder_t *decoder) {
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    aac_compact_owner_enter(&decoder->compact);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
    aac_scratch_reserve_enter(&decoder->scratch);
#endif
    esp_audio_simple_dec_close(decoder->codec);
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    aac_compact_owner_leave();
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
    aac_scratch_reserve_leave();
#endif
    decoder->codec=NULL;
    clear_profile(decoder);
}

native_aac_decoder_t *native_aac_decoder_create(void) {
    codec_memory_trace_dump("aac-before-adts");
    AAC_MEMORY("aac-before-adts");
    native_aac_decoder_t *decoder = calloc(1, sizeof(*decoder));
    if (decoder) {
        decoder->data = decoder->header;
        decoder->capacity = sizeof(decoder->header);
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
        aac_sbr_reserve_prepare(&decoder->reserve);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
        aac_scratch_reserve_prepare(&decoder->scratch);
#endif
    }
    return decoder;
}

void native_aac_decoder_destroy(native_aac_decoder_t *decoder) {
    if (!decoder) return;
    if (decoder->codec) close_codec(decoder);
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
    aac_sbr_reserve_discard(&decoder->reserve);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
    aac_scratch_reserve_discard(&decoder->scratch);
#endif
    codec_memory_trace_dump("aac-close");
    if (decoder->data != decoder->header) free(decoder->data);
    free(decoder);
}

#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
void native_aac_decoder_test_disable_late_sbr(native_aac_decoder_t *decoder) {
    assert(decoder && !decoder->codec);
    decoder->compact.late_disabled=true;
}
void native_aac_decoder_test_footprint(native_aac_decoder_t *decoder,
                                     size_t *requested,size_t *allocated) {
    assert(decoder && requested && allocated);
    *requested=sizeof(*decoder);*allocated=heap_caps_get_allocated_size(decoder);
}
#endif

static bool reserve_frame(native_aac_decoder_t *decoder, size_t needed) {
    if (needed <= decoder->capacity) return true;
    // At most 128 bytes of slack avoids reallocating for every VBR frame.
    size_t capacity = (needed + 127) & ~(size_t)127;
    if (capacity > ADTS_FRAME_MAX) capacity = ADTS_FRAME_MAX;
    bool inline_header = decoder->data == decoder->header;
    uint8_t *resized = realloc(inline_header ? NULL : decoder->data, capacity);
    if (!resized) return false;
    if (inline_header) memcpy(resized, decoder->header, decoder->used);
    decoder->data = resized;
    decoder->capacity = capacity;
    return true;
}

esp_audio_err_t native_aac_decoder_process(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_raw_t *raw, esp_audio_simple_dec_out_t *output) {
    if (!decoder || !raw || !output) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    raw->consumed = 0;
    output->decoded_size = 0;
    // SBR stereo produces 2048 samples/channel. The SDK can split that frame
    // across calls for smaller buffers; keep one frame atomic here instead.
    if (output->len < NATIVE_AAC_PCM_FRAME_BYTES) {
        output->needed_size = NATIVE_AAC_PCM_FRAME_BYTES;
        return ESP_AUDIO_ERR_BUFF_NOT_ENOUGH;
    }
    for (;;) {
        size_t needed = 7;
        if (decoder->used >= 7) {
            const uint8_t *p = decoder->data;
            size_t header_size = (p[1] & 1) ? 7 : 9;
            size_t frame_size = ((p[3] & 3) << 11) | (p[4] << 3) | (p[5] >> 5);
            if (p[0] != 0xff || (p[1] & 0xf6) != 0xf0 ||
                ((p[2] >> 2) & 15) > 12 || frame_size < header_size) {
                // Resynchronize without trusting length bits in arbitrary data.
                memmove(decoder->data, decoder->data + 1, --decoder->used);
                continue;
            }
            needed = frame_size;
            if (!reserve_frame(decoder, needed)) return ESP_AUDIO_ERR_MEM_LACK;
            p = decoder->data; // Growth may move the frame/header.
            if (decoder->used == needed) {
                bool opened = false;
                uint16_t signature = ((p[1] & 8) << 8) |
                    ((p[2] & 0xfd) << 2) | (p[3] >> 6);
                if (!decoder->codec || signature != decoder->signature) {
                    if (decoder->codec) {
                        close_codec(decoder);
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
                        aac_sbr_reserve_discard(&decoder->reserve);
                        aac_sbr_reserve_prepare(&decoder->reserve);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
                        aac_scratch_reserve_discard(&decoder->scratch);
                        aac_scratch_reserve_prepare(&decoder->scratch);
#endif
                    }
                    codec_memory_trace_dump("aac-reopen-close");
                    decoder->codec = NULL;
                    AAC_MEMORY("aac-before-open");
                    esp_aac_dec_cfg_t aac = native_aac_decoder_config();
                    esp_audio_simple_dec_cfg_t config = {
                        .dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_AAC,
                        .dec_cfg = &aac, .cfg_size = sizeof(aac),
                        .use_frame_dec = true,
                    };
                    // Reapply AAC Plus too: the library retains SBR state
                    // across incompatible ADTS configurations otherwise.
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
                    aac_compact_owner_enter(&decoder->compact);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
                    aac_scratch_reserve_enter(&decoder->scratch);
#endif
                    esp_audio_err_t result = esp_audio_simple_dec_open(
                        &config, &decoder->codec);
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
                    aac_compact_owner_leave();
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
                    aac_scratch_reserve_leave();
                    bool retry = decoder->scratch.pending &&
                        (result == ESP_AUDIO_ERR_MEM_LACK || result == ESP_AUDIO_ERR_FAIL);
                    aac_scratch_reserve_discard(&decoder->scratch);
                    if (retry) {
                        decoder->codec = NULL;
                        result = esp_audio_simple_dec_open(&config, &decoder->codec);
                    }
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
                    if ((result == ESP_AUDIO_ERR_MEM_LACK || result == ESP_AUDIO_ERR_FAIL) &&
                        decoder->reserve.pending) {
                        // The early block must not prevent an otherwise viable
                        // LC decoder from opening. The SDK also reports FAIL
                        // when one of its nested initial allocations fails.
                        // Its failed-open path closes the partially built owner.
                        aac_sbr_reserve_discard(&decoder->reserve);
                        decoder->codec = NULL;
                        result = esp_audio_simple_dec_open(&config, &decoder->codec);
                    }
#endif
                    codec_memory_trace_dump("aac-open");
                    if (result != ESP_AUDIO_ERR_OK) return result;
                    decoder->signature = signature;
                    opened = true;
                    AAC_MEMORY("aac-after-open");
                }
                esp_audio_simple_dec_raw_t frame = {
                    .buffer = decoder->data, .len = needed,
                };
                clear_profile(decoder);
#ifdef AAC_PROFILE_DIRECT_SCOPE
                aac_profile_enter(profile_state(decoder));
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
                aac_compact_owner_enter(&decoder->compact);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
                aac_sbr_reserve_enter(&decoder->reserve);
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
                aac_scratch_reserve_enter(&decoder->scratch);
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
                aac_pointer_audit_io(decoder->data,needed,output->buffer,output->len);
#endif
                esp_audio_err_t result = esp_audio_simple_dec_process(
                    decoder->codec, &frame, output);
#ifdef AAC_PROFILE_DIRECT_SCOPE
                aac_profile_leave();
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
                aac_pointer_audit_io(NULL,0,NULL,0);
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
                aac_compact_owner_leave();
                if (decoder->compact.allocation_failed) {
                    output->decoded_size=0;
                    result=ESP_AUDIO_ERR_MEM_LACK;
                }
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
                aac_scratch_reserve_leave();
                if (decoder->scratch.allocation_failed) {
                    output->decoded_size = 0;
                    result = ESP_AUDIO_ERR_MEM_LACK;
                }
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
                aac_sbr_reserve_leave();
                if (decoder->reserve.allocation_failed) {
                    output->decoded_size=0;
                    result=ESP_AUDIO_ERR_MEM_LACK;
                }
                // LC does not need the reserved owner. Release after the first
                // real frame, not after a parser-only or output-retry call.
                if (output->decoded_size) aac_sbr_reserve_discard(&decoder->reserve);
#endif
                codec_memory_trace_dump("aac-process");
                if(result!=ESP_AUDIO_ERR_OK || !output->decoded_size)clear_profile(decoder);
                if (opened) AAC_MEMORY("aac-after-first-process");
                // Keep the frame for a larger PCM buffer retry. The caller
                // still advances input bytes already copied into our buffer.
                if (result != ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) decoder->used = 0;
                return result;
            }
        }
        size_t available = raw->len - raw->consumed;
        if (!available) return ESP_AUDIO_ERR_OK;
        size_t count = needed - decoder->used;
        if (count > available) count = available;
        memcpy(decoder->data + decoder->used, raw->buffer + raw->consumed, count);
        decoder->used += count;
        raw->consumed += count;
    }
}

esp_audio_err_t native_aac_decoder_get_info(native_aac_decoder_t *decoder,
    esp_audio_simple_dec_info_t *info) {
    if (!decoder || !decoder->codec) return ESP_AUDIO_ERR_NOT_FOUND;
    return esp_audio_simple_dec_get_info(decoder->codec, info);
}

#if defined(CONFIG_YORADIO_QEMU_AAC_RESET_TEST) || defined(CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST)
// Test only: fixture boundaries contain no partial ADTS frame.
esp_audio_err_t native_aac_decoder_reset_for_test(native_aac_decoder_t *decoder) {
    if (!decoder || !decoder->codec || decoder->used) return ESP_AUDIO_ERR_INVALID_PARAMETER;
    clear_profile(decoder);
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    aac_compact_owner_enter(&decoder->compact);
#endif
    esp_audio_err_t result=esp_audio_simple_dec_reset(decoder->codec);
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
    aac_compact_owner_leave();
#endif
    return result;
}
#endif

const char *native_aac_decoder_label(native_aac_decoder_t *decoder,
    const esp_audio_simple_dec_info_t *info, bool *format_is_pcm) {
    *format_is_pcm = true;
    if (!decoder || !decoder->codec || !info) return "AAC";
#ifdef YORADIO_AAC_PROFILE_METADATA
    return aac_profile_label(*profile_state(decoder),format_is_pcm);
#else
    return "AAC";
#endif
}

unsigned native_aac_decoder_source_channels(native_aac_decoder_t *decoder) {
#ifdef YORADIO_AAC_PROFILE_METADATA
    if(decoder && decoder->codec)return aac_profile_channels(*profile_state(decoder));
#else
    (void)decoder;
#endif
    return 0;
}
