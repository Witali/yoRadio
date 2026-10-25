// Additional malformed/metadata boundaries; original host/native campaigns stay frozen.
#include "native_vorbis_codebook.h"
#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const uint64_t CANARY=UINT64_C(0x8c64f032a19be75d);
static unsigned checks=0,negative_cases=0;
typedef struct{uint64_t a;native_vorbis_codebook_layout_t value;uint64_t z;} layout_guard;
typedef struct{uint64_t a;native_vorbis_codeword_t value[2];uint64_t z;} words_guard;
typedef struct{uint64_t a;uint16_t value[2];uint64_t z;} quant_guard;
typedef struct{uint64_t a;native_vorbis_codebook_t value;uint64_t z;} book_guard;
static void field(uint8_t *data,size_t bytes,uint64_t *at,uint32_t value,unsigned width){
    assert(width<=32 && *at+width<=8*(uint64_t)bytes);
    for(unsigned i=0;i<width;i++,(*at)++)if((value>>i)&1)data[*at/8]|=(uint8_t)(1u<<(*at%8));
}
static uint64_t header(uint8_t *data,size_t bytes,uint32_t dimension,uint32_t entries,unsigned ordered){
    memset(data,0,bytes);uint64_t at=0;field(data,bytes,&at,0x564342,24);field(data,bytes,&at,dimension,16);
    field(data,bytes,&at,entries,24);field(data,bytes,&at,ordered,1);return at;
}
static uint64_t unordered(uint8_t *data,size_t bytes,uint32_t dimension,const uint32_t *lengths,uint32_t entries,unsigned lookup){
    uint64_t at=header(data,bytes,dimension,entries,0);unsigned sparse=0;
    for(uint32_t i=0;i<entries;i++){if(!lengths[i])sparse=1;}
    field(data,bytes,&at,sparse,1);
    for(uint32_t i=0;i<entries;i++){if(sparse)field(data,bytes,&at,lengths[i]!=0,1);if(lengths[i])field(data,bytes,&at,lengths[i]-1,5);}
    field(data,bytes,&at,lookup,4);
    if(lookup==1){field(data,bytes,&at,0x80000000,32);field(data,bytes,&at,0x62800001,32);field(data,bytes,&at,15,4);field(data,bytes,&at,1,1);}
    return at;
}
static void guards_init(layout_guard *l,words_guard *w,quant_guard *q,book_guard *b){
    memset(l,0xa5,sizeof(*l));memset(w,0xa5,sizeof(*w));memset(q,0xa5,sizeof(*q));memset(b,0xa5,sizeof(*b));
    l->a=l->z=w->a=w->z=q->a=q->z=b->a=b->z=CANARY;
}
static void guards_check(const layout_guard *l,const words_guard *w,const quant_guard *q,const book_guard *b){
    assert(l->a==CANARY&&l->z==CANARY&&w->a==CANARY&&w->z==CANARY&&q->a==CANARY&&q->z==CANARY&&b->a==CANARY&&b->z==CANARY);
}
static void failure(const uint8_t *data,size_t bytes,uint64_t extent,int expected,const native_vorbis_codebook_layout_t *valid){
    assert(bytes<=512);uint8_t input[512];memcpy(input,data,bytes);layout_guard l;words_guard w;quant_guard q;book_guard b;guards_init(&l,&w,&q,&b);
    unsigned char ls[sizeof(l)],ws[sizeof(w)],qs[sizeof(q)],bs[sizeof(b)];memcpy(ls,&l,sizeof(l));memcpy(ws,&w,sizeof(w));memcpy(qs,&q,sizeof(q));memcpy(bs,&b,sizeof(b));
    int status=native_vorbis_codebook_measure(data,bytes,extent,0,&l.value);assert(status==expected&&!memcmp(ls,&l,sizeof(l)));checks++;
    status=native_vorbis_codebook_materialize(data,bytes,extent,valid,w.value,0,q.value,0,&b.value);
    assert(status==expected&&!memcmp(ws,&w,sizeof(w))&&!memcmp(qs,&q,sizeof(q))&&!memcmp(bs,&b,sizeof(b)));checks++;
    assert(!memcmp(input,data,bytes));guards_check(&l,&w,&q,&b);negative_cases++;
}
static void capacity(const uint8_t *data,size_t bytes,uint64_t extent,const native_vorbis_codebook_layout_t *layout,size_t available){
    layout_guard l;words_guard w;quant_guard q;book_guard b;guards_init(&l,&w,&q,&b);unsigned char ws[sizeof(w)],qs[sizeof(q)],bs[sizeof(b)];
    memcpy(ws,&w,sizeof(w));memcpy(qs,&q,sizeof(q));memcpy(bs,&b,sizeof(b));
    assert(native_vorbis_codebook_materialize(data,bytes,extent,layout,w.value,available,q.value,0,&b.value)==NATIVE_VORBIS_NUMERIC_CAPACITY);checks++;
    assert(!memcmp(ws,&w,sizeof(w))&&!memcmp(qs,&q,sizeof(q))&&!memcmp(bs,&b,sizeof(b)));guards_check(&l,&w,&q,&b);
}
int main(int argc,char **argv){
    assert(argc==2);uint8_t packet[512];uint32_t pair[2]={1,1};uint64_t extent=unordered(packet,sizeof(packet),1,pair,2,0);
    native_vorbis_codebook_layout_t valid;assert(native_vorbis_codebook_measure(packet,sizeof(packet),extent,0,&valid)==0);checks++;
    capacity(packet,sizeof(packet),extent,&valid,0);
    uint64_t at=header(packet,sizeof(packet),1,2,1);field(packet,sizeof(packet),&at,0,5);field(packet,sizeof(packet),&at,3,2);field(packet,sizeof(packet),&at,0,4);
    failure(packet,sizeof(packet),at,NATIVE_VORBIS_NUMERIC_INVALID,&valid);
    for(unsigned first=1;first<=32;first++){
        at=header(packet,sizeof(packet),1,2,1);field(packet,sizeof(packet),&at,first-1,5);
        for(unsigned length=first;length<=32;length++)field(packet,sizeof(packet),&at,0,2);
        field(packet,sizeof(packet),&at,0,4);failure(packet,sizeof(packet),at,NATIVE_VORBIS_NUMERIC_INVALID,&valid);
    }
    for(unsigned lookup=3;lookup<16;lookup++){extent=unordered(packet,sizeof(packet),1,pair,2,lookup);failure(packet,sizeof(packet),extent,NATIVE_VORBIS_NUMERIC_INVALID,&valid);}
    for(unsigned length=2;length<=32;length++){
        uint32_t dense[1]={length},sparse[3]={0,length,0};extent=unordered(packet,sizeof(packet),1,dense,1,0);failure(packet,sizeof(packet),extent,NATIVE_VORBIS_NUMERIC_INVALID,&valid);
        extent=unordered(packet,sizeof(packet),1,sparse,3,0);failure(packet,sizeof(packet),extent,NATIVE_VORBIS_NUMERIC_INVALID,&valid);
    }
    for(unsigned bit=0;bit<24;bit++){extent=unordered(packet,sizeof(packet),1,pair,2,0);packet[bit/8]^=(uint8_t)(1u<<(bit%8));failure(packet,sizeof(packet),extent,NATIVE_VORBIS_NUMERIC_INVALID,&valid);}
    extent=unordered(packet,sizeof(packet),1,pair,2,0);
    for(uint64_t cut=64;cut<=70;cut++)failure(packet,sizeof(packet),cut,NATIVE_VORBIS_NUMERIC_TRUNCATED,&valid);
    extent=unordered(packet,sizeof(packet),0,pair,2,1);failure(packet,sizeof(packet),extent,NATIVE_VORBIS_NUMERIC_INVALID,&valid);
    // Full sixteen-bit dimension and a complete fifteen-bit tree; measure without a row array.
    size_t dense_bytes=20489;uint8_t *dense=calloc(dense_bytes,1);assert(dense);at=header(dense,dense_bytes,65535,32768,0);field(dense,dense_bytes,&at,0,1);
    for(uint32_t i=0;i<32768;i++){field(dense,dense_bytes,&at,14,5);}
    field(dense,dense_bytes,&at,0,4);assert(at==UINT64_C(163910));
    uint8_t *saved=malloc(dense_bytes);assert(saved);memcpy(saved,dense,dense_bytes);native_vorbis_codebook_layout_t wide;
    assert(native_vorbis_codebook_measure(dense,dense_bytes,at,0,&wide)==0);checks++;
    assert(wide.quantization.dimensions==65535 && wide.quantization.entries==32768 && wide.used_entries==32768 && wide.maximum_length==15);
    capacity(dense,dense_bytes,at,&wide,0);assert(!memcmp(saved,dense,dense_bytes));free(saved);free(dense);
    // Maximum24-bit sparse metadata: only the last row is used. One word, no entries array.
    const uint32_t maximum=UINT32_C(0xffffff);const uint64_t sparse_bits=UINT64_C(66)+maximum+5+4;size_t sparse_bytes=(size_t)((sparse_bits+7)/8);
    uint8_t *sparse=calloc(sparse_bytes,1);assert(sparse);at=header(sparse,sparse_bytes,65535,maximum,0);field(sparse,sparse_bytes,&at,1,1);
    at+=maximum-1;field(sparse,sparse_bytes,&at,1,1);field(sparse,sparse_bytes,&at,0,5);field(sparse,sparse_bytes,&at,0,4);assert(at==sparse_bits);
    saved=malloc(sparse_bytes);assert(saved);memcpy(saved,sparse,sparse_bytes);native_vorbis_codebook_layout_t largest;
    assert(native_vorbis_codebook_measure(sparse,sparse_bytes,sparse_bits,0,&largest)==0);checks++;
    assert(largest.quantization.dimensions==65535 && largest.quantization.entries==maximum && largest.used_entries==1 && largest.maximum_length==1);
    capacity(sparse,sparse_bytes,sparse_bits,&largest,0);
    struct{uint64_t a;native_vorbis_codeword_t value;uint64_t z;} word;memset(&word,0xa5,sizeof(word));word.a=word.z=CANARY;native_vorbis_codebook_t book;
    assert(native_vorbis_codebook_materialize(sparse,sparse_bytes,sparse_bits,&largest,&word.value,1,NULL,0,&book)==0);checks++;
    assert(book.word_count==1 && word.value.code==0 && word.value.length==1 && word.value.entry==maximum-1 && book.quantization.storage_count==0);
    uint8_t payload=2;native_vorbis_packet_t cursor;assert(native_vorbis_packet_init(&cursor,&payload,1,2,0)==0);checks++;
    for(unsigned bit=0;bit<2;bit++){uint32_t entry=0;assert(native_vorbis_codebook_decode(&book,&cursor,&entry)==0 && entry==maximum-1 && cursor.position==bit+1 && !cursor.end_of_packet);checks++;}
    assert(word.a==CANARY && word.z==CANARY && !memcmp(saved,sparse,sparse_bytes));free(saved);free(sparse);
    assert(negative_cases==140 && checks==290);
    FILE *out=fopen(argv[1],"wb");assert(out);
    assert(fprintf(out,"{\"schema\":\"native-vorbis-codebook-boundaries-capture-v1\",\"passed\":true,\"status_checks\":%u,\"negative_cases\":%u,\"ordered_overrun\":1,\"ordered_length33\":32,\"reserved_lookup\":13,\"bad_singleton\":62,\"wrong_sync\":24,\"unordered_flag_truncations\":7,\"lookup1_zero_dimension\":1,\"wide_complete_entries\":%" PRIu32 ",\"wide_complete_dimensions\":%" PRIu32 ",\"wide_complete_used\":%" PRIu32 ",\"wide_complete_maximum_length\":%" PRIu32 ",\"full24_sparse_entries\":%" PRIu32 ",\"full24_sparse_dimensions\":%" PRIu32 ",\"full24_sparse_used\":%" PRIu32 ",\"full24_sparse_last_entry\":%" PRIu32 ",\"full24_packet_bits\":%" PRIu64 ",\"full24_packet_bytes\":%zu,\"full24_decoded_bits\":2}\n",checks,negative_cases,wide.quantization.entries,wide.quantization.dimensions,wide.used_entries,wide.maximum_length,largest.quantization.entries,largest.quantization.dimensions,largest.used_entries,word.value.entry,sparse_bits,sparse_bytes)>0);
    assert(!fclose(out));return 0;
}
