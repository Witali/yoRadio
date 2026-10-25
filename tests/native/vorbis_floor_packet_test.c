// Owned floor0/floor1 packets and integer floor1-index adapter.
#include "native_vorbis_floor_packet.h"
#include <assert.h>
#include <float.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint64_t CANARY=UINT64_C(0x641bf42c3d8a9705);
_Static_assert(sizeof(native_vorbis_affine_t)==16,"Four exact uint32 fields" );
_Static_assert(sizeof(double)==8 && DBL_MANT_DIG==53,"Binary64 gain capture");
static uint64_t get(FILE *f,unsigned n){uint64_t x=0;for(unsigned i=0;i<n;i++){int c=fgetc(f);assert(c!=EOF);x|=(uint64_t)(unsigned)c<<(8*i);}return x;}
static void put(FILE *f,uint64_t x,unsigned n){for(unsigned i=0;i<n;i++)assert(fputc((int)((x>>(8*i))&255),f)!=EOF);}
typedef struct{unsigned char *base,*data,*before;size_t bytes;} buffer_t;
static buffer_t create(size_t count,size_t unit){assert(unit && count<=(SIZE_MAX-16)/unit);buffer_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);assert(b.base);b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;}
static void copy_before(buffer_t *b){assert(!b->before);b->before=malloc(b->bytes?b->bytes:1);assert(b->before);memcpy(b->before,b->data,b->bytes);}
static void check_buffer(const buffer_t *b,int same){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);assert(a==CANARY && z==CANARY);if(same)assert(b->before && !memcmp(b->before,b->data,b->bytes));}
static void destroy(buffer_t *b){free(b->before);free(b->base);}
static void push(uint8_t *data,uint64_t *at,uint32_t value,unsigned width){assert(width<=32 && *at+width<=4096);for(unsigned i=0;i<width;i++,(*at)++)if((value>>i)&1)data[*at/8]|=(uint8_t)(1u<<(*at%8));}
static uint64_t baseline(uint8_t *id,uint8_t *data){
    memset(id,0,32);const uint8_t signature[]={1,'v','o','r','b','i','s'};memcpy(id,signature,7);uint64_t at=56;
    push(id,&at,0,32);push(id,&at,2,8);push(id,&at,44100,32);push(id,&at,0,32);push(id,&at,UINT32_MAX,32);push(id,&at,UINT32_C(0x80000000),32);push(id,&at,6,4);push(id,&at,7,4);push(id,&at,1,1);assert(at==233);
    memset(data,0,512);memcpy(data,signature,7);data[0]=5;at=56;push(data,&at,1,8);
    for(unsigned book=0;book<2;book++){
        push(data,&at,0x564342,24);push(data,&at,1,16);push(data,&at,2,24);push(data,&at,0,1);push(data,&at,0,1);push(data,&at,0,5);push(data,&at,0,5);push(data,&at,book,4);
        if(book){push(data,&at,0x80000000,32);push(data,&at,0x62800001,32);push(data,&at,2,4);push(data,&at,1,1);push(data,&at,1,3);push(data,&at,2,3);}
    }
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,1,6);
    push(data,&at,0,16);push(data,&at,1,8);push(data,&at,44100,16);push(data,&at,63,16);push(data,&at,6,6);push(data,&at,255,8);push(data,&at,0,4);push(data,&at,1,8);
    push(data,&at,1,16);push(data,&at,1,5);push(data,&at,0,4);push(data,&at,0,3);push(data,&at,0,2);push(data,&at,1,8);push(data,&at,0,2);push(data,&at,4,4);push(data,&at,3,4);
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,0,24);push(data,&at,16,24);push(data,&at,0,24);push(data,&at,0,6);push(data,&at,0,8);push(data,&at,1,3);push(data,&at,0,1);push(data,&at,1,8);
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,0,1);push(data,&at,1,1);push(data,&at,0,8);push(data,&at,0,1);push(data,&at,1,1);push(data,&at,0,2);push(data,&at,199,8);push(data,&at,0,8);push(data,&at,0,8);
    push(data,&at,1,6);for(unsigned mode=0;mode<2;mode++){push(data,&at,mode,1);push(data,&at,0,16);push(data,&at,0,16);push(data,&at,0,8);}push(data,&at,1,1);return at;
}
// BEGIN_SHARED_FLOOR_CAPTURE
#ifdef FLOOR_PACKET_NATIVE
enum{PACKET_LIMIT=32768,WORD_LIMIT=512,Q_LIMIT=1024,CONFIG_LIMIT=8192};
#else
enum{PACKET_LIMIT=1048576,WORD_LIMIT=1048576,Q_LIMIT=1048576,CONFIG_LIMIT=262144};
#endif
enum{CI,CS,CID,CL,CV,CB,CW,CQ,CC,CONTEXT_BUFFERS};
typedef struct{buffer_t b[CONTEXT_BUFFERS];uint64_t id_bits,setup_bits;int ready;} context_t;
static void refresh(buffer_t *b){free(b->before);b->before=NULL;copy_before(b);}
static native_vorbis_setup_t *context_view(context_t *c){return(void *)c->b[CV].data;}
static void context_check(context_t *c){for(unsigned i=0;i<CONTEXT_BUFFERS;i++)check_buffer(&c->b[i],1);}
static void context_destroy(context_t *c){if(c->ready){for(unsigned i=0;i<CONTEXT_BUFFERS;i++)destroy(&c->b[i]);}memset(c,0,sizeof(*c));}
static void context_prepare(context_t *c,const buffer_t *id_data,uint64_t id_bits,const buffer_t *setup_data,uint64_t setup_bits){
    assert(id_data->bytes<=PACKET_LIMIT && setup_data->bytes<=PACKET_LIMIT);
    if(c->ready && c->id_bits==id_bits && c->setup_bits==setup_bits && c->b[CI].bytes==id_data->bytes && c->b[CS].bytes==setup_data->bytes &&
       !memcmp(c->b[CI].data,id_data->data,id_data->bytes) && !memcmp(c->b[CS].data,setup_data->data,setup_data->bytes)){context_check(c);return;}
    if(c->ready){context_check(c);}
    context_destroy(c);c->id_bits=id_bits;c->setup_bits=setup_bits;
    c->b[CI]=create(id_data->bytes,1);memcpy(c->b[CI].data,id_data->data,id_data->bytes);copy_before(&c->b[CI]);
    c->b[CS]=create(setup_data->bytes,1);memcpy(c->b[CS].data,setup_data->data,setup_data->bytes);copy_before(&c->b[CS]);
    c->b[CID]=create(1,sizeof(native_vorbis_identification_t));c->b[CL]=create(1,sizeof(native_vorbis_setup_layout_t));c->b[CV]=create(1,sizeof(native_vorbis_setup_t));
    native_vorbis_identification_t *id=(void *)c->b[CID].data;native_vorbis_setup_layout_t *layout=(void *)c->b[CL].data;
    assert(native_vorbis_identification_parse(c->b[CI].data,c->b[CI].bytes,id_bits,id)==0);copy_before(&c->b[CID]);
    assert(native_vorbis_setup_measure(c->b[CS].data,c->b[CS].bytes,setup_bits,id,layout)==0);copy_before(&c->b[CL]);
    assert(layout->book_count>=1 && layout->book_count<=256 && layout->codeword_count<=WORD_LIMIT && layout->multiplicand_count<=Q_LIMIT && layout->configuration_count<=CONFIG_LIMIT);
    c->b[CB]=create(layout->book_count,sizeof(native_vorbis_codebook_t));c->b[CW]=create((size_t)layout->codeword_count,sizeof(native_vorbis_codeword_t));
    c->b[CQ]=create((size_t)layout->multiplicand_count,sizeof(uint16_t));c->b[CC]=create(layout->configuration_count,sizeof(uint32_t));
    native_vorbis_setup_storage_t storage={(void *)c->b[CB].data,layout->book_count,layout->codeword_count?(void *)c->b[CW].data:NULL,(size_t)layout->codeword_count,
        layout->multiplicand_count?(void *)c->b[CQ].data:NULL,(size_t)layout->multiplicand_count,(void *)c->b[CC].data,layout->configuration_count};
    unsigned char before[sizeof(storage)];memcpy(before,&storage,sizeof(storage));
    assert(native_vorbis_setup_materialize(c->b[CS].data,c->b[CS].bytes,setup_bits,layout,&storage,context_view(c))==0 && !memcmp(before,&storage,sizeof(storage)));
    for(unsigned i=CV;i<CONTEXT_BUFFERS;i++){copy_before(&c->b[i]);}c->ready=1;context_check(c);
}
typedef struct{
    int prefix_status,floor_status,reconstruct_status,curve_status,gain_status;uint32_t gain_consistent;
    size_t coefficient_count,raw_count,final_count,active_count,index_count;
    buffer_t prefix,state,coefficients,raw_y,final_y,active,indices,gain,cursor;
} capture_t;
static uint64_t double_bits(double value){uint64_t bits;memcpy(&bits,&value,8);return bits;}
static int same_gain(const native_vorbis_floor0_gain_t *a,const native_vorbis_floor0_gain_t *b){return a->kind==b->kind && double_bits(a->log2_gain.mantissa)==double_bits(b->log2_gain.mantissa) && a->log2_gain.exponent==b->log2_gain.exponent;}
static void capture_destroy(capture_t *c){buffer_t *all[]={&c->prefix,&c->state,&c->coefficients,&c->raw_y,&c->final_y,&c->active,&c->indices,&c->gain,&c->cursor};for(size_t i=0;i<sizeof(all)/sizeof(all[0]);i++)destroy(all[i]);memset(c,0,sizeof(*c));}
static void capture_case(context_t *context,unsigned operation,const buffer_t *packet,uint64_t bits,uint64_t start,uint32_t floor_index,size_t bins,const uint32_t *raw,size_t raw_count,capture_t *c){
    memset(c,0,sizeof(*c));c->prefix_status=c->floor_status=c->reconstruct_status=c->curve_status=c->gain_status=-99;
    assert(operation>=1 && operation<=2 && packet->bytes<=PACKET_LIMIT && raw_count<=256);native_vorbis_setup_t *setup=context_view(context);uint32_t type=99;
    assert(native_vorbis_setup_floor_type(setup,floor_index,&type)==0);size_t coefficient_capacity=0,raw_capacity=raw_count;native_vorbis_floor0_setup_t f0={0};native_vorbis_floor1_setup_t f1={0};
    if(type==0){assert(native_vorbis_setup_floor0(setup,floor_index,&f0)==0);if(operation==1)coefficient_capacity=f0.order;}
    else{assert(type==1 && native_vorbis_setup_floor1(setup,floor_index,&f1)==0);if(operation==1)raw_capacity=f1.post_count;}
    c->prefix=create(1,sizeof(native_vorbis_audio_prefix_t));c->state=create(1,sizeof(native_vorbis_floor_packet_t));c->cursor=create(1,sizeof(native_vorbis_packet_t));
    c->coefficients=create(coefficient_capacity,sizeof(native_vorbis_affine_t));c->raw_y=create(raw_capacity,sizeof(uint32_t));c->final_y=create(raw_capacity,sizeof(uint32_t));c->active=create(raw_capacity,1);
    c->indices=create(bins<=4096?bins:0,1);c->gain=create(1,sizeof(native_vorbis_floor0_gain_t));
    buffer_t *outputs[]={&c->prefix,&c->state,&c->coefficients,&c->raw_y,&c->final_y,&c->active,&c->indices,&c->gain};
    for(size_t i=0;i<sizeof(outputs)/sizeof(outputs[0]);i++)copy_before(outputs[i]);
    native_vorbis_packet_t *cursor=(void *)c->cursor.data;*cursor=(native_vorbis_packet_t){packet->data,packet->bytes,bits,start,false};
    native_vorbis_floor_packet_t *state=(void *)c->state.data;
    if(operation==1){
        c->prefix_status=native_vorbis_packet_init(cursor,packet->data,packet->bytes,bits,start);
        if(c->prefix_status==0)c->prefix_status=native_vorbis_audio_prefix(setup,cursor,(void *)c->prefix.data);
        if(c->prefix_status){check_buffer(&c->prefix,1);assert(cursor->position==start && cursor->end_of_packet==(c->prefix_status==NATIVE_VORBIS_NUMERIC_TRUNCATED));}
        else{
            refresh(&c->prefix);unsigned char before[sizeof(*cursor)];memcpy(before,cursor,sizeof(*cursor));
            if(type==0)c->floor_status=native_vorbis_floor0_packet(setup,floor_index,cursor,coefficient_capacity?(void *)c->coefficients.data:NULL,coefficient_capacity,state);
            else c->floor_status=native_vorbis_floor1_packet(setup,floor_index,cursor,(void *)c->raw_y.data,raw_capacity,state);
            if(c->floor_status){assert(!memcmp(before,cursor,sizeof(*cursor)));check_buffer(&c->state,1);}
            else{
                refresh(&c->state);
                if(state->present){
                    if(type==0){assert(state->value_count<=coefficient_capacity);c->coefficient_count=state->value_count;refresh(&c->coefficients);}
                    else{assert(state->value_count<=raw_capacity);c->raw_count=state->value_count;refresh(&c->raw_y);}
                }
            }
        }
    }else{if(raw_count)memcpy(c->raw_y.data,raw,raw_count*sizeof(*raw));refresh(&c->raw_y);c->raw_count=raw_count;}
    if(operation==2 || (c->floor_status==0 && state->present && type==1)){
        c->reconstruct_status=native_vorbis_floor1_reconstruct(setup,floor_index,(void *)c->raw_y.data,c->raw_count,(void *)c->final_y.data,c->active.data,raw_capacity);
        if(c->reconstruct_status==0){c->final_count=c->active_count=c->raw_count;refresh(&c->final_y);refresh(&c->active);
            c->curve_status=native_vorbis_floor1_curve(setup,floor_index,(void *)c->final_y.data,c->active.data,c->raw_count,c->indices.data,bins,c->indices.bytes);
            if(c->curve_status==0)c->index_count=bins;
        }
    }
    if(operation==1 && c->floor_status==0 && type==0){
        c->gain_status=native_vorbis_floor0_packet_gain(setup,floor_index,state,c->coefficient_count?(void *)c->coefficients.data:NULL,c->coefficient_count,0,(void *)c->gain.data);
        if(c->gain_status==0){native_vorbis_floor0_gain_t expected;int status;
            if(!state->present){native_vorbis_floor0_amplitude_t absent={0,f0.amplitude_bits,f0.amplitude_offset};status=native_vorbis_floor0_gain_from_denominator(&absent,NULL,&expected);}
            else if(!f0.order){native_vorbis_scaled_t one={0.5,1};status=native_vorbis_floor0_gain_from_denominator(&state->amplitude,&one,&expected);}
            else status=native_vorbis_floor0_gain_from_affine(&state->amplitude,(void *)c->coefficients.data,c->coefficient_count,0,f0.bark_map_size,&expected);
            c->gain_consistent=(uint32_t)(status==0 && same_gain((void *)c->gain.data,&expected));refresh(&c->gain);
        }
    }
    check_buffer(&c->prefix,1);check_buffer(&c->state,1);check_buffer(&c->coefficients,1);check_buffer(&c->raw_y,1);check_buffer(&c->final_y,1);check_buffer(&c->active,1);
    check_buffer(&c->indices,c->curve_status!=0);check_buffer(&c->gain,1);check_buffer(&c->cursor,0);check_buffer(packet,1);context_check(context);
    assert(cursor->data==packet->data && cursor->bytes==packet->bytes && cursor->bits==bits);
}
// END_SHARED_FLOOR_CAPTURE
// BEGIN_FLOOR_CONTROLS
static void overwrite(uint8_t *p,uint64_t at,uint32_t value,unsigned width){for(unsigned i=0;i<width;i++){uint8_t mask=(uint8_t)(1u<<((at+i)%8));p[(at+i)/8]=(uint8_t)((p[(at+i)/8]&~mask)|(((value>>i)&1)?mask:0));}}
static uint64_t zero_setup(uint8_t *p){
    memset(p,0,512);const uint8_t sig[]={5,'v','o','r','b','i','s'};memcpy(p,sig,7);uint64_t at=56;push(p,&at,0,8);
    push(p,&at,0x564342,24);push(p,&at,1,16);push(p,&at,1,24);push(p,&at,0,1);push(p,&at,1,1);push(p,&at,0,1);push(p,&at,0,4);
    push(p,&at,0,6);push(p,&at,0,16);push(p,&at,0,6);push(p,&at,1,16);push(p,&at,1,5);push(p,&at,0,4);push(p,&at,0,3);push(p,&at,0,2);push(p,&at,1,8);push(p,&at,0,2);push(p,&at,4,4);push(p,&at,3,4);
    push(p,&at,0,6);push(p,&at,0,16);push(p,&at,0,24);push(p,&at,0,24);push(p,&at,0,24);push(p,&at,0,6);push(p,&at,0,8);push(p,&at,0,3);push(p,&at,0,1);
    push(p,&at,0,6);push(p,&at,0,16);push(p,&at,0,1);push(p,&at,0,1);push(p,&at,0,2);push(p,&at,0,8);push(p,&at,0,8);push(p,&at,0,8);
    push(p,&at,0,6);push(p,&at,0,1);push(p,&at,0,16);push(p,&at,0,16);push(p,&at,0,8);push(p,&at,1,1);return at;
}
static unsigned controls(void){
    unsigned n=0;uint8_t ip[32],sp[512],wire[512]={0};uint64_t sb=baseline(ip,sp);buffer_t id=create(32,1),data=create(512,1);memcpy(id.data,ip,32);memcpy(data.data,sp,512);copy_before(&id);copy_before(&data);context_t context={0};context_prepare(&context,&id,233,&data,sb);native_vorbis_setup_t *setup=context_view(&context);
    struct{native_vorbis_packet_t cursor;native_vorbis_floor_packet_t state;native_vorbis_affine_t coefficients[1];uint32_t raw[3],final[3];uint8_t active[3],indices[32];native_vorbis_floor0_gain_t gain;} b;memset(&b,0xa5,sizeof(b));
#define SAME(call,status) do{unsigned char before[sizeof(b)];memcpy(before,&b,sizeof(b));assert((call)==(status));assert(!memcmp(before,&b,sizeof(b)));n++;}while(0)
#define CURSOR(extent) assert(native_vorbis_packet_init(&b.cursor,wire,sizeof(wire),(extent),0)==0)
    wire[0]=31;CURSOR(8);assert(native_vorbis_floor0_packet(setup,0,&b.cursor,b.coefficients,1,&b.state)==0 && b.state.present==1 && b.state.value_count==1 && b.state.selected_book==1 && b.state.amplitude.raw_amplitude==31 && b.cursor.position==8);n++;
    native_vorbis_floor0_gain_t expected;assert(native_vorbis_floor0_packet_gain(setup,0,&b.state,b.coefficients,1,0,&b.gain)==0 && native_vorbis_floor0_gain_from_affine(&b.state.amplitude,b.coefficients,1,0,63,&expected)==0 && same_gain(&b.gain,&expected));n++;
    SAME(native_vorbis_floor0_packet_gain(setup,0,&b.state,b.coefficients,0,0,&b.gain),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor0_packet_gain(setup,0,&b.state,b.coefficients,1,63,&b.gain),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor0_packet_gain(setup,0,&b.state,b.coefficients,1,0,NULL),NATIVE_VORBIS_NUMERIC_INVALID);
    for(unsigned k=0;k<4;k++){
        wire[0]=k?31:0;uint64_t extent=k==0?6:k==1?5:k==2?6:7;CURSOR(extent);native_vorbis_affine_t unchanged=b.coefficients[0];
        assert(native_vorbis_floor0_packet(setup,0,&b.cursor,b.coefficients,1,&b.state)==0 && !b.state.present && !b.state.value_count && b.state.amplitude.amplitude_bits==6 && b.state.amplitude.amplitude_offset==255 && !memcmp(&unchanged,b.coefficients,sizeof(unchanged)));
        assert(b.cursor.position==(k==0?6:k==1?0:k==2?6:7) && b.cursor.end_of_packet==(k!=0) && b.state.amplitude.raw_amplitude==(k<2?0:31) && b.state.selected_book==(k==3?1:UINT32_MAX));n++;
    }
    assert(native_vorbis_floor0_packet_gain(setup,0,&b.state,NULL,0,UINT32_MAX,&b.gain)==0 && b.gain.kind==NATIVE_VORBIS_FLOOR0_ABSENT);n++;
    wire[0]=95;CURSOR(7);SAME(native_vorbis_floor0_packet(setup,0,&b.cursor,b.coefficients,1,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    wire[0]=31;CURSOR(6);SAME(native_vorbis_floor0_packet(setup,0,&b.cursor,NULL,0,&b.state),NATIVE_VORBIS_NUMERIC_CAPACITY);
    CURSOR(8);SAME(native_vorbis_floor0_packet(setup,0,&b.cursor,NULL,1,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor0_packet(setup,1,&b.cursor,b.coefficients,1,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor0_packet(setup,0,NULL,b.coefficients,1,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor0_packet(setup,0,&b.cursor,b.coefficients,1,NULL),NATIVE_VORBIS_NUMERIC_INVALID);
    memset(wire,0,sizeof(wire));uint64_t at=0;push(wire,&at,1,1);push(wire,&at,128,8);push(wire,&at,128,8);push(wire,&at,0,1);assert(at==18);CURSOR(at);
    assert(native_vorbis_floor1_packet(setup,1,&b.cursor,b.raw,3,&b.state)==0 && b.state.present && b.state.value_count==3 && b.state.selected_book==UINT32_MAX && b.raw[0]==128 && b.raw[1]==128 && b.raw[2]==0 && b.cursor.position==18);n++;
    assert(native_vorbis_floor1_reconstruct(setup,1,b.raw,3,b.final,b.active,3)==0 && b.final[0]==128 && b.final[1]==128 && b.final[2]==128 && b.active[0]==1 && b.active[1]==1 && !b.active[2]);n++;
    assert(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,32,32)==0);for(unsigned i=0;i<32;i++)assert(b.indices[i]==128);n++;
    SAME(native_vorbis_floor1_reconstruct(setup,1,b.raw,2,b.final,b.active,3),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_reconstruct(setup,1,b.raw,3,b.final,b.active,2),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_floor1_reconstruct(setup,1,NULL,3,b.final,b.active,3),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_reconstruct(setup,1,b.raw,3,NULL,b.active,3),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_reconstruct(setup,1,b.raw,3,b.final,NULL,3),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,32,31),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,0,32),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,4097,32),NATIVE_VORBIS_NUMERIC_INVALID);
    b.active[2]=2;SAME(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,32,32),NATIVE_VORBIS_NUMERIC_INVALID);b.active[2]=0;
    b.final[2]=256;SAME(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,32,32),NATIVE_VORBIS_NUMERIC_INVALID);b.final[2]=128;
    const unsigned cuts[]={0,1,9,17};for(unsigned i=0;i<4;i++){uint32_t before[3];memcpy(before,b.raw,sizeof(before));CURSOR(cuts[i]);assert(native_vorbis_floor1_packet(setup,1,&b.cursor,b.raw,3,&b.state)==0 && !b.state.present && !b.state.value_count && b.cursor.end_of_packet && b.cursor.position==cuts[i] && !memcmp(before,b.raw,sizeof(before)));n++;}
    wire[0]=0;CURSOR(1);assert(native_vorbis_floor1_packet(setup,1,&b.cursor,NULL,0,&b.state)==0 && !b.state.present && b.cursor.position==1 && !b.cursor.end_of_packet);n++;
    wire[0]=1;CURSOR(1);SAME(native_vorbis_floor1_packet(setup,1,&b.cursor,NULL,0,&b.state),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_floor1_packet(setup,1,&b.cursor,NULL,3,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_packet(setup,0,&b.cursor,b.raw,3,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_packet(setup,1,NULL,b.raw,3,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_floor1_packet(setup,1,&b.cursor,b.raw,3,NULL),NATIVE_VORBIS_NUMERIC_INVALID);
    b.raw[0]=UINT32_MAX;b.raw[1]=0;b.raw[2]=UINT32_MAX;assert(native_vorbis_floor1_reconstruct(setup,1,b.raw,3,b.final,b.active,3)==0 && b.final[0]==255 && !b.final[1] && !b.final[2] && b.active[2]);n++;
    assert(native_vorbis_floor1_curve(setup,1,b.final,b.active,3,b.indices,32,32)==0 && b.indices[0]==255 && b.indices[1]==170 && b.indices[2]==85);for(unsigned i=3;i<32;i++)assert(!b.indices[i]);n++;
    uint64_t order_bit=setup->books[1].layout.quantization.end_bit+44;overwrite(data.data,order_bit,0,8);refresh(&data);context_prepare(&context,&id,233,&data,sb);setup=context_view(&context);
    wire[0]=31;CURSOR(8);assert(native_vorbis_floor0_packet(setup,0,&b.cursor,NULL,0,&b.state)==0 && b.state.present && !b.state.value_count && b.cursor.position==8 && b.state.selected_book==1);n++;
    native_vorbis_scaled_t one={0.5,1};assert(native_vorbis_floor0_packet_gain(setup,0,&b.state,NULL,0,0,&b.gain)==0 && native_vorbis_floor0_gain_from_denominator(&b.state.amplitude,&one,&expected)==0 && same_gain(&b.gain,&expected));n++;
    uint64_t zero_bits=zero_setup(data.data);refresh(&data);context_prepare(&context,&id,233,&data,zero_bits);setup=context_view(&context);assert(!setup->books[0].words && !setup->books[0].quantization.multiplicands);n++;
    wire[0]=0;CURSOR(1);assert(native_vorbis_floor1_packet(setup,0,&b.cursor,NULL,0,&b.state)==0 && !b.state.present && b.cursor.position==1);n++;
    memset(wire,0,sizeof(wire));at=0;push(wire,&at,1,1);push(wire,&at,128,8);push(wire,&at,128,8);CURSOR(at);SAME(native_vorbis_floor1_packet(setup,0,&b.cursor,b.raw,3,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    context_check(&context);context_destroy(&context);check_buffer(&id,1);check_buffer(&data,1);destroy(&id);destroy(&data);
#undef CURSOR
#undef SAME
    return n;
}
// END_FLOOR_CONTROLS
static void prefix_put(FILE *f,const native_vorbis_audio_prefix_t *p){put(f,p->mode,4);put(f,p->blockflag,4);put(f,p->previous_window,4);put(f,p->next_window,4);put(f,p->mapping,4);put(f,p->blocksize,4);}
static void state_put(FILE *f,const native_vorbis_floor_packet_t *s){put(f,s->floor_index,4);put(f,s->type,4);put(f,s->present,4);put(f,s->value_count,4);put(f,s->selected_book,4);put(f,s->amplitude.raw_amplitude,8);put(f,s->amplitude.amplitude_bits,4);put(f,s->amplitude.amplitude_offset,4);}
int main(int argc,char **argv){
    assert(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");assert(in && out);uint8_t magic[8];assert(fread(magic,1,8,in)==8 && !memcmp(magic,"FLRTEST1",8));uint32_t count=(uint32_t)get(in,4);assert(count && count<=1000000);
    assert(fwrite("FLROUT01",1,8,out)==8);put(out,count,4);put(out,controls(),4);context_t context={0};
    for(uint32_t index=0;index<count;index++){
        unsigned name=(unsigned)get(in,4);assert(name && name<=63);for(unsigned j=0;j<name;j++){unsigned c=(unsigned)get(in,1);assert((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-');}
        unsigned operation=(unsigned)get(in,4);buffer_t packets[3];uint64_t bits[3];for(unsigned j=0;j<3;j++){size_t bytes=(size_t)get(in,4);assert(bytes<=PACKET_LIMIT);packets[j]=create(bytes,1);assert(fread(packets[j].data,1,bytes,in)==bytes);bits[j]=get(in,8);copy_before(&packets[j]);}
        uint64_t start=get(in,8);uint32_t floor_index=(uint32_t)get(in,4),bins=(uint32_t)get(in,4),raw_count=(uint32_t)get(in,4);assert(raw_count<=256);buffer_t raw=create(raw_count,sizeof(uint32_t));for(unsigned j=0;j<raw_count;j++)((uint32_t *)raw.data)[j]=(uint32_t)get(in,4);copy_before(&raw);
        context_prepare(&context,&packets[0],bits[0],&packets[1],bits[1]);capture_t c;capture_case(&context,operation,&packets[2],bits[2],start,floor_index,bins,(void *)raw.data,raw_count,&c);
        put(out,index,4);put(out,(uint32_t)c.prefix_status,4);if(!c.prefix_status)prefix_put(out,(void *)c.prefix.data);put(out,(uint32_t)c.floor_status,4);if(!c.floor_status)state_put(out,(void *)c.state.data);
        put(out,c.coefficient_count,4);for(size_t i=0;i<c.coefficient_count;i++){const native_vorbis_affine_t *a=(void *)c.coefficients.data;put(out,a[i].minimum_bits,4);put(out,a[i].delta_bits,4);put(out,a[i].minimum_multiplier,4);put(out,a[i].delta_multiplier,4);}
        put(out,c.raw_count,4);for(size_t i=0;i<c.raw_count;i++)put(out,((uint32_t *)c.raw_y.data)[i],4);put(out,(uint32_t)c.reconstruct_status,4);
        put(out,c.final_count,4);for(size_t i=0;i<c.final_count;i++)put(out,((uint32_t *)c.final_y.data)[i],4);put(out,c.active_count,4);for(size_t i=0;i<c.active_count;i++)put(out,c.active.data[i],1);
        put(out,(uint32_t)c.curve_status,4);put(out,c.index_count,4);for(size_t i=0;i<c.index_count;i++)put(out,c.indices.data[i],1);put(out,(uint32_t)c.gain_status,4);
        if(!c.gain_status){const native_vorbis_floor0_gain_t *g=(void *)c.gain.data;put(out,g->kind,4);put(out,double_bits(g->log2_gain.mantissa),8);put(out,(uint32_t)g->log2_gain.exponent,4);}put(out,c.gain_consistent,4);
        const native_vorbis_packet_t *cursor=(void *)c.cursor.data;put(out,cursor->position,8);put(out,cursor->end_of_packet,4);put(out,7,4);
        check_buffer(&raw,1);destroy(&raw);for(unsigned j=0;j<3;j++){check_buffer(&packets[j],1);destroy(&packets[j]);}capture_destroy(&c);
    }
    context_check(&context);context_destroy(&context);assert(fgetc(in)==EOF);assert(!fclose(in));assert(!fclose(out));return 0;
}
