#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "stream_confirm.h"

typedef struct {const uint8_t *data;size_t size,reads;} view_t;
static bool read_span(void *opaque,size_t offset,uint8_t *out,size_t count) {
    view_t *v=opaque;
    assert(offset<=v->size && count<=v->size-offset && count<=STREAM_ID3_HEADER_BYTES);
    // Exercise reads that cross independent 2048-byte packet boundaries.
    while(count) {
        size_t n=2048-offset%2048;if(n>count)n=count;
        memcpy(out,v->data+offset,n);offset+=n;out+=n;count-=n;
    }
    ++v->reads;return true;
}
static stream_confirm_result_t check(const uint8_t *data,size_t size,bool eof,
        size_t budget,uint32_t tags,stream_confirm_info_t *info) {
    view_t v={.data=data,.size=size};
    return stream_confirm_window(read_span,&v,size,eof,budget,tags,info);
}
static void unit(void) {
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\0",4);
    const uint8_t aac[]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    uint8_t mixed[sizeof(mp3)+sizeof(aac)];memcpy(mixed,mp3,sizeof(mp3));memcpy(mixed+sizeof(mp3),aac,sizeof(aac));
    stream_confirm_info_t info;
    for(size_t n=0;n<sizeof(mp3)+7;++n) {
        assert(check(mixed,n,false,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_MORE);
        assert(!info.discard && info.needed>n && info.needed<=sizeof(mp3)+7);
    }
    assert(check(mixed,sizeof(mixed),false,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY);
    assert(info.codec==STREAM_PROBE_MP3 && info.first_frame_bytes==417 && !info.single_frame_eof);
    assert(check(mp3,sizeof(mp3),true,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY && info.single_frame_eof);
    assert(check(mp3,sizeof(mp3)-1,true,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_INVALID);
    // Plausible false header with an impossible next boundary; valid AAC is
    // inside its claimed payload, so a startup/recovery search must find it.
    uint8_t false_mp3[500]={0};memcpy(false_mp3,mp3,4);
    memcpy(false_mp3+32,aac,sizeof(aac));memcpy(false_mp3+44,aac,sizeof(aac));
    assert(check(false_mp3,sizeof(false_mp3),false,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY);
    assert(info.discard==32 && info.codec==STREAM_PROBE_AAC && info.first_frame_bytes==12);
    assert(check(false_mp3,sizeof(false_mp3),false,31,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_INVALID);
    assert(check(false_mp3,56,true,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY && info.discard==32);
    uint8_t false_aac[32+2*sizeof(mp3)]={0};memcpy(false_aac,aac,7);
    memcpy(false_aac+32,mp3,sizeof(mp3));memcpy(false_aac+32+sizeof(mp3),mp3,sizeof(mp3));
    assert(check(false_aac,sizeof(false_aac),false,4096,STREAM_ID3_RUN_BYTES,&info)==STREAM_CONFIRM_READY);
    assert(info.discard==32 && info.codec==STREAM_PROBE_MP3);
    uint8_t tag[10]={'I','D','3',4,0,0,0,0,1,0}; // 128-byte body.
    uint8_t tagged[417+10];memcpy(tagged,mp3,417);memcpy(tagged+417,tag,10);
    assert(check(tagged,sizeof(tagged),false,4096,138,&info)==STREAM_CONFIRM_REMOVE_TAG);
    assert(info.tag_offset==417 && info.tag_bytes==138);
    assert(check(tagged,sizeof(tagged),false,4096,137,&info)==STREAM_CONFIRM_INVALID);
    assert(check(tag,10,false,4096,138,&info)==STREAM_CONFIRM_REMOVE_TAG && !info.tag_offset);
    memcpy(tagged+417,"TAG",3);
    assert(check(tagged,420,false,4096,128,&info)==STREAM_CONFIRM_REMOVE_TAG && info.tag_bytes==128);
    const uint8_t free_mp3[]={0xff,0xfb,0,0};
    assert(check(free_mp3,4,false,4096,0,&info)==STREAM_CONFIRM_FREE_FORMAT);
    uint8_t large[8191+7];memset(large,0x55,sizeof(large));memcpy(large,aac,7);
    large[3]|=3;large[4]=255;large[5]|=0xe0;memcpy(large+8191,aac,7);
    assert(check(large,8191,false,4096,0,&info)==STREAM_CONFIRM_MORE && info.needed==8192);
    assert(check(large,sizeof(large),false,4096,0,&info)==STREAM_CONFIRM_READY && info.first_frame_bytes==8191);
    // Invalid accessor/huge search budget cannot turn into an out-of-bounds read.
    uint8_t junk[128]={0};
    assert(check(junk,sizeof(junk),true,SIZE_MAX,0,&info)==STREAM_CONFIRM_INVALID);
    uint32_t random=0x137a48b1;
    for(unsigned trial=0;trial<5000;++trial) {
        uint8_t data[256];
        for(size_t i=0;i<sizeof(data);++i) {random=random*1664525U+1013904223U;data[i]=random>>24;}
        size_t n=random%sizeof(data),budget=(random>>8)%257;
        bool eof=(random&1)!=0;
        stream_confirm_result_t result=check(data,n,eof,budget,STREAM_ID3_RUN_BYTES,&info);
        assert(info.discard<=n && info.discard<=budget);
        if(result==STREAM_CONFIRM_MORE) assert(!eof && info.needed>n-info.discard && info.needed<=8201);
        if(result==STREAM_CONFIRM_READY) assert(info.codec>=STREAM_PROBE_MP3 && info.codec<=STREAM_PROBE_OGG);
        if(result==STREAM_CONFIRM_REMOVE_TAG) assert(info.tag_bytes<=STREAM_ID3_RUN_BYTES);
    }
    puts("PASS unit: false signatures, exact boundaries, splits, EOF, tags, bounds, max ADTS, free-format");
}

int main(int argc,char **argv) {
    unit();if(argc==1)return 0;assert(argc==2);
    FILE *f=fopen(argv[1],"rb");assert(f);assert(!fseek(f,0,SEEK_END));
    long length=ftell(f);assert(length>0);rewind(f);uint8_t *data=malloc(length);assert(data);
    assert(fread(data,1,length,f)==(size_t)length);fclose(f);
    const size_t chunks[]={1,7,2048};
    for(unsigned i=0;i<3;++i) {
        size_t used=0,discarded=0,budget=4096;stream_confirm_info_t info;
        stream_confirm_result_t result;
        while(true) {
            result=check(data+discarded,used,discarded+used==(size_t)length,budget,STREAM_ID3_RUN_BYTES,&info);
            assert(info.discard<=used && info.discard<=budget);
            discarded+=info.discard;used-=info.discard;budget-=info.discard;
            if(result!=STREAM_CONFIRM_MORE)break;
            assert(info.needed>used && info.needed<=8191+STREAM_ID3_HEADER_BYTES);
            size_t n=info.needed-used;if(n>chunks[i])n=chunks[i];
            if(n>(size_t)length-discarded-used)n=(size_t)length-discarded-used;
            assert(n);used+=n;
        }
        assert(result==STREAM_CONFIRM_READY);
        printf("READY chunk=%zu codec=%u discard=%zu retained=%zu frame=%u single=%u\n",
               chunks[i],info.codec,discarded,used,info.first_frame_bytes,info.single_frame_eof);
    }
    free(data);return 0;
}
