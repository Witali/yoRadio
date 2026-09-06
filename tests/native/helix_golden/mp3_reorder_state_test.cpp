/* Test private scratch lifetime without adding firmware instrumentation. */
#include "../../../yoRadio/src/audioI2S/mp3_decoder/mp3_decoder.cpp"
#include "aac_decoder.h"
#include <cstdio>

struct Allocation {
    unsigned char *raw;
    size_t size;
    CodecArenaOwner owner;
    bool word;
};
static Allocation live[64];
static int attempts, failAt = -1;
static constexpr size_t guard = 16;

static void checkGuards(const Allocation &a) {
    for (size_t i = 0; i < guard; ++i) {
        assert(a.raw[i] == 0xa5);
        assert(a.raw[guard + a.size + i] == 0xa5);
    }
}
static void *allocate(CodecArenaOwner owner, size_t count, size_t size, bool word) {
    if (attempts++ == failAt) return nullptr;
    const size_t bytes = count * size;
    for (auto &a : live) {
        if (a.raw) continue;
        a = {static_cast<unsigned char *>(calloc(1, bytes + 2 * guard)), bytes, owner, word};
        assert(a.raw);
        memset(a.raw, 0xa5, guard);
        memset(a.raw + guard + bytes, 0xa5, guard);
        assert(reinterpret_cast<uintptr_t>(a.raw + guard) % alignof(int) == 0);
        return a.raw + guard;
    }
    assert(false && "test allocator exhausted");
    return nullptr;
}
bool CodecArenaReserve() { return true; }
bool CodecArenaDiscard() { return true; }
void *CodecArenaCalloc(CodecArenaOwner o, size_t n, size_t s) { return allocate(o,n,s,false); }
void *CodecArenaCalloc32(CodecArenaOwner o, size_t n, size_t s) { return allocate(o,n,s,true); }
void CodecArenaFree(void *pointer) {
    if (!pointer) return;
    for (auto &a : live) {
        if (!a.raw || a.raw + guard != pointer) continue;
        checkGuards(a);
        free(a.raw);
        a = {};
        return;
    }
    assert(false && "double free or scratch alias freed as an owner");
}
void CodecArenaRelease(CodecArenaOwner o) {
    for (const auto &a : live) assert(!a.raw || a.owner != o);
}
size_t CodecArenaCapacity() { return 65536; }
size_t CodecArenaUsed() {
    size_t bytes = 0;
    for (const auto &a : live) if (a.raw) bytes += a.size;
    return bytes;
}

static void checkReorder() {
    int reference[576], scratch[m_MAX_REORDER_SAMPS];
    int *work = MP3ReorderBuffer();
#if YORADIO_HELIX_MP3_SHARED_REORDER
    assert(work == reinterpret_cast<int *>(m_IMDCTInfo->outBuf[0]));
#else
    assert(work == m_DequantInfo->workBuf);
#endif
    m_FrameHeader->modeExt = 0;
    for (int version = 0; version < 3; ++version)
        for (int rate = 0; rate < 3; ++rate)
            for (int mixed = 0; mixed < 2; ++mixed)
                for (int ch = 0; ch < 2; ++ch) {
                    m_MPEGVersion = static_cast<MPEGVersion_t>(version);
                    m_SFBandTable = sfBandTable[version][rate];
                    SideInfoSub_t info = {};
                    info.blockType = 2;
                    info.mixedBlock = mixed;
                    info.globalGain = 190;
                    ScaleFactorInfoSub_t factors = {};
                    CriticalBandInfo_t refBand = {}, actualBand = {};
                    for (int i = 0; i < 576; ++i) {
                        uint32_t value = (i % 3 ? 0x80000000U : 0U) | (1U + (i * 17U) % 127U);
                        reference[i] = m_HuffmanInfo->huffDecBuf[ch][i] = static_cast<int>(value);
                    }
                    for (int i = 0; i < 288; ++i) {
                        m_IMDCTInfo->overBuf[0][i] = i + 123;
                        m_IMDCTInfo->overBuf[1][i] = -i - 321;
                    }
#if YORADIO_HELIX_MP3_SHARED_REORDER
                    work[m_MAX_REORDER_SAMPS] = 123456789;
#endif
                    int refBound = 576, actualBound = 576;
                    int refGb = DequantChannel(reference, scratch, &refBound, &info, &factors, &refBand);
                    int actualGb = DequantChannel(m_HuffmanInfo->huffDecBuf[ch], work,
                        &actualBound, &info, &factors, &actualBand);
                    assert(refGb == actualGb && refBound == actualBound);
                    assert(memcmp(reference, m_HuffmanInfo->huffDecBuf[ch], sizeof(reference)) == 0);
                    assert(memcmp(&refBand, &actualBand, sizeof(refBand)) == 0);
#if YORADIO_HELIX_MP3_SHARED_REORDER
                    assert(work[m_MAX_REORDER_SAMPS] == 123456789);
#endif
                    for (int i = 0; i < 288; ++i) {
                        assert(m_IMDCTInfo->overBuf[0][i] == i + 123);
                        assert(m_IMDCTInfo->overBuf[1][i] == -i - 321);
                    }
                    for (const auto &a : live) if (a.raw) checkGuards(a);
                }
    MP3Decoder_ClearBuffer();
    assert(MP3ReorderBuffer() == work);
    for (int i = 0; i < m_MAX_REORDER_SAMPS; ++i) assert(work[i] == 0);
}

int main() {
    static_assert(sizeof(DequantInfo_t) == 792, "update memory-saving expectation");
    assert(MP3Decoder_AllocateBuffers());
    const int allocationCount = attempts;
    size_t heap = 0, word = 0;
    for (const auto &a : live) if (a.raw) (a.word ? word : heap) += a.size;
    checkReorder();
    MP3Decoder_FreeBuffers();
    MP3Decoder_FreeBuffers();
    assert(CodecArenaUsed() == 0);
    for (int failure = 0; failure < allocationCount; ++failure) {
        attempts = 0;
        failAt = failure;
        assert(!MP3Decoder_AllocateBuffers());
        assert(CodecArenaUsed() == 0);
        MP3Decoder_FreeBuffers();
        failAt = -1;
        assert(MP3Decoder_AllocateBuffers());
        checkReorder();
        MP3Decoder_FreeBuffers();
    }
    for (int cycle = 0; cycle < 50; ++cycle) {
        assert(AACDecoder_AllocateBuffers());
        AACDecoder_FreeBuffers();
        assert(MP3Decoder_AllocateBuffers());
        MP3Decoder_ClearBuffer();
        MP3Decoder_FreeBuffers();
        assert(CodecArenaUsed() == 0);
    }
    std::printf("heap=%zu word=%zu allocations=%d; short/mixed 9 rates, failure cleanup, 50 AAC/MP3 cycles PASS\n",
                heap, word, allocationCount);
}
