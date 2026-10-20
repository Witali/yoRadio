#ifndef JPEG_SCRATCH_NOR_MODEL_H
#define JPEG_SCRATCH_NOR_MODEL_H
#include "jpeg_nor.h"
typedef struct {
    uint64_t calls,read_bytes,program_bytes,erases;
    uint64_t fail_at,hits;
    unsigned page_bytes,mode;
    bool allowed;
} scratch_model_stats_t;
/* Model retains physical contents between begin calls, exactly as real NOR. */
void scratch_model_pristine(void);
void scratch_model_begin(unsigned page_bytes,uint64_t fail_at,unsigned mode);
jpeg_nor_device_t scratch_model_device(void);
int scratch_model_check(void *context);
scratch_model_stats_t scratch_model_stats(void);
void scratch_model_allow(bool allowed);
bool scratch_model_canaries(void);
void scratch_model_copy_logical(void *out,uint32_t bytes);
#endif
