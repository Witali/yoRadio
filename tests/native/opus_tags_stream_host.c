/* Real CRC/page ownership and independently generated strict UTF-8 vectors. */
#include "opus_tags_stream.h"
#include <ogg/ogg.h>
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
static uint64_t vector_cases,text_packets,parser_schedules,page_schedules,actual_acks,libogg_walks;
static unsigned limit_controls,field_controls;
static void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;++i)p[i]=(uint8_t)(v>>(i*8u));}
static void put64(uint8_t *p,uint64_t v){for(unsigned i=0;i<8;++i)p[i]=(uint8_t)(v>>(i*8u));}
static opus_tags_status parse(const uint8_t *bytes,size_t count,size_t split) {
    opus_tags_parser s={0};size_t at=0;opus_tags_status status=OTS_MORE;
    while(at<count) {size_t n=count-at;if(split && n>split)n=split;size_t used=0;status=otp_feed(&s,bytes+at,n,&used);assert(used<=n);at+=used;if(status<0)break;assert(used==n);}
    if(status>=0)status=otp_finish(&s);
    if(status<0){size_t used=99;assert(otp_feed(&s,NULL,0,&used)==status && !used && otp_finish(&s)==status);}
    else {size_t used=99;assert(status==OTS_COMPLETE && s.complete && otp_finish(&s)==OTS_COMPLETE && otp_feed(&s,NULL,0,&used)==OTS_ARGUMENT && !used);}
    ++parser_schedules;return status;
}
static void text(const uint8_t *value,unsigned bytes,bool valid) {
    assert(bytes<=8);uint8_t packet[32]={0};memcpy(packet,"OpusTags",8);put32(packet+8,bytes);if(bytes)memcpy(packet+12,value,bytes);
    assert(parse(packet,16u+bytes,1)==(valid?OTS_COMPLETE:OTS_UTF8));++text_packets;
    memset(packet+8,0,sizeof(packet)-8);put32(packet+12,1);put32(packet+16,bytes);if(bytes)memcpy(packet+20,value,bytes);
    assert(parse(packet,20u+bytes,1)==(valid?OTS_COMPLETE:OTS_UTF8));++text_packets;
}
static void vectors(const char *path) {
    FILE *f=fopen(path,"rb");assert(f);uint8_t header[12];assert(fread(header,1,12,f)==12 && !memcmp(header,"OTUF101\0",8));unsigned count=oopt_le32(header+8);
    for(unsigned i=0;i<count;++i) {int n=fgetc(f),valid=fgetc(f);assert(n>=0 && n<=8 && (valid==0 || valid==1));uint8_t value[8];assert(fread(value,1,(size_t)n,f)==(size_t)n);text(value,(unsigned)n,valid!=0);++vector_cases;}
    assert(fgetc(f)==EOF && !fclose(f));
}
static uint8_t *tags(size_t vendor,size_t first,size_t second,size_t tail,size_t *bytes) {
    *bytes=16u+vendor+4u+first+4u+second+tail;uint8_t *p=calloc(*bytes,1);assert(p);memcpy(p,"OpusTags",8);put32(p+8,(uint32_t)vendor);memset(p+12,'v',vendor);size_t at=12u+vendor;put32(p+at,2);at+=4;
    put32(p+at,(uint32_t)first);at+=4;memset(p+at,'a',first);at+=first;put32(p+at,(uint32_t)second);at+=4;memset(p+at,'b',second);at+=second;
    for(size_t i=0;i<tail;++i)p[at+i]=(uint8_t)(i*73u+0xffu);
    return p;
}
static void fields(void) {
    uint8_t empty[16]={0};memcpy(empty,"OpusTags",8);assert(parse(empty,16,0)==OTS_COMPLETE);++field_controls;
    for(size_t n=0;n<16;++n){assert(parse(empty,n,1)==OTS_INVALID);++field_controls;}
    for(unsigned i=0;i<8;++i){empty[i]^=1;assert(parse(empty,16,1)==OTS_INVALID);empty[i]^=1;++field_controls;}
    uint8_t bad[24]={0};memcpy(bad,"OpusTags",8);put32(bad+8,UINT32_MAX);assert(parse(bad,16,1)==OTS_INVALID);++field_controls;
    put32(bad+8,0);put32(bad+12,UINT32_MAX);assert(parse(bad,16,0)==OTS_INVALID);++field_controls;
    put32(bad+12,1);put32(bad+16,UINT32_MAX);assert(parse(bad,20,1)==OTS_INVALID);++field_controls;
    put32(bad+12,2);put32(bad+16,0);assert(parse(bad,20,0)==OTS_INVALID);++field_controls;
    assert(parse(bad,24,1)==OTS_COMPLETE);++field_controls; /* Two zero-length UTF-8 vectors. */
    size_t bytes=0;uint8_t *p=tags(7,11,13,257,&bytes);
    const uint8_t scalar[4]={0xf4,0x8f,0xbf,0xbf};memcpy(p+14,scalar,4);memcpy(p+16u+7u+4u+2u,scalar,4);
    for(size_t split=1;split<=bytes+1u;++split)assert(parse(p,bytes,split)==OTS_COMPLETE);
    ++field_controls;free(p);
    size_t count=65536u,large=16u+count*4u;uint8_t *many=calloc(large,1);assert(many);memcpy(many,"OpusTags",8);put32(many+12,(uint32_t)count);
    assert(parse(many,large,257)==OTS_COMPLETE);++field_controls;free(many);
}
static void limits(void) {
    uint8_t header[16]={0},block[4096];memcpy(header,"OpusTags",8);memset(block,0xff,sizeof(block));
    for(unsigned excess=0;excess<2;++excess) {
        opus_tags_parser s={0};size_t used=0;assert(otp_feed(&s,header,16,&used)==OTS_MORE && used==16);
        while(s.bytes<OPUS_TAGS_MAX_BYTES){size_t n=OPUS_TAGS_MAX_BYTES-(size_t)s.bytes;if(n>sizeof(block))n=sizeof(block);assert(otp_feed(&s,block,n,&used)==OTS_MORE && used==n);}
        if(excess){assert(otp_feed(&s,block,1,&used)==OTS_LIMIT && !used && s.bytes==OPUS_TAGS_MAX_BYTES && otp_finish(&s)==OTS_LIMIT);}
        else assert(otp_finish(&s)==OTS_COMPLETE);
        ++limit_controls;
    }
    opus_tags_parser s={0};put32(header+8,OPUS_TAGS_MAX_BYTES-16);size_t used=0;
    assert(otp_feed(&s,header,12,&used)==OTS_MORE && used==12);memset(block,'x',sizeof(block));
    while(s.remaining){size_t n=s.remaining;if(n>sizeof(block))n=sizeof(block);assert(otp_feed(&s,block,n,&used)==OTS_MORE && used==n);}
    const uint8_t zero[4]={0};assert(otp_feed(&s,zero,4,&used)==OTS_MORE && used==4 && s.bytes==OPUS_TAGS_MAX_BYTES && otp_finish(&s)==OTS_COMPLETE);++limit_controls;
}

typedef struct {uint8_t *data;size_t size,capacity;unsigned pages;} physical;
static void page(physical *p,unsigned flags,uint64_t gp,const uint8_t *body,size_t bytes,bool complete) {
    uint8_t lacing[255];size_t left=bytes;unsigned count=0;
    while(left>=255){assert(count<255);lacing[count++]=255;left-=255;}
    if(complete){assert(count<255);lacing[count++]=(uint8_t)left;}else assert(!left);
    size_t header=27u+count,total=header+bytes;if(p->size+total>p->capacity){p->capacity=(p->size+total)*2u;p->data=realloc(p->data,p->capacity);assert(p->data);}
    uint8_t *to=p->data+p->size;memset(to,0,header);memcpy(to,"OggS",4);to[5]=(uint8_t)flags;put64(to+6,gp);put32(to+14,31);put32(to+18,p->pages++);to[26]=(uint8_t)count;
    if(count)memcpy(to+27,lacing,count);
    if(bytes)memcpy(to+header,body,bytes);
    ogg_page checked={.header=to,.header_len=(long)header,.body=to+header,.body_len=(long)bytes};ogg_page_checksum_set(&checked);p->size+=total;
}
static physical make(const uint8_t *body,size_t bytes,size_t stride,unsigned nil_flags) {
    physical p={0};uint8_t head[22]={0};memcpy(head,"OpusHead",8);head[8]=1;head[9]=1;head[18]=head[19]=1;page(&p,2,0,head,22,true);
    page(&p,nil_flags,0,NULL,0,false);size_t at=0;
    while(bytes-at>stride){page(&p,at?1u:0u,UINT64_MAX,body+at,stride,false);at+=stride;page(&p,nil_flags,UINT64_MAX,NULL,0,false);}
    page(&p,(at?1u:0u)|4u,0,body+at,bytes-at,true);return p;
}
static void creator_walk(const physical *p,const uint8_t *body,size_t bytes) {
    ogg_sync_state sync;ogg_stream_state stream;assert(!ogg_sync_init(&sync) && !ogg_stream_init(&stream,31));size_t at=0;unsigned pages=0,packets=0;
    while(at<p->size) {
        size_t n=p->size-at;if(n>257)n=257;char *buffer=ogg_sync_buffer(&sync,(long)n);assert(buffer);memcpy(buffer,p->data+at,n);assert(!ogg_sync_wrote(&sync,(long)n));at+=n;
        for(;;){ogg_page current;int status=ogg_sync_pageout(&sync,&current);assert(status>=0);if(!status)break;++pages;assert(!ogg_stream_pagein(&stream,&current));
            for(;;){ogg_packet packet;status=ogg_stream_packetout(&stream,&packet);assert(status>=0);if(!status)break;if(packets==1)assert(packet.bytes==(long)bytes && !memcmp(packet.packet,body,bytes));++packets;}}
    }
    assert(pages==p->pages && packets==2 && ogg_stream_eos(&stream));assert(!ogg_stream_clear(&stream) && !ogg_sync_clear(&sync));++libogg_walks;
}
static void verified(const uint8_t *body,size_t bytes,size_t stride,unsigned nil,size_t chunk,opus_tags_status expected,bool corrupt) {
    physical p=make(body,bytes,stride,nil);creator_walk(&p,body,bytes);
    if(corrupt)p.data[p.size-1]^=1;
    ogg_page_input input={0};opi_reset(&input,7);opus_tags_stream s={0};size_t at=0;bool failed=false;opus_tags_status result=OTS_MORE;
    for(;;) {
        size_t count=p.size-at;if(chunk && count>chunk)count=chunk;size_t used=0;ogg_page_input_status status=opi_feed(&input,count?p.data+at:NULL,count,&used);assert(used<=count);at+=used;
        if(status<0){assert(corrupt && status==OPI_INVALID && !input.ready);failed=true;break;}
        if(status==OPI_PAGE) {
            uint64_t token=input.event.token;size_t held=input.size;
            if(input.event.flags&OOPT_HEAD) {
                assert(ots_begin(&s,&input));opus_tags_stream saved=s;assert(!ots_begin(&s,&input) && !memcmp(&s,&saved,sizeof(s)));
            } else {
                opus_tags_stream saved=s;
                result=ots_page(&s,&input);
                assert(input.ready && input.event.token==token && input.size==held);
                if(result<0){assert(!corrupt && result==expected && !memcmp(&s,&saved,sizeof(s)));failed=true;break;}
                assert(result==OTS_MORE || result==OTS_COMPLETE);opus_tags_stream committed=s;
                assert(ots_page(&s,&input)==OTS_ARGUMENT && !memcmp(&s,&committed,sizeof(s)));
            }
            assert(opi_ack(&input,7,token));++actual_acks;
        } else {assert(status==OPI_MORE);if(at==p.size)break;assert(used);}
    }
    if(expected==OTS_COMPLETE && !corrupt)assert(!failed && result==OTS_COMPLETE && s.complete && s.parser.bytes==bytes && at==p.size && opi_finish(&input)==OPI_FINISHED);
    else assert(failed && (corrupt || input.ready));
    ots_reset(&s);opi_reset(&input,8);free(p.data);++page_schedules;
}
static void pages(void) {
    const size_t chunks[3]={0,1,257};
    for(unsigned large=0;large<2;++large) {
        size_t bytes=0;uint8_t *p=tags(large?70000:253,large?70000:257,13,257,&bytes);
        const uint8_t unicode[4]={0xf0,0x90,0x80,0x80};memcpy(p+254,unicode,4); /* A real UTF-8 scalar straddles 255-byte lacing. */
        for(unsigned style=0;style<2;++style)for(unsigned feed=0;feed<3;++feed)verified(p,bytes,style?65025:255,style,chunks[feed],OTS_COMPLETE,false);
        p[256]=0xff;for(unsigned feed=0;feed<3;++feed)verified(p,bytes,255,1,chunks[feed],OTS_UTF8,false);
        free(p);
    }
    size_t bytes=0;uint8_t *p=tags(0,257,0,0,&bytes);put32(p+16,UINT32_MAX);
    verified(p,bytes,255,0,257,OTS_INVALID,false);free(p);
    p=tags(7,11,13,256,&bytes);verified(p,bytes,255,1,257,OTS_COMPLETE,true);free(p);
}
int main(int argc,char **argv) {
    assert(argc==2);vectors(argv[1]);fields();limits();pages();
    printf("{\"suite\":\"opus-tags-stream\",\"passed\":true,\"python_utf8_vectors\":%" PRIu64 ",\"declared_text_packets\":%" PRIu64
        ",\"parser_schedules\":%" PRIu64 ",\"field_controls\":%u,\"size_policy_controls\":%u,\"verified_page_schedules\":%" PRIu64
        ",\"creator_libogg_walks\":%" PRIu64 ",\"actual_page_acks\":%" PRIu64 ",\"maximum_header_bytes\":%u,\"parser_bytes\":%zu,\"stream_bytes\":%zu,\"whole_comment_allocation\":false,\"binary_tail_permitted\":true,\"decoder_executed\":false}\n",
        vector_cases,text_packets,parser_schedules,field_controls,limit_controls,page_schedules,libogg_walks,actual_acks,(unsigned)OPUS_TAGS_MAX_BYTES,sizeof(opus_tags_parser),sizeof(opus_tags_stream));return 0;
}
