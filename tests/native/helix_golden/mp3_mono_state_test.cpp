/* Include the implementation to exercise private lifetime helpers without
 * adding test-only symbols or runtime counters to firmware. */
#include "../../../yoRadio/src/audioI2S/mp3_decoder/mp3_decoder.cpp"
#include <climits>
#include <cstdio>
#include <vector>

static std::vector<short> render(bool optimized) {
    MP3Decoder_ClearBuffer();
    std::vector<short> pcm;
    const int windows[][4] = {
        {0,0,0,0}, {1,1,0,0}, {2,2,0,0}, {2,2,1,1},
        {3,3,0,0}, {0,0,0,0}, {1,0,0,0}, {2,0,0,0},
        {3,0,0,0}, {0,0,0,0}, {0,0,0,0}, {0,0,0,0},
        {0,0,0,0}, {0,0,0,0}, {0,0,0,0}, {0,0,0,0},
    };
    unsigned skipped = 0;
    for (unsigned gr = 0; gr < sizeof(windows) / sizeof(windows[0]); ++gr) {
        m_MPEGVersion = MPEG1;
        m_SFBandTable = sfBandTable[0][0];
        m_sMode = (gr == 10 ? Stereo : Joint);
        m_FrameHeader->modeExt = gr == 11 ? 3 : 2;
        m_MP3DecInfo->nChans = gr == 8 || gr == 12 ? 1 : 2;
        for (int ch = 0; ch < 2; ++ch) {
            m_SideInfoSub[0][ch].blockType = windows[gr][ch];
            m_SideInfoSub[0][ch].mixedBlock = windows[gr][ch + 2];
            m_HuffmanInfo->nonZeroBound[ch] = 576;
            m_HuffmanInfo->gb[ch] = 8;
            for (int i = 0; i < 576; ++i)
                m_HuffmanInfo->huffDecBuf[ch][i] =
                    (((i * 17 + gr * 11 + ch * 7) % 101) - 50) * 8192;
        }
        if (m_MP3DecInfo->nChans == 1) {
            m_SideInfoSub[0][1] = m_SideInfoSub[0][0];
            for (int i = 0; i < 576; ++i)
                m_HuffmanInfo->huffDecBuf[1][i] = m_HuffmanInfo->huffDecBuf[0][i];
        }
        bool fast = MonoMidSide(0);
        if (optimized) {
            if (fast) {
                ++skipped;
                for (int i = 0; i < 576; ++i)
                    m_HuffmanInfo->huffDecBuf[0][i] = MonoAverage(
                        m_HuffmanInfo->huffDecBuf[0][i], m_HuffmanInfo->huffDecBuf[1][i]);
            }
            assert(MonoIMDCT(0, fast) == 0);
        } else {
            assert(IMDCT(0, 0) == 0);
            assert(IMDCT(0, 1) == 0);
            int mask = 0;
            for (int b = 0; b < 18; ++b)
                for (int i = 0; i < 32; ++i) {
                    int value = MonoAverage(m_IMDCTInfo->outBuf[0][b][i], m_IMDCTInfo->outBuf[1][b][i]);
                    m_IMDCTInfo->outBuf[0][b][i] = value;
                    mask |= FASTABS(value);
                }
            m_IMDCTInfo->gb[0] = CLZ(mask) - 1;
        }
        short block[576];
        assert(Subband(block) == 0);
        pcm.insert(pcm.end(), block, block + 576);
    }
    if (optimized) assert(skipped > 4);
    return pcm;
}

int main() {
    assert(MonoAverage(INT_MAX, INT_MAX) == INT_MAX);
    assert(MonoAverage(INT_MIN, INT_MIN) == INT_MIN);
    assert(MonoAverage(INT_MIN, INT_MAX) == -1);
    assert(MonoAverage(-3, 2) == -1);
    assert(MP3Decoder_AllocateBuffers());
    m_MP3DecInfo->nChans = 2;
    m_sMode = Joint;
    m_FrameHeader->modeExt = 2;
    assert(MonoMidSide(0));
    m_FrameHeader->modeExt = 3;
    assert(!MonoMidSide(0));
    m_FrameHeader->modeExt = 2;
    m_SideInfoSub[0][1].mixedBlock = 1;
    assert(!MonoMidSide(0));
    m_SideInfoSub[0][1].mixedBlock = 0;
    m_IMDCTInfo->prevType[1] = 2;
    assert(!MonoMidSide(0));
    m_IMDCTInfo->prevType[1] = 0;
    m_IMDCTInfo->overBuf[0][0] = 1000;
    m_IMDCTInfo->overBuf[1][0] = -600;
    MonoCollapseOverlap();
    assert(m_MonoOverlap && m_IMDCTInfo->overBuf[0][0] == 200);
    m_IMDCTInfo->overBuf[1][0] = 999999;
    MonoExpandOverlap();
    assert(!m_MonoOverlap && m_IMDCTInfo->overBuf[1][0] == 200);
    const auto reference = render(false);
    const auto mono = render(true);
    int maximum = 0;
    assert(mono.size() == reference.size());
    for (size_t i = 0; i < mono.size(); ++i)
        maximum = std::max(maximum, abs(int(mono[i]) - int(reference[i])));
    assert(maximum <= 2);
    MP3Decoder_ClearBuffer();
    assert(!m_MonoOverlap);
    assert(render(true) == mono);
    short guarded[577];
    guarded[576] = 12345;
    m_MP3DecInfo->nGrans = 2;
    m_MP3DecInfo->nGranSamps = 576;
    m_MP3DecInfo->nChans = 2;
    m_OutputBufferSamples = 576;
    MP3ClearBadFrame(guarded);
    assert(guarded[576] == 12345);
    for (int i = 0; i < 576; ++i) assert(guarded[i] == 0);
    MP3Decoder_FreeBuffers();
    std::printf("mono overlap/window/reset/canary PASS, max PCM error=%d\n", maximum);
}
