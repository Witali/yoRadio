/* REQUESTED_CHANGE: real decoder backing, shared NOR cache, reversible coefficients. */
#include "jpeg_backing.h"
#include "jpeg_coefficients.h"
#include <string.h>

static bool disjoint(const void *data,size_t bytes,const void *object,size_t object_bytes)
{
    /* Reject complete invalid/aliased ranges before any preparation or I/O. */
    if(!bytes)return true;
    uintptr_t a=(uintptr_t)data,b=(uintptr_t)object;
    if(!data || bytes-1>UINTPTR_MAX-a)return false;
    return a>=b ? a-b>=object_bytes : bytes<=b-a;
}

size_t jpeg_backing_bitmap_bytes(uint32_t capacity)
{
    /* Two divisions avoid overflow at UINT32_MAX capacity. */
    uint32_t sectors=capacity/4096u+(capacity%4096u!=0);
    return sectors/8u+(sectors%8u!=0);
}

static jpeg_scratch_result_t checkpoint(jpeg_backing_t *b)
{
    /* RAM hits also observe global transport revocation, deadline and budgets. */
    if(!b || !b->active || !b->scratch.active || b->scratch.failed ||
       !b->scratch.store->open || b->scratch.store->failed)return JPEG_SCRATCH_STATE;
    if(b->scratch.check(b->scratch.check_context)){b->scratch.failed=true;return JPEG_SCRATCH_STOP;}
    return JPEG_SCRATCH_OK;
}

jpeg_scratch_result_t jpeg_backing_begin(jpeg_backing_t *b,jpeg_nor_t *store,
    int (*check)(void *),void *context,uint8_t *bitmap,size_t bitmap_bytes)
{
    /* Validate all descriptors before changing either the live owner or bitmap. */
    if(!b || !store || !check || !store->open || store->failed || store->cached || store->dirty ||
       !disjoint(store,sizeof(*store),b,sizeof(*b)))return JPEG_SCRATCH_ARGUMENT;
    size_t needed=jpeg_backing_bitmap_bytes(store->logical_bytes);
    if(!needed || bitmap_bytes<needed || !disjoint(bitmap,bitmap_bytes,b,sizeof(*b)) ||
       !disjoint(bitmap,bitmap_bytes,store,sizeof(*store)))return JPEG_SCRATCH_ARGUMENT;
    if(b->active || b->scratch.active)return JPEG_SCRATCH_STATE;
    if(b->capacity && b->capacity!=store->logical_bytes)return JPEG_SCRATCH_ARGUMENT;
    jpeg_scratch_result_t result=jpeg_scratch_open(&b->scratch,store,check,context);
    if(result!=JPEG_SCRATCH_OK){jpeg_scratch_abort(&b->scratch);b->last_error=result;return result;}
    b->capacity=store->logical_bytes;b->fresh=bitmap;b->fresh_bytes=needed;b->mode=0;b->active=true;
    memset(bitmap,0,needed);b->last_error=JPEG_SCRATCH_OK;return JPEG_SCRATCH_OK;
}

static bool token(jpeg_backing_t *b,uint64_t id,jpeg_scratch_file_t *file)
{
    /* Monotonic IDs survive close/abort/reopen; no stale slot-index handles. */
    if(!b || !b->active || !b->scratch.active)return false;
    for(unsigned i=0;i<JPEG_SCRATCH_MAX_FILES;++i)
        if(b->scratch.files[i].used && b->scratch.files[i].id==id) {
            *file=(jpeg_scratch_file_t){&b->scratch,id,i};return true;
        }
    return false;
}

static jpeg_scratch_result_t validate(jpeg_backing_t *b,uint64_t id,uint32_t offset,
    const void *data,size_t bytes,bool writing,jpeg_scratch_file_t *file)
{
    /* Prefix/mode/bounds/alias validation precedes even first-use sector writes. */
    if(!token(b,id,file))return JPEG_SCRATCH_STATE;
    const jpeg_scratch_region_t *r=&b->scratch.files[file->slot];
    if(offset>r->bytes || bytes>r->bytes-offset)return JPEG_SCRATCH_RANGE;
    if(b->mode==2 && (offset%128u || bytes%128u))return JPEG_SCRATCH_ARGUMENT;
    if(!disjoint(data,bytes,b,sizeof(*b)) || !disjoint(data,bytes,b->scratch.store,sizeof(*b->scratch.store)) ||
       !disjoint(data,bytes,b->fresh,b->fresh_bytes) || !disjoint(data,bytes,file,sizeof(*file)))return JPEG_SCRATCH_ARGUMENT;
    if(bytes && (offset>r->initialized || (!writing && bytes>r->initialized-offset)))return JPEG_SCRATCH_UNINITIALIZED;
    return checkpoint(b);
}

static jpeg_scratch_result_t prepare_fresh(jpeg_backing_t *b,const jpeg_scratch_file_t *file,
    uint32_t offset,size_t bytes,uint8_t erased[256])
{
    /* All live files have one mode, so a new sector contains no initialized raw
     * bytes. Clear each sector only once; adjacent packed files can share it.
     * Reuse the conversion buffer/cache, preserving last-sector owned padding. */
    uint32_t start=b->scratch.files[file->slot].offset+offset,last=(start+(uint32_t)bytes-1u)/4096u;
    for(uint32_t sector=start/4096u;sector<=last;++sector) {
        unsigned mask=1u<<(sector%8u);if(b->fresh[sector/8u]&mask)continue;
        memset(erased,0xff,256);uint32_t base=sector*4096u,length=b->capacity-base;
        if(length>4096u)length=4096u;
        for(uint32_t at=0;at<length;) {
            jpeg_scratch_result_t result=checkpoint(b);if(result!=JPEG_SCRATCH_OK)return result;
            size_t block=length-at;if(block>256u)block=256u;
            b->scratch.last_nor_error=jpeg_nor_write(b->scratch.store,base+at,erased,block);
            if(b->scratch.last_nor_error!=JPEG_NOR_OK){b->scratch.failed=true;return JPEG_SCRATCH_IO;}
            at+=(uint32_t)block;
        }
        b->fresh[sector/8u]|=(uint8_t)mask;
    }
    return JPEG_SCRATCH_OK;
}

static int open_file(void *context,uint32_t bytes,bool coefficients,uint64_t *handle)
{
    /* One homogeneous job avoids clearing a sector containing a raw-file prefix. */
    jpeg_backing_t *b=context;unsigned mode=coefficients ? 2u:1u;
    if(!b)return JPEG_SCRATCH_ARGUMENT;
    if(!handle || !disjoint(handle,sizeof(*handle),b,sizeof(*b)) ||
       (b->active && (!disjoint(handle,sizeof(*handle),b->scratch.store,sizeof(*b->scratch.store)) ||
                      !disjoint(handle,sizeof(*handle),b->fresh,b->fresh_bytes))))return b->last_error=JPEG_SCRATCH_ARGUMENT;
    if((coefficients && bytes%128u) || (b->mode && b->mode!=mode))return b->last_error=JPEG_SCRATCH_ARGUMENT;
    jpeg_scratch_result_t result=checkpoint(b);if(result!=JPEG_SCRATCH_OK)return b->last_error=result;
    jpeg_scratch_file_t file;result=jpeg_scratch_allocate(&b->scratch,bytes,&file);
    if(result==JPEG_SCRATCH_OK){b->mode=mode;*handle=file.id;}
    return b->last_error=result;
}

static int transfer(jpeg_backing_t *b,uint64_t id,uint32_t offset,void *data,size_t bytes,bool writing)
{
    /* One bounded conversion buffer; raw arrays retain byte-granular semantics. */
    jpeg_scratch_file_t file;jpeg_scratch_result_t result=validate(b,id,offset,data,bytes,writing,&file);
    if(result!=JPEG_SCRATCH_OK)return result;
    if(b->mode!=2 || !bytes)return writing ? jpeg_scratch_write(&file,offset,data,bytes) : jpeg_scratch_read(&file,offset,data,bytes);
    uint8_t encoded[256],*current=data;
    while(bytes) {
        result=checkpoint(b);if(result!=JPEG_SCRATCH_OK)return result;
        size_t block=bytes<sizeof(encoded) ? bytes:sizeof(encoded);
        if(writing) {
            result=prepare_fresh(b,&file,offset,block,encoded);if(result!=JPEG_SCRATCH_OK)return result;
            if(!jpeg_coefficients_pack(encoded,current,block,offset))return JPEG_SCRATCH_ARGUMENT;
            result=jpeg_scratch_write(&file,offset,encoded,block);
        } else {
            result=jpeg_scratch_read(&file,offset,encoded,block);
            if(result==JPEG_SCRATCH_OK && !jpeg_coefficients_unpack(current,encoded,block,offset))return JPEG_SCRATCH_ARGUMENT;
        }
        if(result!=JPEG_SCRATCH_OK)return result;
        offset+=(uint32_t)block;current+=block;bytes-=block;
    }
    return JPEG_SCRATCH_OK;
}

static int read_file(void *context,uint64_t handle,uint32_t offset,void *data,size_t bytes)
{
    /* Preserve a concrete storage cause for decoder diagnostics. */
    jpeg_backing_t *b=context;if(!b)return JPEG_SCRATCH_ARGUMENT;
    return b->last_error=(jpeg_scratch_result_t)transfer(b,handle,offset,data,bytes,false);
}

static int write_file(void *context,uint64_t handle,uint32_t offset,const void *data,size_t bytes)
{
    /* The decoder has already preflighted the complete virtual-array demand. */
    jpeg_backing_t *b=context;if(!b)return JPEG_SCRATCH_ARGUMENT;
    return b->last_error=(jpeg_scratch_result_t)transfer(b,handle,offset,(void *)data,bytes,true);
}

static int close_file(void *context,uint64_t handle)
{
    /* Never checkpoint/flush cleanup: expired or failed jobs must still release. */
    jpeg_backing_t *b=context;if(!b)return JPEG_SCRATCH_ARGUMENT;jpeg_scratch_file_t file;
    if(!token(b,handle,&file))return b->last_error=JPEG_SCRATCH_STATE;
    return b->last_error=jpeg_scratch_close(&file);
}

jpeg_decode_backing_t jpeg_backing_callbacks(jpeg_backing_t *b)
{
    /* The descriptor borrows a stable owner whose capacity cannot change on reuse. */
    jpeg_decode_backing_t api={b,b ? b->capacity:0,open_file,read_file,write_file,close_file};return api;
}

void jpeg_backing_abort(jpeg_backing_t *b)
{
    /* Temp files are disposable; preserve IDs but drop dirty NOR RAM with no I/O. */
    if(b){jpeg_scratch_abort(&b->scratch);b->active=false;b->mode=0;}
}
