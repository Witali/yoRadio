#include <assert.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "native_state.h"
#include "native_health.h"
#include "audio_completion.h"
#include "custom_flac_adapter.h"

typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
               NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG } native_codec_t;
typedef int esp_err_t, esp_audio_err_t;
typedef unsigned esp_audio_simple_dec_type_t;
typedef void *esp_audio_simple_dec_handle_t;
typedef struct { unsigned dec_type; void *dec_cfg; unsigned cfg_size; bool use_frame_dec; } esp_audio_simple_dec_cfg_t;
typedef struct { uint8_t *buffer; size_t len, consumed; unsigned eos; } esp_audio_simple_dec_raw_t;
typedef struct { uint8_t *buffer; size_t len, needed_size, decoded_size; } esp_audio_simple_dec_out_t;
typedef struct { uint32_t sample_rate, bitrate; uint8_t bits_per_sample, channel; } esp_audio_simple_dec_info_t;
typedef void *RingbufHandle_t;
#define ESP_AUDIO_SIMPLE_DEC_TYPE_AAC 2
#define ESP_AUDIO_SIMPLE_DEC_TYPE_FLAC 3
#define ESP_AUDIO_SIMPLE_DEC_TYPE_OGG 4
#define ESP_AUDIO_SIMPLE_DEC_TYPE_MP3 1
#define ESP_AUDIO_ERR_OK 0
#define ESP_AUDIO_ERR_BUFF_NOT_ENOUGH -8
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define MAINTENANCE_STREAM 1U
#define MAINTENANCE_DECODER 2U
#define CONFIG_YORADIO_INPUT_PREFILL_MS 0

typedef struct {
    uint32_t generation; native_codec_t codec;
    uint16_t data_size; uint8_t end_of_stream; uint8_t data[];
} encoded_packet_t;
typedef struct {
    uint32_t generation, sample_rate; uint8_t bits_per_sample, channels;
    uint16_t data_size; uint32_t end_of_stream; uint8_t data[];
} pcm_packet_t;
#define DECODE_BUFFER_INITIAL 12288
#define PCM_PACKET_DATA_SIZE 3072
static native_state_t state, *s_state = &state;
static atomic_uint s_generation, s_failed_generation, s_decoder_released_generation;
static uint32_t s_decoder_bitrate_generation, s_decoder_bitrate_bps;
static int64_t s_decoder_bitrate_updated_us;
static RingbufHandle_t s_encoded = (void *)1, s_pcm = (void *)2;
static jmp_buf task_exit;
static unsigned vendor_opens, vendor_closes, vendor_live, terminal_reason, faults;
static unsigned packets_returned, ack_count, quiescent_checks;
static unsigned action, action_after, cancel_send, blocks;
static bool maintenance;
static uint8_t *encoded_data, *reference_pcm;
static size_t encoded_size, reference_size, pcm_position, input_position;
static size_t schedule, eof_cut = SIZE_MAX, input_limit, generation_switch_at;
static bool separate_eof, sent_eof;
static unsigned final_reason = AUDIO_END_EOF;
static unsigned source_bits, source_channels;
static uint64_t pcm_hash;
static void *pending_pcm;
extern void flac_test_begin(size_t);
extern size_t flac_test_calls(void), flac_test_live(void), flac_test_workspace(void);
extern void flac_test_finish(void);
extern unsigned flac_test_errors;

static int64_t esp_timer_get_time(void) { return 0; }
static void assert_quiet(void) {
    assert(!flac_test_live() && !flac_test_workspace() && !vendor_live && !pending_pcm);
    ++quiescent_checks;
}
static bool maintenance_active(void) { return maintenance; }
static bool maintenance_acked(unsigned bits) { assert(bits == MAINTENANCE_STREAM); return maintenance; }
static void maintenance_ack(unsigned bit) {
    assert(bit == MAINTENANCE_DECODER);
    assert_quiet(); ++ack_count;
}
static void maintenance_park(uint32_t generation) {
    assert(generation == atomic_load(&s_generation)); longjmp(task_exit, 1);
}
static void fail_generation(uint32_t generation) {
    assert(generation == atomic_load(&s_generation)); atomic_store(&s_failed_generation, generation);
}
static int esp_audio_simple_dec_open(const esp_audio_simple_dec_cfg_t *cfg, void **p) {
    assert(!flac_test_workspace() && !vendor_live); assert(cfg->dec_type);
    *p = malloc(1); if (!*p) return ESP_FAIL;
    ++vendor_opens; ++vendor_live; return ESP_OK;
}
static void esp_audio_simple_dec_close(void *p) {
    assert(vendor_live == 1); --vendor_live; ++vendor_closes; free(p);
}
static int esp_audio_simple_dec_process(void *p, esp_audio_simple_dec_raw_t *raw,
                                      esp_audio_simple_dec_out_t *out) {
    assert(p && out->len); raw->consumed = raw->len; out->decoded_size = 0; return ESP_OK;
}
static int esp_audio_simple_dec_get_info(void *p, esp_audio_simple_dec_info_t *info) {
    assert(p); *info = (esp_audio_simple_dec_info_t){48000,0,16,2}; return ESP_OK;
}
#ifdef YORADIO_CUSTOM_LEGACY_DECODER
typedef void custom_legacy_decoder_t;
typedef struct { uint32_t sample_rate, bitrate; uint8_t bits_per_sample, channels; } custom_legacy_info_t;
typedef struct { unsigned unused; } custom_legacy_feed_stats_t;
enum { CUSTOM_LEGACY_AAC, CUSTOM_LEGACY_MP3 };
static custom_legacy_decoder_t *custom_legacy_decoder_create(unsigned codec) {
    (void)codec; void *handle = NULL;
    esp_audio_simple_dec_cfg_t cfg = {.dec_type = ESP_AUDIO_SIMPLE_DEC_TYPE_AAC};
    esp_audio_simple_dec_open(&cfg, &handle); return handle;
}
static void custom_legacy_decoder_destroy(custom_legacy_decoder_t *p) { esp_audio_simple_dec_close(p); }
static int custom_legacy_decoder_feed(custom_legacy_decoder_t *p, const uint8_t *data,
        size_t size, bool eos, bool (*output)(void *,const custom_legacy_info_t *,const uint8_t *,size_t),
        void *user, custom_legacy_feed_stats_t *stats) {
    (void)data; (void)size; (void)eos; (void)output; (void)user; (void)stats;
    assert(p); return 0;
}
#endif
static int xRingbufferSendAcquire(void *ring, void **p, size_t size, unsigned wait) {
    assert(ring == s_pcm && wait == 50 && !pending_pcm);
    if (cancel_send) {
        ++blocks;
        if (blocks < 3) return 0;
        assert(flac_test_workspace());
        atomic_fetch_add(&s_generation, 1);
        if (cancel_send == 2) maintenance = true;
        cancel_send = 0; return 0;
    }
    // Queue storage is a platform seam and is not part of decoder allocation
    // failure injection. This static slot remains valid until SendComplete.
    static uint8_t slot[sizeof(pcm_packet_t) + PCM_PACKET_DATA_SIZE];
    assert(size <= sizeof(slot)); pending_pcm = slot; *p = slot; return pdTRUE;
}
static int xRingbufferSendComplete(void *ring, void *p) {
    assert(ring == s_pcm && p == pending_pcm); pcm_packet_t *packet = p;
    pending_pcm = NULL;
    assert(packet->generation == atomic_load(&s_generation));
    if (packet->end_of_stream) {
        assert_quiet(); terminal_reason = packet->end_of_stream; return pdTRUE;
    }
    assert(packet->bits_per_sample == 16 && packet->channels == source_channels);
    assert(packet->sample_rate == 48000 && packet->data_size % (source_channels * 2) == 0);
    assert(pcm_position + packet->data_size <= reference_size);
    assert(!memcmp(packet->data, reference_pcm + pcm_position, packet->data_size));
    assert(state.bits_per_sample == source_bits && state.channels == source_channels);
    assert(!strcmp(state.codec, "FLAC") && !state.format_is_pcm);
    for (size_t i = 0; i < packet->data_size; ++i) pcm_hash = (pcm_hash ^ packet->data[i]) * 1099511628211ULL;
    pcm_position += packet->data_size; return pdTRUE;
}
static void *encoded_receive(void *ring, size_t *size, unsigned wait) {
    (void)size; assert(ring == s_encoded && wait == 20);
    if (packets_returned == action_after && action) {
        assert(flac_test_workspace());
        unsigned saved = action; action = 0;
        if (saved != 3) atomic_fetch_add(&s_generation, 1);
        if (saved == 2 || saved == 3) maintenance = true;
        input_position = input_limit; sent_eof = true;
        return NULL; // The task must loop through release before next receive.
    }
    if (sent_eof) {
        if (maintenance) return NULL;
        assert(atomic_load(&s_decoder_released_generation) == atomic_load(&s_generation));
        assert_quiet(); longjmp(task_exit, 1);
    }
    size_t bytes = input_limit - input_position;
    if (bytes > schedule) bytes = schedule;
    unsigned reason = AUDIO_CONTINUE;
    if (input_position + bytes == input_limit && (!separate_eof || !bytes)) {
        reason = final_reason; sent_eof = true;
    }
    // Input packets were preallocated outside failure tracking and are reused
    // only after the decoder task returns its lease.
    static uint8_t slot[sizeof(encoded_packet_t) + 65536];
    assert(bytes <= 65535); encoded_packet_t *packet = (void *)slot;
    packet->generation = atomic_load(&s_generation);
    packet->codec = generation_switch_at && packets_returned >= generation_switch_at ? NATIVE_CODEC_AAC : NATIVE_CODEC_FLAC;
    packet->data_size = (uint16_t)bytes; packet->end_of_stream = reason;
    memcpy(packet->data, encoded_data + input_position, bytes); input_position += bytes;
    return packet;
}
static void encoded_return(void *ring, void *p) { assert(ring == s_encoded && p); ++packets_returned; }
void native_health_decoder_failure(uint32_t generation, uint32_t codec,
        native_health_decoder_stage_t stage, int32_t result, uint32_t reason, uint32_t bytes) {
    (void)stage; (void)bytes;
    assert(generation == atomic_load(&s_generation) && codec && result <= 0 && reason); ++faults;
}
size_t strlcpy(char *to, const char *from, size_t capacity) {
    size_t n = strlen(from); if (capacity) {size_t copy = n < capacity-1 ? n : capacity-1; memcpy(to,from,copy); to[copy]=0;} return n;
}
#include "production.inc"

static uint8_t *read_file(const char *path, size_t *size) {
    FILE *file = fopen(path, "rb"); assert(file); assert(!fseek(file, 0, SEEK_END));
    *size = (size_t)ftell(file); rewind(file); uint8_t *data = malloc(*size + 1); assert(data);
    assert(fread(data,1,*size,file) == *size); fclose(file); return data;
}
static size_t execute(size_t limit) {
    assert(!vendor_live); input_position = pcm_position = packets_returned = blocks = faults = terminal_reason = ack_count = quiescent_checks = 0;
    sent_eof = maintenance = false; pcm_hash = 14695981039346656037ULL;
    atomic_store(&s_generation, 7); atomic_store(&s_failed_generation, 0);
    atomic_store(&s_decoder_released_generation, 0);
    native_state_begin_audio(&state, 7, "fixture", "connecting");
    flac_test_begin(limit);
    if (!setjmp(task_exit)) decoder_task(NULL);
    assert_quiet(); size_t calls = flac_test_calls(); flac_test_finish(); return calls;
}
int main(int argc, char **argv) {
    assert(argc == 7); encoded_data = read_file(argv[1], &encoded_size);
    reference_pcm = read_file(argv[2], &reference_size);
    source_bits = (unsigned)strtoul(argv[3],NULL,10); source_channels = (unsigned)strtoul(argv[4],NULL,10);
    const char *mode = argv[5]; size_t extra = strtoul(argv[6],NULL,10);
    native_state_init(&state); input_limit = encoded_size; schedule = 127;
    if (!strcmp(mode,"pcm")) {
        schedule = extra ? extra : 127; separate_eof = extra == 0;
        execute(SIZE_MAX); assert(terminal_reason == AUDIO_END_EOF && !faults && pcm_position == reference_size && !flac_test_errors);
    } else if (!strcmp(mode,"cuts")) {
        assert(extra <= encoded_size); unsigned groups = 0;
        for (size_t cut = 1; cut < extra; ++cut) for (unsigned style = 0; style < 4; ++style) {
            input_limit = cut; schedule = style < 2 ? 65535 : 13; separate_eof = (style & 1) != 0;
            execute(SIZE_MAX); assert(terminal_reason == AUDIO_END_DECODE_FAILED && faults == 1 && !pcm_position); ++groups;
        }
        printf("CUTS groups=%u\n",groups);
    } else if (!strcmp(mode,"drain")) {
        final_reason = AUDIO_DRAIN_CODEC; execute(SIZE_MAX);
        assert(!terminal_reason && !faults && pcm_position == reference_size && !atomic_load(&s_failed_generation));
        final_reason = AUDIO_END_EOF; execute(SIZE_MAX);
        assert(terminal_reason == AUDIO_END_EOF && !faults && pcm_position == reference_size);
    } else if (!strcmp(mode,"empty")) {
        input_limit = 0; execute(SIZE_MAX);
        assert(terminal_reason == AUDIO_END_EOF && !faults && !pcm_position);
    } else if (!strcmp(mode,"invalid")) {
        execute(SIZE_MAX); assert(terminal_reason == AUDIO_END_DECODE_FAILED && faults == 1 && !pcm_position);
    } else if (!strcmp(mode,"oom")) {
        size_t calls = execute(SIZE_MAX); assert(terminal_reason == AUDIO_END_EOF && pcm_position == reference_size);
        for (size_t limit = 0; limit < calls; ++limit) {
            execute(limit); assert(terminal_reason == AUDIO_END_DECODE_FAILED || terminal_reason == AUDIO_END_ALLOCATION_FAILED);
            assert(faults == 1); execute(SIZE_MAX);
            assert(terminal_reason == AUDIO_END_EOF && pcm_position == reference_size && !faults);
        }
        printf("OOM failures=%zu reopens=%zu\n", calls,calls);
    } else if (!strcmp(mode,"cancel")) {
        cancel_send = (unsigned)extra; execute(SIZE_MAX);
        assert(blocks == 3 && !terminal_reason && !faults && !pcm_position);
        if (extra == 2) assert(ack_count == 1);
        execute(SIZE_MAX); assert(pcm_position == reference_size && terminal_reason == AUDIO_END_EOF);
    } else if (!strcmp(mode,"owner")) {
        // Complete metadata but hold encoded samples in the real adapter.
        schedule = 42; action = (unsigned)extra; action_after = 1;
        execute(SIZE_MAX); assert(!terminal_reason && !faults && !pcm_position);
        if (extra == 2 || extra == 3) assert(ack_count == 1);
        schedule = 127; execute(SIZE_MAX); assert(pcm_position == reference_size && terminal_reason == AUDIO_END_EOF);
    } else if (!strcmp(mode,"codec")) {
        schedule = 42; generation_switch_at = 1; execute(SIZE_MAX);
        assert(vendor_opens == 1 && vendor_closes == 1 && !pcm_position && terminal_reason == AUDIO_END_EOF);
        generation_switch_at = 0; schedule = 127; execute(SIZE_MAX);
        assert(pcm_position == reference_size && terminal_reason == AUDIO_END_EOF);
    } else assert(false);
    printf("PASS mode=%s pcm_bytes=%zu hash=%016llx quiet=%u\n",mode,pcm_position,(unsigned long long)pcm_hash,quiescent_checks);
    free(encoded_data); free(reference_pcm); free(state.lock); return 0;
}
