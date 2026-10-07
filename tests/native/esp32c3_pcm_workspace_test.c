#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
static bool fail;
static unsigned calls;
static void *fault_realloc(void *p, size_t n) {
    ++calls;
    return fail ? NULL : realloc(p, n);
}
#define realloc fault_realloc
#include "decoder_pcm.h"
#undef realloc

int main(void) {
    uint8_t *p = NULL;
    size_t capacity = 0;
    fail = true;
    assert(!decoder_pcm_prepare(&p, &capacity, true) && !p && !capacity);
    fail = false;
    assert(decoder_pcm_prepare(&p, &capacity, true) && capacity == 8192);
    memset(p, 0xa5, capacity);
    unsigned before = calls;
    assert(decoder_pcm_prepare(&p, &capacity, true) && calls == before);
    fail = true;
    uint8_t *old = p;
    assert(!decoder_pcm_prepare(&p, &capacity, false));
    assert(p == old && capacity == 8192);
    for (size_t i=0; i<capacity; ++i) assert(p[i] == 0xa5);
    fail = false;
    assert(decoder_pcm_prepare(&p, &capacity, false) && capacity == 12288);
    assert(decoder_pcm_resize(&p, &capacity, 20000) && capacity == 20000);
    before = calls;
    assert(decoder_pcm_prepare(&p, &capacity, false) && calls == before);
    fail = true;
    old = p;
    assert(!decoder_pcm_prepare(&p, &capacity, true));
    assert(p == old && capacity == 20000);
    fail = false;
    assert(decoder_pcm_prepare(&p, &capacity, true) && capacity == 8192);
    for (size_t i=0; i<capacity; ++i) assert(p[i] == 0xa5);
    assert(!decoder_pcm_resize(&p, &capacity, 0) && capacity == 8192);
    free(p);
    puts("PASS: AAC/other-codec PCM transitions, retained capacity, shrink, grow and OOM preservation");
}
