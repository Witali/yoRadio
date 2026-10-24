// Public generic raw dispatch only; no decoder-private headers or handle reads.
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

extern esp_audio_err_t __wrap_esp_vorbis_dec_open(void *, uint32_t, void **);
extern esp_audio_err_t __wrap_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *,
    esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);

typedef struct { uint8_t before[16], data[4096], after[16]; } guarded_t;
_Alignas(16) static guarded_t pcm;
static esp_audio_dec_handle_t checked;
static bool checked_owned;
static unsigned case_index, accepted, rejected, packets_done, pcm_bytes;
static unsigned registrations, bindings, closes, unregistrations, metadata, retries;

static bool empty_registry(void) {
    return esp_audio_dec_get_ops(ESP_AUDIO_TYPE_VORBIS)==NULL &&
        esp_audio_dec_check_audio_type(ESP_AUDIO_TYPE_VORBIS)==ESP_AUDIO_ERR_NOT_SUPPORT;
}
static void stop(const char *reason) {
    if(reason) {
        printf("FLOOR1_FAILURE case=%u reason=%s\n",case_index,reason);
        bool closed=checked_owned;
        if(checked_owned) { esp_audio_dec_close(checked); checked=NULL; checked_owned=false; }
        esp_audio_dec_unregister(ESP_AUDIO_TYPE_VORBIS);
        bool empty=esp_audio_dec_get_ops(ESP_AUDIO_TYPE_VORBIS)==NULL;
        bool unsupported=esp_audio_dec_check_audio_type(ESP_AUDIO_TYPE_VORBIS)==ESP_AUDIO_ERR_NOT_SUPPORT;
        printf("VORBIS_REGISTRY_CLEANUP case=%u closed=%u empty=%u unsupported=%u core=%d\n",
            case_index,(unsigned)closed,(unsigned)empty,(unsigned)unsupported,xPortGetCoreID());
    }
    printf("FLOOR1_CONTROLLED_STOP\n"); fflush(stdout); esp_restart();
}
static void check(bool ok,const char *reason) { if(!ok) stop(reason); }
static void arm(void) {
    memset(pcm.before,0xa5,sizeof(pcm.before));
    memset(pcm.data,0xc7,sizeof(pcm.data));
    memset(pcm.after,0x5a,sizeof(pcm.after));
}
static void guard(void) {
    for(unsigned i=0;i<16;i++)
        check(pcm.before[i]==0xa5 && pcm.after[i]==0x5a,"output_canaries");
}
#ifdef VORBIS_RESET_CYCLES
#include "reset_cycles.h"
#endif
static void unregister_case(void) {
    esp_audio_dec_unregister(ESP_AUDIO_TYPE_VORBIS);
    check(empty_registry(),"registry_unregistered");
    unregistrations++;
    printf("VORBIS_REGISTRY_UNREGISTER case=%u empty=1 unsupported=1 core=%d\n",
        case_index,xPortGetCoreID());
}
static void register_case(void) {
    int result=esp_vorbis_dec_register();
    check(result==ESP_AUDIO_ERR_OK,"registry_register");
    const esp_audio_dec_ops_t *ops=esp_audio_dec_get_ops(ESP_AUDIO_TYPE_VORBIS);
    check(ops!=NULL,"registry_ops_present");
    check(esp_audio_dec_check_audio_type(ESP_AUDIO_TYPE_VORBIS)==ESP_AUDIO_ERR_OK,"registry_supported");
    registrations++;
    printf("VORBIS_REGISTRY_REGISTER case=%u result=%d ops=1 supported=1 core=%d\n",
        case_index,result,xPortGetCoreID());
    check(ops->open==__wrap_esp_vorbis_dec_open,"registry_open_binding");
    printf("VORBIS_REGISTRY_BIND_OPEN case=%u match=1 core=%d\n",case_index,xPortGetCoreID());
    check(ops->decode==__wrap_esp_vorbis_dec_decode,"registry_decode_binding");
    printf("VORBIS_REGISTRY_BIND_DECODE case=%u match=1 core=%d\n",case_index,xPortGetCoreID());
    check(ops->reset==esp_vorbis_dec_reset && ops->close==esp_vorbis_dec_close,"registry_other_binding");
    bindings++;
    printf("VORBIS_REGISTRY_BIND_OTHER case=%u reset=1 close=1 core=%d\n",case_index,xPortGetCoreID());
}
static void decode_task(void *unused) {
    (void)unused;
    check(xPortGetCoreID()==DECODE_CORE,"decoder_core");
    printf("VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core=%d\n",xPortGetCoreID());
    esp_audio_dec_unregister(ESP_AUDIO_TYPE_VORBIS);
    check(empty_registry(),"registry_initial_empty");
    printf("VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core=%d\n",xPortGetCoreID());
    check(FIXTURE_CASES==14 && FIXTURE_PACKETS==14 && FIXTURE_PCM_BYTES==28160,"fixture_matrix");
    for(case_index=0;case_index<FIXTURE_CASES;case_index++) {
        const floor1_case_t *c=&cases[case_index];
#ifdef FLOOR1_PER_CASE_AUDIO
        const uint8_t *packets=c->packets;
        const uint32_t *offsets=c->offsets;
#else
        const uint8_t *packets=fixture_packets;
        const uint32_t *offsets=fixture_offsets;
#endif
        register_case();
        esp_vorbis_dec_cfg_t raw_cfg={.info_header=(uint8_t *)fixture_info,
            .info_size=sizeof(fixture_info),.setup_header=(uint8_t *)c->setup,.setup_size=c->setup_size};
        esp_audio_dec_cfg_t cfg={.type=ESP_AUDIO_TYPE_VORBIS,.cfg=&raw_cfg,.cfg_sz=sizeof(raw_cfg)};
        int result=esp_audio_dec_open(&cfg,&checked);
        checked_owned=result==ESP_AUDIO_ERR_OK && checked!=NULL;
        printf("FLOOR1_OPEN case=%u result=%d handle=%u\n",case_index,result,(unsigned)(checked!=NULL));
        if(!c->valid) {
            // FAIL is an observed propagation requirement, never a synthetic label
            // for another generic error. A different result leaves this gate NONPASS.
            check(result==ESP_AUDIO_ERR_FAIL && checked==NULL,"invalid_setup_rejected");
            rejected++;
            check(heap_caps_check_integrity_all(true),"rejected_heap_integrity");
            printf("FLOOR1_REJECT case=%u name=%s result=%d handle=0 core=%d\n",
                case_index,c->name,result,xPortGetCoreID());
            unregister_case();
            continue;
        }
        check(result==ESP_AUDIO_ERR_OK && checked!=NULL,"valid_setup_open");
#ifdef VORBIS_RESET_CYCLES
        reset_initial();
#endif
        unsigned total=0;
        for(unsigned packet=0;packet<FIXTURE_PACKETS;packet++) {
            uint32_t len=offsets[packet+1]-offsets[packet];
            uint32_t expected=fixture_expected_bytes[packet];
            check(expected<=sizeof(pcm.data),"fixture_output_bound");
            if(expected) for(unsigned attempt=0;attempt<3;attempt++) {
                esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len,.consumed=99};
                esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=1,.needed_size=99,.decoded_size=99};
                arm();
                int status=esp_audio_dec_process(checked,&raw,&out);
                guard();
                check(status==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH,"registry_retry_result");
                check(raw.consumed==0 && out.decoded_size==0,"registry_retry_consumption");
                check(out.needed_size==expected,"registry_needed_capacity");
                for(unsigned i=0;i<sizeof(pcm.data);i++) check(pcm.data[i]==0xc7,"registry_retry_output_untouched");
                retries++;
                printf("VORBIS_REGISTRY_RETRY case=%u packet=%u attempt=%u result=%d consumed=0 decoded=0 needed=%" PRIu32 " untouched=1 canaries=1 core=%d\n",
                    case_index,packet,attempt,status,out.needed_size,xPortGetCoreID());
            }
            esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)packets+offsets[packet],.len=len};
            esp_audio_dec_out_frame_t out={.buffer=pcm.data,.len=sizeof(pcm.data)};
            arm();
            int status=esp_audio_dec_process(checked,&raw,&out);
            guard();
            check(status==ESP_AUDIO_ERR_OK && raw.consumed==len,"packet_result_consumption");
            check(out.decoded_size==expected,"packet_output_size");
            esp_audio_dec_info_t info={0};
            int info_status=esp_audio_dec_get_info(checked,&info);
            bool correct=info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16;
            check((info_status==ESP_AUDIO_ERR_OK && correct) ||
                (!expected && info_status==ESP_AUDIO_ERR_NOT_FOUND),"public_metadata");
            metadata++;
            printf("VORBIS_REGISTRY_META case=%u packet=%u result=%d sample_rate=%" PRIu32 " channel=%u bits=%u core=%d\n",
                case_index,packet,info_status,info.sample_rate,(unsigned)info.channel,
                (unsigned)info.bits_per_sample,xPortGetCoreID());
            printf("FLOOR1_PCM case=%u packet=%u consumed=%" PRIu32 " bytes=%" PRIu32 " hex=",
                case_index,packet,raw.consumed,out.decoded_size);
            for(unsigned i=0;i<out.decoded_size;i++) printf("%02x",pcm.data[i]);
            printf("\n"); total+=out.decoded_size; packets_done++;
#ifdef VORBIS_RESET_CYCLES
            reset_capture(packet,pcm.data,out.decoded_size);
#endif
            if(!(packet&3)) vTaskDelay(1);
        }
        check(total==FIXTURE_PCM_BYTES,"complete_case_pcm");
#ifdef VORBIS_RESET_CYCLES
        reset_exercise(c,packets,offsets);
#endif
        esp_audio_dec_close(checked); checked=NULL; checked_owned=false; closes++;
        printf("VORBIS_REGISTRY_CLOSE case=%u called=1 core=%d\n",case_index,xPortGetCoreID());
        unregister_case();
        accepted++;pcm_bytes+=total;
        check(heap_caps_check_integrity_all(true),"valid_heap_integrity");
        printf("FLOOR1_ACCEPT case=%u name=%s packets=14 pcm=28160 renderer_repair=1 core=%d\n",
            case_index,c->name,xPortGetCoreID());
    }
    check(accepted==8 && rejected==6 && registrations==14 && bindings==14 && closes==8 &&
        unregistrations==14 && metadata==112 && retries==312,"complete_registry_matrix");
#ifdef VORBIS_RESET_CYCLES
    reset_summary();
#endif
    printf("VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core=%d\n",xPortGetCoreID());
    printf("FLOOR1_COMPLETE accepted=%u rejected=%u packets=%u pcm=%u core=%d\n",
        accepted,rejected,packets_done,pcm_bytes,xPortGetCoreID());
    stop(NULL);
}
void app_main(void) {
    check(xPortGetCoreID()==0,"coordinator_core0");
    printf("FLOOR1_START coordinator=0 decoder=%u\n",DECODE_CORE);
    check(xTaskCreatePinnedToCore(decode_task,"vorbis_registered",16384,NULL,3,NULL,DECODE_CORE)==pdPASS,"create_decoder_task");
}
