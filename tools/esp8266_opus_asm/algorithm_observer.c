/* Host-only event trace. Never link this I/O or state into firmware. */
#include <stdio.h>
#include <stdlib.h>
#include "opus_memory.h"
void research_event(int type,int a,int b,int c,int d) {
    static FILE *output;
    if (!output) {
        const char *name=getenv("YORADIO_ALGORITHM_TRACE");
        if (!name || !(output=fopen(name,"w"))) abort();
    }
    if (fprintf(output,"%d,%d,%d,%d,%d\n",type,a,b,c,d)<0) abort();
}
extern void *__real_yoradio_opus_scratch_alloc(size_t,size_t,int);
void *__wrap_yoradio_opus_scratch_alloc(size_t count,size_t size,int word_safe) {
    void *result=__real_yoradio_opus_scratch_alloc(count,size,word_safe);
    opus_scratch_mark mark=yoradio_opus_scratch_mark();
    research_event(7,(int)count,(int)size,(int)mark.words,(int)mark.bytes);
    return result;
}
