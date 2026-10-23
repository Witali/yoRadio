/* REQUESTED_CHANGE: bounded, erase-free adoption of matching legacy resources. */
#include "jpeg_provision.h"
#include <string.h>

typedef struct {
    const jpeg_nor_device_t *device;
    const jpeg_guard_resource_t *resource;
    const jpeg_provision_stamp_t *stamp;
} overlay_t;

static int overlay_read(void *context,uint32_t address,void *data,size_t bytes)
{
    /* Read-only verification of the prospective stamp, never authorization.
     * All other resource hashes still consume actual physical flash bytes. The
     * full physical guard must run again after exact write/readback succeeds. */
    overlay_t *overlay=context;const jpeg_guard_resource_t *r=overlay->resource;
    if(address>=r->offset && address-r->offset<r->bytes && bytes<=r->bytes-(address-r->offset)) {
        memcpy(data,overlay->stamp->bytes+address-r->offset,bytes);return 0;
    }
    return overlay->device->read(overlay->device->context,address,data,bytes);
}

static jpeg_guard_result_t stamp_identity(const jpeg_guard_resource_t *resource,
    const jpeg_provision_stamp_t *stamp,const jpeg_guard_sha256_t *hash)
{
    /* Bind the compiled target bytes to the guard's stamp digest even on an
     * already-provisioned boot. No flash permission is implied by this hash. */
    uint8_t digest[32];jpeg_guard_result_t result=JPEG_GUARD_HASH;
    if(!hash->begin(hash->context) && !hash->update(hash->context,stamp->bytes,JPEG_PROVISION_STAMP_BYTES) &&
       !hash->finish(hash->context,digest))
        result=memcmp(digest,resource->sha256,sizeof(digest)) ? JPEG_GUARD_RESOURCE:JPEG_GUARD_OK;
    hash->reset(hash->context);return result;
}

static jpeg_provision_result_t read_twice(const jpeg_nor_device_t *device,
    uint32_t address,uint8_t *data,size_t bytes,jpeg_provision_diagnostic_t *diagnostic)
{
    /* A single silent read fault must not turn an occupied sector or an
     * incompatible stamp into apparently erased/compatible data. */
    uint8_t second[JPEG_GUARD_READ_BYTES];diagnostic->offset=address;
    diagnostic->io_error=device->read(device->context,address,data,bytes);
    if(!diagnostic->io_error)diagnostic->io_error=device->read(device->context,address,second,bytes);
    if(diagnostic->io_error)return JPEG_PROVISION_IO;
    return memcmp(data,second,bytes) ? JPEG_PROVISION_VERIFY:JPEG_PROVISION_ALREADY;
}

static jpeg_provision_result_t compatible_stamp(const jpeg_nor_device_t *device,
    uint32_t address,const jpeg_provision_stamp_t *stamp,uint8_t current[JPEG_PROVISION_STAMP_BYTES],
    jpeg_provision_diagnostic_t *diagnostic)
{
    /* No repair erase: every observed zero must also be zero in the target.
     * Arbitrary torn bit subsets are legal WITHIN each ordered phase. Once the
     * header is nonerased, the identity must already be complete and verified. */
    jpeg_provision_result_t result=read_twice(device,address,current,JPEG_PROVISION_STAMP_BYTES,diagnostic);
    if(result!=JPEG_PROVISION_ALREADY)return result;
    for(unsigned i=0;i<JPEG_PROVISION_STAMP_BYTES;++i)
        if((current[i]&stamp->bytes[i])!=stamp->bytes[i]) {
            diagnostic->offset=address+i;return JPEG_PROVISION_STAMP;
        }
    bool header_erased=true;
    for(unsigned i=0;i<JPEG_PROVISION_HEADER_BYTES;++i)header_erased &= current[i]==0xff;
    if(!header_erased && memcmp(current+JPEG_PROVISION_HEADER_BYTES,
        stamp->bytes+JPEG_PROVISION_HEADER_BYTES,JPEG_PROVISION_ID_BYTES))return JPEG_PROVISION_STAMP;
    return JPEG_PROVISION_ALREADY;
}

static jpeg_provision_result_t write_part(const jpeg_nor_device_t *device,
    uint32_t address,const uint8_t *data,size_t bytes,jpeg_provision_diagnostic_t *diagnostic)
{
    /* Synchronous completion plus fresh readback before the next commit phase.
     * Failed writes remain resumable only under the ordered-state preflight. */
    diagnostic->offset=address;diagnostic->program_attempted=true;
    diagnostic->io_error=device->program(device->context,address,data,bytes);
    if(diagnostic->io_error)return JPEG_PROVISION_IO;
    uint8_t actual[JPEG_PROVISION_STAMP_BYTES];
    jpeg_provision_result_t result=read_twice(device,address,actual,bytes,diagnostic);
    if(result!=JPEG_PROVISION_ALREADY)return result;
    return memcmp(actual,data,bytes) ? JPEG_PROVISION_VERIFY:JPEG_PROVISION_ALREADY;
}

static jpeg_provision_result_t vacant(const jpeg_guard_layout_t *layout,
    const jpeg_nor_device_t *device,jpeg_provision_diagnostic_t *diagnostic)
{
    /* Matching immutable hashes alone do not establish ownership of old gaps.
     * Require every byte of every generated candidate extent, including spare
     * sectors, to be erased. Photos/settings/protected gaps are never scanned. */
    uint8_t bytes[JPEG_GUARD_READ_BYTES];
    for(unsigned i=0;i<layout->allowed_count;++i) {
        const jpeg_nor_extent_t *range=&layout->allowed[i];
        for(uint32_t offset=0;offset<range->bytes;offset+=sizeof(bytes)) {
            jpeg_provision_result_t result=read_twice(device,range->offset+offset,bytes,sizeof(bytes),diagnostic);
            if(result!=JPEG_PROVISION_ALREADY)return result;
            for(unsigned j=0;j<sizeof(bytes);++j)if(bytes[j]!=0xff) {
                diagnostic->offset=range->offset+offset+j;return JPEG_PROVISION_OCCUPIED;
            }
        }
    }
    return JPEG_PROVISION_ALREADY;
}

jpeg_provision_result_t jpeg_provision_legacy(const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed,unsigned observed_count,
    const jpeg_nor_device_t *device,const jpeg_guard_sha256_t *sha256,
    const jpeg_provision_stamp_t *stamp,jpeg_provision_diagnostic_t *diagnostic)
{
    /* No general guard bypass. The overlay validates the exact future stamp
     * descriptor/content and all other physical payloads before any program.
     * The owner retains all capability decisions until final physical success. */
    jpeg_provision_diagnostic_t local={0};if(!diagnostic)diagnostic=&local;
    memset(diagnostic,0,sizeof(*diagnostic));diagnostic->status=JPEG_PROVISION_ARGUMENT;
    if(!layout || !device || !device->read || !device->program || !stamp ||
       !layout->resources || !layout->resource_count ||
       layout->resource_count>JPEG_GUARD_MAX_RESOURCES || stamp->resource_index>=layout->resource_count ||
       device->page_bytes<JPEG_PROVISION_STAMP_BYTES || device->page_bytes>JPEG_NOR_MAX_PAGE_BYTES ||
       (device->page_bytes&(device->page_bytes-1u)) || memcmp(stamp->bytes,"STVOWN1\0",8))return diagnostic->status;
    const jpeg_guard_resource_t *resource=&layout->resources[stamp->resource_index];
    if(resource->bytes!=JPEG_PROVISION_STAMP_BYTES || resource->offset%4u ||
       resource->offset%device->page_bytes>device->page_bytes-JPEG_PROVISION_STAMP_BYTES)return diagnostic->status;
    for(unsigned i=40;i<JPEG_PROVISION_STAMP_BYTES;++i)if(stamp->bytes[i]!=0xff)return diagnostic->status;
    diagnostic->guard=jpeg_guard_verify(layout,observed,observed_count,device,sha256);
    diagnostic->status=JPEG_PROVISION_GUARD;
    if(diagnostic->guard!=JPEG_GUARD_OK && diagnostic->guard!=JPEG_GUARD_RESOURCE)return diagnostic->status;
    bool already=diagnostic->guard==JPEG_GUARD_OK;
    diagnostic->guard=stamp_identity(resource,stamp,sha256);
    if(diagnostic->guard!=JPEG_GUARD_OK)return diagnostic->status;
    if(already){diagnostic->status=JPEG_PROVISION_ALREADY;return diagnostic->status;}
    overlay_t overlay={device,resource,stamp};
    jpeg_nor_device_t prospective={&overlay,device->flash_bytes,device->page_bytes,overlay_read,NULL,NULL};
    diagnostic->guard=jpeg_guard_verify(layout,observed,observed_count,&prospective,sha256);
    if(diagnostic->guard!=JPEG_GUARD_OK)return diagnostic->status;
    uint8_t current[JPEG_PROVISION_STAMP_BYTES];
    diagnostic->status=compatible_stamp(device,resource->offset,stamp,current,diagnostic);
    if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    diagnostic->status=vacant(layout,device,diagnostic);
    if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    diagnostic->status=compatible_stamp(device,resource->offset,stamp,current,diagnostic);
    if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    if(memcmp(current+JPEG_PROVISION_HEADER_BYTES,stamp->bytes+JPEG_PROVISION_HEADER_BYTES,JPEG_PROVISION_ID_BYTES)) {
        diagnostic->status=write_part(device,resource->offset+JPEG_PROVISION_HEADER_BYTES,
            stamp->bytes+JPEG_PROVISION_HEADER_BYTES,JPEG_PROVISION_ID_BYTES,diagnostic);
        if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    }
    if(memcmp(current,stamp->bytes,JPEG_PROVISION_HEADER_BYTES)) {
        diagnostic->status=write_part(device,resource->offset,stamp->bytes,JPEG_PROVISION_HEADER_BYTES,diagnostic);
        if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    }
    uint8_t actual[JPEG_PROVISION_STAMP_BYTES];
    diagnostic->status=read_twice(device,resource->offset,actual,sizeof(actual),diagnostic);
    if(diagnostic->status!=JPEG_PROVISION_ALREADY)return diagnostic->status;
    if(memcmp(actual,stamp->bytes,sizeof(actual))){diagnostic->status=JPEG_PROVISION_VERIFY;return diagnostic->status;}
    diagnostic->guard=jpeg_guard_verify(layout,observed,observed_count,device,sha256);
    diagnostic->status=diagnostic->guard==JPEG_GUARD_OK ?
        (diagnostic->program_attempted ? JPEG_PROVISION_INSTALLED:JPEG_PROVISION_ALREADY):JPEG_PROVISION_GUARD;
    return diagnostic->status;
}
