#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER 1
#define CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST 1
#define CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT 1
// Only allocator ownership is exercised here; ABI and DSP are not emulated.
typedef struct { char bytes[96]; } aac_sbr_owner_abi_t;
typedef struct { char bytes[32]; } owner_t;
typedef struct { char bytes[16]; } aac_sbr_control_abi_t;
typedef struct { void *owner, *pending_owner; bool ps_initialized, inside_sbr, allocation_failed; } aac_compact_owner_t;
static aac_compact_owner_t *current;
static aac_compact_owner_t *context(void) { return current; }
static size_t fail_request;
static unsigned live_owners, live, calls, fail_alloc, audit_live;
static void *alloc(size_t n,size_t size) {
    ++calls;if(fail_alloc){--fail_alloc;return NULL;}
    void *p=calloc(n,size);assert(p);++live;return p;
}
static void release(void *p) { if(p){assert(live);--live;free(p);} }
static void aac_pointer_audit_allocate(void *p,size_t bytes,aac_compact_owner_t *state) {
    if(p && state){assert(bytes);++audit_live;}
}
static void aac_pointer_audit_free(void *p,aac_compact_owner_t *state) {
    if(p && state){assert(audit_live);--audit_live;}
}
void *__real_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    (void)module;return alloc(n,size);
}
void __real_media_lib_free(void *p) {release(p);}
#define calloc alloc
#define free release
void *__real_media_lib_module_calloc(const char *,size_t,size_t);
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
static bool skip_prepare;
void aac_compact_owner_test_skip_prepare(bool skip) {
    assert(!context());skip_prepare=skip;
}
#endif
void aac_compact_owner_prepare(aac_compact_owner_t *state) {
    assert(state && !state->owner && !state->pending_owner && !context());
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(skip_prepare)return;
#endif
    // Reserve the actual configured compact layout, before core/PCM split
    // the heap. An unsuccessful reservation must not prohibit AAC-LC.
    state->pending_owner = calloc(1, sizeof(owner_t));
}
void aac_compact_owner_discard_pending(aac_compact_owner_t *state) {
    assert(state && !context());
    free(state->pending_owner);
    state->pending_owner = NULL;
}
#endif
void *__wrap_media_lib_module_calloc(const char *module,size_t n,size_t size) {
    aac_compact_owner_t *state=context();
    bool owner_request=state && n==1 && size==sizeof(aac_sbr_owner_abi_t);
    void *p;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
    if(state && n==1 && size==fail_request) { fail_request=0;p=NULL; }
    else
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
    if(owner_request && state->pending_owner) {
        p=state->pending_owner;state->pending_owner=NULL;
    } else
#endif
    p=__real_media_lib_module_calloc(module,n,owner_request?sizeof(owner_t):size);
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_allocate(p,n*(owner_request?sizeof(owner_t):size),state);
#endif
    if(owner_request && p) {
        assert(!state->owner);state->owner=p;state->ps_initialized=false;
#ifdef AAC_HIGH_HISTORY_PC19_SIDECAR
        memset(state->high_history.pc19_extra,0,sizeof(state->high_history.pc19_extra));
#endif
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
        ++live_owners;
#endif
    }
    if(state && !p && n==1 &&
       (size==sizeof(aac_sbr_owner_abi_t) || size==sizeof(aac_sbr_control_abi_t)))
        state->allocation_failed=true;
    return p;
}
void __real_media_lib_free(void *);
void __wrap_media_lib_free(void *p) {
    aac_compact_owner_t *state=context();
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
    aac_pointer_audit_free(p,state);
#endif
    if(state && p && state->owner==p) {
        assert(!state->inside_sbr);state->owner=NULL;state->ps_initialized=false;
#ifdef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
        assert(live_owners);--live_owners;
#endif
    }
    __real_media_lib_free(p);
}

#undef calloc
#undef free
static void enter(aac_compact_owner_t *s) { assert(!current);current=s;s->allocation_failed=false; }
static void leave(void) { assert(current);current=NULL; }
// Appended to the actual reservation wrapper test prefix and native adapter.
#undef CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST
#undef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
#define CONFIG_YORADIO_AAC_COMPACT_SBR 1
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS == 0
#define native_aac_decoder_input_growth_ready(decoder) false
#endif
#define NATIVE_AAC_PCM_FRAME_BYTES 8192
typedef int esp_audio_err_t;
typedef void *esp_audio_simple_dec_handle_t;
typedef struct native_aac_decoder native_aac_decoder_t;
enum { ESP_AUDIO_ERR_OK=0, ESP_AUDIO_ERR_FAIL=-1, ESP_AUDIO_ERR_MEM_LACK=-2,
       ESP_AUDIO_ERR_INVALID_PARAMETER=-5, ESP_AUDIO_ERR_NOT_FOUND=-7,
       ESP_AUDIO_ERR_BUFF_NOT_ENOUGH=-8, ESP_AUDIO_SIMPLE_DEC_TYPE_AAC=1 };
typedef struct { bool aac_plus_enable; } esp_aac_dec_cfg_t;
static esp_aac_dec_cfg_t native_aac_decoder_config(void) { return (esp_aac_dec_cfg_t){true}; }
typedef struct { int dec_type; void *dec_cfg; int cfg_size; bool use_frame_dec; } esp_audio_simple_dec_cfg_t;
typedef struct { uint8_t *buffer; uint32_t len; bool eos; uint32_t consumed; } esp_audio_simple_dec_raw_t;
typedef struct { uint8_t *buffer; uint32_t len, needed_size, decoded_size; } esp_audio_simple_dec_out_t;
typedef struct { uint32_t sample_rate; uint8_t bits_per_sample, channel; uint32_t bitrate, frame_size; } esp_audio_simple_dec_info_t;
static unsigned mode, fail_open, opens, closes;
static void *control;
static esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,void **p) {
    assert(context() && cfg->use_frame_dec);
    if(fail_open){--fail_open;return ESP_AUDIO_ERR_MEM_LACK;}
    *p=(void*)1;++opens;return ESP_AUDIO_ERR_OK;
}
static void esp_audio_simple_dec_close(void *p) {
    assert(p && context());
    if(context()->owner)__wrap_media_lib_free(context()->owner);
    if(control){__wrap_media_lib_free(control);control=NULL;}
    ++closes;
}
static esp_audio_err_t esp_audio_simple_dec_process(void *p,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *out) {
    assert(p && context() && raw->len==12);
    if(mode && !context()->owner) {
        void *owner=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_owner_abi_t));
        if(owner)control=__wrap_media_lib_module_calloc("AAC",1,sizeof(aac_sbr_control_abi_t));
    }
    // Match the SDK's misleading core-only success on an SBR failure.
    out->decoded_size=mode && context()->owner && control ? 8192:4096;
    raw->consumed=raw->len;return ESP_AUDIO_ERR_OK;
}
static esp_audio_err_t esp_audio_simple_dec_get_info(void *p,esp_audio_simple_dec_info_t *info) {
    (void)p;(void)info;return ESP_AUDIO_ERR_OK;
}
#define aac_compact_owner_enter enter
#define aac_compact_owner_leave leave
#define codec_memory_trace_dump(stage) ((void)0)

#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_TEST
#endif
#ifdef CONFIG_YORADIO_AAC_COMPACT_SBR
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SBR_RESERVE
#endif
#ifdef CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE
#endif
#if CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS
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
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
        aac_compact_owner_prepare(&decoder->compact);
#endif
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
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
    aac_compact_owner_discard_pending(&decoder->compact);
#endif
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

#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
bool native_aac_decoder_input_growth_ready(const native_aac_decoder_t *decoder) {
    return decoder && decoder->codec && !decoder->compact.allocation_failed &&
           (decoder->compact.owner || decoder->compact.pending_owner);
}
#endif

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
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
bool native_aac_decoder_test_pending_owner(native_aac_decoder_t *decoder) {
    assert(decoder);
    return decoder->compact.pending_owner != NULL;
}
#endif
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
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
                        // An unused reservation has no codec pointers yet.
                        // Keep it across LC header changes; active owners were
                        // released by close_codec and must be prepared again.
                        if (!decoder->compact.pending_owner)
                            aac_compact_owner_prepare(&decoder->compact);
#else
                        aac_compact_owner_discard_pending(&decoder->compact);
                        aac_compact_owner_prepare(&decoder->compact);
#endif
#endif
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
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
                    if (decoder->compact.pending_owner &&
                        (result == ESP_AUDIO_ERR_MEM_LACK || result == ESP_AUDIO_ERR_FAIL)) {
                        // Preserve LC opening under pressure, just as the legacy
                        // reserve does. Keep the retry scoped to this owner too.
                        aac_compact_owner_discard_pending(&decoder->compact);
                        decoder->codec = NULL;
                        aac_compact_owner_enter(&decoder->compact);
                        result = esp_audio_simple_dec_open(&config, &decoder->codec);
                        aac_compact_owner_leave();
                    }
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
#if defined(CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER) && CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS == 0
                // LC returns unused storage after real PCM, not a parser-only
                // call or buffer retry. Later implicit SBR still allocates normally.
                // The optional input-growth policy instead retains this block
                // so occupied extra packets cannot consume the late SBR owner.
                if (result == ESP_AUDIO_ERR_OK && output->decoded_size)
                    aac_compact_owner_discard_pending(&decoder->compact);
#endif
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

static esp_audio_err_t feed(native_aac_decoder_t *d,unsigned signature,unsigned capacity,unsigned *pcm) {
    uint8_t input[12]={0xff,0xf1,signature,0x80,1,0x9f,0xfc},output[8192];
    esp_audio_simple_dec_raw_t raw={.buffer=input,.len=12};
    esp_audio_simple_dec_out_t out={.buffer=output,.len=capacity};
    esp_audio_err_t result=native_aac_decoder_process(d,&raw,&out);
    *pcm=out.decoded_size;assert(!current);return result;
}
static void destroy(native_aac_decoder_t *d) {
    native_aac_decoder_destroy(d);
    assert(!live && !audit_live && !live_owners && opens==closes && !current);
}
int main(void) {
    unsigned pcm;
    native_aac_decoder_t *d=native_aac_decoder_create();assert(d->compact.pending_owner);
    assert(!native_aac_decoder_input_growth_ready(NULL));
    assert(!native_aac_decoder_input_growth_ready(d)); // No open codec yet.
    destroy(d); // Stop before input.
    d=native_aac_decoder_create();
    assert(feed(d,0x50,1024,&pcm)==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH && !pcm && d->compact.pending_owner);
    assert(!native_aac_decoder_input_growth_ready(d));
    mode=0;assert(feed(d,0x50,8192,&pcm)==0 && pcm==4096);
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
    void *pending=d->compact.pending_owner;
    assert(pending && native_aac_decoder_input_growth_ready(d));
    unsigned before=calls;
    assert(feed(d,0x4c,8192,&pcm)==0 && pcm==4096);
    assert(d->compact.pending_owner==pending && calls==before); // Reuse on LC reopen.
#else
    assert(!d->compact.pending_owner);
    assert(!native_aac_decoder_input_growth_ready(d));
#endif
    // Return to the initial signature before late SBR; pending stays owned.
    assert(feed(d,0x50,8192,&pcm)==0 && pcm==4096);
    mode=1;assert(feed(d,0x50,8192,&pcm)==0 && pcm==8192 && d->compact.owner); // Late SBR.
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
    assert(d->compact.owner==pending); // Transfer, no second owner allocation.
    assert(native_aac_decoder_input_growth_ready(d));
#endif
    assert(feed(d,0x4c,8192,&pcm)==0 && pcm==8192 && d->compact.owner && !d->compact.pending_owner); // Reopen.
#if CONFIG_YORADIO_AAC_INPUT_EXTRA_SLOTS > 0
    assert(native_aac_decoder_input_growth_ready(d));
#endif
    destroy(d);
    mode=0;d=native_aac_decoder_create();
    assert(feed(d,0x50,8192,&pcm)==0 && pcm==4096);destroy(d); // Stop with LC reservation.
    fail_alloc=1;d=native_aac_decoder_create();assert(!d->compact.pending_owner);
    assert(feed(d,0x50,8192,&pcm)==0 && pcm==4096);
    assert(!native_aac_decoder_input_growth_ready(d));destroy(d); // LC still works.
    mode=1;
    d=native_aac_decoder_create();fail_request=sizeof(aac_sbr_owner_abi_t);
    assert(feed(d,0x50,8192,&pcm)==ESP_AUDIO_ERR_MEM_LACK && !pcm && d->compact.pending_owner);
    assert(!native_aac_decoder_input_growth_ready(d));
    destroy(d); // Never accept SDK's silent LC fallback; pending block remains ours.
    mode=0;d=native_aac_decoder_create();fail_open=1;
    assert(feed(d,0x50,8192,&pcm)==0 && pcm==4096 && !d->compact.pending_owner);destroy(d);
    d=native_aac_decoder_create();fail_open=2;
    assert(feed(d,0x50,8192,&pcm)==ESP_AUDIO_ERR_MEM_LACK && !pcm && !d->compact.pending_owner);destroy(d);
    puts("PASS actual native AAC adapter: Stop, output retry, LC release, implicit SBR, input-growth eligibility, profile reopen, no silent fallback, failed-open retry/cleanup; DSP mocked");
}
