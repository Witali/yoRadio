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

#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
bool native_aac_decoder_test_pending_owner(native_aac_decoder_t *);
void aac_compact_owner_test_skip_prepare(bool);
// Consume real heap outside the decoder. This changes available capacity, not
// allocator return values. No Wi-Fi/TLS timing claim follows from this test.
enum { PRESSURE_BLOCK_BYTES=4096, PRESSURE_BLOCK_COUNT=128,
       PRESSURE_MIN_FREE=32*1024, PRESSURE_MAX_FREE=112*1024,
       PRESSURE_STEP=4*1024, LC_FIXTURE_FRAMES=13 };
static void *pressure_blocks[PRESSURE_BLOCK_COUNT];
static size_t pressure_begin(size_t target) {
    unsigned used=0;
    while(heap_caps_get_free_size(MALLOC_CAP_8BIT)>target+PRESSURE_BLOCK_BYTES) {
        assert(used<PRESSURE_BLOCK_COUNT);
        pressure_blocks[used]=heap_caps_malloc(PRESSURE_BLOCK_BYTES,MALLOC_CAP_8BIT);
        assert(pressure_blocks[used]);++used;
    }
    return heap_caps_get_free_size(MALLOC_CAP_8BIT);
}
static void pressure_end(void) {
    for(unsigned i=0;i<PRESSURE_BLOCK_COUNT;++i) {
        free(pressure_blocks[i]);pressure_blocks[i]=NULL;
    }
}
static uint32_t early_owner_pressure(uint8_t *pcm,bool early) {
    unsigned successes=0, failures=0, reserved=0;
    uint32_t success_mask=0;
    aac_compact_owner_test_skip_prepare(!early);
    // Warm libc/logging before checking exact settled allocation recovery.
    printf("AAC_EARLY_PRESSURE_BEGIN real_heap=1 early=%u\n",early);fflush(stdout);
    for(size_t target=PRESSURE_MIN_FREE;target<=PRESSURE_MAX_FREE;target+=PRESSURE_STEP) {
        size_t baseline=heap_caps_get_free_size(MALLOC_CAP_8BIT);
        size_t available=pressure_begin(target);
        native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
        bool pending=native_aac_decoder_test_pending_owner(decoder);
        reserved+=pending;
        unsigned frames=0;
        esp_audio_err_t result=ESP_AUDIO_ERR_OK;
        for(const uint8_t *p=lc_22050_mono_start;p<lc_22050_mono_end;) {
            size_t count=lc_22050_mono_end-p;if(count>31)count=31;
            esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)p,.len=count};
            esp_audio_simple_dec_out_t out={.buffer=pcm,.len=NATIVE_AAC_PCM_FRAME_BYTES};
            result=native_aac_decoder_process(decoder,&raw,&out);
            guards(pcm);assert(raw.consumed<=count);
            if(result!=ESP_AUDIO_ERR_OK) {
                assert((result==ESP_AUDIO_ERR_MEM_LACK || result==ESP_AUDIO_ERR_FAIL) && !out.decoded_size);
                break;
            }
            assert(raw.consumed || out.decoded_size);p+=raw.consumed;
            if(out.decoded_size) {
                esp_audio_simple_dec_info_t info;
                assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
                assert(info.sample_rate==22050 && info.channel==1 && info.bits_per_sample==16);
                assert(!native_aac_decoder_test_pending_owner(decoder));++frames;
            }
        }
        pressure_end();
        if(result==ESP_AUDIO_ERR_OK) {
            assert(frames==LC_FIXTURE_FRAMES);++successes;
            success_mask|=1u<<((target-PRESSURE_MIN_FREE)/PRESSURE_STEP);
            // Preserve this LC decoder and its transform history for late SBR.
            assert(decode(decoder,pcm,hev2_44100_stereo_start,hev2_44100_stereo_end,44100,2,VALID_STREAM)==15);
        } else {
            ++failures;
            release(decoder);decoder=native_aac_decoder_create();assert(decoder);
            assert(decode(decoder,pcm,hev2_44100_stereo_start,hev2_44100_stereo_end,44100,2,VALID_STREAM)==15);
        }
        release(decoder);
        size_t recovered=heap_caps_get_free_size(MALLOC_CAP_8BIT);
        assert(recovered==baseline);
        printf("AAC_EARLY_PRESSURE_CASE early=%u target=%u available=%u pending=%u lc_result=%d lc_frames=%u recovery_frames=15 heap_restored=1\n",
               early,(unsigned)target,(unsigned)available,pending,result,frames);fflush(stdout);
    }
    assert(successes && failures && (early ? reserved>0 : reserved==0));
    printf("AAC_EARLY_PRESSURE_PASS early=%u cases=%u lc_success=%u lc_failure=%u reserved=%u heap=valid\n",
           early,successes+failures,successes,failures,reserved);
    aac_compact_owner_test_skip_prepare(false);
    return success_mask;
}
#endif

void qemu_aac_faults_test(void) {
    uint8_t *pcm=new_pcm();unsigned recoveries=0;
#ifdef CONFIG_YORADIO_AAC_COMPACT_EARLY_OWNER
    uint32_t control=early_owner_pressure(pcm,false);
    uint32_t candidate=early_owner_pressure(pcm,true);
    assert(!(control & ~candidate));
    printf("AAC_EARLY_PRESSURE_AB_PASS cases=42 no_lc_regression=1\n");
#endif
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
