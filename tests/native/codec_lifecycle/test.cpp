#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include "esp_heap_caps.h"
#include "codec_bridge.h"
#include "codec_arena_native.h"
#include "CodecMemoryArena.h"
#if CONFIG_YORADIO_OGG_OPUS
#include "native_opus.h"
#include "opus_memory.h"
#endif

static std::map<void *, size_t> live;
static std::map<void *, unsigned> live_caps;
static int fail_after = -1;
static size_t reported_free_heap = 65536;
static size_t reported_dram_budget = 65536;
static size_t first_failed_bytes, first_failed_dram;
static unsigned critical_depth;
void test_codec_enter_critical(void) { assert(!critical_depth); ++critical_depth; }
void test_codec_exit_critical(void) { assert(critical_depth==1); --critical_depth; }
static bool reject_iram;
static unsigned allocations, frees, failures, attempts, tested_failure_sites;
void *heap_caps_malloc(size_t size, unsigned caps) {
    assert(!critical_depth);
    ++attempts;
    if (reject_iram && (caps & MALLOC_CAP_EXEC)) { ++failures; return nullptr; }
    if (fail_after == 0) {
        if (!first_failed_bytes) {
            first_failed_bytes=size; first_failed_dram=heap_caps_get_free_size(MALLOC_CAP_8BIT);
        }
        ++failures; return nullptr;
    }
    if (fail_after > 0) --fail_after;
    void *p = malloc(size); assert(p);
    assert(live.emplace(p, size).second); ++allocations;
    assert(live_caps.emplace(p,caps).second);
    return p;
}
void *heap_caps_calloc(size_t count, size_t size, unsigned caps) {
    void *p = heap_caps_malloc(count * size, caps);
    if (p) memset(p, 0, count * size);
    return p;
}
void heap_caps_free(void *p) {
    assert(!critical_depth);
    if (!p) return;
    assert(live.erase(p) == 1); // double free/unowned pointer fails immediately
    assert(live_caps.erase(p) == 1);
    ++frees; free(p);
}
void *heap_caps_realloc(void *p, size_t size, unsigned caps) {
    // Match ESP8266 SDK: allocate-copy-free (not host in-place realloc).
    void *q = heap_caps_malloc(size, caps);
    if (p && q) {
        assert(live.count(p));
        memcpy(q, p, live.at(p) < size ? live.at(p) : size);
        heap_caps_free(p);
    }
    return q;
}
size_t esp_get_free_heap_size() { return reported_free_heap; }
size_t heap_caps_get_free_size(unsigned caps) {
    assert(!critical_depth);
    if (caps!=MALLOC_CAP_8BIT) return esp_get_free_heap_size();
    size_t used=0;
    for (const auto &allocation:live)
        if (live_caps.at(allocation.first)&MALLOC_CAP_8BIT) used+=allocation.second;
    return used<reported_dram_budget?reported_dram_budget-used:0;
}

#if CONFIG_YORADIO_OGG_OPUS
/* Stub only the low-level adapter: the actual bridge, native_opus_t layout,
 * heap allocator and shared CodecMemoryArena remain under test. This matches
 * the measured host mono decoder-state size; no libopus build is required. */
static void *opus_bound_bytes, *opus_bound_words;
static bool opus_init_fail;
static bool opus_reset_fail;
static int opus_finish_result;
static unsigned opus_inits, opus_resets, opus_finishes;
static unsigned opus_source_channels = 2;
extern "C" size_t native_opus_decoder_size(void) { return 9198; }
extern "C" void yoradio_opus_memory_bind(void *bytes, size_t byte_capacity,
                                         void *words, size_t word_capacity) {
    assert(!!bytes == !!byte_capacity && !!words == !!word_capacity);
    opus_bound_bytes = bytes; opus_bound_words = words;
}
extern "C" size_t yoradio_opus_scratch_peak_bytes(void) { return 0; }
extern "C" size_t yoradio_opus_scratch_peak_words(void) { return 0; }
extern "C" int native_opus_init_ex(native_opus_t *d, const native_opus_config_t *config,
                                     bool allow_live_join) {
    assert(allow_live_join); // The radio bridge opts in; finite adapters do not.
    assert(d && config && config->output && config->output_ctx);
    assert(config->decoder_state_bytes == native_opus_decoder_size());
    assert(config->scratch_bytes == CONFIG_YORADIO_OPUS_SCRATCH_BYTES);
    assert(config->iram_bytes == 16384 && config->pcm_samples == 960);
    assert(live.at(config->decoder_state) == config->decoder_state_bytes);
    assert(live.at(config->scratch) == config->scratch_bytes);
    assert(live.at(config->iram) == config->iram_bytes);
    assert(live.at(config->pcm) == config->pcm_samples * sizeof(int16_t));
    assert((reinterpret_cast<uintptr_t>(config->decoder_state) & 7u) == 0);
    assert((reinterpret_cast<uintptr_t>(config->scratch) & 7u) == 0);
    assert((reinterpret_cast<uintptr_t>(config->iram) & 7u) == 0);
    assert(CodecArenaWordUsed() == 16384);
    memset(d, 0, sizeof(*d));
    d->config = *config;
    d->demux.allow_live_join = allow_live_join;
    ++opus_inits;
    yoradio_opus_memory_bind(config->scratch, config->scratch_bytes,
                            config->iram, config->iram_bytes);
    return opus_init_fail ? NATIVE_OPUS_ERR_MEMORY : 0;
}
extern "C" int native_opus_reset(native_opus_t *d) {
    assert(d && d->config.scratch == opus_bound_bytes);
    assert(d->demux.allow_live_join);
    const native_opus_config_t config = d->config;
    memset(d, 0, sizeof(*d)); d->config = config;
    d->demux.allow_live_join = true;
    ++opus_resets;
    return opus_reset_fail ? NATIVE_OPUS_ERR_MEMORY : 0;
}
extern "C" int native_opus_feed(native_opus_t *d, const uint8_t *data,
                                  size_t size, size_t *consumed) {
    assert(d && consumed && (!size || data));
    *consumed = size < 7 ? size : 7;
    if (!size) return NATIVE_OPUS_NEED_INPUT;
    d->input_channels = opus_source_channels;
    for (size_t i = 0; i < 960; ++i) d->config.pcm[i] = static_cast<int16_t>(i);
    return d->config.output(d->config.output_ctx, d->config.pcm, 960, 24000) ?
        NATIVE_OPUS_PACKET : NATIVE_OPUS_ERR_CANCELLED;
}
extern "C" int native_opus_finish(native_opus_t *d) {
    assert(d); ++opus_finishes;
    return opus_finish_result;
}
extern "C" const char *native_opus_error_string(int) {
    return "Opus lifecycle adapter stub error";
}
#endif

static void clean(const std::map<void *, size_t> &baseline) {
    assert(live == baseline); // only permanent IRAM arena may survive Stop
    assert(CodecArenaHeapUsed() == 0);
    assert(CodecArenaCapacity() == 0);
    assert(CodecArenaWordUsed() == 0);
#if CONFIG_YORADIO_OGG_OPUS
    assert(!opus_bound_bytes && !opus_bound_words);
#endif
}

static const helix_codec_kind_t kinds[] = {
    HELIX_CODEC_MP3, HELIX_CODEC_AAC,
#if CONFIG_YORADIO_OGG_OPUS
    HELIX_CODEC_OPUS,
#endif
};

static void capacity_and_owner(helix_codec_t *c, helix_codec_kind_t kind) {
    const size_t expected = kind == HELIX_CODEC_OPUS ? CONFIG_YORADIO_OPUS_INPUT_BYTES : 4096;
    assert(helix_codec_input_capacity() == 4096);
    assert(helix_codec_active_input_capacity(c) == expected);
    assert(helix_codec_buffered(c) == 0);
    size_t available = 0;
    uint8_t *input = helix_codec_write_pointer(c, &available);
    assert(input && available == expected && live.at(input) == expected);
    assert(helix_codec_buffer_commit(c, expected + 1) == -2);
    memset(input, 0x5a, 17);
    assert(helix_codec_buffer_commit(c, 17) == 0);
    assert(helix_codec_buffered(c) == 17);
    const CodecArenaOwner wrong = kind == HELIX_CODEC_OPUS ? CODEC_ARENA_MP3 : CODEC_ARENA_OPUS;
    assert(!CodecArenaCalloc(wrong, 1, 1));
    assert(helix_codec_iram_used(c) == 16384);
    size_t heap_bytes = 0;
    for (const auto &allocation : live) heap_bytes += allocation.second;
    assert(helix_codec_dram_used(c) == heap_bytes - 16384);
}

static void cycles(const std::map<void *, size_t> &baseline) {
    for (int repeat = 0; repeat < 100; ++repeat) {
        helix_codec_t *c = helix_codec_create(HELIX_CODEC_MP3, 1152); assert(c);
        helix_codec_kind_t previous = HELIX_CODEC_MP3;
        const helix_codec_kind_t sequence[] = {
            HELIX_CODEC_MP3, HELIX_CODEC_AAC, HELIX_CODEC_AAC,
#if CONFIG_YORADIO_OGG_OPUS
            HELIX_CODEC_OPUS, HELIX_CODEC_OPUS, HELIX_CODEC_AAC,
#endif
            HELIX_CODEC_MP3
        };
        for (auto kind : sequence) {
            const unsigned before = attempts;
            const auto allocations_before = live;
            assert(helix_codec_switch(c, kind) == 0);
            if (kind == previous && kind != HELIX_CODEC_AAC) {
                assert(attempts == before && live == allocations_before);
            }
            capacity_and_owner(c, kind);
            previous = kind;
        }
        helix_codec_destroy(c); clean(baseline);
    }
}

static void allocation_failures(const std::map<void *, size_t> &baseline) {
    // Measure successful allocation paths so every site is covered even when
    // decoder internals change. Retry the failed switch on the SAME object.
    for (auto first : kinds) {
        unsigned before = attempts;
        helix_codec_t *c = helix_codec_create(first, 1152); assert(c);
        const unsigned create_sites = attempts - before;
        helix_codec_destroy(c); clean(baseline);
        for (unsigned site = 0; site < create_sites; ++site) {
            const unsigned prior_failures = failures;
            fail_after = static_cast<int>(site);
            assert(!helix_codec_create(first, 1152));
            fail_after = -1;
            assert(failures > prior_failures); ++tested_failure_sites;
            clean(baseline);
        }
        for (auto next : kinds) {
            c = helix_codec_create(first, 1152); assert(c);
            before = attempts;
            assert(helix_codec_switch(c, next) == 0);
            const unsigned switch_sites = attempts - before;
            helix_codec_destroy(c); clean(baseline);
            for (unsigned site = 0; site < switch_sites; ++site) {
                c = helix_codec_create(first, 1152); assert(c);
                const unsigned prior_failures = failures;
                fail_after = static_cast<int>(site);
                assert(helix_codec_switch(c, next) < 0);
                fail_after = -1;
                assert(failures > prior_failures); ++tested_failure_sites;
                assert(helix_codec_switch(c, next) == 0);
                capacity_and_owner(c, next);
                helix_codec_destroy(c); clean(baseline);
            }
            if (!switch_sites) {
                c = helix_codec_create(first, 1152); assert(c);
                before = attempts;
                fail_after = 0;
                assert(helix_codec_switch(c, next) == 0);
                assert(attempts == before);
                fail_after = -1;
                helix_codec_destroy(c); clean(baseline);
            }
        }
        reported_free_heap = 0;
        assert(!helix_codec_create(first, 1152));
        reported_free_heap = 65536; clean(baseline);
    }
}

static void detection(void) {
    const uint8_t mp3[] = {0xff, 0xfb, 0x90, 0x64};
    assert(helix_codec_detect(mp3, sizeof(mp3)) == HELIX_CODEC_MP3);
    uint8_t ogg[64] = {};
    memcpy(ogg, "OggS", 4); ogg[5] = 2; ogg[26] = 1; ogg[27] = 19;
    memcpy(ogg + 28, "OpusHead", 8);
    for (size_t size = 4; size < 36; ++size)
        assert(helix_codec_detect(ogg, size) == 0);
#if CONFIG_YORADIO_OGG_OPUS
    assert(helix_codec_detect(ogg, sizeof(ogg)) == HELIX_CODEC_OPUS);
#else
    assert(helix_codec_detect(ogg, sizeof(ogg)) == 0);
    assert(!helix_codec_create(HELIX_CODEC_OPUS, 1152));
#endif
    memcpy(ogg + 28, "\x01vorbis", 7);
    memcpy(ogg + 42, mp3, sizeof(mp3)); // Accidental MP3 sync inside Ogg payload.
    assert(helix_codec_detect(ogg, sizeof(ogg)) == 0);
    ogg[42] = 0xff; ogg[43] = 0xf1; ogg[44] = 0x50; // AAC sync too.
    assert(helix_codec_detect(ogg, sizeof(ogg)) == 0);
    memcpy(ogg + 28, "OpusHead", 8); ogg[4] = 1;
    assert(helix_codec_detect(ogg, sizeof(ogg)) == 0);
    ogg[4] = 0; ogg[26] = 255;
    assert(helix_codec_detect(ogg, sizeof(ogg)) == 0);
    puts("Ogg Opus detection and Vorbis exclusion PASS");
}

#if CONFIG_YORADIO_OGG_OPUS
static void opus_reserve_and_init_failures(const std::map<void *, size_t> &baseline) {
    for (auto legacy : {HELIX_CODEC_MP3, HELIX_CODEC_AAC}) {
        reported_free_heap = 1152;
        helix_codec_t *c = helix_codec_create(legacy, 1152); assert(c);
        helix_codec_destroy(c); clean(baseline);
    }
    for (size_t reserve : {size_t(0), size_t(1152), size_t(8192)}) {
        const size_t required = reserve > 4096 ? reserve : 4096;
        reported_free_heap = required - 1;
        assert(!helix_codec_create(HELIX_CODEC_OPUS, reserve)); clean(baseline);
        reported_free_heap = required;
        helix_codec_t *c = helix_codec_create(HELIX_CODEC_OPUS, reserve); assert(c);
        const unsigned before = attempts, resets = opus_resets;
        const auto original = live;
        capacity_and_owner(c, HELIX_CODEC_OPUS);
        assert(helix_codec_switch(c, HELIX_CODEC_OPUS) == 0);
        assert(opus_resets == resets + 1 && attempts == before && live == original);
        assert(helix_codec_buffered(c) == 0);
        helix_codec_destroy(c); clean(baseline);
    }
    reported_free_heap = 65536;
    opus_init_fail = true;
    assert(!helix_codec_create(HELIX_CODEC_OPUS, 1152)); clean(baseline);
    opus_init_fail = false;
    for (auto first : kinds) {
        helix_codec_t *c = helix_codec_create(first, 1152); assert(c);
        if (first != HELIX_CODEC_OPUS) {
            opus_init_fail = true;
            assert(helix_codec_switch(c, HELIX_CODEC_OPUS) < 0);
            opus_init_fail = false;
            assert(!opus_bound_bytes && !opus_bound_words);
            assert(helix_codec_switch(c, HELIX_CODEC_OPUS) == 0);
        }
        reported_free_heap = 4095;
        assert(helix_codec_switch(c, HELIX_CODEC_MP3) == 0);
        assert(helix_codec_switch(c, HELIX_CODEC_OPUS) < 0);
        reported_free_heap = 4096;
        assert(helix_codec_switch(c, HELIX_CODEC_OPUS) == 0);
        helix_codec_destroy(c); clean(baseline);
        reported_free_heap = 65536;
    }
    printf("Opus input %u, scratch %u, reserve and allocation-free reset PASS\n",
           unsigned(CONFIG_YORADIO_OPUS_INPUT_BYTES), unsigned(CONFIG_YORADIO_OPUS_SCRATCH_BYTES));
}

struct PcmOutput { unsigned blocks; size_t samples; bool cancel; };
static bool receive_pcm(void *context, const helix_stream_info_t *info,
                        int16_t *pcm, size_t samples) {
    PcmOutput *output = static_cast<PcmOutput *>(context);
    assert(info->sample_rate == 48000 && info->bitrate == 24000);
    assert(info->channels == 1 && info->bits_per_sample == 16);
    assert(info->source_channels == opus_source_channels);
    static_assert(sizeof(helix_stream_info_t) == 12, "Metadata must fit existing padding");
    const size_t offset = output->samples % 960;
    assert(samples == (offset ? 448 : 512));
    assert(pcm[0] == static_cast<int16_t>(offset));
    ++output->blocks; output->samples += samples;
    return !output->cancel;
}

static void opus_bridge_delivery(const std::map<void *, size_t> &baseline) {
    helix_codec_t *c = helix_codec_create(HELIX_CODEC_OPUS, 1152); assert(c);
    size_t capacity = 0;
    uint8_t *input = helix_codec_write_pointer(c, &capacity);
    memset(input, 0x5a, 14);
    assert(helix_codec_buffer_commit(c, 14) == 0);
    const unsigned before = attempts;
    PcmOutput output = {};
    assert(helix_codec_process_one(c, receive_pcm, &output) == 0);
    assert(output.blocks == 2 && output.samples == 960 && helix_codec_buffered(c) == 7);
    opus_source_channels = 1; // A following mono logical stream still outputs mono PCM.
    assert(helix_codec_process_one(c, receive_pcm, &output) == 0);
    assert(output.blocks == 4 && output.samples == 1920 && helix_codec_buffered(c) == 0);
    opus_source_channels = 2;
    assert(helix_codec_process_one(c, receive_pcm, &output) == 1);
    opus_finish_result = NATIVE_OPUS_ERR_TRUNCATED;
    assert(helix_codec_finish(c) == NATIVE_OPUS_ERR_TRUNCATED);
    opus_finish_result = 0;
    assert(helix_codec_feed(c, nullptr, 0, true, receive_pcm, &output) == 0);
    assert(opus_finishes == 2);
    output = {0, 0, true};
    const uint8_t packet[7] = {};
    assert(helix_codec_feed(c, packet, sizeof(packet), false, receive_pcm, &output) ==
           NATIVE_OPUS_ERR_CANCELLED);
    assert(output.blocks == 1 && attempts == before);
    helix_codec_destroy(c); clean(baseline);
    puts("Opus adapter routing, bounded PCM callbacks and finish/cancellation PASS");
}

#if YORADIO_ESP8266_OPUS_STREAM_TEST
static helix_opus_init_failure_t init_failure(unsigned stage) {
    helix_opus_init_failure_t failure;
    const unsigned before=attempts;
    helix_codec_opus_init_failure_snapshot(&failure);
    assert(attempts==before && !critical_depth && failure.stage==stage);
    if (stage) assert(failure.reserve_bytes==4096 && failure.requested_bytes);
    else assert(!failure.free_dram && !failure.requested_bytes && !failure.reserve_bytes && !failure.detail);
    return failure;
}
static void opus_diagnostics(const std::map<void *, size_t> &baseline) {
    const unsigned stages[]={HELIX_OPUS_INIT_CODEC,HELIX_OPUS_INIT_INPUT,HELIX_OPUS_INIT_PCM,
        HELIX_OPUS_INIT_WORKSPACE,HELIX_OPUS_INIT_STATE,HELIX_OPUS_INIT_SCRATCH};
    for(unsigned site=0;site<sizeof(stages)/sizeof(stages[0]);++site) {
        first_failed_bytes=first_failed_dram=0;fail_after=static_cast<int>(site);
        assert(!helix_codec_create(HELIX_CODEC_OPUS,1152));fail_after=-1;
        const auto failure=init_failure(stages[site]);
        assert(failure.requested_bytes==first_failed_bytes && failure.free_dram==first_failed_dram && !failure.detail);
        if(site) assert(failure.free_dram<heap_caps_get_free_size(MALLOC_CAP_8BIT));
        clean(baseline);
        helix_codec_t *c=helix_codec_create(HELIX_CODEC_OPUS,1152);assert(c);init_failure(HELIX_OPUS_INIT_NONE);
        helix_codec_destroy(c);clean(baseline);
    }
    assert(CodecArenaBind(nullptr,1234));
    assert(!helix_codec_create(HELIX_CODEC_OPUS,1152));
    assert(init_failure(HELIX_OPUS_INIT_ARENA_BIND).requested_bytes==32768+CONFIG_YORADIO_OPUS_SCRATCH_BYTES);
    assert(CodecArenaCapacity()==1234 && CodecArenaUnbind());clean(baseline);
    opus_init_fail=true;assert(!helix_codec_create(HELIX_CODEC_OPUS,1152));opus_init_fail=false;
    assert(init_failure(HELIX_OPUS_INIT_NATIVE).detail==NATIVE_OPUS_ERR_MEMORY);clean(baseline);
    helix_codec_t *c=helix_codec_create(HELIX_CODEC_OPUS,1152);assert(c);
    opus_reset_fail=true;assert(helix_codec_switch(c,HELIX_CODEC_OPUS)==NATIVE_OPUS_ERR_MEMORY);
    assert(init_failure(HELIX_OPUS_INIT_NATIVE).detail==NATIVE_OPUS_ERR_MEMORY);
    opus_reset_fail=false;assert(helix_codec_switch(c,HELIX_CODEC_OPUS)==0);init_failure(HELIX_OPUS_INIT_NONE);
    helix_codec_destroy(c);clean(baseline);
    reported_free_heap=4095;reported_dram_budget=24000;
    assert(!helix_codec_create(HELIX_CODEC_OPUS,1152));
    const auto failure=init_failure(HELIX_OPUS_INIT_RESERVE);
    assert(failure.detail==4095 && failure.requested_bytes==4096 && failure.free_dram<4095);
    assert(failure.free_dram<heap_caps_get_free_size(MALLOC_CAP_8BIT));clean(baseline);
    reported_free_heap=reported_dram_budget=65536;
    c=helix_codec_create(HELIX_CODEC_OPUS,1152);assert(c);init_failure(HELIX_OPUS_INIT_NONE);
    helix_codec_destroy(c);clean(baseline);
    puts("Opus init diagnostics: allocation stages, CAP8 before cleanup, native, reserve, retry PASS");
}
#endif

static void dram_fallback(const std::map<void *, size_t> &baseline) {
    assert(!CodecArenaPreallocatedInIram());
    assert(!helix_codec_create(HELIX_CODEC_OPUS, 1152)); clean(baseline);
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    assert(init_failure(HELIX_OPUS_INIT_IRAM).requested_bytes==16384);
#endif
    for (auto first : {HELIX_CODEC_MP3, HELIX_CODEC_AAC}) {
        helix_codec_t *c = helix_codec_create(first, 1152); assert(c);
        assert(helix_codec_iram_used(c) == 0);
        assert(helix_codec_switch(c, HELIX_CODEC_OPUS) < 0);
        assert(helix_codec_switch(c, first) == 0);
        helix_codec_destroy(c); clean(baseline);
    }
    puts("Opus refuses DRAM fallback arena without leaking");
}
#endif

int main(int argc, char **argv) {
    fail_after = 0;
    assert(!helix_codec_prepare());
    assert(live.empty());
#if CONFIG_YORADIO_OGG_OPUS && YORADIO_ESP8266_OPUS_STREAM_TEST
    assert(!helix_codec_create(HELIX_CODEC_OPUS,1152));
    assert(init_failure(HELIX_OPUS_INIT_IRAM).requested_bytes==16384 && live.empty());
#endif
    fail_after = -1;
    reject_iram = argc > 1 && strcmp(argv[1], "--dram-arena") == 0;
    assert(helix_codec_prepare());
    const auto baseline = live;
#if CONFIG_YORADIO_OGG_OPUS
    if (reject_iram) { dram_fallback(baseline); return 0; }
#endif
    assert(CodecArenaPreallocatedInIram());
    cycles(baseline);
    allocation_failures(baseline);
    detection();
#if CONFIG_YORADIO_OGG_OPUS
    opus_reserve_and_init_failures(baseline);
    opus_bridge_delivery(baseline);
#if YORADIO_ESP8266_OPUS_STREAM_TEST
    opus_diagnostics(baseline);
#endif
    assert(opus_inits && opus_resets);
#endif
    clean(baseline);
    assert(failures && allocations == frees + baseline.size());
    printf("Codec lifecycle PASS: 100 mixed cycles, %u allocation failure sites; %u allocations, %u frees, %zu permanent IRAM allocation\n",
           tested_failure_sites, allocations, frees, baseline.size());
}
