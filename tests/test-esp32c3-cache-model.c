#include <assert.h>
#include <stdio.h>
#include "../tools/codec_benchmark/cache/cache_model.h"

int main(void) {
    cache_model_t lru = {0}, fifo = {.fifo = true};
    cache_stats_t a = {0}, b = {0};
    for (unsigned i = 0; i < 8; ++i) {
        cache_access(&lru, &a, i * 2048, 4, false);
        cache_access(&fifo, &b, i * 2048, 4, false);
    }
    assert(a.misses[0] == 8 && a.evictions == 0);
    cache_access(&lru, &a, 0, 4, true);
    cache_access(&fifo, &b, 0, 4, true);
    assert(a.misses[1] == 0); // Shared instruction/data cache.
    cache_access(&lru, &a, 8 * 2048, 4, false);
    cache_access(&fifo, &b, 8 * 2048, 4, false);
    cache_access(&lru, &a, 0, 4, false);
    cache_access(&fifo, &b, 0, 4, false);
    assert(a.misses[0] == 9 && b.misses[0] == 10); // LRU vs FIFO victim.
    assert(a.evictions == 1 && b.evictions == 2);
    cache_clear(&lru);
    memset(&a, 0, sizeof(a));
    cache_access(&lru, &a, 30, 4, false);
    assert(a.accesses[0] == 2 && a.misses[0] == 2); // Fetch spans two lines.
    cache_access(&lru, &a, 31, 2, true);
    assert(a.accesses[1] == 2 && a.misses[1] == 0);
    cache_clear(&lru);
    cache_access(&lru, &a, 31, 2, true);
    assert(a.misses[1] == 2); // Cold-call reset.
    cache_clear(&fifo);
    assert(fifo.fifo);
    uint32_t mmu[128], physical;
    for (unsigned i = 0; i < 128; ++i) mmu[i] = 0x100;
    assert(!flash_offset(0x42010020, mmu, &physical));
    mmu[1] = 5;
    assert(flash_offset(0x42010020, mmu, &physical) && physical == 0x50020);
    assert(flash_offset(0x3c010020, mmu, &physical) && physical == 0x50020);
    assert(!flash_offset(0x3fc90000, mmu, &physical)); // SRAM.
    assert(!flash_offset(0x40000000, mmu, &physical)); // ROM.
    assert(!flash_offset(0x600c5000, mmu, &physical)); // MMIO.
    assert(!flash_offset(0x42800000, mmu, &physical)); // Outside mapping.
    puts("CACHE_MODEL_TEST_PASS");
}
