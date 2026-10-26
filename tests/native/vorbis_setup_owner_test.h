// Portable exact setup-owner lifecycle controls; no audio or DSP path.
#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef NDEBUG
#error "Setup-owner tests require active assertions"
#endif

typedef struct {
    uint64_t checks, successful_opens, parse_failures, allocation_refusals, cases;
} owner_test_totals_t;

size_t owner_test_case_count(void);
void owner_test_run_case(size_t index, bool prefix_sweeps);
owner_test_totals_t owner_test_totals(void);

// The host supplies a no-op; a native harness can yield between prefix batches.
void owner_test_poll(void);
