/* Diagnostic-only byte/string accesses through both classic ESP32 cores.
 * A separate RTC buffer exercises the data bus, not private application state.
 * Application cache placement and heap deltas are checked from the saved ELF
 * and full-application runs. QEMU cannot establish physical access timings. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_attr.h"
#include "esp_memory_utils.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "websocket_service.h"

static RTC_SLOW_ATTR uint8_t s_probe[64];
#ifdef NDEBUG
#error "RTC access probe requires enabled assertions"
#endif

static SemaphoreHandle_t s_done;

static void exercise(void *argument) {
    int core = (int)(intptr_t)argument;
    assert(xPortGetCoreID() == core);
    volatile uint8_t *bytes = s_probe;
    assert(esp_ptr_in_rtc_slow(s_probe) && esp_ptr_in_rtc_slow(s_probe + sizeof(s_probe) - 1));
    for (unsigned phase = 0; phase < 256; ++phase) {
        for (unsigned i = 0; i < sizeof(s_probe); ++i) bytes[i] = (uint8_t)(phase + i);
        for (unsigned i = 0; i < sizeof(s_probe); ++i) assert(bytes[i] == (uint8_t)(phase + i));
        uint8_t copy[63];
        memcpy(copy, s_probe + 1, sizeof(copy));
        for (unsigned i = 0; i < sizeof(copy); ++i) assert(copy[i] == (uint8_t)(phase + i + 1));
        memmove(s_probe + 3, s_probe + 1, 60);
        for (unsigned i = 3; i < 63; ++i) assert(bytes[i] == (uint8_t)(phase + i - 2));
        memset(s_probe + 1, 'x', 61);
        bytes[0] = 'a'; bytes[62] = 'z'; bytes[63] = 0;
        assert(strlen((const char *)s_probe) == 63 && s_probe[1] == 'x' && s_probe[61] == 'x');
        if (!(phase & 15U)) vTaskDelay(1);
    }
    printf("CYD_RTC_ACCESS core=%d phases=256 bytes=64 PASS\n", core);
    BaseType_t given = xSemaphoreGive(s_done);
    assert(given == pdTRUE);
    vTaskDelete(NULL);
}

esp_err_t __real_websocket_service_start(void);

esp_err_t __wrap_websocket_service_start(void) {
    s_done = xSemaphoreCreateBinary();
    assert(s_done);
    for (int core = 0; core < 2; ++core) {
        BaseType_t created = xTaskCreatePinnedToCore(exercise, "rtc_access", 3072,
                                                   (void *)(intptr_t)core, 2, NULL, core);
        assert(created == pdPASS);
        BaseType_t taken = xSemaphoreTake(s_done, pdMS_TO_TICKS(5000));
        assert(taken == pdTRUE);
    }
    // Let idle reap the completed temporary tasks before the radio test.
    vTaskDelay(pdMS_TO_TICKS(20));
    vSemaphoreDelete(s_done);
    s_done = NULL;
    return __real_websocket_service_start();
}
