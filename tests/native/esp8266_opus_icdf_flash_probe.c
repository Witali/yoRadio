#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <link.h>
#include "config.h"
#include "entdec.h"
#include "opus_memory.h"

static unsigned char *mock_flash;
static size_t page_size;
static uintptr_t active_begin, active_end;
static unsigned long flash_calls, dram_calls, word_loads;
#ifndef OPUS_ICDF_UNIT
static unsigned long transferred;
#endif
static struct { uintptr_t begin, end; } readonly_ranges[32];
static unsigned readonly_count;

static int find_readonly(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size; (void)data;
    /* Only the main executable's constant codec tables, never stack/heap CDFs. */
    if (info->dlpi_name && info->dlpi_name[0]) return 0;
    for (unsigned i = 0; i < info->dlpi_phnum; i++) {
        const ElfW(Phdr) *p = &info->dlpi_phdr[i];
        if (p->p_type != PT_LOAD || !(p->p_flags & PF_R) || (p->p_flags & PF_W)) continue;
        assert(readonly_count < 32);
        readonly_ranges[readonly_count].begin = info->dlpi_addr + p->p_vaddr;
        readonly_ranges[readonly_count++].end = info->dlpi_addr + p->p_vaddr + p->p_memsz;
    }
    return 0;
}
static void initialize(void) {
    if (mock_flash) return;
    page_size = (size_t)sysconf(_SC_PAGESIZE);
    assert(page_size && YORADIO_OPUS_FLASH_BEGIN % page_size == 0 && YORADIO_OPUS_FLASH_END % page_size == 0);
    const size_t span = YORADIO_OPUS_FLASH_END - YORADIO_OPUS_FLASH_BEGIN;
    void *wanted = (void *)(YORADIO_OPUS_FLASH_BEGIN - page_size);
    void *mapping = mmap(wanted, span + 2 * page_size, PROT_NONE,
        MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE, -1, 0);
    if (mapping != wanted) { perror("Required fixed mock-flash mapping unavailable; word coverage NOT executed"); exit(1); }
    mock_flash = (unsigned char *)YORADIO_OPUS_FLASH_BEGIN;
    assert(mprotect(mock_flash, span, PROT_READ | PROT_WRITE) == 0);
    memset(mock_flash, 0xa5, span);
    assert(mprotect(mock_flash, span, PROT_READ) == 0);
    dl_iterate_phdr(find_readonly, NULL);
    assert(readonly_count);
}
static void activate(const unsigned char *table, size_t length) {
    active_begin = (uintptr_t)table & ~(uintptr_t)3U;
    active_end = ((uintptr_t)table + length + 3U) & ~(uintptr_t)3U;
    assert(active_begin >= YORADIO_OPUS_FLASH_BEGIN && active_end <= YORADIO_OPUS_FLASH_END);
}
static unsigned char *place_table(const unsigned char *data, size_t length, size_t offset) {
    initialize();
    const size_t span = YORADIO_OPUS_FLASH_END - YORADIO_OPUS_FLASH_BEGIN;
    assert(offset <= span && length <= span - offset);
    assert(mprotect(mock_flash, span, PROT_READ | PROT_WRITE) == 0);
    memcpy(mock_flash + offset, data, length);
    assert(mprotect(mock_flash, span, PROT_READ) == 0);
    activate(mock_flash + offset, length);
    return mock_flash + offset;
}
void yoradio_opus_icdf_test_path(const unsigned char *cdf, int flash) {
    uintptr_t address = (uintptr_t)cdf;
    assert(flash == (address >= YORADIO_OPUS_FLASH_BEGIN && address < YORADIO_OPUS_FLASH_END));
    if (flash) { assert(active_begin && address >= active_begin && address < active_end); flash_calls++; }
    else dram_calls++;
}
void yoradio_opus_icdf_test_word(const void *word) {
    uintptr_t address = (uintptr_t)word;
    assert(address % 4 == 0 && active_begin && address >= active_begin && address <= active_end - 4);
    assert(address >= YORADIO_OPUS_FLASH_BEGIN && address <= YORADIO_OPUS_FLASH_END - 4);
    word_loads++;
}

#ifndef OPUS_ICDF_UNIT
extern int __real_ec_dec_icdf(ec_dec *, const unsigned char *, unsigned);
int __wrap_ec_dec_icdf(ec_dec *decoder, const unsigned char *cdf, unsigned bits) {
    initialize();
    uintptr_t address = (uintptr_t)cdf, segment_end = 0;
    for (unsigned i = 0; i < readonly_count; i++)
        if (address >= readonly_ranges[i].begin && address < readonly_ranges[i].end) segment_end = readonly_ranges[i].end;
    if (!segment_end) {
        /* In particular, silk_decode_signs' exact two-byte local table. */
        unsigned long before = word_loads;
        int result = __real_ec_dec_icdf(decoder, cdf, bits);
        assert(word_loads == before);
        return result;
    }
    size_t length = 0;
    do { assert(length < 256 && address + length < segment_end); } while (cdf[length++] != 0);
    size_t offset = transferred & 3U;
    offset = (transferred & 4U) ? (size_t)(YORADIO_OPUS_FLASH_END - YORADIO_OPUS_FLASH_BEGIN) - length : 16 + offset;
    const unsigned char *copy = place_table(cdf, length, offset);
    unsigned long before = word_loads;
    int result = __real_ec_dec_icdf(decoder, copy, bits);
    assert(word_loads > before);
    transferred++;
    active_begin = active_end = 0;
    return result;
}
__attribute__((destructor)) static void report(void) {
    printf("{\"icdf_flash_calls\":%lu,\"icdf_dram_calls\":%lu,\"icdf_word_loads\":%lu,\"readonly_tables_transferred\":%lu}\n",
        flash_calls, dram_calls, word_loads, transferred);
}
#else
extern int legacy_ec_dec_icdf(ec_dec *, const unsigned char *, unsigned);
static void compare_sequence(const unsigned char *reference, const unsigned char *actual, unsigned bits, unsigned seed) {
    unsigned char packet[64];
    for (unsigned i = 0; i < sizeof(packet); i++) { seed = seed * 1664525U + 1013904223U; packet[i] = seed >> 24; }
    ec_dec a = {0}, b = {0};
    ec_dec_init(&a, packet, sizeof(packet));
    b = a;
    for (unsigned i = 0; i < 512; i++) {
        assert(legacy_ec_dec_icdf(&a, reference, bits) == ec_dec_icdf(&b, actual, bits));
        assert(memcmp(&a, &b, sizeof(a)) == 0);
        assert(ec_tell(&a) == ec_tell(&b) && ec_tell_frac(&a) == ec_tell_frac(&b));
    }
}
int main(void) {
    initialize();
    unsigned sequences = 0;
    for (unsigned bits = 1; bits <= 8; bits++) {
        unsigned char cdf[17];
        unsigned length = (1U << bits) < 17 ? 1U << bits : 17;
        for (unsigned i = 0; i < length; i++) cdf[i] = ((1U << bits) * (length - i - 1)) / length;
        for (unsigned offset = 0; offset < 4; offset++) {
            const unsigned char *copy = place_table(cdf, length, 16 + offset);
            for (unsigned seed = 0; seed < 8; seed++) { compare_sequence(cdf, copy, bits, seed); sequences++; }
        }
        const unsigned char *last = place_table(cdf, length, YORADIO_OPUS_FLASH_END - YORADIO_OPUS_FLASH_BEGIN - length);
        compare_sequence(cdf, last, bits, 23); sequences++;
    }
    /* A final two-byte flash CDF must never prefetch beyond the mapping. */
    const unsigned char two[2] = {128, 0};
    const unsigned char *last = place_table(two, 2, YORADIO_OPUS_FLASH_END - YORADIO_OPUS_FLASH_BEGIN - 2);
    compare_sequence(two, last, 8, 63); sequences++;
    active_begin = active_end = 0;
    unsigned long before = word_loads;
    /* DRAM at a guard page and an exact malloc(2) allocation. The latter is
     * checked with AddressSanitizer too, catching a read before the table. */
    unsigned char *guarded = mmap(NULL, 2 * page_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    assert(guarded != MAP_FAILED && mprotect(guarded + page_size, page_size, PROT_NONE) == 0);
    unsigned char *local = guarded + page_size - 2;
    memcpy(local, two, 2);
    compare_sequence(two, local, 8, 1); sequences++;
    unsigned char *tiny = malloc(2); assert(tiny); memcpy(tiny, two, 2);
    compare_sequence(two, tiny, 8, 2); sequences++;
    free(tiny);
    assert(munmap(guarded, 2 * page_size) == 0);
    /* Valid RAM immediately outside each flash boundary is not flash. */
    unsigned char *left = (unsigned char *)(YORADIO_OPUS_FLASH_BEGIN - page_size);
    unsigned char *right = (unsigned char *)YORADIO_OPUS_FLASH_END;
    assert(mprotect(left, page_size, PROT_READ | PROT_WRITE) == 0);
    assert(mprotect(right, page_size, PROT_READ | PROT_WRITE) == 0);
    memcpy(left + page_size - 2, two, 2); memcpy(right, two, 2);
    compare_sequence(two, left + page_size - 2, 8, 3); sequences++;
    compare_sequence(two, right, 8, 4); sequences++;
    assert(mprotect(left, page_size, PROT_NONE) == 0 && mprotect(right, page_size, PROT_NONE) == 0);
    assert(word_loads == before && flash_calls > 0 && dram_calls == 2048);
    printf("{\"passed\":true,\"sequences\":%u,\"symbols\":%u,\"icdf_flash_calls\":%lu,\"icdf_dram_calls\":%lu,\"icdf_word_loads\":%lu}\n",
        sequences, sequences * 512, flash_calls, dram_calls, word_loads);
    return 0;
}
#endif
