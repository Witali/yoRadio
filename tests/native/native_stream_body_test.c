#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "stream_body.h"
#include "json_buffer.h"

static uint8_t expected[40], captured[40], wire[5000];
static size_t used, title_count, wire_size;
static char titles[3][ICY_TITLE_CAPACITY];
static bool reject;
static bool audio(void *context,const uint8_t *data,size_t size) {
    assert(context==expected);
    if (reject) return false;
    assert(used+size<=sizeof(captured));
    memcpy(captured+used,data,size); used+=size; return true;
}
static void title(void *context,const char *text) {
    assert(context==expected && title_count<3);
    assert(strlen(text)<ICY_TITLE_CAPACITY);
    strcpy(titles[title_count++],text);
}
static void reset(void) { used=title_count=0; reject=false; memset(captured,0,sizeof(captured)); }
static void verify(void) {
    assert(used==sizeof(expected) && !memcmp(captured,expected,used));
    assert(title_count==3 && !strcmp(titles[0],"First \"title\"") && !titles[1][0]);
    assert(strlen(titles[2])==191);
    for (unsigned i=0;i<191;++i) assert(titles[2][i]=='A');
}

int main(int argc,char **argv) {
    assert(argc==2);
    const char *invalid[]={"","-1","+1","1x","4294967296","999999999999999999999"};
    uint32_t interval=9;
    for(unsigned i=0;i<sizeof(invalid)/sizeof(invalid[0]);++i) {
        assert(!stream_body_interval(invalid[i],&interval) && interval==9);
    }
    assert(!stream_body_interval(NULL,&interval));
    assert(stream_body_interval(" \t4294967295\t ",&interval) && interval==UINT32_MAX);
    assert(stream_body_interval("0",&interval) && !interval);
    assert(stream_body_interval(" 5 ",&interval) && interval==5);
    for(unsigned i=0;i<sizeof(expected);++i) expected[i]=(uint8_t)(0x80+i);
    const uint8_t adts[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc};
    memcpy(expected,adts,sizeof(adts));
    for(unsigned block=0;block<8;++block) {
        memcpy(wire+wire_size,expected+block*5,5); wire_size+=5;
        unsigned metadata=block==0 || block==2 ? 32 : block==3 ? 32 : block==4 ? 4080 : 0;
        wire[wire_size++]=(uint8_t)(metadata/16);
        if (!metadata) continue;
        uint8_t *p=wire+wire_size; memset(p,0,metadata);
        if (block==0) memcpy(p,"StreamTitle='First \"title\"';",28);
        if (block==2) memcpy(p,"StreamTitle='';",15);
        if (block==3) memcpy(p,"StreamUrl='fake OggS fLaC ID3';",29);
        if (block==4) {
            memcpy(p,"StreamTitle='",13); memset(p+13,'A',4000);
            p[4013]='\'';p[4014]=';';
        }
        wire_size+=metadata;
    }
    for(size_t split=0;split<=wire_size;++split) {
        stream_body_t body; stream_body_init(&body,5); reset();
        assert(stream_body_feed(&body,wire,split,audio,title,expected));
        assert(stream_body_feed(&body,wire+split,wire_size-split,audio,title,expected));
        verify(); assert(!body.metadata_remaining);
    }
    const size_t chunks[]={1,7,2048};
    for(unsigned c=0;c<3;++c) {
        stream_body_t body; stream_body_init(&body,5); reset();
        for(size_t offset=0;offset<wire_size;) {
            size_t n=wire_size-offset; if(n>chunks[c])n=chunks[c];
            assert(stream_body_feed(&body,wire+offset,n,audio,title,expected)); offset+=n;
        }
        verify();
    }
    stream_body_t body; stream_body_init(&body,0); reset();
    assert(stream_body_feed(&body,expected,sizeof(expected),audio,title,expected));
    assert(used==sizeof(expected) && !title_count);
    stream_body_init(&body,UINT32_MAX); reset();
    assert(stream_body_feed(&body,expected,sizeof(expected),audio,NULL,expected));
    assert(body.audio_remaining==UINT32_MAX-sizeof(expected));
    stream_body_init(&body,5); reset(); reject=true;
    assert(!stream_body_feed(&body,wire,wire_size,audio,title,expected) && !title_count);
    stream_body_init(&body,5); reset();
    assert(stream_body_feed(&body,wire,wire_size-30,audio,title,expected));
    assert(body.metadata_remaining && title_count==2); // No truncated title publication.
    puts("PASS ICY body: every split, 1/7/2048-byte reads, exact audio replay, zero/max metadata, clear/unknown/truncated titles, backpressure, bounded interval");

    const char *valid="quote \" slash \\ line\nПривет 🌍";
    char encoded[1024]; json_buffer_t out;
    json_buffer_init(&out,encoded,sizeof(encoded)); json_buffer_string(&out,valid);
    assert(!out.failed); printf("VALID=%s\n",encoded);
    size_t required=out.length;
    for(size_t cap=0;cap<=required+1;++cap) {
        struct { uint8_t before; char data[1024]; uint8_t after; } guard;
        memset(&guard,0x5a,sizeof(guard));
        json_buffer_init(&out,guard.data,cap); json_buffer_string(&out,valid);
        assert(guard.before==0x5a && guard.after==0x5a);
        for(size_t i=cap;i<sizeof(guard.data);++i) assert((uint8_t)guard.data[i]==0x5a);
        assert(out.failed==(cap<=required));
        if(!out.failed)assert(!strcmp(encoded,guard.data));
    }
    char controls[32];for(unsigned i=0;i<31;++i)controls[i]=(char)(i+1);controls[31]=0;
    json_buffer_init(&out,encoded,sizeof(encoded));json_buffer_string(&out,controls);
    assert(!out.failed);printf("CONTROLS=%s\n",encoded);
    const char malformed[]={ (char)0xc0,(char)0x80,(char)0xed,(char)0xa0,(char)0x80,(char)0xf0,(char)0x90,0 };
    json_buffer_init(&out,encoded,sizeof(encoded));json_buffer_string(&out,malformed);
    assert(!out.failed);printf("INVALID=%s\n",encoded);
    FILE *f=fopen(argv[1],"w");assert(f);uint32_t random=7;
    for(unsigned trial=0;trial<1000;++trial) {
        char text[97];for(unsigned i=0;i<96;++i){random=random*1664525U+1013904223U;text[i]=(char)(random>>24);}text[96]=0;
        json_buffer_init(&out,encoded,sizeof(encoded));json_buffer_string(&out,text);
        assert(!out.failed);assert(fprintf(f,"%s\n",encoded)>0);
    }
    assert(!fclose(f));
    puts("PASS JSON buffer: exact bounds, all control bytes, valid Unicode, invalid/truncated UTF-8 and 1000 deterministic inputs");
    return 0;
}
