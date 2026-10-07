// QEMU-only regression checks for the late-SBR controller experiment.
// Ordinary streams must stay bit-exact against the same storage implementation
// with the controller experiment disabled. Format checks on concatenated LC/HE
// streams do not establish the acoustic quality of their transition.
#include "sdkconfig.h"
#include "native_aac_decoder.h"
#include "decoder_pcm.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <assert.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>

#define FIXTURE(name) \
    extern const uint8_t name##_start[] asm("_binary_" #name "_aac_start"); \
    extern const uint8_t name##_end[] asm("_binary_" #name "_aac_end")
FIXTURE(lc_44100_stereo);
FIXTURE(lc_22050_mono);
FIXTURE(lc_48000_stereo);
FIXTURE(he_44100_stereo);
FIXTURE(he_48000_stereo);
FIXTURE(hev2_44100_stereo);

enum { GUARD_BYTES=16, CHUNK_BYTES=193, STEADY_REPEATS=3 };
typedef struct {
    const char *name;
    const uint8_t *start, *end;
    uint32_t rate;
    uint8_t channels;
} fixture_t;
#define CASE(name, rate, channels) {#name,name##_start,name##_end,rate,channels}
static const fixture_t fixtures[]={
    CASE(lc_44100_stereo,44100,2), CASE(lc_22050_mono,22050,1),
    CASE(lc_48000_stereo,48000,2), CASE(he_44100_stereo,44100,2),
    CASE(he_48000_stereo,48000,2), CASE(hev2_44100_stereo,44100,2)
};
static const char *TAG="late_sbr";

static uint8_t *new_pcm(void) {
    uint8_t *p=malloc(NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);
    assert(p);
    memset(p,0xa5,NATIVE_AAC_PCM_FRAME_BYTES+2*GUARD_BYTES);
    return p+GUARD_BYTES;
}

static void check_pcm(uint8_t *pcm,const esp_audio_simple_dec_out_t *out) {
    assert(out->decoded_size<=NATIVE_AAC_PCM_FRAME_BYTES);
    for(unsigned i=0;i<GUARD_BYTES;++i) {
        assert(pcm[(int)i-GUARD_BYTES]==0xa5);
        assert(pcm[NATIVE_AAC_PCM_FRAME_BYTES+i]==0xa5);
    }
}

static void check_info(native_aac_decoder_t *decoder,const fixture_t *fixture) {
    esp_audio_simple_dec_info_t info={0};
    assert(native_aac_decoder_get_info(decoder,&info)==ESP_AUDIO_ERR_OK);
    if(info.sample_rate!=fixture->rate || info.channel!=fixture->channels || info.bits_per_sample!=16)
        ESP_LOGE(TAG,"AAC_LATE_SBR_FORMAT_MISMATCH case=%s expected_rate=%" PRIu32 " expected_channels=%u actual_rate=%" PRIu32 " actual_channels=%u bits=%u",
                 fixture->name,fixture->rate,fixture->channels,info.sample_rate,info.channel,info.bits_per_sample);
    assert(info.sample_rate==fixture->rate && info.channel==fixture->channels &&
           info.bits_per_sample==16);
}

static void compare_ordinary(const fixture_t *fixture) {
    native_aac_decoder_t *reference=native_aac_decoder_create();
    native_aac_decoder_t *candidate=native_aac_decoder_create();
    assert(reference && candidate);
    native_aac_decoder_test_disable_late_sbr(reference);
    uint8_t *old_pcm=new_pcm(), *new_pcm_data=new_pcm();
    unsigned frames=0;
    uint32_t samples=0,hash=2166136261u;
    for(unsigned repeat=0;repeat<STEADY_REPEATS;++repeat) {
        for(const uint8_t *p=fixture->start;p<fixture->end;) {
            size_t count=fixture->end-p;
            if(count>CHUNK_BYTES)count=CHUNK_BYTES;
            esp_audio_simple_dec_raw_t old_raw={.buffer=(uint8_t *)p,.len=count};
            esp_audio_simple_dec_raw_t new_raw=old_raw;
            esp_audio_simple_dec_out_t old_out={.buffer=old_pcm,.len=NATIVE_AAC_PCM_FRAME_BYTES};
            esp_audio_simple_dec_out_t new_out={.buffer=new_pcm_data,.len=NATIVE_AAC_PCM_FRAME_BYTES};
            assert(native_aac_decoder_process(reference,&old_raw,&old_out)==ESP_AUDIO_ERR_OK);
            assert(native_aac_decoder_process(candidate,&new_raw,&new_out)==ESP_AUDIO_ERR_OK);
            check_pcm(old_pcm,&old_out);check_pcm(new_pcm_data,&new_out);
            assert(old_raw.consumed==new_raw.consumed && old_raw.consumed<=count);
            assert(old_out.decoded_size==new_out.decoded_size);
            assert(old_raw.consumed || old_out.decoded_size);
            assert(!memcmp(old_pcm,new_pcm_data,old_out.decoded_size));
            p+=old_raw.consumed;
            if(old_out.decoded_size) {
                check_info(reference,fixture);check_info(candidate,fixture);
                assert(old_out.decoded_size % (sizeof(int16_t)*fixture->channels)==0);
                ++frames;samples+=old_out.decoded_size/sizeof(int16_t);
                for(unsigned i=0;i<old_out.decoded_size;++i)
                    hash=(hash^old_pcm[i])*16777619u;
                vTaskDelay(1);
            }
        }
    }
    assert(frames && samples);
    native_aac_decoder_destroy(reference);native_aac_decoder_destroy(candidate);
    free(old_pcm-GUARD_BYTES);free(new_pcm_data-GUARD_BYTES);
    assert(heap_caps_check_integrity_all(true));
    ESP_LOGI(TAG,"AAC_LATE_SBR_PCM_PASS case=%s repeats=%u frames=%u channel_samples=%" PRIu32
             " max_error_lsb=0 pcm_hash=%08" PRIx32,
             fixture->name,STEADY_REPEATS,frames,samples,hash);
}

static unsigned decode_fixture(native_aac_decoder_t *decoder,uint8_t *pcm,
                               const fixture_t *fixture) {
    unsigned frames=0;
    for(const uint8_t *p=fixture->start;p<fixture->end;) {
        size_t count=fixture->end-p;if(count>CHUNK_BYTES)count=CHUNK_BYTES;
        esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)p,.len=count};
        esp_audio_simple_dec_out_t out={.buffer=pcm,.len=NATIVE_AAC_PCM_FRAME_BYTES};
        assert(native_aac_decoder_process(decoder,&raw,&out)==ESP_AUDIO_ERR_OK);
        check_pcm(pcm,&out);
        assert(raw.consumed<=count && (raw.consumed || out.decoded_size));
        p+=raw.consumed;
        if(out.decoded_size) { check_info(decoder,fixture);++frames;vTaskDelay(1); }
    }
    assert(frames);return frames;
}

void qemu_aac_late_sbr_test(void) {
    for(unsigned i=0;i<sizeof(fixtures)/sizeof(fixtures[0]);++i)compare_ordinary(&fixtures[i]);
    // The mono LC fixture has an odd frame count. Repeating it twice exercises
    // the other LC history bank before the same-header implicit SBR/PS starts.
    for(unsigned repeats=1;repeats<=2;++repeats) {
        native_aac_decoder_t *decoder=native_aac_decoder_create();assert(decoder);
        uint8_t *pcm=new_pcm();unsigned lc_frames=0;
        for(unsigned i=0;i<repeats;++i)lc_frames+=decode_fixture(decoder,pcm,&fixtures[1]);
        assert(lc_frames % 2==repeats % 2);
        unsigned he_frames=decode_fixture(decoder,pcm,&fixtures[5]);
        unsigned back_frames=decode_fixture(decoder,pcm,&fixtures[1]);
        unsigned again_frames=decode_fixture(decoder,pcm,&fixtures[5]);
        native_aac_decoder_destroy(decoder);free(pcm-GUARD_BYTES);
        assert(heap_caps_check_integrity_all(true));
        ESP_LOGI(TAG,"AAC_LATE_SBR_PARITY_PASS lc_frames=%u he_frames=%u rate=44100 channels=2",lc_frames,he_frames);
        ESP_LOGI(TAG,"AAC_LATE_SBR_REVERSE_PASS lc_frames=%u he_frames=%u",back_frames,again_frames);
    }
    ESP_LOGI(TAG,"AAC_LATE_SBR_REGRESSION_PASS ordinary_cases=6 parities=2 transition_pcm_quality=unqualified");
}
