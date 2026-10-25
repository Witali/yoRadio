// Copied capture helpers; independent oracle lives in Python.
static const uint64_t CANARY=UINT64_C(0x641bf42c3d8a9705);
typedef struct{unsigned char *base,*data,*before;size_t bytes;} buffer_t;
static buffer_t create(size_t count,size_t unit){assert(unit && count<=(SIZE_MAX-16)/unit);buffer_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);assert(b.base);b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;}
static void copy_before(buffer_t *b){assert(!b->before);b->before=malloc(b->bytes?b->bytes:1);assert(b->before);memcpy(b->before,b->data,b->bytes);}
static void check_buffer(const buffer_t *b,int same){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);assert(a==CANARY && z==CANARY);if(same)assert(b->before && !memcmp(b->before,b->data,b->bytes));}
static void destroy(buffer_t *b){free(b->before);free(b->base);}

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
