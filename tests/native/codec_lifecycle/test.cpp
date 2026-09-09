#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include "esp_heap_caps.h"
#include "codec_bridge.h"
#include "codec_arena_native.h"
#include "CodecMemoryArena.h"

static std::map<void *, size_t> live;
static int fail_after = -1;
static bool low_heap;
static unsigned allocations, frees, failures;
void *heap_caps_malloc(size_t size, unsigned) {
    if (fail_after == 0) { ++failures; return nullptr; }
    if (fail_after > 0) --fail_after;
    void *p = malloc(size); assert(p);
    assert(live.emplace(p, size).second); ++allocations;
    return p;
}
void *heap_caps_calloc(size_t count, size_t size, unsigned caps) {
    void *p = heap_caps_malloc(count * size, caps);
    if (p) memset(p, 0, count * size);
    return p;
}
void heap_caps_free(void *p) {
    if (!p) return;
    assert(live.erase(p) == 1); // double free/unowned pointer fails immediately
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
size_t esp_get_free_heap_size() { return low_heap ? 0 : 65536; }
size_t heap_caps_get_free_size(unsigned) { return esp_get_free_heap_size(); }
static void clean(const std::map<void *, size_t> &baseline) {
    assert(live == baseline); // only permanent IRAM arena may survive Stop
    assert(CodecArenaHeapUsed() == 0);
    assert(CodecArenaCapacity() == 0);
    assert(CodecArenaWordUsed() == 0);
}
int main() {
    assert(helix_codec_prepare());
    const auto baseline = live;
    for (int repeat = 0; repeat < 100; ++repeat) {
        helix_codec_t *c = helix_codec_create(HELIX_CODEC_MP3, 1152); assert(c);
        for (auto kind : {HELIX_CODEC_MP3, HELIX_CODEC_AAC, HELIX_CODEC_AAC, HELIX_CODEC_MP3})
            assert(helix_codec_switch(c, kind) == 0);
        helix_codec_destroy(c); clean(baseline);
    }
    // Force every individual allocation failure, including PCM resize and
    // partial decoder construction; cleanup must allow the next Play.
    for (auto first : {HELIX_CODEC_MP3, HELIX_CODEC_AAC}) {
        for (int fail = 0; fail < 24; ++fail) {
            fail_after = fail;
            helix_codec_t *c = helix_codec_create(first, 1152);
            helix_codec_destroy(c); fail_after = -1; clean(baseline);
            for (auto next : {HELIX_CODEC_MP3, HELIX_CODEC_AAC}) {
                c = helix_codec_create(first, 1152); assert(c);
                fail_after = fail;
                helix_codec_switch(c, next);
                helix_codec_destroy(c); fail_after = -1; clean(baseline);
            }
        }
        low_heap = true;
        assert(!helix_codec_create(first, 1152));
        low_heap = false; clean(baseline);
    }
    assert(failures && allocations == frees + baseline.size());
    printf("Codec lifecycle PASS: 100 mixed cycles, every allocation failure; %u allocations, %u frees, %zu permanent IRAM allocation\n",
           allocations, frees, baseline.size());
}
