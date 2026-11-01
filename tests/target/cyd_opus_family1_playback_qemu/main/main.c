/* Standalone RTOS qualification only; not the complete production audio task. */
#include "probe.h"
#include "opus_family1_playback.h"
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
#ifdef NDEBUG
#error "Native qualification requires real assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "Classic ESP32/LX6 only"
#endif
af_observation af_obs;
static opus_family1_playback *active_adapter;
static ogg_page_input *active_input;
static unsigned fixture_refs,adapter_cases;
unsigned af_live(void){unsigned n=0;for(unsigned i=0;i<8;++i)n+=af_obs.handles[i]!=NULL;return n;}
void af_begin(unsigned kind,unsigned id,unsigned schedule) {
    assert(!af_live());memset(&af_obs,0,sizeof(af_obs));af_obs.kind=kind;af_obs.id=id;af_obs.schedule=schedule;
}
static unsigned slot_for(void *handle) {for(unsigned i=0;i<8;++i)if(af_obs.handles[i]==handle)return i;assert(false);return 0;}
esp_audio_err_t af_open(void *opaque,uint32_t bytes,void **out) {
    const esp_opus_dec_cfg_t *cfg=opaque;unsigned slot=af_obs.opens,stream=slot;
    if(af_obs.kind) {
        assert(active_adapter);for(slot=0;slot<8 && cfg!=&active_adapter->decoder.cfg[slot];++slot){}assert(slot<8);stream=active_adapter->decoder.plan.stream_id[slot];
    }
    assert(slot<8 && !af_obs.handles[slot]);size_t before=esp_get_free_heap_size();esp_audio_err_t result=esp_opus_dec_open(opaque,bytes,out);++af_obs.opens;
    if(*out){af_obs.handles[slot]=*out;af_obs.stream[slot]=(uint8_t)stream;af_obs.width[slot]=cfg->channel;}
    printf("AF_OPEN kind=%u fixture=%u schedule=%u slot=%u stream=%u channels=%u rate=%" PRIu32 " self_delimited=%u result=%d handle=%u before=%u after=%u\n",
        af_obs.kind,af_obs.id,af_obs.schedule,slot,stream,(unsigned)cfg->channel,cfg->sample_rate,(unsigned)cfg->self_delimited,(int)result,(unsigned)(*out!=NULL),(unsigned)before,(unsigned)esp_get_free_heap_size());return result;
}
esp_audio_err_t af_decode(void *handle,esp_audio_dec_in_raw_t *raw,esp_audio_dec_out_frame_t *out,esp_audio_dec_info_t *info) {
    unsigned slot=slot_for(handle),input=raw->len,capacity=out->len;esp_audio_err_t result=esp_opus_dec_decode(handle,raw,out,info);++af_obs.calls;
    af_obs.consumed+=raw->consumed;af_obs.decoded+=out->decoded_size;
    if(out->decoded_size) {
        ++af_obs.outputs;
        if(info->sample_rate==48000 && info->channel==af_obs.width[slot] && info->bits_per_sample==16 && out->decoded_size%(info->channel*2u)==0)
            af_obs.frames[slot]+=out->decoded_size/(info->channel*2u);
        else ++af_obs.geometry_errors;
    }
    printf("AF_CALL kind=%u fixture=%u schedule=%u call=%u slot=%u stream=%u len=%u consumed=%" PRIu32 " capacity=%u needed=%" PRIu32
        " decoded=%" PRIu32 " result=%d rate=%" PRIu32 " channels=%u bits=%u\n",af_obs.kind,af_obs.id,af_obs.schedule,af_obs.calls,slot,(unsigned)af_obs.stream[slot],input,
        raw->consumed,capacity,out->needed_size,out->decoded_size,(int)result,info->sample_rate,(unsigned)info->channel,(unsigned)info->bits_per_sample);return result;
}
esp_audio_err_t af_close(void *handle) {
    unsigned slot=slot_for(handle);esp_audio_err_t result=esp_opus_dec_close(handle);++af_obs.closes;
    if(result==ESP_AUDIO_ERR_OK)af_obs.handles[slot]=NULL;else ++af_obs.close_errors;
    printf("AF_CLOSE kind=%u fixture=%u schedule=%u slot=%u stream=%u result=%d pending=%u\n",af_obs.kind,af_obs.id,af_obs.schedule,slot,(unsigned)af_obs.stream[slot],(int)result,(unsigned)(af_obs.handles[slot]!=NULL));return result;
}
void af_hash_begin(af_output *o) {memset(o,0,sizeof(*o));o->lifetime=true;o->hash=psa_hash_operation_init();assert(psa_hash_setup(&o->hash,PSA_ALG_SHA_256)==PSA_SUCCESS);}
void af_hash_add(af_output *o,const uint8_t *data,size_t bytes) {
    assert(bytes && bytes<=2048 && data);assert(psa_hash_update(&o->hash,data,bytes)==PSA_SUCCESS);o->bytes+=bytes;++o->chunks;if(bytes>o->max_chunk)o->max_chunk=(unsigned)bytes;
}
void af_hash_finish(af_output *o,char hex[65]) {
    uint8_t digest[32];size_t bytes=0;assert(psa_hash_finish(&o->hash,digest,sizeof(digest),&bytes)==PSA_SUCCESS && bytes==32);assert(psa_hash_abort(&o->hash)==PSA_SUCCESS);
    for(unsigned i=0;i<32;++i)snprintf(hex+i*2u,3,"%02x",digest[i]);
}
static bool cancelled(void *opaque){(void)opaque;return false;}
static void yield(void *opaque){(void)opaque;vTaskDelay(1);}
typedef struct {const af_fixture *fixture;opus_family1_playback *adapter;af_output *out;} sink_context;
static bool output(void *opaque,uint32_t generation,const opus_family1_plan *plan,const uint8_t *pcm,size_t bytes) {
    sink_context *context=opaque;const af_fixture *e=context->fixture;af_output *out=context->out;
    if(generation!=42 || plan->channels!=e->channels || plan->pre_skip!=e->pre_skip || plan->header_gain_q8!=(int16_t)e->gain || plan->input_rate!=44100 ||
        !bytes || bytes>128u*e->channels*2u || bytes%(e->channels*2u))return false;
    bool lease=plan->needed?(pcm==context->adapter->decoder.scratch && context->adapter->decoder.capacity>=bytes && context->adapter->decoder.active && af_live()):
        (pcm==ofp_zero_chunk && !context->adapter->decoder.scratch && !af_live());out->lifetime=out->lifetime && lease;
    if(!lease)return false;
    af_hash_add(out,pcm,bytes);if((out->chunks&31u)==0u)vTaskDelay(1);return true;
}
static bool run_adapter(const af_fixture *e,unsigned schedule,unsigned style,unsigned chunk,af_output *out,int *driver,unsigned *acks,size_t *used_bytes) {
    opus_family1_playback *adapter=active_adapter;ogg_page_input *input=active_input;assert(adapter && input && !ofp_has_input(adapter));opi_reset(input,42);sink_context context={e,adapter,out};
    ofp_callbacks cb={cancelled,output,yield,&context};ofd_public_api api={af_open,af_decode,af_close};size_t total=style?e->split_bytes:e->whole_bytes;
    const uint8_t *data=af_blob+(style?e->split:e->whole);size_t at=0;*driver=0;*acks=0;
    for(;;) {
        size_t bytes=total-at;if(chunk && bytes>chunk)bytes=chunk;size_t used=0;ogg_page_input_status status=opi_feed(input,bytes?data+at:NULL,bytes,&used);if(used>bytes){*driver=3;break;}at+=used;
        if(status<0){*driver=4;printf("AF_FAILURE fixture=%u schedule=%u source=0 status=%d detail=0 public_known=0 public_result=0 cleanup_pending=%u\n",(unsigned)e->id,schedule,(int)status,af_live());break;}
        if(status==OPI_PAGE) {
            oopt_event event=input->event;ofp_result result=ofp_page(adapter,input,&cb,&api);
            if(result.code!=OFP_OK) {
                *driver=result.code==OFP_MEMORY?1:2;printf("AF_FAILURE fixture=%u schedule=%u source=1 status=%d detail=%d public_known=%u public_result=%d cleanup_pending=%u\n",
                    (unsigned)e->id,schedule,(int)result.code,result.detail,(unsigned)result.decoder.public_error_known,(int)result.decoder.public_error,(unsigned)result.cleanup_pending);break;
            }
            if(input->ready || input->size || (event.flags&OOPT_LINK_END && (af_live() || !input->timeline.seen_eos))){*driver=3;break;}
            ++*acks;if(input->capacity)memset(input->page,0xa5,input->capacity); /* Only AFTER actual successful ACK. */
        } else {if(status!=OPI_MORE){*driver=3;break;}if(at==total)break;if(!used){*driver=3;break;}}
    }
    if(!*driver && (opi_finish(input)!=OPI_FINISHED || ofp_has_input(adapter) || out->bytes!=(uint64_t)e->logical*e->channels*2u || *acks!=(style?e->split_pages:e->whole_pages)))*driver=7;
    ofp_result closed=ofp_abandon(adapter);*used_bytes=at;
    if(closed.code!=OFP_OK || closed.cleanup_pending){*driver=8;printf("AF_FAILURE fixture=%u schedule=%u source=2 status=%d detail=%d public_known=%u public_result=%d cleanup_pending=%u\n",(unsigned)e->id,schedule,(int)closed.code,closed.detail,(unsigned)closed.decoder.public_error_known,(int)closed.decoder.public_error,(unsigned)closed.cleanup_pending);}
    else opi_reset(input,43);
    return !*driver;
}
static bool run_case(const af_fixture *e,unsigned kind,unsigned schedule,unsigned style,unsigned chunk) {
    af_begin(kind,e->id,schedule);size_t before=esp_get_free_heap_size(),used=0;af_output out;af_hash_begin(&out);unsigned acks=0;int driver=0;
    bool complete=kind?run_adapter(e,schedule,style,chunk,&out,&driver,&acks,&used):af_reference(e,&out,&driver);char digest[65];af_hash_finish(&out,digest);
    bool integrity=heap_caps_check_integrity_all(true);size_t after=esp_get_free_heap_size();complete=complete && integrity && !af_live() && !af_obs.geometry_errors && out.lifetime;
    printf("AF_RESULT kind=%u fixture=%u schedule=%u style=%u chunk=%u complete=%u driver=%d channels=%" PRIu32 " needed=%" PRIu32 " opens=%u calls=%u closes=%u close_errors=%u live=%u"
        " consumed=%" PRIu64 " decoded=%" PRIu64 " outputs=%u pcm=%" PRIu64 " chunks=%u max_chunk=%u lifetime=%u sha=%s input_used=%u acks=%u before=%u after=%u heap_min=%u stack_free=%u core=%d priority=%u integrity=%u\n",
        kind,(unsigned)e->id,schedule,style,chunk,(unsigned)complete,driver,e->channels,e->needed,af_obs.opens,af_obs.calls,af_obs.closes,af_obs.close_errors,af_live(),af_obs.consumed,af_obs.decoded,af_obs.outputs,
        out.bytes,out.chunks,out.max_chunk,(unsigned)out.lifetime,digest,(unsigned)used,acks,(unsigned)before,(unsigned)after,(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL),(unsigned)integrity);
    for(unsigned slot=0;slot<8;++slot)if(af_obs.frames[slot])printf("AF_FRAMES kind=%u fixture=%u schedule=%u slot=%u stream=%u frames=%" PRIu64 "\n",kind,(unsigned)e->id,schedule,slot,(unsigned)af_obs.stream[slot],af_obs.frames[slot]);
    fflush(stdout);if(complete){if(kind)++adapter_cases;else ++fixture_refs;}vTaskDelay(1);return complete;
}
static void worker(void *unused) {
    (void)unused;assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==5 && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK && psa_crypto_init()==PSA_SUCCESS);
    /* These owners live until worker termination/reboot even if a real close
     * refuses. Never return from a shorter scope holding public cfg/page leases.
     */
    opus_family1_playback adapter={0};ogg_page_input input={0};active_adapter=&adapter;active_input=&input;
    assert(af_le32(af_blob)==UINT32_C(0x46504131) && af_le32(af_blob+4)==1 && af_le32(af_blob+8)==12 && af_le32(af_blob+12)==80);const af_fixture *entries=(const af_fixture *)(af_blob+16);
    for(unsigned group=0;group<2;++group) {size_t before=esp_get_free_heap_size();for(unsigned i=0;i<32;++i){af_output out;af_hash_begin(&out);char hex[65];af_hash_finish(&out,hex);assert(!strcmp(hex,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"));}
        printf("AF_HASH_CONTROL group=%u iterations=32 before=%u after=%u\n",group,(unsigned)before,(unsigned)esp_get_free_heap_size());}
    size_t before=esp_get_free_heap_size();bool complete=true;
    for(unsigned fixture=0;fixture<12 && complete;++fixture) {
        const af_fixture *e=entries+fixture;assert(e->id==fixture && e->channels && e->channels<=8 && e->streams<=5 && e->packets && e->packets<=92);
        complete=run_case(e,0,0,0,0);if(!complete)break;
        if(fixture<3)for(unsigned style=0;style<2 && complete;++style)for(unsigned feed=0;feed<2 && complete;++feed)complete=run_case(e,1,style*2u+feed,style,feed?257:0);
        else if(fixture==11)for(unsigned style=0;style<2 && complete;++style)complete=run_case(e,1,style,style,257);
        else complete=run_case(e,1,0,fixture%2u,257);
    }
    bool integrity=heap_caps_check_integrity_all(true);printf("AF_COMPLETE references=%u adapters=%u complete=%u before=%u after=%u heap_min=%u stack_free=%u live=%u core=1 priority=5 integrity=%u\n",fixture_refs,adapter_cases,(unsigned)complete,(unsigned)before,(unsigned)esp_get_free_heap_size(),(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),af_live(),(unsigned)integrity);fflush(stdout);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);printf("AF_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=5 stack=16384 fixtures=12 adapter_bytes=%u decoder_bytes=%u tags_bytes=%u zero_bytes=%u hardware=0\n",
        (unsigned)sizeof(opus_family1_playback),(unsigned)sizeof(opus_family1_decoder),(unsigned)sizeof(opus_tags_stream),(unsigned)sizeof(ofp_zero_chunk));fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"family1gate",16384,NULL,5,NULL,1)==pdPASS);while(true)vTaskDelay(portMAX_DELAY);
}
