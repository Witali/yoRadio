// Verbatim owned setup host controls; file/heap host driver excluded.
// tests/native/vorbis_setup_test.c SHA256 1757ca2fed27d0c89891deb8ed98ddfd454154a01ddd1cbf60d033b2287fec21
#define SETUP_CONTROL_COUNT 60
static const uint64_t CANARY=UINT64_C(0x34a271e9c065bd8f);
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
static unsigned controls(void){
    unsigned n=0;uint8_t id_packet[32],packet[512];uint64_t extent=baseline(id_packet,packet);native_vorbis_identification_t id;
#define SAME(call,status,object) do{unsigned char saved[sizeof(object)];memcpy(saved,&(object),sizeof(object));assert((call)==(status));assert(!memcmp(saved,&(object),sizeof(object)));n++;}while(0)
    assert(native_vorbis_identification_parse(id_packet,32,233,&id)==0 && id.channels==2 && id.sample_rate==44100 && id.bitrate_nominal_bits==UINT32_MAX && id.blocksize_1==128);n++;
    SAME(native_vorbis_identification_parse(id_packet,32,233,NULL),NATIVE_VORBIS_NUMERIC_INVALID,id);
    SAME(native_vorbis_identification_parse(NULL,32,233,&id),NATIVE_VORBIS_NUMERIC_INVALID,id);
    SAME(native_vorbis_identification_parse(id_packet,32,232,&id),NATIVE_VORBIS_NUMERIC_TRUNCATED,id);
    const unsigned positions[]={0,7,11,12,28,29};
    for(unsigned k=0;k<sizeof(positions)/sizeof(positions[0]);k++){
        uint8_t changed[32];memcpy(changed,id_packet,32);if(k==0)changed[0]=3;else if(k==1)changed[7]=1;else if(k==2)changed[11]=0;else if(k==3)memset(changed+12,0,4);else if(k==4)changed[28]=0x75;else changed[29]=0;
        SAME(native_vorbis_identification_parse(changed,32,233,&id),NATIVE_VORBIS_NUMERIC_INVALID,id);
    }
    native_vorbis_setup_layout_t layout;memset(&layout,0xa5,sizeof(layout));assert(native_vorbis_setup_measure(packet,512,extent,&id,&layout)==0 && layout.book_count==2 && layout.floor_count==2 && layout.mode_count==2);n++;
    SAME(native_vorbis_setup_measure(packet,512,extent,NULL,&layout),NATIVE_VORBIS_NUMERIC_INVALID,layout);
    SAME(native_vorbis_setup_measure(packet,512,extent,&id,NULL),NATIVE_VORBIS_NUMERIC_INVALID,layout);
    SAME(native_vorbis_setup_measure(NULL,512,extent,&id,&layout),NATIVE_VORBIS_NUMERIC_INVALID,layout);
    SAME(native_vorbis_setup_measure(packet,512,extent-1,&id,&layout),NATIVE_VORBIS_NUMERIC_TRUNCATED,layout);
    native_vorbis_identification_t invalid=id;invalid.channels=256;
    SAME(native_vorbis_setup_measure(packet,512,extent,&invalid,&layout),NATIVE_VORBIS_NUMERIC_INVALID,layout);
    invalid=id;invalid.blocksize_0=96;
    SAME(native_vorbis_setup_measure(packet,512,extent,&invalid,&layout),NATIVE_VORBIS_NUMERIC_INVALID,layout);
    struct{uint64_t a;native_vorbis_codebook_t x[2];uint64_t z;} books;struct{uint64_t a;native_vorbis_codeword_t x[4];uint64_t z;} words;
    struct{uint64_t a;uint16_t x[2];uint64_t z;} q;struct{uint64_t a;uint32_t x[128];uint64_t z;} config;native_vorbis_setup_t setup;memset(&setup,0xa5,sizeof(setup));
    memset(&books,0xa5,sizeof(books));memset(&words,0xa5,sizeof(words));memset(&q,0xa5,sizeof(q));memset(&config,0xa5,sizeof(config));books.a=books.z=words.a=words.z=q.a=q.z=config.a=config.z=CANARY;
    assert(layout.codeword_count==4 && layout.multiplicand_count==2 && layout.configuration_count<=128);
    native_vorbis_setup_storage_t storage={books.x,2,words.x,4,q.x,2,config.x,128};
    for(unsigned k=0;k<9;k++){
        native_vorbis_setup_storage_t small=storage;
        if(k==0)small.book_capacity=1;else if(k==1)small.word_capacity=3;else if(k==2)small.multiplicand_capacity=1;else if(k==3)small.configuration_capacity=layout.configuration_count-1;
        else if(k==4)small.books=NULL;else if(k==5)small.words=NULL;else if(k==6)small.multiplicands=NULL;else if(k==7)small.configuration=NULL;
        unsigned char bw[sizeof(books)],ww[sizeof(words)],qw[sizeof(q)],cw[sizeof(config)],sw[sizeof(small)];memcpy(bw,&books,sizeof(books));memcpy(ww,&words,sizeof(words));memcpy(qw,&q,sizeof(q));memcpy(cw,&config,sizeof(config));memcpy(sw,&small,sizeof(small));
        int expected=k<4?NATIVE_VORBIS_NUMERIC_CAPACITY:NATIVE_VORBIS_NUMERIC_INVALID;
        SAME(native_vorbis_setup_materialize(packet,512,extent,k==8?NULL:&layout,&small,&setup),expected,setup);
        assert(!memcmp(bw,&books,sizeof(books))&&!memcmp(ww,&words,sizeof(words))&&!memcmp(qw,&q,sizeof(q))&&!memcmp(cw,&config,sizeof(config))&&!memcmp(sw,&small,sizeof(small)));
    }
    SAME(native_vorbis_setup_materialize(packet,512,extent,&layout,NULL,&setup),NATIVE_VORBIS_NUMERIC_INVALID,setup);
    SAME(native_vorbis_setup_materialize(packet,512,extent,&layout,&storage,NULL),NATIVE_VORBIS_NUMERIC_INVALID,setup);
    native_vorbis_setup_storage_t zero={0};
    SAME(native_vorbis_setup_materialize(packet,512,extent-1,&layout,&zero,&setup),NATIVE_VORBIS_NUMERIC_TRUNCATED,setup);
    packet[0]=7;SAME(native_vorbis_setup_materialize(packet,512,extent,&layout,&zero,&setup),NATIVE_VORBIS_NUMERIC_INVALID,setup);packet[0]=5;
    native_vorbis_setup_layout_t mismatch=layout;mismatch.end_bit++;
    SAME(native_vorbis_setup_materialize(packet,512,extent,&mismatch,&zero,&setup),NATIVE_VORBIS_NUMERIC_INVALID,setup);
    assert(native_vorbis_setup_materialize(packet,512,extent,&layout,&storage,&setup)==0);n++;
    uint32_t type=99;assert(native_vorbis_setup_floor_type(&setup,0,&type)==0 && type==0);n++;
    SAME(native_vorbis_setup_floor_type(&setup,2,&type),NATIVE_VORBIS_NUMERIC_INVALID,type);
    native_vorbis_floor0_setup_t f0;assert(native_vorbis_setup_floor0(&setup,0,&f0)==0 && f0.order==1 && f0.books[0]==1);n++;
    SAME(native_vorbis_setup_floor0(&setup,1,&f0),NATIVE_VORBIS_NUMERIC_INVALID,f0);
    native_vorbis_floor1_setup_t f1;assert(native_vorbis_setup_floor1(&setup,1,&f1)==0 && f1.class_count==1 && f1.post_count==3);n++;
    SAME(native_vorbis_setup_floor1(&setup,0,&f1),NATIVE_VORBIS_NUMERIC_INVALID,f1);
    native_vorbis_floor1_class_t cls;assert(native_vorbis_setup_floor1_class(&setup,&f1,0,&cls)==0 && cls.masterbook==UINT32_MAX && cls.book_count==1 && cls.books[0]==0);n++;
    SAME(native_vorbis_setup_floor1_class(&setup,&f1,1,&cls),NATIVE_VORBIS_NUMERIC_INVALID,cls);
    native_vorbis_residue_setup_t r;assert(native_vorbis_setup_residue(&setup,0,&r)==0 && r.stage_book_count==1 && r.books[0]==1);n++;
    SAME(native_vorbis_setup_residue(&setup,1,&r),NATIVE_VORBIS_NUMERIC_INVALID,r);
    native_vorbis_mapping_setup_t m;assert(native_vorbis_setup_mapping(&setup,0,&m)==0 && m.coupling_count==1 && m.submaps[0]==199);n++;
    SAME(native_vorbis_setup_mapping(&setup,1,&m),NATIVE_VORBIS_NUMERIC_INVALID,m);
    native_vorbis_mode_setup_t mode;assert(native_vorbis_setup_mode(&setup,1,&mode)==0 && mode.blockflag==1);n++;
    SAME(native_vorbis_setup_mode(&setup,2,&mode),NATIVE_VORBIS_NUMERIC_INVALID,mode);
    uint8_t audio=6;native_vorbis_packet_t cursor;native_vorbis_audio_prefix_t prefix;memset(&prefix,0xa5,sizeof(prefix));
    assert(native_vorbis_packet_init(&cursor,&audio,1,4,0)==0);assert(native_vorbis_audio_prefix(&setup,&cursor,&prefix)==0 && prefix.mode==1 && prefix.previous_window==1 && prefix.next_window==0 && prefix.blocksize==128 && cursor.position==4);n++;
    audio=0;assert(native_vorbis_packet_init(&cursor,&audio,1,2,0)==0);assert(native_vorbis_audio_prefix(&setup,&cursor,&prefix)==0 && prefix.mode==0 && !prefix.blockflag && prefix.blocksize==64 && cursor.position==2);n++;
    audio=6;for(uint64_t cut=0;cut<4;cut++){
        assert(native_vorbis_packet_init(&cursor,&audio,1,cut,0)==0);SAME(native_vorbis_audio_prefix(&setup,&cursor,&prefix),NATIVE_VORBIS_NUMERIC_TRUNCATED,prefix);assert(cursor.position==0 && cursor.end_of_packet);
        uint64_t untouched=CANARY;SAME(native_vorbis_packet_read(&cursor,0,&untouched),NATIVE_VORBIS_NUMERIC_TRUNCATED,cursor);assert(untouched==CANARY);
    }
    audio=1;assert(native_vorbis_packet_init(&cursor,&audio,1,4,0)==0);SAME(native_vorbis_audio_prefix(&setup,&cursor,&prefix),NATIVE_VORBIS_NUMERIC_INVALID,prefix);assert(cursor.position==0 && !cursor.end_of_packet);
    SAME(native_vorbis_audio_prefix(NULL,&cursor,&prefix),NATIVE_VORBIS_NUMERIC_INVALID,prefix);
    SAME(native_vorbis_audio_prefix(&setup,NULL,&prefix),NATIVE_VORBIS_NUMERIC_INVALID,prefix);
    SAME(native_vorbis_audio_prefix(&setup,&cursor,NULL),NATIVE_VORBIS_NUMERIC_INVALID,cursor);
    assert(books.a==CANARY&&books.z==CANARY&&words.a==CANARY&&words.z==CANARY&&q.a==CANARY&&q.z==CANARY&&config.a==CANARY&&config.z==CANARY);
#undef SAME
    return n;
}
