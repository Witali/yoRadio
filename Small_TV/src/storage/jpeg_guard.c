/* REQUESTED_CHANGE: verify matching immutable resources and partition ownership
 * before the JPEG scratch/cache transport can receive writable capabilities. */
#include "jpeg_guard.h"
#include <string.h>

static bool valid_ranges(const jpeg_nor_extent_t *ranges, unsigned count, uint32_t limit)
{
    /* Require sorted complete sectors, proving additions cannot overflow. */
    if (!ranges || !count || count > JPEG_NOR_MAX_EXTENTS)
        return false;
    uint32_t end = 0;
    for (unsigned i = 0; i < count; ++i) {
        uint32_t start = ranges[i].offset, bytes = ranges[i].bytes;
        if (!bytes || start % JPEG_NOR_SECTOR_BYTES || bytes % JPEG_NOR_SECTOR_BYTES ||
            start < end || start > limit || bytes > limit - start)
            return false;
        end = start + bytes;
    }
    return true;
}

static bool contained(uint32_t start, uint32_t bytes,
                      const jpeg_nor_extent_t *ranges, unsigned count)
{
    /* Permit adjacent protected ranges to cover one immutable payload. */
    for (unsigned i = 0; i < count && bytes; ++i) {
        if (start < ranges[i].offset)
            return false;
        uint32_t inside = start - ranges[i].offset;
        if (inside < ranges[i].bytes) {
            uint32_t chunk = ranges[i].bytes - inside;
            if (chunk > bytes)
                chunk = bytes;
            start += chunk;
            bytes -= chunk;
        }
    }
    return bytes == 0;
}

static bool same_partition(const jpeg_guard_partition_t *a, const jpeg_guard_partition_t *b)
{
    /* Compare fields explicitly; C struct padding is not a persisted identity. */
    return !memcmp(a->label, b->label, sizeof(a->label)) && a->type == b->type &&
        a->subtype == b->subtype && a->offset == b->offset && a->bytes == b->bytes &&
        a->flags == b->flags;
}

static bool valid_layout(const jpeg_guard_layout_t *layout,
                         const jpeg_guard_partition_t *observed, unsigned count,
                         uint32_t flash_bytes)
{
    /* Preflight every descriptor before doing I/O. Protected + allowed ranges
     * must tile the entire device exactly: no unclassified gap or overlap. */
    if (!layout->flash_bytes || layout->flash_bytes % JPEG_NOR_SECTOR_BYTES ||
        flash_bytes != layout->flash_bytes || !layout->partitions || !observed ||
        !count || count != layout->partition_count || count > JPEG_GUARD_MAX_PARTITIONS ||
        layout->assets_partition >= count || !layout->resources || !layout->resource_count ||
        layout->resource_count > JPEG_GUARD_MAX_RESOURCES ||
        !valid_ranges(layout->allowed, layout->allowed_count, flash_bytes) ||
        !valid_ranges(layout->protected_ranges, layout->protected_count, flash_bytes))
        return false;
    unsigned a = 0, p = 0;
    uint32_t end = 0;
    while (a < layout->allowed_count || p < layout->protected_count) {
        const jpeg_nor_extent_t *range;
        if (p == layout->protected_count || (a < layout->allowed_count &&
            layout->allowed[a].offset < layout->protected_ranges[p].offset))
            range = &layout->allowed[a++];
        else
            range = &layout->protected_ranges[p++];
        if (range->offset != end)
            return false;
        end += range->bytes;
    }
    if (end != flash_bytes)
        return false;
    end = 0;
    uint32_t app_end = 0;
    for (unsigned i = 0; i < count; ++i) {
        const jpeg_guard_partition_t *part = &layout->partitions[i];
        if (!part->label[0] || !memchr(part->label, 0, sizeof(part->label)) ||
            !same_partition(part, &observed[i]) || !part->bytes ||
            part->offset % JPEG_NOR_SECTOR_BYTES || part->bytes % JPEG_NOR_SECTOR_BYTES ||
            part->offset < end || part->offset > flash_bytes ||
            part->bytes > flash_bytes - part->offset)
            return false;
        end = part->offset + part->bytes;
        if (part->type == 0) {
            if (app_end || part->subtype != 0)
                return false; /* This native layout has one factory app, no OTA. */
            app_end = end;
        }
        if (i != layout->assets_partition &&
            !contained(part->offset, part->bytes, layout->protected_ranges, layout->protected_count))
            return false;
        for (unsigned j = 0; j < i; ++j)
            if (!memcmp(part->label, layout->partitions[j].label, sizeof(part->label)))
                return false;
    }
    const jpeg_guard_partition_t *assets = &layout->partitions[layout->assets_partition];
    if (assets->type != 1 || assets->subtype != 0x40 || assets->flags || !app_end ||
        app_end > assets->offset ||
        !contained(0, app_end, layout->protected_ranges, layout->protected_count) ||
        !contained(assets->offset + assets->bytes, flash_bytes - (assets->offset + assets->bytes),
                   layout->protected_ranges, layout->protected_count))
        return false;
    end = assets->offset;
    for (unsigned i = 0; i < layout->resource_count; ++i) {
        const jpeg_guard_resource_t *resource = &layout->resources[i];
        if (!resource->bytes || resource->offset < end ||
            resource->offset - assets->offset > assets->bytes ||
            resource->bytes > assets->bytes - (resource->offset - assets->offset) ||
            !contained(resource->offset, resource->bytes,
                       layout->protected_ranges, layout->protected_count))
            return false;
        end = resource->offset + resource->bytes;
    }
    return contained(assets->offset, layout->resources[0].offset - assets->offset,
                     layout->protected_ranges, layout->protected_count);
}

static jpeg_guard_result_t verify_resource(const jpeg_guard_resource_t *resource,
    const jpeg_nor_device_t *device, const jpeg_guard_sha256_t *hash)
{
    /* Stream bounded reads through the existing hash library; always release
     * hash state, and never infer success from a partial read or hash failure. */
    uint8_t buffer[JPEG_GUARD_READ_BYTES], digest[32];
    jpeg_guard_result_t result = JPEG_GUARD_HASH;
    if (hash->begin(hash->context))
        goto done;
    for (uint32_t offset = 0; offset < resource->bytes;) {
        uint32_t bytes = resource->bytes - offset;
        if (bytes > sizeof(buffer))
            bytes = sizeof(buffer);
        if (device->read(device->context, resource->offset + offset, buffer, bytes)) {
            result = JPEG_GUARD_IO;
            goto done;
        }
        if (hash->update(hash->context, buffer, bytes))
            goto done;
        offset += bytes;
    }
    if (!hash->finish(hash->context, digest))
        result = memcmp(digest, resource->sha256, sizeof(digest)) ?
            JPEG_GUARD_RESOURCE : JPEG_GUARD_OK;
done:
    hash->reset(hash->context);
    return result;
}

jpeg_guard_result_t jpeg_guard_verify(const jpeg_guard_layout_t *layout,
    const jpeg_guard_partition_t *observed, unsigned observed_count,
    const jpeg_nor_device_t *device, const jpeg_guard_sha256_t *sha256)
{
    /* No state/token is published: only complete current verification grants OK. */
    if (!layout || !device || !device->read || !sha256 || !sha256->begin ||
        !sha256->update || !sha256->finish || !sha256->reset)
        return JPEG_GUARD_ARGUMENT;
    if (!valid_layout(layout, observed, observed_count, device->flash_bytes))
        return JPEG_GUARD_LAYOUT;
    for (unsigned i = 0; i < layout->resource_count; ++i) {
        jpeg_guard_result_t result = verify_resource(&layout->resources[i], device, sha256);
        if (result != JPEG_GUARD_OK)
            return result;
    }
    return JPEG_GUARD_OK;
}
