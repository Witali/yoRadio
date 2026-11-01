/* Public Ogg versus persistent elementary Opus handles. All original return
 * values and PCM survive; no private state, repaired statuses or codec math.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "psa/crypto.h"
#include "decoder_registration.h"
#include "ogg_playback.h" /* Public pending-input ownership types; wrapper not selected. */
#include "esp_opus_dec.h"
#ifdef NDEBUG
#error Diagnostic assertions are required
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error Classic ESP32/LX6 only
#endif
extern const uint8_t body_start[] asm("_binary_control_bin_start");
extern const uint8_t body_end[] asm("_binary_control_bin_end");
typedef struct {uint32_t magic,version,count,entry_size;} header_t;
typedef struct {uint32_t ogg_offset,ogg_bytes,aggregate_offset,aggregate_bytes,elementary_offset,elementary_bytes,
    channels,raw_frames,frame_samples,packet_samples;} entry_t;
_Static_assert(sizeof(header_t)==16 && sizeof(entry_t)==40,"encoded input table ABI");
typedef struct {
    unsigned id,fixture,mode,calls,opens,closes,resizes,packets,outputs;
    uint64_t consumed,pcm_bytes;
    uint32_t rate;unsigned channels,bits;
    int open_status,last_status;
    psa_hash_operation_t hash;
} context_t;
static context_t *active;
static unsigned cases;
static uint32_t le32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void capture(const uint8_t *pcm,size_t bytes) {
    assert(active && bytes && !(bytes%((unsigned)active->channels*2)));
    assert(psa_hash_update(&active->hash,pcm,bytes)==PSA_SUCCESS);
    for(size_t at=0;at<bytes;at+=128) {
        size_t n=bytes-at;if(n>128)n=128;char hex[257];
        for(size_t i=0;i<n;++i)snprintf(hex+2*i,3,"%02x",pcm[at+i]);
        printf("FC_PCM id=%u offset=%" PRIu64 " bytes=%u hex=%s\n",active->id,active->pcm_bytes+at,(unsigned)n,hex);
    }
    active->pcm_bytes+=bytes;++active->outputs;
}
static void observed(int packet,uint32_t length,uint32_t consumed,uint32_t capacity,uint32_t needed,uint32_t decoded,int result) {
    context_t *c=active;++c->calls;c->consumed+=consumed;c->last_status=result;
    if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)++c->resizes;
    printf("FC_CALL id=%u packet=%d call=%u len=%" PRIu32 " consumed=%" PRIu32 " capacity=%" PRIu32
        " needed=%" PRIu32 " decoded=%" PRIu32 " result=%d\n",c->id,packet,c->calls,length,consumed,capacity,needed,decoded,result);
    assert(consumed<=length && decoded<=capacity && c->calls<10000);
    if(!(c->calls&7u))vTaskDelay(1);
}
esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *,esp_audio_simple_dec_handle_t *);
esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_raw_t *,esp_audio_simple_dec_out_t *);
void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);
esp_audio_err_t __wrap_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,esp_audio_simple_dec_handle_t *handle) {
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(cfg,handle);active->open_status=result;
    if(result==ESP_AUDIO_ERR_OK){assert(*handle);++active->opens;}
    printf("FC_OPEN id=%u result=%d handle=%u api=ogg rate=na channels=na duration=na self_delimited=na\n",active->id,result,(unsigned)(*handle!=NULL));return result;
}
esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame) {
    uint32_t length=raw->len,capacity=frame->len;esp_audio_err_t result=__real_esp_audio_simple_dec_process(handle,raw,frame);
    assert(raw->len==length);observed(-1,length,raw->consumed,capacity,frame->needed_size,frame->decoded_size,result);
    if(frame->decoded_size) {
        esp_audio_simple_dec_info_t info={0};assert(esp_audio_simple_dec_get_info(handle,&info)==ESP_AUDIO_ERR_OK);
        active->rate=info.sample_rate;active->channels=info.channel;active->bits=info.bits_per_sample;
        assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16);capture(frame->buffer,frame->decoded_size);
    }
    return result;
}
void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle) {
    __real_esp_audio_simple_dec_close(handle);++active->closes;printf("FC_CLOSE id=%u result=void\n",active->id);
}
static int resize(uint8_t **pcm,size_t *capacity,uint32_t needed) {
    assert(needed>*capacity && needed<=131072);uint8_t *larger=realloc(*pcm,needed);if(!larger)return ESP_AUDIO_ERR_MEM_LACK;
    *pcm=larger;*capacity=needed;return ESP_AUDIO_ERR_OK;
}
static int stock(const uint8_t *body,uint32_t bytes,uint8_t **pcm,size_t *capacity) {
    esp_audio_simple_dec_cfg_t cfg={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};esp_audio_simple_dec_handle_t decoder=NULL;
    int status=esp_audio_simple_dec_open(&cfg,&decoder);if(status!=ESP_AUDIO_ERR_OK)return status;
    esp_audio_simple_dec_raw_t raw={.buffer=(uint8_t *)body,.len=bytes,.eos=true};
    for(;;) {
        esp_audio_simple_dec_out_t frame={.buffer=*pcm,.len=(uint32_t)*capacity};raw.consumed=0;
        status=esp_audio_simple_dec_process(decoder,&raw,&frame);raw.buffer+=raw.consumed;raw.len-=raw.consumed;
        if(status==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH){assert(!frame.decoded_size);status=resize(pcm,capacity,frame.needed_size);if(!status)continue;}
        if(status!=ESP_AUDIO_ERR_OK)break;
        if(!raw.consumed && !frame.decoded_size){if(raw.len)status=ESP_AUDIO_ERR_DATA_LACK;break;}
    }
    esp_audio_simple_dec_close(decoder);return status;
}
static int raw_control(const uint8_t *body,size_t bytes,unsigned mode,uint8_t **pcm,size_t *capacity) {
    assert(bytes>=28 && !memcmp(body,"OPMODE1\0",8));unsigned channels=le32(body+8),count=le32(body+20);assert(channels==2 && count && count<=192);
    unsigned packet_samples=le32(body+24);assert(packet_samples==120 || packet_samples==5760);
    esp_opus_dec_cfg_t cfg={.sample_rate=48000,.channel=2,.self_delimited=false,
        .frame_duration=mode==1 || mode==2?(packet_samples==5760?ESP_OPUS_DEC_FRAME_DURATION_120_MS:ESP_OPUS_DEC_FRAME_DURATION_2_5_MS):
            mode==4?ESP_OPUS_DEC_FRAME_DURATION_2_5_MS:ESP_OPUS_DEC_FRAME_DURATION_INVALID};
    void *decoder=NULL;int status=esp_opus_dec_open(&cfg,sizeof(cfg),&decoder);active->open_status=status;
    if(status==ESP_AUDIO_ERR_OK){assert(decoder);++active->opens;}
    printf("FC_OPEN id=%u result=%d handle=%u api=raw rate=%" PRIu32 " channels=%u duration=%d self_delimited=%u\n",
        active->id,status,(unsigned)(decoder!=NULL),cfg.sample_rate,(unsigned)cfg.channel,(int)cfg.frame_duration,(unsigned)cfg.self_delimited);
    if(status!=ESP_AUDIO_ERR_OK)return status;
    size_t at=28;
    for(unsigned packet=0;packet<count && status==ESP_AUDIO_ERR_OK;++packet) {
        assert(at+4<=bytes);uint32_t length=le32(body+at);at+=4;assert(length && at+length<=bytes);
        esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)body+at,.len=length,.frame_recover=ESP_AUDIO_DEC_RECOVERY_NONE};
        for(;;) {
            esp_audio_dec_out_frame_t frame={.buffer=*pcm,.len=(uint32_t)*capacity};esp_audio_dec_info_t info={0};
            uint32_t offered=raw.len;raw.consumed=0;status=esp_opus_dec_decode(decoder,&raw,&frame,&info);
            assert(raw.len==offered);observed(packet,offered,raw.consumed,(uint32_t)*capacity,frame.needed_size,frame.decoded_size,status);
            if(frame.decoded_size){active->rate=info.sample_rate;active->channels=info.channel;active->bits=info.bits_per_sample;
                assert(info.sample_rate==48000 && info.channel==2 && info.bits_per_sample==16);capture(frame.buffer,frame.decoded_size);}
            raw.buffer+=raw.consumed;raw.len-=raw.consumed;
            if(status==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH){assert(!frame.decoded_size);status=resize(pcm,capacity,frame.needed_size);if(!status)continue;}
            if(status!=ESP_AUDIO_ERR_OK || !raw.len)break;
            if(!raw.consumed && !frame.decoded_size){status=ESP_AUDIO_ERR_DATA_LACK;break;}
        }
        at+=length;++active->packets;
    }
    int closed=esp_opus_dec_close(decoder);++active->closes;printf("FC_CLOSE id=%u result=%d\n",active->id,closed);
    if(status==ESP_AUDIO_ERR_OK){assert(at==bytes);if(closed!=ESP_AUDIO_ERR_OK)status=closed;}
    return status;
}
static void run(unsigned fixture,const entry_t *e,unsigned mode) {
    context_t c={.id=cases,.fixture=fixture,.mode=mode};active=&c;c.hash=psa_hash_operation_init();assert(psa_hash_setup(&c.hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
    size_t before=esp_get_free_heap_size(),capacity=mode==2?12288:23040;uint8_t *pcm=malloc(capacity);assert(pcm);
    size_t initial=capacity;bool elementary=mode>=4;const uint8_t *input=body_start+(elementary?e->elementary_offset:e->aggregate_offset);
    size_t bytes=elementary?e->elementary_bytes:e->aggregate_bytes;int status;
    if(!mode){input=body_start+e->ogg_offset;bytes=e->ogg_bytes;status=stock(input,(uint32_t)bytes,&pcm,&capacity);}
    else status=raw_control(input,bytes,mode,&pcm,&capacity);
    free(pcm);assert(c.opens==c.closes && heap_caps_check_integrity_all(true));uint8_t digest[32];size_t digest_size=0;
    assert(psa_hash_finish(&c.hash,digest,32,&digest_size)==PSA_SUCCESS && digest_size==32 && psa_hash_abort(&c.hash)==PSA_SUCCESS);
    char hex[65];for(unsigned i=0;i<32;++i)snprintf(hex+2*i,3,"%02x",digest[i]);
    printf("FC_CASE id=%u fixture=%u mode=%u status=%d open_status=%d last_status=%d input_bytes=%u consumed=%" PRIu64
        " packets=%u calls=%u opens=%u closes=%u resizes=%u initial_capacity=%u capacity=%u outputs=%u pcm_bytes=%" PRIu64
        " sha=%s rate=%" PRIu32 " channels=%u bits=%u before=%u after=%u heap_min=%u stack_free=%u core=%d priority=%u\n",
        c.id,fixture,mode,status,c.open_status,c.last_status,(unsigned)bytes,c.consumed,c.packets,c.calls,c.opens,c.closes,c.resizes,
        (unsigned)initial,(unsigned)capacity,c.outputs,c.pcm_bytes,hex,c.rate,c.channels,c.bits,(unsigned)before,(unsigned)esp_get_free_heap_size(),
        (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    fflush(stdout);active=NULL;++cases;vTaskDelay(1);
}
static void worker(void *unused) {
    (void)unused;assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3 && psa_crypto_init()==PSA_SUCCESS);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);const header_t *head=(const header_t *)body_start;
    assert(head->magic==UINT32_C(0x46434f50) && head->version==1 && head->count==4 && head->entry_size==40);
    const entry_t *entries=(const entry_t *)(head+1);size_t extent=(size_t)(body_end-body_start);
    for(unsigned i=0;i<4;++i){const entry_t *e=entries+i;assert(e->channels==2 && e->frame_samples==120 && e->raw_frames>0);
        assert(e->ogg_offset>=176 && e->ogg_offset<=extent && e->ogg_bytes<=extent-e->ogg_offset &&
            e->aggregate_offset>=176 && e->aggregate_offset<=extent && e->aggregate_bytes<=extent-e->aggregate_offset &&
            e->elementary_offset>=176 && e->elementary_offset<=extent && e->elementary_bytes<=extent-e->elementary_offset);
        for(unsigned mode=0;mode<6;++mode)run(i,e,mode);}
    decoder_unregister_codecs();assert(cases==24 && heap_caps_check_integrity_all(true));
    printf("FC_COMPLETE cases=%u heap_free=%u heap_min=%u stack_free=%u core=1 priority=3 heap_integrity=1\n",cases,
        (unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));fflush(stdout);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);printf("FC_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 fixtures=4 cases=24\n");fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"opus-frame-control",16384,NULL,3,NULL,1)==pdPASS);while(true)vTaskDelay(portMAX_DELAY);
}
