/* REQUESTED_CHANGE: bounded byte-granular libjpeg backing files sharing ONE
 * sparse NOR cache. No per-array sector padding or stale/uninitialized reads. */
#include "jpeg_scratch.h"
#include <string.h>

static bool disjoint(const void *data,size_t bytes,const void *object,size_t object_bytes)
{
    /* Protect allocator/token state from accidental buffer alias or pointer wrap. */
    uintptr_t a=(uintptr_t)data,b=(uintptr_t)object;
    if(!bytes)return true;
    if(!data || bytes-1>UINTPTR_MAX-a)return false;
    return a>=b ? a-b>=object_bytes : bytes<=b-a;
}

static jpeg_scratch_result_t checkpoint(jpeg_scratch_t *s)
{
    /* A global error/expired budget stops every virtual file, even dirty RAM hits. */
    if(!s || !s->active || s->failed || !s->store->open || s->store->failed)return JPEG_SCRATCH_STATE;
    if(s->check(s->check_context)){s->failed=true;return JPEG_SCRATCH_STOP;}
    return JPEG_SCRATCH_OK;
}

static jpeg_scratch_region_t *region(const jpeg_scratch_file_t *file)
{
    /* Immutable by-value IDs survive slot recycling; no pointer-only ownership. */
    if(!file || !file->owner || !file->owner->active || file->slot>=JPEG_SCRATCH_MAX_FILES)return NULL;
    jpeg_scratch_region_t *r=&file->owner->files[file->slot];
    return r->used && r->id==file->id ? r : NULL;
}

static jpeg_scratch_result_t request(const jpeg_scratch_file_t *file,uint32_t offset,
                                      const void *data,size_t bytes,bool writing)
{
    /* Reject whole invalid requests before NOR or even the owner checkpoint. */
    jpeg_scratch_region_t *r=region(file);
    if(!r)return JPEG_SCRATCH_STATE;
    if(offset>r->bytes || bytes>r->bytes-offset)return JPEG_SCRATCH_RANGE;
    if(!disjoint(data,bytes,file->owner,sizeof(*file->owner)) || !disjoint(data,bytes,file,sizeof(*file)))
        return JPEG_SCRATCH_ARGUMENT;
    if(bytes && (offset>r->initialized || (!writing && bytes>r->initialized-offset)))
        return JPEG_SCRATCH_UNINITIALIZED;
    return checkpoint(file->owner);
}

jpeg_scratch_result_t jpeg_scratch_open(jpeg_scratch_t *s,jpeg_nor_t *store,
                                        int (*check)(void *),void *check_context)
{
    /* Reuse retains next_id; a decoder abort never leaves a valid old file. */
    if(!s || !store || !check || !store->open || store->failed ||
        !disjoint(store,sizeof(*store),s,sizeof(*s)))return JPEG_SCRATCH_ARGUMENT;
    if(s->active)return JPEG_SCRATCH_STATE;
    s->store=store;s->check=check;s->check_context=check_context;s->active=true;s->failed=false;
    s->active_bytes=0;s->peak_bytes=0;s->active_files=0;s->peak_files=0;s->read_bytes=0;s->write_bytes=0;
    s->last_nor_error=JPEG_NOR_OK;memset(s->files,0,sizeof(s->files));
    return checkpoint(s);
}

jpeg_scratch_result_t jpeg_scratch_allocate(jpeg_scratch_t *s,uint32_t bytes,jpeg_scratch_file_t *file)
{
    /* Bounded first-fit allocation; file boundaries may share a physical sector. */
    jpeg_scratch_result_t result=checkpoint(s);if(result!=JPEG_SCRATCH_OK)return result;
    if(!bytes || !file || !disjoint(file,sizeof(*file),s,sizeof(*s)) ||
        !disjoint(file,sizeof(*file),s->store,sizeof(*s->store)))return JPEG_SCRATCH_ARGUMENT;
    if(s->next_id==UINT64_MAX)return JPEG_SCRATCH_LIMIT;
    unsigned slot=0;while(slot<JPEG_SCRATCH_MAX_FILES && s->files[slot].used)++slot;
    if(slot==JPEG_SCRATCH_MAX_FILES)return JPEG_SCRATCH_CAPACITY;
    uint32_t candidate=0;
    for(unsigned attempt=0;attempt<=JPEG_SCRATCH_MAX_FILES;++attempt) {
        if(candidate>s->store->logical_bytes || bytes>s->store->logical_bytes-candidate)return JPEG_SCRATCH_CAPACITY;
        bool moved=false;
        for(unsigned i=0;i<JPEG_SCRATCH_MAX_FILES;++i) {
            const jpeg_scratch_region_t *r=&s->files[i];
            if(r->used && candidate<r->offset+r->bytes && r->offset<candidate+bytes) {
                candidate=r->offset+r->bytes;moved=true;break;
            }
        }
        if(!moved) {
            jpeg_scratch_region_t *r=&s->files[slot];
            *r=(jpeg_scratch_region_t){candidate,bytes,0,++s->next_id,true};
            *file=(jpeg_scratch_file_t){s,r->id,slot};s->active_bytes+=bytes;++s->active_files;
            if(s->active_bytes>s->peak_bytes)s->peak_bytes=s->active_bytes;
            if(s->active_files>s->peak_files)s->peak_files=s->active_files;
            return JPEG_SCRATCH_OK;
        }
    }
    return JPEG_SCRATCH_CAPACITY;
}

jpeg_scratch_result_t jpeg_scratch_read(const jpeg_scratch_file_t *file,uint32_t offset,void *data,size_t bytes)
{
    /* Dirty data in a shared physical sector stays coherent across file owners. */
    jpeg_scratch_result_t result=request(file,offset,data,bytes,false);if(result!=JPEG_SCRATCH_OK)return result;
    jpeg_scratch_t *s=file->owner;
    s->last_nor_error=jpeg_nor_read(s->store,s->files[file->slot].offset+offset,data,bytes);
    if(s->last_nor_error!=JPEG_NOR_OK){s->failed=true;return JPEG_SCRATCH_IO;}
    s->read_bytes+=bytes;return JPEG_SCRATCH_OK;
}

jpeg_scratch_result_t jpeg_scratch_write(const jpeg_scratch_file_t *file,uint32_t offset,const void *data,size_t bytes)
{
    /* Publish initialized bytes only after the entire logical write succeeds. */
    jpeg_scratch_result_t result=request(file,offset,data,bytes,true);if(result!=JPEG_SCRATCH_OK)return result;
    jpeg_scratch_t *s=file->owner;jpeg_scratch_region_t *r=&s->files[file->slot];
    s->last_nor_error=jpeg_nor_write(s->store,r->offset+offset,data,bytes);
    if(s->last_nor_error!=JPEG_NOR_OK){s->failed=true;return JPEG_SCRATCH_IO;}
    if(bytes && offset+(uint32_t)bytes>r->initialized)r->initialized=offset+(uint32_t)bytes;
    s->write_bytes+=bytes;return JPEG_SCRATCH_OK;
}

jpeg_scratch_result_t jpeg_scratch_close(const jpeg_scratch_file_t *file)
{
    /* Library destroy can release resources even after fatal I/O/deadline errors. */
    jpeg_scratch_region_t *r=region(file);if(!r)return JPEG_SCRATCH_STATE;
    r->used=false;file->owner->active_bytes-=r->bytes;--file->owner->active_files;return JPEG_SCRATCH_OK;
}

void jpeg_scratch_abort(jpeg_scratch_t *s)
{
    /* Temp data has no commit requirement; never flush on error/cancel/destroy. */
    if(!s)return;
    if(s->active && s->store)jpeg_nor_abort(s->store);
    s->active=false;s->active_bytes=0;s->active_files=0;
    for(unsigned i=0;i<JPEG_SCRATCH_MAX_FILES;++i)s->files[i].used=false;
}
