// Own the existing exact parser's arrays without retaining incoming packets.
#include "native_vorbis_setup_owner.h"

struct native_vorbis_setup_owner {
    native_vorbis_setup_allocator_t allocator;
    native_vorbis_setup_storage_t storage;
    native_vorbis_setup_t view;
};

typedef struct {
    size_t books, words, multiplicands, configuration;
} storage_bytes_t;

static native_vorbis_setup_owner_status_t parser_status(native_vorbis_numeric_status_t status) {
    switch (status) {
    case NATIVE_VORBIS_NUMERIC_OK: return NATIVE_VORBIS_SETUP_OWNER_OK;
    case NATIVE_VORBIS_NUMERIC_TRUNCATED: return NATIVE_VORBIS_SETUP_OWNER_TRUNCATED;
    case NATIVE_VORBIS_NUMERIC_RANGE:
    case NATIVE_VORBIS_NUMERIC_CAPACITY: return NATIVE_VORBIS_SETUP_OWNER_RANGE;
    default: return NATIVE_VORBIS_SETUP_OWNER_INVALID;
    }
}

static bool object_bytes(uint64_t count, size_t unit, size_t *bytes) {
    if (count > SIZE_MAX / unit) return false;
    *bytes = (size_t)count * unit;
    return true;
}

static bool storage_bytes(const native_vorbis_setup_layout_t *layout, storage_bytes_t *bytes) {
    return object_bytes(layout->book_count, sizeof(native_vorbis_codebook_t), &bytes->books) &&
        object_bytes(layout->codeword_count, sizeof(native_vorbis_codeword_t), &bytes->words) &&
        object_bytes(layout->multiplicand_count, sizeof(uint16_t), &bytes->multiplicands) &&
        object_bytes(layout->configuration_count, sizeof(uint32_t), &bytes->configuration);
}

static void destroy(native_vorbis_setup_owner_t *owner) {
    if (!owner) return;
    native_vorbis_setup_allocator_t allocator = owner->allocator;
    if (owner->storage.configuration) allocator.release(allocator.context, owner->storage.configuration);
    if (owner->storage.multiplicands) allocator.release(allocator.context, owner->storage.multiplicands);
    if (owner->storage.words) allocator.release(allocator.context, owner->storage.words);
    if (owner->storage.books) allocator.release(allocator.context, owner->storage.books);
    allocator.release(allocator.context, owner);
}

native_vorbis_setup_owner_status_t native_vorbis_setup_owner_replace(
    native_vorbis_setup_owner_t **owner,
    const uint8_t *identification, size_t identification_bytes, uint64_t identification_bits,
    const uint8_t *setup, size_t setup_bytes, uint64_t setup_bits,
    const native_vorbis_setup_allocator_t *allocator) {
    if (!owner || !allocator || !allocator->allocate || !allocator->release)
        return NATIVE_VORBIS_SETUP_OWNER_INVALID;
    native_vorbis_setup_allocator_t callbacks = *allocator;
    native_vorbis_identification_t id;
    native_vorbis_numeric_status_t parsed = native_vorbis_identification_parse(
        identification, identification_bytes, identification_bits, &id);
    if (parsed != NATIVE_VORBIS_NUMERIC_OK) return parser_status(parsed);
    native_vorbis_setup_layout_t layout;
    parsed = native_vorbis_setup_measure(setup, setup_bytes, setup_bits, &id, &layout);
    if (parsed != NATIVE_VORBIS_NUMERIC_OK) return parser_status(parsed);
    storage_bytes_t bytes;
    if (!storage_bytes(&layout, &bytes)) return NATIVE_VORBIS_SETUP_OWNER_RANGE;

    native_vorbis_setup_owner_t *candidate = callbacks.allocate(callbacks.context, sizeof(*candidate));
    if (!candidate) return NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY;
    *candidate = (native_vorbis_setup_owner_t){.allocator = callbacks};
    candidate->storage.books = callbacks.allocate(callbacks.context, bytes.books);
    if (!candidate->storage.books) goto no_memory;
    if (bytes.words) {
        candidate->storage.words = callbacks.allocate(callbacks.context, bytes.words);
        if (!candidate->storage.words) goto no_memory;
    }
    if (bytes.multiplicands) {
        candidate->storage.multiplicands = callbacks.allocate(callbacks.context, bytes.multiplicands);
        if (!candidate->storage.multiplicands) goto no_memory;
    }
    candidate->storage.configuration = callbacks.allocate(callbacks.context, bytes.configuration);
    if (!candidate->storage.configuration) goto no_memory;
    candidate->storage.book_capacity = layout.book_count;
    candidate->storage.word_capacity = (size_t)layout.codeword_count;
    candidate->storage.multiplicand_capacity = (size_t)layout.multiplicand_count;
    candidate->storage.configuration_capacity = layout.configuration_count;
    parsed = native_vorbis_setup_materialize(setup, setup_bytes, setup_bits,
        &layout, &candidate->storage, &candidate->view);
    if (parsed != NATIVE_VORBIS_NUMERIC_OK) {
        destroy(candidate);
        return parser_status(parsed);
    }
    native_vorbis_setup_owner_t *previous = *owner;
    *owner = candidate;
    destroy(previous);
    return NATIVE_VORBIS_SETUP_OWNER_OK;

no_memory:
    destroy(candidate);
    return NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY;
}

const native_vorbis_setup_t *native_vorbis_setup_owner_view(
    const native_vorbis_setup_owner_t *owner) {
    return owner ? &owner->view : NULL;
}

void native_vorbis_setup_owner_clear(native_vorbis_setup_owner_t **owner) {
    if (!owner) return;
    native_vorbis_setup_owner_t *previous = *owner;
    *owner = NULL;
    destroy(previous);
}
