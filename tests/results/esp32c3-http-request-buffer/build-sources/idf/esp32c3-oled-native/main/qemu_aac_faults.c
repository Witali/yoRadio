// Real-library fault checks: late allocation failure, malformed FIL and cleanup.
#include "native_aac_decoder.h"
#include "aac_sbr_abi.h"
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
DATA(lc_22050_mono);DATA(hev2_44100_stereo);
DATA(header_only);DATA(sbr_truncated);DATA(sbr_count_overrun);DATA(fill_count_overrun);
void aac_compact_owner_test_fail_next(size_t);
void aac_compact_owner_test_assert_idle(void);
enum { GUARD_BYTES=16 };
typedef enum { VALID_STREAM, MEMORY_ERROR, MALFORMED_NO_PCM } decode_expectation_t;

static void no_profile(native_aac_decoder_t *decoder) {
    bool pcm_only=false;esp_audio_simple_dec_info_t info={0};
    assert(!strcmp(native_aac_decoder_label(decoder,&info,&pcm_only),"AAC") && pcm_only);
    assert(!native_aac_decoder_source_channels(decoder));
}

static uint8_t *new_pcm(void) {
    uint8_t *p=malloc(NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);assert(p);
    memset(p,0xa5,NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);return p+GUARD_BYTES;
}
static void guards(const uint8_t *p) {
    for(unsigned i=0;i<GUARD_BYTES;++i)
        assert(p[(int)i-GUARD_BYTES]==0xa5 && p[NATIVE_AAC_PCM_FRAME_BYTES+i]==0xa5);
}
static unsigned decode(native_aac_decoder_t *decoder,uint8_t *pcm,
                       const uint8_t *start,const uint8_t *end,unsigned rate,unsigned channels,
                       decode_expectation_t expected) {
    unsigned frames=0;
    while(start<end) {
        size_t count=end-start;if(count>31)count=31;
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)start,.len=count};
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        esp_audio_err_t result=native_aac_decoder_process(decoder,&raw,&out);
        guards(pcm);assert(raw.consumed<=count);
        if(result!=ESP_AUDIO_ERR_OK) {
            assert(expected!=VALID_STREAM && !frames && !out.decoded_size);
            if(expected==MEMORY_ERROR)assert(result==ESP_AUDIO_ERR_MEM_LACK);
            else assert(result==ESP_AUDIO_ERR_FAIL || result==ESP_AUDIO_ERR_DATA_LACK ||
                        result==ESP_AUDIO_ERR_HEADER_PARSE);
            no_profile(decoder);
            printf("AAC_FAULT_OUTCOME public_error=%d pcm_bytes=0\n",result);
            return 0;
        }
        assert(raw.consumed || out.decoded_size);start+=raw.consumed;
        if(out.decoded_size) {
            assert(expected==VALID_STREAM);
            esp_audio_simple_dec_info_t info;
            assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
            assert(info.sample_rate==rate && info.channel==channels && info.bits_per_sample==16);
            ++frames;vTaskDelay(1);
        }
    }
    // The simple-decoder layer may consume a malformed frame and return OK
    // with no output even when the inner AAC decoder reported an error.
    if(expected==MALFORMED_NO_PCM) {
        assert(!frames);no_profile(decoder);
        printf("AAC_FAULT_OUTCOME public_error=0 pcm_bytes=0\n");return 0;
    }
    assert(expected==VALID_STREAM && frames);return frames;
}
static void release(native_aac_decoder_t *decoder) {
    native_aac_decoder_destroy(decoder);aac_compact_owner_test_assert_idle();
    assert(heap_caps_check_integrity_all(true));
}

void qemu_aac_faults_test(void) {
    uint8_t *pcm=new_pcm();unsigned recoveries=0;
    for(unsigned repeats=1;repeats<=2;++repeats) {
        for(unsigned fail=0;fail<2;++fail) {
            native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
            for(unsigned n=0;n<repeats;++n)
                assert(decode(decoder,pcm,lc_22050_mono_start,lc_22050_mono_end,22050,1,VALID_STREAM)==13);
            printf("AAC_FAULT_BEGIN kind=late_oom parity=%u allocation=%s\n",repeats%2,fail?"control":"owner");fflush(stdout);
            aac_compact_owner_test_fail_next(fail?sizeof(aac_sbr_control_abi_t):sizeof(aac_sbr_owner_abi_t));
            decode(decoder,pcm,hev2_44100_stereo_start,hev2_44100_stereo_end,44100,2,MEMORY_ERROR);
            release(decoder);
            decoder=native_aac_decoder_create();assert(decoder);
            assert(decode(decoder,pcm,hev2_44100_stereo_start,hev2_44100_stereo_end,44100,2,VALID_STREAM)==15);
            release(decoder);++recoveries;
            printf("AAC_LATE_OOM_PASS parity=%u allocation=%s suppressed_pcm=1 recovery_frames=15\n",repeats%2,fail?"control":"owner");
        }
    }
    const struct { const char *name;const uint8_t *start,*end; } damaged[]={
        {"header_only",header_only_start,header_only_end},
        {"sbr_truncated",sbr_truncated_start,sbr_truncated_end},
        {"sbr_count_overrun",sbr_count_overrun_start,sbr_count_overrun_end},
        {"fill_count_overrun",fill_count_overrun_start,fill_count_overrun_end}
    };
    for(unsigned i=0;i<sizeof(damaged)/sizeof(damaged[0]);++i) {
        printf("AAC_FAULT_BEGIN kind=malformed case=%s\n",damaged[i].name);fflush(stdout);
        native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
        decode(decoder,pcm,damaged[i].start,damaged[i].end,0,0,MALFORMED_NO_PCM);
        release(decoder);
        decoder=native_aac_decoder_create();assert(decoder);
        assert(decode(decoder,pcm,hev2_44100_stereo_start,hev2_44100_stereo_end,44100,2,VALID_STREAM)==15);
        release(decoder);++recoveries;
        printf("AAC_MALFORMED_PASS case=%s recovery_frames=15\n",damaged[i].name);
    }
    free(pcm-GUARD_BYTES);assert(heap_caps_check_integrity_all(true));
    printf("AAC_FAULTS_PASS late_oom=4 malformed=4 recoveries=%u heap=valid\n",recoveries);
}
