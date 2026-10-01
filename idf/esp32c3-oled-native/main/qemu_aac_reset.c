// QEMU-only guarded reproduction and source repair of the pinned AAC reset ABI.
// Offsets are verified against the complete archive disassembly, not C types
// inferred by the decompiler. No DSP arithmetic is changed.
#include "native_aac_decoder.h"
#include "qemu_aac_packed_history.h"
#include "esp_log.h"
#include "esp_partition.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define CORE_BYTES 35460u
#define OLD_PS_POINTER 0x153dcu
#define PADDED_BYTES (OLD_PS_POINTER+4u)
#define GUARD 16u
typedef struct { uint8_t *raw, *core; size_t bytes; unsigned leg; } core_t;
static core_t cores[2];
static unsigned leg, enabled, observed, resets;
static const char *TAG="aac_reset";
void *__real_media_lib_module_calloc(const char *,size_t,size_t);
void __real_media_lib_free(void *);
void __real_PVMP4AudioDecoderResetBuffer(void *);
void *aac_sbr_layout_ps(void *);
void aac_sbr_layout_assert_idle(void);
esp_audio_err_t native_aac_decoder_reset_for_test(native_aac_decoder_t *);

static uint32_t word(void *base,size_t offset) { uint32_t v; memcpy(&v,(uint8_t*)base+offset,4);return v; }
static void put(void *base,size_t offset,uint32_t value) { memcpy((uint8_t*)base+offset,&value,4); }
static void *ptr(void *base,size_t offset) { return (void*)(uintptr_t)word(base,offset); }
static void zero(void *base,size_t offset,size_t bytes) { memset((uint8_t*)base+offset,0,bytes); }
static void guards(core_t *c) {
    for(unsigned i=0;i<GUARD;++i) { assert(c->raw[i]==0xa5);assert(c->core[c->bytes+i]==0x5a); }
}
bool qemu_aac_reset_calloc(const char *module,size_t n,size_t size,void **result) {
    if(!enabled || n!=1 || size!=CORE_BYTES) return false;
    core_t *c=cores+leg; assert(!c->core);
    size_t bytes=leg ? CORE_BYTES : PADDED_BYTES;
    uint8_t *raw=__real_media_lib_module_calloc(module,1,bytes+2*GUARD);assert(raw);
    memset(raw,0xa5,GUARD);memset(raw+GUARD+bytes,0x5a,GUARD);
    if(!leg) memset(raw+GUARD+CORE_BYTES,0xa6,bytes-CORE_BYTES);
    *c=(core_t){raw,raw+GUARD,bytes,leg};*result=c->core;return true;
}
bool qemu_aac_reset_free(void *p) {
    if(!p) return false;
    for(unsigned i=0;i<2;++i) if(cores[i].core==p) {
        guards(cores+i);__real_media_lib_free(cores[i].raw);memset(cores+i,0,sizeof(core_t));return true;
    }
    return false;
}

static void repaired_reset(uint8_t *core) {
    zero(core,0x1570,0x1000);zero(core,0x3a24,0x1000);
    uint8_t *sbr=ptr(core,0x8a58);
    if(sbr && !word(sbr,0xc980) && core[8]) {
        void *ps=aac_sbr_layout_ps(sbr);
        put(sbr,0xc984,(uintptr_t)ps); // Correct owner, replacing core+0x153dc.
        zero(core,0xf0,0x240);zero(core,0xb30,0x240);
        zero(sbr,0x42c0,0x900);zero(sbr,0x1160,40);
        zero(core,0x25a4,0x240);zero(core,0x2fe4,0x240);
        zero(sbr,0xa780,0x900);zero(sbr,0x7620,40);
        zero(sbr,0x11b8,0x400);zero(sbr,0x11a0,24);
        zero(sbr,0x4cc0,0x500);zero(sbr,0x51c0,0x500);
        zero(sbr,0x3e40,0x480);zero(sbr,0x39bc,0x480);
        void *control=ptr(core,0x8a5c);
        if(word(control,4)==1) {
            zero(sbr,0x7678,0x400);zero(sbr,0xa300,0x480);zero(sbr,0x7660,24);
            zero(sbr,0xb180,0x500);zero(sbr,0xb680,0x500);
        } else if(word(core,0xc0)==1) {
            void *hybrid=ptr(ps,0x1fc);
            for(unsigned row=0;row<3;++row) {
                memset(ptr(ptr(hybrid,12),row*4),0,48);
                memset(ptr(ptr(hybrid,16),row*4),0,48);
            }
        }
        put(sbr,4,1);put(sbr,0x64c4,1);put(control,0,0);put(sbr,0xc980,1);put(ps,0,0);
    }
    put(core,0,0);core[8]=core[0x8a80];
}
void __wrap_PVMP4AudioDecoderResetBuffer(void *core) {
    if(!enabled) { __real_PVMP4AudioDecoderResetBuffer(core);return; }
    core_t *c=cores+leg;assert(c->core==core);guards(c);
    if(leg) repaired_reset(core);
    else {
        uint8_t *sbr=ptr(core,0x8a58);
        bool will_write=sbr && !word(sbr,0xc980) && ((uint8_t*)core)[8];
        memset(c->core+CORE_BYTES,0xa6,PADDED_BYTES-CORE_BYTES);
        __real_PVMP4AudioDecoderResetBuffer(core);
        size_t end=will_write ? OLD_PS_POINTER : PADDED_BYTES;
        for(size_t i=CORE_BYTES;i<end;++i) assert(c->core[i]==0xa6);
        if(will_write) { assert(word(core,OLD_PS_POINTER)==(uintptr_t)(sbr+0xc988));++observed; }
    }
    guards(c);++resets;
}

#define FIXTURE(name,symbol) extern const uint8_t name##_start[] asm("_binary_" symbol "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" symbol "_aac_end")
FIXTURE(lc44,"lc_44100_stereo");FIXTURE(lc22,"lc_22050_mono");FIXTURE(lc48,"lc_48000_stereo");
FIXTURE(he44,"he_44100_stereo");FIXTURE(he48,"he_48000_stereo");FIXTURE(hev2,"hev2_44100_stereo");
void qemu_aac_reset_test(void) {
    const struct { const char *name;const uint8_t *start,*end;unsigned rate,channels; } files[]={
        {"lc44",lc44_start,lc44_end,44100,2},{"lc22",lc22_start,lc22_end,22050,1},
        {"lc48",lc48_start,lc48_end,48000,2},{"he44",he44_start,he44_end,44100,2},
        {"he48",he48_start,he48_end,48000,2},{"hev2",hev2_start,hev2_end,44100,2}};
    // The protective baseline padding makes two live HE decoders exceed C3
    // heap. Store the baseline call metadata/PCM in the disposable QEMU app1
    // partition, then compare one candidate instance byte-for-byte on replay.
    const esp_partition_t *capture=esp_partition_find_first(ESP_PARTITION_TYPE_APP,ESP_PARTITION_SUBTYPE_APP_OTA_1,NULL);
    assert(capture);uint8_t *pcm=malloc(8192),*reference=malloc(8192);assert(pcm && reference);enabled=1;
    for(unsigned f=0;f<6;++f) {
        packed_history_reset(0);
        uint32_t samples[2]={0,0};size_t captured=0;
        assert(esp_partition_erase_range(capture,0,0x80000)==ESP_OK);
        for(leg=0;leg<2;++leg) {
            native_aac_decoder_t *dec=native_aac_decoder_create();assert(dec);size_t offset=0;packed_history_select(leg);
            for(unsigned cycle=0;cycle<3;++cycle) {
                if(cycle)assert(native_aac_decoder_reset_for_test(dec)==ESP_AUDIO_ERR_OK);
                for(const uint8_t *p=files[f].start;p<files[f].end;) {
                    size_t count=files[f].end-p;if(count>193)count=193;
                    esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t*)p,.len=count};
                    while(raw.len) {
                        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=8192};
                        assert(native_aac_decoder_process(dec,&raw,&out)==ESP_AUDIO_ERR_OK);
                        esp_audio_simple_dec_info_t info={0};
                        if(out.decoded_size) {
                            assert(native_aac_decoder_get_info(dec,&info)==ESP_AUDIO_ERR_OK);
                            assert(info.sample_rate==files[f].rate && info.channel==files[f].channels && info.bits_per_sample==16);
                        }
                        uint32_t record[4]={raw.consumed,out.decoded_size,info.sample_rate,info.channel},expected[4];
                        assert(raw.consumed || out.decoded_size);assert(offset+16+out.decoded_size<=0x80000);
                        if(!leg) { assert(esp_partition_write(capture,offset,record,16)==ESP_OK); }
                        else { assert(esp_partition_read(capture,offset,expected,16)==ESP_OK);assert(!memcmp(record,expected,16)); }
                        offset+=16;
                        if(out.decoded_size) {
                            if(!leg)assert(esp_partition_write(capture,offset,pcm,out.decoded_size)==ESP_OK);
                            else { assert(esp_partition_read(capture,offset,reference,out.decoded_size)==ESP_OK);assert(!memcmp(pcm,reference,out.decoded_size)); }
                        }
                        offset+=out.decoded_size;samples[leg]+=out.decoded_size/2;
                        raw.buffer+=raw.consumed;raw.len-=raw.consumed;
                    }
                    p+=count;
                }
            }
            native_aac_decoder_destroy(dec);
            if(!leg)captured=offset;else assert(captured==offset && samples[0]==samples[1]);
        }
        packed_history_select(0);
        assert(!cores[0].core && !cores[1].core);aac_sbr_layout_assert_idle();
        ESP_LOGI(TAG,"AACRESET_PASS case=%s cycles=3 resets=2 samples=%lu PCM=exact guards=pass cleanup=complete",files[f].name,(unsigned long)samples[0]);
    }
    enabled=0;free(pcm);free(reference);assert(observed==6 && resets==24);
    ESP_LOGI(TAG,"AACRESET_COMPLETE baseline_oob_writes=%u paired_reset_calls=%u core_bytes=%u old_offset=%u",observed,resets,CORE_BYTES,OLD_PS_POINTER);
}
