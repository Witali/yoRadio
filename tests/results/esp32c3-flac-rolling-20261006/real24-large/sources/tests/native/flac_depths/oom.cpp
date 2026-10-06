#include "custom_flac_adapter.h"
#include "flac_decoder.h"
#include <cassert>
#include <cstdio>
#include <vector>

// Linker wrapping affects the real core/adapter C allocations, including
// realloc preserving its old block on failure. C++/ASan runtime allocations
// outside those calls are not counted or claimed to be covered.
extern "C" void *__real_malloc(size_t);
extern "C" void *__real_realloc(void *,size_t);
extern "C" void __real_free(void *);
struct Allocation {void *pointer;size_t bytes;};
static Allocation live[128];
static bool active;
static size_t calls,fail_after=SIZE_MAX,live_bytes,peak;
unsigned flac_test_errors;
static void remove(void *pointer) {
    if(!pointer)return;
    for(auto &entry:live)if(entry.pointer==pointer){live_bytes-=entry.bytes;entry={};return;}
}
static void add(void *pointer,size_t bytes) {
    if(!pointer)return;
    for(auto &entry:live)if(!entry.pointer){entry={pointer,bytes};live_bytes+=bytes;peak=std::max(peak,live_bytes);return;}
    assert(false);
}
extern "C" void *__wrap_malloc(size_t bytes) {
    if(active && calls++>=fail_after)return nullptr;
    void *pointer=__real_malloc(bytes);if(active)add(pointer,bytes);return pointer;
}
extern "C" void *__wrap_realloc(void *old,size_t bytes) {
    if(active && calls++>=fail_after)return nullptr;
    void *pointer=__real_realloc(old,bytes);
    if(pointer){remove(old);if(active)add(pointer,bytes);}
    return pointer;
}
extern "C" void __wrap_free(void *pointer) {remove(pointer);__real_free(pointer);}
struct Output {uint64_t hash=14695981039346656037ULL;size_t bytes=0;};
static bool pcm(void *user,const custom_flac_info_t *info,const uint8_t *data,size_t bytes) {
    auto &out=*static_cast<Output *>(user);assert(info->pcm_bits_per_sample==16);
    for(size_t i=0;i<bytes;++i)out.hash=(out.hash^data[i])*1099511628211ULL;
    out.bytes+=bytes;return true;
}
static bool decode(const std::vector<uint8_t> &data,Output &out,size_t limit) {
    assert(!live_bytes && !FLACDecoder_GetAllocatedBytes());
    calls=peak=flac_test_errors=0;fail_after=limit;active=true;
    auto *decoder=custom_flac_decoder_create();bool success=decoder!=nullptr;
    if(decoder) {
        for(size_t offset=0;offset<data.size();) {
            size_t bytes=std::min<size_t>(127,data.size()-offset);custom_flac_feed_stats_t stats={};
            if(custom_flac_decoder_feed(decoder,data.data()+offset,bytes,offset+bytes==data.size(),pcm,&out,&stats)<0){success=false;break;}
            offset+=bytes;
        }
        custom_flac_decoder_destroy(decoder);
    }
    active=false;
    assert(!live_bytes && !FLACDecoder_GetAllocatedBytes());
    for(const auto &entry:live)assert(!entry.pointer);
    return success;
}
int main(int argc,char **argv) {
    assert(argc==2);FILE *file=fopen(argv[1],"rb");assert(file);
    fseek(file,0,SEEK_END);size_t size=ftell(file);rewind(file);
    std::vector<uint8_t> data(size);assert(fread(data.data(),1,size,file)==size);fclose(file);
    Output baseline;assert(decode(data,baseline,SIZE_MAX) && !flac_test_errors && baseline.bytes);
    const size_t allocations=calls,peak_bytes=peak;
    for(size_t limit=0;limit<allocations;++limit) {
        Output failed;assert(!decode(data,failed,limit));
        Output recovered;assert(decode(data,recovered,SIZE_MAX) && !flac_test_errors);
        assert(recovered.bytes==baseline.bytes && recovered.hash==baseline.hash);
    }
    printf("PASS persistent_oom_cases=%zu recovery_cases=%zu tracked_peak_bytes=%zu pcm_bytes=%zu\n",
        allocations,allocations,peak_bytes,baseline.bytes);
}
