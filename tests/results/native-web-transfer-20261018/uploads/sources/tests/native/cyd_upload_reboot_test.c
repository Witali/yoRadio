#include <assert.h>
#include <limits.h>
#include <pthread.h>
#include <setjmp.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef int esp_err_t;
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
typedef pthread_mutex_t portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED PTHREAD_MUTEX_INITIALIZER
#define portENTER_CRITICAL(lock) assert(!pthread_mutex_lock(lock))
#define portEXIT_CRITICAL(lock) assert(!pthread_mutex_unlock(lock))
#define ESP_OK 0
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_INVALID_STATE 0x103
#define pdPASS 1
#define pdTRUE 1
#define pdMS_TO_TICKS(ms) (ms)
#define portMAX_DELAY UINT32_MAX
static uint32_t ticks;
static unsigned creates, deletes, notifications, waits, restarts, scenarios;
static bool fail_create;
static void (*created_entry)(void *);
static jmp_buf restart_exit;
static unsigned injected_request;
static uint32_t inject_at;
static bool inject_when_waiting;
static unsigned xTaskGetTickCount(void) {return ticks;}
static int xTaskCreate(void (*entry)(void *), const char *name, unsigned stack,
                       void *argument, unsigned priority, TaskHandle_t *task) {
    assert(!strcmp(name, "web_reboot") && stack == 2048 && !argument && priority == 2);
    ++creates;
    if (fail_create) return 0;
    created_entry = entry; *task = (TaskHandle_t)(uintptr_t)1; return pdPASS;
}
static void vTaskDelete(TaskHandle_t task) {assert(task == (TaskHandle_t)(uintptr_t)1); ++deletes;}
static void xTaskNotifyGive(TaskHandle_t task) {assert(task == (TaskHandle_t)(uintptr_t)1); ++notifications;}
static unsigned ulTaskNotifyTake(int clear, TickType_t wait);
static void esp_restart(void) {++restarts; longjmp(restart_exit, 1);}
#include "cyd-reboot-production.inc"
static unsigned ulTaskNotifyTake(int clear, TickType_t wait) {
    assert(clear == pdTRUE); ++waits;
    if (inject_when_waiting) {
        assert(wait == portMAX_DELAY || inject_at <= wait);
        ticks += inject_at; inject_when_waiting = false;
        web_reboot_request(injected_request);
        return 1;
    }
    assert(wait != portMAX_DELAY); ticks += wait; return 0;
}
static void reset(void) {
    // Tests isolate a process-lifetime service after a mocked noreturn restart.
    s_task = NULL; atomic_store(&s_ready, false); s_pending = false; s_deadline = 0;
    fail_create = false; injected_request = 0; inject_at = 0; inject_when_waiting = false;
    ++scenarios;
}
static void execute(uint32_t expected_tick) {
    unsigned before_creates = creates, before_restarts = restarts;
    if (!setjmp(restart_exit)) created_entry(NULL);
    assert(restarts == before_restarts + 1U && ticks == expected_tick && creates == before_creates);
}
int main(void) {
    reset(); assert(!web_reboot_ready()); web_reboot_request(750); assert(!notifications && !s_pending);
    fail_create = true; assert(web_reboot_start() == ESP_ERR_NO_MEM && !web_reboot_ready());
    assert(web_reboot_abort() == ESP_OK && !deletes);
    fail_create = false; assert(web_reboot_start() == ESP_OK && web_reboot_ready());
    unsigned allocated = creates; assert(web_reboot_start() == ESP_OK && creates == allocated);
    assert(web_reboot_abort() == ESP_OK && deletes == 1 && !web_reboot_ready());
    assert(web_reboot_abort() == ESP_OK && deletes == 1);

    reset(); ticks = 100; assert(web_reboot_start() == ESP_OK); web_reboot_request(750);
    assert(s_pending && s_deadline == 850 && web_reboot_abort() == ESP_ERR_INVALID_STATE);
    ticks = 200; web_reboot_request(1000); assert(s_deadline == 850);
    web_reboot_request(300); assert(s_deadline == 500); execute(500);

    reset(); ticks = UINT32_MAX - 749U; assert(web_reboot_start() == ESP_OK);
    web_reboot_request(750); assert(s_pending && s_deadline == 0); execute(0);
    reset(); ticks = UINT32_MAX - 99U; assert(web_reboot_start() == ESP_OK);
    web_reboot_request(750); ticks += 100; web_reboot_request(50); execute(50);
    reset(); ticks = 123; assert(web_reboot_start() == ESP_OK); web_reboot_request(0); execute(123);
    reset(); ticks = 123; assert(web_reboot_start() == ESP_OK); web_reboot_request(UINT_MAX); execute(60123);
    reset(); ticks = 123; assert(web_reboot_start() == ESP_OK); web_reboot_request(1); ticks = 126; execute(126);

    reset(); ticks = 10; assert(web_reboot_start() == ESP_OK);
    inject_when_waiting = true; inject_at = 20; injected_request = 750; execute(780);
    reset(); ticks = 10; assert(web_reboot_start() == ESP_OK); web_reboot_request(750);
    inject_when_waiting = true; inject_at = 100; injected_request = 200; execute(310);
    reset(); ticks = 10; assert(web_reboot_start() == ESP_OK); web_reboot_request(750);
    inject_when_waiting = true; inject_at = 100; injected_request = 1000; execute(760);
    assert(notifications >= 13 && waits >= 8);
    printf("PASS CYD reboot: %u scenarios, checked 2048-byte unpinned task, OOM/retry/startup abort, allocation-free notifications, earliest deadline, exact zero/wrap, idle wake and response-independent scheduling\n", scenarios);
    return 0;
}
