#pragma once
#include <stddef.h>
/* Pinned MEM_LIBC_MALLOC branch; size_t follows the host ABI here. */
typedef size_t mem_size_t;
#define MEM_ALIGNMENT 4
#define LWIP_MEM_ALIGN_SIZE(size) (((size) + MEM_ALIGNMENT - 1U) & ~(MEM_ALIGNMENT - 1U))
