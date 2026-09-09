#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "opus.h"
#ifdef YORADIO_OPUS_BOUNDED
#include "opus_memory.h"
#define GUARD 0x5a39ce71U
static struct { uint32_t before[2], data[4096], after[2]; } words;
static struct { uint32_t before[2], data[1792], after[2]; } bytes;
static void bind_arenas(size_t byte_capacity) {
    words.before[0] = words.before[1] = words.after[0] = words.after[1] = GUARD;
    bytes.before[0] = bytes.before[1] = bytes.after[0] = bytes.after[1] = GUARD;
    yoradio_opus_memory_bind(bytes.data, byte_capacity, words.data, sizeof(words.data));
}
static int guards_ok(void) {
    return words.before[0] == GUARD && words.before[1] == GUARD &&
        words.after[0] == GUARD && words.after[1] == GUARD &&
        bytes.before[0] == GUARD && bytes.before[1] == GUARD &&
        bytes.after[0] == GUARD && bytes.after[1] == GUARD;
}
#else
static int guards_ok(void) { return 1; }
#endif
static void check(int condition, const char *message) {
    if (!condition) { fprintf(stderr, "%s\n", message); exit(1); }
}
static int decode(OpusDecoder *decoder, const unsigned char *packet, int length, int16_t *pcm) {
#ifdef YORADIO_OPUS_BOUNDED
    return yoradio_opus_decode_bounded(decoder, packet, length, pcm, 5760);
#else
    return opus_decode(decoder, packet, length, pcm, 5760, 0);
#endif
}
static void initialize(OpusDecoder *decoder) {
#ifdef YORADIO_OPUS_BOUNDED
    bind_arenas(sizeof(bytes.data));
#endif
    check(opus_decoder_init(decoder, 48000, 1) == OPUS_OK, "decoder initialization failed");
}
static void self_test(OpusDecoder *decoder, const unsigned char *packet, int length) {
    int16_t reference[5760], actual[5760];
    initialize(decoder);
    int expected = decode(decoder, packet, length, reference);
    check(expected > 0, "fresh decode failed");
    check(decode(decoder, packet, length, actual) > 0, "warmup decode failed");
    check(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK, "state reset failed");
    int count = decode(decoder, packet, length, actual);
    check(count == expected && !memcmp(reference, actual, count * sizeof(*actual)), "reset PCM differs from fresh decoder");
    check(guards_ok(), "reset corrupted arena guards");
#ifdef YORADIO_OPUS_BOUNDED
    // Zero DRAM scratch forces the bounded wrapper's OOM path on every fixture.
    bind_arenas(0);
    check(opus_decoder_init(decoder, 48000, 1) == OPUS_OK, "small-arena initialization failed");
    check(decode(decoder, packet, length, actual) == OPUS_ALLOC_FAIL, "undersized scratch did not return OPUS_ALLOC_FAIL");
    check(guards_ok(), "OOM corrupted arena guards");
    // OOM may interrupt state updates. Rebind and reinitialize before reuse.
    initialize(decoder);
    count = decode(decoder, packet, length, actual);
    check(count == expected && !memcmp(reference, actual, count * sizeof(*actual)), "OOM recovery PCM differs from fresh decoder");
    check(guards_ok(), "OOM recovery corrupted arena guards");
#endif
}

int main(int argc, char **argv) {
    if (argc == 1) {
        printf("{\"libopus\":\"%s\",\"mono_state_bytes\":%d,\"stereo_state_bytes\":%d}\n",
            opus_get_version_string(), opus_decoder_get_size(1), opus_decoder_get_size(2));
        return 0;
    }
    check(argc == 3 || (argc == 4 && !strcmp(argv[3], "--self-test")), "usage: probe packets.opuspkt decoded.pcm [--self-test]");
    OpusDecoder *decoder = malloc(opus_decoder_get_size(1));
    check(decoder != NULL, "decoder allocation failed");
    initialize(decoder);
    FILE *in = fopen(argv[1], "rb"), *out = fopen(argv[2], "wb");
    check(in && out, "cannot open input/output");
    unsigned char packet[4096], first_packet[4096];
    unsigned first_size = 0, samples = 0, packets = 0, silk = 0, hybrid = 0, celt = 0;
    int16_t pcm[5760];
    for (;;) {
        unsigned char length[2];
        size_t read = fread(length, 1, 2, in);
        if (!read) break;
        check(read == 2, "truncated packet length");
        unsigned size = length[0] | ((unsigned)length[1] << 8);
        check(size && size <= sizeof(packet), "invalid packet length");
        check(fread(packet, 1, size, in) == size, "truncated packet body");
        if (!packets) { memcpy(first_packet, packet, size); first_size = size; }
        unsigned config = packet[0] >> 3;
        if (config < 12) ++silk;
        else if (config < 16) ++hybrid;
        else ++celt;
        int count = decode(decoder, packet, size, pcm);
        if (count <= 0) { fprintf(stderr, "decode failed packet %u error %d\n", packets, count); return 1; }
        check(guards_ok(), "decode corrupted arena guards");
        check(fwrite(pcm, sizeof(*pcm), count, out) == (size_t)count, "PCM write failed");
        samples += count;
        ++packets;
    }
    check(!ferror(in) && packets > 0, "empty or unreadable packet fixture");
    check(fclose(in) == 0 && fclose(out) == 0, "file close failed");
#ifdef YORADIO_OPUS_BOUNDED
    size_t peak_bytes = yoradio_opus_scratch_peak_bytes(), peak_words = yoradio_opus_scratch_peak_words();
#endif
    if (argc == 4) self_test(decoder, first_packet, first_size);
    printf("{\"libopus\":\"%s\",\"mono_state_bytes\":%d,\"stereo_state_bytes\":%d,"
        "\"output_channels\":1,\"sample_rate\":48000,\"packets\":%u,\"samples\":%u,"
        "\"modes\":{\"SILK\":%u,\"hybrid\":%u,\"CELT\":%u},\"reset_exact\":%s",
        opus_get_version_string(), opus_decoder_get_size(1), opus_decoder_get_size(2),
        packets, samples, silk, hybrid, celt, argc == 4 ? "true" : "null");
#ifdef YORADIO_OPUS_BOUNDED
    printf(",\"scratch_byte_peak_bytes\":%zu,\"scratch_word_peak_bytes\":%zu,"
        "\"scratch_byte_capacity_bytes\":%zu,\"scratch_word_capacity_bytes\":%zu,"
        "\"arena_guards_ok\":true,\"oom_reinitialized_exact\":%s", peak_bytes, peak_words,
        sizeof(bytes.data), sizeof(words.data), argc == 4 ? "true" : "null");
#endif
    puts("}");
    free(decoder);
    return 0;
}
