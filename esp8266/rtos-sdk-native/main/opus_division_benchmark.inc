/* Diagnostic only: both LX106 helpers in one image, same indirect-call loop,
 * complete ordered RAM chunks. No audio or decoder CPU claim. Microseconds
 * include interrupts/preemption. Odd runs: after yield, NOT known cold cache.
 * Even runs: one identical warmup batch immediately before timing.
 * Do not mask interrupts across a batch, flush cache, or add tasks/connections. */
#include "opus_division_fixtures.h"
extern "C" uint32_t __udivsi3(uint32_t, uint32_t);
extern "C" uint32_t yoradio_opus_small_udiv(uint32_t, uint32_t);
static_assert(sizeof(opus_benchmark_case_t)==44, "Keep raw result RAM budget");
static_assert(sizeof(opus_division_fixtures)/sizeof(opus_division_fixtures[0])
              ==OPUS_BENCH_FIXTURE_COUNT, "Fixture order must match census");
namespace {
using division_fn=uint32_t (*)(uint32_t,uint32_t);
inline uint32_t division_clock(){
    /* SDK resets CCOUNT in tick handling. Match the established stage clock:
     * atomic accumulated epoch + current cycles, lock ONLY the snapshot. */
    taskENTER_CRITICAL();
    uint32_t value=(uint32_t)esp_timer_get_time();
    taskEXIT_CRITICAL();
    return value;
}
/* Prevent specialization into unequal direct-call loops. Unsigned hash keeps
 * every quotient live, with defined wraparound. Registers follow call0 ABI. */
__attribute__((noinline,noclone)) uint32_t division_batch(
    division_fn fn,const uint32_t *pairs,unsigned count){
    uint32_t value=2166136261U;
    for(unsigned i=0;i<count;++i)
        value=(value^fn(pairs[2*i],pairs[2*i+1]))*16777619U;
    return value;
}
}
extern "C" __attribute__((noinline)) void opus_benchmark_run_pending(
    uint32_t generation,bool (*current)(uint32_t)){
    taskENTER_CRITICAL();
    bool pending=s_status.state==1;
    uint32_t run=s_status.run;
    if(pending)s_status.state=2;
    taskEXIT_CRITICAL();
    if(!pending)return;
    uint32_t before=dram_free();
    /* Same 1536-byte allocation as raw packet input; no full trace in RAM. */
    uint32_t *pairs=static_cast<uint32_t *>(heap_caps_malloc(kPacketBytes,MALLOC_CAP_8BIT));
    int error=pairs?0:-9101;
    taskENTER_CRITICAL();
    s_status.dram_before=before;s_status.state_bytes=0;
    taskEXIT_CRITICAL();
    for(unsigned f=0;f<OPUS_BENCH_FIXTURE_COUNT&&!error;++f){
        opus_division_fixture_t fixture;
        copy_words(&fixture,&opus_division_fixtures[f],sizeof(fixture));
        if(fixture.first>OPUS_DIVISION_PAIR_COUNT||
            fixture.count>OPUS_DIVISION_PAIR_COUNT-fixture.first){error=-9102;break;}
        opus_benchmark_case_t result={};
        result.min_dram=dram_free();result.stack_free=uxTaskGetStackHighWaterMark(nullptr);
        for(unsigned round=0;round<kRounds&&!error;++round){
            for(unsigned offset=0;offset<fixture.count&&!error;){
                if(!current(generation)){error=-9002;break;}
                unsigned count=fixture.count-offset;
                if(count>kPacketBytes/8)count=kPacketBytes/8;
                copy_words(pairs,&opus_division_pairs[2*(fixture.first+offset)],count*8);
                /* Exact per-operand check outside timing; not a cold-cache proof. */
                for(unsigned i=0;i<count;++i){
                    if(!pairs[2*i+1]||__udivsi3(pairs[2*i],pairs[2*i+1])!=
                        yoradio_opus_small_udiv(pairs[2*i],pairs[2*i+1])){error=-9103;break;}
                }
                if(error)break;
                uint32_t ticks[2],hashes[2];
                unsigned first=(result.batches+run)&1U;
                for(unsigned order=0;order<2;++order){
                    unsigned which=first^order;
                    division_fn fn=which?yoradio_opus_small_udiv:__udivsi3;
                    vTaskDelay(1);
                    if(!(run&1U))(void)division_batch(fn,pairs,count);
                    uint32_t start=division_clock();
                    hashes[which]=division_batch(fn,pairs,count);
                    ticks[which]=division_clock()-start;
                }
                if(hashes[0]!=hashes[1]){error=-9103;break;}
                if(UINT32_MAX-result.reference_ticks<ticks[0]||
                    UINT32_MAX-result.candidate_ticks<ticks[1]){error=-9104;break;}
                result.calls+=count;++result.batches;
                result.reference_ticks+=ticks[0];result.candidate_ticks+=ticks[1];
                if(ticks[0]>result.reference_max)result.reference_max=ticks[0];
                if(ticks[1]>result.candidate_max)result.candidate_max=ticks[1];
                result.reference_hash+=hashes[0];result.candidate_hash+=hashes[1];
                uint32_t free=dram_free(),stack=uxTaskGetStackHighWaterMark(nullptr);
                if(free<result.min_dram)result.min_dram=free;
                if(stack<result.stack_free)result.stack_free=stack;
                offset+=count;
            }
            publish(f,round+1,result);
        }
        result.error=error;publish(f,kRounds,result);
    }
    heap_caps_free(pairs);
    taskENTER_CRITICAL();
    s_status.dram_after=dram_free();s_status.error=error;s_status.state=error?4:3;
    taskEXIT_CRITICAL();
}
