/* Host-only fault injection: a longjmp after lending may interrupt writes to
 * the SILK channel bodies, including the two persistent IRAM pointers. Reset
 * must work WITHOUT rebinding/reinitializing those pointers first. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "opus.h"
#include "opus_memory.h"
#if !YORADIO_OPUS_CELT_SILK_SCRATCH
#error "This test requires SILK scratch lending"
#endif
static uint64_t scratch[768], words[2048];
static unsigned fail_at, allocations, injected;
void *__real_yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe);
void *__wrap_yoradio_opus_scratch_alloc(size_t count, size_t size, int word_safe) {
    void *result = __real_yoradio_opus_scratch_alloc(count, size, word_safe);
    if (count && size && yoradio_opus_scratch_mark().loan) {
        allocations++;
        if (fail_at && allocations == fail_at) {
            /* Write first: testing an untouched pointer would miss corruption. */
            memset(result, 0xa5, count * size);
            injected++;
            (void)__real_yoradio_opus_scratch_alloc(SIZE_MAX, 2, 0);
            abort();
        }
    }
    return result;
}
static int read_packet(FILE *file, unsigned char *packet) {
    unsigned char length[2];
    size_t got = fread(length, 1, 2, file);
    if (!got) { assert(!ferror(file)); return 0; }
    assert(got == 2);
    int size = length[0] | (unsigned)length[1] << 8;
    assert(size > 0 && size <= 1536);
    assert(fread(packet, 1, size, file) == (size_t)size);
    return size;
}
int main(int argc, char **argv) {
    assert(argc >= 3);
    unsigned char silk[1536], packet[1536];
    int16_t reference[960], output[960];
    FILE *file = fopen(argv[1], "rb"); assert(file);
    int silk_size = read_packet(file, silk); assert(silk_size && !(silk[0] & 0x80));
    assert(fclose(file) == 0);
    size_t state_size = opus_decoder_get_size(1);
    unsigned char *storage = malloc(state_size + 16); assert(storage);
    memset(storage, 0x39, state_size + 16);
    OpusDecoder *decoder = (OpusDecoder *)(storage + 8);
    yoradio_opus_memory_bind(scratch, sizeof(scratch), words, sizeof(words));
    assert(!yoradio_opus_scratch_lend(scratch, sizeof(scratch)));
    assert(opus_decoder_init(decoder, 48000, 1) == OPUS_OK);
    int expected = yoradio_opus_decode_bounded(decoder, silk, silk_size, reference, 960);
    assert(expected > 0);
    unsigned packets = 0, recoveries = 0;
    for (int arg = 2; arg < argc; arg++) {
        file = fopen(argv[arg], "rb"); assert(file);
        for (unsigned index = 0; index < 12; index++) {
            int size = read_packet(file, packet); if (!size) break;
            assert(packet[0] & 0x80);
            int count = opus_packet_get_nb_samples(packet, size, 48000);
            assert(count > 0 && count <= 960);
            assert(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK);
            allocations = injected = fail_at = 0;
            assert(yoradio_opus_decode_bounded(decoder, packet, size, output, count) == count);
            unsigned allocation_count = allocations;
            assert(allocation_count > 0);
            for (unsigned fault = 1; fault <= allocation_count; fault++) {
                assert(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK);
                allocations = injected = 0; fail_at = fault;
                int result = yoradio_opus_decode_bounded(decoder, packet, size, output, count);
                fail_at = 0;
                assert(injected == 1 && result == OPUS_ALLOC_FAIL);
                opus_scratch_mark mark = yoradio_opus_scratch_mark();
                assert(mark.bytes == 0 && mark.loan == 0);
                assert(!yoradio_opus_scratch_lend(scratch, sizeof(scratch)));
                /* No bind/init here: RESET must use the restored pointers. */
                assert(opus_decoder_ctl(decoder, OPUS_RESET_STATE) == OPUS_OK);
                result = yoradio_opus_decode_bounded(decoder, silk, silk_size, output, 960);
                assert(result == expected && !memcmp(reference, output, expected * sizeof(*output)));
                recoveries++;
                for (unsigned i = 0; i < 8; i++)
                    assert(storage[i] == 0x39 && storage[8 + state_size + i] == 0x39);
            }
            packets++;
        }
        assert(fclose(file) == 0);
    }
    assert(packets && recoveries > packets);
    printf("{\"passed\":true,\"packets\":%u,\"injected_ooms\":%u,\"reset_without_rebind_exact\":true,\"decoder_state_bytes\":%zu,\"loan_peak_bytes\":%zu}\n",
        packets, recoveries, state_size, yoradio_opus_scratch_peak_loan());
    free(storage);
    return 0;
}
