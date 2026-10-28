/* REQUESTED_CHANGE: bounded sparse NOR I/O for the planned JPEG scratch/cache.
 * This core is not enabled in production until ownership and metadata gates exist. */
#include "jpeg_nor.h"
#include <string.h>

static bool valid_extents(const jpeg_nor_extent_t *extents, unsigned count,
                          uint32_t flash_bytes, uint32_t *capacity)
{
    /* Validate each complete sector without overflowing an address or total. */
    if (!extents || !count || count > JPEG_NOR_MAX_EXTENTS)
        return false;
    uint32_t previous_end = 0, total = 0;
    for (unsigned i = 0; i < count; ++i) {
        uint32_t start = extents[i].offset, bytes = extents[i].bytes;
        if (!bytes || start % JPEG_NOR_SECTOR_BYTES || bytes % JPEG_NOR_SECTOR_BYTES ||
            start < previous_end || start > flash_bytes || bytes > flash_bytes - start ||
            bytes > UINT32_MAX - total)
            return false;
        previous_end = start + bytes;
        total += bytes;
    }
    *capacity = total;
    return true;
}

static bool covered(const jpeg_nor_extent_t *extent,
                    const jpeg_nor_extent_t *allowed, unsigned count)
{
    /* Cover the whole physical extent, accepting adjacent allowed capabilities. */
    uint32_t cursor = extent->offset, remaining = extent->bytes;
    for (unsigned i = 0; i < count && remaining; ++i) {
        if (cursor < allowed[i].offset)
            return false;
        uint32_t inside = cursor - allowed[i].offset;
        if (inside < allowed[i].bytes) {
            uint32_t block = allowed[i].bytes - inside;
            if (block > remaining)
                block = remaining;
            cursor += block;
            remaining -= block;
        }
    }
    return remaining == 0;
}

static bool valid_buffer(const jpeg_nor_t *store, const void *data, size_t bytes)
{
    /* Reject pointer wrap and buffers that could overwrite/alias the live handle. */
    if (!bytes)
        return true;
    uintptr_t start = (uintptr_t)data, state = (uintptr_t)store;
    if (!data || bytes - 1 > UINTPTR_MAX - start)
        return false;
    return start > state ? start - state >= sizeof(*store) : bytes <= state - start;
}

static jpeg_nor_result_t check_request(const jpeg_nor_t *store, uint32_t offset,
                                      const void *data, size_t bytes)
{
    /* Reject the entire request before any cache/transport side effect. */
    if (!store || !store->open || store->failed)
        return JPEG_NOR_STATE;
    if (offset > store->logical_bytes || bytes > store->logical_bytes - offset)
        return JPEG_NOR_RANGE;
    return valid_buffer(store, data, bytes) ? JPEG_NOR_OK : JPEG_NOR_ARGUMENT;
}

static jpeg_nor_result_t io_read(jpeg_nor_t *store, uint32_t address, void *data, size_t bytes)
{
    /* Count actual transport requests; a failure poisons the handle until abort. */
    ++store->stats.read_calls;
    store->stats.read_bytes += bytes;
    store->last_io_error = store->device.read(store->device.context, address, data, bytes);
    if (store->last_io_error) {
        store->failed = true;
        return JPEG_NOR_IO;
    }
    return JPEG_NOR_OK;
}

static jpeg_nor_result_t flush_sector(jpeg_nor_t *store)
{
    /* Preserve every byte in the owned sector. Erase only if any requested bit
     * needs 0->1; after erase restore all non-FF pages, including unchanged data.
     * Partial failure is never retried against a possibly stale RAM image.
     * The metadata layer must invalidate the frame before this non-atomic I/O. */
    if (!store->dirty)
        return JPEG_NOR_OK;
    uint8_t previous[JPEG_NOR_MAX_PAGE_BYTES];
    const uint8_t *wanted = (const uint8_t *)store->sector_data;
    uint32_t changed = 0, nonempty = 0;
    bool erase = false;
    uint32_t page_bytes = store->device.page_bytes;
    unsigned pages = JPEG_NOR_SECTOR_BYTES / page_bytes;
    for (unsigned page = 0; page < pages; ++page) {
        uint32_t offset = page * page_bytes;
        jpeg_nor_result_t result = io_read(store, store->cached_sector + offset,
                                          previous, page_bytes);
        if (result != JPEG_NOR_OK)
            return result;
        for (uint32_t i = 0; i < page_bytes; ++i) {
            uint8_t value = wanted[offset + i];
            if (previous[i] != value)
                changed |= UINT32_C(1) << page;
            if (value != 0xff)
                nonempty |= UINT32_C(1) << page;
            if ((previous[i] & value) != value)
                erase = true;
        }
    }
    if (!changed) {
        store->dirty = false;
        return JPEG_NOR_OK;
    }
    if (erase) {
        ++store->stats.erase_calls;
        store->last_io_error = store->device.erase_sector(store->device.context,
                                                         store->cached_sector);
        if (store->last_io_error) {
            store->failed = true;
            return JPEG_NOR_IO;
        }
        ++store->stats.successful_erases;
        /* A short erase reported as success must not lead to programming 0->1.
         * Verify the entire erased sector before restoring any page. */
        for (unsigned page = 0; page < pages; ++page) {
            jpeg_nor_result_t result = io_read(store,
                store->cached_sector + page * page_bytes, previous, page_bytes);
            if (result != JPEG_NOR_OK)
                return result;
            for (uint32_t i = 0; i < page_bytes; ++i)
                if (previous[i] != 0xff) {
                    store->failed = true;
                    return JPEG_NOR_VERIFY;
                }
        }
    }
    uint32_t selected = erase ? nonempty : changed;
    for (unsigned page = 0; page < pages; ++page) {
        if (!(selected & (UINT32_C(1) << page)))
            continue;
        uint32_t offset = page * page_bytes;
        ++store->stats.program_calls;
        store->stats.program_bytes += page_bytes;
        store->last_io_error = store->device.program(store->device.context,
            store->cached_sector + offset, wanted + offset, page_bytes);
        if (store->last_io_error) {
            store->failed = true;
            return JPEG_NOR_IO;
        }
        store->stats.successful_program_bytes += page_bytes;
    }
    /* Verify even a transport reporting success: silent/short operations must
     * not let higher-level metadata publish a corrupt image as complete. */
    for (unsigned page = 0; page < pages; ++page) {
        uint32_t offset = page * page_bytes;
        jpeg_nor_result_t result = io_read(store, store->cached_sector + offset,
                                          previous, page_bytes);
        if (result != JPEG_NOR_OK)
            return result;
        if (memcmp(previous, wanted + offset, page_bytes)) {
            store->failed = true;
            return JPEG_NOR_VERIFY;
        }
    }
    store->dirty = false;
    return JPEG_NOR_OK;
}

static uint32_t physical_address(const jpeg_nor_t *store, uint32_t offset)
{
    /* Translate a prevalidated logical byte across noncontiguous owned extents. */
    for (unsigned i = 0; i < store->extent_count; ++i) {
        if (offset < store->extents[i].bytes)
            return store->extents[i].offset + offset;
        offset -= store->extents[i].bytes;
    }
    return UINT32_MAX; /* Not reachable for a valid nonempty request. */
}

jpeg_nor_result_t jpeg_nor_open(jpeg_nor_t *store, const jpeg_nor_device_t *device,
    const jpeg_nor_extent_t *extents, unsigned extent_count, uint32_t logical_bytes,
    const jpeg_nor_extent_t *allowed, unsigned allowed_count)
{
    /* Copy an entirely validated capability; opening never reads or writes flash. */
    if (!store || !device || !logical_bytes || !device->read || !device->program ||
        !device->erase_sector || !device->flash_bytes ||
        device->page_bytes < JPEG_NOR_SECTOR_BYTES / 32 ||
        device->page_bytes > JPEG_NOR_MAX_PAGE_BYTES ||
        JPEG_NOR_SECTOR_BYTES % device->page_bytes)
        return JPEG_NOR_ARGUMENT;
    if (store->open)
        return JPEG_NOR_STATE;
    uint32_t capacity, allowed_capacity;
    if (!valid_extents(extents, extent_count, device->flash_bytes, &capacity) ||
        !valid_extents(allowed, allowed_count, device->flash_bytes, &allowed_capacity) ||
        ((uint64_t)logical_bytes + JPEG_NOR_SECTOR_BYTES - 1) /
            JPEG_NOR_SECTOR_BYTES * JPEG_NOR_SECTOR_BYTES != capacity)
        return JPEG_NOR_RANGE;
    for (unsigned i = 0; i < extent_count; ++i)
        if (!covered(&extents[i], allowed, allowed_count))
            return JPEG_NOR_RANGE;
    /* Arguments may point into a previously closed handle; copy before clearing. */
    jpeg_nor_device_t saved_device = *device;
    jpeg_nor_extent_t saved_extents[JPEG_NOR_MAX_EXTENTS];
    memcpy(saved_extents, extents, extent_count * sizeof(*extents));
    memset(store, 0, sizeof(*store));
    store->device = saved_device;
    memcpy(store->extents, saved_extents, extent_count * sizeof(*extents));
    store->extent_count = extent_count;
    store->logical_bytes = logical_bytes;
    store->open = true;
    return JPEG_NOR_OK;
}

jpeg_nor_result_t jpeg_nor_read(jpeg_nor_t *store, uint32_t offset, void *data, size_t bytes)
{
    /* Read dirty bytes coherently without flushing or evicting the one-sector cache. */
    jpeg_nor_result_t result = check_request(store, offset, data, bytes);
    if (result != JPEG_NOR_OK)
        return result;
    store->stats.logical_read_bytes += bytes;
    uint8_t *out = data;
    while (bytes) {
        uint32_t address = physical_address(store, offset);
        uint32_t inside = address % JPEG_NOR_SECTOR_BYTES;
        size_t block = JPEG_NOR_SECTOR_BYTES - inside;
        if (block > bytes)
            block = bytes;
        if (store->cached && store->cached_sector == address - inside)
            memcpy(out, (const uint8_t *)store->sector_data + inside, block);
        else {
            result = io_read(store, address, out, block);
            if (result != JPEG_NOR_OK)
                return result;
        }
        out += block;
        offset += (uint32_t)block;
        bytes -= block;
    }
    return JPEG_NOR_OK;
}

jpeg_nor_result_t jpeg_nor_write(jpeg_nor_t *store, uint32_t offset,
                                 const void *data, size_t bytes)
{
    /* Buffer partial writes and flush only on sector eviction or explicit sync. */
    jpeg_nor_result_t result = check_request(store, offset, data, bytes);
    if (result != JPEG_NOR_OK)
        return result;
    store->stats.logical_write_bytes += bytes;
    const uint8_t *in = data;
    while (bytes) {
        uint32_t address = physical_address(store, offset);
        uint32_t inside = address % JPEG_NOR_SECTOR_BYTES;
        uint32_t sector = address - inside;
        if (!store->cached || store->cached_sector != sector) {
            result = flush_sector(store);
            if (result != JPEG_NOR_OK)
                return result;
            result = io_read(store, sector, store->sector_data, JPEG_NOR_SECTOR_BYTES);
            if (result != JPEG_NOR_OK)
                return result;
            store->cached_sector = sector;
            store->cached = true;
            ++store->stats.cache_loads;
        }
        size_t block = JPEG_NOR_SECTOR_BYTES - inside;
        if (block > bytes)
            block = bytes;
        uint8_t *target = (uint8_t *)store->sector_data + inside;
        if (memcmp(target, in, block)) {
            memcpy(target, in, block);
            store->dirty = true;
        }
        in += block;
        offset += (uint32_t)block;
        bytes -= block;
    }
    return JPEG_NOR_OK;
}

jpeg_nor_result_t jpeg_nor_sync(jpeg_nor_t *store)
{
    /* Persist the dirty sector, retaining transport counters and failure state. */
    if (!store || !store->open || store->failed)
        return JPEG_NOR_STATE;
    return flush_sector(store);
}

jpeg_nor_result_t jpeg_nor_close(jpeg_nor_t *store)
{
    /* A successful close flushes; failed handles require explicit abort instead. */
    jpeg_nor_result_t result = jpeg_nor_sync(store);
    if (result == JPEG_NOR_OK) {
        store->open = false;
        store->cached = false;
    }
    return result;
}

void jpeg_nor_abort(jpeg_nor_t *store)
{
    /* Release only this handle, never writing a cancelled or failed RAM image. */
    if (store) {
        store->open = false;
        store->cached = false;
        store->dirty = false;
    }
}
