#include "../../../yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp"
#include <cassert>
#include <cstdio>

int main() {
    unsigned vectors = 0;
    for (int book = 0; book < 12; ++book) {
        const HuffInfo_t *info = book == 11 ? &huffTabScaleFactInfo : &huffTabSpecInfo[book];
        const short *symbols = book == 11 ? huffTabScaleFact : huffTabSpec;
        // Every possible maximum-length prefix, with both extreme suffixes.
        for (unsigned prefix = 0; prefix < (1U << info->maxBits); ++prefix) {
            for (unsigned suffix : {0U, (1U << (32 - info->maxBits)) - 1U}) {
                const uint32_t input = (prefix << (32 - info->maxBits)) | suffix;
                int32_t expected, actual;
                const int bits = DecodeHuffmanScalar(symbols, info, input, &expected);
                const int got = aac_huffman_decode(book, input, &actual);
                assert(bits == got && expected == actual);
                ++vectors;
            }
        }
    }
    std::printf("AAC Huffman: %u exhaustive prefixes/suffixes, exact symbols and bit counts\n", vectors);
}
