// Real native-library metadata checks, independent of output channel duplication.
#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DATA(name) \
    extern const uint8_t name##_start[] asm("_binary_" #name "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" #name "_aac_end")
DATA(lc_48000_stereo);DATA(he_48000_stereo);DATA(hev2_44100_stereo);DATA(he_mono_metadata);
typedef struct {
    const char *name,*label;
    const uint8_t *start,*end;
    unsigned rate,source_channels,frames;
    bool pcm_only;
} fixture_t;
#define CASE(name,label,hz,ch,n,pcm) {#name,label,name##_start,name##_end,hz,ch,n,pcm}
static const fixture_t fixtures[]={
    CASE(lc_48000_stereo,"AAC",48000,2,26,true),
    CASE(he_48000_stereo,"HE-AAC",48000,2,15,false),
    CASE(hev2_44100_stereo,"HE-AACv2",44100,2,15,false),
    CASE(he_mono_metadata,"HE-AAC",32000,1,11,false)
};

static void check(native_aac_decoder_t *decoder,const fixture_t *f) {
    esp_audio_simple_dec_info_t info;
    assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
    bool pcm_only;
    const char *label=native_aac_decoder_label(decoder,&info,&pcm_only);
    if(strcmp(label,f->label) || native_aac_decoder_source_channels(decoder)!=f->source_channels)
        printf("AAC_METADATA_FAILURE case=%s label=%s source_channels=%u\n",
               f->name,label,native_aac_decoder_source_channels(decoder));
    assert(!strcmp(label,f->label) && pcm_only==f->pcm_only);
    assert(native_aac_decoder_source_channels(decoder)==f->source_channels);
    assert(info.sample_rate==f->rate && info.channel==2 && info.bits_per_sample==16);
}

static unsigned decode(native_aac_decoder_t *decoder,const fixture_t *f,
                       native_aac_decoder_t *other,const fixture_t *other_format) {
    uint8_t *pcm=malloc(NATIVE_AAC_PCM_FRAME_BYTES);assert(pcm);
    unsigned frames=0,calls=0;
    const unsigned chunks[]={1,7,31,193};
    for(const uint8_t *p=f->start;p<f->end;) {
        size_t size=f->end-p,chunk=chunks[calls++%4];if(size>chunk)size=chunk;
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)p,.len=size};
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        assert(native_aac_decoder_process(decoder,&raw,&out)==ESP_AUDIO_ERR_OK);
        assert(raw.consumed<=size && (raw.consumed || out.decoded_size));p+=raw.consumed;
        if(other)check(other,other_format);
        if(out.decoded_size) {
            check(decoder,f);++frames;
            if(f->source_channels==1) {
                const int16_t *samples=(const int16_t *)pcm;
                assert(out.decoded_size%4==0);
                for(unsigned i=0;i<out.decoded_size/sizeof(int16_t);i+=2)
                    assert(samples[i]==samples[i+1]);
            }
            vTaskDelay(1);
        } else if(frames)check(decoder,f); // Incomplete network input keeps the last valid format.
    }
    assert(frames==f->frames);free(pcm);
    printf("AAC_METADATA_CASE case=%s label=%s source_channels=%u pcm_channels=2 rate=%u frames=%u\n",
           f->name,f->label,f->source_channels,f->rate,frames);
    return frames;
}

void qemu_aac_metadata_test(void) {
    native_aac_decoder_t *a=native_aac_decoder_create(),*b=native_aac_decoder_create();assert(a && b);
    esp_audio_simple_dec_info_t dummy={0};bool pcm_only=false;
    assert(!strcmp(native_aac_decoder_label(a,&dummy,&pcm_only),"AAC") && pcm_only);
    assert(!native_aac_decoder_source_channels(a));
    unsigned frames=decode(a,&fixtures[2],NULL,NULL);
    frames+=decode(b,&fixtures[3],a,&fixtures[2]);
    // Reopen on changed ADTS configuration; a second decoder retains its PS state.
    frames+=decode(b,&fixtures[0],a,&fixtures[2]);
    frames+=decode(b,&fixtures[1],a,&fixtures[2]);
    frames+=decode(b,&fixtures[2],a,&fixtures[2]);
    frames+=decode(b,&fixtures[3],a,&fixtures[2]);
#if defined(CONFIG_YORADIO_QEMU_AAC_RESET_TEST) || defined(CONFIG_YORADIO_QEMU_AAC_COMPACT_ADAPTER_TEST)
    esp_audio_err_t native_aac_decoder_reset_for_test(native_aac_decoder_t *);
    assert(native_aac_decoder_reset_for_test(b)==ESP_AUDIO_ERR_OK);
    assert(!strcmp(native_aac_decoder_label(b,&dummy,&pcm_only),"AAC") && pcm_only);
    assert(!native_aac_decoder_source_channels(b));
    frames+=decode(b,&fixtures[3],a,&fixtures[2]);
    printf("AAC_METADATA_RESET_PASS\n");
#endif
    native_aac_decoder_destroy(a);native_aac_decoder_destroy(b);
    assert(heap_caps_check_integrity_all(true));
    printf("AAC_METADATA_PASS frames=%u decoder_isolation=2 mono_duplicated=verified heap=valid\n",frames);
}
