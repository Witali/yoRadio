#include "custom_flac_adapter.h"
#include "flac_decoder.h"
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

unsigned flac_test_errors;
static size_t groups, failures;
struct Capture {
    std::vector<uint8_t> pcm;
    unsigned bits, channels, rate;
};
static bool capture(void *user, const custom_flac_info_t *info,
                    const uint8_t *data, size_t size) {
    auto &out = *static_cast<Capture *>(user);
    assert(info->bits_per_sample == out.bits && info->pcm_bits_per_sample == 16);
    assert(info->channels == out.channels && info->sample_rate == out.rate);
    assert(size && size % (2 * info->channels) == 0);
    out.pcm.insert(out.pcm.end(), data, data + size);
    return true;
}
static std::vector<uint8_t> read_file(const char *path) {
    FILE *file = fopen(path, "rb"); assert(file);
    assert(!fseek(file, 0, SEEK_END)); long size = ftell(file); assert(size >= 0);
    rewind(file); std::vector<uint8_t> bytes(static_cast<size_t>(size));
    assert(fread(bytes.data(), 1, bytes.size(), file) == bytes.size());
    assert(!fclose(file)); return bytes;
}
static Capture output_for(const std::vector<uint8_t> &bytes) {
    assert(bytes.size() >= 42);
    return {{}, unsigned((((bytes[20] & 1) << 4) | (bytes[21] >> 4)) + 1),
        unsigned(((bytes[20] >> 1) & 7) + 1),
        unsigned((bytes[18] << 12) | (bytes[19] << 4) | (bytes[20] >> 4))};
}
static int feed(custom_flac_decoder_t *decoder, const uint8_t *data,
                size_t size, bool eos, Capture &out) {
    custom_flac_feed_stats_t stats{};
    return custom_flac_decoder_feed(decoder, data, size, eos, capture, &out, &stats);
}
static void destroy(custom_flac_decoder_t *decoder) {
    custom_flac_decoder_destroy(decoder);
    assert(!FLACDecoder_GetAllocatedBytes());
}
static void check(bool good, const char *name, size_t cut, int result) {
    ++groups;
    if (!good) {
        ++failures;
        printf("FAIL %s cut=%zu result=%d\n", name, cut, result);
    }
}
static int prefix(custom_flac_decoder_t *decoder, const std::vector<uint8_t> &data,
                  size_t size, bool eos, bool fragmented, Capture &out) {
    static const size_t chunks[] = {1, 3, 127, 511, 17};
    size_t offset = 0, index = 0; int result = 1;
    do {
        size_t bytes = fragmented ? std::min(size - offset, chunks[index++ % 5]) : size;
        result = feed(decoder, bytes ? data.data() + offset : nullptr, bytes,
                      eos && offset + bytes == size, out);
        offset += bytes;
        if (result < 0) break;
    } while (offset < size);
    return result;
}
static void cuts(const std::vector<uint8_t> &data, size_t metadata) {
    assert(metadata >= 42 && metadata < data.size());
    for (size_t cut = 0; cut < metadata; ++cut) {
        for (bool fragmented : {false, true}) {
            for (bool separate_eof : {false, true}) {
                auto out = output_for(data); auto *decoder = custom_flac_decoder_create();
                assert(decoder); flac_test_errors = 0;
                int result = prefix(decoder, data, cut, !separate_eof, fragmented, out);
                if (separate_eof) {
                    assert(result == 1 && out.pcm.empty());
                    result = feed(decoder, nullptr, 0, true, out);
                }
                check(result == ERR_FLAC_TRUNCATED_INPUT && out.pcm.empty(),
                      separate_eof ? "metadata-empty-eof" : "metadata-inline-eof", cut, result);
                destroy(decoder);
            }
        }
        // The same incomplete prefix remains legal while more bytes can arrive.
        // Continue with actual frames, including a final call larger than 512 bytes.
        auto out = output_for(data); auto *decoder = custom_flac_decoder_create(); assert(decoder);
        flac_test_errors = 0;
        assert(prefix(decoder, data, cut, false, true, out) == 1 && out.pcm.empty());
        int result = feed(decoder, data.data() + cut, data.size() - cut, true, out);
        check(result == 0 && !out.pcm.empty() && !flac_test_errors,
              "metadata-resume", cut, result);
        destroy(decoder);
    }
    // This narrow fix intentionally retains the existing metadata-only policy:
    // complete metadata is accepted, with no claim to audio/sample-count checks.
    for (bool separate_eof : {false, true}) {
        auto out = output_for(data); auto *decoder = custom_flac_decoder_create(); assert(decoder);
        int result = prefix(decoder, data, metadata, !separate_eof, true, out);
        assert(result == 0 && out.pcm.empty());
        if (separate_eof) result = feed(decoder, nullptr, 0, true, out);
        check(result == 0 && out.pcm.empty(), "complete-metadata-policy", metadata, result);
        destroy(decoder);
    }
    printf("RESULT groups=%zu failures=%zu metadata_bytes=%zu\n", groups, failures, metadata);
}
static void valid(const std::vector<uint8_t> &data, const char *destination, unsigned mode) {
    auto out = output_for(data); auto *decoder = custom_flac_decoder_create(); assert(decoder);
    flac_test_errors = 0; int result;
    if (mode == 0) result = prefix(decoder, data, data.size(), true, false, out);
    else if (mode == 1) result = prefix(decoder, data, data.size(), true, true, out);
    else {
        result = prefix(decoder, data, data.size(), false, true, out); assert(result >= 0);
        result = feed(decoder, nullptr, 0, true, out);
    }
    assert(result == 0 && !flac_test_errors && !out.pcm.empty());
    // A second empty EOF cannot duplicate the already delivered PCM.
    size_t size = out.pcm.size(); assert(feed(decoder, nullptr, 0, true, out) == 0);
    assert(out.pcm.size() == size);
    FILE *file = fopen(destination, "wb"); assert(file);
    assert(fwrite(out.pcm.data(), 1, out.pcm.size(), file) == out.pcm.size());
    assert(!fclose(file)); destroy(decoder);
    printf("PASS pcm_bytes=%zu source_bits=%u channels=%u mode=%u\n",
           out.pcm.size(), out.bits, out.channels, mode);
}
int main(int argc, char **argv) {
    assert(argc >= 4); auto data = read_file(argv[2]);
    if (!strcmp(argv[1], "cuts")) cuts(data, static_cast<size_t>(strtoul(argv[3], nullptr, 10)));
    else { assert(argc == 5 && !strcmp(argv[1], "valid")); valid(data, argv[3], unsigned(strtoul(argv[4], nullptr, 10))); }
    return failures ? 1 : 0;
}
