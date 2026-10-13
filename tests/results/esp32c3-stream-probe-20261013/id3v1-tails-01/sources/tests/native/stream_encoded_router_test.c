#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdatomic.h>
#include <stdalign.h>
#include <string.h>
#include <stdlib.h>
#include "stream_probe.h"
#include "audio_completion.h"
#define CONFIG_YORADIO_FRAME_ROUTER 1
#define STREAM_CHUNK_SIZE 2048
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
               NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG } native_codec_t;
typedef struct { uint32_t generation; native_codec_t codec; uint16_t data_size;
                 uint8_t end_of_stream; uint8_t data[]; } encoded_packet_t;
static atomic_uint s_generation;
static void *s_encoded;
static alignas(max_align_t) uint8_t storage[sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE];
static bool leased, fail_commit, cancel_acquire, cancel_after_acquire;
static unsigned waits, packets, markers;
static uint8_t captured[1024*1024];static native_codec_t kinds[1024*1024];
static size_t captured_size, marker_offset[8];static native_codec_t marker_codec[8];
static int encoded_acquire(void *queue,void **packet,size_t size,unsigned timeout) {
    (void)queue;(void)timeout;assert(!leased && size<=sizeof(storage));*packet=NULL;
    if(cancel_acquire) {atomic_fetch_add(&s_generation,1);return 0;}
    if(waits) {--waits;return 0;}
    leased=true;*packet=storage;
    if(cancel_after_acquire)atomic_fetch_add(&s_generation,1);
    return pdTRUE;
}
static int encoded_commit(void *queue,void *p) {
    (void)queue;assert(leased && p==storage);
    if(fail_commit)return 0;
    encoded_packet_t *packet=p;assert(packet->generation==42);
    assert(packet->codec!=NATIVE_CODEC_AUTO);++packets;
    if(packet->end_of_stream) {
        assert(packet->end_of_stream==AUDIO_DRAIN_CODEC && !packet->data_size && markers<8);
        marker_offset[markers]=captured_size;marker_codec[markers++]=packet->codec;
    } else {
        assert(packet->data_size && captured_size+packet->data_size<=sizeof(captured));
        memcpy(captured+captured_size,packet->data,packet->data_size);
        for(unsigned i=0;i<packet->data_size;++i)kinds[captured_size+i]=packet->codec;
        captured_size+=packet->data_size;
    }
    leased=false;return pdTRUE;
}
static bool adaptive_input_cancel(void *queue,void *p) {
    (void)queue;assert(leased && p==storage);leased=false;return true;
}
static const char *codec_name(native_codec_t codec) {(void)codec;return "codec";}
static void state_set_audio(unsigned generation,bool playing,const char *name) {
    assert(generation==42 && playing && name);
}
/* PRODUCTION_SEND */

static void reset(void) {
    assert(!leased);atomic_store(&s_generation,42);captured_size=packets=markers=waits=0;
    fail_commit=cancel_acquire=cancel_after_acquire=false;stream_route_reset();
}
int main(int argc,char **argv) {
    if(argc==4) {
        FILE *file=fopen(argv[1],"rb");assert(file);
        assert(!fseek(file,0,SEEK_END));long length=ftell(file);rewind(file);
        assert(length>0 && (size_t)length<sizeof(captured));
        uint8_t *data=malloc(length);assert(data);assert(fread(data,1,length,file)==(size_t)length);fclose(file);
        reset();stream_probe_t probe={0};native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;
        size_t chunk=strtoul(argv[3],NULL,10);assert(chunk && chunk<=STREAM_CHUNK_SIZE);
        for(size_t offset=0;offset<(size_t)length;) {
            size_t count=(size_t)length-offset;if(count>chunk)count=chunk;
            assert(send_stream_audio(42,&codec,data+offset,count,&first,&probe));assert(!leased);offset+=count;
        }
        assert(stream_route_complete(codec));
        file=fopen(argv[2],"wb");assert(file);assert(fwrite(captured,1,captured_size,file)==captured_size);fclose(file);
        for(unsigned i=0;i<markers;++i)printf("MARKER %zu %u\n",marker_offset[i],marker_codec[i]);
        printf("CORPUS PASS bytes=%zu packets=%u markers=%u chunk=%zu\n",captured_size,packets,markers,chunk);
        free(data);return 0;
    }
    assert(argc==1);
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\x00",4);
    uint8_t aac[12]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    uint8_t tail[128]={0};memcpy(tail,"TAG",3);memcpy(tail+20,aac,sizeof(aac));
    for(size_t tail_size=1;tail_size<=sizeof(tail);++tail_size) {
        reset();stream_probe_t probe={0};native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;
        assert(send_stream_audio(42,&codec,mp3,sizeof(mp3),&first,&probe));
        assert(send_stream_audio(42,&codec,tail,tail_size,&first,&probe));
        assert(!leased && !markers && captured_size==sizeof(mp3) && !memcmp(captured,mp3,sizeof(mp3)));
        assert(stream_route_end(codec,AUDIO_END_EOF)==
               (tail_size==sizeof(tail) ? AUDIO_END_EOF : AUDIO_END_FRAME_TRUNCATED));
    }
    uint8_t input[868],expected[858];
    memcpy(expected,mp3,417);memcpy(expected+417,aac,12);memcpy(expected+429,aac,12);memcpy(expected+441,mp3,417);
    memcpy(input,mp3,417);memcpy(input+417,"ID3\x04\0\0\0\0\0\0",10);memcpy(input+427,expected+417,441);
    for(size_t split=0;split<=sizeof(input)+1;++split) {
        reset();stream_probe_t probe={0};native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;
        if(split<=sizeof(input)) {
            assert(send_stream_audio(42,&codec,input,split,&first,&probe));
            assert(!leased);
            assert(send_stream_audio(42,&codec,input+split,sizeof(input)-split,&first,&probe));
        } else for(size_t i=0;i<sizeof(input);++i) {
            assert(send_stream_audio(42,&codec,input+i,1,&first,&probe));assert(!leased);
        }
        assert(!leased && captured_size==sizeof(expected) && !memcmp(captured,expected,sizeof(expected)));
        assert(markers==2 && marker_offset[0]==417 && marker_offset[1]==441);
        assert(marker_codec[0]==NATIVE_CODEC_MP3 && marker_codec[1]==NATIVE_CODEC_AAC);
        for(unsigned i=0;i<sizeof(expected);++i)
            assert(kinds[i]==(i>=417 && i<441?NATIVE_CODEC_AAC:NATIVE_CODEC_MP3));
        assert(codec==NATIVE_CODEC_MP3 && stream_route_complete(codec));
        if(split==sizeof(input))assert(packets==5); // Three payloads, two drain markers.
    }
    // One network read with many small ADTS frames uses one queue slot.
    reset();uint8_t many[1200];for(unsigned i=0;i<100;++i)memcpy(many+12*i,aac,12);
    stream_probe_t probe={0};native_codec_t codec=NATIVE_CODEC_AUTO;bool first=true;
    waits=3;assert(send_stream_audio(42,&codec,many,sizeof(many),&first,&probe));
    assert(!waits && packets==1 && !markers && captured_size==1200 && !memcmp(captured,many,1200));
    reset();uint8_t large[3600];for(unsigned i=0;i<3;++i)memcpy(large+1200*i,many,1200);
    probe=(stream_probe_t){0};codec=NATIVE_CODEC_AUTO;first=true;
    assert(send_stream_audio(42,&codec,large,sizeof(large),&first,&probe));
    assert(packets==2 && !markers && captured_size==sizeof(large) && !memcmp(captured,large,sizeof(large)));
    // An explicit MP3 hint does not send an empty drain before first actual AAC.
    reset();probe=(stream_probe_t){0};codec=NATIVE_CODEC_MP3;first=true;
    assert(send_stream_audio(42,&codec,aac,12,&first,&probe));assert(codec==NATIVE_CODEC_AAC && !markers);
    // Free-format header and remaining data are replayed exactly, with no scan.
    reset();probe=(stream_probe_t){0};codec=NATIVE_CODEC_AUTO;first=true;
    uint8_t free_mp3[417];memcpy(free_mp3,mp3,417);free_mp3[2]&=15;
    assert(send_stream_audio(42,&codec,free_mp3,417,&first,&probe));
    assert(s_frame_router.bypass && captured_size==417 && !memcmp(captured,free_mp3,417));
    // EOF in payload or metadata remains incomplete; new connection resets it.
    reset();probe=(stream_probe_t){0};codec=NATIVE_CODEC_AUTO;first=true;
    assert(send_stream_audio(42,&codec,mp3,416,&first,&probe));assert(!stream_route_complete(codec));
    assert(stream_route_end(codec,AUDIO_END_EOF)==AUDIO_END_FRAME_TRUNCATED);
    assert(stream_route_end(codec,AUDIO_END_READ_FAILED)==AUDIO_END_READ_FAILED);
    assert(audio_completion_is_terminal(AUDIO_END_FRAME_TRUNCATED));
    assert(!strcmp(audio_completion_status(AUDIO_END_FRAME_TRUNCATED),"truncated audio frame"));
    reset();assert(stream_route_complete(NATIVE_CODEC_MP3));
    assert(stream_route_end(NATIVE_CODEC_MP3,AUDIO_END_EOF)==AUDIO_END_EOF);
    // FLAC/Ogg keep the original opaque send path, no invented MP3 routing.
    for(unsigned c=NATIVE_CODEC_FLAC;c<=NATIVE_CODEC_OGG;++c) {
        reset();probe=(stream_probe_t){0};codec=c;first=true;
        assert(send_stream_audio(42,&codec,many,1200,&first,&probe));
        assert(codec==c && packets==1 && !markers && !memcmp(captured,many,1200));
    }
    // Lease is returned on commit failure, parser rejection, and cancellation.
    for(unsigned failure=0;failure<4;++failure) {
        reset();probe=(stream_probe_t){0};codec=NATIVE_CODEC_AUTO;first=true;
        fail_commit=failure==0;cancel_acquire=failure==1;cancel_after_acquire=failure==3;
        uint8_t invalid[418];memcpy(invalid,mp3,417);invalid[417]=0;
        assert(!send_stream_audio(42,&codec,invalid,failure==2?418:417,&first,&probe));
        assert(!leased && !packets);
    }
    puts("PASS router: every split, byte replay, ordered drains, coalescing, backpressure, cancellation, free-format bypass, opaque codecs");
}
