// Guarded owned residue packets and exact inverse-coupling adapter.
#include "native_vorbis_residue.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint64_t CANARY=UINT64_C(0x641bf42c3d8a9705);
static uint64_t get(FILE *f,unsigned n){uint64_t x=0;for(unsigned i=0;i<n;i++){int c=fgetc(f);assert(c!=EOF);x|=(uint64_t)(unsigned)c<<(8*i);}return x;}
static void put(FILE *f,uint64_t x,unsigned n){for(unsigned i=0;i<n;i++)assert(fputc((int)((x>>(8*i))&255),f)!=EOF);}
typedef struct{unsigned char *base,*data,*before;size_t bytes;} buffer_t;
static buffer_t create(size_t count,size_t unit){assert(unit && count<=(SIZE_MAX-16)/unit);buffer_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);assert(b.base);b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;}
static void copy_before(buffer_t *b){assert(!b->before);b->before=malloc(b->bytes?b->bytes:1);assert(b->before);memcpy(b->before,b->data,b->bytes);}
static void check_buffer(const buffer_t *b,int same){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);assert(a==CANARY && z==CANARY);if(same)assert(b->before && !memcmp(b->before,b->data,b->bytes));}
static void destroy(buffer_t *b){free(b->before);free(b->base);}
static void push(uint8_t *data,uint64_t *at,uint32_t value,unsigned width){assert(width<=32 && *at+width<=4096);for(unsigned i=0;i<width;i++,(*at)++)if((value>>i)&1)data[*at/8]|=(uint8_t)(1u<<(*at%8));}
static uint64_t baseline(uint8_t *id,uint8_t *data,unsigned variant){
    memset(id,0,32);const uint8_t signature[]={1,'v','o','r','b','i','s'};memcpy(id,signature,7);uint64_t at=56;
    push(id,&at,0,32);push(id,&at,2,8);push(id,&at,44100,32);for(unsigned i=0;i<3;i++)push(id,&at,0,32);push(id,&at,6,4);push(id,&at,7,4);push(id,&at,1,1);assert(at==233);
    memset(data,0,512);memcpy(data,signature,7);data[0]=5;at=56;push(data,&at,1,8);
    for(unsigned book=0;book<2;book++){
        push(data,&at,0x564342,24);push(data,&at,1,16);push(data,&at,2,24);push(data,&at,0,1);
        unsigned empty=(variant==2 && book==1)||(variant==3 && book==0);push(data,&at,empty,1);
        if(empty){push(data,&at,0,1);push(data,&at,0,1);}else{push(data,&at,0,5);push(data,&at,0,5);}
        push(data,&at,book,4);if(book){push(data,&at,0,32);push(data,&at,variant==1?0:0x62800001,32);push(data,&at,1,4);push(data,&at,1,1);push(data,&at,1,2);push(data,&at,2,2);}
    }
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,0,6);push(data,&at,1,16);push(data,&at,0,5);push(data,&at,0,2);push(data,&at,4,4);
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,0,24);push(data,&at,variant==5?0:4,24);push(data,&at,0,24);push(data,&at,1,6);push(data,&at,0,8);
    for(unsigned i=0;i<2;i++){push(data,&at,variant==4?0:1,3);push(data,&at,0,1);}if(variant!=4){push(data,&at,1,8);push(data,&at,1,8);}
    push(data,&at,0,6);push(data,&at,0,16);push(data,&at,0,1);push(data,&at,1,1);push(data,&at,0,8);push(data,&at,0,1);push(data,&at,1,1);push(data,&at,0,2);push(data,&at,0,8);push(data,&at,0,8);push(data,&at,0,8);
    push(data,&at,0,6);push(data,&at,0,1);push(data,&at,0,16);push(data,&at,0,16);push(data,&at,0,8);push(data,&at,1,1);return at;
}
// BEGIN_SHARED_RESIDUE_CAPTURE
#ifdef RESIDUE_NATIVE
enum{PACKET_LIMIT=32768,WORD_LIMIT=512,Q_LIMIT=1024,CONFIG_LIMIT=8192,LIMB_LIMIT=4096,CLASS_LIMIT=65536};
#else
enum{PACKET_LIMIT=1048576,WORD_LIMIT=1048576,Q_LIMIT=1048576,CONFIG_LIMIT=262144,LIMB_LIMIT=1048576,CLASS_LIMIT=1048576};
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
    int measure_status,packet_status,coupling_status;
    size_t decoded_count,coupled_count;
    buffer_t layout,state,cursor,scratch,decoded,coupled;
} capture_t;
static void capture_destroy(capture_t *c){buffer_t *all[]={&c->layout,&c->state,&c->cursor,&c->scratch,&c->decoded,&c->coupled};for(size_t i=0;i<sizeof(all)/sizeof(all[0]);i++)destroy(all[i]);memset(c,0,sizeof(*c));}
static void capture_case(context_t *context,const buffer_t *packet,uint64_t bits,uint64_t start,unsigned initial_eop,uint32_t mapping,size_t bins,const buffer_t *flags,capture_t *c){
    memset(c,0,sizeof(*c));c->packet_status=c->coupling_status=-99;assert(packet->bytes<=PACKET_LIMIT && initial_eop<=1 && flags->bytes<=255);
    c->layout=create(1,sizeof(native_vorbis_residue_layout_t));c->state=create(1,sizeof(native_vorbis_residue_packet_t));c->cursor=create(1,sizeof(native_vorbis_packet_t));copy_before(&c->layout);copy_before(&c->state);
    native_vorbis_packet_t *cursor=(void *)c->cursor.data;assert(native_vorbis_packet_init(cursor,packet->data,packet->bytes,bits,start)==0);cursor->end_of_packet=initial_eop!=0;copy_before(&c->cursor);
    native_vorbis_setup_t *setup=context_view(context);native_vorbis_residue_layout_t *layout=(void *)c->layout.data;
    c->measure_status=native_vorbis_residue_measure(setup,mapping,bins,flags->bytes?flags->data:NULL,flags->bytes,layout);
    size_t limbs=0,classes=0;if(!c->measure_status){assert(layout->limb_count<=LIMB_LIMIT && layout->classification_count<=CLASS_LIMIT);limbs=(size_t)layout->limb_count;classes=(size_t)layout->classification_count;refresh(&c->layout);}
    c->scratch=create(classes,1);c->decoded=create(limbs,sizeof(uint32_t));c->coupled=create(limbs,sizeof(uint32_t));copy_before(&c->scratch);copy_before(&c->decoded);copy_before(&c->coupled);
    if(!c->measure_status){
        c->packet_status=native_vorbis_residue_packet(setup,layout,flags->bytes?flags->data:NULL,flags->bytes,cursor,classes?c->scratch.data:NULL,classes,limbs?(void *)c->decoded.data:NULL,limbs,(void *)c->state.data);
        if(!c->packet_status){
            c->decoded_count=limbs;refresh(&c->decoded);refresh(&c->state);memcpy(c->coupled.data,c->decoded.data,c->decoded.bytes);refresh(&c->coupled);
            c->coupling_status=native_vorbis_residue_inverse_coupling(setup,layout,limbs?(void *)c->coupled.data:NULL,limbs);
            if(!c->coupling_status){c->coupled_count=limbs;refresh(&c->coupled);}
        }else{check_buffer(&c->cursor,1);check_buffer(&c->state,1);check_buffer(&c->decoded,1);}
    }else{check_buffer(&c->cursor,1);check_buffer(&c->state,1);}
    check_buffer(&c->layout,1);check_buffer(&c->state,1);check_buffer(&c->decoded,1);check_buffer(&c->coupled,1);check_buffer(&c->scratch,0);check_buffer(&c->cursor,0);check_buffer(packet,1);check_buffer(flags,1);context_check(context);
    assert(cursor->data==packet->data && cursor->bytes==packet->bytes && cursor->bits==bits);
}
// END_SHARED_RESIDUE_CAPTURE
// BEGIN_RESIDUE_CONTROLS
static unsigned controls(void){
    unsigned n=0;uint8_t ip[32],sp[512],wire[32]={0};uint64_t sb=baseline(ip,sp,0);buffer_t id=create(32,1),data=create(512,1);memcpy(id.data,ip,32);memcpy(data.data,sp,512);copy_before(&id);copy_before(&data);context_t context={0};context_prepare(&context,&id,233,&data,sb);native_vorbis_setup_t *setup=context_view(&context);uint8_t flags[2]={1,1};
    struct{native_vorbis_residue_layout_t layout;native_vorbis_packet_t cursor;native_vorbis_residue_packet_t state;uint32_t output[64];uint8_t scratch[64];} b;memset(&b,0xa5,sizeof(b));
#define SAME(call,status) do{unsigned char before[sizeof(b)];memcpy(before,&b,sizeof(b));assert((call)==(status));assert(!memcmp(before,&b,sizeof(b)));n++;}while(0)
#define MEASURE() assert(native_vorbis_residue_measure(setup,0,32,flags,2,&b.layout)==0)
#define CURSOR(extent) assert(native_vorbis_packet_init(&b.cursor,wire,sizeof(wire),(extent),0)==0)
#define DECODE() native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,sizeof(b.scratch),b.output,64,&b.state)
    MEASURE();assert(b.layout.limbs==1 && b.layout.exponent==0 && b.layout.limb_count==64 && b.layout.classification_count==8);n++;
    SAME(native_vorbis_residue_measure(NULL,0,32,flags,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,1,32,flags,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,0,0,flags,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,0,4097,flags,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,0,32,NULL,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,0,32,flags,1,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_measure(setup,0,32,flags,2,NULL),NATIVE_VORBIS_NUMERIC_INVALID);
    flags[0]=2;SAME(native_vorbis_residue_measure(setup,0,32,flags,2,&b.layout),NATIVE_VORBIS_NUMERIC_INVALID);flags[0]=1;
    CURSOR(16);SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,7,b.output,64,&b.state),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,64,b.output,63,&b.state),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,NULL,8,b.output,64,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,64,NULL,64,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_packet(setup,NULL,flags,2,&b.cursor,b.scratch,64,b.output,64,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,NULL,b.scratch,64,b.output,64,&b.state),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,64,b.output,64,NULL),NATIVE_VORBIS_NUMERIC_INVALID);
    b.layout.bins=31;SAME(DECODE(),NATIVE_VORBIS_NUMERIC_INVALID);b.layout.bins=32;
    assert(DECODE()==0 && b.cursor.position==16 && !b.cursor.end_of_packet && !b.state.stopped_on_eop && b.state.classwords==8 && b.state.vectors==8 && b.state.values==8);for(unsigned ch=0;ch<2;ch++)for(unsigned i=0;i<32;i++)assert(b.output[ch*32+i]==(i<4));n++;
    assert(native_vorbis_residue_inverse_coupling(setup,&b.layout,b.output,64)==0);for(unsigned i=0;i<32;i++){assert(b.output[i]==(i<4));assert(!b.output[32+i]);}n++;
    SAME(native_vorbis_residue_inverse_coupling(setup,&b.layout,b.output,63),NATIVE_VORBIS_NUMERIC_CAPACITY);
    SAME(native_vorbis_residue_inverse_coupling(setup,&b.layout,NULL,64),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_inverse_coupling(NULL,&b.layout,b.output,64),NATIVE_VORBIS_NUMERIC_INVALID);
    SAME(native_vorbis_residue_inverse_coupling(setup,NULL,b.output,64),NATIVE_VORBIS_NUMERIC_INVALID);
    assert(b.layout.magnitude_bits<31);b.output[0]=UINT32_C(1)<<b.layout.magnitude_bits;SAME(native_vorbis_residue_inverse_coupling(setup,&b.layout,b.output,64),NATIVE_VORBIS_NUMERIC_INVALID);
    b.output[0]=0U-(UINT32_C(1)<<b.layout.magnitude_bits);SAME(native_vorbis_residue_inverse_coupling(setup,&b.layout,b.output,64),NATIVE_VORBIS_NUMERIC_INVALID);
    const int32_t m[]={1,1,-1,-1},a[]={2,-1,1,-2},left[]={1,0,-1,1},right[]={-1,1,0,-1};for(unsigned k=0;k<4;k++){memset(b.output,0,sizeof(b.output));b.output[0]=(uint32_t)m[k];b.output[32]=(uint32_t)a[k];assert(native_vorbis_residue_inverse_coupling(setup,&b.layout,b.output,64)==0 && b.output[0]==(uint32_t)left[k] && b.output[32]==(uint32_t)right[k]);n++;}
    CURSOR(3);assert(DECODE()==0 && b.cursor.position==3 && b.cursor.end_of_packet && b.state.stopped_on_eop && b.state.classwords==2 && b.state.vectors==1 && b.state.values==1 && b.output[0]==1 && !b.output[32]);n++;
    CURSOR(16);b.cursor.end_of_packet=true;assert(DECODE()==0 && !b.cursor.position && b.cursor.end_of_packet && b.state.stopped_on_eop && !b.state.vectors);for(unsigned i=0;i<64;i++)assert(!b.output[i]);n++;
    flags[0]=flags[1]=0;MEASURE();assert(!b.layout.classification_count);CURSOR(16);b.cursor.end_of_packet=true;assert(DECODE()==0 && !b.cursor.position && b.cursor.end_of_packet && !b.state.stopped_on_eop);n++;flags[0]=flags[1]=1;
    for(unsigned variant=1;variant<=5;variant++){
        sb=baseline(ip,data.data,variant);refresh(&data);context_prepare(&context,&id,233,&data,sb);setup=context_view(&context);MEASURE();CURSOR(32);
        if(variant==2 || variant==3){unsigned char cursor_before[sizeof(b.cursor)],state_before[sizeof(b.state)];uint32_t output_before[64];memcpy(cursor_before,&b.cursor,sizeof(b.cursor));memcpy(state_before,&b.state,sizeof(b.state));memcpy(output_before,b.output,sizeof(b.output));assert(DECODE()==NATIVE_VORBIS_NUMERIC_INVALID && !memcmp(cursor_before,&b.cursor,sizeof(b.cursor)) && !memcmp(state_before,&b.state,sizeof(b.state)) && !memcmp(output_before,b.output,sizeof(b.output)));n++;}
        else if(variant==1 || variant==4){assert(!b.layout.limbs && !b.layout.limb_count && !b.layout.magnitude_bits && !b.layout.exponent);assert(native_vorbis_residue_packet(setup,&b.layout,flags,2,&b.cursor,b.scratch,64,NULL,0,&b.state)==0 && b.cursor.position==(variant==1?16:8) && !b.state.stopped_on_eop);assert(native_vorbis_residue_inverse_coupling(setup,&b.layout,NULL,0)==0);n++;}
        else{b.cursor.end_of_packet=true;assert(DECODE()==0 && !b.cursor.position && b.cursor.end_of_packet && !b.state.stopped_on_eop);n++;}
    }
    context_check(&context);context_destroy(&context);check_buffer(&id,1);check_buffer(&data,1);destroy(&id);destroy(&data);
#undef DECODE
#undef CURSOR
#undef MEASURE
#undef SAME
    return n;
}
// END_RESIDUE_CONTROLS
static void layout_put(FILE *f,const native_vorbis_residue_layout_t *p){put(f,p->mapping,4);put(f,p->bins,4);put(f,p->channels,4);put(f,p->limbs,4);put(f,p->magnitude_bits,4);put(f,(uint32_t)p->exponent,4);put(f,p->sample_count,8);put(f,p->limb_count,8);put(f,p->classification_count,8);}
int main(int argc,char **argv){
    assert(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");assert(in && out);uint8_t magic[8];assert(fread(magic,1,8,in)==8 && !memcmp(magic,"RESTEST1",8));uint32_t count=(uint32_t)get(in,4);assert(count && count<=1000000);
    assert(fwrite("RESOUT01",1,8,out)==8);put(out,count,4);put(out,controls(),4);context_t context={0};
    for(uint32_t index=0;index<count;index++){
        unsigned name=(unsigned)get(in,4);assert(name && name<=63);for(unsigned j=0;j<name;j++){unsigned c=(unsigned)get(in,1);assert((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-');}
        buffer_t packets[3];uint64_t bits[3];for(unsigned j=0;j<3;j++){size_t bytes=(size_t)get(in,4);assert(bytes<=PACKET_LIMIT);packets[j]=create(bytes,1);assert(fread(packets[j].data,1,bytes,in)==bytes);bits[j]=get(in,8);copy_before(&packets[j]);}
        uint64_t start=get(in,8);unsigned initial_eop=(unsigned)get(in,4);uint32_t mapping=(uint32_t)get(in,4),bins=(uint32_t)get(in,4),flag_count=(uint32_t)get(in,4);assert(flag_count<=255);buffer_t flags=create(flag_count,1);assert(fread(flags.data,1,flag_count,in)==flag_count);copy_before(&flags);
        context_prepare(&context,&packets[0],bits[0],&packets[1],bits[1]);capture_t c;capture_case(&context,&packets[2],bits[2],start,initial_eop,mapping,bins,&flags,&c);
        put(out,index,4);put(out,(uint32_t)c.measure_status,4);if(!c.measure_status)layout_put(out,(void *)c.layout.data);put(out,(uint32_t)c.packet_status,4);
        if(!c.packet_status){const native_vorbis_residue_packet_t *s=(void *)c.state.data;put(out,s->classwords,8);put(out,s->vectors,8);put(out,s->values,8);put(out,s->stopped_on_eop,4);}
        put(out,c.decoded_count,4);for(size_t i=0;i<c.decoded_count;i++)put(out,((uint32_t *)c.decoded.data)[i],4);put(out,(uint32_t)c.coupling_status,4);put(out,c.coupled_count,4);for(size_t i=0;i<c.coupled_count;i++)put(out,((uint32_t *)c.coupled.data)[i],4);
        const native_vorbis_packet_t *cursor=(void *)c.cursor.data;put(out,cursor->position,8);put(out,cursor->end_of_packet,4);put(out,7,4);
        check_buffer(&flags,1);destroy(&flags);for(unsigned j=0;j<3;j++){check_buffer(&packets[j],1);destroy(&packets[j]);}capture_destroy(&c);
    }
    context_check(&context);context_destroy(&context);assert(fgetc(in)==EOF);assert(!fclose(in));assert(!fclose(out));return 0;
}
