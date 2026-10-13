#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "stream_frames.h"

typedef struct {
    const uint8_t *expected;
    size_t size, delivered, frames;
    bool reject_begin, reject_data, dump;
} sink_t;

static bool begin(void *opaque, const stream_frame_info_t *info) {
    sink_t *s = opaque;
    if (s->reject_begin) return false;
    assert(info->bytes >= 4);
    if (s->dump) printf("FRAME %zu %u %u %u %u %u\n",s->delivered,
        info->bytes,info->codec,info->core_rate,info->core_channels,info->core_samples);
    ++s->frames;
    return true;
}
static bool emit(void *opaque, const uint8_t *data, size_t size) {
    sink_t *s = opaque;
    if (s->reject_data) return false;
    assert(size && s->delivered + size <= s->size);
    assert(!memcmp(s->expected + s->delivered, data, size));
    s->delivered += size;
    return true;
}
static void feed(stream_frames_t *s, sink_t *sink, const uint8_t *data, size_t n) {
    size_t count = 0;
    assert(stream_frames_feed(s,data,n,&count,begin,emit,sink)==STREAM_FRAME_MORE);
    assert(count==n);
}

static void tag_header(uint8_t *p, unsigned version, uint32_t body, bool footer) {
    memcpy(p,"ID3",3); p[3]=version; p[4]=0; p[5]=footer ? 0x10 : 0;
    p[6]=(body>>21)&127; p[7]=(body>>14)&127;
    p[8]=(body>>7)&127; p[9]=body&127;
}

static void tags(void) {
    const uint8_t audio[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc,1,2,3,4,5};
    uint8_t expected[24]; memcpy(expected,audio,12); memcpy(expected+12,audio,12);
    for(unsigned version=2;version<=4;++version) {
        for(unsigned footer=0;footer<=(version==4);++footer) {
            uint8_t tag[32]; tag_header(tag,version,12,footer);
            memcpy(tag+10,audio,12); // Valid sync in tag must never reach decoder.
            if(footer) {memcpy(tag+22,tag,10);memcpy(tag+22,"3DI",3);}
            size_t length=22+10*footer;
            uint8_t input[120]; size_t size=0;
            memcpy(input+size,tag,length);size+=length;
            memcpy(input+size,audio,12);size+=12;
            memcpy(input+size,tag,length);size+=length;
            memcpy(input+size,audio,12);size+=12;
            memcpy(input+size,tag,length);size+=length;
            for(size_t split=0;split<=size+1;++split) {
                stream_frames_t state={0};sink_t sink={.expected=expected,.size=24};
                if(split<=size) {
                    feed(&state,&sink,input,split);feed(&state,&sink,input+split,size-split);
                } else for(size_t i=0;i<size;++i) feed(&state,&sink,input+i,1);
                assert(stream_frames_complete(&state) && sink.frames==2 && sink.delivered==24);
            }
            for(size_t end=1;end<length;++end) {
                stream_frames_t state={0};sink_t sink={0};
                feed(&state,&sink,tag,end);
                assert(!stream_frames_complete(&state) && !sink.frames && !sink.delivered);
            }
        }
    }
    // Reject malformed envelopes and oversize tags, with sticky failures.
    for(unsigned mutation=0;mutation<10;++mutation) {
        uint8_t tag[10];tag_header(tag,4,0,false);
        if(mutation==0) tag[3]=5;
        if(mutation==1) tag[4]=255;
        if(mutation==2) tag[5]=1;
        if(mutation>=3 && mutation<=6) tag[mutation+3]=128;
        if(mutation==7) {tag[3]=2;tag[5]=0x20;}
        if(mutation==8) {tag[3]=3;tag[5]=0x10;}
        if(mutation==9) tag_header(tag,4,STREAM_ID3_RUN_BYTES,false);
        stream_frames_t state={0};sink_t sink={0};size_t count;
        assert(stream_frames_feed(&state,tag,10,&count,begin,emit,&sink)==STREAM_FRAME_INVALID);
        assert(count==10 && !sink.frames && !sink.delivered);
        assert(stream_frames_feed(&state,audio,12,&count,begin,emit,&sink)==STREAM_FRAME_INVALID && !count);
    }
    // Consume a full resource-bound run using a small reusable chunk. A second
    // tag exceeds the run bound, but an intervening audio frame resets it.
    uint8_t tag[10],chunk[257]={0};
    tag_header(tag,4,STREAM_ID3_RUN_BYTES-10,false);
    stream_frames_t state={0};sink_t sink={.expected=audio,.size=12};
    feed(&state,&sink,tag,10);
    while(state.skip) feed(&state,&sink,chunk,state.skip<sizeof(chunk)?state.skip:sizeof(chunk));
    assert(stream_frames_complete(&state));
    stream_frames_t limited=state; size_t count;
    uint8_t empty[10];tag_header(empty,4,0,false);
    assert(stream_frames_feed(&limited,empty,10,&count,begin,emit,&sink)==STREAM_FRAME_INVALID);
    feed(&state,&sink,audio,12);assert(state.tag_bytes==0);
    feed(&state,&sink,tag,10);
    while(state.skip) feed(&state,&sink,chunk,state.skip<sizeof(chunk)?state.skip:sizeof(chunk));
    assert(stream_frames_complete(&state) && sink.frames==1 && sink.delivered==12);
    // Adjacent empty tags and ID3-looking bytes inside an audio payload.
    state=(stream_frames_t){0};sink=(sink_t){0};
    for(unsigned i=0;i<100;++i) feed(&state,&sink,empty,10);
    assert(stream_frames_complete(&state) && state.tag_bytes==1000);
    uint8_t bait[12];memcpy(bait,audio,12);memcpy(bait+7,"ID3",3);
    sink=(sink_t){.expected=bait,.size=12};feed(&state,&sink,bait,12);
    assert(stream_frames_complete(&state) && sink.frames==1 && sink.delivered==12);
    puts("ID3 PASS splits/truncation/versions/footer/bounds/payload isolation");
}
static void id3v1_tails(void) {
    enum { MP3_BYTES = 417, TAG_BYTES = 128 };
    uint8_t mp3[MP3_BYTES], tag[TAG_BYTES], input[MP3_BYTES+TAG_BYTES];
    memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\x00",4);
    memcpy(mp3+100,"TAG",3); // Payload is never searched for metadata.
    memset(tag,0,sizeof(tag));memcpy(tag,"TAG",3);
    memcpy(tag+3,"\xff\xf1\x4c\x80\x01\x9f\xfc",7);
    memcpy(tag+50,"ID3\x04\0\0\0\0\0\0",10);
    for(unsigned version=0;version<2;++version) {
        tag[125]=0;tag[126]=version ? 17 : 0;tag[127]=255;
        memcpy(input,mp3,sizeof(mp3));memcpy(input+sizeof(mp3),tag,sizeof(tag));
        for(size_t split=0;split<=sizeof(input)+1;++split) {
            stream_frames_t state={0};sink_t sink={.expected=mp3,.size=sizeof(mp3)};
            if(split<=sizeof(input)) {
                feed(&state,&sink,input,split);feed(&state,&sink,input+split,sizeof(input)-split);
            } else for(size_t i=0;i<sizeof(input);++i) feed(&state,&sink,input+i,1);
            assert(stream_frames_complete(&state) && sink.frames==1 && sink.delivered==sizeof(mp3));
        }
    }
    for(size_t length=1;length<TAG_BYTES;++length) {
        stream_frames_t state={0};sink_t sink={.expected=mp3,.size=sizeof(mp3)};
        feed(&state,&sink,mp3,sizeof(mp3));feed(&state,&sink,tag,length);
        assert(!stream_frames_complete(&state) && sink.frames==1 && sink.delivered==sizeof(mp3));
    }
    // No ID3v1 heuristic at startup or after AAC. Both must remain invalid.
    const uint8_t aac[]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    for(unsigned after_aac=0;after_aac<2;++after_aac) {
        stream_frames_t state={0};sink_t sink={.expected=aac,.size=sizeof(aac)};size_t count;
        if(after_aac) feed(&state,&sink,aac,sizeof(aac));
        assert(stream_frames_feed(&state,tag,sizeof(tag),&count,begin,emit,&sink)==STREAM_FRAME_INVALID);
    }
    for(unsigned over=0;over<2;++over) {
        stream_frames_t state={0};sink_t sink={.expected=mp3,.size=sizeof(mp3)};size_t count;
        feed(&state,&sink,mp3,sizeof(mp3));state.tag_bytes=STREAM_ID3_RUN_BYTES-TAG_BYTES+over;
        if(!over) {feed(&state,&sink,tag,sizeof(tag));assert(stream_frames_complete(&state));}
        else assert(stream_frames_feed(&state,tag,sizeof(tag),&count,begin,emit,&sink)==STREAM_FRAME_INVALID);
    }
    // A concatenated next track can change format after a complete tail.
    uint8_t expected[MP3_BYTES+sizeof(aac)];memcpy(expected,mp3,sizeof(mp3));memcpy(expected+sizeof(mp3),aac,sizeof(aac));
    stream_frames_t state={0};sink_t sink={.expected=expected,.size=sizeof(expected)};
    feed(&state,&sink,mp3,sizeof(mp3));feed(&state,&sink,tag,sizeof(tag));feed(&state,&sink,aac,sizeof(aac));
    assert(stream_frames_complete(&state) && sink.frames==2 && sink.delivered==sizeof(expected));
    puts("ID3v1 PASS splits/truncation/payload isolation/codec context/bounds/next track");
}

static void unit(void) {
    id3v1_tails();
    tags();
    stream_frame_info_t info;
    const uint8_t mp3[]={0xff,0xfb,0x90,0};
    const uint8_t mpeg2[]={0xff,0xf3,0x80,0xc0};
    const uint8_t mpeg25[]={0xff,0xe3,0x18,0xc0};
    assert(stream_frame_header(mp3,4,&info)==STREAM_FRAME_READY);
    assert(info.bytes==417 && info.core_rate==44100 && info.core_samples==1152);
    assert(stream_frame_header(mpeg2,4,&info)==STREAM_FRAME_READY);
    assert(info.bytes==208 && info.core_rate==22050 && info.core_channels==1);
    assert(stream_frame_header(mpeg25,4,&info)==STREAM_FRAME_READY);
    assert(info.bytes==72 && info.core_rate==8000 && info.core_samples==576);
    uint8_t free_format[]={0xff,0xfb,0,0};
    assert(stream_frame_header(free_format,4,&info)==STREAM_FRAME_FREE_FORMAT);
    assert(info.bytes==0 && info.codec==STREAM_FRAME_MP3);
    uint8_t adts[]={0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc};
    assert(stream_frame_header(adts,7,&info)==STREAM_FRAME_READY);
    assert(info.bytes==12 && info.core_rate==48000 && info.core_channels==2);
    adts[3]=0; // PCE: channels must be unknown, not silently stereo.
    assert(stream_frame_header(adts,7,&info)==STREAM_FRAME_READY && !info.core_channels);
    adts[2]|=1; adts[3]=0xc0; adts[6]=0xff;
    assert(stream_frame_header(adts,7,&info)==STREAM_FRAME_READY);
    assert(info.core_channels==8 && info.core_samples==4096);
    adts[1]=0xf0; adts[4]=0; adts[5]=0xe0; // CRC header needs at least nine bytes.
    assert(stream_frame_header(adts,7,&info)==STREAM_FRAME_INVALID);
    adts[1]=0xf1; adts[2]=0x4c; adts[3]=0x80; adts[4]=1; adts[5]=0x9f; adts[6]=0xfc;
    uint8_t data[846]; memset(data,0x55,sizeof(data));
    memcpy(data,mp3,4); memcpy(data+417,adts,7); memcpy(data+429,mp3,4);
    memcpy(data+80,adts,7); memcpy(data+500,mp3,4); // Sync-shaped payload is not a boundary.
    for(size_t split=0;split<=sizeof(data)+1;++split) {
        stream_frames_t state={0}; sink_t sink={.expected=data,.size=sizeof(data)};
        if(split<=sizeof(data)) {
            feed(&state,&sink,data,split); feed(&state,&sink,data+split,sizeof(data)-split);
        } else for(size_t i=0;i<sizeof(data);++i) feed(&state,&sink,data+i,1);
        assert(sink.frames==3 && sink.delivered==sizeof(data) && stream_frames_complete(&state));
    }
    for(size_t end=1;end<sizeof(data);++end) {
        stream_frames_t state={0}; sink_t sink={.expected=data,.size=sizeof(data)};
        feed(&state,&sink,data,end);
        assert(stream_frames_complete(&state)==(end==417 || end==429));
    }
    for(unsigned failure=0;failure<2;++failure) {
        stream_frames_t state={0}; size_t consumed=0;
        sink_t sink={.expected=data,.size=sizeof(data),.reject_begin=!failure,.reject_data=failure};
        assert(stream_frames_feed(&state,data,sizeof(data),&consumed,begin,emit,&sink)==STREAM_FRAME_SINK_FAILED);
        assert(!sink.delivered);
        assert(stream_frames_feed(&state,data,sizeof(data),&consumed,begin,emit,&sink)==STREAM_FRAME_SINK_FAILED && !consumed);
    }
    stream_frames_t state={0}; sink_t sink={0}; size_t consumed=0;
    assert(stream_frames_feed(&state,free_format,4,&consumed,begin,emit,&sink)==STREAM_FRAME_FREE_FORMAT);
    assert(consumed==4 && !sink.frames && !sink.delivered && state.used==4);
    uint32_t random=17;
    for(unsigned i=0;i<100000;++i) {
        uint8_t header[7];
        for(unsigned j=0;j<7;++j) {random=random*1664525U+1013904223U;header[j]=random>>24;}
        for(size_t n=0;n<=7;++n) {
            stream_frame_result_t result=stream_frame_header(header,n,&info);
            if(result==STREAM_FRAME_READY) assert(info.bytes>=4 && info.bytes<=8191 && info.core_rate);
        }
    }
    printf("UNIT PASS state=%zu info=%zu\n",sizeof(stream_frames_t),sizeof(stream_frame_info_t));
}

int main(int argc,char **argv) {
    unit();
    if(argc==1) return 0;
    assert(argc==2);
    FILE *f=fopen(argv[1],"rb"); assert(f);
    assert(!fseek(f,0,SEEK_END)); long size=ftell(f); assert(size>0); rewind(f);
    uint8_t *data=malloc((size_t)size); assert(data);
    assert(fread(data,1,(size_t)size,f)==(size_t)size); fclose(f);
    const size_t chunks[]={1,7,2048};
    for(unsigned run=0;run<3;++run) {
        stream_frames_t state={0}; sink_t sink={.expected=data,.size=(size_t)size,.dump=run==2};
        for(size_t offset=0;offset<(size_t)size;) {
            size_t count=(size_t)size-offset; if(count>chunks[run])count=chunks[run];
            feed(&state,&sink,data+offset,count);offset+=count;
        }
        assert(stream_frames_complete(&state) && sink.delivered==(size_t)size);
        printf("CORPUS PASS chunk=%zu frames=%zu bytes=%zu\n",chunks[run],sink.frames,sink.delivered);
        // Repeat the real compressed payload with a tag before every frame.
        // Emit must reproduce exactly the original bytes, including transitions.
        state=(stream_frames_t){0};sink=(sink_t){.expected=data,.size=(size_t)size};
        for(size_t offset=0;offset<(size_t)size;) {
            stream_frame_info_t info;
            assert(stream_frame_header(data+offset,(size_t)size-offset,&info)==STREAM_FRAME_READY);
            uint8_t tag[27];tag_header(tag,4,7,true);
            memcpy(tag+10,"ID3\xff\xfb\x90\x00",7);
            memcpy(tag+17,tag,10);memcpy(tag+17,"3DI",3);
            for(size_t pos=0;pos<sizeof(tag);) {
                size_t count=sizeof(tag)-pos;if(count>chunks[run])count=chunks[run];
                feed(&state,&sink,tag+pos,count);pos+=count;
            }
            assert(info.bytes<=(size_t)size-offset);
            for(size_t pos=0;pos<info.bytes;) {
                size_t count=info.bytes-pos;if(count>chunks[run])count=chunks[run];
                feed(&state,&sink,data+offset+pos,count);pos+=count;
            }
            offset+=info.bytes;
        }
        assert(stream_frames_complete(&state) && sink.delivered==(size_t)size);
        printf("TAGGED CORPUS PASS chunk=%zu frames=%zu bytes=%zu\n",chunks[run],sink.frames,sink.delivered);
    }
    free(data);return 0;
}
