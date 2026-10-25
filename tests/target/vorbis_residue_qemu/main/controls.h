#define RESIDUE_CONTROL_COUNT 37
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
