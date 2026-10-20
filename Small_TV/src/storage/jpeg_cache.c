/* REQUESTED_CHANGE: durable RGB565 cache, physical identities and one decode. */
#include "jpeg_cache.h"
#include <string.h>

static bool disjoint(const void *data,size_t bytes,const void *object,size_t size)
{
    /* Validate complete external buffers before I/O or owner-state mutation. */
    uintptr_t a=(uintptr_t)data,b=(uintptr_t)object;
    if(!data || !bytes || bytes-1>UINTPTR_MAX-a)return false;
    return a>=b ? a-b>=size : bytes<=b-a;
}

static bool device_valid(const jpeg_nor_device_t *d,bool writing)
{
    /* Readonly source need not provide program/erase capabilities. */
    return d->flash_bytes && d->read && (!writing ||
        (d->program && d->erase_sector && (d->page_bytes==128 || d->page_bytes==256)));
}

static bool overlap(uint32_t a,uint32_t bytes,uint32_t b,uint32_t size)
{
    /* All ranges were bounded against flash before comparing them. */
    return a>=b ? a-b<size : b-a<bytes;
}

static bool covered(uint32_t at,uint32_t bytes,const jpeg_cache_layout_t *layout)
{
    /* Match NOR coverage, including adjacent generated capabilities. */
    for(unsigned i=0;i<layout->allowed_count && bytes;++i) {
        const jpeg_nor_extent_t *r=&layout->allowed[i];
        if(at<r->offset)return false;
        if(at-r->offset<r->bytes){uint32_t n=r->bytes-(at-r->offset);if(n>bytes)n=bytes;at+=n;bytes-=n;}
    }
    return !bytes;
}

static bool layout_valid(const jpeg_cache_layout_t *l,const jpeg_cache_devices_t *d)
{
    /* Validate every slot, not just the selected one, before even journal reads. */
    if(!l || !d || !device_valid(&d->source,false) || !device_valid(&d->frames,true) || !device_valid(&d->metadata,true) ||
       d->source.flash_bytes!=d->frames.flash_bytes || d->source.flash_bytes!=d->metadata.flash_bytes ||
       !l->width || l->width>240 || !l->height || l->height>240 ||
       l->journal.frame_bytes!=l->width*l->height*2u || !l->journal.source_limit ||
       !l->allowed || !l->allowed_count || l->allowed_count>JPEG_NOR_MAX_EXTENTS)return false;
    uint32_t flash=d->source.flash_bytes,end=0;
    for(unsigned i=0;i<l->allowed_count;++i) {
        const jpeg_nor_extent_t *r=&l->allowed[i];
        if(!r->bytes || r->offset%4096u || r->bytes%4096u || r->offset<end || r->offset>flash || r->bytes>flash-r->offset)return false;
        end=r->offset+r->bytes;
    }
    for(unsigned b=0;b<2;++b) {
        uint32_t at=l->journal.banks[b];
        if(at%4096u || at>flash || 4096u>flash-at || !covered(at,4096,l))return false;
    }
    if(l->journal.banks[0]==l->journal.banks[1])return false;
    for(unsigned s=0;s<JPEG_JOURNAL_SLOTS;++s) {
        uint32_t source=l->source_offsets[s];
        if(source>flash || l->journal.source_limit>flash-source)return false;
        for(unsigned b=0;b<2;++b)if(overlap(source,l->journal.source_limit,l->journal.banks[b],4096))return false;
        for(unsigned prior=0;prior<s;++prior)
            if(overlap(source,l->journal.source_limit,l->source_offsets[prior],l->journal.source_limit))return false;
        const jpeg_cache_map_t *m=&l->frames[s];uint64_t total=0;end=0;
        if(!m->extents || !m->count || m->count>JPEG_NOR_MAX_EXTENTS)return false;
        for(unsigned i=0;i<m->count;++i) {
            const jpeg_nor_extent_t *r=&m->extents[i];
            if(!r->bytes || r->offset%4096u || r->bytes%4096u || r->offset<end || r->offset>flash ||
               r->bytes>flash-r->offset || !covered(r->offset,r->bytes,l))return false;
            end=r->offset+r->bytes;total+=r->bytes;
            for(unsigned b=0;b<2;++b)if(overlap(r->offset,r->bytes,l->journal.banks[b],4096))return false;
            for(unsigned p=0;p<JPEG_JOURNAL_SLOTS;++p)
                if(overlap(r->offset,r->bytes,l->source_offsets[p],l->journal.source_limit))return false;
            for(unsigned p=0;p<s;++p)
                for(unsigned j=0;j<l->frames[p].count;++j) {
                    const jpeg_nor_extent_t *other=&l->frames[p].extents[j];
                    if(overlap(r->offset,r->bytes,other->offset,other->bytes))return false;
                }
        }
        if(total!=((l->journal.frame_bytes+4095u)/4096u)*4096u)return false;
    }
    return true;
}

static jpeg_cache_result_t fail(jpeg_cache_t *c,jpeg_cache_result_t result)
{
    /* Failed jobs cannot continue from stale SHA/NOR/journal assumptions. */
    c->failed=true;c->verified=false;c->last_error=result;return result;
}

static jpeg_cache_result_t checkpoint(jpeg_cache_t *c)
{
    /* Cached RAM operations still obey the owner's global budget/deadline. */
    if(!c || !c->open || c->failed)return JPEG_CACHE_STATE;
    if(c->check(c->check_context))return fail(c,JPEG_CACHE_STOP);
    return JPEG_CACHE_OK;
}

static jpeg_cache_result_t hash_begin(jpeg_cache_t *c)
{
    /* Reset is mandatory even after a partially successful provider begin. */
    c->hash_active=true;c->callback_error=c->hash.begin(c->hash.context);
    return c->callback_error ? fail(c,JPEG_CACHE_HASH):checkpoint(c);
}

static jpeg_cache_result_t hash_update(jpeg_cache_t *c,const void *data,size_t bytes)
{
    /* No private SHA implementation; host BCrypt and target PSA share this API. */
    c->callback_error=c->hash.update(c->hash.context,data,bytes);
    return c->callback_error ? fail(c,JPEG_CACHE_HASH):checkpoint(c);
}

static jpeg_cache_result_t hash_finish(jpeg_cache_t *c,uint8_t digest[32])
{
    /* Provider state is released on success as well as on abort/error. */
    c->callback_error=c->hash.finish(c->hash.context,digest);
    c->hash.reset(c->hash.context);c->hash_active=false;
    return c->callback_error ? fail(c,JPEG_CACHE_HASH):checkpoint(c);
}

static jpeg_cache_result_t open_frame(jpeg_cache_t *c)
{
    /* Always discard old cache before a physical identity check/new slot. */
    jpeg_nor_abort(&c->frame);const jpeg_cache_map_t *m=&c->layout->frames[c->slot];
    c->nor_error=jpeg_nor_open(&c->frame,&c->devices.frames,m->extents,m->count,c->layout->journal.frame_bytes,c->layout->allowed,c->layout->allowed_count);
    return c->nor_error ? fail(c,JPEG_CACHE_IO):JPEG_CACHE_OK;
}

static jpeg_cache_result_t source_hash(jpeg_cache_t *c,uint8_t digest[32])
{
    /* Hash actual persistent source, never an HTTP/settings-supplied digest. */
    jpeg_cache_result_t r=hash_begin(c);if(r)return r;uint8_t bytes[256];
    for(uint32_t offset=0;offset<c->source_bytes;) {
        size_t count=c->source_bytes-offset;if(count>sizeof(bytes))count=sizeof(bytes);
        r=checkpoint(c);if(r)return r;
        c->callback_error=c->devices.source.read(c->devices.source.context,c->layout->source_offsets[c->slot]+offset,bytes,count);
        if(c->callback_error)return fail(c,JPEG_CACHE_IO);
        r=hash_update(c,bytes,count);if(r)return r;offset+=(uint32_t)count;
    }
    return hash_finish(c,digest);
}

static int verify_frame(void *context,unsigned slot,uint32_t frame_bytes,const uint8_t expected[32])
{
    /* Flush FIRST, reopen, then read the whole physical frame, bypassing old RAM. */
    jpeg_cache_t *c=context;
    if(slot!=c->slot || frame_bytes!=c->layout->journal.frame_bytes || checkpoint(c))return -1;
    c->nor_error=jpeg_nor_sync(&c->frame);if(c->nor_error){fail(c,JPEG_CACHE_IO);return -1;}
    if(open_frame(c) || hash_begin(c))return -1;
    uint8_t bytes[256],digest[32];
    for(uint32_t offset=0;offset<frame_bytes;) {
        size_t count=frame_bytes-offset;if(count>sizeof(bytes))count=sizeof(bytes);
        if(checkpoint(c))return -1;
        c->nor_error=jpeg_nor_read(&c->frame,offset,bytes,count);
        if(c->nor_error){fail(c,JPEG_CACHE_IO);return -1;}
        if(hash_update(c,bytes,count))return -1;
        offset+=(uint32_t)count;
    }
    if(hash_finish(c,digest))return -1;
    if(memcmp(digest,expected,32)){fail(c,JPEG_CACHE_VERIFY);return -1;}
    return 0;
}

jpeg_cache_result_t jpeg_cache_open(jpeg_cache_t *c,const jpeg_cache_layout_t *layout,
    const jpeg_cache_devices_t *devices,const jpeg_guard_sha256_t *hash,int (*check)(void *),void *context)
{
    /* Validate everything before resetting the owner or reading metadata. */
    if(!c || !layout || !devices || !hash || !hash->begin || !hash->update || !hash->finish || !hash->reset || !check ||
       !disjoint(layout,sizeof(*layout),c,sizeof(*c)) || !disjoint(devices,sizeof(*devices),c,sizeof(*c)) ||
       !disjoint(hash,sizeof(*hash),c,sizeof(*c)) || !layout_valid(layout,devices))return JPEG_CACHE_ARGUMENT;
    if(c->open)return JPEG_CACHE_STATE;
    if(!disjoint(layout->allowed,layout->allowed_count*sizeof(*layout->allowed),c,sizeof(*c)))return JPEG_CACHE_ARGUMENT;
    for(unsigned i=0;i<JPEG_JOURNAL_SLOTS;++i)
        if(!disjoint(layout->frames[i].extents,layout->frames[i].count*sizeof(jpeg_nor_extent_t),c,sizeof(*c)))return JPEG_CACHE_ARGUMENT;
    memset(c,0,sizeof(*c));c->layout=layout;c->devices=*devices;c->hash=*hash;c->check=check;c->check_context=context;c->open=true;
    jpeg_cache_result_t r=checkpoint(c);if(r)return r;
    c->journal_error=jpeg_journal_open(&c->journal,&c->devices.metadata,&layout->journal,layout->allowed,layout->allowed_count);
    if(c->journal_error)return fail(c,JPEG_CACHE_JOURNAL);
    return checkpoint(c);
}

static jpeg_cache_result_t select_slot(jpeg_cache_t *c,unsigned slot,uint32_t length)
{
    /* Changing slots cannot discard an unfinished writer or active SHA stream. */
    if(!c || !c->open || c->failed || c->writing || c->hash_active)return JPEG_CACHE_STATE;
    if(slot>=JPEG_JOURNAL_SLOTS || !length)return JPEG_CACHE_ARGUMENT;
    if(length>c->layout->journal.source_limit) {
        c->required=length;c->available=c->layout->journal.source_limit;c->last_error=JPEG_CACHE_SOURCE_LIMIT;
        return JPEG_CACHE_SOURCE_LIMIT;
    }
    c->required=0;c->available=0;
    c->verified=false;c->slot=slot;c->source_bytes=length;c->next_row=0;return checkpoint(c);
}

jpeg_cache_result_t jpeg_cache_invalidate(jpeg_cache_t *c,unsigned slot)
{
    /* Upload owner calls this BEFORE settings/source erase/write. */
    if(!c || !c->open || c->failed || c->writing || c->hash_active)return JPEG_CACHE_STATE;
    if(slot>=JPEG_JOURNAL_SLOTS)return JPEG_CACHE_ARGUMENT;
    jpeg_cache_result_t r=checkpoint(c);if(r)return r;c->verified=false;
    c->journal_error=jpeg_journal_begin(&c->journal,slot);
    if(c->journal_error)return fail(c,JPEG_CACHE_JOURNAL);
    jpeg_journal_cancel(&c->journal);return checkpoint(c);
}

jpeg_cache_result_t jpeg_cache_lookup(jpeg_cache_t *c,unsigned slot,uint32_t length)
{
    /* Readonly hit: full source and frame hashes; no program/erase is issued. */
    jpeg_cache_result_t r=select_slot(c,slot,length);if(r)return r;
    r=source_hash(c,c->source_sha256);if(r)return r;
    if(open_frame(c))return c->last_error;
    jpeg_journal_verifier_t verifier={c,verify_frame};
    c->journal_error=jpeg_journal_lookup(&c->journal,slot,length,c->source_sha256,&verifier);
    if(c->journal_error==JPEG_JOURNAL_MISS){c->last_error=JPEG_CACHE_MISS;return JPEG_CACHE_MISS;}
    if(c->journal_error)return c->failed ? c->last_error:fail(c,JPEG_CACHE_JOURNAL);
    r=checkpoint(c);if(r)return r;c->verified=true;c->last_error=JPEG_CACHE_OK;return JPEG_CACHE_OK;
}

jpeg_cache_result_t jpeg_cache_begin(jpeg_cache_t *c,unsigned slot,uint32_t length)
{
    /* Durable invalidation is a prerequisite for even the first output row. */
    jpeg_cache_result_t r=select_slot(c,slot,length);if(r)return r;
    c->journal_error=jpeg_journal_begin(&c->journal,slot);
    if(c->journal_error)return fail(c,JPEG_CACHE_JOURNAL);
    r=checkpoint(c);if(r)return r;
    r=source_hash(c,c->source_sha256);if(r)return r;
    if(open_frame(c) || hash_begin(c))return c->last_error;
    c->writing=true;c->last_error=JPEG_CACHE_OK;return JPEG_CACHE_OK;
}

jpeg_cache_result_t jpeg_cache_read_source(jpeg_cache_t *c,uint32_t offset,void *data,size_t bytes)
{
    /* FIXED_RECONSTRUCTION: stable before/after source hashes cannot detect a
     * transient read fault INSIDE the decoder. Compare returned bytes with fresh
     * bounded physical reads before the codec can accept them. Never publish a
     * frame derived from a different byte stream under the original source SHA. */
    if(!c || !c->open || c->failed || !c->writing)return JPEG_CACHE_STATE;
    if(offset>c->source_bytes || bytes>c->source_bytes-offset || (bytes && !disjoint(data,bytes,c,sizeof(*c))))return JPEG_CACHE_ARGUMENT;
    jpeg_cache_result_t r=checkpoint(c);if(r || !bytes)return r;
    c->callback_error=c->devices.source.read(c->devices.source.context,c->layout->source_offsets[c->slot]+offset,data,bytes);
    if(c->callback_error)return fail(c,JPEG_CACHE_IO);
    uint8_t verify[256];
    for(size_t at=0;at<bytes;) {
        r=checkpoint(c);if(r)return r;
        size_t count=bytes-at;if(count>sizeof(verify))count=sizeof(verify);
        c->callback_error=c->devices.source.read(c->devices.source.context,c->layout->source_offsets[c->slot]+offset+(uint32_t)at,verify,count);
        if(c->callback_error)return fail(c,JPEG_CACHE_IO);
        r=checkpoint(c);if(r)return r;
        if(memcmp((const uint8_t *)data+at,verify,count))return fail(c,JPEG_CACHE_VERIFY);
        at+=count;
    }
    return JPEG_CACHE_OK;
}

static bool row_valid(jpeg_cache_t *c,uint32_t row,const void *pixels,uint32_t count)
{
    /* Fixed full rows with valid external buffers; never silently crop output. */
    return row<c->layout->height && count==c->layout->width && disjoint(pixels,(size_t)count*2u,c,sizeof(*c));
}

jpeg_cache_result_t jpeg_cache_write_row(jpeg_cache_t *c,uint32_t row,const uint16_t *pixels,uint32_t count)
{
    /* Explicit little-endian storage/hash; no dependence on host word endian. */
    if(!c || !c->open || c->failed || !c->writing || !c->hash_active)return JPEG_CACHE_STATE;
    if(row!=c->next_row || !row_valid(c,row,pixels,count))return JPEG_CACHE_ARGUMENT;
    uint8_t data[256];uint32_t offset=row*count*2u;
    for(uint32_t x=0;x<count;) {
        jpeg_cache_result_t r=checkpoint(c);if(r)return r;
        uint32_t n=count-x;if(n>sizeof(data)/2)n=sizeof(data)/2;
        for(unsigned i=0;i<n;++i){uint16_t value;memcpy(&value,pixels+x+i,2);data[i*2]=(uint8_t)value;data[i*2+1]=(uint8_t)(value>>8);}
        c->nor_error=jpeg_nor_write(&c->frame,offset,data,n*2u);
        if(c->nor_error)return fail(c,JPEG_CACHE_IO);
        r=hash_update(c,data,n*2u);if(r)return r;offset+=n*2u;x+=n;
    }
    ++c->next_row;return JPEG_CACHE_OK;
}

jpeg_cache_result_t jpeg_cache_commit(jpeg_cache_t *c)
{
    /* An incomplete decoder result never reaches this method in the owner. */
    if(!c || !c->open || c->failed || !c->writing || !c->hash_active)return JPEG_CACHE_STATE;
    if(c->next_row!=c->layout->height)return JPEG_CACHE_STATE;
    jpeg_cache_result_t r=checkpoint(c);if(r)return r;
    r=hash_finish(c,c->frame_sha256);if(r)return r;
    uint8_t source[32];r=source_hash(c,source);if(r)return r;
    if(memcmp(source,c->source_sha256,32))return fail(c,JPEG_CACHE_SOURCE_CHANGED);
    jpeg_journal_verifier_t verifier={c,verify_frame};
    c->journal_error=jpeg_journal_publish(&c->journal,c->source_bytes,c->source_sha256,c->frame_sha256,&verifier);
    if(c->journal_error)return c->failed ? c->last_error:fail(c,JPEG_CACHE_JOURNAL);
    r=checkpoint(c);if(r)return r;c->writing=false;c->verified=true;c->last_error=JPEG_CACHE_OK;return JPEG_CACHE_OK;
}

jpeg_cache_result_t jpeg_cache_read_row(jpeg_cache_t *c,uint32_t row,uint16_t *pixels,uint32_t count)
{
    /* Verified cache display performs bounded reads only, without any decoder. */
    if(!c || !c->open || c->failed || !c->verified || c->writing)return JPEG_CACHE_STATE;
    if(!row_valid(c,row,pixels,count))return JPEG_CACHE_ARGUMENT;
    uint8_t data[256];uint32_t offset=row*count*2u;
    for(uint32_t x=0;x<count;) {
        jpeg_cache_result_t r=checkpoint(c);if(r)return r;
        uint32_t n=count-x;if(n>sizeof(data)/2)n=sizeof(data)/2;
        c->nor_error=jpeg_nor_read(&c->frame,offset,data,n*2u);if(c->nor_error)return fail(c,JPEG_CACHE_IO);
        for(unsigned i=0;i<n;++i){uint16_t value=(uint16_t)data[i*2]|((uint16_t)data[i*2+1]<<8);memcpy(pixels+x+i,&value,2);}
        r=checkpoint(c);if(r)return r;offset+=n*2u;x+=n;
    }
    return JPEG_CACHE_OK;
}

void jpeg_cache_abort(jpeg_cache_t *c)
{
    /* Release crypto state even after partial begin; NEVER flush or publish. */
    if(!c)return;
    if(c->hash_active){c->hash.reset(c->hash.context);c->hash_active=false;}
    jpeg_nor_abort(&c->frame);jpeg_journal_abort(&c->journal);
    c->open=false;c->writing=false;c->verified=false;
}
