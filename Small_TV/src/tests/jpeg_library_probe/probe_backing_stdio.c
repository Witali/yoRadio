/* Unchanged stdio semantics, factored out of the common hard-capped allocator. */
#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jmemsys.h"
#include "probe_backing.h"
#include "probe_faults.h"
#include <assert.h>

static probe_memory_stats *stats;
static struct {backing_store_ptr owner;long size;} stores[16];

void probe_backing_reset(probe_memory_stats *current)
{
    /* A new measurement must not silently lose an open temporary file. */
    for(unsigned i=0;i<16;++i)assert(!stores[i].owner);
    stats=current;memset(stores,0,sizeof(stores));
}

void probe_backing_snapshot(probe_memory_stats *current)
{
    /* Physical NOR metrics stay zero for this independent file-backed oracle. */
    (void)current;
}

static void check_range(j_common_ptr cinfo,backing_store_ptr info,long offset,long count)
{
    /* Preserve the previous whole-request bounded temporary-file contract. */
    for(unsigned i=0;i<16;++i)
        if(stores[i].owner==info && offset>=0 && count>=0 && offset<=stores[i].size && count<=stores[i].size-offset)return;
    ERREXIT(cinfo,JERR_TFILE_SEEK);
}

static void read_store(j_common_ptr cinfo,backing_store_ptr info,void *data,long offset,long count)
{
    /* A short transfer really occurs before the fatal error unwinds. */
    check_range(cinfo,info,offset,count);
    if(probe_fault_visit(PROBE_FAULT_SEEK) || fseek(info->temp_file,offset,SEEK_SET))ERREXIT(cinfo,JERR_TFILE_SEEK);
    size_t wanted=(size_t)count,request=probe_fault_visit(PROBE_FAULT_READ)&&wanted ? wanted-1 : wanted;
    size_t received=fread(data,1,request,info->temp_file);stats->bytes_read+=received;
    if(received!=wanted)ERREXIT(cinfo,JERR_TFILE_READ);
}

static void write_store(j_common_ptr cinfo,backing_store_ptr info,void *data,long offset,long count)
{
    /* This oracle counts logical I/O, without pretending stdio is a NOR device. */
    check_range(cinfo,info,offset,count);
    if(probe_fault_visit(PROBE_FAULT_SEEK) || fseek(info->temp_file,offset,SEEK_SET))ERREXIT(cinfo,JERR_TFILE_SEEK);
    size_t wanted=(size_t)count,request=probe_fault_visit(PROBE_FAULT_WRITE)&&wanted ? wanted-1 : wanted;
    size_t written=fwrite(data,1,request,info->temp_file);stats->bytes_written+=written;
    if(written!=wanted)ERREXIT(cinfo,JERR_TFILE_WRITE);
}

static void close_store(j_common_ptr cinfo,backing_store_ptr info)
{
    /* Close on normal completion and fatal-error unwind. */
    (void)cinfo;fclose(info->temp_file);++stats->stores_closed;info->temp_file=NULL;
    for(unsigned i=0;i<16;++i)if(stores[i].owner==info)stores[i].owner=NULL;
}

GLOBAL(void) jpeg_open_backing_store(j_common_ptr cinfo,backing_store_ptr info,long size)
{
    /* Keep file-backed expected pixels independent of the new NOR implementation. */
    if(!stats->allow_backing)ERREXIT(cinfo,JERR_NO_BACKING_STORE);
    if(probe_fault_visit(PROBE_FAULT_OPEN))ERREXITS(cinfo,JERR_TFILE_CREATE,"injected");
    unsigned slot;for(slot=0;slot<16 && stores[slot].owner;++slot){}
    if(slot==16 || size<0)ERREXIT(cinfo,JERR_NO_BACKING_STORE);
    info->temp_file=tmpfile();if(!info->temp_file)ERREXITS(cinfo,JERR_TFILE_CREATE,"probe");
    stores[slot].owner=info;stores[slot].size=size;
    info->read_backing_store=read_store;info->write_backing_store=write_store;info->close_backing_store=close_store;
    ++stats->stores_opened;stats->backing_capacity+=(unsigned long long)size;
}
