#include "platform.h"
#include "native_input_reclaim.h"
#include <errno.h>
#include <sched.h>
#include <stdatomic.h>
#include <string.h>
#include <time.h>

enum { CAPACITY=2060, TARGET=8, MINIMUM=4, STRESS_PACKETS=10000 };
static _Thread_local unsigned critical_depth, local_calls;
static _Thread_local bool in_isr, allocator_worker;
static pthread_mutex_t ledger_lock=PTHREAD_MUTEX_INITIALIZER;
static struct { void *pointer; size_t bytes; bool live; } ledger[256];
static void *protected_pointers[20];
static unsigned protected_count;
static atomic_uint live_blocks, live_semaphores, packet_frees, original_calls, release_calls;
static _Thread_local size_t last_count,last_size;
static unsigned baseline_frees,recovery_after;
static adaptive_input_t *active_queue;
enum { ALWAYS_FAIL, SUCCESS, RECOVER, DELEGATE_SENTINEL, PINNED, REFILL };
static unsigned allocation_mode;
enum { NO_GATE, RELEASE_GATE, FREE_GATE, RETRY_GATE };
static unsigned gate_point;
static pthread_barrier_t entered_gate,resume_gate;
static atomic_bool gate_used, deny_main_release;
static pthread_mutex_t refill_lock=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t refill_condition=PTHREAD_COND_INITIALIZER;
static bool refill_request,refill_complete,refill_stop;

void test_enter_critical(portMUX_TYPE *lock) {
    CHECK(!critical_depth && !in_isr,"critical_not_nested_or_isr");
    CHECK(!pthread_mutex_lock(lock),"critical_lock");++critical_depth;
}
void test_exit_critical(portMUX_TYPE *lock) {
    CHECK(critical_depth==1,"critical_balance");--critical_depth;
    CHECK(!pthread_mutex_unlock(lock),"critical_unlock");
}
BaseType_t xPortInIsrContext(void) { return in_isr; }
static void outside_lock(void) { CHECK(!critical_depth,"heap_rtos_outside_registry_queue_locks"); }
static void barrier(pthread_barrier_t *value) {
    outside_lock();int result=pthread_barrier_wait(value);
    CHECK(result==0 || result==PTHREAD_BARRIER_SERIAL_THREAD,"barrier_progress");
}
static void gate(unsigned point) {
    if (allocator_worker && gate_point==point && !atomic_exchange(&gate_used,true)) {
        barrier(&entered_gate);barrier(&resume_gate);
    }
}
void *cyd_test_calloc(size_t count,size_t size) {
    outside_lock();CHECK(!in_isr,"queue_allocator_task_only");
    if (size && count>SIZE_MAX/size) return NULL;
    void *pointer=calloc(count,size);CHECK(pointer,"fixture_heap_available");
    CHECK(!pthread_mutex_lock(&ledger_lock),"ledger_lock");
    unsigned index=0;while(index<256 && ledger[index].live)++index;
    CHECK(index<256,"ledger_capacity");
    ledger[index].pointer=pointer;ledger[index].bytes=count*size;ledger[index].live=true;
    atomic_fetch_add(&live_blocks,1);
    CHECK(!pthread_mutex_unlock(&ledger_lock),"ledger_unlock");return pointer;
}
void *cyd_test_malloc(size_t bytes) { return cyd_test_calloc(1,bytes); }
void cyd_test_free(void *pointer) {
    outside_lock();if (!pointer)return;
    for(unsigned i=0;i<protected_count;++i)
        CHECK(protected_pointers[i]!=pointer,"no_live_lease_is_freed");
    CHECK(!pthread_mutex_lock(&ledger_lock),"ledger_lock");
    unsigned index=0;while(index<256 && (!ledger[index].live || ledger[index].pointer!=pointer))++index;
    CHECK(index<256,"queue_free_owned_pointer");
    size_t bytes=ledger[index].bytes;ledger[index].live=false;
    CHECK(!pthread_mutex_unlock(&ledger_lock),"ledger_unlock");
    if(bytes==CAPACITY)gate(FREE_GATE);
    free(pointer);atomic_fetch_sub(&live_blocks,1);
    if(bytes==CAPACITY)atomic_fetch_add(&packet_frees,1);
}
struct test_semaphore { pthread_mutex_t mutex;pthread_cond_t condition;bool signalled; };
SemaphoreHandle_t xSemaphoreCreateBinary(void) {
    outside_lock();SemaphoreHandle_t result=calloc(1,sizeof(*result));CHECK(result,"semaphore_alloc");
    CHECK(!pthread_mutex_init(&result->mutex,NULL) && !pthread_cond_init(&result->condition,NULL),"semaphore_init");
    atomic_fetch_add(&live_semaphores,1);return result;
}
void vSemaphoreDelete(SemaphoreHandle_t semaphore) {
    outside_lock();CHECK(!pthread_cond_destroy(&semaphore->condition) && !pthread_mutex_destroy(&semaphore->mutex),"semaphore_destroy");
    atomic_fetch_sub(&live_semaphores,1);free(semaphore);
}
BaseType_t xSemaphoreGive(SemaphoreHandle_t semaphore) {
    outside_lock();CHECK(!pthread_mutex_lock(&semaphore->mutex),"semaphore_lock");
    semaphore->signalled=true;CHECK(!pthread_cond_signal(&semaphore->condition),"semaphore_signal");
    CHECK(!pthread_mutex_unlock(&semaphore->mutex),"semaphore_unlock");return pdTRUE;
}
BaseType_t xSemaphoreTake(SemaphoreHandle_t semaphore,TickType_t timeout) {
    outside_lock();struct timespec until;CHECK(!clock_gettime(CLOCK_REALTIME,&until),"clock");
    until.tv_sec+=timeout/1000;until.tv_nsec+=(timeout%1000)*1000000L;
    if(until.tv_nsec>=1000000000L){++until.tv_sec;until.tv_nsec-=1000000000L;}
    CHECK(!pthread_mutex_lock(&semaphore->mutex),"semaphore_lock");int error=0;
    while(!semaphore->signalled && !error)
        error=timeout==portMAX_DELAY?pthread_cond_wait(&semaphore->condition,&semaphore->mutex):
            pthread_cond_timedwait(&semaphore->condition,&semaphore->mutex,&until);
    CHECK(!error || error==ETIMEDOUT,"semaphore_wait");
    bool ready=semaphore->signalled;semaphore->signalled=false;
    CHECK(!pthread_mutex_unlock(&semaphore->mutex),"semaphore_unlock");return ready;
}
TickType_t xTaskGetTickCount(void) {
    outside_lock();struct timespec now;CHECK(!clock_gettime(CLOCK_MONOTONIC,&now),"clock");
    return (TickType_t)((uint64_t)now.tv_sec*1000+now.tv_nsec/1000000);
}
bool __real_adaptive_input_release_one(adaptive_input_t *input);
bool __wrap_adaptive_input_release_one(adaptive_input_t *input) {
    outside_lock();CHECK(!in_isr,"queue_release_task_only");
    CHECK(!atomic_load(&deny_main_release) || allocator_worker,"retiring_new_pins_denied");
    gate(RELEASE_GATE);atomic_fetch_add(&release_calls,1);
    return __real_adaptive_input_release_one(input);
}
static void request_refill(void) {
    CHECK(!pthread_mutex_lock(&refill_lock),"refill_lock");
    refill_complete=false;refill_request=true;CHECK(!pthread_cond_signal(&refill_condition),"refill_signal");
    while(!refill_complete)CHECK(!pthread_cond_wait(&refill_condition,&refill_lock),"refill_wait");
    CHECK(!pthread_mutex_unlock(&refill_lock),"refill_unlock");
}
void *__real_esp_mbedtls_mem_calloc(size_t count,size_t size) {
    outside_lock();++local_calls;atomic_fetch_add(&original_calls,1);
    last_count=count;last_size=size;
    if(allocation_mode==REFILL)CHECK(local_calls<=TARGET-MINIMUM+1,"bounded_retry_budget");
    if(local_calls==1 && allocation_mode!=ALWAYS_FAIL && (allocation_mode!=PINNED || allocator_worker))
        CHECK(atomic_load(&packet_frees)==baseline_frees,"original_allocator_first_no_preclaim");
    if(local_calls>1 && allocation_mode!=ALWAYS_FAIL)
        CHECK(atomic_load(&packet_frees)>baseline_frees,"retry_after_completed_slot_free");
    if(allocation_mode==DELEGATE_SENTINEL)return calloc(1,1);
    if(!count || !size || size>SIZE_MAX/count)return NULL;
    if(allocation_mode==REFILL && local_calls>1)request_refill();
    bool success=allocation_mode==SUCCESS ||
        (allocation_mode==RECOVER && atomic_load(&packet_frees)-baseline_frees>=recovery_after) ||
        (allocation_mode==PINNED && allocator_worker && local_calls>1);
    if(success){gate(RETRY_GATE);return calloc(count,size);}
    return NULL;
}
static void *allocate(size_t count,size_t size) {
    local_calls=0;void *result=__wrap_esp_mbedtls_mem_calloc(count,size);
    CHECK(last_count==count && last_size==size,"original_arguments_preserved");return result;
}
static void reset(void) {
    CHECK(!atomic_load(&live_blocks) && !atomic_load(&live_semaphores),"previous_case_quiescent");
    atomic_store(&packet_frees,0);atomic_store(&original_calls,0);atomic_store(&release_calls,0);
    baseline_frees=0;recovery_after=0;allocation_mode=ALWAYS_FAIL;active_queue=NULL;
    gate_point=NO_GATE;atomic_store(&gate_used,false);atomic_store(&deny_main_release,false);
    protected_count=0;in_isr=allocator_worker=false;critical_depth=local_calls=0;
    refill_request=refill_complete=refill_stop=false;
}
static adaptive_input_t *create(unsigned target,unsigned minimum) {
    adaptive_input_t *input=adaptive_input_create((size_t)target*CAPACITY,(size_t)minimum*CAPACITY,CAPACITY);
    CHECK(input,"public_queue_create");adaptive_input_stats_t stats=adaptive_input_stats(input);
    CHECK(stats.target==target && stats.minimum==minimum && stats.resident==target,"queue_geometry");return input;
}
static adaptive_input_t *bound_queue(void) {
    active_queue=create(TARGET,MINIMUM);
    CHECK(native_input_reclaim_bind(active_queue),"bind_fresh_pool");return active_queue;
}
static void destroy_bound(adaptive_input_t *input) {
    CHECK(native_input_reclaim_detach(input)==NATIVE_INPUT_RECLAIM_DETACHED,"all_allocator_pins_drained");
    adaptive_input_destroy(input);
}
static void zero_and_free(void *pointer,size_t bytes) {
    CHECK(pointer,"recovery_returns_original_pointer");
    for(size_t i=0;i<bytes;++i)CHECK(!((uint8_t *)pointer)[i],"calloc_zeroing_preserved");
    memset(pointer,0xa5,bytes);free(pointer);
}
static void registry(void) {
    adaptive_input_t *first=bound_queue(),*other=create(TARGET,MINIMUM);
    CHECK(native_input_reclaim_bind(first),"same_active_bind_idempotent");
    CHECK(!native_input_reclaim_bind(NULL) && !native_input_reclaim_bind(other),"null_conflicting_bind_rejected");
    CHECK(native_input_reclaim_detach(NULL)==NATIVE_INPUT_RECLAIM_WRONG_OWNER &&
        native_input_reclaim_detach(other)==NATIVE_INPUT_RECLAIM_WRONG_OWNER,"wrong_owner_no_effect");
    CHECK(native_input_reclaim_bind(first),"wrong_owner_no_effect");
    in_isr=true;
    CHECK(!native_input_reclaim_bind(first) && !native_input_reclaim_bind(other),"isr_bind_rejected");
    CHECK(native_input_reclaim_detach(first)==NATIVE_INPUT_RECLAIM_WRONG_OWNER,"isr_detach_rejected");
    in_isr=false;
    CHECK(!allocate(1,32),"allocation_failure_preserved");
    CHECK(adaptive_input_stats(first).resident==MINIMUM && adaptive_input_stats(other).resident==TARGET,"conflict_retains_original_owner");
    CHECK(native_input_reclaim_detach(first)==NATIVE_INPUT_RECLAIM_DETACHED,"all_allocator_pins_drained");
    CHECK(native_input_reclaim_detach(first)==NATIVE_INPUT_RECLAIM_WRONG_OWNER,"stale_detach_no_effect");
    adaptive_input_destroy(first);
    CHECK(native_input_reclaim_bind(other),"bind_after_explicit_detach");destroy_bound(other);
}
static void unbound(void) {
    CHECK(!allocate(1,32) && atomic_load(&original_calls)==1 && !atomic_load(&release_calls),"unbound_calls_original_once");
}
static void first_success(void) {
    adaptive_input_t *input=bound_queue();allocation_mode=SUCCESS;
    zero_and_free(allocate(3,13),39);
    CHECK(atomic_load(&original_calls)==1 && !atomic_load(&packet_frees) &&
          adaptive_input_stats(input).resident==TARGET,"success_no_reclaim");destroy_bound(input);
}
static void malformed(bool sentinel) {
    adaptive_input_t *input=bound_queue();allocation_mode=sentinel?DELEGATE_SENTINEL:ALWAYS_FAIL;
    size_t arguments[][2]={{0,13},{3,0},{SIZE_MAX,2},{2,SIZE_MAX},{0,SIZE_MAX}};
    for(unsigned i=0;i<5;++i){
        unsigned before=atomic_load(&original_calls);void *result=allocate(arguments[i][0],arguments[i][1]);
        CHECK(atomic_load(&original_calls)==before+1 && !atomic_load(&release_calls),"malformed_delegates_once_without_reclaim");
        if(sentinel)zero_and_free(result,1);else CHECK(!result,"malformed_original_result");
    }
    CHECK(adaptive_input_stats(input).resident==TARGET,"malformed_preserves_pool");destroy_bound(input);
}
static void isr_request(void) {
    adaptive_input_t *input=bound_queue();in_isr=true;
    CHECK(!allocate(1,32),"isr_original_failure");in_isr=false;
    CHECK(atomic_load(&original_calls)==1 && !atomic_load(&release_calls) &&
          adaptive_input_stats(input).resident==TARGET,"isr_no_reclaim");destroy_bound(input);
}
static void exhaustion(bool zero_budget) {
    adaptive_input_t *input=zero_budget?create(TARGET,TARGET):bound_queue();
    if(zero_budget)CHECK(native_input_reclaim_bind(input),"bind_zero_budget");
    CHECK(!allocate(1,32),"allocation_exhaustion_returns_null");
    unsigned budget=zero_budget?0:TARGET-MINIMUM;
    CHECK(atomic_load(&original_calls)==budget+1 && atomic_load(&packet_frees)==budget &&
          adaptive_input_stats(input).resident==TARGET-budget,"floor_and_retry_limit");
    destroy_bound(input);
}
static void repeat_exhaustion(void) {
    adaptive_input_t *input=bound_queue();
    CHECK(!allocate(1,32) && !allocate(1,32),"repeated_allocation_failure");
    CHECK(atomic_load(&original_calls)==TARGET-MINIMUM+2 &&
          atomic_load(&packet_frees)==TARGET-MINIMUM &&
          adaptive_input_stats(input).resident==MINIMUM,"repeated_pressure_keeps_floor");
    destroy_bound(input);
}
static void recovery(unsigned count,bool restore) {
    adaptive_input_t *input=bound_queue();allocation_mode=RECOVER;recovery_after=count;
    zero_and_free(allocate(3,13),39);
    CHECK(atomic_load(&original_calls)==count+1 && atomic_load(&packet_frees)==count &&
          adaptive_input_stats(input).resident==TARGET-count,"one_original_retry_per_completed_free");
    if(restore){
        adaptive_input_restore(input);CHECK(adaptive_input_stats(input).resident==TARGET,"producer_restores_unleased_slots");
        baseline_frees=atomic_load(&packet_frees);allocation_mode=SUCCESS;zero_and_free(allocate(2,9),18);
        CHECK(adaptive_input_stats(input).resident==TARGET,"restored_success_keeps_pool");
    }
    destroy_bound(input);
}
static void protect(void *pointer) { CHECK(protected_count<20,"protected_capacity");protected_pointers[protected_count++]=pointer; }
static void leases(unsigned control_state) {
    adaptive_input_t *input=bound_queue();uint8_t control[64];memset(control,0x63,sizeof(control));
    CHECK(adaptive_input_attach_control(input,control,sizeof(control)),"attach_borrowed_control");
    void *reading,*ready,*writing,*node;size_t size;
    CHECK(adaptive_input_acquire(input,&reading,31,0) && adaptive_input_commit(input,reading),"reading_lease_prepare");
    CHECK(adaptive_input_receive(input,&size,0)==reading,"public_reading_lease");memset(reading,0x31,31);protect(reading);
    CHECK(adaptive_input_acquire(input,&ready,29,0),"ready_acquire");memset(ready,0x29,29);protect(ready);
    CHECK(adaptive_input_commit(input,ready),"ready_commit");
    CHECK(adaptive_input_acquire(input,&writing,27,0),"writing_acquire");memset(writing,0x27,27);protect(writing);
    CHECK(adaptive_input_acquire_control(input,&node,sizeof(control),0) && node==control,"control_lease");protect(control);
    if(control_state!=0)CHECK(adaptive_input_commit(input,control),"control_commit");
    if(control_state==2){
        CHECK(adaptive_input_receive(input,&size,0)==ready,"advance_to_control");
        CHECK(adaptive_input_receive(input,&size,0)==control,"control_reading");
    }
    CHECK(!allocate(1,32),"leased_pressure_fails_safely");
    adaptive_input_stats_t stats=adaptive_input_stats(input);
    CHECK(stats.resident==MINIMUM && stats.minimum==MINIMUM && stats.reading==(control_state==2?2U:1U) && stats.writing==1,
          "leases_and_floor_preserved");
    for(unsigned i=0;i<31;++i)CHECK(((uint8_t *)reading)[i]==0x31,"reading_payload_unchanged");
    for(unsigned i=0;i<29;++i)CHECK(((uint8_t *)ready)[i]==0x29,"ready_payload_unchanged");
    for(unsigned i=0;i<27;++i)CHECK(((uint8_t *)writing)[i]==0x27,"writing_payload_unchanged");
    for(unsigned i=0;i<64;++i)CHECK(control[i]==0x63,"control_payload_unchanged");
    protected_count=0;
    if(control_state!=2){
        CHECK(adaptive_input_receive(input,&size,0)==ready,"ready_fifo_preserved");CHECK(adaptive_input_return(input,ready),"return_ready");
    }else CHECK(adaptive_input_return(input,ready),"return_second_reading_lease");
    if(control_state==0)CHECK(adaptive_input_cancel(input,control),"cancel_control_writing");
    else {
        if(control_state==1)CHECK(adaptive_input_receive(input,&size,0)==control,"control_fifo_preserved");
        CHECK(adaptive_input_return(input,control),"return_control");
    }
    CHECK(adaptive_input_return(input,reading) && adaptive_input_cancel(input,writing),"release_original_leases");
    destroy_bound(input);
}
static void no_idle(void) {
    adaptive_input_t *input=bound_queue();void *packets[TARGET];
    for(unsigned i=0;i<TARGET;++i){CHECK(adaptive_input_acquire(input,&packets[i],32,0),"acquire_all_leases");protect(packets[i]);}
    CHECK(!allocate(1,32) && atomic_load(&original_calls)==1 && !atomic_load(&packet_frees),"no_idle_no_retry");
    CHECK(adaptive_input_stats(input).writing==TARGET,"all_busy_leases_kept");protected_count=0;
    for(unsigned i=0;i<TARGET;++i)CHECK(adaptive_input_cancel(input,packets[i]),"cancel_all_leases");
    destroy_bound(input);
}
static void *pinned_allocator(void *unused) {
    (void)unused;allocator_worker=true;void *result=allocate(3,13);allocator_worker=false;return result;
}
static void pinned_detach(unsigned point) {
    adaptive_input_t *input=bound_queue(),*other=create(TARGET,MINIMUM);
    allocation_mode=PINNED;gate_point=point;
    CHECK(!pthread_barrier_init(&entered_gate,NULL,2) && !pthread_barrier_init(&resume_gate,NULL,2),"gate_init");
    pthread_t thread;CHECK(!pthread_create(&thread,NULL,pinned_allocator,NULL),"pinned_worker_start");barrier(&entered_gate);
    CHECK(native_input_reclaim_detach(other)==NATIVE_INPUT_RECLAIM_WRONG_OWNER && native_input_reclaim_bind(input),"wrong_owner_no_effect");
    CHECK(native_input_reclaim_detach(input)==NATIVE_INPUT_RECLAIM_BUSY,"pinned_owner_is_busy");
    CHECK(!native_input_reclaim_bind(input) && !native_input_reclaim_bind(other),"retiring_bind_denied");
    unsigned before=atomic_load(&release_calls);atomic_store(&deny_main_release,true);
    CHECK(!allocate(1,17) && atomic_load(&release_calls)==before,"retiring_new_pins_denied");
    atomic_store(&deny_main_release,false);barrier(&resume_gate);
    void *result=NULL;CHECK(!pthread_join(thread,&result),"pinned_worker_join");zero_and_free(result,39);
    CHECK(!native_input_reclaim_bind(input) && !native_input_reclaim_bind(other),"retired_owner_requires_explicit_detach");
    CHECK(native_input_reclaim_detach(input)==NATIVE_INPUT_RECLAIM_DETACHED,"explicit_detach_after_pin_drain");
    CHECK(native_input_reclaim_bind(other),"rebind_after_explicit_drain");destroy_bound(other);adaptive_input_destroy(input);
    CHECK(!pthread_barrier_destroy(&entered_gate) && !pthread_barrier_destroy(&resume_gate),"gate_destroy");
}
static void *refill_producer(void *unused) {
    (void)unused;CHECK(!pthread_mutex_lock(&refill_lock),"refill_lock");
    for(;;){
        while(!refill_request && !refill_stop)CHECK(!pthread_cond_wait(&refill_condition,&refill_lock),"refill_wait");
        if(refill_stop)break;
        refill_request=false;CHECK(!pthread_mutex_unlock(&refill_lock),"refill_unlock");
        adaptive_input_restore(active_queue);
        CHECK(adaptive_input_stats(active_queue).resident==TARGET,"concurrent_restore_replenishes_pool");
        CHECK(!pthread_mutex_lock(&refill_lock),"refill_lock");refill_complete=true;
        CHECK(!pthread_cond_signal(&refill_condition),"refill_signal");
    }
    CHECK(!pthread_mutex_unlock(&refill_lock),"refill_unlock");return NULL;
}
static void fixed_budget(void) {
    adaptive_input_t *input=bound_queue();
    for(unsigned i=0;i<3;++i)CHECK(adaptive_input_release_one(input),"initial_sparse_pool");
    CHECK(adaptive_input_stats(input).resident==5,"initial_sparse_pool");
    baseline_frees=atomic_load(&packet_frees);allocation_mode=REFILL;
    pthread_t thread;CHECK(!pthread_create(&thread,NULL,refill_producer,NULL),"refill_worker_start");
    CHECK(!allocate(1,32),"bounded_exhaustion_returns_failure");
    CHECK(!pthread_mutex_lock(&refill_lock),"refill_lock");refill_stop=true;
    CHECK(!pthread_cond_signal(&refill_condition) && !pthread_mutex_unlock(&refill_lock),"refill_stop");
    CHECK(!pthread_join(thread,NULL),"refill_worker_join");
    CHECK(atomic_load(&original_calls)==TARGET-MINIMUM+1 &&
          atomic_load(&packet_frees)==baseline_frees+TARGET-MINIMUM &&
          adaptive_input_stats(input).resident==TARGET,"fixed_target_budget");destroy_bound(input);
}
static atomic_bool transfer_done;
static void *producer(void *unused) {
    (void)unused;
    for(unsigned n=0;n<STRESS_PACKETS;++n){
        void *packet;CHECK(adaptive_input_acquire(active_queue,&packet,64,3000),"concurrent_acquire_progress");
        memset(packet,(uint8_t)n,64);memcpy(packet,&n,sizeof(n));
        CHECK(adaptive_input_commit(active_queue,packet),"concurrent_commit");
        if(n%31==0)adaptive_input_restore(active_queue);
    }
    return NULL;
}
static void *consumer(void *unused) {
    (void)unused;
    for(unsigned n=0;n<STRESS_PACKETS;++n){
        size_t bytes;void *packet=adaptive_input_receive(active_queue,&bytes,3000);
        CHECK(packet && bytes==64,"concurrent_receive_progress");unsigned actual;memcpy(&actual,packet,sizeof(actual));
        CHECK(actual==n,"concurrent_fifo_preserved");
        for(unsigned i=sizeof(actual);i<64;++i)CHECK(((uint8_t *)packet)[i]==(uint8_t)n,"concurrent_payload_preserved");
        CHECK(adaptive_input_return(active_queue,packet),"concurrent_return");
    }
    atomic_store(&transfer_done,true);return NULL;
}
static void *tls_pressure(void *unused) {
    (void)unused;
    do {
        local_calls=0;CHECK(!__wrap_esp_mbedtls_mem_calloc(1,15360),"concurrent_original_failure");
        CHECK(local_calls<=TARGET-MINIMUM+1,"concurrent_fixed_retry_budget");
        adaptive_input_stats_t stats=adaptive_input_stats(active_queue);
        CHECK(stats.resident>=MINIMUM && stats.occupied<=stats.resident,"concurrent_floor_and_leases");sched_yield();
    }while(!atomic_load(&transfer_done));
    return NULL;
}
static void concurrent(void) {
    adaptive_input_t *input=bound_queue();atomic_store(&transfer_done,false);
    pthread_t threads[4];void *(*functions[4])(void *)={producer,consumer,tls_pressure,tls_pressure};
    for(unsigned i=0;i<4;++i)CHECK(!pthread_create(&threads[i],NULL,functions[i],NULL),"stress_thread_start");
    for(unsigned i=0;i<4;++i)CHECK(!pthread_join(threads[i],NULL),"stress_thread_join");
    CHECK(!adaptive_input_stats(input).occupied,"all_stress_leases_returned");destroy_bound(input);
}
static const char *const cases[]={"registry","unbound","first-success","malformed-null","malformed-sentinel",
    "isr","exhaustion","repeat-exhaustion","zero-budget","recovery","floor-recovery","restore","control-writing","control-ready",
    "control-reading","no-idle","pinned-detach","free-detach","retry-detach","fixed-budget","concurrent"};
static void run_case(const char *name) {
    reset();
    if(!strcmp(name,"registry"))registry();
    else if(!strcmp(name,"unbound"))unbound();
    else if(!strcmp(name,"first-success"))first_success();
    else if(!strcmp(name,"malformed-null"))malformed(false);
    else if(!strcmp(name,"malformed-sentinel"))malformed(true);
    else if(!strcmp(name,"isr"))isr_request();
    else if(!strcmp(name,"exhaustion"))exhaustion(false);
    else if(!strcmp(name,"repeat-exhaustion"))repeat_exhaustion();
    else if(!strcmp(name,"zero-budget"))exhaustion(true);
    else if(!strcmp(name,"recovery"))recovery(2,false);
    else if(!strcmp(name,"floor-recovery"))recovery(4,false);
    else if(!strcmp(name,"restore"))recovery(4,true);
    else if(!strcmp(name,"control-writing"))leases(0);
    else if(!strcmp(name,"control-ready"))leases(1);
    else if(!strcmp(name,"control-reading"))leases(2);
    else if(!strcmp(name,"no-idle"))no_idle();
    else if(!strcmp(name,"pinned-detach"))pinned_detach(RELEASE_GATE);
    else if(!strcmp(name,"free-detach"))pinned_detach(FREE_GATE);
    else if(!strcmp(name,"retry-detach"))pinned_detach(RETRY_GATE);
    else if(!strcmp(name,"fixed-budget"))fixed_budget();
    else if(!strcmp(name,"concurrent"))concurrent();
    else CHECK(false,"known_case");
    CHECK(!atomic_load(&live_blocks) && !atomic_load(&live_semaphores) && !critical_depth,"case_all_allocations_released");
    printf("PASS:%s\n",name);fflush(stdout);
}
int main(int argc,char **argv) {
    CHECK(argc==2,"case_argument");
    if(!strcmp(argv[1],"all"))for(unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);++i)run_case(cases[i]);
    else run_case(argv[1]);
    return 0;
}
