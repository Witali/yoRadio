/* Independent unsigned-rate metadata fixture. No setup, DSP or audio decode. */
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "vorbis/codec.h"
#include "vorbis_xiph_alloc.h"
extern int xiph_rate_tests(void);
#ifdef NDEBUG
#error "Rate metadata tests require active assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "This metadata fixture targets ESP32"
#endif
#if configUSE_TIME_SLICING != 1
#error "The new equal-priority metadata worker requires normal time slicing"
#endif
#ifndef NATIVE_VORBIS_XIPH_RATE_API
#error "The owned rate public header must be selected"
#endif
_Static_assert(sizeof(long) * CHAR_BIT == 32, "Actual ILP32 long");
_Static_assert(_Generic(((vorbis_info *)0)->rate, unsigned long: 1, default: 0),
               "Actual public field is unsigned long");
static void worker(void *unused) {
    (void)unused;
    printf("RATE_WORKER core=%d priority=%u stack=16384\n",
           xPortGetCoreID(), (unsigned)uxTaskPriorityGet(NULL));
    printf("RATE_ABI long_bits=%u rate_bits=%u info_bytes=%u alignment=%u rate_offset=%u unsigned=1 overlay=%d\n",
           (unsigned)(sizeof(long) * CHAR_BIT),
           (unsigned)(sizeof(((vorbis_info *)0)->rate) * CHAR_BIT),
           (unsigned)sizeof(vorbis_info), (unsigned)_Alignof(vorbis_info),
           (unsigned)offsetof(vorbis_info, rate), NATIVE_VORBIS_XIPH_RATE_API);
    assert(xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
    int cases = xiph_rate_tests();
    assert(cases == XIPH_RATE_CASES && xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
    printf("RATE_PASS cases=%d live=0 bytes=0 core=%d minimum_free=%u remaining_stack=%u\n",
           cases, xPortGetCoreID(), (unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));
    printf("RATE_STOP status=PASSED\n");
    fflush(stdout);
    esp_restart();
}
void app_main(void) {
    printf("RATE_BEGIN coordinator=%d worker=1 base=%s port=%s fixture=%s expected=%d\n",
           xPortGetCoreID(), XIPH_BASE_MANIFEST_SHA256, XIPH_PORT_MANIFEST_SHA256,
           XIPH_RATE_FIXTURE_SHA256, XIPH_RATE_CASES);
    fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker, "vorbis_rate", 16384, NULL, 0, NULL, 1) == pdPASS);
}
