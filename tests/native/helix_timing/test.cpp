#include <cassert>
#include <cstdio>
#include "opus_benchmark.h"
#include "codec_bridge.h"
extern "C" {
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
}
struct helix_codec {int kind;uint32_t input[512];};
static helix_codec decoder;
static unsigned active,creates,destroys,calls,critical;
static uint32_t wall,cpu;
static bool fail_alloc,fail_decode,cancel;
extern "C" void test_enter_critical(){++critical;}
extern "C" void test_exit_critical(){assert(critical);--critical;}
extern "C" void vTaskGetInfo(TaskHandle_t,TaskStatus_t *s,int,eTaskState){s->ulRunTimeCounter=cpu;}
extern "C" void vTaskDelay(unsigned){wall+=1000;}
extern "C" UBaseType_t uxTaskGetStackHighWaterMark(TaskHandle_t){return 2048;}
extern "C" int64_t esp_timer_get_time(){return wall;}
extern "C" size_t heap_caps_get_free_size(unsigned){return 25000-active*10000;}
extern "C" helix_codec_t *helix_codec_create(helix_codec_kind_t k,size_t){
    if(fail_alloc)return nullptr;
    assert(!active);active=1;++creates;decoder.kind=k;return &decoder;
}
extern "C" void helix_codec_destroy(helix_codec_t *p){assert(p==&decoder&&active);active=0;++destroys;}
extern "C" uint8_t *helix_codec_write_pointer(helix_codec_t *,size_t *n){*n=sizeof(decoder.input);return (uint8_t*)decoder.input;}
extern "C" int helix_codec_buffer_commit(helix_codec_t *,size_t n){return n==4?0:-1;}
extern "C" size_t helix_codec_dram_used(const helix_codec_t *){return 9000;}
extern "C" size_t helix_codec_iram_used(const helix_codec_t *){return 16384;}
extern "C" int helix_codec_process_one(helix_codec_t *,helix_pcm_callback_t callback,void *context){
    assert(!critical);++calls;cpu+=5000;wall+=5050;if(fail_decode)return -77;
    helix_stream_info_t info={};info.channels=1;info.sample_rate=48000;int16_t pcm[32];
    for(unsigned n=0;n<32;++n)pcm[n]=(int16_t)n;
    unsigned count=decoder.kind==1?36:32;
    for(unsigned n=0;n<count;++n)if(!callback(context,&info,pcm,32))return -78;
    return 0;
}
static bool current(uint32_t n){assert(n==42);return !cancel||calls==0;}
static opus_benchmark_status_t run(){assert(opus_benchmark_request());assert(!opus_benchmark_request());
    opus_benchmark_run_pending(42,current);opus_benchmark_status_t s;opus_benchmark_snapshot(&s);
    assert(!active&&creates==destroys&&!critical);return s;}
int main(){
    auto s=run();assert(s.state==3&&s.rounds==10&&s.cases==2&&s.dram_before==s.dram_after);
    for(unsigned n=0;n<2;++n){opus_benchmark_case_t r;opus_benchmark_case_snapshot(n,&r);
        assert(r.packets==20&&r.task_us==100000&&r.wall_us==101000&&r.max_wall_us==5050&&r.pcm_hash);
        assert(r.samples==20U*(n?1024:1152));}
    assert(run().state==3);
    fail_alloc=true;assert(run().error==-9001);fail_alloc=false;
    fail_decode=true;assert(run().error==-77);fail_decode=false;
    cancel=true;calls=0;assert(run().error==-9002);cancel=false;
    assert(run().state==3);
    assert(opus_benchmark_request());opus_benchmark_cancel_pending();opus_benchmark_snapshot(&s);assert(s.error==-9002);
    std::puts("Helix timing lifecycle and timing boundaries PASS");
}
