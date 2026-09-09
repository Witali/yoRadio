#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>
#include "codec_bridge.h"
#include "codec_arena_native.h"

/* Heap-backed host arena only. This test verifies byte/PCM ordering and not
 * ESP8266 memory availability or timing. The decoder implementations are real. */
bool CodecArenaBind(uint8_t *, size_t) { return true; }
bool CodecArenaUnbind(void) { return true; }
bool CodecArenaPreallocateMp3(void) { return true; }
size_t CodecArenaPreallocatedBytes(void) { return 0; }
size_t CodecArenaHeapUsed(void) { return 0; }
size_t CodecArenaWordUsed(void) { return 0; }
bool CodecArenaPreallocatedInIram(void) { return false; }

struct Result {
    std::vector<int16_t> pcm;
    std::vector<uint32_t> formats;
    bool cancel = false;
};
static bool collect(void *context, const helix_stream_info_t *info,
                    int16_t *pcm, size_t samples) {
    Result &result = *static_cast<Result *>(context);
    if (result.cancel) return false;
    result.pcm.insert(result.pcm.end(), pcm, pcm + samples);
    result.formats.push_back(info->sample_rate);
    result.formats.push_back(info->bitrate);
    result.formats.push_back(info->channels);
    return true;
}

static Result decode(const std::vector<uint8_t> &bytes, bool queued,
                     size_t chunk) {
    const helix_codec_kind_t kind = helix_codec_detect(bytes.data(), bytes.size());
    assert(kind == HELIX_CODEC_MP3 || kind == HELIX_CODEC_AAC);
    helix_codec_t *codec = helix_codec_create(kind, 0);
    assert(codec);
    Result result;
    size_t offset = 0;
    if (!queued) {
        while (offset < bytes.size()) {
            size_t count = std::min(chunk, bytes.size() - offset);
            assert(helix_codec_feed(codec, bytes.data() + offset, count, false,
                                    collect, &result) == 0);
            offset += count;
        }
    } else {
        for (;;) {
            /* Fill every free byte before processing ONE frame. Reads can
             * split anywhere; compacting the queue must not lose reservoir data. */
            while (offset < bytes.size()) {
                size_t capacity = 0;
                uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
                assert(destination);
                if (!capacity) break;
                size_t count = std::min({capacity, chunk, bytes.size() - offset});
                memcpy(destination, bytes.data() + offset, count);
                assert(helix_codec_buffer_commit(codec, count) == 0);
                offset += count;
            }
            int status = helix_codec_process_one(codec, collect, &result);
            assert(status >= 0);
            if (status == 1) {
                assert(offset == bytes.size()); /* No stall while full. */
                break;
            }
        }
    }
    assert(!result.pcm.empty());
    assert(helix_codec_switch(codec, kind) == 0);
    assert(helix_codec_buffered(codec) == 0);
    size_t capacity = 0;
    uint8_t *destination = helix_codec_write_pointer(codec, &capacity);
    assert(capacity == helix_codec_input_capacity());
    assert(helix_codec_buffer_commit(codec, capacity + 1) == -2);
    assert(helix_codec_buffered(codec) == 0);
    size_t count = std::min(bytes.size(), capacity);
    memcpy(destination, bytes.data(), count);
    assert(helix_codec_buffer_commit(codec, count) == 0);
    Result cancelled; cancelled.cancel = true;
    int status;
    do { status = helix_codec_process_one(codec, collect, &cancelled); }
    while (status == 0);
    assert(status < 0 && cancelled.pcm.empty());
    helix_codec_destroy(codec);
    return result;
}

int main(int argc, char **argv) {
    assert(argc >= 2);
    for (int i = 1; i < argc; ++i) {
        FILE *input = fopen(argv[i], "rb"); assert(input);
        std::vector<uint8_t> bytes;
        int value;
        while ((value = fgetc(input)) != EOF) bytes.push_back((uint8_t)value);
        fclose(input);
        Result original = decode(bytes, false, 1024);
        for (size_t chunk : {1U, 73U, 1024U}) {
            Result queued = decode(bytes, true, chunk);
            assert(original.pcm == queued.pcm);
            assert(original.formats == queued.formats);
        }
        printf("PCM identical: %s (%zu samples, input %zu)\n",
               argv[i], original.pcm.size(), helix_codec_input_capacity());
    }
    puts("Codec input tests passed");
    return 0;
}
