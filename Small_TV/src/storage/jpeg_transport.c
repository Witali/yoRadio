/* REQUESTED_CHANGE: shared physical I/O budgets and revocable, bounded NOR ports
 * backed only by complete immutable-resource/layout authorization. */
#include "jpeg_transport.h"
#include <string.h>

static jpeg_transport_result_t stop(jpeg_transport_t *t,jpeg_transport_result_t error)
{
    /* A failed operation cannot be retried through another still-live port. */
    t->active=false;t->last_error=error;return error;
}

static bool disjoint(const void *a,size_t bytes,const void *b,size_t other_bytes)
{
    /* Reject buffer wrap and accidental overwrite of live capability state. */
    uintptr_t left=(uintptr_t)a,right=(uintptr_t)b;
    if(!a || !b || !bytes || !other_bytes || bytes-1>UINTPTR_MAX-left || other_bytes-1>UINTPTR_MAX-right)return false;
    return left>=right ? left-right>=other_bytes : right-left>=bytes;
}

static bool covered(uint32_t address,size_t bytes,const jpeg_nor_extent_t *ranges,unsigned count)
{
    /* Cover the entire request, allowing adjacency but never hopping over gaps. */
    for(unsigned i=0;i<count && bytes;++i) {
        if(address<ranges[i].offset)return false;
        uint32_t inside=address-ranges[i].offset;
        if(inside<ranges[i].bytes) {
            size_t chunk=ranges[i].bytes-inside;if(chunk>bytes)chunk=bytes;
            address+=(uint32_t)chunk;bytes-=chunk;
        }
    }
    return bytes==0;
}

static jpeg_transport_result_t deadline(jpeg_transport_t *t)
{
    /* Subtraction avoids a deadline addition overflow; reject a clock rollback. */
    uint64_t now=t->now_us(t->clock_context);
    if(now<t->started_us)return stop(t,JPEG_TRANSPORT_CLOCK);
    return now-t->started_us>=t->limits.duration_us ? stop(t,JPEG_TRANSPORT_TIME) : JPEG_TRANSPORT_OK;
}

static jpeg_transport_result_t start(jpeg_transport_t *t,const jpeg_transport_limits_t *limits)
{
    /* New epoch only, never reset a job budget behind old dirty NOR handles. */
    t->active=false;
    if(t->epoch==UINT64_MAX)return stop(t,JPEG_TRANSPORT_STATE);
    ++t->epoch;
    if(!limits || !limits->duration_us)return stop(t,JPEG_TRANSPORT_ARGUMENT);
    t->limits=*limits;memset(&t->usage,0,sizeof(t->usage));t->last_io_error=0;
    t->started_us=t->now_us(t->clock_context);t->last_error=JPEG_TRANSPORT_OK;t->active=true;
    return JPEG_TRANSPORT_OK;
}

static jpeg_transport_result_t charge(jpeg_transport_t *t,char operation,size_t bytes)
{
    /* Preflight whole request before touching flash; failed requests count if
     * issued, not if rejected. Zero budget explicitly forbids that operation. */
    if(!t->active)return JPEG_TRANSPORT_STATE;
    jpeg_transport_result_t result=deadline(t);if(result!=JPEG_TRANSPORT_OK)return result;
    if(t->usage.calls>=t->limits.calls ||
        (operation=='R' && bytes>t->limits.read_bytes-t->usage.read_bytes) ||
        (operation=='P' && bytes>t->limits.program_bytes-t->usage.program_bytes) ||
        (operation=='E' && t->usage.erase_calls>=t->limits.erase_calls))return stop(t,JPEG_TRANSPORT_LIMIT);
    ++t->usage.calls;
    if(operation=='R')t->usage.read_bytes+=bytes;
    if(operation=='P')t->usage.program_bytes+=bytes;
    if(operation=='E')++t->usage.erase_calls;
    return JPEG_TRANSPORT_OK;
}

static int complete(jpeg_transport_t *t,int io_error)
{
    /* Even a completed write may exceed time: report failure and recover from
     * physical bytes; do not let a later metadata operation publish blindly. */
    t->last_io_error=io_error;
    if(io_error)return -(int)stop(t,JPEG_TRANSPORT_IO);
    jpeg_transport_result_t result=deadline(t);return result==JPEG_TRANSPORT_OK ? 0 : -(int)result;
}

static int guard_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* Guard's temporary read permission covers immutable payloads only. */
    jpeg_transport_t *t=context;
    if(!t->verifying || !bytes || !data || address>t->raw.flash_bytes || bytes>t->raw.flash_bytes-address)
        return -(int)stop(t,JPEG_TRANSPORT_RANGE);
    bool allowed=false;
    for(unsigned i=0;i<t->verifying->resource_count;++i) {
        const jpeg_guard_resource_t *r=&t->verifying->resources[i];
        if(address>=r->offset && address-r->offset<r->bytes && bytes<=r->bytes-(address-r->offset))allowed=true;
    }
    if(!allowed)return -(int)stop(t,JPEG_TRANSPORT_RANGE);
    jpeg_transport_result_t result=charge(t,'R',bytes);
    return result==JPEG_TRANSPORT_OK ? complete(t,t->raw.read(t->raw.context,address,data,bytes)) : -(int)result;
}

typedef struct {
    jpeg_transport_t *transport;
    const jpeg_guard_layout_t *layout;
    const jpeg_provision_stamp_t *stamp;
} provision_io_t;

static int provision_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* Guard/provision validates all descriptors before its first read. Bootstrap
     * additionally scans only the generated candidate sectors, never photos or
     * settings. Every physical read shares the SAME startup count/time budget. */
    provision_io_t *io=context;jpeg_transport_t *t=io->transport;
    if(!bytes || !data || address>t->raw.flash_bytes || bytes>t->raw.flash_bytes-address)
        return -(int)stop(t,JPEG_TRANSPORT_RANGE);
    if(!covered(address,bytes,io->layout->allowed,io->layout->allowed_count))
        return guard_read(t,address,data,bytes);
    jpeg_transport_result_t result=charge(t,'R',bytes);
    return result==JPEG_TRANSPORT_OK ? complete(t,t->raw.read(t->raw.context,address,data,bytes)) : -(int)result;
}

static int provision_program(void *context,uint32_t address,const void *data,size_t bytes)
{
    /* Independent bootstrap capabilities: canonical32-byte identity and8-byte
     * commit header only, never a writable page/sector or user-supplied data. */
    provision_io_t *io=context;jpeg_transport_t *t=io->transport;
    if(!t->verifying || t->authorized || io->stamp->resource_index>=io->layout->resource_count || !data)
        return -(int)stop(t,JPEG_TRANSPORT_RANGE);
    uint32_t base=io->layout->resources[io->stamp->resource_index].offset;
    bool header=address==base && bytes==JPEG_PROVISION_HEADER_BYTES && !memcmp(data,io->stamp->bytes,bytes);
    bool identity=address==base+JPEG_PROVISION_HEADER_BYTES && bytes==JPEG_PROVISION_ID_BYTES &&
        !memcmp(data,io->stamp->bytes+JPEG_PROVISION_HEADER_BYTES,bytes);
    if(!header && !identity)return -(int)stop(t,JPEG_TRANSPORT_RANGE);
    jpeg_transport_result_t result=charge(t,'P',bytes);
    return result==JPEG_TRANSPORT_OK ? complete(t,t->raw.program(t->raw.context,address,data,bytes)) : -(int)result;
}

static jpeg_transport_result_t request(jpeg_transport_port_t *port,uint32_t address,size_t bytes,char operation,const void *data)
{
    /* No read/write/erase can outlive authorization or escape the port's scope. */
    if(!port || !port->owner)return JPEG_TRANSPORT_STATE;
    jpeg_transport_t *t=port->owner;
    if(!t->initialized || !t->authorized || !t->active || port->epoch!=t->epoch)return JPEG_TRANSPORT_STATE;
    if(operation!='E' && (!disjoint(data,bytes,t,sizeof(*t)) || !disjoint(data,bytes,port,sizeof(*port))))
        return stop(t,JPEG_TRANSPORT_ARGUMENT);
    if(!bytes || address>t->raw.flash_bytes || bytes>t->raw.flash_bytes-address ||
        !covered(address,bytes,port->extents,port->count) || (operation!='R' && !port->writable) ||
        (operation=='P' && (bytes!=t->raw.page_bytes || address%t->raw.page_bytes)) ||
        (operation=='E' && (bytes!=JPEG_NOR_SECTOR_BYTES || address%JPEG_NOR_SECTOR_BYTES)))
        return stop(t,JPEG_TRANSPORT_RANGE);
    return charge(t,operation,bytes);
}

static int port_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* The NOR core and bounded input reader share the same global counters. */
    jpeg_transport_port_t *port=context;
    jpeg_transport_result_t result=request(port,address,bytes,'R',data);
    if(result!=JPEG_TRANSPORT_OK)return -(int)result;
    jpeg_transport_t *t=port->owner;return complete(t,t->raw.read(t->raw.context,address,data,bytes));
}

static int port_program(void *context,uint32_t address,const void *data,size_t bytes)
{
    /* One explicit logical page; platform driver handles its actual chip pages. */
    jpeg_transport_port_t *port=context;
    jpeg_transport_result_t result=request(port,address,bytes,'P',data);
    if(result!=JPEG_TRANSPORT_OK)return -(int)result;
    jpeg_transport_t *t=port->owner;return complete(t,t->raw.program(t->raw.context,address,data,bytes));
}

static int port_erase(void *context,uint32_t address)
{
    /* No bulk erase or implicit recovery outside the exact authorized sector. */
    jpeg_transport_port_t *port=context;
    jpeg_transport_result_t result=request(port,address,JPEG_NOR_SECTOR_BYTES,'E',NULL);
    if(result!=JPEG_TRANSPORT_OK)return -(int)result;
    jpeg_transport_t *t=port->owner;return complete(t,t->raw.erase_sector(t->raw.context,address));
}

jpeg_transport_result_t jpeg_transport_init(jpeg_transport_t *t,const jpeg_nor_device_t *raw,
                                            uint64_t (*now_us)(void *),void *clock_context)
{
    /* Initialize only once so zeroing/reuse cannot revive an old epoch token. */
    if(!t || !raw || !now_us || !raw->read || !raw->program || !raw->erase_sector ||
        !raw->flash_bytes || (raw->page_bytes!=128 && raw->page_bytes!=256))return JPEG_TRANSPORT_ARGUMENT;
    if(t->initialized)return JPEG_TRANSPORT_STATE;
    t->raw=*raw;t->now_us=now_us;t->clock_context=clock_context;t->epoch=1;t->initialized=true;
    return JPEG_TRANSPORT_OK;
}

static jpeg_transport_result_t grant(jpeg_transport_t *t,const jpeg_guard_layout_t *layout)
{
    /* Shared publication after a complete physical guard, including its last
     * hash callback. No partial layout or live bootstrap permission escapes. */
    jpeg_transport_result_t result=deadline(t);t->verifying=NULL;t->active=false;
    if(result!=JPEG_TRANSPORT_OK)return result;
    memcpy(t->allowed,layout->allowed,layout->allowed_count*sizeof(t->allowed[0]));
    t->allowed_count=layout->allowed_count;
    const jpeg_guard_partition_t *assets=&layout->partitions[layout->assets_partition];
    t->readable=(jpeg_nor_extent_t){assets->offset,assets->bytes};t->authorized=true;
    return JPEG_TRANSPORT_OK;
}

jpeg_transport_result_t jpeg_transport_authorize(jpeg_transport_t *t,const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed,unsigned count,const jpeg_guard_sha256_t *sha256,
    const jpeg_transport_limits_t *limits)
{
    /* Ordinary authorization remains strictly read-only, on every outcome. */
    if(!t || !t->initialized)return JPEG_TRANSPORT_STATE;
    jpeg_transport_revoke(t);
    jpeg_transport_result_t result=start(t,limits);if(result!=JPEG_TRANSPORT_OK)return result;
    t->verifying=layout;
    jpeg_nor_device_t reader={t,t->raw.flash_bytes,t->raw.page_bytes,guard_read,NULL,NULL};
    jpeg_guard_result_t checked=jpeg_guard_verify(layout,observed,count,&reader,sha256);
    if(checked!=JPEG_GUARD_OK) {
        t->verifying=NULL;
        return stop(t,t->last_error==JPEG_TRANSPORT_OK ? JPEG_TRANSPORT_GUARD : t->last_error);
    }
    return grant(t,layout);
}

jpeg_transport_result_t jpeg_transport_provision(jpeg_transport_t *t,const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed,unsigned count,const jpeg_guard_sha256_t *sha256,
    const jpeg_provision_stamp_t *stamp,jpeg_provision_diagnostic_t *diagnostic,
    const jpeg_transport_limits_t *limits)
{
    /* Revoke all ordinary ports BEFORE looking at legacy data. The core must
     * finish a physical guard after provisioning; only then publish capabilities. */
    if(!t || !t->initialized)return JPEG_TRANSPORT_STATE;
    jpeg_transport_revoke(t);
    jpeg_transport_result_t result=start(t,limits);if(result!=JPEG_TRANSPORT_OK)return result;
    t->verifying=layout;
    provision_io_t io={t,layout,stamp};
    jpeg_nor_device_t scoped={&io,t->raw.flash_bytes,t->raw.page_bytes,provision_read,provision_program,NULL};
    jpeg_provision_result_t checked=jpeg_provision_legacy(layout,observed,count,&scoped,sha256,stamp,diagnostic);
    if(checked!=JPEG_PROVISION_ALREADY && checked!=JPEG_PROVISION_INSTALLED) {
        t->verifying=NULL;
        return stop(t,t->last_error==JPEG_TRANSPORT_OK ? JPEG_TRANSPORT_GUARD : t->last_error);
    }
    return grant(t,layout);
}

jpeg_transport_result_t jpeg_transport_begin(jpeg_transport_t *t,const jpeg_transport_limits_t *limits)
{
    /* Caller starts one budget before opening all decoder storage handles. */
    if(!t || !t->initialized || !t->authorized)return JPEG_TRANSPORT_STATE;
    return start(t,limits);
}

jpeg_transport_result_t jpeg_transport_check(jpeg_transport_t *t)
{
    /* I/O revocation cannot by itself stop RAM-only work; owners check here. */
    if(!t || !t->initialized || !t->authorized || !t->active)return JPEG_TRANSPORT_STATE;
    return deadline(t);
}

void jpeg_transport_end(jpeg_transport_t *t)
{
    /* Stale ports stay unusable, even if another budget is started later. */
    if(t)t->active=false;
}

void jpeg_transport_revoke(jpeg_transport_t *t)
{
    /* No I/O and no old write permission during rediscovery/reverification. */
    if(t){t->active=false;t->authorized=false;t->verifying=NULL;}
}

jpeg_transport_result_t jpeg_transport_port(jpeg_transport_t *t,jpeg_transport_port_t *port,
    const jpeg_nor_extent_t *extents,unsigned count,bool writable,jpeg_nor_device_t *device)
{
    /* Descriptors never borrow a mutable HTTP array or alias a dirty NOR cache. */
    if(!t || !t->initialized || !t->authorized || !t->active)return JPEG_TRANSPORT_STATE;
    jpeg_transport_result_t timing=deadline(t);if(timing!=JPEG_TRANSPORT_OK)return timing;
    if(!port || !device || !extents || !count || count>JPEG_NOR_MAX_EXTENTS)return JPEG_TRANSPORT_ARGUMENT;
    if(!disjoint(port,sizeof(*port),t,sizeof(*t)) || !disjoint(device,sizeof(*device),t,sizeof(*t)) ||
        !disjoint(port,sizeof(*port),device,sizeof(*device)))return JPEG_TRANSPORT_ARGUMENT;
    uint32_t end=0;
    for(unsigned i=0;i<count;++i) {
        const jpeg_nor_extent_t *r=&extents[i];
        if(!r->bytes || r->offset<end || r->offset>t->raw.flash_bytes || r->bytes>t->raw.flash_bytes-r->offset ||
            (writable && (r->offset%JPEG_NOR_SECTOR_BYTES || r->bytes%JPEG_NOR_SECTOR_BYTES)) ||
            !(covered(r->offset,r->bytes,t->allowed,t->allowed_count) ||
              (!writable && covered(r->offset,r->bytes,&t->readable,1))))return JPEG_TRANSPORT_RANGE;
        end=r->offset+r->bytes;
    }
    jpeg_transport_port_t saved={0};saved.owner=t;saved.count=count;saved.epoch=t->epoch;saved.writable=writable;
    memcpy(saved.extents,extents,count*sizeof(extents[0]));*port=saved;
    *device=(jpeg_nor_device_t){port,t->raw.flash_bytes,t->raw.page_bytes,port_read,port_program,port_erase};
    return JPEG_TRANSPORT_OK;
}
