#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "esp_heap_caps.h"
#include "native_heap_diag.h"
static _Alignas(8) unsigned char region_bytes[256];
heap_region_t g_heap_region[2];
size_t g_heap_region_num;
static unsigned locks, unlocks, depth;
void test_heap_lock(void) { assert(!depth); ++depth; ++locks; }
void test_heap_unlock(void) { assert(depth==1); --depth; ++unlocks; }
static mem_blk_t *at(size_t offset) { return (mem_blk_t *)(region_bytes+offset); }
static void reset(void) {
    memset(region_bytes,0,sizeof(region_bytes));
    g_heap_region_num=2;
    g_heap_region[0]=(heap_region_t){region_bytes,sizeof(region_bytes),160,MALLOC_CAP_8BIT,at(0)};
    /* An invalid IRAM link must never be visited as a byte-addressable region. */
    g_heap_region[1]=(heap_region_t){NULL,0,9999,MALLOC_CAP_32BIT,(mem_blk_t *)1};
    at(0)->next=at(64); at(64)->next=at(128); at(64)->used=1;
    at(128)->next=at(240); at(240)->next=NULL;
}
static void check(uint32_t free_bytes,uint32_t largest) {
    native_heap_diag_t result=native_heap_diag_snapshot();
    assert(!depth && locks==unlocks);
    assert(result.free_dram==free_bytes && result.largest_dram==largest);
}
int main(void) {
    reset(); check(160,112-MEM_HEAD_SIZE);
    at(128)->used=1; check(160,64-MEM_HEAD_SIZE);
    at(0)->used=1; check(160,0);
    reset(); g_heap_region[0].free_blk=at(128); check(160,112-MEM_HEAD_SIZE);
    reset(); g_heap_region[0].free_blk=NULL; check(160,0);
    reset(); g_heap_region[1]=g_heap_region[0]; check(320,112-MEM_HEAD_SIZE);
    reset(); at(128)->next=at(64); check(160,UINT32_MAX);
    reset(); at(128)->next=at(128); check(160,UINT32_MAX);
    reset(); at(128)->next=at(136); check(160,UINT32_MAX); /* overlaps header */
    reset(); at(128)->next=(mem_blk_t *)(region_bytes+129); check(160,UINT32_MAX);
    reset(); at(128)->next=(mem_blk_t *)(region_bytes+sizeof(region_bytes)); check(160,UINT32_MAX);
    reset(); g_heap_region[0].free_blk=(mem_blk_t *)(region_bytes+1); check(160,UINT32_MAX);
    reset(); g_heap_region[0].free_blk=(mem_blk_t *)((uintptr_t)region_bytes-8); check(160,UINT32_MAX);
    reset(); g_heap_region[0].total_size=MEM_HEAD_SIZE-1; check(160,UINT32_MAX);
    reset(); g_heap_region[0].start_addr=(void *)(UINTPTR_MAX-7); check(160,UINT32_MAX);
    puts("Heap diagnostic PASS: fragmentation, CAP8, bounds, sentinel and balanced lock");
}
