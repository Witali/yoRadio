// Actual five-API controls. Driver SHA256 2a8ea35652fe4d668a0ccf78821fa93528559488911f9bf55834c8531013105b
#define FLOOR_PACKET_CONTROL_COUNT 46
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
