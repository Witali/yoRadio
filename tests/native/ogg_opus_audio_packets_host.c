/* Real verified-page owner versus creator libogg, using complete real packets. */
#include <stddef.h>
#include <stdlib.h>
static void *packet_realloc(void *,size_t);
static void packet_free(void *);
#define OPK_REALLOC packet_realloc
#define OPK_FREE packet_free
#include "ogg_opus_audio_packets.h"
#include "opus_family1_mapping.h"
#include <ogg/ogg.h>
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct {uint8_t *body;size_t size,capacity;unsigned pages;} physical;
typedef struct {uint8_t head[40];uint8_t *packets[11];size_t bytes[11];unsigned count,channels,streams,coupled,pre_skip,logical;} corpus;
typedef struct {unsigned packets,borrowed,copied,pages,realloc_calls,failures;size_t capacity;opk_status status;bool abandoned;} observation;
static unsigned cases;
static unsigned fail_on,realloc_calls,failures;
static bool retry_failure;
static void *live_prefix;
static size_t live_capacity;
static ogg_opus_audio_packets *fault_owner;
static uint8_t saved_prefix[61440];
static size_t saved_size,saved_capacity,saved_cursor;
static unsigned saved_segment;
static uint64_t saved_token;
static void *packet_realloc(void *pointer,size_t bytes) {
    assert(pointer==live_prefix && bytes<=61440);++realloc_calls;
    if(fail_on==realloc_calls) {
        assert(fault_owner && fault_owner->source->ready);saved_size=fault_owner->prefix_size;saved_capacity=fault_owner->capacity;
        saved_cursor=fault_owner->payload_at;saved_segment=fault_owner->segment;saved_token=fault_owner->token_sequence;
        if(saved_size)memcpy(saved_prefix,fault_owner->prefix,saved_size);
        ++failures;return NULL;
    }
    void *next=realloc(pointer,bytes);assert(next);live_prefix=next;live_capacity=bytes;return next;
}
static void packet_free(void *pointer) {
    if(!pointer)return;
    assert(pointer==live_prefix);free(pointer);live_prefix=NULL;live_capacity=0;
}
static void put32(uint8_t *p,uint32_t value){for(unsigned i=0;i<4;++i)p[i]=(uint8_t)(value>>(8*i));}
static void put64(uint8_t *p,uint64_t value){for(unsigned i=0;i<8;++i)p[i]=(uint8_t)(value>>(8*i));}
static uint32_t checksum(const uint8_t *p,size_t n) {
    uint32_t table[256];for(unsigned i=0;i<256;++i){uint32_t c=i<<24;for(unsigned bit=0;bit<8;++bit)c=(c<<1)^((c&UINT32_C(0x80000000))?UINT32_C(0x04c11db7):0);table[i]=c;}
    uint32_t value=0;for(size_t i=0;i<n;++i){uint8_t byte=i>=22&&i<26?0:p[i];value=(value<<8)^table[(value>>24)^byte];}return value;
}
static void page(physical *out,unsigned flags,uint64_t gp,const uint8_t *laces,unsigned count,const uint8_t *payload,size_t bytes) {
    size_t sum=0;for(unsigned i=0;i<count;++i)sum+=laces[i];assert(count<=255 && sum==bytes);size_t size=27u+count+bytes,need=out->size+size;
    if(need>out->capacity){size_t capacity=out->capacity?out->capacity:1024;while(capacity<need)capacity*=2;void *p=realloc(out->body,capacity);assert(p);out->body=p;out->capacity=capacity;}
    uint8_t *p=out->body+out->size;memset(p,0,27);memcpy(p,"OggS",4);p[5]=(uint8_t)flags;put64(p+6,gp);put32(p+14,77);put32(p+18,out->pages++);p[26]=(uint8_t)count;
    if(count)memcpy(p+27,laces,count);
    if(bytes)memcpy(p+27+count,payload,bytes);
    put32(p+22,checksum(p,size));out->size+=size;
}
static unsigned laces(uint8_t *out,size_t bytes) {unsigned n=0;while(bytes>=255){out[n++]=255;bytes-=255;}out[n++]=(uint8_t)bytes;return n;}
static physical make(const corpus *source,unsigned style) {
    physical out={0};uint8_t head[40]={0};memcpy(head,"OpusHead",8);head[8]=1;head[9]=(uint8_t)source->channels;head[10]=(uint8_t)source->pre_skip;head[11]=(uint8_t)(source->pre_skip>>8);
    put32(head+12,48000);head[18]=1;head[19]=(uint8_t)source->streams;head[20]=(uint8_t)source->coupled;memcpy(head+21,source->head+32,source->channels);
    uint8_t lace=(uint8_t)(21+source->channels);page(&out,2,0,&lace,1,head,lace);
    if(style==4) {
        uint8_t *tags=calloc(70000,1);assert(tags);memcpy(tags,"OpusTags",8);put32(tags+8,69984);memset(tags+12,'A',69984);
        uint8_t table[255];memset(table,255,255);page(&out,0,UINT64_MAX,table,255,tags,65025);unsigned n=laces(table,4975);page(&out,1,0,table,n,tags+65025,4975);free(tags);
    } else {uint8_t tags[16]="OpusTags";lace=16;page(&out,0,0,&lace,1,tags,16);}
    for(unsigned index=0;index<source->count;) {
        bool final=index+1==source->count;uint64_t gp=final?source->pre_skip+source->logical:(uint64_t)(index+1)*960;
        const uint8_t *body=source->packets[index];size_t bytes=source->bytes[index];
        if(style==5) {
            size_t at=0;
            while(bytes-at>255){lace=255;page(&out,at?1u:0u,UINT64_MAX,&lace,1,body+at,255);at+=255;}
            uint8_t table[2];unsigned n=laces(table,bytes-at);page(&out,(at?1u:0u)|(final?4u:0u),gp,table,n,body+at,bytes-at);++index;
        } else if((style==1 || style==2) && bytes>255) {
            lace=255;page(&out,0,UINT64_MAX,&lace,1,body,255);page(&out,style==1?0:1,UINT64_MAX,NULL,0,NULL,0);
            uint8_t table[255];unsigned n=laces(table,bytes-255);page(&out,1u|(final?4u:0u),gp,table,n,body+255,bytes-255);++index;
        } else if(style==3) {
            unsigned batch=source->count-index;if(batch>3)batch=3;uint8_t table[255],payload[65025];unsigned n=0;size_t used=0;
            for(unsigned i=0;i<batch;++i){assert(used+source->bytes[index+i]<=sizeof(payload));n+=laces(table+n,source->bytes[index+i]);memcpy(payload+used,source->packets[index+i],source->bytes[index+i]);used+=source->bytes[index+i];}
            index+=batch;final=index==source->count;gp=final?source->pre_skip+source->logical:(uint64_t)index*960;page(&out,final?4u:0u,gp,table,n,payload,used);
        } else {uint8_t table[255];unsigned n=laces(table,bytes);page(&out,final?4u:0u,gp,table,n,body,bytes);++index;}
    }
    return out;
}
static void creator_walk(const physical *bytes,const corpus *source) {
    ogg_sync_state sync;ogg_stream_state stream;assert(ogg_sync_init(&sync)==0 && ogg_stream_init(&stream,77)==0);unsigned pages=0,packets=0;size_t at=0;
    while(at<bytes->size) {
        size_t n=bytes->size-at;if(n>257)n=257;char *buffer=ogg_sync_buffer(&sync,(long)n);assert(buffer);memcpy(buffer,bytes->body+at,n);assert(ogg_sync_wrote(&sync,(long)n)==0);at+=n;
        for(;;) {
            ogg_page current;int status=ogg_sync_pageout(&sync,&current);assert(status>=0);if(!status)break;++pages;assert(ogg_stream_pagein(&stream,&current)==0);
            for(;;){ogg_packet packet;status=ogg_stream_packetout(&stream,&packet);assert(status>=0);if(!status)break;
                if(packets>=2){unsigned id=packets-2;assert(id<source->count && packet.bytes==(long)source->bytes[id] && !memcmp(packet.packet,source->packets[id],source->bytes[id]));}++packets;}
        }
    }
    assert(pages==bytes->pages && packets==source->count+2 && ogg_stream_eos(&stream));assert(ogg_stream_clear(&stream)==0 && ogg_sync_clear(&sync)==0);
}
static observation observe(const physical *physical_bytes,const corpus *expected,size_t chunk,bool policy,bool crc_error) {
    ogg_page_input input={0};opi_reset(&input,9);ogg_opus_audio_packets owner={0};size_t at=0;observation r={0};bool stopped=false;
    assert(!live_prefix && !live_capacity);realloc_calls=failures=0;fault_owner=&owner;
    while(!stopped) {
        size_t n=physical_bytes->size-at;if(chunk && n>chunk)n=chunk;size_t used=0;
        ogg_page_input_status status=opi_feed(&input,n?physical_bytes->body+at:NULL,n,&used);assert(used<=n);at+=used;
        if(status<0){assert(crc_error && !input.ready);stopped=true;continue;}
        if(status==OPI_PAGE) {
            oopt_event e=input.event;assert(e.crc_verified);bool audio=false;
            if(e.flags&OOPT_HEAD){opus_family1_plan plan;size_t offset=27u+input.page[26];assert(of1_plan_header(input.page+offset,input.size-offset,&plan)==OF1_OK);}
            else if(e.flags&OOPT_TAGS){assert(opk_start_link(&owner,&input));}
            else if(owner.active) {
                audio=true;assert(opk_begin_page(&owner,&input)==OPK_NEED_PAGE);++r.pages;
                for(;;) {
                    opus_audio_packet_view view;opk_status next=opk_next(&owner,&view);r.status=next;
                    if(next==OPK_MEMORY) {
                        assert(fail_on && failures==1 && input.ready && owner.page_active && !owner.ready &&
                            owner.prefix_size==saved_size && owner.capacity==saved_capacity && owner.payload_at==saved_cursor && owner.segment==saved_segment &&
                            owner.token_sequence==saved_token && (!saved_size || !memcmp(owner.prefix,saved_prefix,saved_size)) &&
                            owner.prefix==live_prefix && !opk_page_exhausted(&owner) && !opk_page_released(&owner,&input));
                        if(retry_failure){fail_on=0;continue;}
                        r.abandoned=true;stopped=true;break;
                    }
                    if(next==OPK_PACKET_POLICY){assert(policy && !owner.ready);stopped=true;break;}
                    if(next==OPK_PAGE_DONE)break;
                    assert(next==OPK_PACKET && r.packets<expected->count && view.bytes==expected->bytes[r.packets] && !memcmp(view.data,expected->packets[r.packets],view.bytes));
                    uint16_t duration=0;assert(omf_family01_packet(view.data,view.bytes,(uint8_t)expected->streams,NULL,0,NULL,&duration)==OMF_OK && duration==960);
                    opus_audio_packet_view repeated;assert(opk_next(&owner,&repeated)==OPK_PACKET && repeated.token==view.token && repeated.data==view.data);
                    assert(!opk_consume(&owner,e.generation+1,e.serial,view.token) && !opk_consume(&owner,e.generation,e.serial^1u,view.token) &&
                        !opk_consume(&owner,e.generation,e.serial,view.token-1));
                    assert(!opk_page_exhausted(&owner) && !opk_page_released(&owner,&input));
                    assert(opk_consume(&owner,e.generation,e.serial,view.token) && !opk_consume(&owner,e.generation,e.serial,view.token));
                    ++r.packets;if(view.borrowed)++r.borrowed;else ++r.copied;
                }
                if(stopped)continue;
                assert(opk_page_exhausted(&owner) && !opk_page_released(&owner,&input));
                if(owner.capacity>r.capacity)r.capacity=owner.capacity;
            }
            assert(opi_ack(&input,e.generation,e.token));
            if(audio){assert(opk_page_released(&owner,&input));if(e.flags&OOPT_LINK_END)assert(opk_finish_link(&owner) && !owner.capacity);}
            if(input.capacity)memset(input.page,0xa5,input.capacity); /* The prefix must survive genuine page retirement. */
        } else {assert(status==OPI_MORE);if(at==physical_bytes->size)break;assert(used);}
    }
    if(!policy && !crc_error && !r.abandoned)assert(at==physical_bytes->size && r.packets==expected->count && !owner.active && opi_finish(&input)==OPI_FINISHED);
    if(policy)assert(r.status==OPK_PACKET_POLICY && r.packets==0 && owner.prefix_size<=255 && owner.capacity<=OMF_FAMILY01_MAX_PACKET);
    if(crc_error)assert(r.packets==0 && !input.ready && owner.prefix_size==0);
    if(r.abandoned)assert(input.ready && r.packets==0 && failures==1);
    r.realloc_calls=realloc_calls;r.failures=failures;opk_reset(&owner);opi_reset(&input,10);assert(!owner.prefix && !owner.ready && !owner.source && !live_prefix && !live_capacity);fault_owner=NULL;++cases;return r;
}
static corpus load(const char *path) {
    FILE *f=fopen(path,"rb");assert(f);corpus out={0};assert(fread(out.head,1,40,f)==40 && !memcmp(out.head,"OFAM101\0",8));
    out.channels=of1_le32(out.head+8);out.streams=of1_le32(out.head+12);out.coupled=of1_le32(out.head+16);out.pre_skip=of1_le32(out.head+20);out.logical=of1_le32(out.head+24);out.count=of1_le32(out.head+28);assert(out.count==11);
    for(unsigned i=0;i<out.count;++i){uint8_t size[4];assert(fread(size,1,4,f)==4);out.bytes[i]=of1_le32(size);out.packets[i]=malloc(out.bytes[i]);assert(out.packets[i] && fread(out.packets[i],1,out.bytes[i],f)==out.bytes[i]);}
    assert(fgetc(f)==EOF && !fclose(f));return out;
}
static corpus padded(size_t bytes) {
    corpus out={.count=1,.channels=1,.streams=1,.logical=960};out.head[32]=0;out.bytes[0]=bytes;out.packets[0]=calloc(bytes,1);assert(out.packets[0]);
    uint8_t *p=out.packets[0];p[0]=0xfb;p[1]=0x41;memset(p+2,255,240);p[242]=(uint8_t)(bytes-243-240*254);return out;
}
static void release(corpus *source){for(unsigned i=0;i<source->count;++i)free(source->packets[i]);}
int main(int argc,char **argv) {
    assert(argc==3);unsigned creator_walks=0,borrowed=0,copied=0;const size_t chunks[3]={0,1,257};
    for(unsigned fixture=0;fixture<2;++fixture) {
        corpus source=load(argv[fixture+1]);
        for(unsigned style=0;style<5;++style) {
            physical bytes=make(&source,style);creator_walk(&bytes,&source);++creator_walks;
            for(unsigned feed=0;feed<3;++feed){observation r=observe(&bytes,&source,chunks[feed],false,false);assert((style==0 || style==3 || style==4)?(r.borrowed==11 && !r.copied && !r.capacity):(r.copied==11 && !r.borrowed));borrowed+=r.borrowed;copied+=r.copied;}
            free(bytes.body);
        }
        physical bad=make(&source,0);size_t first=0;for(unsigned page_id=0;page_id<2;++page_id){size_t n=27u+bad.body[first+26];for(unsigned i=0;i<bad.body[first+26];++i)n+=bad.body[first+27+i];first+=n;}
        size_t payload=first+27u+bad.body[first+26];bad.body[payload+source.bytes[0]-1]^=1;observe(&bad,&source,257,false,true);free(bad.body);release(&source);
    }
    for(unsigned excessive=0;excessive<2;++excessive) {
        corpus source=padded(61440u+excessive);
        for(unsigned style=0;style<2;++style){physical bytes=make(&source,style);creator_walk(&bytes,&source);++creator_walks;
            for(unsigned feed=0;feed<2;++feed){observation r=observe(&bytes,&source,feed?257:0,excessive,false);if(!excessive){borrowed+=r.borrowed;copied+=r.copied;}}
            free(bytes.body);}
        release(&source);
    }
    corpus extreme={.count=1,.channels=8,.streams=255,.logical=960};const uint8_t map[8]={254,0,254,255,128,1,253,255};memcpy(extreme.head+32,map,8);
    extreme.bytes[0]=509;extreme.packets[0]=malloc(509);assert(extreme.packets[0]);
    for(unsigned s=0;s<254;++s){extreme.packets[0][s*2]=0xf8;extreme.packets[0][s*2+1]=0;}extreme.packets[0][508]=0xf8;
    for(unsigned style=0;style<3;++style){physical bytes=make(&extreme,style);creator_walk(&bytes,&extreme);++creator_walks;
        for(unsigned feed=0;feed<2;++feed){observation r=observe(&bytes,&extreme,feed?257:0,false,false);borrowed+=r.borrowed;copied+=r.copied;}
        free(bytes.body);}
    release(&extreme);
    corpus growth=padded(61440);physical ladder=make(&growth,5);creator_walk(&ladder,&growth);++creator_walks;
    observation baseline=observe(&ladder,&growth,257,false,false);assert(baseline.realloc_calls==9 && baseline.copied==1 && !baseline.failures);copied+=baseline.copied;
    unsigned retry_cases=0,abandon_cases=0;
    for(unsigned ordinal=1;ordinal<=baseline.realloc_calls;++ordinal)for(unsigned retry=0;retry<2;++retry) {
        fail_on=ordinal;retry_failure=retry!=0;observation r=observe(&ladder,&growth,257,false,false);assert(r.failures==1);
        if(retry){assert(!r.abandoned && r.packets==1 && r.copied==1 && r.realloc_calls==baseline.realloc_calls+1);copied+=r.copied;++retry_cases;}
        else {assert(r.abandoned && r.packets==0 && r.realloc_calls==ordinal);++abandon_cases;}
        printf("{\"suite\":\"packet-realloc-control\",\"ordinal\":%u,\"retry\":%s,\"packets\":%u,\"held_page_preserved\":true,\"cursor_prefix_token_preserved\":true,\"cleanup_live_bytes\":0}\n",ordinal,retry?"true":"false",r.packets);
    }
    fail_on=0;retry_failure=false;free(ladder.body);release(&growth);
    printf("{\"suite\":\"ogg-opus-audio-packets\",\"passed\":true,\"owner_schedules\":%u,\"creator_libogg_walks\":%u,\"borrowed_packets\":%u,\"copied_packets\":%u,\"maximum_packet\":61440,\"over_limit_policy\":61441,\"allocation_failure_injected\":true,\"realloc_ordinals\":%u,\"retry_cases\":%u,\"abandon_cases\":%u,\"decoder_drain_claimed\":false,\"production_selected\":false}\n",
        cases,creator_walks,borrowed,copied,baseline.realloc_calls,retry_cases,abandon_cases);return 0;
}
