/* REQUESTED_CHANGE: atomic JPEG cache metadata, durable invalidation before
 * in-place data writes, and verified publication/recovery from two NOR banks. */
#include "jpeg_journal.h"
#include <string.h>

#define ENTRY_BASE 112u
#define ENTRY_BYTES 72u
#define CRC_OFFSET 508u
static const uint8_t body_magic[8] = {'S','T','V','J','C','0','1',0};
static const uint8_t commit_magic[8] = {'S','T','V','C','M','T','1',0};

static uint32_t get32(const uint8_t *data)
{
    /* Explicit little endian; wire data never aliases a native C struct. */
    return (uint32_t)data[0] | (uint32_t)data[1]<<8 | (uint32_t)data[2]<<16 | (uint32_t)data[3]<<24;
}

static void put32(uint8_t *data, uint32_t value)
{
    /* Encode unaligned persistent fields on both host and RV32. */
    for (unsigned i = 0; i < 4; ++i) data[i] = (uint8_t)(value>>(8*i));
}

static uint64_t get64(const uint8_t *data)
{
    /* Generation zero is reserved for the lack of any valid snapshot. */
    return get32(data) | (uint64_t)get32(data+4)<<32;
}

static void put64(uint8_t *data, uint64_t value)
{
    /* Keep sequence ordering independent of host word size and struct padding. */
    put32(data,(uint32_t)value); put32(data+4,(uint32_t)(value>>32));
}

static uint32_t body_crc(const uint8_t *body)
{
    /* CRC-32/ISO-HDLC over the fixed body prefix; detection, not authentication. */
    uint32_t crc = UINT32_MAX;
    for (unsigned i = 0; i < CRC_OFFSET; ++i) {
        crc ^= body[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc>>1) ^ ((crc&1) ? UINT32_C(0xedb88320) : 0);
    }
    return crc ^ UINT32_MAX;
}

static bool live(const jpeg_journal_t *journal)
{
    /* Metadata transport/read-back failures require explicit cold-state recovery. */
    return journal && journal->open && !journal->failed;
}

static jpeg_journal_result_t read_flash(jpeg_journal_t *journal, uint32_t address, void *data, size_t bytes)
{
    /* Count issued requests, including a partially completed failing read. */
    ++journal->read_calls;
    journal->last_io_error = journal->device.read(journal->device.context,address,data,bytes);
    if (!journal->last_io_error) return JPEG_JOURNAL_OK;
    journal->failed = true;
    return JPEG_JOURNAL_IO;
}

static bool config_valid(const jpeg_nor_device_t *device, const jpeg_journal_config_t *config,
                          const jpeg_nor_extent_t *allowed, unsigned count)
{
    /* Validate whole erase sectors and the complete sorted capability list. */
    if (!device || !config || !allowed || !count || count > JPEG_NOR_MAX_EXTENTS ||
        !device->read || !device->program || !device->erase_sector ||
        (device->page_bytes != 128 && device->page_bytes != 256) ||
        !config->frame_bytes || !config->source_limit || config->banks[0] == config->banks[1]) return false;
    uint32_t end = 0;
    bool covered[2] = {false,false};
    for (unsigned i = 0; i < count; ++i) {
        const jpeg_nor_extent_t *range = &allowed[i];
        if (!range->bytes || range->offset % JPEG_NOR_SECTOR_BYTES || range->bytes % JPEG_NOR_SECTOR_BYTES ||
            range->offset < end || range->offset > device->flash_bytes ||
            range->bytes > device->flash_bytes-range->offset) return false;
        end = range->offset+range->bytes;
        for (unsigned bank = 0; bank < 2; ++bank)
            if (config->banks[bank] % JPEG_NOR_SECTOR_BYTES == 0 &&
                config->banks[bank] >= range->offset && config->banks[bank]-range->offset < range->bytes &&
                JPEG_NOR_SECTOR_BYTES <= range->bytes-(config->banks[bank]-range->offset)) covered[bank] = true;
    }
    return covered[0] && covered[1];
}

static void make_footer(const jpeg_journal_t *journal, uint8_t *footer)
{
    /* Commit page is programmed last. Every non-FF byte must match on recovery. */
    memset(footer,0xff,journal->device.page_bytes);
    memcpy(footer,commit_magic,sizeof(commit_magic));
    put64(footer+8,get64(journal->body+16));
    uint32_t crc = get32(journal->body+CRC_OFFSET);
    put32(footer+16,crc); put32(footer+20,crc^UINT32_MAX);
}

static bool valid_body(const uint8_t *body)
{
    /* Accept only canonical bounded v1 records; identity matching is separate
     * so a newer foreign snapshot can never resurrect an older matching one. */
    if (memcmp(body,body_magic,8) || get32(body+8) != 1 ||
        get32(body+12) != JPEG_JOURNAL_BODY_BYTES || !get64(body+16) ||
        !get32(body+88) || !get32(body+92) || get32(body+96) != JPEG_JOURNAL_SLOTS ||
        body_crc(body) != get32(body+CRC_OFFSET)) return false;
    for (unsigned i = 100; i < ENTRY_BASE; ++i) if (body[i]) return false;
    for (unsigned slot = 0; slot < JPEG_JOURNAL_SLOTS; ++slot) {
        const uint8_t *entry = body+ENTRY_BASE+slot*ENTRY_BYTES;
        uint32_t ready = get32(entry), bytes = get32(entry+4);
        if (ready > 1 || (ready && (!bytes || bytes > get32(body+92)))) return false;
        if (!ready)
            for (unsigned i = 0; i < ENTRY_BYTES; ++i) if (entry[i]) return false;
    }
    for (unsigned i = ENTRY_BASE+JPEG_JOURNAL_SLOTS*ENTRY_BYTES; i < CRC_OFFSET; ++i)
        if (body[i]) return false;
    return true;
}

static bool valid_footer(const jpeg_journal_t *journal, const uint8_t *footer)
{
    /* Validate fields/padding directly instead of allocating another256-byte
     * expected page on the ESP32-C2 boot stack. Semantics match make_footer. */
    uint32_t crc = get32(journal->body+CRC_OFFSET);
    if (memcmp(footer,commit_magic,8) || get64(footer+8) != get64(journal->body+16) ||
        get32(footer+16) != crc || get32(footer+20) != (crc^UINT32_MAX)) return false;
    for (unsigned i = 24; i < journal->device.page_bytes; ++i) if (footer[i] != 0xff) return false;
    return true;
}

static jpeg_journal_result_t load_bank(jpeg_journal_t *journal, unsigned bank, bool *valid)
{
    /* Read errors cannot be treated as empty: an unread bank might be newer. */
    uint8_t footer[JPEG_NOR_MAX_PAGE_BYTES];
    *valid = false;
    uint32_t address = journal->config.banks[bank];
    for (unsigned offset = 0; offset < JPEG_JOURNAL_BODY_BYTES; offset += JPEG_NOR_MAX_PAGE_BYTES) {
        jpeg_journal_result_t result = read_flash(journal,address+offset,
            journal->body+offset,JPEG_NOR_MAX_PAGE_BYTES);
        if (result != JPEG_JOURNAL_OK) return result;
    }
    jpeg_journal_result_t result = read_flash(journal,address+JPEG_NOR_SECTOR_BYTES-journal->device.page_bytes,
                                              footer,journal->device.page_bytes);
    if (result != JPEG_JOURNAL_OK || !valid_body(journal->body)) return result;
    *valid = valid_footer(journal,footer);
    return JPEG_JOURNAL_OK;
}

static void adopt_body(jpeg_journal_t *journal, unsigned bank)
{
    /* Keep generation even across a layout/codec change; never wrap or roll back. */
    journal->bank = bank; journal->have_head = true;
    journal->generation = get64(journal->body+16);
    journal->matching = !memcmp(journal->body+24,journal->config.layout_id,32) &&
        !memcmp(journal->body+56,journal->config.codec_id,32) &&
        get32(journal->body+88) == journal->config.frame_bytes && get32(journal->body+92) == journal->config.source_limit;
    memset(journal->entries,0,sizeof(journal->entries));
    if (!journal->matching) return;
    for (unsigned slot = 0; slot < JPEG_JOURNAL_SLOTS; ++slot) {
        const uint8_t *wire = journal->body+ENTRY_BASE+slot*ENTRY_BYTES;
        jpeg_journal_entry_t *entry = &journal->entries[slot];
        entry->ready = get32(wire) != 0; entry->source_bytes = get32(wire+4);
        memcpy(entry->source_sha256,wire+8,32); memcpy(entry->frame_sha256,wire+40,32);
    }
}

static void encode_body(jpeg_journal_t *journal, unsigned slot, const jpeg_journal_entry_t *replacement)
{
    /* Full five-entry snapshot: updating one slot preserves every other entry. */
    uint8_t *body = journal->body;
    memset(body,0,JPEG_JOURNAL_BODY_BYTES); memcpy(body,body_magic,8);
    put32(body+8,1); put32(body+12,JPEG_JOURNAL_BODY_BYTES); put64(body+16,journal->generation+1);
    memcpy(body+24,journal->config.layout_id,32); memcpy(body+56,journal->config.codec_id,32);
    put32(body+88,journal->config.frame_bytes); put32(body+92,journal->config.source_limit);
    put32(body+96,JPEG_JOURNAL_SLOTS);
    for (unsigned i = 0; i < JPEG_JOURNAL_SLOTS; ++i) {
        const jpeg_journal_entry_t *entry = i == slot ? replacement : &journal->entries[i];
        if (!entry->ready) continue;
        uint8_t *wire = body+ENTRY_BASE+i*ENTRY_BYTES;
        put32(wire,1); put32(wire+4,entry->source_bytes);
        memcpy(wire+8,entry->source_sha256,32); memcpy(wire+40,entry->frame_sha256,32);
    }
    put32(body+CRC_OFFSET,body_crc(body));
}

static jpeg_journal_result_t verify_bytes(jpeg_journal_t *journal, uint32_t address,
                                          const uint8_t *expected, uint32_t bytes, bool erased)
{
    /* Verify whole erased bank, body, or commit page with bounded temporary RAM. */
    uint8_t buffer[JPEG_NOR_MAX_PAGE_BYTES];
    for (uint32_t offset = 0; offset < bytes;) {
        uint32_t chunk = bytes-offset;
        if (chunk > sizeof(buffer)) chunk = sizeof(buffer);
        jpeg_journal_result_t result = read_flash(journal,address+offset,buffer,chunk);
        if (result != JPEG_JOURNAL_OK) return result;
        for (uint32_t i = 0; i < chunk; ++i)
            if (buffer[i] != (erased ? 0xff : expected[offset+i])) {
                journal->failed = true; return JPEG_JOURNAL_VERIFY;
            }
        offset += chunk;
    }
    return JPEG_JOURNAL_OK;
}

static jpeg_journal_result_t program_page(jpeg_journal_t *journal, uint32_t address, const uint8_t *data)
{
    /* Never retry a failed program using potentially stale RAM assumptions. */
    ++journal->program_calls;
    journal->last_io_error = journal->device.program(journal->device.context,address,data,journal->device.page_bytes);
    if (!journal->last_io_error) return JPEG_JOURNAL_OK;
    journal->failed = true; return JPEG_JOURNAL_IO;
}

static jpeg_journal_result_t snapshot(jpeg_journal_t *journal, unsigned slot, const jpeg_journal_entry_t *entry)
{
    /* The current head stays untouched. Commit the other bank only after erase
     * and full body verification; failed publication leaves either old or new
     * complete metadata on cold boot, never authority from an unfinished body. */
    if (journal->generation == UINT64_MAX) return JPEG_JOURNAL_LIMIT;
    encode_body(journal,slot,entry);
    unsigned target = journal->have_head ? journal->bank^1u : 0;
    uint32_t address = journal->config.banks[target];
    ++journal->erase_calls;
    journal->last_io_error = journal->device.erase_sector(journal->device.context,address);
    if (journal->last_io_error) {journal->failed = true; return JPEG_JOURNAL_IO;}
    jpeg_journal_result_t result = verify_bytes(journal,address,NULL,JPEG_NOR_SECTOR_BYTES,true);
    if (result != JPEG_JOURNAL_OK) return result;
    for (unsigned offset = 0; offset < JPEG_JOURNAL_BODY_BYTES; offset += journal->device.page_bytes) {
        result = program_page(journal,address+offset,journal->body+offset);
        if (result != JPEG_JOURNAL_OK) return result;
    }
    result = verify_bytes(journal,address,journal->body,JPEG_JOURNAL_BODY_BYTES,false);
    if (result != JPEG_JOURNAL_OK) return result;
    uint8_t footer[JPEG_NOR_MAX_PAGE_BYTES];
    make_footer(journal,footer);
    result = program_page(journal,address+JPEG_NOR_SECTOR_BYTES-journal->device.page_bytes,footer);
    if (result != JPEG_JOURNAL_OK) return result;
    result = verify_bytes(journal,address+JPEG_NOR_SECTOR_BYTES-journal->device.page_bytes,
                           footer,journal->device.page_bytes,false);
    if (result == JPEG_JOURNAL_OK) adopt_body(journal,target);
    return result;
}

jpeg_journal_result_t jpeg_journal_open(jpeg_journal_t *journal,
    const jpeg_nor_device_t *device, const jpeg_journal_config_t *config,
    const jpeg_nor_extent_t *allowed, unsigned allowed_count)
{
    /* Only successful full-bank reads can establish the newest durable state. */
    if (!journal) return JPEG_JOURNAL_ARGUMENT;
    if (journal->open) return JPEG_JOURNAL_STATE;
    if (!config_valid(device,config,allowed,allowed_count)) return JPEG_JOURNAL_ARGUMENT;
    jpeg_nor_device_t saved_device = *device;
    jpeg_journal_config_t saved_config = *config;
    memset(journal,0,sizeof(*journal)); journal->device = saved_device; journal->config = saved_config;
    journal->open = true;
    for (unsigned bank = 0; bank < 2; ++bank) {
        bool valid;
        jpeg_journal_result_t result = load_bank(journal,bank,&valid);
        if (result != JPEG_JOURNAL_OK) return result;
        if (!valid) continue;
        uint64_t generation = get64(journal->body+16);
        if (journal->have_head && generation == journal->generation) {
            journal->failed = true; return JPEG_JOURNAL_AMBIGUOUS;
        }
        if (!journal->have_head || generation > journal->generation) adopt_body(journal,bank);
    }
    return JPEG_JOURNAL_OK;
}

jpeg_journal_result_t jpeg_journal_begin(jpeg_journal_t *journal, unsigned slot)
{
    /* Successful return is the sole permission to overwrite this cache/source. */
    if (!live(journal) || journal->pending) return JPEG_JOURNAL_STATE;
    if (slot >= JPEG_JOURNAL_SLOTS) return JPEG_JOURNAL_ARGUMENT;
    if (journal->generation == UINT64_MAX) return JPEG_JOURNAL_LIMIT;
    if (!journal->have_head || !journal->matching || journal->entries[slot].ready) {
        jpeg_journal_entry_t invalid = {0};
        jpeg_journal_result_t result = snapshot(journal,slot,&invalid);
        if (result != JPEG_JOURNAL_OK) return result;
    }
    journal->pending = true; journal->pending_slot = slot;
    return JPEG_JOURNAL_OK;
}

jpeg_journal_result_t jpeg_journal_publish(jpeg_journal_t *journal,
    uint32_t source_bytes, const uint8_t source_sha256[32], const uint8_t frame_sha256[32],
    const jpeg_journal_verifier_t *verifier)
{
    /* Verify data before the first publication erase/program, not afterwards. */
    if (!live(journal) || !journal->pending) return JPEG_JOURNAL_STATE;
    if (!source_bytes || source_bytes > journal->config.source_limit || !source_sha256 ||
        !frame_sha256 || !verifier || !verifier->verify) return JPEG_JOURNAL_ARGUMENT;
    jpeg_journal_entry_t entry = {0};
    entry.ready = true; entry.source_bytes = source_bytes;
    memcpy(entry.source_sha256,source_sha256,32); memcpy(entry.frame_sha256,frame_sha256,32);
    if (verifier->verify(verifier->context,journal->pending_slot,journal->config.frame_bytes,entry.frame_sha256))
        return JPEG_JOURNAL_VERIFY;
    jpeg_journal_result_t result = snapshot(journal,journal->pending_slot,&entry);
    if (result == JPEG_JOURNAL_OK) journal->pending = false;
    return result;
}

jpeg_journal_result_t jpeg_journal_lookup(jpeg_journal_t *journal, unsigned slot,
    uint32_t source_bytes, const uint8_t source_sha256[32], const jpeg_journal_verifier_t *verifier)
{
    /* A prior-generation fallback is safe only after hashing current frame data. */
    if (!live(journal)) return JPEG_JOURNAL_STATE;
    if (slot >= JPEG_JOURNAL_SLOTS || !source_bytes || source_bytes > journal->config.source_limit ||
        !source_sha256 || !verifier || !verifier->verify) return JPEG_JOURNAL_ARGUMENT;
    const jpeg_journal_entry_t *entry = &journal->entries[slot];
    if (!entry->ready || entry->source_bytes != source_bytes || memcmp(entry->source_sha256,source_sha256,32))
        return JPEG_JOURNAL_MISS;
    return verifier->verify(verifier->context,slot,journal->config.frame_bytes,entry->frame_sha256) ?
        JPEG_JOURNAL_VERIFY : JPEG_JOURNAL_OK;
}

void jpeg_journal_cancel(jpeg_journal_t *journal)
{
    /* Invalidation already persisted; a cancelled decode never republishes it. */
    if (journal) journal->pending = false;
}

void jpeg_journal_abort(jpeg_journal_t *journal)
{
    /* No implicit write or RAM-state retry after uncertain completion. */
    if (journal) {journal->open = false; journal->pending = false;}
}
