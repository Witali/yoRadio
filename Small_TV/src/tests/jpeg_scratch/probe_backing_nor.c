/* Host libjpeg jmemsys binding to actual shared-subfile/NOR code, not stdio. */
#define JPEG_INTERNALS
#include "jinclude.h"
#include "jpeglib.h"
#include "jmemsys.h"
#include "probe_backing.h"
#include "probe_faults.h"
#include "jpeg_scratch.h"
#include "nor_model.h"
#include "scratch_fixture.h"
#include <assert.h>
#define REQUIRE(v) do{if(!(v)){fprintf(stderr,"NOR BACKING FAIL %s:%d: %s\n",__FILE__,__LINE__,#v);exit(2);}}while(0)

static probe_memory_stats *stats;
static jpeg_nor_t nor;
static jpeg_scratch_t scratch;
static struct {backing_store_ptr owner;jpeg_scratch_file_t file;long bytes;} files[16];
static bool model_started;

void probe_backing_reset(probe_memory_stats *current)
{
    /* The model retains physical bytes; reset accounting only for a new harness run. */
    for(unsigned i=0;i<16;++i)REQUIRE(!files[i].owner);
    jpeg_scratch_abort(&scratch);stats=current;model_started=false;memset(files,0,sizeof(files));
}

void probe_backing_snapshot(probe_memory_stats *current)
{
    /* Snapshot after abort/destroy also releases an unregistered failed-open handle. */
    if(!model_started)return;
    scratch_model_stats_t physical=scratch_model_stats();
    current->nor_calls=physical.calls;current->nor_read_bytes=physical.read_bytes;
    current->nor_program_bytes=physical.program_bytes;current->nor_erases=physical.erases;current->nor_fault_hits=physical.hits;
    if(scratch.peak_bytes>current->scratch_peak_bytes)current->scratch_peak_bytes=scratch.peak_bytes;
    if(scratch.peak_files>current->scratch_peak_files)current->scratch_peak_files=scratch.peak_files;
    REQUIRE(scratch_model_canaries());
    if(!scratch.active_files)jpeg_scratch_abort(&scratch);
}

static void start_store(j_common_ptr cinfo)
{
    /* Lazy creation keeps baseline/lossless decodes free of needless scratch I/O. */
    if(scratch.active)return;
    if(!model_started) {
        const char *fault=getenv("SMALL_TV_NOR_FAIL_AT"),*mode=getenv("SMALL_TV_NOR_FAULT_MODE");
        scratch_model_begin(256,fault ? strtoull(fault,NULL,10) : 0,mode ? (unsigned)atoi(mode) : 1);
        model_started=true;
    }
    jpeg_nor_device_t device=scratch_model_device();
    if(jpeg_nor_open(&nor,&device,scratch_extents,SCRATCH_EXTENT_COUNT,SCRATCH_LOGICAL_BYTES,
                     scratch_extents,SCRATCH_EXTENT_COUNT)!=JPEG_NOR_OK ||
        jpeg_scratch_open(&scratch,&nor,scratch_model_check,NULL)!=JPEG_SCRATCH_OK)ERREXIT(cinfo,JERR_NO_BACKING_STORE);
}

static unsigned find_file(j_common_ptr cinfo,backing_store_ptr info,long offset,long count)
{
    /* Every jmemsys offset/count must fit its own exact requested file size. */
    for(unsigned i=0;i<16;++i)
        if(files[i].owner==info && offset>=0 && count>=0 && offset<=files[i].bytes && count<=files[i].bytes-offset)return i;
    ERREXIT(cinfo,JERR_TFILE_SEEK);return 0;
}

static void read_store(j_common_ptr cinfo,backing_store_ptr info,void *data,long offset,long count)
{
    /* Initialized-prefix enforcement detects unexpected real virtual-array traces. */
    unsigned slot=find_file(cinfo,info,offset,count);
    if(probe_fault_visit(PROBE_FAULT_SEEK))ERREXIT(cinfo,JERR_TFILE_SEEK);
    size_t wanted=(size_t)count,request=probe_fault_visit(PROBE_FAULT_READ)&&wanted ? wanted-1 : wanted;
    jpeg_scratch_result_t result=jpeg_scratch_read(&files[slot].file,(uint32_t)offset,data,request);
    if(result!=JPEG_SCRATCH_OK){stats->scratch_error=(unsigned)result;ERREXIT(cinfo,JERR_TFILE_READ);}
    stats->bytes_read+=request;if(request!=wanted)ERREXIT(cinfo,JERR_TFILE_READ);
}

static void write_store(j_common_ptr cinfo,backing_store_ptr info,void *data,long offset,long count)
{
    /* One shared cache handles interleaved component arrays and boundary sectors. */
    unsigned slot=find_file(cinfo,info,offset,count);
    if(probe_fault_visit(PROBE_FAULT_SEEK))ERREXIT(cinfo,JERR_TFILE_SEEK);
    size_t wanted=(size_t)count,request=probe_fault_visit(PROBE_FAULT_WRITE)&&wanted ? wanted-1 : wanted;
    jpeg_scratch_result_t result=jpeg_scratch_write(&files[slot].file,(uint32_t)offset,data,request);
    if(result!=JPEG_SCRATCH_OK){stats->scratch_error=(unsigned)result;ERREXIT(cinfo,JERR_TFILE_WRITE);}
    stats->bytes_written+=request;if(request!=wanted)ERREXIT(cinfo,JERR_TFILE_WRITE);
}

static void close_store(j_common_ptr cinfo,backing_store_ptr info)
{
    /* Error unwind closes files even when a shared I/O failure poisoned all reads. */
    unsigned slot=find_file(cinfo,info,0,0);
    jpeg_scratch_result_t closed=jpeg_scratch_close(&files[slot].file);
    REQUIRE(closed==JPEG_SCRATCH_OK);
    files[slot].owner=NULL;++stats->stores_closed;info->temp_file=NULL;
    probe_backing_snapshot(stats);
}

GLOBAL(void) jpeg_open_backing_store(j_common_ptr cinfo,backing_store_ptr info,long bytes)
{
    /* No per-file sector rounding: four115200-byte files exactly fit460800. */
    if(!stats->allow_backing)ERREXIT(cinfo,JERR_NO_BACKING_STORE);
    if(probe_fault_visit(PROBE_FAULT_OPEN))ERREXITS(cinfo,JERR_TFILE_CREATE,"injected");
    unsigned slot;for(slot=0;slot<16 && files[slot].owner;++slot){}
    if(slot==16 || bytes<=0 || (unsigned long long)bytes>SCRATCH_LOGICAL_BYTES) {
        stats->scratch_error=JPEG_SCRATCH_CAPACITY;ERREXIT(cinfo,JERR_NO_BACKING_STORE);
    }
    start_store(cinfo);
    jpeg_scratch_result_t result=jpeg_scratch_allocate(&scratch,(uint32_t)bytes,&files[slot].file);
    if(result!=JPEG_SCRATCH_OK){stats->scratch_error=(unsigned)result;ERREXIT(cinfo,JERR_NO_BACKING_STORE);}
    files[slot].owner=info;files[slot].bytes=bytes;info->temp_file=NULL;
    info->read_backing_store=read_store;info->write_backing_store=write_store;info->close_backing_store=close_store;
    ++stats->stores_opened;stats->backing_capacity+=(unsigned long long)bytes;
}
