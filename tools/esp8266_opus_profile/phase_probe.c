#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "config.h"
#include "opus.h"
#ifdef YORADIO_OPUS_BOUNDED
#include "bands.h"
#include "modes.h"
#include "opus_memory.h"
#endif

#define GUARD 0x5a39ce71U
#define TAIL 12345
static struct { uint32_t before[2]; int16_t data[960]; uint32_t after[2]; } pcm;
static unsigned borrowed[4], transient_borrowed, dual_borrowed, denied;
static void check(int condition, const char *message) {
    if (!condition) { fprintf(stderr, "%s\n", message); exit(1); }
}
#ifdef YORADIO_OPUS_BOUNDED
static struct { uint32_t before[2], data[4096], after[2]; } words;
static struct { uint32_t before[2], data[1920], after[2]; } bytes;
static size_t active_capacity;
static unsigned trace_peak;
void *__real_yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe);
void *__wrap_yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe) {
    void *result = __real_yoradio_opus_scratch_alloc(count, size, word_safe);
    opus_scratch_mark mark = yoradio_opus_scratch_mark();
    if (mark.bytes > trace_peak) {
        trace_peak = mark.bytes;
        if (getenv("OPUS_TRACE_ALLOC")) fprintf(stderr, "peak=%zu count=%zu size=%zu word=%d caller=%p\n",
            mark.bytes, count, size, word_safe, __builtin_return_address(0));
    }
    return result;
}
#define QUANT_ARGS int encode, const CELTMode *m, int start, int end, celt_norm *X, celt_norm *Y, \
    unsigned char *collapse_masks, const celt_ener *bandE, int *pulses, int shortBlocks, int spread, \
    int dual_stereo, int intensity, int *tf_res, opus_int32 total_bits, opus_int32 balance, ec_ctx *ec, \
    int LM, int codedBands, opus_uint32 *seed, int complexity, int arch, int disable_inv, \
    celt_norm *norm2_scratch, int norm2_scratch_size
void __real_quant_all_bands(QUANT_ARGS);
void __wrap_quant_all_bands(QUANT_ARGS) {
    if (norm2_scratch) {
        check(!encode && Y != NULL && LM >= 0 && LM <= 3, "invalid borrowed norm2 mode");
        check(norm2_scratch_size >= (1 << LM) * (m->eBands[m->nbEBands - 1] - m->eBands[start]), "borrowed norm2 is too short");
        borrowed[LM]++;
        transient_borrowed += shortBlocks != 0;
        dual_borrowed += dual_stereo != 0;
    } else denied++;
    __real_quant_all_bands(encode, m, start, end, X, Y, collapse_masks, bandE, pulses, shortBlocks, spread,
        dual_stereo, intensity, tf_res, total_bits, balance, ec, LM, codedBands, seed, complexity, arch,
        disable_inv, norm2_scratch, norm2_scratch_size);
}
#endif

static void prepare_pcm(void) {
    pcm.before[0] = pcm.before[1] = pcm.after[0] = pcm.after[1] = GUARD;
    for (unsigned i = 0; i < 960; i++) pcm.data[i] = TAIL;
}
static void guards_ok(unsigned used) {
    check(pcm.before[0] == GUARD && pcm.before[1] == GUARD && pcm.after[0] == GUARD && pcm.after[1] == GUARD,
        "PCM output guard corrupted");
    for (unsigned i = used; i < 960; i++) check(pcm.data[i] == TAIL, "short packet wrote past returned PCM");
#ifdef YORADIO_OPUS_BOUNDED
    check(words.before[0] == GUARD && words.before[1] == GUARD && words.after[0] == GUARD && words.after[1] == GUARD &&
        bytes.before[0] == GUARD && bytes.before[1] == GUARD && bytes.after[0] == GUARD && bytes.after[1] == GUARD,
        "scratch arena guard corrupted");
    for (size_t i = active_capacity / 4; i < 1920; i++) check(bytes.data[i] == GUARD, "scratch wrote past logical capacity");
#endif
}
int main(int argc, char **argv) {
    check(argc >= 3, "usage: phase_probe output.pcm [--plc] input.opuspkt ...");
    int with_plc = !strcmp(argv[2], "--plc"), first = with_plc ? 3 : 2;
    int rate = getenv("OPUS_PHASE_RATE") ? atoi(getenv("OPUS_PHASE_RATE")) : 48000;
    int plc_burst = getenv("OPUS_PHASE_PLC_BURST") ? atoi(getenv("OPUS_PHASE_PLC_BURST")) : 1;
    check(plc_burst > 0 && plc_burst <= 8, "invalid PLC burst");
    check(argc > first, "missing input packets");
    OpusDecoder *decoder = malloc(opus_decoder_get_size(1));
    check(decoder != NULL, "decoder allocation failed");
#ifdef YORADIO_OPUS_BOUNDED
    words.before[0] = words.before[1] = words.after[0] = words.after[1] = GUARD;
    bytes.before[0] = bytes.before[1] = bytes.after[0] = bytes.after[1] = GUARD;
    size_t capacity = getenv("OPUS_PHASE_CAPACITY") ? strtoul(getenv("OPUS_PHASE_CAPACITY"), NULL, 10) : sizeof(bytes.data);
    check(capacity <= sizeof(bytes.data) && capacity % 4 == 0, "invalid requested scratch capacity");
    active_capacity = capacity;
    for (unsigned i = 0; i < 1920; i++) bytes.data[i] = GUARD;
    yoradio_opus_memory_bind(bytes.data, capacity, words.data, sizeof(words.data));
#endif
    check(opus_decoder_init(decoder, rate, 1) == OPUS_OK, "decoder init failed");
    FILE *out = fopen(argv[1], "w+b");
    check(out != NULL, "cannot open PCM output");
    unsigned expected_samples = 0, packets = 0, losses = 0, multiframe = 0;
    for (int round = 0; round < 2; round++) {
        unsigned samples = 0;
        packets = losses = multiframe = 0;
        if (round) {
            check(fflush(out) == 0 && fseek(out, 0, SEEK_SET) == 0, "PCM rewind failed");
            check(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK, "decoder reset failed");
        }
        for (int file = first; file < argc; file++) {
            FILE *in = fopen(argv[file], "rb");
            check(in != NULL, "cannot open packet fixture");
            for (;;) {
                unsigned char length[2], packet[1536];
                size_t got = fread(length, 1, 2, in);
                if (!got) break;
                check(got == 2, "truncated packet length");
                unsigned size = length[0] | (unsigned)length[1] << 8;
                check(size && size <= sizeof(packet) && fread(packet, 1, size, in) == size, "invalid packet body");
                int expected = opus_packet_get_nb_samples(packet, size, rate);
                check(expected > 0 && expected <= rate / 50, "packet exceeds 20 ms profile");
                multiframe += opus_packet_get_nb_frames(packet, size) > 1;
                for (int loss = 0; loss < 1 + (with_plc && (packets & 7U) == 7U ? plc_burst : 0); loss++) {
                    prepare_pcm();
                    int count;
#ifdef YORADIO_OPUS_BOUNDED
                    count = yoradio_opus_decode_bounded(decoder, loss ? NULL : packet, loss ? 0 : size, pcm.data, loss ? rate / 50 : expected);
#else
                    count = opus_decode(decoder, loss ? NULL : packet, loss ? 0 : size, pcm.data, loss ? rate / 50 : expected, 0);
#endif
                    if (count <= 0) fprintf(stderr, "file=%s packet=%u loss=%d error=%d\n", argv[file], packets, loss, count);
                    check(count == (loss ? rate / 50 : expected), "decode returned wrong sample count");
                    guards_ok(count);
                    if (!round) check(fwrite(pcm.data, sizeof(*pcm.data), count, out) == (size_t)count, "PCM write failed");
                    else {
                        int16_t reference[960];
                        check(fread(reference, sizeof(*reference), count, out) == (size_t)count &&
                            !memcmp(reference, pcm.data, count * sizeof(*reference)), "reset PCM mismatch");
                    }
                    samples += count;
                    losses += loss != 0;
                }
                packets++;
            }
            check(!ferror(in) && fclose(in) == 0, "packet read failed");
        }
        if (!round) expected_samples = samples;
        else check(samples == expected_samples, "reset sample count mismatch");
    }
    check(fclose(out) == 0, "PCM close failed");
    printf("{\"samples\":%u,\"packets\":%u,\"plc_frames\":%u,\"multiframe_packets\":%u,\"sample_rate\":%d,\"reset_exact\":true,\"pcm_guards_ok\":true",
        expected_samples, packets, losses, multiframe, rate);
#ifdef YORADIO_OPUS_BOUNDED
    printf(",\"scratch_byte_peak_bytes\":%zu,\"scratch_word_peak_bytes\":%zu,\"scratch_byte_capacity_bytes\":%zu,"
        "\"borrowed_by_lm\":[%u,%u,%u,%u],\"transient_borrowed\":%u,\"dual_stereo_borrowed\":%u,\"borrow_denied\":%u",
        yoradio_opus_scratch_peak_bytes(), yoradio_opus_scratch_peak_words(), capacity,
        borrowed[0], borrowed[1], borrowed[2], borrowed[3], transient_borrowed, dual_borrowed, denied);
#endif
    puts("}");
    free(decoder);
    return 0;
}
