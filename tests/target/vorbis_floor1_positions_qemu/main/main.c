// Standalone public raw API regression. Never synthesize a malformed setup.
#include <stdbool.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "esp_vorbis_dec.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "fixture.h"

#if CONFIG_IDF_TARGET_ESP32
#define DECODE_CORE 1
#else
#define DECODE_CORE 0
#endif

extern esp_audio_err_t __real_esp_vorbis_dec_open(void *, uint32_t, void **);
extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);
static void *original, *checked;
typedef struct { uint8_t before[16], data[4096], after[16]; } guarded_t;
static guarded_t original_pcm, checked_pcm;
static unsigned case_index, accepted, rejected, packets_done, pcm_bytes;

static void close_handles(void) {
    if(original) { esp_vorbis_dec_close(original); original=NULL; }
    if(checked) { esp_vorbis_dec_close(checked); checked=NULL; }
}
static void stop(const char *reason) {
    if(reason) printf("FLOOR1_FAILURE case=%u reason=%s\n",case_index,reason);
    close_handles();
    printf("FLOOR1_CONTROLLED_STOP\n"); fflush(stdout); esp_restart();
}
static void check(bool ok,const char *reason) { if(!ok) stop(reason); }
static void arm(guarded_t *pcm) {
    memset(pcm->before,0xa5,16); memset(pcm->data,0xc7,sizeof(pcm->data));
    memset(pcm->after,0x5a,16);
}
static void guard(const guarded_t *pcm) {
    for(unsigned i=0;i<16;i++)
        check(pcm->before[i]==0xa5 && pcm->after[i]==0x5a,"output_canaries");
}
static void decode_task(void *unused) {
    (void)unused;
    check(xPortGetCoreID()==DECODE_CORE,"decoder_core");
    for(case_index=0;case_index<FIXTURE_CASES;case_index++) {
        const floor1_case_t *c=&cases[case_index];
        esp_vorbis_dec_cfg_t cfg={.info_header=(uint8_t *)fixture_info,
            .info_size=sizeof(fixture_info),.setup_header=(uint8_t *)c->setup,.setup_size=c->setup_size};
        int result=esp_vorbis_dec_open(&cfg,sizeof(cfg),&checked);
        printf("FLOOR1_OPEN case=%u result=%d handle=%u\n",case_index,result,checked!=NULL);
        if(!c->valid) {
            check(result==ESP_AUDIO_ERR_FAIL && !checked,"invalid_setup_rejected");
            rejected++;
            check(heap_caps_check_integrity_all(true),"rejected_heap_integrity");
            printf("FLOOR1_REJECT case=%u name=%s result=%d handle=0 core=%u\n",case_index,c->name,result,DECODE_CORE);
            continue;
        }
        check(result==ESP_AUDIO_ERR_OK && checked,"valid_setup_open");
        check(__real_esp_vorbis_dec_open(&cfg,sizeof(cfg),&original)==ESP_AUDIO_ERR_OK && original,
              "original_valid_setup_open");
        esp_audio_dec_info_t a_info={0}, b_info={0};
        unsigned total=0;
        for(unsigned packet=0;packet<FIXTURE_PACKETS;packet++) {
            uint32_t len=fixture_offsets[packet+1]-fixture_offsets[packet];
            esp_audio_dec_in_raw_t a={.buffer=(uint8_t *)fixture_packets+fixture_offsets[packet],.len=len},b=a;
            esp_audio_dec_out_frame_t ao={.buffer=original_pcm.data,.len=sizeof(original_pcm.data)},
                bo={.buffer=checked_pcm.data,.len=sizeof(checked_pcm.data)};
            arm(&original_pcm);arm(&checked_pcm);
            int ar=__real_esp_vorbis_dec_decode(original,&a,&ao,&a_info);
            int br=esp_vorbis_dec_decode(checked,&b,&bo,&b_info);
            guard(&original_pcm);guard(&checked_pcm);
            check(ar==ESP_AUDIO_ERR_OK && br==ar && a.consumed==len && b.consumed==len,"packet_result_consumption");
            check(ao.decoded_size==fixture_expected_bytes[packet] && bo.decoded_size==ao.decoded_size &&
                  bo.decoded_size<=sizeof(checked_pcm.data),"packet_output_size");
            check(!memcmp(original_pcm.data,checked_pcm.data,bo.decoded_size),"original_exact_pcm");
            check(a_info.sample_rate==48000 && b_info.sample_rate==48000 &&
                  a_info.channel==2 && b_info.channel==2 &&
                  a_info.bits_per_sample==16 && b_info.bits_per_sample==16,"public_metadata");
            printf("FLOOR1_PCM case=%u packet=%u consumed=%" PRIu32 " bytes=%" PRIu32 " hex=",
                case_index,packet,b.consumed,bo.decoded_size);
            for(unsigned i=0;i<bo.decoded_size;i++) printf("%02x",checked_pcm.data[i]);
            printf("\n"); total+=bo.decoded_size; packets_done++;
            if(!(packet&3)) vTaskDelay(1);
        }
        check(total==FIXTURE_PCM_BYTES,"complete_case_pcm");
        close_handles();accepted++;pcm_bytes+=total;
        check(heap_caps_check_integrity_all(true),"valid_heap_integrity");
        printf("FLOOR1_ACCEPT case=%u name=%s packets=%u pcm=%u original_exact=1 core=%u\n",
            case_index,c->name,FIXTURE_PACKETS,total,DECODE_CORE);
    }
    check(accepted==8 && rejected==6,"complete_case_matrix");
    printf("FLOOR1_COMPLETE accepted=%u rejected=%u packets=%u pcm=%u core=%u\n",
        accepted,rejected,packets_done,pcm_bytes,DECODE_CORE);
    stop(NULL);
}
void app_main(void) {
    check(xPortGetCoreID()==0,"coordinator_core0");
    printf("FLOOR1_START coordinator=0 decoder=%u\n",DECODE_CORE);
    check(xTaskCreatePinnedToCore(decode_task,"floor1_raw",16384,NULL,3,NULL,DECODE_CORE)==pdPASS,"create_decoder_task");
}
