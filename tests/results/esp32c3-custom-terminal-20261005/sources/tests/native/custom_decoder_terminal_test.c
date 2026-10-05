#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>

#define CONFIG_YORADIO_FLAC_DECODER_CUSTOM 1
#define YORADIO_CUSTOM_LEGACY_DECODER 1
#define CONFIG_YORADIO_AAC_DECODER_HELIX 1
#define CONFIG_YORADIO_MP3_DECODER_HELIX 1
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
enum { NATIVE_CODEC_FLAC=1, NATIVE_CODEC_AAC=2, NATIVE_CODEC_MP3=3 };
typedef int native_codec_t;
typedef struct { uint64_t decode_us; uint32_t calls, max_call_us, input_bytes; } decode_stats_t;
typedef struct { unsigned sample_rate; } esp_audio_simple_dec_info_t;
typedef struct {
    uint32_t generation;
    decode_stats_t *stats;
    esp_audio_simple_dec_info_t *stream_info;
    bool *stream_info_ready;
} custom_flac_output_context_t;
typedef custom_flac_output_context_t custom_legacy_output_context_t;
typedef struct { uint64_t decode_us; uint32_t decode_calls, max_call_us, input_bytes; } custom_flac_feed_stats_t;
typedef custom_flac_feed_stats_t custom_legacy_feed_stats_t;
typedef struct { uint8_t *workspace; } custom_flac_decoder_t;
typedef custom_flac_decoder_t custom_legacy_decoder_t;
typedef struct { uint32_t generation; uint8_t data[4]; size_t data_size; uint8_t end_of_stream; } encoded_packet_t;

static atomic_uint s_generation;
static unsigned live_decoders, feed_calls, returned, errors;
static int feed_result;
static bool arena_busy;
static uint8_t *arena;
static uint8_t queued[128];
static size_t queued_size;
static uint32_t final_failed;
static bool custom_flac_output(void *user, const void *info, const uint8_t *pcm, size_t size) {
    (void)user; (void)info;
    assert(queued_size+size <= sizeof(queued));
    memcpy(queued+queued_size,pcm,size);queued_size+=size;
    return true;
}
#define custom_legacy_output custom_flac_output
static int custom_flac_decoder_feed(custom_flac_decoder_t *decoder, const uint8_t *data, size_t size, bool eos,
        bool (*output)(void*,const void*,const uint8_t*,size_t), void *user, custom_flac_feed_stats_t *stats) {
    (void)data; (void)size; ++feed_calls;
    *stats=(custom_flac_feed_stats_t){.decode_us=12,.decode_calls=2,.max_call_us=7,.input_bytes=4};
    // Model synchronous PCM callbacks, including a second chunk on EOF. The
    // actual algorithm is unchanged; this test exercises its owner's lifetime.
    assert(output(user,NULL,decoder->workspace,16));
    if(eos) assert(output(user,NULL,decoder->workspace+16,16));
    return feed_result;
}
#define custom_legacy_decoder_feed custom_flac_decoder_feed
static void custom_flac_decoder_destroy(custom_flac_decoder_t *decoder) {
    if(!decoder)return;
    assert(live_decoders);--live_decoders;
    memset(decoder->workspace,0xa5,32);free(decoder->workspace);free(decoder);
}
#define custom_legacy_decoder_destroy custom_flac_decoder_destroy
static bool custom_legacy_decoder_discard_arena(void) {
    assert(!live_decoders); // Destroy must release the owner before discard.
    if(arena_busy)return false;
    free(arena);arena=NULL;return true;
}
static int64_t esp_timer_get_time(void) { return 10; }
static void decode_stats_report(decode_stats_t *stats, int64_t time) { (void)stats;(void)time; }
static void log_runtime_memory(const char *stage) { (void)stage; }
static void state_set_audio(uint32_t generation,bool playing,const char *status) {
    (void)generation;(void)status;assert(!playing);++errors;
}
static void return_decoded_packet(encoded_packet_t *packet,uint32_t failed_generation) {
    (void)packet;++returned;final_failed=failed_generation;
}

static custom_flac_decoder_t *make_decoder(void) {
    custom_flac_decoder_t *p=malloc(sizeof(*p));assert(p);
    p->workspace=malloc(32);assert(p->workspace);
    for(unsigned i=0;i<32;++i)p->workspace[i]=(uint8_t)(i*3);
    ++live_decoders;return p;
}

static void process(native_codec_t codec, uint32_t generation, uint32_t failed_generation,
                    encoded_packet_t *packet, custom_flac_decoder_t **handle) {
    custom_flac_decoder_t *flac_decoder=codec==NATIVE_CODEC_FLAC ? *handle : NULL;
    custom_legacy_decoder_t *legacy_decoder=codec!=NATIVE_CODEC_FLAC ? *handle : NULL;
    decode_stats_t stats={0};
    esp_audio_simple_dec_info_t stream_info={0};
    bool stream_info_ready=true, first_frame_memory_logged=true;
    do {
/* PRODUCTION_CUSTOM_BRANCHES */
    } while(false);
    *handle=codec==NATIVE_CODEC_FLAC ? flac_decoder : legacy_decoder;
}

int main(void) {
    unsigned cases=0;
    for(int codec=NATIVE_CODEC_FLAC;codec<=NATIVE_CODEC_MP3;++codec)
    for(unsigned mode=0;mode<5;++mode) {
        queued_size=returned=errors=feed_calls=0;feed_result=0;arena_busy=false;
        atomic_store(&s_generation,4);
        custom_flac_decoder_t *handle=make_decoder();
        if(codec!=NATIVE_CODEC_FLAC) { arena=malloc(4096);assert(arena); }
        encoded_packet_t packet={.generation=4,.data_size=4,.end_of_stream=mode==0 ? 0 : 1};
        // normal data, EOF, transport-end, decode failure, and cancellation
        // during a callback (next generation owns the subsequent cleanup).
        if(mode==2)packet.end_of_stream=2;
        if(mode>=3) { feed_result=-5;packet.end_of_stream=0; }
        if(mode==4)atomic_store(&s_generation,5);
        process(codec,4,0,&packet,&handle);
        bool terminal=mode>=1 && mode<=3;
        assert(returned==1 && feed_calls==1);
        assert((handle==NULL)==terminal);
        assert(live_decoders==(terminal ? 0U:1U));
        if(codec!=NATIVE_CODEC_FLAC)assert((arena==NULL)==terminal);
        assert(errors==(mode==3 ? 1U:0U));
        assert(final_failed==(mode==3 ? 4U:0U));
        size_t expected=packet.end_of_stream ? 32:16;
        assert(queued_size==expected);
        for(size_t i=0;i<expected;++i)assert(queued[i]==(uint8_t)(i*3));
        if(terminal) {
            // A repeated terminal return or Stop cannot double free or replay
            // the tail, even after failed initialization left a null handle.
            process(codec,4,mode==3 ? 4:0,&packet,&handle);
            assert(feed_calls==1 && queued_size==expected && !handle);
        }
        custom_flac_decoder_destroy(handle);handle=NULL;
        assert(custom_legacy_decoder_discard_arena());
        ++cases;
    }
    for(int codec=NATIVE_CODEC_AAC;codec<=NATIVE_CODEC_MP3;++codec) {
        queued_size=errors=returned=0;feed_result=0;arena_busy=true;
        atomic_store(&s_generation,4);
        custom_flac_decoder_t *handle=make_decoder();arena=malloc(4096);
        encoded_packet_t packet={.generation=4,.end_of_stream=1};
        process(codec,4,0,&packet,&handle);
        assert(!handle && arena && errors==1 && final_failed==4);
        arena_busy=false;assert(custom_legacy_decoder_discard_arena());++cases;
    }
    assert(!live_decoders && !arena);
    printf("PASS custom terminal ownership cases=%u queued PCM unchanged\n",cases);
}
