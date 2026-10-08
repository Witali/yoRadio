#pragma once
#include <cstdint>
#include <cstdio>
#include <ctime>

// Host CPU time excludes time when this thread is descheduled. These numbers
// locate hot loops on the host; they are not ESP32-C3 cycle measurements.
namespace flac_profile {
enum Stage { frame, stereo, subframe, residual, prediction, count };
static const char* names[count] = {"frame_and_pcm", "stereo", "subframe",
                                   "residual", "prediction"};
static uint64_t elapsed[count] = {}, calls[count] = {};
static uint64_t clock_ns() {
    timespec t{};
    if (clock_gettime(CLOCK_THREAD_CPUTIME_ID, &t)) std::abort();
    return uint64_t(t.tv_sec) * 1000000000 + t.tv_nsec;
}
struct Scope;
static Scope* current = nullptr;
struct Scope {
    Stage stage;
    Scope* parent;
    uint64_t start, children = 0;
    explicit Scope(Stage id) : stage(id), parent(current), start(clock_ns()) {
        current = this;
    }
    ~Scope() {
        const uint64_t duration = clock_ns() - start;
        elapsed[stage] += duration - children;
        ++calls[stage];
        if (parent) parent->children += duration;
        current = parent;
    }
};
static void print() {
    for (unsigned i = 0; i < count; ++i)
        printf("STAGE %s %llu %llu\n", names[i],
               (unsigned long long)elapsed[i], (unsigned long long)calls[i]);
}
}
