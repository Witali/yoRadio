/* Real public-capability allocations and aligned volatile32 accesses only.
 * This minimal program does not qualify full application memory headroom.
 */
#include <assert.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include "esp_heap_caps.h"
#include "esp_memory_utils.h"
#include "esp_system.h"
#include "esp_task_wdt.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "soc/soc.h"
#include "pcm_word_plane.h"

#ifdef NDEBUG
#error "Public-capability access probe requires assertions"
#endif

enum { PLANE_BYTES=11520, PLANE_SAMPLES=5760, PLANE_COUNT=8, DRAM_BYTES=23040 };
typedef struct {size_t free8,large8,free32,large32,free_exec,large_exec;} caps_snapshot;

static void require(bool value,const char *reason) {
    if(!value){printf("CYD_WORD_FAILURE %s\n",reason);fflush(stdout);assert(value);}
}

/* Separate named, noinline entrypoints permit exact linked-object inspection.
 * Only these functions touch the caller's word-only storage.
 */
__attribute__((noinline)) void probe_word_clear(volatile uint32_t *words,size_t count) {
    pcm_word_plane_clear(words,count);
}
__attribute__((noinline)) void probe_word_store(volatile uint32_t *words,size_t sample,uint16_t bits) {
    pcm_word_plane_store(words,sample,bits);
}
__attribute__((noinline)) uint16_t probe_word_load(const volatile uint32_t *words,size_t sample) {
    return pcm_word_plane_load(words,sample);
}

static caps_snapshot resources(const char *kind,const char *phase,unsigned slot) {
    caps_snapshot result={
        heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
        heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT),
        heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT),
        heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT),
        heap_caps_get_free_size(MALLOC_CAP_INTERNAL|MALLOC_CAP_EXEC|MALLOC_CAP_32BIT),
        heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL|MALLOC_CAP_EXEC|MALLOC_CAP_32BIT)};
    printf("CYD_WORD_HEAP kind=%s phase=%s slot=%u free8=%u largest8=%u free32=%u largest32=%u free_exec=%u largest_exec=%u integrity=%u\n",
        kind,phase,slot,(unsigned)result.free8,(unsigned)result.large8,(unsigned)result.free32,(unsigned)result.large32,
        (unsigned)result.free_exec,(unsigned)result.large_exec,(unsigned)heap_caps_check_integrity_all(true));
    return result;
}

static void classify(const char *kind,unsigned slot,const void *pointer,size_t bytes,uint32_t caps) {
    uintptr_t first=(uintptr_t)pointer,last=first+bytes-4u;
    bool diram_i=esp_ptr_in_diram_iram(pointer) && esp_ptr_in_diram_iram((const void *)last);
    bool diram_d=esp_ptr_in_diram_dram(pointer) && esp_ptr_in_diram_dram((const void *)last);
    uintptr_t alias_first=0,alias_last=0;
    if(diram_i){alias_first=(uintptr_t)esp_ptr_diram_iram_to_dram(pointer);alias_last=(uintptr_t)esp_ptr_diram_iram_to_dram((const void *)last);}
    if(diram_d){alias_first=(uintptr_t)esp_ptr_diram_dram_to_iram(pointer);alias_last=(uintptr_t)esp_ptr_diram_dram_to_iram((const void *)last);}
    bool pure=first>=SOC_IRAM_LOW && first+bytes<=SOC_DIRAM_IRAM_LOW;
    require(pointer && !(first&3u) && esp_ptr_internal(pointer),"actual_aligned_internal_pointer");
    /* Keep the public address-query result separate from requested heap caps.
     * The allocator can return a D/IRAM instruction alias beyond SOC_IRAM_HIGH;
     * esp_ptr_executable checks narrower fixed address windows in SDK6.0.2.
     * This probe executes no allocated code: it verifies integer word access.
     */
    require(pure || diram_i || diram_d || esp_ptr_in_dram(pointer),"public_word_storage_region");
    if(caps&MALLOC_CAP_8BIT)require(esp_ptr_byte_accessible(pointer) && esp_ptr_in_dram(pointer),"control_scratch_remains_DRAM");
    printf("CYD_WORD_POINTER kind=%s slot=%u caps=%u pointer=%" PRIuPTR " bytes=%u internal=%u byte_accessible=%u executable=%u in_dram=%u in_iram=%u diram_dram=%u diram_iram=%u pure_iram=%u alias_first_word=%" PRIuPTR " alias_last_word=%" PRIuPTR " alias_dereferenced=0\n",
        kind,slot,(unsigned)caps,first,(unsigned)bytes,(unsigned)esp_ptr_internal(pointer),(unsigned)esp_ptr_byte_accessible(pointer),
        (unsigned)esp_ptr_executable(pointer),(unsigned)esp_ptr_in_dram(pointer),(unsigned)esp_ptr_in_iram(pointer),
        (unsigned)diram_d,(unsigned)diram_i,(unsigned)pure,alias_first,alias_last);
}

static uint16_t expected(unsigned plane,size_t sample) {
    return (uint16_t)(UINT32_C(0x8000)^(plane*7919u+(uint32_t)sample*97u));
}

static void access_plane(volatile uint32_t *plane,unsigned slot) {
    probe_word_clear(plane,PLANE_BYTES/4u);
    for(size_t sample=0;sample<PLANE_SAMPLES;++sample)require(probe_word_load(plane,sample)==0,"clear_all_real_word_storage");
    for(size_t sample=0;sample<PLANE_SAMPLES;++sample)probe_word_store(plane,sample,expected(slot,sample));
    for(size_t sample=PLANE_SAMPLES;sample--;)require(probe_word_load(plane,sample)==expected(slot,sample),"every_original_integer_bit_pattern");
    probe_word_store(plane,1,UINT16_C(0x8000));probe_word_store(plane,PLANE_SAMPLES-1,UINT16_C(0x7fff));
    require(probe_word_load(plane,0)==expected(slot,0) && probe_word_load(plane,1)==UINT16_C(0x8000) &&
        probe_word_load(plane,PLANE_SAMPLES-2)==expected(slot,PLANE_SAMPLES-2) && probe_word_load(plane,PLANE_SAMPLES-1)==UINT16_C(0x7fff),
        "odd_half_read_modify_write_preserves_neighbors");
}

static bool same(caps_snapshot a,caps_snapshot b) {
    return a.free8==b.free8 && a.large8==b.large8 && a.free32==b.free32 && a.large32==b.large32 &&
        a.free_exec==b.free_exec && a.large_exec==b.large_exec;
}

static void run_case(const char *kind,uint32_t caps) {
    caps_snapshot before=resources(kind,"BEFORE",0);
    void *scratch=heap_caps_malloc(DRAM_BYTES,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
    require(scratch!=NULL,"separate_byte_capable_control_allocation");
    classify("DRAM_CONTROL",0,scratch,DRAM_BYTES,MALLOC_CAP_INTERNAL|MALLOC_CAP_8BIT);
    resources(kind,"SCRATCH",0);
    volatile uint32_t *planes[PLANE_COUNT]={0};unsigned allocated=0,attempted=0,refused=0;
    for(unsigned slot=0;slot<PLANE_COUNT;++slot) {
        resources(kind,"ALLOC_BEFORE",slot);++attempted;
        planes[slot]=heap_caps_malloc(PLANE_BYTES,caps);
        printf("CYD_WORD_ALLOC kind=%s slot=%u bytes=%u caps=%u pointer=%" PRIuPTR " success=%u\n",kind,slot,PLANE_BYTES,(unsigned)caps,(uintptr_t)planes[slot],(unsigned)(planes[slot]!=NULL));
        resources(kind,"ALLOC_AFTER",slot);
        if(!planes[slot]){++refused;break;}
        ++allocated;classify(kind,slot,(const void *)(uintptr_t)planes[slot],PLANE_BYTES,caps);
        access_plane(planes[slot],slot);
        printf("CYD_WORD_ACCESS kind=%s slot=%u samples=%u clear=1 whole_pattern=1 odd_rmw=1 volatile32_only=1\n",kind,slot,PLANE_SAMPLES);
        vTaskDelay(1);
    }
    resources(kind,"HELD",0);
    for(unsigned slot=0;slot<allocated;++slot) {
        uintptr_t pointer=(uintptr_t)planes[slot];heap_caps_free((void *)pointer);
        printf("CYD_WORD_FREE kind=%s slot=%u pointer=%" PRIuPTR " real_returned=1\n",kind,slot,pointer);
    }
    heap_caps_free(scratch);
    caps_snapshot after=resources(kind,"CLEANUP",0);
    require(allocated>0 && same(before,after),"real_word_access_and_exact_caps_cleanup");
    printf("CYD_WORD_CASE kind=%s attempted=%u allocated=%u refused=%u bytes_per_plane=%u byte_control=%u exact_cleanup=1 extra_RAM_inferred=0 application_qualified=0\n",
        kind,attempted,allocated,refused,PLANE_BYTES,DRAM_BYTES);
}

void app_main(void) {
    printf("CYD_WORD_BOOT sdk=%s public_caps=1 physical_hardware=0 decoder=0 private_heap=0\n",esp_get_idf_version());
    vTaskDelay(pdMS_TO_TICKS(20));
    require(esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(0))==ESP_OK && esp_task_wdt_status(xTaskGetIdleTaskHandleForCore(1))==ESP_OK,"both_real_idle_watchdogs");
    printf("CYD_WORD_LIMITS iram_low=%u pure_iram_high=%u iram_high=%u diram_iram_low=%u diram_iram_high=%u diram_dram_low=%u diram_dram_high=%u dram_low=%u dram_high=%u cap_internal=%u cap32=%u cap8=%u cap_exec=%u\n",
        SOC_IRAM_LOW,SOC_DIRAM_IRAM_LOW,SOC_IRAM_HIGH,SOC_DIRAM_IRAM_LOW,SOC_DIRAM_IRAM_HIGH,SOC_DIRAM_DRAM_LOW,SOC_DIRAM_DRAM_HIGH,SOC_DRAM_LOW,SOC_DRAM_HIGH,
        MALLOC_CAP_INTERNAL,MALLOC_CAP_32BIT,MALLOC_CAP_8BIT,MALLOC_CAP_EXEC);
    run_case("WORDS32",MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT);
    run_case("EXEC32",MALLOC_CAP_INTERNAL|MALLOC_CAP_32BIT|MALLOC_CAP_EXEC);
    require(heap_caps_check_integrity_all(true),"final_public_heap_integrity");
    printf("CYD_WORD_COMPLETE cases=2 word_plane_bytes=%u plane_slots=8 diagnostic_yield_between_planes=1 all_planes_byte_or_FP_access=0 hardware=0 application_memory_qualified=0 integrity=1\n",PLANE_BYTES);
    require(fflush(stdout)==0,"complete_console_flush");esp_restart();
}
