// Complete owned-book adapter; explicit little-endian capture, no reference math.
#include "native_vorbis_codebook.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint64_t CANARY=UINT64_C(0x94e2635b10ca7fd8);
static uint64_t get(FILE *f,unsigned n){uint64_t x=0;for(unsigned i=0;i<n;i++){int c=fgetc(f);assert(c!=EOF);x|=(uint64_t)(unsigned)c<<(8*i);}return x;}
static void put(FILE *f,uint64_t x,unsigned n){for(unsigned i=0;i<n;i++)assert(fputc((int)((x>>(8*i))&255),f)!=EOF);}
static void *guarded(size_t bytes){uint8_t *p=malloc(bytes+16);assert(p);memcpy(p,&CANARY,8);memset(p+8,0xa5,bytes);memcpy(p+8+bytes,&CANARY,8);return p+8;}
static void check_guard(const void *p,size_t bytes){uint64_t a,z;memcpy(&a,(const uint8_t *)p-8,8);memcpy(&z,(const uint8_t *)p+bytes,8);assert(a==CANARY && z==CANARY);}
static void release(void *p){free((uint8_t *)p-8);}
static void layout_put(FILE *f,native_vorbis_codebook_layout_t l){
    native_vorbis_quant_layout_t q=l.quantization;put(f,l.start_bit,8);put(f,l.used_entries,4);put(f,l.maximum_length,4);
    put(f,q.dimensions,4);put(f,q.entries,4);put(f,q.lookup_type,4);put(f,q.minimum_bits,4);put(f,q.delta_bits,4);put(f,q.value_bits,4);put(f,q.sequence_p,4);
    put(f,q.multiplicand_count,8);put(f,q.start_bit,8);put(f,q.multiplicand_bit,8);put(f,q.end_bit,8);
}
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
int main(int argc,char **argv){
    assert(argc==3);FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb");assert(in&&out);uint8_t magic[8];assert(fread(magic,1,8,in)==8&&!memcmp(magic,"CBTEST01",8));
    uint32_t count=(uint32_t)get(in,4);assert(count>0&&count<=10000);assert(fwrite("CBOUT001",1,8,out)==8);put(out,count,4);put(out,controls(),4);
    for(uint32_t i=0;i<count;i++){
        uint32_t names=(uint32_t)get(in,4);assert(names>=1&&names<=63);for(uint32_t j=0;j<names;j++){unsigned c=(unsigned)get(in,1);assert((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-');}
        uint32_t op=(uint32_t)get(in,4),bytes=(uint32_t)get(in,4);assert(bytes<=65536);uint8_t *packet=guarded(bytes);assert(fread(packet,1,bytes,in)==bytes);uint64_t packet_bits=get(in,8),start=get(in,8);
        uint32_t payload_bytes=(uint32_t)get(in,4);assert(payload_bytes<=65536);uint8_t *payload=guarded(payload_bytes);assert(fread(payload,1,payload_bytes,in)==payload_bytes);uint64_t payload_bits=get(in,8),payload_start=get(in,8);uint32_t length=(uint32_t)get(in,4);assert(length<=255);
        uint8_t *packet_copy=malloc(bytes?bytes:1),*payload_copy=malloc(payload_bytes?payload_bytes:1);assert(packet_copy&&payload_copy);memcpy(packet_copy,packet,bytes);memcpy(payload_copy,payload,payload_bytes);
        native_vorbis_codebook_layout_t layout;memset(&layout,0xa5,sizeof(layout));int ms=native_vorbis_codebook_measure(packet,bytes,packet_bits,start,&layout);assert(ms==0);
        uint64_t truncations=0;for(uint64_t cut=start;cut<layout.quantization.end_bit;cut++){native_vorbis_codebook_layout_t test;memcpy(&test,&layout,sizeof(test));assert(native_vorbis_codebook_measure(packet,bytes,cut,start,&test)==NATIVE_VORBIS_NUMERIC_TRUNCATED&&!memcmp(&test,&layout,sizeof(test)));truncations++;}
        assert(layout.used_entries<=4096 && layout.quantization.multiplicand_count<=65535);size_t words_count=layout.used_entries,qcount=(size_t)layout.quantization.multiplicand_count;
        native_vorbis_codeword_t *words=guarded(words_count*sizeof(*words));uint16_t *q=guarded(qcount*2);native_vorbis_codebook_t book;memset(&book,0xa5,sizeof(book));
        int mt=native_vorbis_codebook_materialize(packet,bytes,packet_bits,&layout,words,words_count,q,qcount,&book);assert(mt==0);
        void *word_copy=malloc(words_count?words_count*sizeof(*words):1),*qcopy=malloc(qcount?qcount*2:1);assert(word_copy&&qcopy);memcpy(word_copy,words,words_count*sizeof(*words));memcpy(qcopy,q,qcount*2);native_vorbis_codebook_t book_copy;memcpy(&book_copy,&book,sizeof(book));
        native_vorbis_affine_t *values=guarded(length*sizeof(*values));native_vorbis_packet_t cursor;assert(native_vorbis_packet_init(&cursor,payload,payload_bytes,payload_bits,payload_start)==0);
        uint32_t decoded[255];uint64_t positions[255];size_t reads=op==1?length:op==2?(length?1:0):(length-1)/layout.quantization.dimensions+1;
        assert(op>=1&&op<=3 && reads<=255);native_vorbis_packet_t copy=cursor;
        for(size_t j=0;j<reads;j++){assert(native_vorbis_codebook_decode(&book,&copy,&decoded[j])==0);positions[j]=copy.position;}
        uint64_t payload_truncations=0;
        for(uint64_t cut=payload_start;cut<copy.position;cut++){
            native_vorbis_packet_t trial;assert(native_vorbis_packet_init(&trial,payload,payload_bytes,cut,payload_start)==0);
            if(op==1){
                int failed=0;for(size_t j=0;j<reads;j++){uint32_t v=0xfedcba98;uint64_t before=trial.position;int result=native_vorbis_codebook_decode(&book,&trial,&v);
                    if(result==NATIVE_VORBIS_NUMERIC_TRUNCATED){assert(v==0xfedcba98 && trial.position==before && trial.end_of_packet);failed=1;break;}
                    assert(result==0 && v==decoded[j]);}assert(failed);
            }else{
                unsigned char saved[255*sizeof(native_vorbis_affine_t)];memcpy(saved,values,length*sizeof(*values));
                int result=op==2?native_vorbis_codebook_vector(&book,&trial,length,values,length):native_vorbis_codebook_floor0_lsp(&book,&trial,length,values,length);
                assert(result==NATIVE_VORBIS_NUMERIC_TRUNCATED && trial.position==payload_start && trial.end_of_packet && !memcmp(saved,values,length*sizeof(*values)));
            }
            uint64_t v=CANARY,before=trial.position;assert(native_vorbis_packet_read(&trial,0,&v)==NATIVE_VORBIS_NUMERIC_TRUNCATED && v==CANARY && trial.position==before);payload_truncations++;
        }
        int status=0;if(op==1)cursor=copy;else if(op==2)status=native_vorbis_codebook_vector(&book,&cursor,length,values,length);else status=native_vorbis_codebook_floor0_lsp(&book,&cursor,length,values,length);
        assert(status==0 && cursor.position==copy.position && !cursor.end_of_packet);size_t outputs=op==1?0:length;
        assert(!memcmp(packet,packet_copy,bytes)&&!memcmp(payload,payload_copy,payload_bytes)&&!memcmp(words,word_copy,words_count*sizeof(*words))&&!memcmp(q,qcopy,qcount*2)&&!memcmp(&book,&book_copy,sizeof(book)));
        check_guard(packet,bytes);check_guard(payload,payload_bytes);check_guard(words,words_count*sizeof(*words));check_guard(q,qcount*2);check_guard(values,length*sizeof(*values));
        put(out,i,4);put(out,(uint32_t)ms,4);put(out,(uint32_t)mt,4);put(out,(uint32_t)status,4);layout_put(out,layout);put(out,words_count,4);
        for(size_t j=0;j<words_count;j++){put(out,words[j].code,4);put(out,words[j].entry,4);put(out,words[j].length,4);}put(out,qcount,4);for(size_t j=0;j<qcount;j++)put(out,q[j],2);
        put(out,reads,4);for(size_t j=0;j<reads;j++){put(out,decoded[j],4);put(out,positions[j],8);}put(out,outputs,4);for(size_t j=0;j<outputs;j++){put(out,values[j].minimum_bits,4);put(out,values[j].delta_bits,4);put(out,values[j].minimum_multiplier,4);put(out,values[j].delta_multiplier,4);}
        put(out,cursor.position,8);put(out,cursor.end_of_packet,4);put(out,truncations,8);put(out,payload_truncations,8);put(out,7,4);
        free(word_copy);free(qcopy);free(packet_copy);free(payload_copy);release(packet);release(payload);release(words);release(q);release(values);
    }
    assert(fgetc(in)==EOF&&!fclose(in)&&!fclose(out));return 0;
}
