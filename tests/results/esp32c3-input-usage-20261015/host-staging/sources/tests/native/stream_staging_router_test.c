#include "stream_confirm.h"
#include "audio_completion.h"
/* STAGING_HEADER */

#define STREAM_CHUNK_SIZE 2048
#define pdMS_TO_TICKS(x) (x)
typedef enum {NATIVE_CODEC_AUTO,NATIVE_CODEC_MP3,NATIVE_CODEC_AAC,
              NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG} native_codec_t;
typedef struct {uint32_t generation; native_codec_t codec; uint16_t data_size;
                uint8_t end_of_stream; uint8_t data[];} encoded_packet_t;
static adaptive_input_t *s_encoded;
static atomic_uint s_generation;
#define encoded_acquire adaptive_input_acquire
static BaseType_t encoded_commit(adaptive_input_t *input, encoded_packet_t *packet) {
    return adaptive_input_commit_size(input,packet,sizeof(*packet)+packet->data_size);
}
static bool send_encoded(uint32_t gen,native_codec_t codec,const uint8_t *data,size_t size,uint8_t eos) {
    encoded_packet_t *packet=NULL;
    // Any attempt to route around the dedicated control node while the
    // candidate owns all slots must fail this test, never hang indefinitely.
    assert(adaptive_input_acquire(s_encoded,(void **)&packet,sizeof(*packet)+size,0));
    packet->generation=gen;packet->codec=codec;packet->data_size=size;packet->end_of_stream=eos;
    if(size)memcpy(packet->data,data,size);
    return adaptive_input_commit(s_encoded,packet)==pdTRUE;
}
#include "stream_encoded_router.h"

enum {CONTROL_PAYLOAD=128,MAX_BYTES=8202};
static alignas(encoded_packet_t) uint8_t control[sizeof(encoded_packet_t)+CONTROL_PAYLOAD];
static uint8_t input[MAX_BYTES],expected[MAX_BYTES],captured[MAX_BYTES];
static native_codec_t kinds[MAX_BYTES];
static size_t captured_size,markers[4];
static unsigned marker_count,packets;
static atomic_bool finished;
static bool cancel_first;
static void *consume(void *unused) {
    (void)unused;
    while (true) {
        size_t size;
        encoded_packet_t *p=adaptive_input_receive(s_encoded,&size,10);
        if(!p) {if(atomic_load(&finished))break;else continue;}
        assert((void *)p==control && p->generation==42);
        assert(p->data_size<=CONTROL_PAYLOAD && size<=sizeof(control));
        ++packets;
        if(p->end_of_stream) {
            assert(p->end_of_stream==AUDIO_DRAIN_CODEC && !p->data_size && marker_count<4);
            markers[marker_count++]=captured_size;
        } else {
            assert(captured_size+p->data_size<=sizeof(captured));
            memcpy(captured+captured_size,p->data,p->data_size);
            for(unsigned i=0;i<p->data_size;++i)kinds[captured_size+i]=p->codec;
            captured_size+=p->data_size;
        }
        if(cancel_first && packets==1) atomic_store(&s_generation,43);
        assert(adaptive_input_return(s_encoded,p));
    }
    return NULL;
}
static size_t add_frame(size_t offset,const uint8_t *frame,size_t n) {
    memcpy(input+offset,frame,n);memcpy(expected+offset,frame,n);return offset+n;
}
int main(void) {
    uint8_t mp3[417];memset(mp3,0x55,sizeof(mp3));memcpy(mp3,"\xff\xfb\x90\0",4);
    uint8_t aac[12]={0xff,0xf1,0x4c,0x80,1,0x9f,0xfc,1,2,3,4,5};
    size_t length=0;
    for(unsigned i=0;i<9;++i)length=add_frame(length,mp3,sizeof(mp3));
    size_t to_aac=length;
    for(unsigned i=0;i<330;++i)length=add_frame(length,aac,sizeof(aac));
    size_t to_mp3=length;
    length=add_frame(length,mp3,sizeof(mp3));
    assert(length>3*STREAM_CHUNK_SIZE && length<sizeof(input));
    const size_t chunks[]={1,7,2048};
    for(unsigned cancelled=0;cancelled<2;++cancelled)for(unsigned chunk=0;chunk<3;++chunk) {
        size_t capacity=sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE;
        s_encoded=adaptive_input_create(4*capacity,4*capacity,capacity);assert(s_encoded);
        assert(adaptive_input_attach_control(s_encoded,control,sizeof(control)));
        stream_staging_t storage={0};
        assert(stream_staging_init(&storage,s_encoded,sizeof(encoded_packet_t),STREAM_CHUNK_SIZE));
        assert(stream_staging_append(&storage,input,length)==length);
        assert(adaptive_input_stats(s_encoded).occupied==4);
        atomic_store(&fail_after,0);
        captured_size=marker_count=packets=0;cancel_first=cancelled;
        atomic_store(&finished,false);atomic_store(&s_generation,42);stream_route_reset();
        native_codec_t codec=NATIVE_CODEC_MP3;
        stream_route_context_t route={.generation=42,.codec=&codec,.control_payload_bytes=CONTROL_PAYLOAD};
        pthread_t thread;assert(!pthread_create(&thread,NULL,consume,NULL));
        bool ok=true;
        for(size_t offset=0;offset<length && ok;) {
            size_t available;uint8_t *span=stream_staging_span(&storage,offset,&available);
            if(available>chunks[chunk])available=chunks[chunk];
            ok=stream_route_feed(&route,span,available);
            offset+=available;
        }
        if(ok)ok=stream_route_flush(&route);
        if(!ok)stream_route_cancel(&route);
        stream_staging_cancel(&storage); // Consumer still owns only its copied control fragment.
        atomic_store(&finished,true);assert(!pthread_join(thread,NULL));
        assert(!route.packet && !adaptive_input_stats(s_encoded).occupied);
        if(cancelled) {
            assert(!ok && captured_size<=CONTROL_PAYLOAD && !marker_count);
        } else {
            assert(ok && captured_size==length && !memcmp(captured,expected,length));
            assert(marker_count==2 && markers[0]==to_aac && markers[1]==to_mp3);
            assert(stream_route_complete(codec));
            for(size_t i=0;i<length;++i)assert(kinds[i]==(i>=to_aac && i<to_mp3?NATIVE_CODEC_AAC:NATIVE_CODEC_MP3));
        }
        adaptive_input_destroy(s_encoded);assert(!atomic_load(&live_allocations));
        atomic_store(&fail_after,-1);
    }
    puts("PASS staging router: four held data slots, independent 128-byte fragments, MP3/AAC/MP3 ordered drain markers, concurrent consumer cancellation, exact bytes, chunks 1/7/2048; ASan/UBSan");
}
