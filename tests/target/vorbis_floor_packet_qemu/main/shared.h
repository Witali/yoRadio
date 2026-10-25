// Actual caller-owned capture helpers; no oracle decisions. Driver SHA256 2a8ea35652fe4d668a0ccf78821fa93528559488911f9bf55834c8531013105b
#define FLOOR_PACKET_NATIVE 1
static const uint64_t CANARY=UINT64_C(0x641bf42c3d8a9705);
typedef struct{unsigned char *base,*data,*before;size_t bytes;} buffer_t;
static buffer_t create(size_t count,size_t unit){assert(unit && count<=(SIZE_MAX-16)/unit);buffer_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);assert(b.base);b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;}
static void copy_before(buffer_t *b){assert(!b->before);b->before=malloc(b->bytes?b->bytes:1);assert(b->before);memcpy(b->before,b->data,b->bytes);}
static void check_buffer(const buffer_t *b,int same){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);assert(a==CANARY && z==CANARY);if(same)assert(b->before && !memcmp(b->before,b->data,b->bytes));}
static void destroy(buffer_t *b){free(b->before);free(b->base);}
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
