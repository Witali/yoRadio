#pragma once
#include <stdint.h>

// Numerical qualification only. The pinned binary still allocates int32 arrays.
// 1/2/3: nearest SBR/PS/both; 4/5/6: midpoint SBR/PS/both;
// 7: lossless traversal of both histories; 0: wrapper bypass.
void packed_history_reset(unsigned run);
void packed_history_select(unsigned variant);
void packed_history_report(const char *name, unsigned variant, unsigned run,
                           uint32_t *rows, uint32_t *changed, unsigned *shift);
void packed_history_arithmetic_tests(void);
