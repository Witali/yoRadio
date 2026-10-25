// Full setup adapter. capture_getters is shared as test-only capture code.
#include "native_vorbis_setup.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint64_t CANARY=UINT64_C(0x34a271e9c065bd8f);
static void getter_append(uint32_t *out,size_t capacity,size_t *count,uint32_t value){assert(*count<capacity);out[(*count)++]=value;}
static size_t capture_getters(const native_vorbis_setup_t *setup,uint32_t *out,size_t capacity){
    size_t n=0;
#define EMIT(value) getter_append(out,capacity,&n,(value))
#define ARRAY(values,count) do{for(size_t j_=0;j_<(size_t)(count);j_++){EMIT((values)[j_]);}}while(0)
    for(uint32_t i=0;i<setup->layout.floor_count;i++){
        uint32_t type=99;assert(native_vorbis_setup_floor_type(setup,i,&type)==0);EMIT(type);
        if(type==0){native_vorbis_floor0_setup_t f;assert(native_vorbis_setup_floor0(setup,i,&f)==0);
            EMIT(f.order);EMIT(f.rate);EMIT(f.bark_map_size);EMIT(f.amplitude_bits);EMIT(f.amplitude_offset);EMIT(f.book_count);ARRAY(f.books,f.book_count);
        }else{assert(type==1);native_vorbis_floor1_setup_t f;assert(native_vorbis_setup_floor1(setup,i,&f)==0);
            EMIT(f.partition_count);EMIT(f.class_count);EMIT(f.multiplier);EMIT(f.range_bits);EMIT(f.post_count);
            ARRAY(f.partitions,f.partition_count);ARRAY(f.class_offsets,f.class_count);ARRAY(f.x,f.post_count);
            for(uint32_t c=0;c<f.class_count;c++){native_vorbis_floor1_class_t cls;assert(native_vorbis_setup_floor1_class(setup,&f,c,&cls)==0);
                EMIT(cls.dimensions);EMIT(cls.subclass_bits);EMIT(cls.masterbook);EMIT(cls.book_count);ARRAY(cls.books,cls.book_count);}
        }
    }
    for(uint32_t i=0;i<setup->layout.residue_count;i++){native_vorbis_residue_setup_t r;assert(native_vorbis_setup_residue(setup,i,&r)==0);
        EMIT(r.type);EMIT(r.begin);EMIT(r.end);EMIT(r.partition_size);EMIT(r.classifications);EMIT(r.classbook);EMIT(r.stage_book_count);
        ARRAY(r.cascades,r.classifications);ARRAY(r.book_offsets,r.classifications);ARRAY(r.books,r.stage_book_count);}
    for(uint32_t i=0;i<setup->layout.mapping_count;i++){native_vorbis_mapping_setup_t m;assert(native_vorbis_setup_mapping(setup,i,&m)==0);
        EMIT(m.submap_count);EMIT(m.coupling_count);EMIT(m.channels);ARRAY(m.coupling_pairs,2*m.coupling_count);ARRAY(m.mux,m.channels);ARRAY(m.submaps,3*m.submap_count);}
    for(uint32_t i=0;i<setup->layout.mode_count;i++){native_vorbis_mode_setup_t m;assert(native_vorbis_setup_mode(setup,i,&m)==0);EMIT(m.blockflag);EMIT(m.mapping);}
#undef ARRAY
#undef EMIT
    return n;
}
static uint64_t get(FILE *f,unsigned n){uint64_t x=0;for(unsigned i=0;i<n;i++){int c=fgetc(f);assert(c!=EOF);x|=(uint64_t)(unsigned)c<<(8*i);}return x;}
static void put(FILE *f,uint64_t x,unsigned n){for(unsigned i=0;i<n;i++)assert(fputc((int)((x>>(8*i))&255),f)!=EOF);}
typedef struct{unsigned char *base,*data,*before;size_t bytes;} buffer_t;
static buffer_t create(size_t count,size_t unit){assert(unit && count<=(SIZE_MAX-16)/unit);buffer_t b={0};b.bytes=count*unit;b.base=malloc(b.bytes+16);assert(b.base);b.data=b.base+8;memcpy(b.base,&CANARY,8);memcpy(b.data+b.bytes,&CANARY,8);memset(b.data,0xa5,b.bytes);return b;}
static void copy_before(buffer_t *b){assert(!b->before);b->before=malloc(b->bytes?b->bytes:1);assert(b->before);memcpy(b->before,b->data,b->bytes);}
static void check_buffer(const buffer_t *b,int same){uint64_t a,z;memcpy(&a,b->base,8);memcpy(&z,b->data+b->bytes,8);assert(a==CANARY && z==CANARY);if(same)assert(b->before && !memcmp(b->before,b->data,b->bytes));}
static void destroy(buffer_t *b){free(b->before);free(b->base);}
static void id_put(FILE *f,const native_vorbis_identification_t *id){put(f,id->channels,4);put(f,id->sample_rate,4);put(f,id->bitrate_maximum_bits,4);put(f,id->bitrate_nominal_bits,4);put(f,id->bitrate_minimum_bits,4);put(f,id->blocksize_0,4);put(f,id->blocksize_1,4);}
static void layout_put(FILE *f,const native_vorbis_setup_layout_t *l){
    id_put(f,&l->identification);put(f,l->end_bit,8);put(f,l->codeword_count,8);put(f,l->multiplicand_count,8);
    put(f,l->book_count,4);put(f,l->time_count,4);put(f,l->floor_count,4);put(f,l->residue_count,4);put(f,l->mapping_count,4);put(f,l->mode_count,4);put(f,l->configuration_count,4);
    put(f,l->floor_table,4);put(f,l->residue_table,4);put(f,l->mapping_table,4);put(f,l->mode_table,4);
}
static void book_put(FILE *f,const native_vorbis_codebook_t *b){
    const native_vorbis_codebook_layout_t *l=&b->layout;const native_vorbis_quant_layout_t *q=&l->quantization;
    put(f,l->start_bit,8);put(f,l->used_entries,4);put(f,l->maximum_length,4);
    put(f,q->dimensions,4);put(f,q->entries,4);put(f,q->lookup_type,4);put(f,q->minimum_bits,4);put(f,q->delta_bits,4);put(f,q->value_bits,4);put(f,q->sequence_p,4);
    put(f,q->multiplicand_count,8);put(f,q->start_bit,8);put(f,q->multiplicand_bit,8);put(f,q->end_bit,8);
    put(f,b->word_count,4);for(size_t i=0;i<b->word_count;i++){put(f,b->words[i].code,4);put(f,b->words[i].entry,4);put(f,b->words[i].length,4);}
    put(f,b->quantization.storage_count,4);for(size_t i=0;i<b->quantization.storage_count;i++)put(f,b->quantization.multiplicands[i],2);
}
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
int main(int argc,char **argv){
    assert(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");assert(in && out);uint8_t magic[8];assert(fread(magic,1,8,in)==8 && !memcmp(magic,"SETTEST1",8));
    uint32_t count=(uint32_t)get(in,4);assert(count>0 && count<=10000);assert(fwrite("SETOUT01",1,8,out)==8);put(out,count,4);put(out,controls(),4);
    for(uint32_t index=0;index<count;index++){
        unsigned name=(unsigned)get(in,4);assert(name>=1 && name<=63);for(unsigned j=0;j<name;j++){unsigned c=(unsigned)get(in,1);assert((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-');}
        buffer_t packets[3];uint64_t bits[3];
        for(unsigned j=0;j<3;j++){size_t bytes=(size_t)get(in,4);assert(bytes<=1048576);packets[j]=create(bytes,1);assert(fread(packets[j].data,1,bytes,in)==bytes);bits[j]=get(in,8);copy_before(&packets[j]);}
        uint64_t start=get(in,8),position=start,id_cuts=0,setup_cuts=0,audio_cuts=0;unsigned eop=0;
        buffer_t identity=create(1,sizeof(native_vorbis_identification_t)),layout_buf=create(1,sizeof(native_vorbis_setup_layout_t)),view_buf=create(1,sizeof(native_vorbis_setup_t));
        native_vorbis_identification_t *id=(void *)identity.data;native_vorbis_setup_layout_t *layout=(void *)layout_buf.data;native_vorbis_setup_t *view=(void *)view_buf.data;
        int is=native_vorbis_identification_parse(packets[0].data,packets[0].bytes,bits[0],id),ms=-99,mt=-99,as=-99;
        buffer_t books={0},words={0},q={0},config={0},getter={0};size_t getters=0;native_vorbis_audio_prefix_t prefix;memset(&prefix,0xa5,sizeof(prefix));
        if(is){for(size_t k=0;k<identity.bytes;k++)assert(identity.data[k]==0xa5);}
        else{
            copy_before(&identity);
            for(uint64_t cut=0;cut<233;cut++){native_vorbis_identification_t trial;unsigned char before[sizeof(trial)];memcpy(&trial,id,sizeof(trial));memcpy(before,&trial,sizeof(trial));assert(native_vorbis_identification_parse(packets[0].data,packets[0].bytes,cut,&trial)==NATIVE_VORBIS_NUMERIC_TRUNCATED && !memcmp(&trial,before,sizeof(trial)));id_cuts++;}
            ms=native_vorbis_setup_measure(packets[1].data,packets[1].bytes,bits[1],id,layout);
            if(ms){
                for(size_t k=0;k<layout_buf.bytes;k++)assert(layout_buf.data[k]==0xa5);
                native_vorbis_setup_layout_t probe={0};probe.identification=*id;unsigned char before[sizeof(probe)];memcpy(before,&probe,sizeof(probe));
                books=create(1,sizeof(native_vorbis_codebook_t));words=create(1,sizeof(native_vorbis_codeword_t));q=create(1,sizeof(uint16_t));config=create(1,sizeof(uint32_t));
                copy_before(&books);copy_before(&words);copy_before(&q);copy_before(&config);copy_before(&view_buf);
                native_vorbis_setup_storage_t zero={(void *)books.data,0,(void *)words.data,0,(void *)q.data,0,(void *)config.data,0};native_vorbis_setup_storage_t unchanged=zero;
                mt=native_vorbis_setup_materialize(packets[1].data,packets[1].bytes,bits[1],&probe,&zero,view);assert(mt==ms && !memcmp(&probe,before,sizeof(probe)) && !memcmp(&zero,&unchanged,sizeof(zero)));
                check_buffer(&books,1);check_buffer(&words,1);check_buffer(&q,1);check_buffer(&config,1);check_buffer(&view_buf,1);
            }else{
                assert(layout->book_count<=256 && layout->codeword_count<=1048576 && layout->multiplicand_count<=1048576 && layout->configuration_count<=262144);copy_before(&layout_buf);
                for(uint64_t cut=0;cut<layout->end_bit;cut++){native_vorbis_setup_layout_t trial;unsigned char before[sizeof(trial)];memcpy(&trial,layout,sizeof(trial));memcpy(before,&trial,sizeof(trial));assert(native_vorbis_setup_measure(packets[1].data,packets[1].bytes,cut,id,&trial)==NATIVE_VORBIS_NUMERIC_TRUNCATED && !memcmp(&trial,before,sizeof(trial)));setup_cuts++;}
                books=create(layout->book_count,sizeof(native_vorbis_codebook_t));words=create((size_t)layout->codeword_count,sizeof(native_vorbis_codeword_t));q=create((size_t)layout->multiplicand_count,sizeof(uint16_t));config=create(layout->configuration_count,sizeof(uint32_t));
                native_vorbis_setup_storage_t storage={(void *)books.data,layout->book_count,(void *)words.data,(size_t)layout->codeword_count,(void *)q.data,(size_t)layout->multiplicand_count,(void *)config.data,layout->configuration_count};native_vorbis_setup_storage_t unchanged=storage;
                mt=native_vorbis_setup_materialize(packets[1].data,packets[1].bytes,bits[1],layout,&storage,view);assert(mt==0 && !memcmp(&storage,&unchanged,sizeof(storage)));
                copy_before(&view_buf);copy_before(&books);copy_before(&words);copy_before(&q);copy_before(&config);
                size_t capacity=(size_t)layout->configuration_count+16U*layout->floor_count;getter=create(capacity,sizeof(uint32_t));getters=capture_getters(view,(void *)getter.data,capacity);
                native_vorbis_packet_t cursor={packets[2].data,packets[2].bytes,bits[2],start,false};
                unsigned char cursor_before[sizeof(cursor)];memcpy(cursor_before,&cursor,sizeof(cursor));as=native_vorbis_packet_init(&cursor,packets[2].data,packets[2].bytes,bits[2],start);
                if(as)assert(!memcmp(cursor_before,&cursor,sizeof(cursor)));
                if(as==0){native_vorbis_audio_prefix_t before=prefix;as=native_vorbis_audio_prefix(view,&cursor,&prefix);if(as)assert(!memcmp(&prefix,&before,sizeof(prefix)) && cursor.position==start && cursor.end_of_packet==(as==NATIVE_VORBIS_NUMERIC_TRUNCATED));}
                assert(cursor.data==packets[2].data && cursor.bytes==packets[2].bytes && cursor.bits==bits[2]);position=cursor.position;eop=cursor.end_of_packet;
                if(as==0)for(uint64_t cut=start;cut<position;cut++){
                    native_vorbis_packet_t trial;assert(native_vorbis_packet_init(&trial,packets[2].data,packets[2].bytes,cut,start)==0);native_vorbis_audio_prefix_t value=prefix,before=value;
                    assert(native_vorbis_audio_prefix(view,&trial,&value)==NATIVE_VORBIS_NUMERIC_TRUNCATED && !memcmp(&value,&before,sizeof(value)) && trial.position==start && trial.end_of_packet);audio_cuts++;
                    uint64_t untouched=CANARY;assert(native_vorbis_packet_read(&trial,0,&untouched)==NATIVE_VORBIS_NUMERIC_TRUNCATED && untouched==CANARY && trial.position==start);
                }
                check_buffer(&layout_buf,1);check_buffer(&view_buf,1);check_buffer(&books,1);check_buffer(&words,1);check_buffer(&q,1);check_buffer(&config,1);check_buffer(&getter,0);
            }
            check_buffer(&identity,1);
        }
        for(unsigned j=0;j<3;j++){check_buffer(&packets[j],1);}check_buffer(&identity,0);check_buffer(&layout_buf,0);check_buffer(&view_buf,0);
        put(out,index,4);put(out,(uint32_t)is,4);put(out,(uint32_t)ms,4);put(out,(uint32_t)mt,4);put(out,(uint32_t)as,4);
        if(is==0)id_put(out,id);
        if(mt==0){layout_put(out,layout);for(size_t j=0;j<view->book_count;j++)book_put(out,&view->books[j]);put(out,view->configuration_count,4);for(size_t j=0;j<view->configuration_count;j++)put(out,view->configuration[j],4);put(out,getters,4);for(size_t j=0;j<getters;j++)put(out,((uint32_t *)getter.data)[j],4);if(as==0){put(out,prefix.mode,4);put(out,prefix.blockflag,4);put(out,prefix.previous_window,4);put(out,prefix.next_window,4);put(out,prefix.mapping,4);put(out,prefix.blocksize,4);}}
        put(out,position,8);put(out,eop,4);put(out,id_cuts,8);put(out,setup_cuts,8);put(out,audio_cuts,8);put(out,7,4);
        for(unsigned j=0;j<3;j++){destroy(&packets[j]);}destroy(&identity);destroy(&layout_buf);destroy(&view_buf);if(books.base)destroy(&books);if(words.base)destroy(&words);if(q.base)destroy(&q);if(config.base)destroy(&config);if(getter.base)destroy(&getter);
    }
    assert(fgetc(in)==EOF);assert(!fclose(in));assert(!fclose(out));return 0;
}
