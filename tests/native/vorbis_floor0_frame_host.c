// Real guarded packet decode -> floor application -> reused IMDCT, without PCM.
#include "native_vorbis_floor0_spectrum.h"
static native_vorbis_numeric_status_t capture_frame_decode(const native_vorbis_setup_t *,
    native_vorbis_packet_t *, const native_vorbis_frame_workspace_t *, native_vorbis_packet_frame_t *);
#define native_vorbis_frame_decode capture_frame_decode
#define main unused_packet_frame_main
#include "vorbis_packet_frame_host.c"
#undef main
#undef native_vorbis_frame_decode
#include <math.h>

static emitter_t handoff;
static bool capture_next;
static uint32_t current_case;
static uint64_t channel_total, floor0_total, floor1_total, route_total[6], handoff_refusals;

static void doubles_put(emitter_t *out, const double *values, uint32_t count) {
    for (uint32_t i = 0; i < count; ++i) {
        uint64_t word; memcpy(&word, values + i, 8); emit_integer(out, word, 8);
    }
}
static void tail_unchanged(const void *data, size_t used, size_t bytes) {
    const unsigned char *p = data;
    for (size_t i = used; i < bytes; ++i) check(p[i] == 0xa5);
}
typedef struct {
    unsigned char descriptor[sizeof(native_vorbis_packet_frame_t)];
    const void *input[4]; void *copy[4]; size_t bytes[4];
} frame_copy_t;
static frame_copy_t frame_snapshot(const native_vorbis_packet_frame_t *frame) {
    frame_copy_t c = {0}; memcpy(c.descriptor, frame, sizeof(*frame));
    c.input[0]=frame->floors; c.bytes[0]=frame->floor_count*sizeof(*frame->floors);
    c.input[1]=frame->floor0; c.bytes[1]=frame->floor0_count*sizeof(*frame->floor0);
    c.input[2]=frame->floor1; c.bytes[2]=frame->floor1_count*sizeof(*frame->floor1);
    c.input[3]=frame->spectrum; c.bytes[3]=(size_t)frame->spectrum_layout.limb_count*sizeof(*frame->spectrum);
    for (unsigned i=0;i<4;++i) if(c.bytes[i]) {c.copy[i]=tracked_allocate(c.bytes[i],TAG_SNAPSHOT);memcpy(c.copy[i],c.input[i],c.bytes[i]);}
    return c;
}
static void frame_unchanged(const native_vorbis_packet_frame_t *frame,const frame_copy_t *c) {
    check(!memcmp(c->descriptor,frame,sizeof(*frame)));
    for(unsigned i=0;i<4;++i) if(c->bytes[i]) check(!memcmp(c->copy[i],c->input[i],c->bytes[i]));
    validate_allocations();
}
static void frame_snapshot_free(frame_copy_t *c) {for(unsigned i=0;i<4;++i)tracked_free(c->copy[i]);}

static void prepare_refusal(const native_vorbis_packet_frame_t *frame,uint32_t channel,
    uint16_t *map,size_t mc,native_vorbis_floor0_factor_t *factors,size_t fc,
    int wanted,const native_vorbis_packet_frame_t *actual,const frame_copy_t *saved) {
    native_vorbis_floor0_spectrum_plan_t plan;memset(&plan,0xa5,sizeof(plan));
    unsigned char before[sizeof(plan)];memcpy(before,&plan,sizeof(plan));
    allocation_t *ma=map?find_allocation(map):NULL,*fa=factors?find_allocation(factors):NULL;
    void *map_copy=ma?tracked_allocate(ma->bytes,TAG_SNAPSHOT):NULL;
    void *factor_copy=fa?tracked_allocate(fa->bytes,TAG_SNAPSHOT):NULL;
    if(ma)memcpy(map_copy,map,ma->bytes);
    if(fa)memcpy(factor_copy,factors,fa->bytes);
    check(native_vorbis_frame_floor0_prepare(frame,channel,map,mc,factors,fc,&plan)==wanted);
    check(!memcmp(before,&plan,sizeof(plan)));
    if(ma)check(!memcmp(map_copy,map,ma->bytes));
    if(fa)check(!memcmp(factor_copy,factors,fa->bytes));
    tracked_free(factor_copy);tracked_free(map_copy);frame_unchanged(actual,saved);++handoff_refusals;
}
static void materialize_refusal(const native_vorbis_floor0_spectrum_plan_t *plan,
    double *output,size_t capacity,int wanted,const native_vorbis_packet_frame_t *frame,
    const frame_copy_t *saved,size_t bytes) {
    native_vorbis_transform_block_t result;memset(&result,0xa5,sizeof(result));
    unsigned char before[sizeof(result)];memcpy(before,&result,sizeof(result));
    unsigned char plan_before[sizeof(*plan)];if(plan)memcpy(plan_before,plan,sizeof(*plan));
    check(native_vorbis_frame_floor0_materialize(plan,output,capacity,&result)==wanted);
    check(!memcmp(before,&result,sizeof(result)));if(plan)check(!memcmp(plan_before,plan,sizeof(*plan)));
    if(output)tail_unchanged(output,0,bytes);
    frame_unchanged(frame,saved);++handoff_refusals;
}

static void transform_put(const native_vorbis_transform_block_t *source) {
    uint32_t n=source->count*2;
    native_vorbis_imdct_requirements_t req;check(native_vorbis_imdct_measure(n,&req)==0);
    double *trig=workspace_array(req.trig_count,sizeof(*trig));
    int *bitrev=workspace_array(req.bitrev_count,sizeof(*bitrev));
    double *work=workspace_array(n+12,sizeof(*work));
    native_vorbis_imdct_plan_t plan;
    check(native_vorbis_imdct_prepare(n,trig,(size_t)req.trig_count,bitrev,(size_t)req.bitrev_count,&plan)==0);
    freeze(trig);freeze(bitrev);
    unsigned char before[sizeof(plan)],source_before[sizeof(*source)];memcpy(before,&plan,sizeof(plan));memcpy(source_before,source,sizeof(*source));
    native_vorbis_transform_block_t result;
    check(native_vorbis_imdct_transform_binary64(&plan,source,source->count,work,n+8,&result)==0);
    check(result.count==n&&result.exponent==source->exponent&&result.samples==work+8);
    check(!memcmp(before,&plan,sizeof(plan))&&!memcmp(source_before,source,sizeof(*source)));
    tail_unchanged(work,(n+8)*sizeof(*work),(n+12)*sizeof(*work));
    for(unsigned i=0;i<8;++i){uint64_t word;memcpy(&word,work+i,8);check(word==0);}
    emit_integer(&handoff,result.count,4);emit_integer(&handoff,(uint64_t)result.exponent,8);doubles_put(&handoff,result.samples,result.count);
    tracked_free(work);tracked_free(bitrev);tracked_free(trig);
}

static void channel_put(const native_vorbis_packet_frame_t *frame,uint32_t channel) {
    frame_copy_t saved=frame_snapshot(frame);
    uint32_t bins=frame->spectrum_layout.bins,type=frame->floors[channel].state.type;
    double *output=workspace_array(bins+2,sizeof(*output));
    native_vorbis_transform_block_t source={0};
    emit_integer(&handoff,type,4);++channel_total;
    if(type==0){
        ++floor0_total;
        uint16_t *map=workspace_array(bins+2,sizeof(*map));
        native_vorbis_floor0_factor_t *factors=workspace_array(bins+2,sizeof(*factors));
        native_vorbis_floor0_spectrum_plan_t plan;
        prepare_refusal(NULL,channel,map,bins,factors,bins,-1,frame,&saved);
        prepare_refusal(frame,frame->floor_count,map,bins,factors,bins,-1,frame,&saved);
        check(native_vorbis_frame_floor0_prepare(frame,channel,map,bins,factors,bins,&plan)==0);
        check(plan.frame==frame&&plan.channel==channel&&plan.bins==bins&&plan.route<=5);
        if(plan.route==NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE&&!plan.zero){
            prepare_refusal(frame,channel,map,bins-1,factors,bins,-4,frame,&saved);
            prepare_refusal(frame,channel,map,bins,factors,bins-1,-4,frame,&saved);
            prepare_refusal(frame,channel,NULL,bins,factors,bins,-1,frame,&saved);
            prepare_refusal(frame,channel,map,bins,NULL,bins,-1,frame,&saved);
            prepare_refusal(frame,channel,map,SIZE_MAX,factors,bins,-2,frame,&saved);
            prepare_refusal(frame,channel,map,bins,factors,SIZE_MAX,-2,frame,&saved);
        }
        ++route_total[plan.route];
        if(current_case<434)check(plan.route==NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE);
        emit_integer(&handoff,plan.route,4);emit_integer(&handoff,bins,4);
        emit_integer(&handoff,(uint64_t)plan.exponent,8);emit_integer(&handoff,plan.zero,4);emit_integer(&handoff,plan.approximate,4);
        emit_integer(&handoff,plan.gain_evaluations,4);emit_integer(&handoff,plan.minimum_log_fraction_bits,4);emit_integer(&handoff,plan.route_sample,4);
        uint32_t mapped=plan.bark_map?bins:0,fac=plan.factors?bins:0;
        emit_integer(&handoff,mapped,4);for(uint32_t i=0;i<mapped;++i)emit_integer(&handoff,plan.bark_map[i],2);
        emit_integer(&handoff,fac,4);for(uint32_t i=0;i<fac;++i){emit_integer(&handoff,plan.factors[i].mantissa,8);emit_integer(&handoff,(uint64_t)plan.factors[i].exponent,8);}
        tail_unchanged(map,bins*sizeof(*map),(bins+2)*sizeof(*map));tail_unchanged(factors,bins*sizeof(*factors),(bins+2)*sizeof(*factors));
        freeze(map);freeze(factors);
        if(plan.route==NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE){
            unsigned char before[sizeof(plan)];memcpy(before,&plan,sizeof(plan));
            materialize_refusal(NULL,output,bins,-1,frame,&saved,(bins+2)*sizeof(*output));
            materialize_refusal(&plan,NULL,bins,-1,frame,&saved,0);
            materialize_refusal(&plan,output,bins-1,-4,frame,&saved,(bins+2)*sizeof(*output));
            materialize_refusal(&plan,output,SIZE_MAX,-2,frame,&saved,(bins+2)*sizeof(*output));
            check(native_vorbis_frame_floor0_materialize(&plan,output,bins,NULL)==-1);++handoff_refusals;
            tail_unchanged(output,0,(bins+2)*sizeof(*output));frame_unchanged(frame,&saved);
            check(native_vorbis_frame_floor0_materialize(&plan,output,bins,&source)==0);
            check(!memcmp(before,&plan,sizeof(plan)));emit_integer(&handoff,1,4);
        }else{emit_integer(&handoff,0,4);tail_unchanged(output,0,(bins+2)*sizeof(*output));}
        tracked_free(factors);tracked_free(map);
    }else{
        check(type==1);++floor1_total;
        uint8_t *curve=workspace_array(bins,sizeof(*curve));
        native_vorbis_floor1_product_layout_t layout;
        check(native_vorbis_frame_floor1_measure(frame,channel,curve,bins,&layout)==0);
        uint32_t *words=workspace_array(layout.limb_count+2,sizeof(*words));
        native_vorbis_floor1_product_t product;
        check(native_vorbis_frame_floor1_product(frame,channel,curve,bins,words,(size_t)layout.limb_count,&product)==0);
        check(native_vorbis_spectrum_to_binary64(&product,(size_t)layout.limb_count,output,bins,&source)==0);
        tail_unchanged(words,(size_t)layout.limb_count*sizeof(*words),((size_t)layout.limb_count+2)*sizeof(*words));
        emit_integer(&handoff,0,4);emit_integer(&handoff,bins,4);emit_integer(&handoff,(uint64_t)source.exponent,8);
        emit_integer(&handoff,!product.layout.limbs,4);emit_integer(&handoff,0,4);
        emit_integer(&handoff,0,4);emit_integer(&handoff,0,4);emit_integer(&handoff,UINT32_MAX,4);
        emit_integer(&handoff,0,4);emit_integer(&handoff,0,4);emit_integer(&handoff,1,4);
        tracked_free(words);tracked_free(curve);
    }
    if(source.samples){
        check(source.count==bins&&source.samples==output);tail_unchanged(output,bins*sizeof(*output),(bins+2)*sizeof(*output));
        freeze(output);emit_integer(&handoff,source.count,4);emit_integer(&handoff,(uint64_t)source.exponent,8);doubles_put(&handoff,source.samples,source.count);
        transform_put(&source);
    }
    frame_unchanged(frame,&saved);tracked_free(output);frame_snapshot_free(&saved);
}

static native_vorbis_numeric_status_t capture_frame_decode(const native_vorbis_setup_t *setup,
    native_vorbis_packet_t *packet,const native_vorbis_frame_workspace_t *workspace,native_vorbis_packet_frame_t *frame) {
    native_vorbis_numeric_status_t status=native_vorbis_frame_decode(setup,packet,workspace,frame);
    if(status==0&&capture_next){
        capture_next=false;emit_integer(&handoff,current_case,4);emit_integer(&handoff,frame->floor_count,4);
        for(uint32_t channel=0;channel<frame->floor_count;++channel)channel_put(frame,channel);
    }
    return status;
}

int main(int argc,char **argv){
    require(argc==4);FILE *input=fopen(argv[1],"rb"),*front=fopen(argv[2],"wb"),*output=fopen(argv[3],"wb");require(input&&front&&output);
    unsigned char magic[8];require(fread(magic,1,8,input)==8&&!memcmp(magic,"VFRAME01",8));
    uint32_t count=(uint32_t)read_integer(input,4);require(count>=434);
    require(fwrite("VFOUT001",1,8,front)==8&&fwrite("VF0HAND1",1,8,output)==8);
    emitter_t standard={front,UINT64_C(14695981039346656037)};handoff=(emitter_t){output,UINT64_C(14695981039346656037)};
    emit_integer(&standard,count,4);emit_integer(&handoff,count,4);
    for(uint32_t i=0;i<count;++i){current_case=i;capture_next=true;run_case(input,&standard,i);require(!capture_next);}
    require(fgetc(input)==EOF&&!ferror(input));require(fclose(input)==0&&fclose(front)==0&&fclose(output)==0);
    require(!allocations&&!live_allocations&&!live_bytes);
    printf("FLOOR0_HANDOFF cases=%" PRIu32 " channels=%" PRIu64 " floor0=%" PRIu64 " floor1=%" PRIu64 " refusals=%" PRIu64 " checks=%" PRIu64 " live=0 bytes=0\n",count,channel_total,floor0_total,floor1_total,handoff_refusals,checks);
    return 0;
}
