#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdio.h>

typedef int esp_err_t;
typedef unsigned TickType_t;
typedef TickType_t TimeOut_t;
typedef struct {
    atomic_bool is_enabled, is_async, is_cyclic, is_running;
    struct { int desc_num; } cfg;
    struct { void *first; } head;
    void *mutex, *desc_pool;
    void **desc[1];
} dac_state;
typedef dac_state *dac_continuous_handle_t;

enum { ESP_OK, ESP_ERR_INVALID_STATE, ESP_ERR_TIMEOUT };
#define pdTRUE 1
#define portMAX_DELAY UINT32_MAX
#define pdMS_TO_TICKS(ms) ((TickType_t)(ms))
#define DAC_NULL_POINTER_CHECK(value) assert(value)
#define ESP_RETURN_ON_FALSE(value, code, ...) do { if (!(value)) return code; } while (0)
#define ESP_GOTO_ON_ERROR(expr, label, ...) do { ret = (expr); if (ret != ESP_OK) goto label; } while (0)
#define STAILQ_FIRST(head) ((head)->first)
#define STAILQ_INIT(head) ((head)->first = 0)
#define STAILQ_NEXT(desc, field) (*(desc))
#define DESC_ENTER_CRITICAL() ((void)0)
#define DESC_EXIT_CRITICAL() ((void)0)
#define xQueueReset(queue) ((void)(queue))
#define xQueueSend(queue, desc, ticks) ((void)(queue), (void)(desc), (void)(ticks))

static dac_state *current;
static unsigned ticks, starts, irq_after;
static bool locked;

static int xSemaphoreTake(void *mutex, TickType_t timeout) {
    assert(mutex && !locked);
    (void)timeout;
    locked = true;
    return pdTRUE;
}

static void xSemaphoreGive(void *mutex) {
    assert(mutex && locked);
    locked = false;
}

static void vTaskSetTimeOutState(TimeOut_t *start) { *start = ticks; }

static bool xTaskCheckForTimeOut(TimeOut_t *start, TickType_t *remaining) {
    if (*remaining == portMAX_DELAY) return false;
    TickType_t elapsed = ticks - *start;
    if (elapsed >= *remaining) return true;
    *remaining -= elapsed;
    *start = ticks;
    return false;
}

static void vTaskDelay(TickType_t delay) {
    ticks += delay;
    if (ticks == irq_after) atomic_store(&current->is_running, false);
}

static void dac_dma_periph_dma_trans_start(uint32_t descriptor) {
    assert(descriptor == 1);
    ++starts;
    /* Model a completion ISR that runs before the start call returns. */
    current->head.first = NULL;
    atomic_store(&current->is_running, false);
}

static esp_err_t s_dac_wait_to_load_dma_data(dac_continuous_handle_t handle,
        uint8_t *data, size_t size, size_t *loaded, TickType_t timeout) {
    assert(handle == current && data && size > 0 && locked);
    (void)timeout;
    handle->head.first = (void *)(uintptr_t)1;
    *loaded = 1;
    return ESP_OK;
}

#include "dac-write.inc"

int main(void) {
    dac_state driver = {.is_enabled = true, .cfg.desc_num = 1, .mutex = &driver};
    current = &driver;
    uint8_t data[2] = {1, 2};
    size_t written = 0;

    assert(dac_continuous_write(&driver, data, sizeof(data), &written, 10) == ESP_OK);
    assert(starts == 2 && written == 2 && !driver.is_running && !locked);

    atomic_store(&driver.is_running, true);
    assert(dac_continuous_write(&driver, data, 1, &written, 0) == ESP_ERR_TIMEOUT);
    assert(starts == 2 && written == 0 && ticks == 0 && !locked);
    assert(dac_continuous_write(&driver, data, 1, &written, 3) == ESP_ERR_TIMEOUT);
    assert(starts == 2 && written == 0 && ticks == 3 && driver.is_running && !locked);

    irq_after = 5;
    assert(dac_continuous_write(&driver, data, 1, &written, 4) == ESP_OK);
    assert(starts == 3 && written == 1 && ticks == 5 && !locked);

    atomic_store(&driver.is_running, true);
    irq_after = 7;
    assert(dac_continuous_write(&driver, data, 1, &written, -1) == ESP_OK);
    assert(starts == 4 && written == 1 && ticks == 7 && !locked);
    puts("PASS 5 synchronous DAC start/stop cases");
}
