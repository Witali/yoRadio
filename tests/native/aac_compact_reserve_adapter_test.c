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
/* PRODUCTION_NATIVE_ADAPTER */
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
