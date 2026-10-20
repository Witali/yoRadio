#include <assert.h>
#include <pthread.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
static _Thread_local unsigned critical_depth;
#define portENTER_CRITICAL(p) do {assert(!pthread_mutex_lock(p));++critical_depth;} while(0)
#define portEXIT_CRITICAL(p) do {assert(critical_depth);--critical_depth;assert(!pthread_mutex_unlock(p));} while(0)
#define pdPASS 1
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define portMAX_DELAY UINT32_MAX
static uint32_t ticks;
static unsigned allocations,notifications,cases,restarts;
static _Thread_local jmp_buf task_exit;
static _Thread_local void (*restart_observer)(void);
static void require(bool condition,const char *name) {
    if(!condition){fprintf(stderr,"SEMANTIC_FAILURE:%s:\n",name);exit(80);}
}
static uint32_t xTaskGetTickCount(void) {return ticks;}
static void esp_restart(void) {
    require(!critical_depth,"restart_outside_critical");++restarts;
    if(restart_observer){restart_observer();return;}
    longjmp(task_exit,2);
}
static unsigned ulTaskNotifyTake(int clear,TickType_t wait) {
    assert(clear==pdTRUE);if(wait==portMAX_DELAY)longjmp(task_exit,1);
    ticks+=wait;return 0;
}
static int xTaskCreate(void (*fn)(void *),const char *name,unsigned size,void *arg,unsigned priority,TaskHandle_t *task) {
    (void)fn;assert(!strcmp(name,"web_reboot")&&size==2048&&!arg&&priority==2);++allocations;*task=(void *)1;return pdPASS;
}
static void xTaskNotifyGive(TaskHandle_t task) {assert(task==(void *)1);++notifications;}
static void vTaskDelete(TaskHandle_t task) {assert(task==(void *)1);}
#ifdef TARGET_C3
#include "websocket_service.h"
#include "reboot-production.inc"
typedef websocket_reboot_lease_t lease_t;
#define reserve websocket_service_reboot_reserve
#define cancel websocket_service_reboot_cancel
#define commit websocket_service_reboot_commit
#define request websocket_service_request_reboot
#define pending s_reboot_pending
#define deadline s_reboot_at
#define reserved s_reboot_reserved_epoch
#define epoch_next s_reboot_next_epoch
static void ready(void){atomic_store(&s_reboot_ready,true);}
static void unavailable(void){atomic_store(&s_reboot_ready,false);}
#else
#include "web_reboot.h"
#include "reboot-production.inc"
typedef web_reboot_lease_t lease_t;
#define reserve web_reboot_reserve
#define cancel web_reboot_cancel
#define commit web_reboot_commit
#define request web_reboot_request
#define pending s_pending
#define deadline s_deadline
#define reserved s_reserved_epoch
#define epoch_next s_next_epoch
static void ready(void){assert(web_reboot_start()==ESP_OK);}
static void unavailable(void){atomic_store(&s_ready,false);}
#endif
static void reset(void) {
    pending=false;reserved=0;deadline=0;epoch_next=0;ticks=100;ready();++cases;
}
static void expect_task(int expected) {
    unsigned before=allocations;int result=setjmp(task_exit);
    if(!result){
#ifdef TARGET_C3
        poll_reboot();result=1;
#else
        reboot_task(NULL);
#endif
    }
    assert(result==expected&&allocations==before);
}
static pthread_barrier_t barrier;
static lease_t raced_lease;
static esp_err_t reserve_result;
static void *reserve_thread(void *arg) {(void)arg;pthread_barrier_wait(&barrier);reserve_result=reserve(&raced_lease);return NULL;}
static void *request_thread(void *arg) {(void)arg;pthread_barrier_wait(&barrier);request(0);return NULL;}
#ifndef TARGET_C3
static pthread_barrier_t restart_barrier;
static uint64_t immediate_epoch;
static bool check_competing_reserve;
static void rendezvous_restart(void) {
    (void)pthread_barrier_wait(&restart_barrier);
    (void)pthread_barrier_wait(&restart_barrier);
}
static void returning_restart(void) {}
static void *observe_restart(void *arg) {
    (void)arg;
    (void)pthread_barrier_wait(&restart_barrier);
    if(check_competing_reserve){
        lease_t competing={0};
        esp_err_t result=reserve(&competing);
        require(result==ESP_ERR_INVALID_STATE&&!competing.epoch,
                "reservation_retained_during_restart");
    }
    // This ordinary request is irreversible, but must remain deferred while the
    // immediate caller is inside the SDK. Execute the actual reboot task loop.
    request(0);
    require(reserved==immediate_epoch,"reservation_retained_during_restart");
    unsigned before=restarts;
    expect_task(1);
    require(restarts==before,"ordinary_task_deferred_during_restart");
    (void)pthread_barrier_wait(&restart_barrier);
    return NULL;
}
typedef struct {lease_t lease;esp_err_t result;} reservation_race_t;
static void *competing_reservation(void *arg) {
    reservation_race_t *attempt=arg;
    (void)pthread_barrier_wait(&barrier);
    attempt->result=reserve(&attempt->lease);
    return NULL;
}
static void interleaved_immediate_cases(void) {
    lease_t lease={0};
    for(unsigned pending_before=0;pending_before<2;++pending_before){
        reset();assert(reserve(&lease)==ESP_OK);immediate_epoch=lease.epoch;
        if(pending_before)request(0);
        check_competing_reserve=!pending_before;
        assert(!pthread_barrier_init(&restart_barrier,NULL,2));
        pthread_t observer;assert(!pthread_create(&observer,NULL,observe_restart,NULL));
        unsigned before=restarts,allocated=allocations;restart_observer=rendezvous_restart;
        require(web_reboot_restart_reserved_now(&lease)==ESP_OK,
                "valid_immediate_calls_sdk");
        restart_observer=NULL;
        assert(!pthread_join(observer,NULL)&&!pthread_barrier_destroy(&restart_barrier));
        require(restarts==before+1&&pending&&reserved==immediate_epoch&&
                lease.epoch==immediate_epoch&&allocations==allocated,
                "interleaved_immediate_keeps_lease_and_durable_request");
        assert(cancel(&lease)==ESP_OK);expect_task(2);
    }
}
static void immediate_cases(void) {
    lease_t lease={0},stale;
    // Invalid-token controls must report a semantic failure even if a mutant
    // incorrectly reaches the SDK; do not longjmp to an uninitialized target.
    restart_observer=returning_restart;
    reset();unsigned before=restarts,notified=notifications,allocated=allocations;
    require(web_reboot_restart_reserved_now(NULL)==ESP_ERR_INVALID_ARG&&
            web_reboot_restart_reserved_now(&lease)==ESP_ERR_INVALID_STATE,
            "immediate_rejects_invalid_token");
    require(!reserved&&!pending&&notifications==notified&&allocations==allocated&&
            restarts==before,"invalid_immediate_has_no_effects");

    reset();assert(reserve(&lease)==ESP_OK);stale=lease;
    assert(cancel(&lease)==ESP_OK&&reserve(&lease)==ESP_OK);
    immediate_epoch=lease.epoch;before=restarts;notified=notifications;
    require(web_reboot_restart_reserved_now(&stale)==ESP_ERR_INVALID_STATE&&
            reserved==immediate_epoch&&lease.epoch==immediate_epoch&&
            restarts==before&&notifications==notified&&!pending,
            "stale_copy_cannot_restart_or_consume_new_lease");
    assert(cancel(&lease)==ESP_OK);

    reset();assert(reserve(&lease)==ESP_OK);immediate_epoch=lease.epoch;
    unavailable();before=restarts;notified=notifications;
    restart_observer=returning_restart;
    require(web_reboot_restart_reserved_now(&lease)==ESP_ERR_INVALID_STATE&&
            restarts==before&&lease.epoch==immediate_epoch&&
            reserved==immediate_epoch&&notifications==notified&&!pending,
            "unavailable_service_rejects_immediate");
    restart_observer=NULL;ready();assert(cancel(&lease)==ESP_OK);

    reset();assert(reserve(&lease)==ESP_OK);immediate_epoch=lease.epoch;
    before=restarts;notified=notifications;allocated=allocations;
    restart_observer=returning_restart;
    require(web_reboot_restart_reserved_now(&lease)==ESP_OK&&restarts==before+1&&
            lease.epoch==immediate_epoch&&reserved==immediate_epoch&&
            notifications==notified&&allocations==allocated&&!pending,
            "returning_double_keeps_exclusive_lease");
    restart_observer=NULL;assert(cancel(&lease)==ESP_OK);

    // Both a nonreturning SDK seam and a returning seam retain the reservation.
    reset();assert(reserve(&lease)==ESP_OK);immediate_epoch=lease.epoch;
    before=restarts;
    int returned=setjmp(task_exit);
    if(!returned){(void)web_reboot_restart_reserved_now(&lease);require(false,"sdk_restart_does_not_return");}
    require(returned==2&&restarts==before+1&&reserved==immediate_epoch&&
            lease.epoch==immediate_epoch&&!critical_depth,
            "nonreturning_restart_retains_lease");
    assert(cancel(&lease)==ESP_OK);

    interleaved_immediate_cases();

    // A final eligibility rejection cancels only this token. A queued durable
    // request still restarts, and the stale immediate authorization is rejected.
    reset();assert(reserve(&lease)==ESP_OK);stale=lease;request(0);
    assert(cancel(&lease)==ESP_OK);before=restarts;
    require(web_reboot_restart_reserved_now(&stale)==ESP_ERR_INVALID_STATE&&
            pending&&!reserved&&restarts==before,"cancelled_guard_preserves_durable_reboot");
    expect_task(2);

    // AP and OTA use the same actual reserve operation. At admission exactly
    // one can own the token, regardless of which pthread wins the mutex.
    for(unsigned i=0;i<200;++i){
        reset();reservation_race_t a={0},b={0};pthread_t ta,tb;
        assert(!pthread_barrier_init(&barrier,NULL,3));
        assert(!pthread_create(&ta,NULL,competing_reservation,&a)&&
               !pthread_create(&tb,NULL,competing_reservation,&b));
        (void)pthread_barrier_wait(&barrier);
        assert(!pthread_join(ta,NULL)&&!pthread_join(tb,NULL)&&!pthread_barrier_destroy(&barrier));
        require((a.result==ESP_OK)+(b.result==ESP_OK)==1&&
                (a.result==ESP_OK?b.result:a.result)==ESP_ERR_INVALID_STATE,
                "ap_ota_have_one_reservation_owner");
        lease_t *winner=a.result==ESP_OK?&a.lease:&b.lease;
        require(winner->epoch&&reserved==winner->epoch&&!pending,
                "winning_admission_owns_exact_lease");
        assert(cancel(winner)==ESP_OK);
    }
    puts("PASS reserved-immediate: 208 scenarios; 200 real AP/OTA admission races, 2 SDK-entry interleavings, outside-critical restart, stale/cancelled/zero/NULL/unavailable rejection, returning and nonreturning SDK seams");
}
#endif
int main(int argc,char **argv) {
#ifndef TARGET_C3
    if(argc==2&&!strcmp(argv[1],"immediate")){immediate_cases();return 0;}
    if(argc==2&&!strcmp(argv[1],"interleaving")){interleaved_immediate_cases();return 0;}
#else
    (void)argc;(void)argv;
#endif
    lease_t lease={0},second={0};
    reset();unavailable();assert(reserve(&lease)==ESP_ERR_INVALID_STATE&&!lease.epoch);
    assert(reserve(NULL)==ESP_ERR_INVALID_ARG&&cancel(NULL)==ESP_ERR_INVALID_ARG&&commit(NULL,0)==ESP_ERR_INVALID_ARG);
    reset();request(0);assert(reserve(&lease)==ESP_ERR_INVALID_STATE&&!lease.epoch);expect_task(2);
    reset();assert(reserve(&lease)==ESP_OK&&lease.epoch&&reserved==lease.epoch);
    assert(reserve(&lease)==ESP_ERR_INVALID_STATE&&reserve(&second)==ESP_ERR_INVALID_STATE&&!second.epoch);
#ifndef TARGET_C3
    assert(web_reboot_abort()==ESP_ERR_INVALID_STATE);
#endif
    expect_task(1);request(0);ticks+=1000;expect_task(1);
    lease_t stale=lease;assert(cancel(&lease)==ESP_OK&&!lease.epoch);expect_task(2);
    assert(cancel(&stale)==ESP_ERR_INVALID_STATE&&commit(&stale,0)==ESP_ERR_INVALID_STATE);
    reset();assert(reserve(&lease)==ESP_OK);assert(cancel(&lease)==ESP_OK&&!pending);
    assert(reserve(&lease)==ESP_OK);assert(cancel(&stale)==ESP_ERR_INVALID_STATE&&reserved==lease.epoch);
    unsigned before=allocations;assert(commit(&lease,1000)==ESP_OK&&!lease.epoch&&pending&&allocations==before);
    ticks=deadline;expect_task(2);assert(commit(&lease,0)==ESP_ERR_INVALID_STATE);
    reset();assert(reserve(&lease)==ESP_OK);request(500);request(1);assert(commit(&lease,1000)==ESP_OK);
#ifdef TARGET_C3
    assert(deadline==600); // first ordinary request remains first
#else
    assert(deadline==101); // earliest deadline remains earliest
#endif
    ticks=deadline;expect_task(2);
    reset();ticks=UINT32_MAX-9U;assert(reserve(&lease)==ESP_OK);assert(commit(&lease,10)==ESP_OK&&deadline==0);
    ticks=0;expect_task(2);
    reset();assert(reserve(&lease)==ESP_OK);assert(commit(&lease,UINT32_MAX)==ESP_OK&&deadline==60100);
    reset();epoch_next=UINT64_MAX;assert(reserve(&lease)==ESP_ERR_INVALID_STATE&&!lease.epoch);
    // Competing admission/request races must produce either a rejected OTA,
    // or an owned lease that suppresses even an already expired reboot.
    for(unsigned i=0;i<200;++i){
        reset();raced_lease=(lease_t){0};pthread_t a,b;assert(!pthread_barrier_init(&barrier,NULL,3));
        assert(!pthread_create(&a,NULL,reserve_thread,NULL)&&!pthread_create(&b,NULL,request_thread,NULL));
        pthread_barrier_wait(&barrier);assert(!pthread_join(a,NULL)&&!pthread_join(b,NULL)&&!pthread_barrier_destroy(&barrier));
        assert(pending);
        if(reserve_result==ESP_OK){expect_task(1);assert(cancel(&raced_lease)==ESP_OK);}
        else assert(reserve_result==ESP_ERR_INVALID_STATE&&!raced_lease.epoch);
        expect_task(2);
    }
    printf("PASS reboot leases: %u scenarios; 200 real thread admission/request races, stale/duplicate tokens, pending rejection, deferred execution, commit allocation-free, tick wrap\n",cases);
#ifndef TARGET_C3
    immediate_cases();
#endif
    return 0;
}
