#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "opus.h"
#ifdef YORADIO_OPUS_BOUNDED
#include "config.h"
#include "structs.h"
#include "opus_memory.h"
extern int silk_init_decoder(silk_decoder_state *state);
#define GUARD 0x5a39ce71U
#ifndef OPUS_PROBE_BYTE_CAPACITY
#define OPUS_PROBE_BYTE_CAPACITY 7680
#endif
static struct { uint32_t before[2], data[4096], after[2]; } words;
static struct { uint32_t before[2], data[OPUS_PROBE_BYTE_CAPACITY / 4], after[2]; } bytes;
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
#ifdef YORADIO_OPUS_BOUNDED
static void persistent_test(OpusDecoder *decoder) {
    /* Inspect the private SILK prefix through OpusDecoder's two offsets. This
       deliberately tracks the vendored ABI, not a public libopus API. */
    int offsets[2];
    bind_arenas(sizeof(bytes.data));
    check(yoradio_opus_history_begin(), "persistent begin failed");
    check(yoradio_opus_history(SIZE_MAX) == NULL && yoradio_opus_scratch_mark().words == 0,
          "overflowing persistent allocation changed the arena");
    check(yoradio_opus_history(1) == words.data &&
          yoradio_opus_history(1) == (unsigned char *)words.data + 8 &&
          yoradio_opus_scratch_mark().words == 16, "persistent allocations do not accumulate with alignment");
    yoradio_opus_memory_bind(bytes.data, sizeof(bytes.data), words.data, 11231);
    check(opus_decoder_init(decoder, 48000, 1) == OPUS_ALLOC_FAIL, "undersized persistent arena was accepted");
    initialize(decoder);
    memcpy(offsets, decoder, sizeof(offsets));
    silk_decoder_state *channels = (silk_decoder_state *)((char *)decoder + offsets[1]);
    opus_int32 *first = channels[0].exc_Q14, *second = channels[1].exc_Q14;
    check(first == (opus_int32 *)words.data && second == first + MAX_FRAME_LENGTH,
          "SILK persistent regions overlap or were not prebound");
    check(yoradio_opus_scratch_mark().words == 11232, "incorrect cumulative persistent size");
    for (int iteration = 0; iteration < 3; iteration++) {
        first[0] = 123; second[MAX_FRAME_LENGTH - 1] = -456;
        check(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK, "persistent reset failed");
        check(channels[0].exc_Q14 == first && channels[1].exc_Q14 == second,
              "whole SILK reset lost persistent pointers");
        check(first[0] == 0 && second[MAX_FRAME_LENGTH - 1] == 0, "persistent reset did not clear excitation");
        /* Same initializer used by the in-packet mono-to-stereo transition. */
        first[0] = 123; second[0] = -456;
        check(silk_init_decoder(&channels[1]) == 0, "channel reinitialization failed");
        check(channels[1].exc_Q14 == second && second[0] == 0 && first[0] == 123,
              "channel initialization lost or overlapped excitation");
        check(yoradio_opus_scratch_mark().words == 11232, "channel initialization allocated history");
        check(opus_decoder_init(decoder, 48000, 1) == OPUS_OK, "reinitialization without rebind failed");
        check(yoradio_opus_scratch_mark().words == 11232, "reinitialization leaked persistent memory");
        check(channels[0].exc_Q14 == first && channels[1].exc_Q14 == second,
              "reinitialization changed persistent layout");
    }
    check(guards_ok(), "persistent tests corrupted guards");
}
#endif
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
    persistent_test(decoder);
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

/* Continuous mixed-mode/channel corpus, with PLC after every eighth packet.
 * Write round one for byte-exact baseline/bounded comparison; round two starts
 * from OPUS_RESET_STATE and compares every sample against the saved sequence. */
static int sequence_test(int argc, char **argv) {
    check(argc >= 5, "usage: probe --sequence output.pcm input1.opuspkt input2.opuspkt ...");
    OpusDecoder *decoder = malloc(opus_decoder_get_size(1));
    check(decoder != NULL, "sequence decoder allocation failed");
    initialize(decoder);
    FILE *out = fopen(argv[2], "w+b");
    check(out != NULL, "cannot open sequence output");
    unsigned expected_samples = 0, packets = 0, losses = 0;
    for (int round = 0; round < 2; round++) {
        unsigned samples = 0;
        packets = losses = 0;
        if (round) {
            check(fflush(out) == 0 && fseek(out, 0, SEEK_SET) == 0, "sequence rewind failed");
            check(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK, "sequence reset failed");
        }
        for (int fixture = 3; fixture < argc; fixture++) {
            FILE *in = fopen(argv[fixture], "rb");
            check(in != NULL, "cannot open sequence input");
            for (;;) {
                unsigned char length[2], packet[4096];
                int16_t pcm[5760];
                size_t read = fread(length, 1, 2, in);
                if (!read) break;
                check(read == 2, "truncated sequence packet length");
                unsigned size = length[0] | ((unsigned)length[1] << 8);
                check(size && size <= sizeof(packet), "invalid sequence packet length");
                check(fread(packet, 1, size, in) == size, "truncated sequence packet");
                for (int plc = 0; plc < 1 + ((packets & 7U) == 7U); plc++) {
                    int count;
#ifdef YORADIO_OPUS_BOUNDED
                    count = yoradio_opus_decode_bounded(decoder, plc ? NULL : packet, plc ? 0 : (int)size, pcm, 960);
                    check(yoradio_opus_scratch_mark().words == 11232, "packet changed persistent reservation");
#else
                    count = opus_decode(decoder, plc ? NULL : packet, plc ? 0 : (int)size, pcm, 960, 0);
#endif
                    if (count <= 0) fprintf(stderr, "sequence decode failed fixture %d packet %u PLC %d error %d\n", fixture, packets, plc, count);
                    check(count > 0, "sequence decode failed");
                    check(guards_ok(), "sequence corrupted arena guards");
                    if (!round) check(fwrite(pcm, sizeof(*pcm), count, out) == (size_t)count, "sequence PCM write failed");
                    if (round) {
                        int16_t reference[5760];
                        check(fread(reference, sizeof(*reference), count, out) == (size_t)count &&
                              !memcmp(pcm, reference, count * sizeof(*pcm)), "mixed-mode/channel PLC reset PCM differs");
                    }
                    samples += count;
                    losses += plc;
                }
                packets++;
            }
            check(!ferror(in) && fclose(in) == 0, "sequence input failed");
        }
        if (!round) expected_samples = samples;
        else check(samples == expected_samples, "mixed-mode/channel PLC reset sample count differs");
    }
    check(fclose(out) == 0, "sequence output close failed");
    printf("{\"sequence_packets\":%u,\"plc_frames\":%u,\"samples\":%u,\"reset_exact\":true", packets, losses, expected_samples);
#ifdef YORADIO_OPUS_BOUNDED
    printf(",\"persistent_bytes\":%zu,\"scratch_byte_peak_bytes\":%zu,\"scratch_word_peak_bytes\":%zu,\"scratch_byte_capacity_bytes\":%zu",
           yoradio_opus_scratch_mark().words, yoradio_opus_scratch_peak_bytes(), yoradio_opus_scratch_peak_words(), sizeof(bytes.data));
#endif
    puts("}");
    free(decoder);
    return 0;
}

int main(int argc, char **argv) {
    if (argc > 1 && !strcmp(argv[1], "--sequence")) return sequence_test(argc, argv);
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
