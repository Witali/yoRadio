#pragma once
#include "aac_sbr_abi.h"
#include <assert.h>
#include <string.h>

enum { AAC_SMOOTHING_TABLES=4, AAC_SMOOTHING_PAST_ROWS=AAC_SBR_ROWS-1 };
typedef struct {
    int32_t current[AAC_SMOOTHING_TABLES][AAC_SBR_BANDS];
} aac_smoothing_scratch_t;

// The fifth pointer is a free slot, never retained history. Native FIR code
// rotates all five pointers; reconnect any surviving stack row before return.
static inline void aac_smoothing_begin(int32_t **tables[AAC_SMOOTHING_TABLES],
                                      aac_smoothing_scratch_t *scratch) {
    memset(scratch,0,sizeof(*scratch));
    for(unsigned t=0;t<AAC_SMOOTHING_TABLES;++t) {
        assert(!tables[t][AAC_SMOOTHING_PAST_ROWS]);
        for(unsigned row=0;row<AAC_SMOOTHING_PAST_ROWS;++row)assert(tables[t][row]);
        tables[t][AAC_SMOOTHING_PAST_ROWS]=scratch->current[t];
    }
}
static inline void aac_smoothing_end(int32_t **tables[AAC_SMOOTHING_TABLES],
                                    aac_smoothing_scratch_t *scratch) {
    for(unsigned t=0;t<AAC_SMOOTHING_TABLES;++t) {
        int32_t *spare=tables[t][AAC_SMOOTHING_PAST_ROWS];
        unsigned found=0;
        for(unsigned row=0;row<AAC_SMOOTHING_PAST_ROWS;++row) {
            if(tables[t][row]==scratch->current[t]) {
                assert(spare!=scratch->current[t]);
                memcpy(spare,scratch->current[t],sizeof(scratch->current[t]));
                tables[t][row]=spare;++found;
            }
        }
        assert(found==(spare!=scratch->current[t]));
        tables[t][AAC_SMOOTHING_PAST_ROWS]=NULL;
    }
}
