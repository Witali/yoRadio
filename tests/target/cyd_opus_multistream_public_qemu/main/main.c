/* Public independent mono/stereo Opus handles, with unchanged documented APIs.
 * Original AppendixB segments first; common-framing controls use independently
 * creator-qualified removal of the extra length field. No Ogg/private decoder.
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
#include "esp_opus_dec.h"
#ifdef NDEBUG
#error "Public diagnostic assertions are required"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "Classic ESP32/LX6 only"
#endif
extern const uint8_t blob_start[] asm("_binary_streams_bin_start");
extern const uint8_t blob_end[] asm("_binary_streams_bin_end");
typedef struct {uint32_t magic,version,count,entry_size;} header_t;
typedef struct {uint32_t channels,offset,bytes,streams,coupled,packets,raw_frames,logical_frames;} entry_t;
typedef struct {const uint8_t *original,*common;uint32_t original_size,common_size,self_delimited;} view_t;
typedef struct {void *handle;uint8_t *pcm;size_t capacity;uint64_t bytes,frames,consumed,expected;unsigned calls,outputs,closes;int last_result,close_result;} stream_t;
_Static_assert(sizeof(header_t)==16 && sizeof(entry_t)==32,"transport ABI");
static uint32_t le32(const uint8_t *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static void pcm_record(unsigned id,unsigned stream,const uint8_t *data,size_t size,uint64_t offset) {
    for(size_t at=0;at<size;at+=128) {
        size_t n=size-at;if(n>128)n=128;char text[257];for(size_t i=0;i<n;++i)snprintf(text+2*i,3,"%02x",data[at+i]);
        printf("MS_PCM id=%u stream=%u offset=%" PRIu64 " bytes=%u hex=%s\n",id,stream,offset+at,(unsigned)n,text);
    }
}
static void parse(const entry_t *e,view_t views[11][5]) {
    const uint8_t *body=blob_start+e->offset,*at=body+40,*end=body+e->bytes;
    assert(e->bytes>=40 && !memcmp(body,"MSPUB01\0",8) && le32(body+8)==e->channels && le32(body+12)==e->streams &&
        le32(body+16)==e->coupled && le32(body+28)==11);
    for(unsigned p=0;p<11;++p) {
        assert(end-at>=4);uint32_t packet_bytes=le32(at);at+=4;assert(packet_bytes && (size_t)(end-at)>=packet_bytes);
        const uint8_t *packet=at;at+=packet_bytes;uint32_t offset=0;
        for(unsigned s=0;s<e->streams;++s) {
            assert(end-at>=16);uint32_t begin=le32(at);view_t *v=&views[p][s];v->original_size=le32(at+4);v->common_size=le32(at+8);v->self_delimited=le32(at+12);at+=16;
            assert(begin==offset && v->original_size && v->common_size && v->common_size<=v->original_size &&
                v->original_size<=packet_bytes-offset && (size_t)(end-at)>=v->original_size+v->common_size && v->self_delimited==(s+1<e->streams));
            v->original=at;v->common=at+v->original_size;at+=v->original_size+v->common_size;
            assert(!memcmp(v->original,packet+offset,v->original_size));offset+=v->original_size;
        }
        assert(offset==packet_bytes);
    }
    assert(at==end);
}
static void run_case(unsigned id,const entry_t *e,unsigned mode) {
    view_t views[11][5]={0};parse(e,views);stream_t streams[5]={0};esp_opus_dec_cfg_t configs[5]={0};size_t before=esp_get_free_heap_size();
    int driver_status=0,api_status=0;unsigned public_calls=0,opens=0,close_calls=0,close_errors=0;bool geometry=true;
    for(unsigned s=0;s<e->streams;++s) {
        stream_t *own=streams+s;unsigned width=s<e->coupled?2:1;own->capacity=960*width*2;own->pcm=malloc(own->capacity);
        printf("MS_ALLOC id=%u stream=%u bytes=%u success=%u\n",id,s,(unsigned)own->capacity,(unsigned)(own->pcm!=NULL));
        if(!own->pcm){driver_status=1;break;}
        configs[s]=(esp_opus_dec_cfg_t){.sample_rate=48000,.channel=(uint8_t)width,.frame_duration=ESP_OPUS_DEC_FRAME_DURATION_20_MS,
            .self_delimited=!mode && s+1<e->streams};size_t start_heap=esp_get_free_heap_size();
        esp_audio_err_t result=esp_opus_dec_open(&configs[s],sizeof(configs[s]),&own->handle);api_status=result;++public_calls;
        printf("MS_OPEN id=%u stream=%u channels=%u rate=48000 self_delimited=%u result=%d handle=%u heap_before=%u heap_after=%u\n",
            id,s,width,(unsigned)configs[s].self_delimited,(int)result,(unsigned)(own->handle!=NULL),(unsigned)start_heap,(unsigned)esp_get_free_heap_size());
        if(result!=ESP_AUDIO_ERR_OK){driver_status=2;break;}assert(own->handle);++opens;
        for(unsigned p=0;p<11;++p)own->expected+=mode?views[p][s].common_size:views[p][s].original_size;
    }
    for(unsigned p=0;p<11 && !driver_status;++p)for(unsigned s=0;s<e->streams && !driver_status;++s) {
        stream_t *own=streams+s;view_t *v=&views[p][s];unsigned width=s<e->coupled?2:1;
        esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)(mode?v->common:v->original),.len=mode?v->common_size:v->original_size,
            .frame_recover=ESP_AUDIO_DEC_RECOVERY_NONE};
        for(;;) {
            esp_audio_dec_out_frame_t frame={.buffer=own->pcm,.len=(uint32_t)own->capacity};esp_audio_dec_info_t info={0};raw.consumed=0;
            uint32_t input=raw.len;esp_audio_err_t result=esp_opus_dec_decode(own->handle,&raw,&frame,&info);api_status=result;own->last_result=result;++own->calls;++public_calls;
            assert(raw.len==input && raw.consumed<=input && frame.decoded_size<=own->capacity);
            printf("MS_CALL id=%u packet=%u stream=%u call=%u len=%" PRIu32 " consumed=%" PRIu32 " capacity=%u needed=%" PRIu32
                " decoded=%" PRIu32 " result=%d rate=%" PRIu32 " channels=%u bits=%u\n",id,p,s,own->calls,input,raw.consumed,
                (unsigned)own->capacity,frame.needed_size,frame.decoded_size,(int)result,info.sample_rate,(unsigned)info.channel,(unsigned)info.bits_per_sample);
            raw.buffer+=raw.consumed;raw.len-=raw.consumed;own->consumed+=raw.consumed;
            if(frame.decoded_size) {
                pcm_record(id,s,frame.buffer,frame.decoded_size,own->bytes);own->bytes+=frame.decoded_size;++own->outputs;
                if(info.sample_rate==48000 && info.channel==width && info.bits_per_sample==16 && frame.decoded_size%(width*2)==0)
                    own->frames+=frame.decoded_size/(width*2);
                else geometry=false;
            }
            if(result==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                assert(!frame.decoded_size && frame.needed_size>own->capacity && frame.needed_size<=131072);
                uint8_t *larger=realloc(own->pcm,frame.needed_size);if(!larger){driver_status=1;break;}
                own->pcm=larger;own->capacity=frame.needed_size;continue;
            }
            if(result!=ESP_AUDIO_ERR_OK){driver_status=3;break;}
            if(!raw.len)break;
            if(!raw.consumed && !frame.decoded_size){driver_status=4;break;}
            assert(own->calls<1000);
        }
        vTaskDelay(1);
    }
    bool complete=!driver_status && geometry;
    for(unsigned s=0;s<e->streams;++s) {
        stream_t *own=streams+s;
        if(own->handle){own->close_result=esp_opus_dec_close(own->handle);++close_calls;++own->closes;close_errors+=own->close_result!=ESP_AUDIO_ERR_OK;
            printf("MS_CLOSE id=%u stream=%u result=%d\n",id,s,own->close_result);own->handle=NULL;}
        complete=complete && own->frames==10560 && own->consumed==own->expected && own->outputs==11 && own->closes==1 && own->close_result==0;
        printf("MS_STREAM id=%u stream=%u configured_channels=%u calls=%u outputs=%u expected_input=%" PRIu64 " consumed=%" PRIu64
            " frames=%" PRIu64 " pcm_bytes=%" PRIu64 " last_result=%d process_result_known=%u closes=%u close_result=%d\n",id,s,s<e->coupled?2u:1u,
            own->calls,own->outputs,own->expected,own->consumed,own->frames,own->bytes,own->last_result,(unsigned)(own->calls!=0),own->closes,own->close_result);
        free(own->pcm);
    }
    assert(heap_caps_check_integrity_all(true));size_t after=esp_get_free_heap_size();
    printf("MS_CASE id=%u encoded_channels=%u streams=%u coupled=%u mode=%u api_result=%d api_result_known=%u driver_status=%d geometry_valid=%u complete=%u"
        " opens=%u close_calls=%u close_errors=%u before=%u after=%u heap_min=%u stack_free=%u core=%d priority=%u\n",id,(unsigned)e->channels,
        (unsigned)e->streams,(unsigned)e->coupled,mode,api_status,(unsigned)(public_calls!=0),driver_status,(unsigned)geometry,(unsigned)complete,opens,close_calls,close_errors,
        (unsigned)before,(unsigned)after,(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL),xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(fflush(stdout)==0);vTaskDelay(1);
}
static void worker(void *unused) {
    (void)unused;assert(xPortGetCoreID()==1 && uxTaskPriorityGet(NULL)==3 && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK &&
        esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK);
    const header_t *head=(const header_t *)blob_start;assert(head->magic==UINT32_C(0x4d535055) && head->version==1 && head->count==3 && head->entry_size==32);
    const entry_t *entries=(const entry_t *)(head+1);size_t before=esp_get_free_heap_size();
    for(unsigned fixture=0;fixture<3;++fixture) {
        const entry_t *e=entries+fixture;assert((e->channels==3 || e->channels==6 || e->channels==8) && e->streams+e->coupled==e->channels && e->streams<=5 &&
            e->packets==11 && e->raw_frames==10560 && e->logical_frames==9600 && e->offset>=112 && e->offset<(size_t)(blob_end-blob_start) && e->bytes<=(size_t)(blob_end-blob_start)-e->offset);
        for(unsigned mode=0;mode<2;++mode)run_case(fixture*2+mode,e,mode);
    }
    assert(heap_caps_check_integrity_all(true));size_t after=esp_get_free_heap_size();
    printf("MS_COMPLETE cases=6 heap_before=%u heap_after=%u retained=%d heap_min=%u stack_free=%u core=1 priority=3 heap_integrity=1\n",
        (unsigned)before,(unsigned)after,(int)before-(int)after,(unsigned)esp_get_minimum_free_heap_size(),(unsigned)uxTaskGetStackHighWaterMark(NULL));fflush(stdout);esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID()==0);printf("MS_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 fixtures=3 modes=2 public_raw_handles=1\n");fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"opusmulti",16384,NULL,3,NULL,1)==pdPASS);while(true)vTaskDelay(portMAX_DELAY);
}
