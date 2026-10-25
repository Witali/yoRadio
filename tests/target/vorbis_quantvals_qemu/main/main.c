// Arithmetic-only target test. The entire canonical setup and native ABI
// assertions compile; only the existing static quantvals helper is called.
#include <inttypes.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "cases.h"

#ifndef QUANTVALS_SETUP_FILE
#error "The frozen canonical setup source must be selected explicitly"
#endif
#ifndef QUANTVALS_CASES_SHA256
#error "The frozen independent cases JSON must be bound"
#endif
#include QUANTVALS_SETUP_FILE

#if CONFIG_IDF_TARGET_ESP32
enum { worker_core = 1 };
#elif CONFIG_IDF_TARGET_ESP32C3
enum { worker_core = 0 };
#else
#error "Unsupported quantvals target"
#endif

// A volatile function pointer preserves an actual call to the canonical
// static helper instead of allowing whole-fixture constant folding.
static long (*volatile quantvals_function)(codebook *) =
    _book_maptype1_quantvals;

static void stop(const char *status) {
    printf("QUANTVALS_STOP status=%s\n", status);
    fflush(stdout);
    esp_restart();
}

static void worker(void *unused) {
    (void)unused;
    printf("QUANTVALS_WORKER core=%d priority=%u stack=16384\n",
           xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    for (uint32_t i = 0; i < QUANTVALS_CASE_COUNT; ++i) {
        const quantvals_case_t *test = &quantvals_cases[i];
        codebook book = {0};
        book.entries = (long)test->entries;
        book.dim = (long)test->dimensions;
        long actual = quantvals_function(&book);
        printf("QUANTVALS_CASE index=%" PRIu32 " entries=%" PRIu32
               " dimensions=%" PRIu32 " expected=%" PRIu32
               " actual=%ld core=%d\n",
               i, test->entries, test->dimensions, test->expected, actual,
               xPortGetCoreID());
        if (actual != (long)test->expected || xPortGetCoreID() != worker_core) {
            stop("FAIL");
        }
        if ((i & 63U) == 63U) vTaskDelay(1);
    }
    printf("QUANTVALS_COMPLETE cases=%u core=%d\n",
           (unsigned)QUANTVALS_CASE_COUNT, xPortGetCoreID());
    stop("PASS");
}

void app_main(void) {
    printf("QUANTVALS_BEGIN cases=%u coordinator=%d worker=%d data=%s\n",
           (unsigned)QUANTVALS_CASE_COUNT, xPortGetCoreID(), worker_core,
           QUANTVALS_CASES_SHA256);
    fflush(stdout);
    if (xTaskCreatePinnedToCore(worker, "quantvals", 16384, NULL, 3, NULL,
                                worker_core) != pdPASS) {
        stop("TASK_CREATE_FAILED");
    }
}
