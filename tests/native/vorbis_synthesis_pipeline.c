// Public-API raw-packet synthesis shared by the host and minimal MCU fixture.
#include "vorbis_synthesis_pipeline.h"
#include <stdlib.h>
#include <string.h>

typedef union {max_align_t alignment;struct {size_t bytes;} value;} allocation_t;
typedef struct {native_vorbis_imdct_plan_t plan;double *trig;int *bitrev;} transform_t;
typedef struct {
    vorbis_synthesis_pipeline_result_t result;
    native_vorbis_setup_owner_t *setup_owner;
    native_vorbis_window_plan_t short_plan,long_plan;
    native_vorbis_synthesis_t synthesis;
    transform_t transforms[2];
    uint32_t channels;
    double *short_coefficients,*long_coefficients,*history,**work,*spectrum;
    int64_t *exponents;
    native_vorbis_transform_block_t *blocks;
    size_t *capacities;
    int16_t *pcm;
    native_vorbis_frame_workspace_t frame;
    uint8_t *curve;
    uint16_t *map;
    native_vorbis_floor0_factor_t *factors;
    uint32_t *product;
    size_t product_capacity;
} resources_t;

static bool bits_for_bytes(uint64_t bytes,uint64_t *bits){
    if(bytes>UINT64_MAX/8)return false;
    *bits=bytes*8;return true;
}
static bool addressable(uint64_t count,size_t unit){return unit&&count<=SIZE_MAX/unit;}
static void *allocate(void *context,size_t bytes){
    resources_t *r=context;
    if(!bytes||bytes>SIZE_MAX-sizeof(allocation_t)||bytes>SIZE_MAX-r->result.live_payload_bytes)return NULL;
    allocation_t *a=malloc(sizeof(*a)+bytes);if(!a)return NULL;
    a->value.bytes=bytes;++r->result.allocations;++r->result.live_allocations;r->result.live_payload_bytes+=bytes;
    if(r->result.live_allocations>r->result.peak_allocations)r->result.peak_allocations=r->result.live_allocations;
    if(r->result.live_payload_bytes>r->result.peak_payload_bytes)r->result.peak_payload_bytes=r->result.live_payload_bytes;
    return a+1;
}
static void release(void *context,void *pointer){
    resources_t *r=context;if(!pointer)return;allocation_t *a=(allocation_t *)pointer-1;
    r->result.live_payload_bytes-=a->value.bytes;--r->result.live_allocations;++r->result.releases;free(a);
}
static void *array(resources_t *r,uint64_t count,size_t unit,int *status){
    if(!unit||count>SIZE_MAX/unit){*status=NATIVE_VORBIS_NUMERIC_RANGE;return NULL;}
    void *pointer=count?allocate(r,(size_t)count*unit):NULL;
    *status=!count||pointer?0:-101;return pointer;
}
static void *grow(resources_t *r,void *pointer,size_t *capacity,uint64_t count,size_t unit,int *status){
    if(count<=*capacity){*status=0;return pointer;}
    if(!unit||count>SIZE_MAX/unit){*status=NATIVE_VORBIS_NUMERIC_RANGE;return pointer;}
    // No earlier frame borrows remain when scratch is grown for another packet.
    release(r,pointer);*capacity=0;
    pointer=array(r,count,unit,status);if(!*status)*capacity=(size_t)count;return pointer;
}
static void cleanup(resources_t *r){
    native_vorbis_setup_owner_clear(&r->setup_owner);
    if(r->work)for(uint32_t i=0;i<r->channels;++i)release(r,r->work[i]);
    for(unsigned i=0;i<2;++i){release(r,r->transforms[i].trig);release(r,r->transforms[i].bitrev);}
    release(r,r->frame.floors);release(r,r->frame.floor0);release(r,r->frame.floor1);
    release(r,r->frame.spectrum);release(r,r->frame.classifications);
    release(r,r->curve);release(r,r->map);release(r,r->factors);release(r,r->product);release(r,r->spectrum);
    release(r,r->short_coefficients);release(r,r->long_coefficients);release(r,r->history);release(r,r->exponents);
    release(r,r->work);release(r,r->blocks);release(r,r->capacities);release(r,r->pcm);
}
static int frame_storage(resources_t *r,const native_vorbis_frame_requirements_t *q){
    int status;
#define GROW(P,C,N) do{r->frame.P=grow(r,r->frame.P,&r->frame.C,N,sizeof(*r->frame.P),&status);if(status)return status;}while(0)
    GROW(floors,floor_capacity,q->floor_count);GROW(floor0,floor0_capacity,q->floor0_values);
    GROW(floor1,floor1_capacity,q->floor1_values);GROW(spectrum,spectrum_capacity,q->residue_bound.limb_count);
    GROW(classifications,classification_capacity,q->residue_bound.classification_count);
#undef GROW
    return 0;
}
static int transform_prepare(resources_t *r,unsigned which,uint32_t n){
    transform_t *t=&r->transforms[which];if(t->plan.blocksize)return 0;
    native_vorbis_imdct_requirements_t q;int status=native_vorbis_imdct_measure(n,&q);if(status)return status;
    t->trig=array(r,q.trig_count,sizeof(*t->trig),&status);if(status)return status;
    t->bitrev=array(r,q.bitrev_count,sizeof(*t->bitrev),&status);if(status)return status;
    return native_vorbis_imdct_prepare(n,t->trig,(size_t)q.trig_count,t->bitrev,(size_t)q.bitrev_count,&t->plan);
}

int vorbis_synthesis_pipeline_run(const vorbis_synthesis_pipeline_case_t *input,
    const vorbis_synthesis_pipeline_callbacks_t *callbacks,vorbis_synthesis_pipeline_result_t *result){
    if(!result)return NATIVE_VORBIS_NUMERIC_INVALID;
    resources_t r={0};r.result.failed_packet=UINT32_MAX;r.result.failed_channel=UINT32_MAX;r.result.failed_route=UINT32_MAX;
    int status=0;const char *stage="input";
    if(!input||!input->identification||!input->setup||!input->audio||!input->packet_offsets||!input->granules||!input->packet_count){status=-1;goto done;}
    uint64_t identification_bits,setup_bits;
    if(!bits_for_bytes(input->identification_bytes,&identification_bits)||!bits_for_bytes(input->setup_bytes,&setup_bits)||
        !addressable((uint64_t)input->packet_count+1,sizeof(*input->packet_offsets))||
        !addressable(input->packet_count,sizeof(*input->granules))){status=-2;goto done;}
    if(input->packet_offsets[0]||input->packet_offsets[input->packet_count]!=input->audio_bytes){status=-1;goto done;}
    for(uint32_t i=0;i<input->packet_count;++i)if(input->packet_offsets[i]>input->packet_offsets[i+1]||input->granules[i]<-1){status=-1;goto done;}
    native_vorbis_setup_allocator_t allocator={.context=&r,.allocate=allocate,.release=release};
    stage="setup-owner";status=native_vorbis_setup_owner_replace(&r.setup_owner,input->identification,input->identification_bytes,
        identification_bits,input->setup,input->setup_bytes,setup_bits,&allocator);
    if(status)goto done;
    const native_vorbis_setup_t *setup=native_vorbis_setup_owner_view(r.setup_owner);
    uint32_t s=setup->layout.identification.blocksize_0,l=setup->layout.identification.blocksize_1;
    r.channels=setup->layout.identification.channels;
    native_vorbis_synthesis_requirements_t requirements;
    stage="synthesis-measure";status=native_vorbis_synthesis_measure(s,l,r.channels,&requirements);if(status)goto done;
#define ARRAY(P,N) do{r.P=array(&r,N,sizeof(*r.P),&status);if(status)goto done;}while(0)
    stage="stream-storage";ARRAY(short_coefficients,s/2);if(s!=l)ARRAY(long_coefficients,l/2);
    ARRAY(history,requirements.history_samples);ARRAY(exponents,requirements.exponent_count);
    ARRAY(work,r.channels);memset(r.work,0,(size_t)r.channels*sizeof(*r.work));
    ARRAY(blocks,r.channels);ARRAY(capacities,r.channels);ARRAY(pcm,requirements.max_pcm_samples);
    ARRAY(curve,l/2);ARRAY(map,l/2);ARRAY(factors,l/2);ARRAY(spectrum,l/2);
    for(uint32_t channel=0;channel<r.channels;++channel){
        r.work[channel]=array(&r,(uint64_t)l+8,sizeof(*r.work[channel]),&status);if(status)goto done;
        r.capacities[channel]=l;
    }
#undef ARRAY
    stage="window-prepare";status=native_vorbis_window_prepare(s,r.short_coefficients,s/2,&r.short_plan);if(status)goto done;
    if(s==l)r.long_plan=r.short_plan;
    else{status=native_vorbis_window_prepare(l,r.long_coefficients,l/2,&r.long_plan);if(status)goto done;}
    stage="synthesis-init";status=native_vorbis_synthesis_init(&r.short_plan,&r.long_plan,r.channels,r.history,
        (size_t)requirements.history_samples,r.exponents,requirements.exponent_count,&r.synthesis);if(status)goto done;
    for(uint32_t packet_index=0;packet_index<input->packet_count;++packet_index){
        r.result.failed_packet=packet_index;r.result.failed_channel=UINT32_MAX;r.result.failed_route=UINT32_MAX;
        const uint8_t *raw=input->audio+input->packet_offsets[packet_index];
        size_t bytes=input->packet_offsets[packet_index+1]-input->packet_offsets[packet_index];
        native_vorbis_packet_t packet;stage="packet-init";status=native_vorbis_packet_init(&packet,raw,bytes,(uint64_t)bytes*8,0);if(status)goto done;
        native_vorbis_frame_requirements_t q;stage="frame-measure";status=native_vorbis_frame_measure(setup,&packet,&q);if(status)goto done;
        stage="frame-storage";status=frame_storage(&r,&q);if(status)goto done;
        native_vorbis_packet_frame_t frame;stage="frame-decode";status=native_vorbis_frame_decode(setup,&packet,&r.frame,&frame);if(status)goto done;
        uint32_t n=frame.prefix.blocksize,bins=n/2;unsigned which=n==l&&s!=l;
        stage="imdct-prepare";status=transform_prepare(&r,which,n);if(status)goto done;
        vorbis_synthesis_pipeline_packet_t metadata={.packet=packet_index,.blocksize=n,.channels=r.channels,
            .consumed_bits=packet.position,.end_of_packet=packet.end_of_packet};
        for(uint32_t channel=0;channel<r.channels;++channel){
            r.result.failed_channel=channel;native_vorbis_transform_block_t spectrum;
            if(frame.floors[channel].state.type==0){
                ++metadata.floor0_channels;native_vorbis_floor0_spectrum_plan_t plan;
                stage="floor0-prepare";status=native_vorbis_frame_floor0_prepare(&frame,channel,r.map,l/2,r.factors,l/2,&plan);if(status)goto done;
                if(plan.route!=NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE){r.result.failed_route=plan.route;status=-104;stage="floor0-route";goto done;}
                stage="floor0-materialize";status=native_vorbis_frame_floor0_materialize(&plan,r.spectrum,bins,&spectrum);if(status)goto done;
            }else if(frame.floors[channel].state.type==1){
                ++metadata.floor1_channels;native_vorbis_floor1_product_layout_t layout;
                stage="floor1-measure";status=native_vorbis_frame_floor1_measure(&frame,channel,r.curve,l/2,&layout);if(status)goto done;
                stage="floor1-storage";r.product=grow(&r,r.product,&r.product_capacity,layout.limb_count,sizeof(*r.product),&status);if(status)goto done;
                native_vorbis_floor1_product_t product;stage="floor1-product";
                status=native_vorbis_frame_floor1_product(&frame,channel,r.curve,l/2,layout.limb_count?r.product:NULL,(size_t)layout.limb_count,&product);if(status)goto done;
                stage="floor1-materialize";status=native_vorbis_spectrum_to_binary64(&product,(size_t)layout.limb_count,r.spectrum,bins,&spectrum);if(status)goto done;
            }else{status=-1;stage="floor-type";goto done;}
            stage="imdct";status=native_vorbis_imdct_transform_binary64(&r.transforms[which].plan,&spectrum,bins,r.work[channel],(size_t)l+8,&r.blocks[channel]);if(status)goto done;
        }
        r.result.failed_channel=UINT32_MAX;
        native_vorbis_timing_event_t event={.blocksize=n,.granule_position=input->granules[packet_index],
            .end_of_stream=packet_index+1==input->packet_count};
        stage="synthesis-push";status=native_vorbis_synthesis_push(&r.synthesis,&event,r.blocks,r.capacities,r.channels,
            r.pcm,(size_t)requirements.max_pcm_samples,&metadata.synthesis);if(status)goto done;
        if(callbacks&&callbacks->packet&&!callbacks->packet(callbacks->context,&metadata)){status=-102;stage="packet-callback";goto done;}
        if(callbacks&&callbacks->pcm)for(uint64_t offset=0;offset<metadata.synthesis.pcm_samples;){
            size_t count=metadata.synthesis.pcm_samples-offset>128?128:(size_t)(metadata.synthesis.pcm_samples-offset);
            if(!callbacks->pcm(callbacks->context,packet_index,r.pcm+(size_t)offset,count)){status=-102;stage="pcm-callback";goto done;}
            offset+=count;
        }
        ++r.result.packets;r.result.frames+=metadata.synthesis.timing.count;r.result.pcm_samples+=metadata.synthesis.pcm_samples;
        r.result.floor0_channels+=metadata.floor0_channels;r.result.floor1_channels+=metadata.floor1_channels;
    }
    r.result.failed_packet=UINT32_MAX;r.result.failed_channel=UINT32_MAX;r.result.failed_route=UINT32_MAX;
done:
    r.result.status=status;
    if(status&&callbacks&&callbacks->error)callbacks->error(callbacks->context,r.result.failed_packet,stage,status,r.result.failed_channel,r.result.failed_route);
    cleanup(&r);*result=r.result;return status;
}
