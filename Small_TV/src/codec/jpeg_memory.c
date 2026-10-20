/* REQUESTED_CHANGE: per-instance hard-capped jmemsys and exact backing preflight. */
#include "jpeg_decoder_internal.h"

static jpeg_decoder_t *state(j_common_ptr codec)
{
    /* jpeg_CreateDecompress preserves client_data before initializing jmemsys. */
    return codec->client_data;
}

static void *allocate(j_common_ptr codec,size_t bytes)
{
    /* Remember a failed attempt separately: pool-slop retries may still succeed. */
    jpeg_decoder_t *s=state(codec);
    if(bytes>s->config.pool_limit-s->pool_current) {
        s->allocation_status=JPEG_DECODE_POOL_LIMIT;s->allocation_required=(uint64_t)s->pool_current+bytes;return NULL;
    }
    void *data=s->config.allocator.allocate(s->config.allocator.context,bytes);
    if(!data){s->allocation_status=JPEG_DECODE_ALLOCATION;s->allocation_required=bytes;return NULL;}
    s->allocation_status=JPEG_DECODE_OK;s->pool_current+=bytes;
    if(s->pool_current>s->diagnostic.pool_peak)s->diagnostic.pool_peak=s->pool_current;
    return data;
}

GLOBAL(void *) jpeg_get_small(j_common_ptr codec,size_t bytes)
{ /* Allocate one small library pool; no shared allocator globals. */ return allocate(codec,bytes); }
GLOBAL(void *) jpeg_get_large(j_common_ptr codec,size_t bytes)
{ /* Virtual-array windows obey the same actual allocation cap. */ return allocate(codec,bytes); }
GLOBAL(void) jpeg_free_small(j_common_ptr codec,void *data,size_t bytes)
{
    /* Release the original allocation size during success and error unwind. */
    jpeg_decoder_t *s=state(codec);s->pool_current-=bytes;
    s->config.allocator.release(s->config.allocator.context,data,bytes);
}
GLOBAL(void) jpeg_free_large(j_common_ptr codec,void *data,size_t bytes)
{ /* Large and small pools have identical accounting/lifetime requirements. */ jpeg_free_small(codec,data,bytes); }
GLOBAL(size_t) jpeg_mem_available(j_common_ptr codec,size_t minimum,size_t maximum,size_t allocated)
{
    /* Pinned jmemmgr chooses exactly one minimum-height window per array.
     * Later pools/entropy state still obey the real allocation cap. */
    (void)codec;(void)minimum;(void)maximum;(void)allocated;return 0;
}
GLOBAL(long) jpeg_mem_init(j_common_ptr codec)
{ /* The owning context keeps counters across library-object initialization. */ (void)codec;return 0; }
GLOBAL(void) jpeg_mem_term(j_common_ptr codec)
{ /* No backend-global lifetime or implicit I/O. */ (void)codec; }

static void account(jpeg_decoder_t *s,uint64_t columns,uint64_t rows,uint64_t access,uint64_t unit)
{
    /* Record actual padded requests, not a guessed240x240 coefficient bound. */
    if(!columns || !rows || !access || columns>UINT64_MAX/unit || rows>UINT64_MAX/(columns*unit))
        jpeg_decoder_fail(s,JPEG_DECODE_INTERNAL,0,0);
    if(rows>access) {
        uint64_t bytes=columns*rows*unit;
        if(bytes>UINT64_MAX-s->diagnostic.backing_required)jpeg_decoder_fail(s,JPEG_DECODE_BACKING_LIMIT,UINT64_MAX,s->config.backing.capacity);
        s->diagnostic.backing_required+=bytes;++s->backing_files;
    }
}

static jvirt_sarray_ptr samples(j_common_ptr codec,int pool,boolean zero,JDIMENSION columns,JDIMENSION rows,JDIMENSION access)
{
    /* Lossless/multiscan sample arrays use the actual precision's sample width. */
    jpeg_decoder_t *s=state(codec);++s->sample_arrays;
    account(s,columns,rows,access,s->codec.data_precision>8 ? 2u : 1u);
    return s->request_samples(codec,pool,zero,columns,rows,access);
}

static jvirt_barray_ptr blocks(j_common_ptr codec,int pool,boolean zero,JDIMENSION columns,JDIMENSION rows,JDIMENSION access)
{
    /* Each JBLOCK contains64signed16 coefficients, including padded edge blocks. */
    jpeg_decoder_t *s=state(codec);account(s,columns,rows,access,sizeof(JBLOCK));
    return s->request_blocks(codec,pool,zero,columns,rows,access);
}

static void realize(j_common_ptr codec)
{
    /* REQUESTED_CHANGE: reject the ENTIRE requirement before the original loop
     * can open any file. A later component must not discover capacity after
     * earlier arrays have already started physical storage operations. */
    jpeg_decoder_t *s=state(codec);jpeg_decoder_checkpoint(s);
    if(s->diagnostic.backing_required>s->config.backing.capacity)
        jpeg_decoder_fail(s,JPEG_DECODE_BACKING_LIMIT,s->diagnostic.backing_required,s->config.backing.capacity);
    if(s->backing_files>JPEG_DECODER_FILES)jpeg_decoder_fail(s,JPEG_DECODE_BACKING_FILES,s->backing_files,JPEG_DECODER_FILES);
    s->realize_arrays(codec);
}

void jpeg_decoder_install_memory(jpeg_decoder_t *s)
{
    /* Install once per created JPEG object; abort preserves these function pointers. */
    s->request_samples=s->codec.mem->request_virt_sarray;s->request_blocks=s->codec.mem->request_virt_barray;
    s->realize_arrays=s->codec.mem->realize_virt_arrays;
    s->codec.mem->request_virt_sarray=samples;s->codec.mem->request_virt_barray=blocks;s->codec.mem->realize_virt_arrays=realize;
}

static unsigned file_slot(j_common_ptr codec,backing_store_ptr info,long offset,long bytes)
{
    /* Validate the whole request before any callback or buffer mutation. */
    jpeg_decoder_t *s=state(codec);
    for(unsigned i=0;i<JPEG_DECODER_FILES;++i)
        if(s->files[i].owner==info && offset>=0 && bytes>=0 && (uint64_t)offset<=s->files[i].bytes &&
           (uint64_t)bytes<=s->files[i].bytes-(uint64_t)offset)return i;
    jpeg_decoder_fail(s,JPEG_DECODE_INTERNAL,0,0);return 0;
}

static void read_store(j_common_ptr codec,backing_store_ptr info,void *data,long offset,long bytes)
{
    /* Read exact initialized bytes; the backing owner enforces NOR/epoch policy. */
    jpeg_decoder_t *s=state(codec);unsigned i=file_slot(codec,info,offset,bytes);jpeg_decoder_checkpoint(s);
    int result=s->config.backing.read(s->config.backing.context,s->files[i].handle,(uint32_t)offset,data,(size_t)bytes);
    if(result)jpeg_decoder_callback_error(s,JPEG_DECODE_BACKING_IO,result);
    jpeg_decoder_checkpoint(s);
}

static void write_store(j_common_ptr codec,backing_store_ptr info,void *data,long offset,long bytes)
{
    /* Preserve partial-error causes; callers must not publish provisional rows. */
    jpeg_decoder_t *s=state(codec);unsigned i=file_slot(codec,info,offset,bytes);jpeg_decoder_checkpoint(s);
    int result=s->config.backing.write(s->config.backing.context,s->files[i].handle,(uint32_t)offset,data,(size_t)bytes);
    if(result)jpeg_decoder_callback_error(s,JPEG_DECODE_BACKING_IO,result);
    jpeg_decoder_checkpoint(s);
}

static void close_store(j_common_ptr codec,backing_store_ptr info)
{
    /* Cleanup cannot longjmp or depend on a still-valid I/O/deadline budget. */
    jpeg_decoder_t *s=state(codec);unsigned i=0;
    while(i<JPEG_DECODER_FILES && s->files[i].owner!=info)++i;
    if(i==JPEG_DECODER_FILES){if(s->diagnostic.status==JPEG_DECODE_OK)s->diagnostic.status=JPEG_DECODE_INTERNAL;return;}
    int result=s->config.backing.close(s->config.backing.context,s->files[i].handle);
    s->backing_current-=s->files[i].bytes;s->files[i].owner=NULL;++s->diagnostic.stores_closed;
    if(result && s->diagnostic.status==JPEG_DECODE_OK){s->diagnostic.status=JPEG_DECODE_BACKING_IO;s->diagnostic.callback_error=result;}
}

void jpeg_decoder_release_backing(jpeg_decoder_t *s)
{
    /* A post-open deadline can longjmp before jmemmgr sets b_s_open. After its
     * normal abort loop, release such orphan handles without dereferencing the
     * already freed virtual-array owner pointer or issuing a budgeted flush. */
    for(unsigned i=0;i<JPEG_DECODER_FILES;++i)
        if(s->files[i].owner)close_store((j_common_ptr)&s->codec,s->files[i].owner);
}

GLOBAL(void) jpeg_open_backing_store(j_common_ptr codec,backing_store_ptr info,long bytes)
{
    /* The preflight uses the same minimum-window policy as jmemmgr, then this
     * defense checks the actual per-file opens again. No FILE/stdio ownership. */
    jpeg_decoder_t *s=state(codec);unsigned i=0;while(i<JPEG_DECODER_FILES && s->files[i].owner)++i;
    if(i==JPEG_DECODER_FILES)jpeg_decoder_fail(s,JPEG_DECODE_BACKING_FILES,i+1u,JPEG_DECODER_FILES);
    if(bytes<=0)jpeg_decoder_fail(s,JPEG_DECODE_INTERNAL,0,0);
    if((uint64_t)bytes>s->config.backing.capacity-s->backing_current)
        jpeg_decoder_fail(s,JPEG_DECODE_BACKING_LIMIT,s->backing_current+(uint64_t)bytes,s->config.backing.capacity);
    if(!s->config.backing.open)jpeg_decoder_fail(s,JPEG_DECODE_BACKING_LIMIT,s->diagnostic.backing_required,0);
    jpeg_decoder_checkpoint(s);uint64_t handle=0;
    bool coefficients=!s->sample_arrays && s->codec.progressive_mode;
    int result=s->config.backing.open(s->config.backing.context,(uint32_t)bytes,coefficients,&handle);
    if(result)jpeg_decoder_callback_error(s,JPEG_DECODE_BACKING_IO,result);
    s->files[i].owner=info;s->files[i].handle=handle;s->files[i].bytes=(uint32_t)bytes;
    s->backing_current+=(uint32_t)bytes;if(s->backing_current>s->diagnostic.backing_peak)s->diagnostic.backing_peak=s->backing_current;
    ++s->diagnostic.stores_opened;info->temp_file=NULL;
    info->read_backing_store=read_store;info->write_backing_store=write_store;info->close_backing_store=close_store;
    jpeg_decoder_checkpoint(s);
}
