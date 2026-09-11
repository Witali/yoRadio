#pragma once
#include "esp_heap_caps.h"
#define mem_blk_next(b) ((b)->next)
#define mem_blk_is_used(b) ((b)->used)
#define blk_link_size(b) ((uintptr_t)(b)->next - (uintptr_t)(b))
