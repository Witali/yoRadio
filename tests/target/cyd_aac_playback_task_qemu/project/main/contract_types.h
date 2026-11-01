#pragma once
#include <stddef.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"

enum { AAC_BASE_COUNT=6, AAC_OBSERVATION_COUNT=4, AAC_REFERENCE_COUNT=10,
       AAC_MAX_RUNS=16, AAC_REFERENCE_DONE=8 };
struct entry_t {
    const char *name;
    const uint8_t *data;
    size_t bytes,hold_offset,pcm_bytes;
    uint32_t rate;
    uint8_t channels,bits;
    const char *pcm_sha;
};
struct fixture_t {
    const char *name;
    unsigned parts[2],part_count,schedule,reference;
    bool observational;
};
struct pcm_run_t {
    uint32_t rate;
    uint8_t channels,bits;
    size_t bytes;
    char sha[65];
};
struct reference_t {
    bool measured,success,drained;
    int result;
    size_t input,pcm_bytes;
    unsigned calls,frames,resizes,run_count;
    char sha[65];
    pcm_run_t runs[AAC_MAX_RUNS];
};
extern reference_t aac_references[AAC_REFERENCE_COUNT];
extern EventGroupHandle_t aac_reference_events;
void aac_public_reference_worker(void *);
