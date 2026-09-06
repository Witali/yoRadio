#include "../../../yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp"
#include <cassert>
#include <cstdio>
#include <cstring>

static uint32_t oracle(const unsigned char *data, int size, int position, int bits) {
    uint32_t value = 0;
    while (bits--) {
        value <<= 1;
        if (position < size * 8) value |= (data[position / 8] >> (7 - (position & 7))) & 1U;
        ++position;
    }
    return value;
}

int main() {
    unsigned char input[100];
    uint32_t random = 8266;
    for (auto &byte : input) { random ^= random << 13; random ^= random >> 17; random ^= random << 5; byte = random; }
    unsigned vectors = 0;
    // Exercise all byte alignments, cache offsets, lookahead sizes and end tails.
    for (int align = 0; align < 4; ++align) for (int size = 1; size <= 60; ++size)
    for (int skip = 0; skip <= 31 && skip < size * 8; ++skip)
    for (int look = 0; look <= 31; ++look) {
        SetBitstreamPointer(size, input + align);
        GetBits(skip);
        const auto before = m_aac_BitStreamInfo;
        const unsigned expected = oracle(input + align, size, skip, look);
        const unsigned actual = GetBitsNoAdvance(look);
        assert(expected == actual);
        assert(CalcBitsUsed(input + align, 0) == skip);
        assert(std::memcmp(&before, &m_aac_BitStreamInfo, sizeof(before)) == 0);
        const int available = size * 8 - skip;
        for (int take = 0; take <= look && take <= available; ++take) {
            m_aac_BitStreamInfo = before;
            AdvanceBitstream(take);
            assert(GetBitsNoAdvance(17) == oracle(input + align, size, skip + take, 17));
            assert(CalcBitsUsed(input + align, 0) == skip + take);
            ++vectors;
        }
    }
    std::printf("AAC bit reader: %u peek/consume comparisons, exact bits and logical positions\n", vectors);
}
