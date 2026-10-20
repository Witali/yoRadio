/* Host-only replacement for jmemnobs.c; no firmware/storage integration yet. */
#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jmemsys.h"
#include "probe_memory.h"
#include "probe_faults.h"
#include "probe_backing.h"
#include <assert.h>

static probe_memory_stats stats;

void probe_memory_reset(size_t limit_bytes, int allow_backing)
{
    /* Start a new measurement only after the preceding library object was freed. */
    assert(stats.current_bytes == 0);
    memset(&stats, 0, sizeof(stats));
    stats.limit_bytes = limit_bytes;
    stats.allow_backing = allow_backing;
    probe_backing_reset(&stats);
}

probe_memory_stats probe_memory_snapshot(void)
{
    /* Report library-pool allocations; stdio, row buffers and stack are separate. */
    probe_backing_snapshot(&stats);
    return stats;
}

static void *allocate(size_t size)
{
    /* Enforce the actual allocation budget, including pool alignment overhead. */
    if (probe_fault_visit(PROBE_FAULT_ALLOC)) return NULL;
    if (stats.limit_bytes && (stats.current_bytes > stats.limit_bytes ||
                             size > stats.limit_bytes - stats.current_bytes))
        return NULL;
    void *data = malloc(size);
    if (data) {
        stats.current_bytes += size;
        if (stats.current_bytes > stats.peak_bytes)
            stats.peak_bytes = stats.current_bytes;
    }
    return data;
}

static void release(void *data, size_t size)
{
    /* Use the original requested size supplied by libjpeg's pool manager. */
    assert(stats.current_bytes >= size);
    stats.current_bytes -= size;
    free(data);
}

GLOBAL(void *) jpeg_get_small(j_common_ptr cinfo, size_t size)
{
    /* Allocate one small library pool under the same hard limit. */
    (void)cinfo;
    return allocate(size);
}
GLOBAL(void *) jpeg_get_large(j_common_ptr cinfo, size_t size)
{
    /* Allocate one large virtual-array window under the same hard limit. */
    (void)cinfo;
    return allocate(size);
}
GLOBAL(void) jpeg_free_small(j_common_ptr cinfo, void *data, size_t size)
{
    /* Release a small pool during normal completion or error unwind. */
    (void)cinfo;
    release(data, size);
}
GLOBAL(void) jpeg_free_large(j_common_ptr cinfo, void *data, size_t size)
{
    /* Release a large pool during normal completion or error unwind. */
    (void)cinfo;
    release(data, size);
}
GLOBAL(size_t) jpeg_mem_available(j_common_ptr cinfo, size_t minimum,
                                 size_t maximum, size_t already_allocated)
{
    /* FIXED_TEST: measure the smallest supported virtual-array windows.
     * Later pipeline allocations and row pointers also consume the hard budget;
     * offering all remaining bytes to coefficient arrays overcommits that heap.
     * jmemsys.h explicitly permits zero to request minimum-sized windows. */
    (void)cinfo; (void)minimum; (void)already_allocated;
    if (!stats.limit_bytes) return maximum;
    return 0;
}

GLOBAL(long) jpeg_mem_init(j_common_ptr cinfo)
{
    /* Keep measurement lifetime in the harness, outside individual library calls. */
    (void)cinfo;
    return 0;
}
GLOBAL(void) jpeg_mem_term(j_common_ptr cinfo)
{
    /* Assertable cleanup is checked by the harness after jpeg_destroy. */
    (void)cinfo;
}
