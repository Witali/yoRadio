/* Native AAC-LC sequential window/overlap output. Included by aac_decoder.cpp.
 * No full PCM frame: coefficients stay read-only during emission, and each
 * old overlap word is replaced only after its output sample has been read.
 * All accesses to the coefficient/overlap IRAM arena remain aligned int32. */
struct AACWindowState {
    int sequence;
    const int *previous;
    const int *current;
};

struct AACBlockOutput {
    int frames;
    bool mono;
    AACPCMCallback sink;
    void *context;
    AACWindowState window[2];
};

/* Tables contain interleaved low/high window coefficients. */
static inline int aac_window_index(int n, int size) {
    return n < size / 2 ? 2 * n : 2 * (size - 1 - n) + 1;
}

static inline int aac_short_first(const int *coef, const int *window, int n) {
    const int i = n < 64 ? n : 127 - n;
    const int value = MULSHIFT32(window[aac_window_index(n, 128)], coef[64 + i]);
    return n < 64 ? -value : value;
}

static inline int aac_short_second(const int *coef, const int *window, int n) {
    const int i = n < 64 ? n : 127 - n;
    return MULSHIFT32(window[aac_window_index(127 - n, 128)], coef[63 - i]);
}

static inline short aac_window_sample(const AACWindowState &w,
                                      const int *coef, int *overlap, int n) {
    int current = 0, next = 0;
    if (w.sequence == 2) {
        /* Eight 256-sample short windows, stride 128, start offset 448.
         * Current PCM and next overlap each need at most two contributions.
         * Only the first short window uses the previous window shape. */
        if (n >= 448) {
            const int block = (n - 448) >> 7;
            const int local = (n - 448) & 127;
            current = aac_short_first(coef + block * 128,
                block ? w.current : w.previous, local);
            if (block) current += aac_short_second(coef + (block - 1) * 128,
                                                   w.current, local);
        }
        if (n < 576) {
            const int block = (576 + n) >> 7;
            const int local = (576 + n) & 127;
            if (block < 8)
                next = aac_short_first(coef + block * 128, w.current, local);
            next += aac_short_second(coef + (block - 1) * 128, w.current, local);
        }
    } else {
        const int i = n < 512 ? n : 1023 - n;
        const int input = coef[512 + i];
        if (w.sequence != 3) {
            const int value = MULSHIFT32(w.previous[aac_window_index(n, 1024)], input);
            current = n < 512 ? -value : value;
        } else if (n >= 576) {
            current = input >> 1;
        } else if (n >= 448) {
            const int value = MULSHIFT32(w.previous[aac_window_index(n - 448, 128)], input);
            current = n < 512 ? -value : value;
        }
        if (w.sequence != 1) {
            next = MULSHIFT32(w.current[aac_window_index(1023 - n, 1024)], coef[511 - i]);
        } else if (n < 448) {
            next = coef[511 - i] >> 1;
        } else if (n < 576) {
            next = MULSHIFT32(w.current[aac_window_index(575 - n, 128)], coef[511 - i]);
        }
    }
    const int value = overlap[n] + current;
    overlap[n] = next;
    return CLIPTOSHORT((value + (1 << (FBITS_OUT_IMDCT - 1))) >> FBITS_OUT_IMDCT);
}

static AACWindowState aac_window_state(int ch, int chOut) {
    const ICSInfo_t &ics = m_PSInfoBase->icsInfo[
        ch == 1 && m_PSInfoBase->commonWin ? 0 : ch];
    const int previousSize = (ics.winSequence == 2 || ics.winSequence == 3) ? 0 : 1;
    const int currentSize = (ics.winSequence == 1 || ics.winSequence == 2) ? 0 : 1;
    return {ics.winSequence,
        m_PSInfoBase->prevWinShape[chOut] == 1
            ? kbdWindow + kbdWindowOffset[previousSize]
            : sinWindow + sinWindowOffset[previousSize],
        ics.winShape == 1 ? kbdWindow + kbdWindowOffset[currentSize]
                          : sinWindow + sinWindowOffset[currentSize]};
}

static int aac_emit_blocks(short *pcm, AACBlockOutput &output) {
    const int channels = m_AACDecInfo->nChans;
    for (int start = 0; start < 1024; start += output.frames) {
        HELIX_PROFILE_BEGIN(HELIX_STAGE_SYNTHESIS);
        for (int i = 0; i < output.frames; ++i) {
            const int n = start + i;
            const short left = aac_window_sample(output.window[0],
                m_PSInfoBase->coef[0], m_PSInfoBase->overlap[0], n);
            if (channels == 1) {
                pcm[i] = left;
            } else {
                const short right = aac_window_sample(output.window[1],
                    m_PSInfoBase->coef[1], m_PSInfoBase->overlap[1], n);
                if (output.mono) pcm[i] = static_cast<short>((static_cast<int>(left) + right) >> 1);
                else { pcm[2 * i] = left; pcm[2 * i + 1] = right; }
            }
        }
        HELIX_PROFILE_END(HELIX_STAGE_SYNTHESIS);
        if (!output.sink(output.context, pcm, output.frames * (output.mono ? 1 : channels))) {
            AACFlushCodec(); // partially updated overlap must never reach the next stream
            return ERR_AAC_OUTPUT_CANCELLED;
        }
    }
    return ERR_AAC_NONE;
}

/* Two SCEs must retain both transformed channels until the whole frame has
 * been parsed. Helpers still use local channel indices; restore even on error. */
struct AACCoefOffset {
    int (*saved)[1024];
    AACCoefOffset(int channels) : saved(m_PSInfoBase->coef) {
        m_PSInfoBase->coef += channels;
    }
    ~AACCoefOffset() { m_PSInfoBase->coef = saved; }
};
