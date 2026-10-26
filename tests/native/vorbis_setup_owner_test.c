// Complete retained-view comparison and failure-atomic allocation lifetimes.
#include "vorbis_setup_owner_test.h"
#include "native_vorbis_setup_owner.h"
#include "owner_cases.h"
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

enum {
    MAX_LIVE_BLOCKS = 16,
    PREFIX_BYTES = ((sizeof(uint64_t) + _Alignof(max_align_t) - 1) /
        _Alignof(max_align_t)) * _Alignof(max_align_t)
};

typedef struct {
    unsigned char *base, *data, *snapshot;
    size_t bytes;
    uint64_t canary;
} block_t;

typedef struct {
    block_t blocks[MAX_LIVE_BLOCKS];
    size_t live, bytes, attempts, releases, fail_at, failures;
    uint64_t tag;
    native_vorbis_setup_owner_t **watched_handle;
    const native_vorbis_setup_owner_t *old_handle;
    bool expect_null;
} allocator_context_t;

typedef struct {
    const uint32_t *expected;
    size_t capacity, at;
} comparison_t;

static owner_test_totals_t totals;
static size_t all_live, all_bytes;

static void check(bool condition) {
    assert(condition);
    if (!condition) abort();
    assert(totals.checks < UINT64_MAX);
    ++totals.checks;
}

static void check_guards(const block_t *block) {
    uint64_t before, after;
    memcpy(&before, block->data - sizeof(before), sizeof(before));
    memcpy(&after, block->data + block->bytes, sizeof(after));
    check(before == block->canary && after == block->canary);
}

static void *allocate(void *opaque, size_t bytes) {
    allocator_context_t *context = opaque;
    check(context != NULL && bytes != 0);
    check(bytes <= SIZE_MAX - PREFIX_BYTES - sizeof(uint64_t));
    check(context->attempts < SIZE_MAX);
    ++context->attempts;
    if (context->fail_at && context->attempts == context->fail_at) {
        ++context->failures;
        return NULL;
    }
    size_t slot = 0;
    while (slot < MAX_LIVE_BLOCKS && context->blocks[slot].base) ++slot;
    check(slot < MAX_LIVE_BLOCKS);
    unsigned char *base = malloc(bytes + PREFIX_BYTES + sizeof(uint64_t));
    check(base != NULL);
    unsigned char *data = base + PREFIX_BYTES;
    check((uintptr_t)data % _Alignof(max_align_t) == 0);
    uint64_t canary = UINT64_C(0x9d72f16eab5034c8) ^ context->tag ^ (uint64_t)context->attempts;
    memcpy(data - sizeof(canary), &canary, sizeof(canary));
    memcpy(data + bytes, &canary, sizeof(canary));
    memset(data, 0xa5, bytes);
    context->blocks[slot] = (block_t){base, data, NULL, bytes, canary};
    check(context->bytes <= SIZE_MAX - bytes && all_bytes <= SIZE_MAX - bytes);
    ++context->live;
    context->bytes += bytes;
    ++all_live;
    all_bytes += bytes;
    return data;
}

static void release(void *opaque, void *allocation) {
    allocator_context_t *context = opaque;
    check(context != NULL && allocation != NULL);
    if (context->watched_handle) {
        check(*context->watched_handle != context->old_handle);
        check(context->expect_null ? *context->watched_handle == NULL :
            *context->watched_handle != NULL);
    }
    size_t slot = 0;
    while (slot < MAX_LIVE_BLOCKS && context->blocks[slot].data != allocation) ++slot;
    check(slot < MAX_LIVE_BLOCKS);
    block_t *block = &context->blocks[slot];
    check(block->base != NULL);
    check_guards(block);
    check(context->live && all_live && context->bytes >= block->bytes && all_bytes >= block->bytes);
    --context->live;
    context->bytes -= block->bytes;
    --all_live;
    all_bytes -= block->bytes;
    ++context->releases;
    free(block->snapshot);
    memset(block->data, 0xdd, block->bytes);
    free(block->base);
    *block = (block_t){0};
}

static native_vorbis_setup_allocator_t callbacks(allocator_context_t *context) {
    return (native_vorbis_setup_allocator_t){context, allocate, release};
}

static void reset_attempts(allocator_context_t *context, size_t fail_at) {
    context->attempts = context->failures = 0;
    context->fail_at = fail_at;
    context->watched_handle = NULL;
}

static void check_empty(const allocator_context_t *context) {
    check(context->live == 0 && context->bytes == 0);
    for (size_t i = 0; i < MAX_LIVE_BLOCKS; ++i)
        check(!context->blocks[i].base && !context->blocks[i].data && !context->blocks[i].snapshot);
}

static void snapshot(allocator_context_t *context) {
    for (size_t i = 0; i < MAX_LIVE_BLOCKS; ++i) {
        block_t *block = &context->blocks[i];
        if (!block->base) continue;
        check(!block->snapshot);
        block->snapshot = malloc(block->bytes);
        check(block->snapshot != NULL);
        memcpy(block->snapshot, block->data, block->bytes);
    }
}

static void unchanged(const allocator_context_t *context) {
    size_t live = 0, bytes = 0;
    for (size_t i = 0; i < MAX_LIVE_BLOCKS; ++i) {
        const block_t *block = &context->blocks[i];
        if (!block->base) continue;
        check_guards(block);
        check(block->snapshot != NULL && memcmp(block->data, block->snapshot, block->bytes) == 0);
        ++live;
        check(bytes <= SIZE_MAX - block->bytes);
        bytes += block->bytes;
    }
    check(live == context->live && bytes == context->bytes);
}

static void contains(const allocator_context_t *context, const void *data, size_t bytes) {
    if (!bytes) { check(data == NULL); return; }
    check(data != NULL);
    uintptr_t pointer = (uintptr_t)data;
    bool found = false;
    for (size_t i = 0; i < MAX_LIVE_BLOCKS; ++i) {
        const block_t *block = &context->blocks[i];
        if (!block->base) continue;
        uintptr_t start = (uintptr_t)block->data;
        if (pointer >= start && pointer - start <= block->bytes &&
            bytes <= block->bytes - (size_t)(pointer - start)) found = true;
    }
    check(found);
}

static void emit(comparison_t *comparison, uint32_t value) {
    check(comparison->at < comparison->capacity);
    check(comparison->expected[comparison->at] == value);
    ++comparison->at;
}

static void emit64(comparison_t *comparison, uint64_t value) {
    emit(comparison, (uint32_t)value);
    emit(comparison, (uint32_t)(value >> 32));
}

static void getter_emit(comparison_t *comparison, size_t *count, uint32_t value) {
    check(*count < SIZE_MAX);
    ++*count;
    if (comparison) emit(comparison, value);
}

static size_t getters(const native_vorbis_setup_t *setup, comparison_t *comparison) {
    size_t count = 0;
#define EMIT(value) getter_emit(comparison, &count, (value))
#define ARRAY(values, length) do { \
    for (size_t j_ = 0; j_ < (size_t)(length); ++j_) EMIT((values)[j_]); \
} while (0)
    for (uint32_t i = 0; i < setup->layout.floor_count; ++i) {
        uint32_t type = 99;
        check(native_vorbis_setup_floor_type(setup, i, &type) == NATIVE_VORBIS_NUMERIC_OK);
        EMIT(type);
        if (type == 0) {
            native_vorbis_floor0_setup_t floor;
            check(native_vorbis_setup_floor0(setup, i, &floor) == NATIVE_VORBIS_NUMERIC_OK);
            EMIT(floor.order); EMIT(floor.rate); EMIT(floor.bark_map_size);
            EMIT(floor.amplitude_bits); EMIT(floor.amplitude_offset); EMIT(floor.book_count);
            ARRAY(floor.books, floor.book_count);
        } else {
            check(type == 1);
            native_vorbis_floor1_setup_t floor;
            check(native_vorbis_setup_floor1(setup, i, &floor) == NATIVE_VORBIS_NUMERIC_OK);
            EMIT(floor.partition_count); EMIT(floor.class_count); EMIT(floor.multiplier);
            EMIT(floor.range_bits); EMIT(floor.post_count);
            ARRAY(floor.partitions, floor.partition_count); ARRAY(floor.class_offsets, floor.class_count);
            ARRAY(floor.x, floor.post_count);
            for (uint32_t c = 0; c < floor.class_count; ++c) {
                native_vorbis_floor1_class_t cls;
                check(native_vorbis_setup_floor1_class(setup, &floor, c, &cls) == NATIVE_VORBIS_NUMERIC_OK);
                EMIT(cls.dimensions); EMIT(cls.subclass_bits); EMIT(cls.masterbook); EMIT(cls.book_count);
                ARRAY(cls.books, cls.book_count);
            }
        }
    }
    for (uint32_t i = 0; i < setup->layout.residue_count; ++i) {
        native_vorbis_residue_setup_t residue;
        check(native_vorbis_setup_residue(setup, i, &residue) == NATIVE_VORBIS_NUMERIC_OK);
        EMIT(residue.type); EMIT(residue.begin); EMIT(residue.end); EMIT(residue.partition_size);
        EMIT(residue.classifications); EMIT(residue.classbook); EMIT(residue.stage_book_count);
        ARRAY(residue.cascades, residue.classifications); ARRAY(residue.book_offsets, residue.classifications);
        ARRAY(residue.books, residue.stage_book_count);
    }
    for (uint32_t i = 0; i < setup->layout.mapping_count; ++i) {
        native_vorbis_mapping_setup_t mapping;
        check(native_vorbis_setup_mapping(setup, i, &mapping) == NATIVE_VORBIS_NUMERIC_OK);
        EMIT(mapping.submap_count); EMIT(mapping.coupling_count); EMIT(mapping.channels);
        ARRAY(mapping.coupling_pairs, 2 * mapping.coupling_count); ARRAY(mapping.mux, mapping.channels);
        ARRAY(mapping.submaps, 3 * mapping.submap_count);
    }
    for (uint32_t i = 0; i < setup->layout.mode_count; ++i) {
        native_vorbis_mode_setup_t mode;
        check(native_vorbis_setup_mode(setup, i, &mode) == NATIVE_VORBIS_NUMERIC_OK);
        EMIT(mode.blockflag); EMIT(mode.mapping);
    }
#undef ARRAY
#undef EMIT
    return count;
}

static bool quant_layout_equal(const native_vorbis_quant_layout_t *a,
                              const native_vorbis_quant_layout_t *b) {
    return a->dimensions == b->dimensions && a->entries == b->entries && a->lookup_type == b->lookup_type &&
        a->minimum_bits == b->minimum_bits && a->delta_bits == b->delta_bits && a->value_bits == b->value_bits &&
        a->sequence_p == b->sequence_p && a->multiplicand_count == b->multiplicand_count &&
        a->start_bit == b->start_bit && a->multiplicand_bit == b->multiplicand_bit && a->end_bit == b->end_bit;
}

static void compare_view(const owner_case_t *test, const native_vorbis_setup_t *view,
                         const allocator_context_t *context) {
    check(view != NULL && test->status == NATIVE_VORBIS_SETUP_OWNER_OK);
    comparison_t comparison = {test->expected, test->expected_count, 0};
    const native_vorbis_setup_layout_t *layout = &view->layout;
    const native_vorbis_identification_t *id = &layout->identification;
    check(view->book_count == layout->book_count && view->configuration_count == layout->configuration_count);
    check(view->book_count <= SIZE_MAX / sizeof(*view->books));
    check(view->configuration_count <= SIZE_MAX / sizeof(*view->configuration));
    contains(context, view, sizeof(*view));
    contains(context, view->books, view->book_count * sizeof(*view->books));
    contains(context, view->configuration, view->configuration_count * sizeof(*view->configuration));
#define EMIT(value) emit(&comparison, (value))
    EMIT(id->channels); EMIT(id->sample_rate); EMIT(id->bitrate_maximum_bits);
    EMIT(id->bitrate_nominal_bits); EMIT(id->bitrate_minimum_bits); EMIT(id->blocksize_0); EMIT(id->blocksize_1);
    emit64(&comparison, layout->end_bit); emit64(&comparison, layout->codeword_count);
    emit64(&comparison, layout->multiplicand_count);
    EMIT(layout->book_count); EMIT(layout->time_count); EMIT(layout->floor_count); EMIT(layout->residue_count);
    EMIT(layout->mapping_count); EMIT(layout->mode_count); EMIT(layout->configuration_count);
    EMIT(layout->floor_table); EMIT(layout->residue_table); EMIT(layout->mapping_table); EMIT(layout->mode_table);
    for (size_t i = 0; i < view->book_count; ++i) {
        const native_vorbis_codebook_t *book = &view->books[i];
        const native_vorbis_codebook_layout_t *book_layout = &book->layout;
        const native_vorbis_quant_layout_t *quant = &book_layout->quantization;
        check(quant_layout_equal(quant, &book->quantization.layout));
        check(book->word_count == book_layout->used_entries && book->quantization.storage_count == quant->multiplicand_count);
        check(book->word_count <= UINT32_MAX && book->word_count <= SIZE_MAX / sizeof(*book->words));
        check(book->quantization.storage_count <= UINT32_MAX &&
            book->quantization.storage_count <= SIZE_MAX / sizeof(*book->quantization.multiplicands));
        contains(context, book->words, book->word_count * sizeof(*book->words));
        contains(context, book->quantization.multiplicands,
            book->quantization.storage_count * sizeof(*book->quantization.multiplicands));
        emit64(&comparison, book_layout->start_bit); EMIT(book_layout->used_entries); EMIT(book_layout->maximum_length);
        EMIT(quant->dimensions); EMIT(quant->entries); EMIT(quant->lookup_type); EMIT(quant->minimum_bits);
        EMIT(quant->delta_bits); EMIT(quant->value_bits); EMIT(quant->sequence_p);
        emit64(&comparison, quant->multiplicand_count); emit64(&comparison, quant->start_bit);
        emit64(&comparison, quant->multiplicand_bit); emit64(&comparison, quant->end_bit);
        EMIT((uint32_t)book->word_count);
        for (size_t j = 0; j < book->word_count; ++j) {
            EMIT(book->words[j].code); EMIT(book->words[j].entry); EMIT(book->words[j].length);
        }
        EMIT((uint32_t)book->quantization.storage_count);
        for (size_t j = 0; j < book->quantization.storage_count; ++j) EMIT(book->quantization.multiplicands[j]);
    }
    EMIT((uint32_t)view->configuration_count);
    for (size_t i = 0; i < view->configuration_count; ++i) EMIT(view->configuration[i]);
    size_t count = getters(view, NULL);
    check(count <= UINT32_MAX);
    EMIT((uint32_t)count);
    check(getters(view, &comparison) == count);
    check(comparison.at == comparison.capacity);
#undef EMIT
}

static native_vorbis_setup_owner_status_t open_case(native_vorbis_setup_owner_t **owner,
    const owner_case_t *test, const native_vorbis_setup_allocator_t *allocator) {
    native_vorbis_setup_owner_status_t status = native_vorbis_setup_owner_replace(owner,
        test->identification, test->identification_bytes, test->identification_bits,
        test->setup, test->setup_bytes, test->setup_bits, allocator);
    if (status == NATIVE_VORBIS_SETUP_OWNER_OK) ++totals.successful_opens;
    return status;
}

static void clear_owner(native_vorbis_setup_owner_t **owner, allocator_context_t *context) {
    context->watched_handle = owner;
    context->old_handle = *owner;
    context->expect_null = true;
    native_vorbis_setup_owner_clear(owner);
    check(*owner == NULL);
    context->watched_handle = NULL;
    size_t releases = context->releases;
    native_vorbis_setup_owner_clear(owner);
    check(context->releases == releases);
    check_empty(context);
}

static void baseline_owner(native_vorbis_setup_owner_t **owner, allocator_context_t *context) {
    native_vorbis_setup_allocator_t allocator = callbacks(context);
    reset_attempts(context, 0);
    check(owner_cases[0].status == NATIVE_VORBIS_SETUP_OWNER_OK);
    check(open_case(owner, &owner_cases[0], &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
    compare_view(&owner_cases[0], native_vorbis_setup_owner_view(*owner), context);
    snapshot(context);
}

static void preserved(native_vorbis_setup_owner_t *owner, native_vorbis_setup_owner_t *old,
    const native_vorbis_setup_t *borrowed, const allocator_context_t *a, const allocator_context_t *c) {
    check(owner == old && native_vorbis_setup_owner_view(owner) == borrowed);
    unchanged(a);
    unchanged(c);
}

static void invalid_arguments(native_vorbis_setup_owner_t **owner, allocator_context_t *context) {
    const owner_case_t *valid = &owner_cases[0];
    native_vorbis_setup_owner_t *old = *owner;
    const native_vorbis_setup_t *borrowed = native_vorbis_setup_owner_view(old);
    native_vorbis_setup_allocator_t allocator = callbacks(context);
    reset_attempts(context, 1);
#define REPLACE(handle, source, id, bytes, bits, setup, setup_bytes, setup_bits) \
    native_vorbis_setup_owner_replace((handle), (id), (bytes), (bits), (setup), (setup_bytes), (setup_bits), (source))
#define VALID_ARGS valid->identification, valid->identification_bytes, valid->identification_bits, \
    valid->setup, valid->setup_bytes, valid->setup_bits
    check(native_vorbis_setup_owner_replace(NULL, VALID_ARGS, &allocator) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    check(native_vorbis_setup_owner_replace(owner, VALID_ARGS, NULL) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    native_vorbis_setup_allocator_t missing = allocator;
    missing.allocate = NULL;
    check(native_vorbis_setup_owner_replace(owner, VALID_ARGS, &missing) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    missing = allocator;
    missing.release = NULL;
    check(native_vorbis_setup_owner_replace(owner, VALID_ARGS, &missing) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    check(REPLACE(owner, &allocator, NULL, valid->identification_bytes, valid->identification_bits,
        valid->setup, valid->setup_bytes, valid->setup_bits) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    check(REPLACE(owner, &allocator, valid->identification, valid->identification_bytes, valid->identification_bits,
        NULL, valid->setup_bytes, valid->setup_bits) == NATIVE_VORBIS_SETUP_OWNER_INVALID);
    check(context->attempts == 0 && context->failures == 0);
    check(*owner == old && native_vorbis_setup_owner_view(*owner) == borrowed);
    native_vorbis_setup_owner_clear(NULL);
    check(native_vorbis_setup_owner_view(NULL) == NULL);
#undef VALID_ARGS
#undef REPLACE
}

static void prefix_failures(const owner_case_t *test, native_vorbis_setup_owner_t **owner,
    allocator_context_t *a, allocator_context_t *b, const allocator_context_t *c) {
    native_vorbis_setup_allocator_t allocator = callbacks(b);
    native_vorbis_setup_owner_t *old = *owner;
    const native_vorbis_setup_t *borrowed = native_vorbis_setup_owner_view(old);
    reset_attempts(b, 1);
    uint64_t trials = 0;
    for (uint64_t bits = 0; bits < 233; ++bits) {
        check(native_vorbis_setup_owner_replace(owner, test->identification, test->identification_bytes, bits,
            test->setup, test->setup_bytes, test->setup_bits, &allocator) == NATIVE_VORBIS_SETUP_OWNER_TRUNCATED);
        ++totals.parse_failures;
        check(b->attempts == 0 && b->failures == 0);
        preserved(*owner, old, borrowed, a, c);
        if (++trials % 64 == 0) owner_test_poll();
    }
    for (uint64_t bits = 0; bits < test->setup_end_bit; ++bits) {
        check(native_vorbis_setup_owner_replace(owner, test->identification, test->identification_bytes,
            test->identification_bits, test->setup, test->setup_bytes, bits, &allocator) == NATIVE_VORBIS_SETUP_OWNER_TRUNCATED);
        ++totals.parse_failures;
        check(b->attempts == 0 && b->failures == 0);
        preserved(*owner, old, borrowed, a, c);
        if (++trials % 64 == 0) owner_test_poll();
    }
}

size_t owner_test_case_count(void) { return OWNER_CASE_COUNT; }

void owner_test_run_case(size_t index, bool prefix_sweeps) {
    check(index < OWNER_CASE_COUNT);
    check(all_live == 0 && all_bytes == 0);
    const owner_case_t *test = &owner_cases[index];
    allocator_context_t a = {.tag = UINT64_C(0x11)};
    allocator_context_t b = {.tag = UINT64_C(0x22)};
    allocator_context_t c = {.tag = UINT64_C(0x33)};
    native_vorbis_setup_owner_t *owner = NULL, *independent = NULL;
    baseline_owner(&owner, &a);
    baseline_owner(&independent, &c);
    const native_vorbis_setup_t *independent_view = native_vorbis_setup_owner_view(independent);
    invalid_arguments(&owner, &b);
    unchanged(&a);
    unchanged(&c);
    native_vorbis_setup_allocator_t allocator = callbacks(&b);

    if (test->status != NATIVE_VORBIS_SETUP_OWNER_OK) {
        native_vorbis_setup_owner_t *old = owner;
        const native_vorbis_setup_t *borrowed = native_vorbis_setup_owner_view(owner);
        reset_attempts(&b, 1);
        check((int)open_case(&owner, test, &allocator) == test->status);
        ++totals.parse_failures;
        check(b.attempts == 0 && b.failures == 0);
        preserved(owner, old, borrowed, &a, &c);
        native_vorbis_setup_owner_t *empty = NULL;
        check(open_case(&empty, &owner_cases[0], &allocator) == NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY);
        ++totals.allocation_refusals;
        check(empty == NULL && b.attempts == 1 && b.failures == 1);
        check_empty(&b);
    } else {
        unsigned char *id = malloc(test->identification_bytes ? test->identification_bytes : 1);
        unsigned char *setup = malloc(test->setup_bytes ? test->setup_bytes : 1);
        check(id != NULL && setup != NULL);
        memcpy(id, test->identification, test->identification_bytes);
        memcpy(setup, test->setup, test->setup_bytes);
        reset_attempts(&b, 0);
        native_vorbis_setup_owner_t *created = NULL;
        check(native_vorbis_setup_owner_replace(&created, id, test->identification_bytes, test->identification_bits,
            setup, test->setup_bytes, test->setup_bits, &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
        ++totals.successful_opens;
        check(memcmp(id, test->identification, test->identification_bytes) == 0);
        check(memcmp(setup, test->setup, test->setup_bytes) == 0);
        memset(id, 0x5a, test->identification_bytes);
        memset(setup, 0xa5, test->setup_bytes);
        free(id);
        free(setup);
        compare_view(test, native_vorbis_setup_owner_view(created), &b);
        const native_vorbis_setup_layout_t *layout = &native_vorbis_setup_owner_view(created)->layout;
        size_t attempts = b.attempts;
        check(attempts == (size_t)3 + (layout->codeword_count != 0) + (layout->multiplicand_count != 0));
        allocator = (native_vorbis_setup_allocator_t){0};
        clear_owner(&created, &b);
        allocator = callbacks(&b);
        unchanged(&a);
        unchanged(&c);
        if (prefix_sweeps) prefix_failures(test, &owner, &a, &b, &c);
        for (size_t ordinal = 1; ordinal <= attempts; ++ordinal) {
            native_vorbis_setup_owner_t *empty = NULL;
            reset_attempts(&b, ordinal);
            check(open_case(&empty, test, &allocator) == NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY);
            ++totals.allocation_refusals;
            check(empty == NULL && b.attempts == ordinal && b.failures == 1);
            check_empty(&b);
            unchanged(&a);
            unchanged(&c);
            reset_attempts(&b, 0);
            check(open_case(&empty, test, &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
            compare_view(test, native_vorbis_setup_owner_view(empty), &b);
            clear_owner(&empty, &b);

            native_vorbis_setup_owner_t *old = owner;
            const native_vorbis_setup_t *borrowed = native_vorbis_setup_owner_view(owner);
            reset_attempts(&b, ordinal);
            check(open_case(&owner, test, &allocator) == NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY);
            ++totals.allocation_refusals;
            check(b.attempts == ordinal && b.failures == 1);
            check_empty(&b);
            preserved(owner, old, borrowed, &a, &c);
            reset_attempts(&b, 0);
            a.watched_handle = &owner;
            a.old_handle = owner;
            a.expect_null = false;
            check(open_case(&owner, test, &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
            a.watched_handle = NULL;
            check_empty(&a);
            compare_view(test, native_vorbis_setup_owner_view(owner), &b);
            unchanged(&c);
            clear_owner(&owner, &b);
            baseline_owner(&owner, &a);
            owner_test_poll();
        }
    }
    check(native_vorbis_setup_owner_view(independent) == independent_view);
    compare_view(&owner_cases[0], independent_view, &c);
    unchanged(&a);
    unchanged(&c);
    clear_owner(&owner, &a);
    clear_owner(&independent, &c);
    check_empty(&b);
    check(all_live == 0 && all_bytes == 0);
    ++totals.cases;
}

owner_test_totals_t owner_test_totals(void) {
    check(all_live == 0 && all_bytes == 0);
    return totals;
}
