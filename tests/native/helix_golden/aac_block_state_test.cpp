#include "../../../yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

static uint32_t rng = 8266;
static int random_word() { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return static_cast<int>(rng % 200000001) - 100000000; }
struct Sink { std::vector<short> pcm; int frames, channels, calls, cancel; };
static bool sink(void *opaque, short *pcm, int count) {
    Sink &s = *static_cast<Sink *>(opaque);
    assert(count == s.frames * s.channels);
    s.pcm.insert(s.pcm.end(), pcm, pcm + count);
    for (int i = 0; i < count; ++i) pcm[i] = 12345; // real sink changes PCM
    return ++s.calls != s.cancel;
}

static std::vector<unsigned char> two_sce_frame() {
    std::vector<unsigned char> bits;
    auto put = [&](unsigned value, int count) {
        while (count--) bits.push_back((value >> count) & 1U);
    };
    for (int ch = 0; ch < 2; ++ch) {
        put(AAC_ID_SCE, 3); put(ch, 4); put(100, 8); // element, tag, global gain
        put(0, 1); put(0, 2); put(0, 1); put(0, 6); put(0, 1); // long ICS, zero bands
        put(0, 3); // no pulse, TNS or gain control
    }
    put(AAC_ID_END, 3);
    while (bits.size() & 7U) bits.push_back(0);
    const size_t length = 7 + bits.size() / 8;
    std::vector<unsigned char> frame(length, 0);
    frame[0] = 0xff; frame[1] = 0xf1; frame[2] = 0x50;
    frame[3] = 0x80 | ((length >> 11) & 3); frame[4] = length >> 3;
    frame[5] = ((length & 7) << 5) | 31; frame[6] = 0xfc;
    for (size_t i = 0; i < bits.size(); ++i) frame[7 + i / 8] |= bits[i] << (7 - (i & 7));
    return frame;
}

int main() {
    assert(AACDecoder_AllocateBuffers());
    int original[2][1024], oldOverlap[2][1024], expectedOverlap[2][1024];
    using Window = void (*)(int *, int *, short *, int, int, int);
    Window legacy[] = {DecWindowOverlap, DecWindowOverlapLongStart,
                       DecWindowOverlapShort, DecWindowOverlapLongStop};
    unsigned vectors = 0;
    for (int size : {32, 64, 128, 256, 512}) for (int channels : {1, 2})
    for (int mono : {0, 1}) for (int sequence = 0; sequence < 4; ++sequence)
    for (int shape = 0; shape < 4; ++shape) for (int pass = 0; pass < 4; ++pass) {
        m_AACDecInfo->nChans = channels;
        m_PSInfoBase->commonWin = 0;
        std::vector<short> expected(1024 * channels);
        for (int ch = 0; ch < channels; ++ch) {
            for (int n = 0; n < 1024; ++n) {
                original[ch][n] = random_word();
                oldOverlap[ch][n] = random_word();
            }
            m_PSInfoBase->icsInfo[ch].winSequence = (sequence + ch) % 4;
            m_PSInfoBase->icsInfo[ch].winShape = shape & 1;
            m_PSInfoBase->prevWinShape[ch] = shape >> 1;
            std::memcpy(expectedOverlap[ch], oldOverlap[ch], sizeof(oldOverlap[ch]));
            legacy[(sequence + ch) % 4](original[ch], expectedOverlap[ch],
                expected.data() + ch, channels, shape & 1, shape >> 1);
        }
        if (channels == 2 && mono) {
            for (int n = 0; n < 1024; ++n)
                expected[n] = static_cast<short>((static_cast<int>(expected[2*n]) + expected[2*n+1]) >> 1);
            expected.resize(1024);
        }
        std::memcpy(m_PSInfoBase->coef, original, sizeof(original));
        std::memcpy(m_PSInfoBase->overlap, oldOverlap, sizeof(oldOverlap));
        const int outChannels = mono ? 1 : channels;
        Sink output = {{}, size, outChannels, 0, 0};
        AACBlockOutput blocks = {size, mono != 0, sink, &output, {}};
        for (int ch = 0; ch < channels; ++ch) blocks.window[ch] = aac_window_state(ch, ch);
        std::vector<short> guard(size * outChannels + 2, 23456);
        assert(aac_emit_blocks(guard.data() + 1, blocks) == ERR_AAC_NONE);
        if (output.pcm != expected) {
            for (int n = 0; n < static_cast<int>(expected.size()); ++n) if (output.pcm[n] != expected[n]) {
                std::printf("PCM mismatch seq=%d shape=%d n=%d actual=%d expected=%d\n", sequence, shape, n, output.pcm[n], expected[n]); break;
            }
            return 1;
        }
        assert(output.calls == 1024 / size);
        for (int ch = 0; ch < channels; ++ch)
            assert(std::memcmp(m_PSInfoBase->overlap[ch], expectedOverlap[ch], sizeof(expectedOverlap[ch])) == 0);
        assert(std::memcmp(m_PSInfoBase->coef, original, sizeof(original)) == 0);
        assert(guard.front() == 23456 && guard.back() == 23456);
        for (int cancel = 1; cancel <= 1024 / size; ++cancel) {
            std::memcpy(m_PSInfoBase->overlap, oldOverlap, sizeof(oldOverlap));
            output.calls = 0; output.cancel = cancel; output.pcm.clear();
            assert(aac_emit_blocks(guard.data() + 1, blocks) == ERR_AAC_OUTPUT_CANCELLED);
            assert(output.calls == cancel);
            for (int ch = 0; ch < 2; ++ch) for (int n = 0; n < 1024; ++n)
                assert(m_PSInfoBase->overlap[ch][n] == 0);
        }
        ++vectors;
    }
    unsigned char invalid[16] = {};
    short pcm[256] = {};
    Sink output = {{}, 128, 1, 0, 0};
    for (int frames : {0, 16, 33, 1024}) {
        int left = sizeof(invalid);
        assert(AACDecodeBlocks(invalid, &left, pcm, 256, frames, true, sink, &output) == ERR_AAC_INVALID_FRAME);
        assert(left == sizeof(invalid) && output.calls == 0);
    }
    int left = sizeof(invalid);
    assert(AACDecodeBlocks(invalid, &left, pcm, 127, 128, true, sink, &output) == ERR_AAC_INVALID_FRAME);
    assert(AACDecodeBlocks(invalid, &left, pcm, 256, 128, true, nullptr, &output) == ERR_AAC_NULL_POINTER);
    const auto frame = two_sce_frame();
    const auto coefficientBase = m_PSInfoBase->coef;
    for (int mono : {0, 1}) {
        AACFlushCodec();
        short full[2048];
        left = static_cast<int>(frame.size());
        assert(AACDecode(const_cast<unsigned char *>(frame.data()), &left, full) == ERR_AAC_NONE);
        assert(left == 0 && AACGetChannels() == 2);
        for (int cancel = 0; cancel <= 8; ++cancel) {
            AACFlushCodec();
            left = static_cast<int>(frame.size());
            output = {{}, 128, mono ? 1 : 2, 0, cancel};
            const int result = AACDecodeBlocks(const_cast<unsigned char *>(frame.data()), &left,
                pcm, 256, 128, mono != 0, sink, &output);
            assert(result == (cancel ? ERR_AAC_OUTPUT_CANCELLED : ERR_AAC_NONE));
            assert(left == 0 && m_PSInfoBase->coef == coefficientBase);
            assert(output.calls == (cancel ? cancel : 8));
            for (short value : output.pcm) assert(value == 0);
            assert(AACGetSampRate() == 44100 && AACGetBitrate() > 0);
        }
    }
    for (int bytes = 1; bytes < static_cast<int>(frame.size()); ++bytes) {
        AACFlushCodec(); output = {{}, 128, 1, 0, 0};
        left = bytes;
        assert(AACDecodeBlocks(const_cast<unsigned char *>(frame.data()), &left,
            pcm, 256, 128, true, sink, &output) != ERR_AAC_NONE);
        assert(output.calls == 0 && m_PSInfoBase->coef == coefficientBase);
    }
    AACDecoder_FreeBuffers();
    std::printf("AAC sequential windows: %u vectors, exact PCM/overlap, immutable coefficients, all block cancellations and canaries passed\n", vectors);
}
