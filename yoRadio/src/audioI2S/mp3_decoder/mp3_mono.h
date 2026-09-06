/* Private helpers, included after decoder state in mp3_decoder.cpp. */
#pragma once

#if YORADIO_HELIX_MP3_MONO
/* Overlap is in the (L+R)/2 domain, not encoded M. Discarded side history
 * must not reappear on fallback to independently windowed L/R transforms. */
static bool m_MonoOverlap;

static int MonoAverage(int a, int b) {
    return (a >> 1) + (b >> 1) + ((a & b) & 1);
}

static bool MonoOverlapCompatible() {
    return m_MonoOverlap ||
        (m_IMDCTInfo->prevType[0] == m_IMDCTInfo->prevType[1] &&
         m_IMDCTInfo->prevWinSwitch[0] == m_IMDCTInfo->prevWinSwitch[1]);
}

static bool MonoMidSide(int gr) {
    return m_MP3DecInfo->nChans == 2 && m_sMode == Joint &&
        m_FrameHeader->modeExt == 2 &&
        m_SideInfoSub[gr][0].blockType == m_SideInfoSub[gr][1].blockType &&
        m_SideInfoSub[gr][0].mixedBlock == m_SideInfoSub[gr][1].mixedBlock &&
        MonoOverlapCompatible();
}

static void MonoCollapseOverlap() {
    if (m_MonoOverlap) return;
    for (int i = 0; i < m_MAX_NSAMP / 2; ++i)
        m_IMDCTInfo->overBuf[0][i] = MonoAverage(
            m_IMDCTInfo->overBuf[0][i], m_IMDCTInfo->overBuf[1][i]);
    if (m_IMDCTInfo->numPrevIMDCT[1] > m_IMDCTInfo->numPrevIMDCT[0])
        m_IMDCTInfo->numPrevIMDCT[0] = m_IMDCTInfo->numPrevIMDCT[1];
    m_MonoOverlap = true;
}

static void MonoExpandOverlap() {
    if (!m_MonoOverlap) return;
    /* Aligned word accesses also work for IRAM workspaces. */
    for (int i = 0; i < m_MAX_NSAMP / 2; ++i)
        m_IMDCTInfo->overBuf[1][i] = m_IMDCTInfo->overBuf[0][i];
    m_IMDCTInfo->numPrevIMDCT[1] = m_IMDCTInfo->numPrevIMDCT[0];
    m_IMDCTInfo->prevType[1] = m_IMDCTInfo->prevType[0];
    m_IMDCTInfo->prevWinSwitch[1] = m_IMDCTInfo->prevWinSwitch[0];
    m_MonoOverlap = false;
}

static int MonoIMDCT(int gr, bool midSide) {
    if (midSide || (m_MP3DecInfo->nChans == 1 && MonoOverlapCompatible())) {
        MonoCollapseOverlap();
        return IMDCT(gr, 0);
    }
    MonoExpandOverlap();
    if (m_MP3DecInfo->nChans == 1) {
        /* A stereo->mono header change may leave differently windowed old
         * overlaps. Feed mono to both transforms for this granule only. */
        for (int i = 0; i < m_MAX_NSAMP; ++i)
            m_HuffmanInfo->huffDecBuf[1][i] = m_HuffmanInfo->huffDecBuf[0][i];
        m_HuffmanInfo->nonZeroBound[1] = m_HuffmanInfo->nonZeroBound[0];
        m_HuffmanInfo->gb[1] = m_HuffmanInfo->gb[0];
        m_SideInfoSub[gr][1] = m_SideInfoSub[gr][0];
    }
    if (IMDCT(gr, 0) < 0 || IMDCT(gr, 1) < 0) return -1;
    int mask = 0;
    for (int b = 0; b < m_BLOCK_SIZE; ++b) {
        for (int i = 0; i < m_NBANDS; ++i) {
            int value = MonoAverage(m_IMDCTInfo->outBuf[0][b][i],
                                    m_IMDCTInfo->outBuf[1][b][i]);
            m_IMDCTInfo->outBuf[0][b][i] = value;
            mask |= FASTABS(value);
        }
    }
    m_IMDCTInfo->gb[0] = CLZ(mask) - 1;
    return 0;
}
#endif
