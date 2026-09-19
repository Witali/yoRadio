/* Diagnostic alternative behind the existing benchmark HTTP/owner-task API.
 * No network input, output, normalization or flash copy in the timed window.
 * CPU counters exclude other tasks, but ISR time is charged by the SDK.
 * The tiny PCM callback is part of the real block decoder API; hashing occurs
 * only in the unscored warm-up round. Never disable interrupts over decode. */
#include "opus_benchmark.h"
#include "codec_bridge.h"
#include "helix_timing_fixtures.h"
#include <string.h>
extern "C" {
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
}
#if !configGENERATE_RUN_TIME_STATS || !configUSE_TRACE_FACILITY || !CONFIG_FREERTOS_RUN_TIME_STATS_USING_ESP_TIMER
#error "Helix timing requires microsecond task runtime counters"
#endif
namespace {
constexpr unsigned kRounds=10;
opus_benchmark_status_t status;
opus_benchmark_case_t results[HELIX_TIMING_CASES];
uint32_t cpu_time() { TaskStatus_t s; vTaskGetInfo(nullptr,&s,pdFALSE,eRunning);return s.ulRunTimeCounter; }
uint32_t clock_us() {
    taskENTER_CRITICAL();uint32_t t=(uint32_t)esp_timer_get_time();taskEXIT_CRITICAL();return t;
}
uint32_t free_dram() { return heap_caps_get_free_size(MALLOC_CAP_8BIT); }
void copy_words(void *to,const void *from,size_t bytes) {
    auto d=static_cast<uint32_t *>(to);auto s=static_cast<const volatile uint32_t *>(from);
    for(size_t i=0;i<(bytes+3)/4;++i)d[i]=s[i];
}
struct Sink {uint32_t samples, hash;bool validate;uint16_t nonzero;};
bool accept(void *context,const helix_stream_info_t *info,int16_t *pcm,size_t count) {
    auto s=static_cast<Sink *>(context);
    if(!info||!pcm||!count||info->channels!=1||info->sample_rate!=48000)return false;
    s->samples+=count;
    if(s->validate)for(size_t n=0;n<count;++n) {
        uint16_t v=(uint16_t)pcm[n];s->nonzero|=v;
        s->hash=(s->hash^(v&255U))*16777619U;s->hash=(s->hash^(v>>8))*16777619U;
    }
    return true;
}
void publish(unsigned f,unsigned round,const opus_benchmark_case_t &r) {
    taskENTER_CRITICAL();status.current_case=f;status.round=round;results[f]=r;taskEXIT_CRITICAL();
}
}
extern "C" bool opus_benchmark_request(void) {
    taskENTER_CRITICAL();bool ok=status.state!=1&&status.state!=2;
    if(ok) {uint32_t run=status.run+1;memset(&status,0,sizeof(status));memset(results,0,sizeof(results));
        status.run=run;status.state=1;status.cases=HELIX_TIMING_CASES;status.rounds=kRounds;}
    taskEXIT_CRITICAL();return ok;
}
extern "C" void opus_benchmark_cancel_pending(void) {
    taskENTER_CRITICAL();if(status.state==1){status.state=4;status.error=-9002;}taskEXIT_CRITICAL();
}
extern "C" void opus_benchmark_snapshot(opus_benchmark_status_t *out) {
    taskENTER_CRITICAL();*out=status;taskEXIT_CRITICAL();
}
extern "C" void opus_benchmark_case_snapshot(unsigned n,opus_benchmark_case_t *out) {
    taskENTER_CRITICAL();if(n<HELIX_TIMING_CASES)*out=results[n];else memset(out,0,sizeof(*out));taskEXIT_CRITICAL();
}
extern "C" void opus_benchmark_run_pending(uint32_t generation,bool (*current)(uint32_t)) {
    taskENTER_CRITICAL();bool pending=status.state==1;if(pending)status.state=2;taskEXIT_CRITICAL();
    if(!pending)return;
    int error=0;uint32_t before=free_dram(),empty=0;
    for(unsigned n=0;n<16;++n) {
        vTaskDelay(1);uint32_t t=cpu_time();(void)clock_us();(void)clock_us();vTaskDelay(1);empty+=cpu_time()-t;
    }
    taskENTER_CRITICAL();status.dram_before=before;status.empty_task_us=(empty+8)/16;taskEXIT_CRITICAL();
    for(unsigned f=0;f<HELIX_TIMING_CASES&&!error;++f) {
        helix_timing_fixture_t fixture;copy_words(&fixture,&helix_timing_fixtures[f],sizeof(fixture));
        opus_benchmark_case_t r={};r.min_dram=free_dram();r.stack_free=UINT32_MAX;
        if(fixture.first>HELIX_TIMING_PACKETS||fixture.count>HELIX_TIMING_PACKETS-fixture.first)error=-9004;
        for(unsigned round=0;round<=kRounds&&!error;++round) {
            // Reset reservoir/history between identical clips, never between frames.
            helix_codec_t *codec=helix_codec_create((helix_codec_kind_t)fixture.kind,0);
            if(!codec){error=-9001;break;}
            r.scratch_bytes=helix_codec_dram_used(codec);r.scratch_words=helix_codec_iram_used(codec);
            Sink sink={0,2166136261U,round==0,0};
            for(unsigned p=0;p<fixture.count&&!error;++p) {
                if(!current(generation)){error=-9002;break;}
                helix_timing_packet_t entry;copy_words(&entry,&helix_timing_packets[fixture.first+p],sizeof(entry));
                size_t capacity=0;uint8_t *data=helix_codec_write_pointer(codec,&capacity);
                size_t padded=(entry.bytes+3U)&~3U;
                if(!data||((uintptr_t)data&3)||!entry.bytes||entry.bytes>1536||padded>capacity||(entry.offset&3)||
                   entry.offset>HELIX_TIMING_PAYLOAD_BYTES||padded>HELIX_TIMING_PAYLOAD_BYTES-entry.offset){error=-9004;break;}
                copy_words(data,(const uint8_t *)helix_timing_payload+entry.offset,entry.bytes);
                if(helix_codec_buffer_commit(codec,entry.bytes)!=0){error=-9004;break;}
                vTaskDelay(1);uint32_t task_start=cpu_time(),t=clock_us(),prior=sink.samples;
                int rc=helix_codec_process_one(codec,accept,&sink);
                uint32_t elapsed=clock_us()-t;
                vTaskDelay(1);uint32_t task_elapsed=cpu_time()-task_start;
                if(rc!=0||sink.samples<=prior){error=rc<0?rc:-9005;break;}
                if(round) {++r.packets;r.samples+=sink.samples-prior;r.wall_us+=elapsed;r.task_us+=task_elapsed;
                    if(elapsed>r.max_wall_us)r.max_wall_us=elapsed;}
                uint32_t heap=free_dram(),stack=uxTaskGetStackHighWaterMark(nullptr);
                if(heap<r.min_dram)r.min_dram=heap;
                if(stack<r.stack_free)r.stack_free=stack;
            }
            if(!error&&sink.samples!=fixture.samples)error=-9006;
            if(!round){r.pcm_hash=sink.hash;if(!sink.nonzero&&!error)error=-9007;}
            helix_codec_destroy(codec); // Also on cancellation, malformed data and decode error.
            r.error=error;publish(f,round,r);
        }
        r.error=error;publish(f,status.round,r);
    }
    uint32_t after=free_dram();
    taskENTER_CRITICAL();status.dram_after=after;status.error=error;status.state=error?4:3;taskEXIT_CRITICAL();
}
