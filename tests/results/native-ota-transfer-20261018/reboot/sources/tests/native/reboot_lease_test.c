#include <assert.h>
#include <pthread.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(p) assert(!pthread_mutex_lock(p))
#define portEXIT_CRITICAL(p) assert(!pthread_mutex_unlock(p))
#define pdPASS 1
#define pdTRUE 1
#define pdMS_TO_TICKS(v) (v)
#define portMAX_DELAY UINT32_MAX
static uint32_t ticks;
static unsigned allocations,notifications,cases;
static jmp_buf task_exit;
static uint32_t xTaskGetTickCount(void) {return ticks;}
static void esp_restart(void) {longjmp(task_exit,2);}
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
int main(void) {
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
    return 0;
}
