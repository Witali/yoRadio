/* Observe stock public vendor output first, then the unchanged current wrapper.
 * Public call observers forward exact arguments/results. No private layouts,
 * replacement statuses, decoder hooks or application source modifications.
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
#include "ogg_playback.h"
#ifdef NDEBUG
#error "Diagnostic assertions are required"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "Classic ESP32/LX6 only"
#endif
extern const uint8_t fixture_start[] asm("_binary_modes_bin_start");
extern const uint8_t fixture_end[] asm("_binary_modes_bin_end");
typedef struct {uint32_t magic,version,count,entry_size;} header_t;
typedef struct {uint32_t channels,offset,bytes,raw_frames,logical_frames,pre_skip,mode_id,case_id;} entry_t;
_Static_assert(sizeof(header_t)==16 && sizeof(entry_t)==32,"transport ABI");
typedef struct {
    unsigned id,fixture,encoded_channels,mode,chunk,calls,opens,closes,resizes,data_eos,empty_eos,frames,outputs;
    uint64_t consumed,raw_bytes,output_bytes;
    esp_audio_simple_dec_info_t info;
    psa_hash_operation_t raw_hash,output_hash;
    int process_status,open_status;
} context_t;
static context_t *active;
static unsigned cases;
static void hex_pcm(const char *kind,const uint8_t *pcm,size_t size,uint64_t start) {
    for(size_t at=0;at<size;at+=128) {
        size_t n=size-at;if(n>128)n=128;char text[257];
        for(size_t i=0;i<n;++i)snprintf(text+2*i,3,"%02x",pcm[at+i]);
        printf("PM_PCM id=%u kind=%s offset=%" PRIu64 " bytes=%u hex=%s\n",active->id,kind,start+at,(unsigned)n,text);
    }
}
static void begin_hash(psa_hash_operation_t *hash) {
    *hash=psa_hash_operation_init();assert(psa_hash_setup(hash,PSA_ALG_SHA_256)==PSA_SUCCESS);
}
static void end_hash(psa_hash_operation_t *hash,char hex[65]) {
    uint8_t digest[32];size_t n=0;assert(psa_hash_finish(hash,digest,sizeof(digest),&n)==PSA_SUCCESS && n==32);
    assert(psa_hash_abort(hash)==PSA_SUCCESS);for(unsigned i=0;i<32;++i)snprintf(hex+2*i,3,"%02x",digest[i]);
}
esp_audio_err_t __real_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *,esp_audio_simple_dec_handle_t *);
esp_audio_err_t __real_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t,esp_audio_simple_dec_raw_t *,esp_audio_simple_dec_out_t *);
void __real_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t);
esp_audio_err_t __wrap_esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *cfg,esp_audio_simple_dec_handle_t *handle) {
    assert(active && cfg->dec_type==ESP_AUDIO_SIMPLE_DEC_TYPE_OGG && !cfg->dec_cfg && !cfg->cfg_size && !cfg->use_frame_dec);
    esp_audio_err_t result=__real_esp_audio_simple_dec_open(cfg,handle);active->open_status=result;
    if(result==ESP_AUDIO_ERR_OK){assert(*handle);++active->opens;}
    printf("PM_OPEN id=%u result=%d handle=%u\n",active->id,(int)result,(unsigned)(*handle!=NULL));return result;
}
esp_audio_err_t __wrap_esp_audio_simple_dec_process(esp_audio_simple_dec_handle_t handle,
    esp_audio_simple_dec_raw_t *raw,esp_audio_simple_dec_out_t *frame) {
    context_t *c=active;assert(c && handle && c->opens==1 && !c->closes);
    uint32_t length=raw->len,capacity=frame->len;
    esp_audio_err_t result=__real_esp_audio_simple_dec_process(handle,raw,frame);
    assert(raw->len==length && raw->consumed<=length && frame->decoded_size<=capacity);
    ++c->calls;c->consumed+=raw->consumed;c->process_status=result;
    if(raw->eos){if(length)++c->data_eos;else ++c->empty_eos;}
    if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH)++c->resizes;
    printf("PM_CALL id=%u call=%u len=%" PRIu32 " consumed=%" PRIu32 " capacity=%" PRIu32
        " needed=%" PRIu32 " decoded=%" PRIu32 " eos=%u result=%d\n",c->id,c->calls,length,raw->consumed,capacity,
        frame->needed_size,frame->decoded_size,(unsigned)raw->eos,(int)result);
    if(frame->decoded_size) {
        esp_audio_err_t info_status=esp_audio_simple_dec_get_info(handle,&c->info);
        printf("PM_INFO id=%u result=%d rate=%" PRIu32 " channels=%u bits=%u\n",c->id,(int)info_status,
            c->info.sample_rate,(unsigned)c->info.channel,(unsigned)c->info.bits_per_sample);
        assert(info_status==ESP_AUDIO_ERR_OK && c->info.channel && c->info.bits_per_sample==16 &&
            c->info.sample_rate==48000 && frame->decoded_size%((unsigned)c->info.channel*2)==0);
        assert(psa_hash_update(&c->raw_hash,frame->buffer,frame->decoded_size)==PSA_SUCCESS);
        hex_pcm("raw",frame->buffer,frame->decoded_size,c->raw_bytes);c->raw_bytes+=frame->decoded_size;++c->frames;
    }
    if(!(c->calls&7u))vTaskDelay(1);
    assert(c->calls<10000);return result;
}
void __wrap_esp_audio_simple_dec_close(esp_audio_simple_dec_handle_t handle) {
    assert(active && handle && active->opens==1 && !active->closes);__real_esp_audio_simple_dec_close(handle);++active->closes;
    printf("PM_CLOSE id=%u\n",active->id);
}
static bool cancelled(void *opaque){assert(opaque==active);return false;}
static bool output(void *opaque,const esp_audio_simple_dec_info_t *info,const uint8_t *pcm,size_t bytes,int16_t header_gain_q8) {
    context_t *c=opaque;assert(c==active && info->sample_rate==48000 && info->channel && info->bits_per_sample==16);
    assert(header_gain_q8==0); /* Complete packet-mode inputs carry exact zero header gain. */
    assert(bytes && bytes%((unsigned)info->channel*2)==0 && psa_hash_update(&c->output_hash,pcm,bytes)==PSA_SUCCESS);
    hex_pcm("output",pcm,bytes,c->output_bytes);c->output_bytes+=bytes;++c->outputs;return true;
}
static void yield(void *opaque){assert(opaque==active);vTaskDelay(1);}
static int direct_feed(esp_audio_simple_dec_handle_t decoder,decoder_pending_input_t *pending,
    uint8_t **pcm,size_t *capacity,const uint8_t *data,uint32_t bytes,bool eos,bool *drained) {
    esp_audio_simple_dec_raw_t raw={.eos=eos};bool owned=false;
    decoder_pending_input_status_t prepared=decoder_pending_input_prepare(pending,(uint8_t *)data,bytes,&raw.buffer,&raw.len,&owned);
    if(prepared!=DECODER_PENDING_INPUT_OK)return prepared==DECODER_PENDING_INPUT_NO_MEMORY?ESP_AUDIO_ERR_MEM_LACK:ESP_AUDIO_ERR_INVALID_PARAMETER;
    for(;;) {
        esp_audio_simple_dec_out_t frame={.buffer=*pcm,.len=(uint32_t)*capacity};raw.consumed=0;
        esp_audio_err_t result=esp_audio_simple_dec_process(decoder,&raw,&frame);
        raw.buffer+=raw.consumed;raw.len-=raw.consumed;
        if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
            assert(!frame.decoded_size && frame.needed_size>*capacity && frame.needed_size<=131072);
            uint8_t *larger=realloc(*pcm,frame.needed_size);if(!larger)return ESP_AUDIO_ERR_MEM_LACK;
            *pcm=larger;*capacity=frame.needed_size;continue;
        }
        if(result!=ESP_AUDIO_ERR_OK)return result;
        if(!raw.consumed && !frame.decoded_size) {
            if(eos){if(raw.len)return ESP_AUDIO_ERR_DATA_LACK;*drained=true;}
            else if(raw.len) {
                prepared=decoder_pending_input_retain(pending,raw.buffer,raw.len,owned);
                if(prepared!=DECODER_PENDING_INPUT_OK)return prepared==DECODER_PENDING_INPUT_NO_MEMORY?ESP_AUDIO_ERR_MEM_LACK:ESP_AUDIO_ERR_INVALID_PARAMETER;
            }
            break;
        }
        if(!eos && !raw.len)break;
    }
    return ESP_AUDIO_ERR_OK;
}
static void run_case(unsigned id,const entry_t *entry,unsigned mode,unsigned chunk) {
    context_t c={.id=id,.fixture=entry->case_id,.encoded_channels=entry->channels,.mode=mode,.chunk=chunk};active=&c;
    begin_hash(&c.raw_hash);begin_hash(&c.output_hash);size_t before=esp_get_free_heap_size(),capacity=12288;
    uint8_t *pcm=malloc(capacity);assert(pcm);decoder_pending_input_t pending={0};esp_audio_simple_dec_handle_t decoder=NULL;
    ogg_playback playback={0};bool drained=false;int status=0;int32_t cause=0;size_t offered=0;
    const uint8_t *body=fixture_start+entry->offset;
    if(mode)ogp_reset(&playback,19);
    else {esp_audio_simple_dec_cfg_t config={.dec_type=ESP_AUDIO_SIMPLE_DEC_TYPE_OGG};status=esp_audio_simple_dec_open(&config,&decoder);cause=status;}
    while(status==0 && offered<entry->bytes) {
        size_t n=entry->bytes-offered;if(chunk && n>chunk)n=chunk;
        bool eos=offered+n==entry->bytes;
        if(mode) {
            ogg_playback_callbacks callbacks={.cancelled=cancelled,.output=output,.yield=yield,.context=&c};
            status=ogp_feed(&playback,body+offered,n,eos,&decoder,&pcm,&capacity,&pending,&callbacks,&cause);
            drained=status==OGP_OK && eos && !decoder && !ogp_has_input(&playback) && !pending.size;
        } else {status=direct_feed(decoder,&pending,&pcm,&capacity,body+offered,(uint32_t)n,eos,&drained);cause=status;}
        offered+=n;
    }
    if(decoder)esp_audio_simple_dec_close(decoder);
    decoder_pending_input_clear(&pending);free(pcm);
    if(mode)ogp_reset(&playback,20);
    assert(c.opens==c.closes && heap_caps_check_integrity_all(true));char raw_sha[65],output_sha[65];end_hash(&c.raw_hash,raw_sha);end_hash(&c.output_hash,output_sha);
    size_t after=esp_get_free_heap_size();
    printf("PM_CASE id=%u fixture=%u encoded_channels=%u mode=%u chunk=%u fixture_bytes=%u offered=%u consumed=%" PRIu64
        " status=%d cause=%" PRId32 " open_status=%d process_status=%d calls=%u opens=%u closes=%u resizes=%u drained=%u"
        " frames=%u raw_bytes=%" PRIu64 " raw_sha=%s output_bytes=%" PRIu64 " output_sha=%s outputs=%u rate=%" PRIu32
        " channels=%u bits=%u data_eos=%u empty_eos=%u capacity=%u before=%u after=%u heap_min=%u stack_free=%u core=%d priority=%u\n",
        id,(unsigned)entry->case_id,(unsigned)entry->channels,mode,chunk,(unsigned)entry->bytes,(unsigned)offered,c.consumed,status,cause,c.open_status,c.process_status,
        c.calls,c.opens,c.closes,c.resizes,(unsigned)drained,c.frames,c.raw_bytes,raw_sha,c.output_bytes,output_sha,c.outputs,c.info.sample_rate,
        (unsigned)c.info.channel,(unsigned)c.info.bits_per_sample,c.data_eos,c.empty_eos,(unsigned)capacity,(unsigned)before,(unsigned)after,
        (unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout)==0);active=NULL;++cases;vTaskDelay(1);
}
static void worker(void *unused) {
    (void)unused;assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3 && psa_crypto_init()==PSA_SUCCESS);
    assert(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    size_t before=esp_get_free_heap_size();assert(decoder_register_codecs()==ESP_AUDIO_ERR_OK);
    const header_t *head=(const header_t *)fixture_start;assert(head->magic==UINT32_C(0x504d4f47) && head->version==1 && head->count==49 && head->entry_size==32);
    const entry_t *entries=(const entry_t *)(head+1);
    for(unsigned i=0;i<49;++i) {
        const entry_t *e=entries+i;
        assert((e->channels==1 || e->channels==2) && e->raw_frames>e->pre_skip &&
            e->logical_frames==e->raw_frames-e->pre_skip-13 && e->mode_id<=2 && e->case_id==i &&
            e->offset>=1584 && e->offset<(size_t)(fixture_end-fixture_start) &&
            e->bytes<=(size_t)(fixture_end-fixture_start)-e->offset && !memcmp(fixture_start+e->offset,"OggS",4));
        for(unsigned mode=0;mode<2;++mode)for(unsigned split=0;split<2;++split)run_case(cases,e,mode,split?257:0);
    }
    decoder_unregister_codecs();assert(cases==196 && heap_caps_check_integrity_all(true));size_t after=esp_get_free_heap_size();
    printf("PM_COMPLETE cases=%u registry_before=%u heap_free=%u retained=%d heap_min=%u stack_free=%u core=1 priority=3 heap_integrity=1\n",
        cases,(unsigned)before,(unsigned)after,(int)before-(int)after,(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));
    assert(fflush(stdout)==0);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);printf("PM_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=49\n");fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"packet_modes",16384,NULL,3,NULL,1)==pdPASS);while(true)vTaskDelay(portMAX_DELAY);
}
