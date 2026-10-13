// Read-only comparison adapter: report decisions of the actual two headers.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "stream_probe.h"
#include "stream_frames.h"

typedef struct { size_t headers, bytes; } capture_t;
static bool begin(void *opaque, const stream_frame_info_t *info) {
    capture_t *s=opaque; assert(info->bytes); ++s->headers; return true;
}
static bool emit(void *opaque, const uint8_t *data, size_t size) {
    capture_t *s=opaque; assert(data && size); s->bytes+=size; return true;
}
int main(int argc,char **argv) {
    assert(argc==2);
    FILE *f=fopen(argv[1],"rb");assert(f);
    assert(!fseek(f,0,SEEK_END));long length=ftell(f);assert(length>0);rewind(f);
    uint8_t *data=malloc((size_t)length);assert(data);
    assert(fread(data,1,(size_t)length,f)==(size_t)length);fclose(f);
    stream_probe_t probe={0};size_t consumed=0;
    stream_probe_result_t result=stream_probe_feed(&probe,data,(size_t)length,&consumed);
    stream_frames_t walker={0};capture_t capture={0};size_t walked=0;
    size_t start=consumed-probe.used;
    if(result==STREAM_PROBE_MP3 || result==STREAM_PROBE_AAC)
        stream_frames_feed(&walker,data+start,(size_t)length-start,&walked,begin,emit,&capture);
    printf("{\"probe\":%u,\"start\":%zu,\"probe_consumed\":%zu,"
           "\"walker\":%u,\"walked\":%zu,\"announced_headers\":%zu,"
           "\"emitted_bytes\":%zu,\"complete\":%s}\n",
           result,start,consumed,walker.result,walked,capture.headers,capture.bytes,
           ((result==STREAM_PROBE_MP3 || result==STREAM_PROBE_AAC) &&
             stream_frames_complete(&walker))?"true":"false");
    free(data);return 0;
}
