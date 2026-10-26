/* Independent metadata API tests; no decoder, synthesis or DSP calls. */
#include <assert.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "vorbis_xiph_alloc.h"
extern int xiph_comment_tests(void);
#ifdef NDEBUG
#error "Metadata tests require active assertions"
#endif
#if !CONFIG_IDF_TARGET_ESP32
#error "This metadata fixture targets ESP32"
#endif
static void worker(void *unused){
    (void)unused;
    printf("COMMENTS_WORKER core=%d priority=%u stack=16384\n",xPortGetCoreID(),(unsigned)uxTaskPriorityGet(NULL));
    assert(xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    int cases=xiph_comment_tests();
    assert(cases==XIPH_COMMENT_CASES && xiph_port_test_live()==0 && xiph_port_test_bytes()==0);
    printf("COMMENTS_PASS cases=%d live=0 bytes=0 core=%d minimum_free=%u remaining_stack=%u\n",
           cases,xPortGetCoreID(),(unsigned)esp_get_minimum_free_heap_size(),
           (unsigned)uxTaskGetStackHighWaterMark(NULL));
    printf("COMMENTS_STOP status=PASSED\n");fflush(stdout);esp_restart();
}
void app_main(void){
    printf("COMMENTS_BEGIN coordinator=%d worker=1 base=%s port=%s fixture=%s expected=%d\n",
           xPortGetCoreID(),XIPH_BASE_MANIFEST_SHA256,XIPH_PORT_MANIFEST_SHA256,
           XIPH_COMMENT_FIXTURE_SHA256,XIPH_COMMENT_CASES);fflush(stdout);
    assert(xTaskCreatePinnedToCore(worker,"vorbis_comments",16384,NULL,3,NULL,1)==pdPASS);
}
