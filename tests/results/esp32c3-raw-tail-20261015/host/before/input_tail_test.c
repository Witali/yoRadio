#include "audio_completion.h"
#define STREAM_CHUNK_SIZE 2048
#define pdMS_TO_TICKS(x) (x)
typedef enum {NATIVE_CODEC_AUTO,NATIVE_CODEC_MP3,NATIVE_CODEC_AAC,
              NATIVE_CODEC_FLAC,NATIVE_CODEC_OGG} native_codec_t;
typedef struct {uint32_t generation; native_codec_t codec; uint16_t data_size;
                uint8_t end_of_stream; uint8_t data[];} encoded_packet_t;
static adaptive_input_t *s_encoded;
static atomic_uint s_generation;
#define encoded_acquire adaptive_input_acquire
static BaseType_t encoded_commit(adaptive_input_t *input, encoded_packet_t *p) {
    return adaptive_input_commit_size(input,p,sizeof(*p)+p->data_size);
}
static bool send_encoded(uint32_t gen,native_codec_t codec,const uint8_t *data,size_t size,uint8_t eos) {
    encoded_packet_t *p=NULL;
    assert(adaptive_input_acquire(s_encoded,(void **)&p,sizeof(*p)+size,0));
    p->generation=gen;p->codec=codec;p->data_size=size;p->end_of_stream=eos;
    if(size)memcpy(p->data,data,size);
    return encoded_commit(s_encoded,p)==pdTRUE;
}
#include "stream_encoded_router.h"

static void create(void) {
    size_t capacity=sizeof(encoded_packet_t)+STREAM_CHUNK_SIZE;
    s_encoded=adaptive_input_create(4*capacity,4*capacity,capacity);assert(s_encoded);
    atomic_store(&s_generation,42);atomic_store(&fail_after,0);stream_route_reset();
}
static void destroy(void) {
    assert(!adaptive_input_stats(s_encoded).occupied);
    adaptive_input_destroy(s_encoded);assert(!atomic_load(&live_allocations));
    atomic_store(&fail_after,-1);
}
static void expect_packet(unsigned gen,native_codec_t codec,unsigned reason,const char *data) {
    size_t used;encoded_packet_t *p=adaptive_input_receive(s_encoded,&used,0);assert(p);
    assert(p->generation==gen && p->codec==codec && p->end_of_stream==reason);
    assert(used==sizeof(*p)+strlen(data) && p->data_size==strlen(data));
    assert(!memcmp(p->data,data,p->data_size));assert(adaptive_input_return(s_encoded,p));
}
static void publish(unsigned gen,native_codec_t codec,unsigned reason,const char *data) {
    assert(send_encoded(gen,codec,(const uint8_t *)data,strlen(data),reason));
}
static bool route_payload(stream_route_context_t *route,const uint8_t *data,size_t size) {
    return *route->codec==NATIVE_CODEC_AAC ? stream_route_emit(route,data,size)
                                         : stream_route_feed(route,data,size);
}
static void router_cases(native_codec_t codec) {
    // A lone ready packet is never withheld from the consumer.
    create();
    stream_route_context_t r={.generation=42,.codec=&codec};
    publish(42,codec,AUDIO_CONTINUE,"first");
    assert(route_payload(&r,(const uint8_t *)"second",6));assert(stream_route_flush(&r));
    assert(adaptive_input_stats(s_encoded).ready==2);
    assert(route_payload(&r,(const uint8_t *)"+tail",5));assert(stream_route_flush(&r));
    assert(adaptive_input_stats(s_encoded).ready==2);
    expect_packet(42,codec,AUDIO_CONTINUE,"first");expect_packet(42,codec,AUDIO_CONTINUE,"second+tail");destroy();

    // Cancellation restores the previously committed prefix, including after
    // a generation change. The consumer never observes unpublished suffixes.
    for(unsigned stop=0;stop<2;++stop) {
        create();r=(stream_route_context_t){.generation=42,.codec=&codec};
        publish(42,codec,AUDIO_CONTINUE,"first");publish(42,codec,AUDIO_CONTINUE,"old");
        assert(route_payload(&r,(const uint8_t *)"new",3));
        if(stop) {atomic_store(&s_generation,43);assert(!stream_route_flush(&r));}
        else stream_route_cancel(&r);
        assert(!r.packet && !r.reopened_bytes);
        expect_packet(42,codec,AUDIO_CONTINUE,"first");expect_packet(42,codec,AUDIO_CONTINUE,"old");destroy();
    }
    // Do not append across generation/family/drain/EOF barriers.
    for(unsigned mode=0;mode<4;++mode) {
        create();r=(stream_route_context_t){.generation=42,.codec=&codec};
        unsigned gen=mode==0?41:42;
        native_codec_t old=mode==1?NATIVE_CODEC_MP3:codec;
        unsigned end=mode==2?AUDIO_DRAIN_CODEC:mode==3?AUDIO_END_EOF:AUDIO_CONTINUE;
        const char *payload=mode>=2?"":"old";
        publish(42,codec,AUDIO_CONTINUE,"first");publish(gen,old,end,payload);
        assert(route_payload(&r,(const uint8_t *)"new",3));assert(stream_route_flush(&r));
        assert(adaptive_input_stats(s_encoded).ready==3);
        expect_packet(42,codec,AUDIO_CONTINUE,"first");expect_packet(gen,old,end,payload);
        expect_packet(42,codec,AUDIO_CONTINUE,"new");destroy();
    }
}

static void short_passthrough_reads(native_codec_t codec) {
    create();
    uint8_t input[4096];for(size_t i=0;i<sizeof(input);++i)input[i]=(uint8_t)(i%251);
    for(size_t offset=0;offset<sizeof(input);offset+=512) {
        // The production caller creates a new context and flushes each read.
        stream_route_context_t route={.generation=42,.codec=&codec};
        assert(stream_route_feed(&route,input+offset,512));assert(stream_route_flush(&route));
        if(offset==1024)assert(adaptive_input_stats(s_encoded).ready==2);
    }
    assert(adaptive_input_stats(s_encoded).ready==3);
    size_t offset=0,packets=0;
    for(;;) {
        size_t size;encoded_packet_t *packet=adaptive_input_receive(s_encoded,&size,0);
        if(!packet)break;
        assert(packet->generation==42 && packet->codec==codec && packet->end_of_stream==AUDIO_CONTINUE);
        assert(size==sizeof(*packet)+packet->data_size && offset+packet->data_size<=sizeof(input));
        assert(!memcmp(packet->data,input+offset,packet->data_size));
        offset+=packet->data_size;++packets;assert(adaptive_input_return(s_encoded,packet));
    }
    assert(offset==sizeof(input) && packets==3);destroy();
}

static void queue_cases(void) {
    create();void *p=(void *)1;size_t used=1;
    assert(!adaptive_input_reopen_tail(NULL,&p,&used) && !p && !used);
    assert(!adaptive_input_reopen_tail(s_encoded,NULL,&used));
    assert(!adaptive_input_reopen_tail(s_encoded,&p,NULL));
    assert(!adaptive_input_reopen_tail(s_encoded,&p,&used));
    publish(42,NATIVE_CODEC_AAC,AUDIO_CONTINUE,"head");
    assert(!adaptive_input_reopen_tail(s_encoded,&p,&used));
    alignas(encoded_packet_t) uint8_t control[sizeof(encoded_packet_t)+128];
    assert(adaptive_input_attach_control(s_encoded,control,sizeof(control)));
    assert(adaptive_input_acquire_control(s_encoded,&p,8,0));memcpy(p,"control",8);
    assert(adaptive_input_commit(s_encoded,p));
    assert(!adaptive_input_reopen_tail(s_encoded,&p,&used));
    publish(42,NATIVE_CODEC_AAC,AUDIO_CONTINUE,"tail");
    assert(adaptive_input_reopen_tail(s_encoded,&p,&used));
    assert(used==sizeof(encoded_packet_t)+4);
    // Consumer may drain every earlier node while the tail is reopened.
    expect_packet(42,NATIVE_CODEC_AAC,AUDIO_CONTINUE,"head");
    size_t size;void *q=adaptive_input_receive(s_encoded,&size,0);
    assert(q==control && size==8 && !memcmp(q,"control",8));assert(adaptive_input_return(s_encoded,q));
    assert(!adaptive_input_receive(s_encoded,&size,0));
    assert(!adaptive_input_release_one(s_encoded));
    assert(adaptive_input_commit_size(s_encoded,p,used));
    q=adaptive_input_receive(s_encoded,&size,0);assert(q==p && size==used);
    assert(!adaptive_input_reopen_tail(s_encoded,&p,&used));
    assert(adaptive_input_return(s_encoded,q));destroy();

    create();publish(42,NATIVE_CODEC_AAC,AUDIO_CONTINUE,"head");
    assert(adaptive_input_acquire(s_encoded,&p,2060,0));memset(p,0x37,2060);
    assert(adaptive_input_commit(s_encoded,p));
    assert(!adaptive_input_reopen_tail(s_encoded,&p,&used));
    expect_packet(42,NATIVE_CODEC_AAC,AUDIO_CONTINUE,"head");
    q=adaptive_input_receive(s_encoded,&size,0);assert(q && size==2060);
    assert(adaptive_input_return(s_encoded,q));destroy();
}

enum {STRESS_BYTES=600000};
static atomic_uint reopen_count;
static void *consumer(void *unused) {
    (void)unused;size_t position=0;
    while(position<STRESS_BYTES) {
        size_t used;uint8_t *p=adaptive_input_receive(s_encoded,&used,1000);assert(p);
        assert(position+used<=STRESS_BYTES);
        for(size_t i=0;i<used;++i)assert(p[i]==(uint8_t)((position+i)%251));
        position+=used;assert(adaptive_input_return(s_encoded,p));
    }
    return NULL;
}
static void stress(void) {
    create();pthread_t thread;assert(!pthread_create(&thread,NULL,consumer,NULL));
    for(size_t position=0;position<STRESS_BYTES;) {
        void *p=NULL;size_t used=0;
        if(adaptive_input_reopen_tail(s_encoded,&p,&used))atomic_fetch_add(&reopen_count,1);
        else assert(adaptive_input_acquire(s_encoded,&p,2060,1000));
        size_t count=17;if(count>2060-used)count=2060-used;
        if(count>STRESS_BYTES-position)count=STRESS_BYTES-position;
        for(size_t i=0;i<count;++i)((uint8_t *)p)[used+i]=(uint8_t)((position+i)%251);
        assert(adaptive_input_commit_size(s_encoded,p,used+count));position+=count;
    }
    assert(!pthread_join(thread,NULL));destroy();
    printf("PASS input tail: FIFO, barriers, original-prefix restoration, control exclusion, consumer ownership; %u concurrent reopens, %u exact bytes\n",atomic_load(&reopen_count),STRESS_BYTES);
}
int main(void) {
    queue_cases();
    router_cases(NATIVE_CODEC_AAC);
    router_cases(NATIVE_CODEC_FLAC);router_cases(NATIVE_CODEC_OGG);
    short_passthrough_reads(NATIVE_CODEC_FLAC);short_passthrough_reads(NATIVE_CODEC_OGG);
    stress();
    puts("PASS FLAC/Ogg passthrough: 8 short reads pack into 3 slots; exact bytes and all barriers preserved");
}
