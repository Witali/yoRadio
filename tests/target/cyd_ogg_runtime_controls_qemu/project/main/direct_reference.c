/* Independent integration oracle: documented public raw handles + prepared
 * original AppendixB offsets. NO production framing/mapping/trim/page helper.
 * PCM is hashed completely in logical speaker order after independently
 * calculated preskip/end bounds. This is a same-vendor regression oracle,
 * not creator numeric conformance and not a replacement decoder.
 */
#include "probe.h"
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
typedef struct {esp_opus_dec_cfg_t cfg[8];void *handle[8];uint8_t *scratch,*planes;size_t capacity,plane_capacity;} reference_owner;
static reference_owner owner; /* Stable public cfg addresses through real close, including failure. */
static void workspace(const char *operation,const char *phase,unsigned stream,size_t requested,int result,bool present) {
    printf("CYD_F1_REFERENCE_WORKSPACE index=%u operation=%s phase=%s stream=%u requested=%u result=%d present=%u heap_free=%u largest_internal=%u heap_min=%u\n",
        af_obs.id,operation,phase,stream,(unsigned)requested,result,(unsigned)present,(unsigned)esp_get_free_heap_size(),
        (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),(unsigned)esp_get_minimum_free_heap_size());
}
static bool cleanup(void) {
    bool quiet=true;
    for(unsigned s=0;s<8;++s)if(owner.handle[s]) {
        if(af_close(owner.handle[s])==ESP_AUDIO_ERR_OK)owner.handle[s]=NULL;else quiet=false;
    }
    if(quiet){free(owner.scratch);free(owner.planes);owner.scratch=owner.planes=NULL;owner.capacity=owner.plane_capacity=0;}
    return quiet;
}
bool af_reference(const af_fixture *e,af_output *output,int *driver) {
    assert(e->streams<=5 && e->streams+e->coupled<=8);for(unsigned s=0;s<8;++s)assert(!owner.handle[s]);*driver=0;
    /* Independent legal maximum:5760 frames, widest actual elementary stream,
     * signed16. Reference allocation is independent of the production owner's
     * documented11520→23040 retry protocol, which remains unchanged. */
    owner.capacity=5760u*(e->coupled?2u:1u)*sizeof(int16_t);
    workspace("SCRATCH","BEFORE",255,owner.capacity,-1,false);
    owner.scratch=malloc(owner.capacity);
    workspace("SCRATCH","AFTER",255,owner.capacity,owner.scratch?0:1,owner.scratch!=NULL);
    if(!owner.scratch){owner.capacity=0;*driver=1;goto done;}
    for(unsigned s=0;s<e->streams;++s) {
        owner.cfg[s]=(esp_opus_dec_cfg_t){.sample_rate=48000,.channel=s<e->coupled?2:1,.frame_duration=ESP_OPUS_DEC_FRAME_DURATION_INVALID,.self_delimited=s+1<e->streams};
        workspace("OPEN","BEFORE",s,0,-1,false);
        esp_audio_err_t result=af_open(owner.cfg+s,sizeof(owner.cfg[s]),owner.handle+s);
        workspace("OPEN","AFTER",s,0,result,owner.handle[s]!=NULL);
        if(result!=ESP_AUDIO_ERR_OK || !owner.handle[s]){*driver=2;goto done;}
    }
    const uint8_t *table=af_blob+e->table;uint64_t position=0;unsigned decoded_channels=e->streams+e->coupled;
    for(unsigned p=0;p<e->packets;++p) {
        unsigned samples=af_le32(table),bytes=af_le32(table+4),offset=af_le32(table+8);const uint8_t *parts=table+12;table+=12+8u*e->streams;
        assert(samples && samples<=5760 && bytes && offset<=(size_t)(af_blob_end-af_blob) && bytes<=(size_t)(af_blob_end-af_blob)-offset);
        size_t plane_bytes=(size_t)samples*decoded_channels*2u;
        if(plane_bytes>owner.plane_capacity){
            workspace("PLANES","BEFORE",255,plane_bytes,-1,owner.planes!=NULL);
            uint8_t *larger=realloc(owner.planes,plane_bytes);
            workspace("PLANES","AFTER",255,plane_bytes,larger?0:1,larger!=NULL);
            if(!larger){*driver=1;goto done;}owner.planes=larger;owner.plane_capacity=plane_bytes;
        }
        unsigned total=0;
        for(unsigned s=0;s<e->streams;++s) {
            unsigned start=af_le32(parts+s*8u),size=af_le32(parts+s*8u+4),width=s<e->coupled?2u:1u;assert(start==total && size<=bytes-start);total+=size;size_t produced=0;
            esp_audio_dec_in_raw_t raw={.buffer=(uint8_t *)af_blob+offset+start,.len=size,.frame_recover=ESP_AUDIO_DEC_RECOVERY_NONE};
            for(;;) {
                unsigned input=raw.len;raw.consumed=0;esp_audio_dec_out_frame_t frame={.buffer=owner.scratch,.len=(uint32_t)owner.capacity};esp_audio_dec_info_t info={0};
                esp_audio_err_t actual=af_decode(owner.handle[s],&raw,&frame,&info);vTaskDelay(1);
                if(raw.len!=input || raw.consumed>input || frame.decoded_size>owner.capacity){*driver=3;goto done;}
                raw.buffer+=raw.consumed;raw.len-=raw.consumed;
                if(actual==ESP_AUDIO_ERR_BUFF_NOT_ENOUGH) {
                    if(frame.decoded_size || frame.needed_size<=owner.capacity || frame.needed_size>23040){*driver=3;goto done;}
                    uint8_t *larger=realloc(owner.scratch,frame.needed_size);if(!larger){*driver=1;goto done;}owner.scratch=larger;owner.capacity=frame.needed_size;continue;
                }
                if(actual!=ESP_AUDIO_ERR_OK){*driver=2;goto done;}
                if(frame.decoded_size) {
                    if(info.sample_rate!=48000 || info.channel!=width || info.bits_per_sample!=16 || frame.decoded_size%(width*2u)){*driver=3;goto done;}
                    size_t frames=frame.decoded_size/(width*2u);if(frames>samples-produced){*driver=3;goto done;}
                    unsigned first=s<e->coupled?s*2u:s+e->coupled;
                    for(unsigned channel=0;channel<width;++channel)for(size_t f=0;f<frames;++f) {
                        uint8_t *to=owner.planes+((size_t)(first+channel)*samples+produced+f)*2u;const uint8_t *from=owner.scratch+(f*width+channel)*2u;to[0]=from[0];to[1]=from[1];
                    }
                    produced+=frames;
                }
                if(!raw.len && produced==samples)break;
                if(produced==samples || (!raw.consumed && !frame.decoded_size)){*driver=3;goto done;}
            }
        }
        assert(total==bytes);uint64_t first=position>e->pre_skip?position:e->pre_skip,end=e->pre_skip+(uint64_t)e->logical,last=position+samples;if(last>end)last=end;
        while(first<last) {
            size_t frames=last-first;if(frames>128)frames=128;
            for(size_t f=0;f<frames;++f)for(unsigned speaker=0;speaker<e->channels;++speaker) {
                unsigned channel=e->mapping[speaker];uint8_t *to=owner.scratch+(f*e->channels+speaker)*2u;
                if(channel==255)to[0]=to[1]=0;
                else {assert(channel<decoded_channels);const uint8_t *from=owner.planes+((size_t)channel*samples+(size_t)(first-position)+f)*2u;to[0]=from[0];to[1]=from[1];}
            }
            af_hash_add(output,owner.scratch,frames*e->channels*2u);first+=frames;
        }
        position+=samples;
    }
    if(position!=e->raw || output->bytes!=(uint64_t)e->logical*e->channels*2u)*driver=7;
done:
    if(!cleanup())*driver=8;
    return !*driver;
}
