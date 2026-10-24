// Repaired floor1 path only. Independent PCM lives in separate reference files.
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

static void *checked;
typedef struct { uint8_t before[16], data[4096], after[16]; } guarded_t;
static guarded_t pcm;
static unsigned case_index, accepted, rejected, packets_done, pcm_bytes;

static void stop(const char *reason) {
    if(reason) printf("FLOOR1_FAILURE case=%u reason=%s\n",case_index,reason);
    if(checked) { esp_vorbis_dec_close(checked); checked=NULL; }
    printf("FLOOR1_CONTROLLED_STOP\n"); fflush(stdout); esp_restart();
}
static void check(bool ok,const char *reason) { if(!ok) stop(reason); }
static void arm(void) {
    memset(pcm.before,0xa5,16); memset(pcm.data,0xc7,sizeof(pcm.data));
    memset(pcm.after,0x5a,16);
}
static void guard(void) {
    for(unsigned i=0;i<16;i++)
        check(pcm.before[i]==0xa5 && pcm.after[i]==0x5a,"output_canaries");
}
static void decode_task(void *unused) {
    (void)unused;
    check(xPortGetCoreID()==DECODE_CORE,"decoder_core");
    for(case_index=0;case_index<FIXTURE_CASES;case_index++) {
        const floor1_case_t *c=&cases[case_index];
#ifdef FLOOR1_PER_CASE_AUDIO
        const uint8_t *packets=c->packets;
        const uint32_t *offsets=c->offsets;
#else
        const uint8_t *packets=fixture_packets;
        const uint32_t *offsets=fixture_offsets;
#endif
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
        esp_audio_dec_info_t info={0};
        unsigned total=0;
        for(unsigned packet=0;packet<FIXTURE_PACKETS;packet++) {
            uint32_t len=offsets[packet+1]-offsets[packet];
            esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len};
            esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=sizeof(pcm.data)};
            arm();
            int decoded=esp_vorbis_dec_decode(checked,&raw,&out,&info);
            guard();
            check(decoded==ESP_AUDIO_ERR_OK && raw.consumed==len,"packet_result_consumption");
            check(out.decoded_size==fixture_expected_bytes[packet] &&
                  out.decoded_size<=sizeof(pcm.data),"packet_output_size");
            check(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16,"public_metadata");
            printf("FLOOR1_PCM case=%u packet=%u consumed=%" PRIu32 " bytes=%" PRIu32 " hex=",
                case_index,packet,raw.consumed,out.decoded_size);
            for(unsigned i=0;i<out.decoded_size;i++) printf("%02x",pcm.data[i]);
            printf("\n"); total+=out.decoded_size; packets_done++;
            if(!(packet&3)) vTaskDelay(1);
        }
        check(total==FIXTURE_PCM_BYTES,"complete_case_pcm");
        check(esp_vorbis_dec_close(checked)==ESP_AUDIO_ERR_OK,"checked_close");checked=NULL;
        accepted++;pcm_bytes+=total;
        check(heap_caps_check_integrity_all(true),"valid_heap_integrity");
        printf("FLOOR1_ACCEPT case=%u name=%s packets=%u pcm=%u renderer_repair=1 core=%u\n",
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
