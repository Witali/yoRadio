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
static void unit(void) {
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
    }
    free(data);return 0;
}
