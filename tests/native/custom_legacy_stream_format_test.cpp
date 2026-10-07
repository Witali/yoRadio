// Real Helix decoder + shared adapter. The include also exposes internal state
// for a focused SBR fill-element test with synthesis disabled, as on C3.
#include "aac_decoder/aac_decoder.cpp"
#include "custom_legacy_adapter.h"

#include <cassert>
#include <fstream>
#include <iterator>
#include <vector>

static unsigned frames;
static uint32_t wanted_rate;
static uint32_t wanted_stream_rate;
static unsigned wanted_channels;
static bool wanted_sbr;
static bool output(void *, const custom_legacy_info_t *info,
                   const uint8_t *pcm, size_t size) {
    assert(pcm && size);
    assert(info->sample_rate == wanted_rate);
    assert(info->stream_sample_rate == wanted_stream_rate);
    assert(info->channels == wanted_channels);
    assert(info->stream_channels == wanted_channels);
    assert(info->bits_per_sample == 16);
    assert(info->aac_profile_known && info->aac_profile == 1);
    assert(info->aac_sbr == wanted_sbr);
    assert(info->channels_are_core == (wanted_sbr && wanted_channels == 1));
    assert(size == 1024 * wanted_channels * sizeof(int16_t));
    ++frames;
    return true;
}

static void feed(custom_legacy_decoder_t *decoder, const char *file,
                 uint32_t rate, unsigned channels, uint32_t stream_rate = 0) {
    wanted_rate = rate;
    wanted_stream_rate = stream_rate ? stream_rate : rate;
    wanted_sbr = wanted_stream_rate != wanted_rate;
    wanted_channels = channels;
    unsigned before = frames;
    std::ifstream input(file, std::ios::binary);
    assert(input.good());
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(input)), {});
    // Deliberately split ADTS headers and payloads across network packets.
    for (size_t offset = 0; offset < bytes.size();) {
        size_t count = std::min(size_t(97), bytes.size() - offset);
        custom_legacy_feed_stats_t stats = {};
        assert(custom_legacy_decoder_feed(decoder, bytes.data() + offset,
                    count, false, output, nullptr, &stats) >= 0);
        offset += count;
    }
    assert(frames > before);
}

int main(int argc, char **argv) {
    assert(argc == 6);
    auto *decoder = custom_legacy_decoder_create(CUSTOM_LEGACY_AAC);
    assert(decoder);
    feed(decoder, argv[1], 44100, 2);
    feed(decoder, argv[3], 22050, 2, 44100);
    feed(decoder, argv[4], 24000, 2, 48000);
    feed(decoder, argv[5], 22050, 1, 44100);
    feed(decoder, argv[1], 44100, 2);
    feed(decoder, argv[2], 22050, 1);
    // A real SBR fill extension is detected even when synthesis is disabled.
    unsigned char fill[] = {0x1d, 0x00}; // count=1, EXT_SBR_DATA=13
    SetBitstreamPointer(sizeof(fill), fill);
    assert(DecodeFillElement() == 0);
    assert(AACGetSBRPresent());
    assert(AACGetStreamSampRate() == 44100);
    assert(AACGetSampRate() == 22050);
    assert(AACGetChannels() == 1);
    // A new ADTS frame clears SBR metadata; it must not stick to AAC-LC.
    feed(decoder, argv[1], 44100, 2);
    custom_legacy_decoder_destroy(decoder);
    puts("PASS: real Helix AAC adapter stereo/mono/rate transitions and SBR source/PCM separation");
}
