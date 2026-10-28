// Isolated public arithmetic fixture; no production task or backend changes.
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_heap_caps.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "corpus.h"

#ifdef NDEBUG
#error "Native arithmetic qualification requires assertions"
#endif
#if CONFIG_IDF_TARGET_ESP32
enum { BFQ_WORKER_CORE = 1 };
#define BFQ_TARGET "esp32"
#elif CONFIG_IDF_TARGET_ESP32C3
enum { BFQ_WORKER_CORE = 0 };
#define BFQ_TARGET "esp32c3"
#else
#error "Unsupported native arithmetic target"
#endif

static uint64_t bfq_completed_flushes;
static __attribute__((noinline)) int bfq_record_flush(FILE *stream) {
    int result = fflush(stream);
    if (!result) {
        assert(xPortGetCoreID() == BFQ_WORKER_CORE && uxTaskPriorityGet(NULL) == 3);
        ++bfq_completed_flushes;
        // Existing fixture flushes only completed BFBEGIN/BFROW/BFOOM records.
        // A long arithmetic operation has no inserted yield or WDT reset.
        vTaskDelay(1);
    }
    return result;
}

// Include original bytes after stdio's declaration; redirect only its fflush.
#define fflush bfq_record_flush
#include "vorbis_bigfloat_host.c"
#undef fflush

_Static_assert(sizeof(void *) == 4 && LIMB_BITS == 32 && sizeof(limb_t) == 4,
               "Actual native pointer and limb ABI must be32bit");

static int bfq_idle1(void) {
#if CONFIG_IDF_TARGET_ESP32
    return esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1));
#else
    return -1;
#endif
}
static void bfq_metadata(const char *stage, int status) {
    int idle0 = esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0));
    int idle1 = bfq_idle1();
    assert(idle0 == 0 && idle1 == (BFQ_WORKER_CORE ? 0 : -1));
    assert(heap_caps_check_integrity_all(true));
    printf("BFQ_%s status=%d core=%d priority=%u stack=16384 flushes=%" PRIu64
           " stack_free=%u heap_free=%u heap_min=%u largest=%u idle0=%d idle1=%d heap_integrity=1\n",
           stage, status, xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL), bfq_completed_flushes,
           (unsigned)uxTaskGetStackHighWaterMark(NULL), (unsigned)esp_get_free_heap_size(),
           (unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT), idle0, idle1);
    assert(fflush(stdout) == 0);
}
static void bfq_worker(void *unused) {
    (void)unused;
    bfq_metadata("WORKER", 0);
    int status = native_vorbis_bigfloat_fixture_run((const char *)bfq_input, sizeof(bfq_input));
    assert(fflush(stdout) == 0);
    assert(status == 0 && xPortGetCoreID() == BFQ_WORKER_CORE);
    bfq_metadata("COMPLETE", status);
    printf("BFQ_STOP status=CAPTURED\n");
    assert(fflush(stdout) == 0);
    esp_restart();
}
void app_main(void) {
    assert(xPortGetCoreID() == 0);
    printf("BFQ_BEGIN target=%s cases=%u data=%s fixture=%s coordinator=0 worker=%d\n",
           BFQ_TARGET, BFQ_CASES, BFQ_INPUT_SHA256, BFQ_FIXTURE_SHA256, BFQ_WORKER_CORE);
    assert(fflush(stdout) == 0);
    assert(xTaskCreatePinnedToCore(bfq_worker, "vorbisbigfloat", 16384, NULL, 3, NULL, BFQ_WORKER_CORE) == pdPASS);
}
