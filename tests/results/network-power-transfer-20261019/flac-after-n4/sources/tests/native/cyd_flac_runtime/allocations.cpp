#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <new>
#include "flac_decoder.h"

// Track only direct production C allocations and the adapter's nothrow object.
// RTOS queue/state setup is performed before tracking. This is a host failure
// seam, not an ESP heap capacity/fragmentation measurement.
struct Allocation { void *pointer; size_t size; };
static Allocation live[128];
static bool active;
static size_t calls, limit = SIZE_MAX, live_bytes, peak_bytes;
unsigned flac_test_errors;
extern "C" void *__real_malloc(size_t);
extern "C" void *__real_realloc(void *, size_t);
extern "C" void __real_free(void *);
extern "C" void *__real__ZnwmRKSt9nothrow_t(size_t, const std::nothrow_t &) noexcept;
extern "C" void __real__ZdlPv(void *) noexcept;
extern "C" void __real__ZdlPvm(void *, size_t) noexcept;
static void remove(void *p) {
    if (!p) return;
    for (auto &entry : live) if (entry.pointer == p) {
        live_bytes -= entry.size; entry = {}; return;
    }
}
static void add(void *p, size_t size) {
    if (!p || !active) return;
    for (auto &entry : live) if (!entry.pointer) {
        entry = {p, size}; live_bytes += size;
        peak_bytes = std::max(peak_bytes, live_bytes); return;
    }
    assert(false);
}
static bool fail() { return active && calls++ >= limit; }
extern "C" void *__wrap_malloc(size_t size) {
    if (fail()) return nullptr;
    void *p = __real_malloc(size); add(p, size); return p;
}
extern "C" void *__wrap_realloc(void *old, size_t size) {
    if (fail()) return nullptr;
    void *p = __real_realloc(old, size);
    if (p) { remove(old); add(p, size); }
    return p;
}
extern "C" void __wrap_free(void *p) { remove(p); __real_free(p); }
extern "C" void *__wrap__ZnwmRKSt9nothrow_t(size_t size, const std::nothrow_t &tag) noexcept {
    if (fail()) return nullptr;
    void *p = __real__ZnwmRKSt9nothrow_t(size, tag); add(p, size); return p;
}
extern "C" void __wrap__ZdlPv(void *p) noexcept { remove(p); __real__ZdlPv(p); }
extern "C" void __wrap__ZdlPvm(void *p, size_t size) noexcept { remove(p); __real__ZdlPvm(p, size); }
extern "C" void flac_test_begin(size_t fail_after) {
    assert(!active && !live_bytes && !FLACDecoder_GetAllocatedBytes());
    calls = peak_bytes = flac_test_errors = 0; limit = fail_after; active = true;
}
extern "C" size_t flac_test_calls(void) { return calls; }
extern "C" size_t flac_test_live(void) { return live_bytes; }
extern "C" size_t flac_test_workspace(void) { return FLACDecoder_GetAllocatedBytes(); }
extern "C" void flac_test_finish(void) {
    assert(active && !live_bytes && !FLACDecoder_GetAllocatedBytes());
    for (const auto &entry : live) assert(!entry.pointer);
    active = false;
}
