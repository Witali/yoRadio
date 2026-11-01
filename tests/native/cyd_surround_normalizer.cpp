// Public stereo instances supply an independent all-channel envelope oracle.
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <vector>
#include "AudioNormalizer.h"
#include "native_audio_normalizer.h"

static uint32_t magnitude(int16_t value)
{
    return value == INT16_MIN ? 32768u : static_cast<uint32_t>(value < 0 ? -value : value);
}

static int16_t input(size_t frame, uint8_t channel, uint8_t channels)
{
    if (frame % 19 == 0 && channel + 1 == channels) return INT16_MIN;
    if (frame % 23 == 0 && channel == 0) return INT16_MAX;
    if ((frame / 257) % 3 == 0 && channel < 2) return 0;
    uint32_t value = static_cast<uint32_t>(frame * 167u + channel * 8179u);
    return static_cast<int16_t>(static_cast<int32_t>(value % 18001u) - 9000);
}

int main()
{
    struct Config { bool enabled; uint8_t gain; int8_t target; uint16_t time; uint32_t rate; };
    const Config configs[] = {{false, 0, -3, 1000, 48000}, {true, 0, -3, 1000, 48000},
                              {true, 18, -12, 100, 8000}, {true, 24, -6, 5000, 48000}};
    constexpr size_t frames = 4096;
    const size_t partitions[] = {1, 127, 128, 511};
    uint64_t compared = 0, differences = 0, legacy_multichannel_gaps = 0;
    unsigned streams = 0;
    for (const auto &config : configs) for (uint8_t channels = 1; channels <= 8; ++channels) {
        std::vector<int16_t> original(frames * channels), expected(original.size());
        for (size_t frame = 0; frame < frames; ++frame)
            for (uint8_t channel = 0; channel < channels; ++channel)
                original[frame * channels + channel] = input(frame, channel, channels);
        std::array<AudioNormalizer, 8> oracle;
        for (auto &item : oracle)
            item.configure(config.enabled, config.gain, config.target, config.time, config.rate);
        for (size_t frame = 0; frame < frames; ++frame) {
            const int16_t *source = original.data() + frame * channels;
            int16_t peak = source[0];
            for (uint8_t channel = 1; channel < channels; ++channel)
                if (magnitude(source[channel]) > magnitude(peak)) peak = source[channel];
            for (uint8_t channel = 0; channel < channels; ++channel) {
                int16_t pair[2] = {source[channel], peak};
                oracle[channel].process(pair);
                expected[frame * channels + channel] = pair[0];
            }
        }
        for (size_t partition : partitions) {
            native_audio_normalizer_configure(config.enabled, config.gain, config.target, config.time, config.rate);
            native_audio_normalizer_reset();
            std::vector<int16_t> guarded(original.size() + 2, 12345);
            std::copy(original.begin(), original.end(), guarded.begin() + 1);
            int16_t *samples = guarded.data() + 1;
#ifndef TEST_LEGACY_BLOCK
            native_audio_normalizer_process_multichannel_block(nullptr, frames, channels);
            native_audio_normalizer_process_multichannel_block(samples, 0, channels);
            native_audio_normalizer_process_multichannel_block(samples, 1, 0);
            native_audio_normalizer_process_multichannel_block(samples, 1, 9);
            native_audio_normalizer_process_multichannel_block(samples, SIZE_MAX, channels);
            assert(std::equal(original.begin(), original.end(), samples));
#endif
            for (size_t first = 0; first < frames; first += partition) {
                size_t count = std::min(partition, frames - first);
#ifdef TEST_LEGACY_BLOCK
                native_audio_normalizer_process_block(samples + first * channels, count, channels);
#else
                native_audio_normalizer_process_multichannel_block(samples + first * channels, count, channels);
#endif
            }
            assert(guarded.front() == 12345 && guarded.back() == 12345);
            size_t unequal = 0;
            for (size_t i = 0; i < expected.size(); ++i) unequal += samples[i] != expected[i];
            compared += expected.size(); differences += unequal; ++streams;
#ifdef TEST_LEGACY_BLOCK
            if (!config.enabled || channels <= 2) assert(!unequal);
            else { assert(unequal); ++legacy_multichannel_gaps; }
#else
            assert(!unequal);
#endif
        }
    }
#ifdef TEST_LEGACY_BLOCK
    assert(legacy_multichannel_gaps == 72 && differences > 0);
    const char *mode = "legacy_characterization";
#else
    assert(!differences && !legacy_multichannel_gaps);
    const char *mode = "all_channels";
#endif
    assert(streams == 128 && compared == UINT64_C(2359296));
    printf("{\"passed\":true,\"mode\":\"%s\",\"streams\":%u,\"samples\":%llu,\"differences\":%llu,\"legacy_multichannel_gaps\":%llu}\n",
           mode, streams, static_cast<unsigned long long>(compared),
           static_cast<unsigned long long>(differences), static_cast<unsigned long long>(legacy_multichannel_gaps));
}
