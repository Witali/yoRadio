// Desktop-only bit-exact RCPDM research. No device access or firmware changes.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
#include "rcpdm_variants.h"
#include "rcpdm_runs.h"

#ifdef _MSC_VER
#define NOINLINE __declspec(noinline)
#else
#define NOINLINE __attribute__((noinline))
#endif
template<int V, bool Count = false>
static inline uint32_t sample(rc_pdm_t *state, int16_t pcm, RcRunStats *stats) {
    if constexpr (V == 0) return rc_pdm_sample(state, pcm);
    if constexpr (V == 1) return rc_candidate_original(state, pcm);
    if constexpr (V == 2) return rc_run_sample<2,true,false,Count>(state,pcm,stats);
    if constexpr (V == 3) return rc_run_sample<4,true,false,Count>(state,pcm,stats);
    if constexpr (V == 4) return rc_run_sample<8,true,false,Count>(state,pcm,stats);
    if constexpr (V == 5) return rc_run_sample<2,false,false,Count>(state,pcm,stats);
    if constexpr (V == 6) return rc_run_sample<4,false,false,Count>(state,pcm,stats);
    if constexpr (V == 7) return rc_run_sample<8,false,false,Count>(state,pcm,stats);
    if constexpr (V == 8) return rc_run_sample<4,true,true,Count>(state,pcm,stats);
    if constexpr (V == 9) return rc_run_sample<4,false,true,Count>(state,pcm,stats);
    if constexpr (V == 10) return rc_run_entry_split<4,true,Count>(state,pcm,stats);
    if constexpr (V == 11) return rc_run_entry_split<2,false,Count>(state,pcm,stats);
    if constexpr (V == 12) return rc_run_entry_split<4,false,Count>(state,pcm,stats);
    if constexpr (V == 13) return rc_run_entry_split<8,false,Count>(state,pcm,stats);
}
template<int V>
static NOINLINE uint32_t pack(const int16_t *pcm, uint32_t *out, size_t n) {
    rc_pdm_t state; rc_pdm_init(&state);
    for (size_t i = 0; i < n; ++i) out[i] = sample<V>(&state,pcm[i],nullptr);
    return state.rc;
}
using Pack = uint32_t (*)(const int16_t *,uint32_t *,size_t);
using Scalar = uint32_t (*)(rc_pdm_t *,int16_t,RcRunStats *);
struct Variant { const char *name; unsigned group; Pack pack; Scalar stats; };
static const Variant variants[] = {
    {"production",0,pack<0>,sample<0,true>}, {"original",0,pack<1>,sample<1,true>},
    {"fixed2",2,pack<2>,sample<2,true>}, {"fixed4",4,pack<3>,sample<3,true>},
    {"fixed8",8,pack<4>,sample<4,true>}, {"state2",2,pack<5>,sample<5,true>},
    {"state4",4,pack<6>,sample<6,true>}, {"state8",8,pack<7>,sample<7,true>},
    {"entry-fixed4",4,pack<8>,sample<8,true>}, {"entry-state4",4,pack<9>,sample<9,true>},
    {"split-fixed4",4,pack<10>,sample<10,true>}, {"split-state2",2,pack<11>,sample<11,true>},
    {"split-state4",4,pack<12>,sample<12,true>}, {"split-state8",8,pack<13>,sample<13,true>}
};
constexpr size_t NV = sizeof(variants)/sizeof(variants[0]);
static volatile uint32_t observed;

static void require(bool condition, const char *message) {
    if (!condition) throw std::runtime_error(message);
}
static uint32_t check_one(uint32_t initial, int16_t pcm, uint64_t &checked) {
    rc_pdm_t ref{initial}; const uint32_t expected = rc_candidate_original(&ref,pcm);
    for (const auto &v : variants) {
        rc_pdm_t actual{initial}; RcRunStats stats;
        require(v.stats(&actual,pcm,&stats) == expected && actual.rc == ref.rc, "self-test word/state mismatch");
        ++checked;
    }
    return ref.rc;
}
static void self_test() {
    uint64_t checked = 0;
    for (uint32_t initial : {0U,1U,15U,0x80000000U,UINT32_MAX-15U,UINT32_MAX})
        for (int pcm = -32768; pcm <= 32767; ++pcm) check_one(initial,(int16_t)pcm,checked);
    uint32_t state = 0x80000000U, random = 1;
    for (unsigned i = 0; i < 100000; ++i) {
        random = random * 1664525U + 1013904223U;
        const int16_t pcm = (int16_t)(random & 65535U);
        state = check_one(state,pcm,checked);
        check_one(random ^ (random >> 13),pcm,checked);
    }
    // Check uninstrumented bulk code too, across non-aligned buffer lengths.
    std::vector<int16_t> pcm(8193); std::vector<uint32_t> ref(pcm.size()),actual(pcm.size());
    for (auto &s : pcm) { random = random * 1664525U + 1013904223U; s = (int16_t)random; }
    const uint32_t last = pack<1>(pcm.data(),ref.data(),pcm.size());
    for (const auto &v : variants) {
        require(v.pack(pcm.data(),actual.data(),pcm.size()) == last && ref == actual,"bulk self-test mismatch");
    }
    std::cout << "{\"wordStateComparisons\":" << checked << ",\"bulkWordsPerVariant\":8193,\"variants\":" << NV << ",\"pass\":true}\n";
}
static int16_t scale(int16_t s, uint32_t gain) {
    const int32_t product = (int32_t)s * (int32_t)gain;
    return (int16_t)(product >= 0 ? (product+16384)>>15 : -((-product+16384)>>15));
}
static std::vector<int16_t> prepare(const char *file, unsigned rate, unsigned channels, unsigned volume) {
    std::ifstream input(file,std::ios::binary | std::ios::ate);
    require((bool)input,"cannot open PCM file");
    const auto bytes = input.tellg();
    require(bytes > 0 && (uint64_t)bytes % (channels*2) == 0,"invalid PCM size");
    input.seekg(0);
    std::vector<int16_t> raw((size_t)bytes/2);
    require((bool)input.read((char*)raw.data(),bytes),"cannot read PCM");
    // Native signed Q15 volume, C stereo division (toward zero), then the
    // firmware's zero-order hold phase accumulator. NOT FFmpeg resampling.
    const uint32_t gain = (volume * 16U * 32768U + 254U*16U/2) / (254U*16U);
    std::vector<int16_t> mono; mono.reserve(raw.size()*48000/(channels*rate)+1);
    uint32_t phase = 0;
    for (size_t i = 0; i < raw.size(); i += channels) {
        int32_t s = scale(raw[i],gain);
        if (channels == 2) s = (s + scale(raw[i+1],gain))/2;
        phase += 48000;
        while (phase >= rate) { mono.push_back((int16_t)s); phase -= rate; }
    }
    return mono;
}
template<class T> static void save(const std::string &file,const std::vector<T> &data) {
    std::ofstream out(file,std::ios::binary);
    require((bool)out.write((const char*)data.data(),(std::streamsize)(data.size()*sizeof(T))),"cannot save output");
}
static int run(int argc, char **argv) {
    const uint16_t endian = 1;
    require(*(const unsigned char*)&endian == 1,"PCM/output files require a little-endian host");
    if (argc == 2 && std::string(argv[1]) == "--self-test") { self_test(); return 0; }
    require(argc == 7 || argc == 8,"usage: benchmark PCM rate channels volume repeats output-prefix [--save]");
    const unsigned rate = (unsigned)std::stoul(argv[2]), channels = (unsigned)std::stoul(argv[3]);
    const unsigned volume = (unsigned)std::stoul(argv[4]), repeats = (unsigned)std::stoul(argv[5]);
    require(rate >= 8000 && rate <= 192000 && (channels == 1 || channels == 2) && volume <= 254 && repeats >= 3,"invalid arguments");
    const auto pcm = prepare(argv[1],rate,channels,volume);
    require(!pcm.empty(),"empty PCM");
    std::vector<uint32_t> ref(pcm.size()), actual(pcm.size()), states(pcm.size());
    rc_pdm_t state; rc_pdm_init(&state);
    double energy = 0; int peak = 0;
    uint64_t run_hist[33] = {}; // Per-word maximal constant runs; split at word boundaries.
    for (size_t i = 0; i < pcm.size(); ++i) {
        ref[i] = rc_candidate_original(&state,pcm[i]); states[i] = state.rc;
        energy += (double)pcm[i]*pcm[i]; peak = std::max(peak,std::abs((int)pcm[i]));
        unsigned length = 1, prev = ref[i] >> 31;
        for (int b = 30; b >= 0; --b) {
            const unsigned next = (ref[i] >> b)&1U;
            if (next == prev) ++length; else { ++run_hist[length]; length = 1; prev = next; }
        }
        ++run_hist[length];
    }
    RcRunStats counters[NV];
    // Word AND state after every sample, not just final checksum.
    for (size_t v = 0; v < NV; ++v) {
        rc_pdm_init(&state);
        for (size_t i = 0; i < pcm.size(); ++i)
            require(variants[v].stats(&state,pcm[i],&counters[v]) == ref[i] && state.rc == states[i],"real PCM word/state mismatch");
        require(variants[v].pack(pcm.data(),actual.data(),pcm.size()) == states.back() && actual == ref,"uninstrumented word mismatch");
    }
    // Allocation, decode, resampling, I/O and counters are excluded from timing.
    // Rotate order every round to limit temperature/scheduler/order bias.
    std::vector<double> durations[NV];
    for (unsigned round = 0; round < repeats; ++round) {
        for (size_t j = 0; j < NV; ++j) {
            const size_t v = (j+round)%NV;
            const auto begin = std::chrono::steady_clock::now();
            const uint32_t final = variants[v].pack(pcm.data(),actual.data(),pcm.size());
            const auto end = std::chrono::steady_clock::now();
            observed = final ^ actual[(round*7919U)%actual.size()];
            durations[v].push_back(std::chrono::duration<double,std::micro>(end-begin).count());
        }
    }
    if (argc == 8) {
        require(std::string(argv[7]) == "--save","unknown switch");
        save(std::string(argv[6])+".mono48.s16le",pcm);
        save(std::string(argv[6])+".original.rcpdm32le",ref);
        pack<6>(pcm.data(),actual.data(),pcm.size()); // State-aware group-4 candidate.
        save(std::string(argv[6])+".state4.rcpdm32le",actual);
    }
    std::cout << std::fixed << std::setprecision(6)
        << "{\"samples\":" << pcm.size() << ",\"outputRate\":48000,\"volume\":" << volume
        << ",\"peak\":" << peak << ",\"rms\":" << std::sqrt(energy/pcm.size())
        << ",\"wordMismatches\":0,\"stateMismatches\":0,\"bitMismatches\":0,\"differenceRms\":0"
        << ",\"differenceSnrDb\":\"infinity (identical)\",\"runHistogram\":[";
    for (unsigned i = 0; i <= 32; ++i) std::cout << (i ? "," : "") << run_hist[i];
    std::cout << "],\"variants\":[";
    for (size_t v = 0; v < NV; ++v) {
        auto sorted = durations[v]; std::sort(sorted.begin(),sorted.end());
        const auto &s = counters[v];
        std::cout << (v ? "," : "") << "{\"name\":\"" << variants[v].name << "\",\"groupSize\":" << variants[v].group
            << ",\"medianUs\":" << sorted[sorted.size()/2] << ",\"minUs\":" << sorted.front() << ",\"maxUs\":" << sorted.back()
            << ",\"checks\":" << s.checks << ",\"groups\":" << s.groups << ",\"highGroups\":" << s.high_groups
            << ",\"wordsWithGroup\":" << s.words_with_group
            << ",\"coveredBitsPercent\":" << (100.0*s.groups*variants[v].group/(32.0*pcm.size())) << ",\"roundUs\":[";
        for (size_t i = 0; i < durations[v].size(); ++i) std::cout << (i ? "," : "") << durations[v][i];
        std::cout << "]}";
    }
    std::cout << "]}\n";
    return 0;
}
int main(int argc,char **argv) {
    try { return run(argc,argv); }
    catch (const std::exception &error) { std::cerr << error.what() << '\n'; return 1; }
}
