/* Host-only replacement for jmemnobs.c; no firmware/storage integration yet. */
#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jmemsys.h"
#include "probe_memory.h"
#include <assert.h>

static probe_memory_stats stats;
static struct { backing_store_ptr owner; long size; } stores[16];

void probe_memory_reset(size_t limit_bytes, int allow_backing)
{
    /* Start a new measurement only after the preceding library object was freed. */
    assert(stats.current_bytes == 0);
    memset(&stats, 0, sizeof(stats));
    memset(stores, 0, sizeof(stores));
    stats.limit_bytes = limit_bytes;
    stats.allow_backing = allow_backing;
}

probe_memory_stats probe_memory_snapshot(void)
{
    /* Report library-pool allocations; stdio, row buffers and stack are separate. */
    return stats;
}

static void *allocate(size_t size)
{
    /* Enforce the actual allocation budget, including pool alignment overhead. */
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

static void check_range(j_common_ptr cinfo, backing_store_ptr info, long offset, long count)
{
    /* Check every temporary I/O against the capacity requested by libjpeg. */
    for (unsigned i = 0; i < 16; ++i) {
        if (stores[i].owner == info && offset >= 0 && count >= 0 &&
            offset <= stores[i].size && count <= stores[i].size - offset)
            return;
    }
    ERREXIT(cinfo, JERR_TFILE_SEEK);
}
static void read_store(j_common_ptr cinfo, backing_store_ptr info, void *data,
                       long offset, long count)
{
    /* Read only initialized virtual-array bytes through the host temporary file. */
    check_range(cinfo, info, offset, count);
    if (fseek(info->temp_file, offset, SEEK_SET) ||
        fread(data, 1, (size_t)count, info->temp_file) != (size_t)count)
        ERREXIT(cinfo, JERR_TFILE_READ);
    stats.bytes_read += (unsigned long long)count;
}
static void write_store(j_common_ptr cinfo, backing_store_ptr info, void *data,
                        long offset, long count)
{
    /* Count actual logical writes; this is not a NOR erase/wear simulation. */
    check_range(cinfo, info, offset, count);
    if (fseek(info->temp_file, offset, SEEK_SET) ||
        fwrite(data, 1, (size_t)count, info->temp_file) != (size_t)count)
        ERREXIT(cinfo, JERR_TFILE_WRITE);
    stats.bytes_written += (unsigned long long)count;
}
static void close_store(j_common_ptr cinfo, backing_store_ptr info)
{
    /* Close and remove the anonymous host file on success and on decode errors. */
    (void)cinfo;
    fclose(info->temp_file);
    stats.stores_closed++;
    info->temp_file = NULL;
    for (unsigned i = 0; i < 16; ++i)
        if (stores[i].owner == info) stores[i].owner = NULL;
}
GLOBAL(void) jpeg_open_backing_store(j_common_ptr cinfo, backing_store_ptr info, long size)
{
    /* Model optional backing storage without pretending that C2 already has it. */
    if (!stats.allow_backing) ERREXIT(cinfo, JERR_NO_BACKING_STORE);
    unsigned slot;
    for (slot = 0; slot < 16 && stores[slot].owner; ++slot) {}
    if (slot == 16 || size < 0) ERREXIT(cinfo, JERR_NO_BACKING_STORE);
    info->temp_file = tmpfile();
    if (!info->temp_file) ERREXITS(cinfo, JERR_TFILE_CREATE, "probe");
    stores[slot].owner = info; stores[slot].size = size;
    info->read_backing_store = read_store;
    info->write_backing_store = write_store;
    info->close_backing_store = close_store;
    stats.stores_opened++;
    stats.backing_capacity += (unsigned long long)size;
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
