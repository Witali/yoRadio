// Verbatim final owned host controls; host file/heap driver excluded.
// tests/native/vorbis_codebook_test.c SHA256 5cb7b8def265b62045721f21895508c6867b51c8d007050d95fb5625c321d44e
#define CODEBOOK_CONTROL_COUNT 719
static const uint64_t CANARY=UINT64_C(0x94e2635b10ca7fd8);
static void write_bits(uint8_t *p,uint64_t *at,uint32_t value,unsigned n){for(unsigned i=0;i<n;i++,(*at)++)if((value>>i)&1)p[*at/8]|=(uint8_t)(1u<<(*at%8));}
static uint64_t fixture(uint8_t *p,const uint32_t *lengths,uint32_t count,uint32_t dim,unsigned lookup,unsigned seq){
    memset(p,0,128);uint64_t at=0;write_bits(p,&at,0x564342,24);write_bits(p,&at,dim,16);write_bits(p,&at,count,24);write_bits(p,&at,0,1);
    unsigned sparse=0;for(uint32_t i=0;i<count;i++)if(!lengths[i])sparse=1;write_bits(p,&at,sparse,1);
    for(uint32_t i=0;i<count;i++){if(sparse)write_bits(p,&at,lengths[i]!=0,1);if(lengths[i])write_bits(p,&at,lengths[i]-1,5);}
    write_bits(p,&at,lookup,4);
    if(lookup){write_bits(p,&at,0x80000000,32);write_bits(p,&at,0x62800001,32);write_bits(p,&at,2,4);write_bits(p,&at,seq,1);if(lookup==1)write_bits(p,&at,7,3);}
    return at;
}
static unsigned controls(void){
    unsigned n=0;uint8_t bytes[9]={0x29,0x81,0x7f,0x55,0xa3,0xe9,0x16,0xc0,0xb7};native_vorbis_packet_t cursor;memset(&cursor,0xa5,sizeof(cursor));uint64_t value=CANARY;
#define SAME(call,status,object) do{unsigned char saved[sizeof(object)];memcpy(saved,&(object),sizeof(object));assert((call)==(status));assert(!memcmp(saved,&(object),sizeof(object)));n++;}while(0)
    for(unsigned start=0;start<8;start++)for(unsigned width=0;width<=64;width++){
        assert(native_vorbis_packet_init(&cursor,bytes,9,72,start)==0);uint64_t wanted=0;
        for(unsigned bit=0;bit<width;bit++)wanted|=(uint64_t)((bytes[(start+bit)/8]>>((start+bit)%8))&1) <<bit;
        assert(native_vorbis_packet_read(&cursor,width,&value)==0 && value==wanted && cursor.position==start+width && !cursor.end_of_packet);n++;
    }
    assert(native_vorbis_packet_init(&cursor,NULL,0,0,0)==0);assert(native_vorbis_packet_read(&cursor,0,&value)==0 && value==0);n++;
    assert(native_vorbis_packet_read(&cursor,1,&value)==NATIVE_VORBIS_NUMERIC_TRUNCATED && cursor.position==0 && cursor.end_of_packet && value==0);n++;
    SAME(native_vorbis_packet_read(&cursor,0,&value),NATIVE_VORBIS_NUMERIC_TRUNCATED,cursor);assert(value==0);
    SAME(native_vorbis_packet_init(&cursor,NULL,1,1,0),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_packet_init(&cursor,bytes,1,9,0),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_packet_init(&cursor,bytes,1,8,9),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_packet_init(NULL,bytes,1,8,0),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    assert(native_vorbis_packet_init(&cursor,bytes,9,72,3)==0);
    SAME(native_vorbis_packet_read(&cursor,65,&value),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_packet_read(&cursor,1,NULL),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_packet_read(NULL,1,&value),NATIVE_VORBIS_NUMERIC_INVALID,value);
    uint8_t setup[128];uint32_t lengths[3]={1,1,0};uint64_t end=fixture(setup,lengths,2,3,1,1);
    struct{uint64_t a;native_vorbis_codebook_layout_t x;uint64_t z;} l;memset(&l,0xa5,sizeof(l));l.a=l.z=CANARY;
    assert(native_vorbis_codebook_measure(setup,128,end,0,&l.x)==0);n++;native_vorbis_codebook_layout_t layout=l.x;
    SAME(native_vorbis_codebook_measure(NULL,1,8,0,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    SAME(native_vorbis_codebook_measure(setup,128,end,0,NULL),NATIVE_VORBIS_NUMERIC_INVALID,l);
    for(uint64_t cut=0;cut<end;cut++)SAME(native_vorbis_codebook_measure(setup,128,cut,0,&l.x),NATIVE_VORBIS_NUMERIC_TRUNCATED,l);
    struct{uint64_t a;native_vorbis_codeword_t x[2];uint64_t z;} w;memset(&w,0xa5,sizeof(w));w.a=w.z=CANARY;
    struct{uint64_t a;uint16_t x[1];uint64_t z;} q;memset(&q,0xa5,sizeof(q));q.a=q.z=CANARY;
    struct{uint64_t a;native_vorbis_codebook_t x;uint64_t z;} b;memset(&b,0xa5,sizeof(b));b.a=b.z=CANARY;
    unsigned char qw[sizeof(q)],ww[sizeof(w)];memcpy(qw,&q,sizeof(q));memcpy(ww,&w,sizeof(w));
    SAME(native_vorbis_codebook_materialize(setup,128,end,NULL,w.x,2,q.x,1,&b.x),NATIVE_VORBIS_NUMERIC_INVALID,b);
    SAME(native_vorbis_codebook_materialize(setup,128,end,&layout,w.x,2,q.x,1,NULL),NATIVE_VORBIS_NUMERIC_INVALID,b);
    SAME(native_vorbis_codebook_materialize(setup,128,end,&layout,w.x,1,q.x,1,&b.x),NATIVE_VORBIS_NUMERIC_CAPACITY,b);assert(!memcmp(qw,&q,sizeof(q))&&!memcmp(ww,&w,sizeof(w)));
    SAME(native_vorbis_codebook_materialize(setup,128,end,&layout,w.x,2,q.x,0,&b.x),NATIVE_VORBIS_NUMERIC_CAPACITY,b);assert(!memcmp(qw,&q,sizeof(q))&&!memcmp(ww,&w,sizeof(w)));
    SAME(native_vorbis_codebook_materialize(setup,128,end-1,&layout,NULL,0,NULL,0,&b.x),NATIVE_VORBIS_NUMERIC_TRUNCATED,b);
    native_vorbis_codebook_layout_t wrong=layout;wrong.maximum_length++;
    SAME(native_vorbis_codebook_materialize(setup,128,end,&wrong,w.x,2,q.x,1,&b.x),NATIVE_VORBIS_NUMERIC_INVALID,b);
    assert(native_vorbis_codebook_materialize(setup,128,end,&layout,w.x,2,q.x,1,&b.x)==0 && q.x[0]==7);n++;native_vorbis_codebook_t book=b.x;
    assert(w.x[0].code==0 && w.x[0].entry==0 && w.x[0].length==1 && w.x[1].code==0x80000000 && w.x[1].entry==1 && w.x[1].length==1);
    uint8_t payload=2;uint32_t entry=0xabcdef;
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);
    SAME(native_vorbis_codebook_decode(NULL,&cursor,&entry),NATIVE_VORBIS_NUMERIC_INVALID,cursor);assert(entry==0xabcdef);
    SAME(native_vorbis_codebook_decode(&book,NULL,&entry),NATIVE_VORBIS_NUMERIC_INVALID,entry);
    SAME(native_vorbis_codebook_decode(&book,&cursor,NULL),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);assert(native_vorbis_codebook_decode(&book,&cursor,&entry)==0 && entry==0 && cursor.position==1);n++;
    assert(native_vorbis_codebook_decode(&book,&cursor,&entry)==0 && entry==1 && cursor.position==2);n++;
    entry=0xabcdef;assert(native_vorbis_codebook_decode(&book,&cursor,&entry)==NATIVE_VORBIS_NUMERIC_TRUNCATED && cursor.position==2 && cursor.end_of_packet && entry==0xabcdef);n++;
    struct{uint64_t a;native_vorbis_affine_t x[255];uint64_t z;} out;memset(&out,0xa5,sizeof(out));out.a=out.z=CANARY;
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);native_vorbis_packet_t before=cursor;
    SAME(native_vorbis_codebook_vector(&book,&cursor,1,NULL,1),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_codebook_floor0_lsp(&book,&cursor,1,NULL,1),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    SAME(native_vorbis_codebook_vector(&book,NULL,1,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    SAME(native_vorbis_codebook_floor0_lsp(&book,NULL,1,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    SAME(native_vorbis_codebook_vector(&book,&cursor,3,out.x,2),NATIVE_VORBIS_NUMERIC_CAPACITY,out);assert(!memcmp(&cursor,&before,sizeof(cursor)));
    assert(native_vorbis_codebook_vector(&book,&cursor,0,NULL,0)==0 && cursor.position==0);n++;
    assert(native_vorbis_codebook_vector(&book,&cursor,3,out.x,255)==0 && cursor.position==1 && out.x[2].minimum_multiplier==3 && out.x[2].delta_multiplier==21);n++;
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);assert(native_vorbis_codebook_floor0_lsp(&book,&cursor,4,out.x,255)==0 && cursor.position==2 && out.x[3].minimum_multiplier==4 && out.x[3].delta_multiplier==28);n++;
    assert(native_vorbis_packet_init(&cursor,&payload,1,1,0)==0);before=cursor;
    SAME(native_vorbis_codebook_floor0_lsp(&book,&cursor,4,out.x,255),NATIVE_VORBIS_NUMERIC_TRUNCATED,out);assert(cursor.position==before.position && cursor.end_of_packet);
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);before=cursor;
    SAME(native_vorbis_codebook_floor0_lsp(&book,&cursor,4,out.x,3),NATIVE_VORBIS_NUMERIC_CAPACITY,out);assert(!memcmp(&cursor,&before,sizeof(cursor)));
    SAME(native_vorbis_codebook_floor0_lsp(&book,&cursor,0,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    SAME(native_vorbis_codebook_floor0_lsp(&book,&cursor,256,out.x,255),NATIVE_VORBIS_NUMERIC_INVALID,out);
    setup[0]^=1;SAME(native_vorbis_codebook_measure(setup,128,end,0,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);setup[0]^=1;
    uint32_t under[2]={2,2},over[3]={1,1,1},single[1]={2};
    end=fixture(setup,under,2,3,0,0);SAME(native_vorbis_codebook_measure(setup,128,end,0,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    end=fixture(setup,over,3,3,0,0);SAME(native_vorbis_codebook_measure(setup,128,end,0,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    end=fixture(setup,single,1,3,0,0);SAME(native_vorbis_codebook_measure(setup,128,end,0,&l.x),NATIVE_VORBIS_NUMERIC_INVALID,l);
    single[0]=1;end=fixture(setup,single,1,3,0,0);assert(native_vorbis_codebook_measure(setup,128,end,0,&layout)==0);assert(native_vorbis_codebook_materialize(setup,128,end,&layout,w.x,2,NULL,0,&b.x)==0);
    for(uint8_t bit=0;bit<2;bit++){assert(native_vorbis_packet_init(&cursor,&bit,1,1,0)==0);assert(native_vorbis_codebook_decode(&b.x,&cursor,&entry)==0 && entry==0 && cursor.position==1);n++;}
    assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);before=cursor;
    SAME(native_vorbis_codebook_vector(&b.x,&cursor,1,out.x,255),NATIVE_VORBIS_NUMERIC_NO_LOOKUP,out);assert(!memcmp(&cursor,&before,sizeof(cursor)));
    uint32_t empty[3]={0,0,0};end=fixture(setup,empty,3,3,0,0);assert(native_vorbis_codebook_measure(setup,128,end,0,&layout)==0 && layout.used_entries==0 && layout.maximum_length==0);assert(native_vorbis_codebook_materialize(setup,128,end,&layout,NULL,0,NULL,0,&b.x)==0);n++;
    entry=0x9fedcba8;uint32_t empty_entry=entry;SAME(native_vorbis_codebook_decode(&b.x,&cursor,&entry),NATIVE_VORBIS_NUMERIC_INVALID,cursor);assert(entry==empty_entry);
    assert(l.a==CANARY&&l.z==CANARY&&w.a==CANARY&&w.z==CANARY&&q.a==CANARY&&q.z==CANARY&&b.a==CANARY&&b.z==CANARY&&out.a==CANARY&&out.z==CANARY);
#undef SAME
    return n;
}
