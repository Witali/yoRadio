#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Host-sized pointers model the allocator links, not its target binary ABI. */
#define MALLOC_CAP_8BIT 1U
#define MALLOC_CAP_32BIT 2U
#define HEAP_ALIGN_SIZE 8U
typedef struct mem_blk { uintptr_t used; struct mem_blk *next; } mem_blk_t;
#define MEM_HEAD_SIZE sizeof(mem_blk_t)
typedef struct {
    void *start_addr;
    size_t total_size, free_bytes;
    unsigned caps;
    mem_blk_t *free_blk;
} heap_region_t;
