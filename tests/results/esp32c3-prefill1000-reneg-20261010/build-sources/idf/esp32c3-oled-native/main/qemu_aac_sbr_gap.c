// QEMU-only regression: SBR is removed from parser-verified FIL spans while
// preserving all core audio bits. Test paired output, reset and partial close.
#include "sdkconfig.h"
#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DATA(name) \
    extern const uint8_t name##_start[] asm("_binary_" #name "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" #name "_aac_end")
#define PAIR(name) DATA(source_##name);DATA(missing_##name)
PAIR(he_44100_stereo);PAIR(he_48000_stereo);PAIR(hev2_44100_stereo);PAIR(he_32000_mono);
typedef struct {
    const char *name;
    const uint8_t *source,*source_end,*missing,*missing_end;
    uint32_t rate;
    unsigned channels,frames;
    bool duplicate_mono;
    const char *label;
} fixture_t;
#define CASE(name,hz,ch,n,mono,label) {#name,source_##name##_start,source_##name##_end, \
    missing_##name##_start,missing_##name##_end,hz,ch,n,mono,label}
static const fixture_t fixtures[]={
    CASE(he_44100_stereo,44100,2,14,false,"HE-AAC"),CASE(he_48000_stereo,48000,2,15,false,"HE-AAC"),
    CASE(hev2_44100_stereo,44100,2,15,false,"HE-AACv2"),
    // The native SDK duplicates non-PS mono SBR to stereo by default.
    // Prove this against its unmodified controller and check every L/R pair.
    CASE(he_32000_mono,32000,2,11,true,"HE-AAC")
};
enum { GUARD_BYTES=16, CAPTURE_BYTES=256, SBR_SAMPLES_PER_CHANNEL=2048 };
esp_audio_err_t native_aac_decoder_reset_for_test(native_aac_decoder_t *);
void aac_compact_owner_test_assert_idle(void);

static uint32_t instruction_count(void) {
    uint32_t n;__asm__ volatile("csrr %0, minstret" : "=r"(n) :: "memory");return n;
}
static void check_instruction_counter(void) {
    portMUX_TYPE lock=portMUX_INITIALIZER_UNLOCKED;uint32_t before,after;
    taskENTER_CRITICAL(&lock);
    __asm__ volatile("csrr %0, minstret\n.rept 1024\nnop\n.endr\ncsrr %1, minstret\n"
                     : "=r"(before),"=r"(after) :: "memory");
    taskEXIT_CRITICAL(&lock);assert(after-before==1025);
    printf("AAC_GAP_WORK_COUNTER nop1024=%" PRIu32 "\n",after-before);
}

static uint8_t *new_output(void) {
    uint8_t *p=malloc(NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);assert(p);
    memset(p,0xa5,NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);return p+GUARD_BYTES;
}
static void guard(const uint8_t *p) {
    for(unsigned i=0;i<GUARD_BYTES;++i) {
        assert(p[(int)i-GUARD_BYTES]==0xa5);
        assert(p[NATIVE_AAC_PCM_FRAME_BYTES+i]==0xa5);
    }
}
static void info(native_aac_decoder_t *decoder,const fixture_t *f) {
    esp_audio_simple_dec_info_t i={0};
    assert(native_aac_decoder_get_info(decoder,&i)==ESP_AUDIO_ERR_OK);
    if(i.sample_rate!=f->rate || i.channel!=f->channels)
        printf("AAC_GAP_FORMAT_FAILURE case=%s rate=%" PRIu32 " channels=%u\n",f->name,i.sample_rate,i.channel);
    assert(i.sample_rate==f->rate && i.channel==f->channels && i.bits_per_sample==16);
    bool pcm_only;
    assert(!strcmp(native_aac_decoder_label(decoder,&i,&pcm_only),f->label) && !pcm_only);
    assert(native_aac_decoder_source_channels(decoder)==(f->duplicate_mono ? 1 : f->channels));
}
static void capture(const fixture_t *f,unsigned phase,unsigned frame,const uint8_t *pcm,unsigned bytes) {
#ifdef CONFIG_YORADIO_QEMU_AAC_LATE_SBR_CAPTURE
    static const char digits[]="0123456789abcdef";char hex[2*CAPTURE_BYTES+1];
    printf("AAC_GAP_PCM_FRAME case=%s phase=%u frame=%u rate=%" PRIu32 " channels=%u bytes=%u\n",
           f->name,phase,frame,f->rate,f->channels,bytes);
    for(unsigned offset=0;offset<bytes;offset+=CAPTURE_BYTES) {
        unsigned size=bytes-offset;if(size>CAPTURE_BYTES)size=CAPTURE_BYTES;
        for(unsigned i=0;i<size;++i) {hex[2*i]=digits[pcm[offset+i]>>4];hex[2*i+1]=digits[pcm[offset+i]&15];}
        hex[2*size]=0;
        printf("AAC_GAP_PCM_DATA offset=%u hex=%s\n",offset,hex);
    }
#else
    (void)f;(void)phase;(void)frame;(void)pcm;(void)bytes;
#endif
}
static unsigned decode_pair(native_aac_decoder_t *a,native_aac_decoder_t *b,
        uint8_t *pa,uint8_t *pb,const fixture_t *f,bool missing,unsigned phase,bool record) {
    const uint8_t *p=missing?f->missing:f->source,*end=missing?f->missing_end:f->source_end;
    unsigned frames=0,call=0;uint64_t instructions=0;
    const unsigned chunks[]={1,7,193,31}; // split sync/header/payload boundaries
    while(p<end) {
        size_t count=end-p,chunk=chunks[call++%4];if(count>chunk)count=chunk;
        esp_audio_simple_dec_raw_t ar={.buffer=(uint8_t *)p,.len=count},br=ar;
        esp_audio_simple_dec_out_t ao={.buffer=pa,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        esp_audio_simple_dec_out_t bo={.buffer=pb,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        memset(pa,0x55,NATIVE_AAC_PCM_FRAME_BYTES);memset(pb,0xaa,NATIVE_AAC_PCM_FRAME_BYTES);
        uint32_t before=instruction_count();
        esp_audio_err_t result=native_aac_decoder_process(a,&ar,&ao);
        instructions+=(uint32_t)(instruction_count()-before);
        assert(result==ESP_AUDIO_ERR_OK);
        assert(native_aac_decoder_process(b,&br,&bo)==ESP_AUDIO_ERR_OK);
        guard(pa);guard(pb);
        assert(ar.consumed<=count && ar.consumed==br.consumed && (ar.consumed || ao.decoded_size));
        assert(ao.decoded_size==bo.decoded_size && ao.decoded_size<=NATIVE_AAC_PCM_FRAME_BYTES);
        assert(!memcmp(pa,pb,ao.decoded_size));p+=ar.consumed;
        if(ao.decoded_size) {
            if(ao.decoded_size!=SBR_SAMPLES_PER_CHANNEL*f->channels*sizeof(int16_t))
                printf("AAC_GAP_SIZE_FAILURE case=%s phase=%u frame=%u actual_bytes=%" PRIu32 "\n",f->name,phase,frames,ao.decoded_size);
            info(a,f);info(b,f);
            assert(ao.decoded_size==SBR_SAMPLES_PER_CHANNEL*f->channels*sizeof(int16_t));
            if(f->duplicate_mono) {
                const int16_t *samples=(const int16_t *)pa;
                for(unsigned i=0;i<ao.decoded_size/sizeof(int16_t);i+=2)assert(samples[i]==samples[i+1]);
            }
            if(record)capture(f,phase,frames,pa,ao.decoded_size);
            ++frames;vTaskDelay(1);
        }
    }
    assert(frames==f->frames);
    if(record)printf("AAC_GAP_WORK case=%s phase=%u frames=%u calls=%u instructions=%" PRIu64 "\n",
                     f->name,phase,frames,call,instructions);
    return frames;
}

void qemu_aac_sbr_gap_test(void) {
    check_instruction_counter();
    native_aac_decoder_t *sizing=native_aac_decoder_create();assert(sizing);
    size_t requested,allocated;native_aac_decoder_test_footprint(sizing,&requested,&allocated);
    printf("AAC_GAP_ADAPTER_MEMORY requested=%u allocated=%u\n",(unsigned)requested,(unsigned)allocated);
    native_aac_decoder_destroy(sizing);
    unsigned total=0;
    for(unsigned index=0;index<sizeof(fixtures)/sizeof(fixtures[0]);++index) {
        const fixture_t *f=&fixtures[index];
        native_aac_decoder_t *a=native_aac_decoder_create(),*b=native_aac_decoder_create();assert(a && b);
        uint8_t *pa=new_output(),*pb=new_output();
        if(f->duplicate_mono) {
            native_aac_decoder_test_disable_late_sbr(a);
            decode_pair(a,b,pa,pb,f,false,0,false);
            native_aac_decoder_destroy(a);native_aac_decoder_destroy(b);
            a=native_aac_decoder_create();b=native_aac_decoder_create();assert(a && b);
            printf("AAC_GAP_MONO_CONTROL_PASS source_channels=1 pcm_channels=2 rate=32000 duplicated_pairs=exact controller_pcm=exact\n");
        }
        for(unsigned phase=0;phase<3;++phase)
            total+=decode_pair(a,b,pa,pb,f,phase==1,phase,true)*SBR_SAMPLES_PER_CHANNEL*f->channels;
        // Reset while retained SBR is active, then compare with a fresh decoder.
        decode_pair(a,b,pa,pb,f,true,0,false);
        assert(native_aac_decoder_reset_for_test(a)==ESP_AUDIO_ERR_OK);
        native_aac_decoder_destroy(b);b=native_aac_decoder_create();assert(b);
        decode_pair(a,b,pa,pb,f,false,0,false);
        // Destruction with a partially buffered frame must free its allocations.
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)f->source,.len=9};
        esp_audio_simple_dec_out_t out={.buffer=pa,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        assert(native_aac_decoder_process(a,&raw,&out)==ESP_AUDIO_ERR_OK);
        assert(raw.consumed==9 && !out.decoded_size);guard(pa);
        native_aac_decoder_destroy(a);native_aac_decoder_destroy(b);
        free(pa-GUARD_BYTES);free(pb-GUARD_BYTES);
        aac_compact_owner_test_assert_idle();assert(heap_caps_check_integrity_all(true));
        printf("AAC_GAP_PASS case=%s frames_per_phase=%u phases=3 reset_vs_fresh=exact partial_close=9\n",f->name,f->frames);
    }
    printf("AAC_GAP_SUITE_PASS cases=4 capture_channel_samples=%u heap=valid\n",total);
}
