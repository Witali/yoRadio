#include "vorbis_xiph_alloc.h"
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { void *pointer; size_t bytes; } allocation_t;
static allocation_t allocations[4096];
static size_t attempts, realloc_attempts, fail_at, failures, live, live_bytes;
static int zero_null;

void xiph_port_test_reset(size_t ordinal) {
    attempts = realloc_attempts = failures = 0;
    fail_at = ordinal; zero_null = 0;
}
void xiph_port_test_zero_null(int enabled) { zero_null = !!enabled; }
size_t xiph_port_test_attempts(void) { return attempts; }
size_t xiph_port_test_realloc_attempts(void) { return realloc_attempts; }
size_t xiph_port_test_live(void) { return live; }
size_t xiph_port_test_bytes(void) { return live_bytes; }
size_t xiph_port_test_failures(void) { return failures; }
static int refused(void) {
    attempts++;
    if (fail_at && attempts == fail_at) { failures++; return 1; }
    return 0;
}
static size_t find(void *pointer) {
    for (size_t i = 0; i < sizeof(allocations)/sizeof(allocations[0]); i++) {
        if (allocations[i].pointer == pointer) { return i; }
    }
    assert(!"Unknown or already freed allocation"); return 0;
}
static void record(void *pointer, size_t bytes) {
    if (!pointer) { return; }
    for (size_t i = 0; i < sizeof(allocations)/sizeof(allocations[0]); i++) {
        if (!allocations[i].pointer) {
            allocations[i].pointer = pointer; allocations[i].bytes = bytes;
            live++; live_bytes += bytes; return;
        }
    }
    assert(!"Test allocation ledger exhausted");
}
void *xiph_port_test_malloc(size_t bytes) {
    if (refused() || (zero_null && !bytes)) { return NULL; }
    void *pointer = malloc(bytes); record(pointer, bytes); return pointer;
}
void *xiph_port_test_calloc(size_t count, size_t bytes) {
    if (refused() || (zero_null && (!count || !bytes))) { return NULL; }
    if (bytes && count > SIZE_MAX/bytes) { failures++; return NULL; }
    void *pointer = calloc(count, bytes); record(pointer, count*bytes); return pointer;
}
void *xiph_port_test_realloc(void *pointer, size_t bytes) {
    realloc_attempts++;
    if (refused()) { return NULL; }
    if (!pointer) {
        if (zero_null && !bytes) { return NULL; }
        void *result = malloc(bytes); record(result, bytes); return result;
    }
    size_t index = find(pointer), old_bytes = allocations[index].bytes;
    if (!bytes) {
        free(pointer); memset(&allocations[index], 0, sizeof(allocations[index]));
        live--; live_bytes -= old_bytes; return NULL;
    }
    void *result = realloc(pointer, bytes);
    if (result) {
        allocations[index].pointer = result; allocations[index].bytes = bytes;
        live_bytes = live_bytes - old_bytes + bytes;
    }
    return result;
}
void xiph_port_test_free(void *pointer) {
    if (!pointer) { return; }
    size_t index = find(pointer);
    live_bytes -= allocations[index].bytes; live--;
    memset(&allocations[index], 0, sizeof(allocations[index])); free(pointer);
}
