#include "../../../yoRadio/src/audioI2S/mp3_decoder/mp3_decoder.cpp"
#include <cassert>
#include <cstdio>
#include <vector>

struct Sink { int calls; int cancelAt; int channels; std::vector<short> pcm; };
static bool sink(void *opaque, short *pcm, int samples) {
    Sink *s = static_cast<Sink *>(opaque);
    assert(samples == 32 * s->channels);
    ++s->calls;
    s->pcm.insert(s->pcm.end(), pcm, pcm + samples);
    for (int i = 0; i < samples; ++i) pcm[i] = 1234;
    return s->calls != s->cancelAt;
}

static void prepare(int channels) {
    MP3Decoder_ClearBuffer();
    m_MP3DecInfo->nChans = channels;
    for (int ch = 0; ch < 2; ++ch) {
        m_IMDCTInfo->gb[ch] = 8;
        for (int b = 0; b < 18; ++b)
            for (int i = 0; i < 32; ++i)
                m_IMDCTInfo->outBuf[ch][b][i] = (i * 23 + b * 11 + ch * 9 - 300) * 4096;
    }
}

int main() {
    assert(MP3Decoder_AllocateBuffers());
    const int capacity = 32 * (YORADIO_HELIX_MP3_MONO ? 1 : 2);
    std::vector<short> guarded(capacity + 2, 23456);
    short *pcm = guarded.data() + 1;
    for (int channels = 1; channels <= 2; ++channels) {
        const int outputChannels = YORADIO_HELIX_MP3_MONO ? 1 : channels;
        for (int cancel = 1; cancel <= 18; ++cancel) {
            prepare(channels);
            Sink s = {0, cancel, outputChannels, {}};
            assert(SubbandInternal(pcm, sink, &s) < 0);
            assert(s.calls == cancel);
            assert(guarded.front() == 23456 && guarded.back() == 23456);
            prepare(channels); // restart must not inherit partial synthesis
            std::vector<short> expected(576 * outputChannels);
            assert(Subband(expected.data()) == 0);
            prepare(channels);
            Sink complete = {0, 0, outputChannels, {}};
            assert(SubbandInternal(pcm, sink, &complete) == 0);
            assert(complete.calls == 18 && complete.pcm == expected);
        }
    }
    unsigned char input[417] = {0xff, 0xfb, 0x90, 0x60};
    prepare(2);
    Sink s = {0, 0, YORADIO_HELIX_MP3_MONO ? 1 : 2, {}};
    int left = 36;
    assert(MP3DecodeBlocks(input, &left, pcm, capacity - 1, 0, sink, &s) < 0);
    assert(left == 36 && s.calls == 0 && m_OutputBufferSamples == 0);
    assert(MP3DecodeBlocks(input, &left, pcm, capacity, 0, nullptr, &s) < 0);
    assert(MP3DecodeBlocks(input, &left, pcm, capacity, 0, sink, &s) == ERR_MP3_INDATA_UNDERFLOW);
    assert(s.calls == 0 && m_OutputBufferSamples == 0);
    for (int i = 0; i < capacity; ++i) assert(pcm[i] == 0);
    assert(guarded.front() == 23456 && guarded.back() == 23456);
    // Valid zero-data frame, cancellation through the public API.
    prepare(2);
    left = sizeof(input);
    s.cancelAt = 3;
    assert(MP3DecodeBlocks(input, &left, pcm, capacity, 0, sink, &s) < 0);
    assert(s.calls == 3 && m_OutputBufferSamples == 0);
    assert(guarded.front() == 23456 && guarded.back() == 23456);
    MP3Decoder_FreeBuffers();
    puts("32-frame MP3: cancellation at all synthesis boundaries, reset, capacity, underflow and canaries passed");
}
