/* Test of our exact included parser; no vendor library or decoder handles.
 * Consumer seam follows the public BSD Tremor codebook.c decode formats at
 * revision 0ad0141e864cfbb130db4f22e279d421832e7336. It adds bounds and restricts
 * the point/formats to the declared valid fixtures. See PROVENANCE.md/COPYING.
 * It is not a PCM synthesis implementation or a byte-identical upstream file.
 */
#include <inttypes.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pinned/production/vorbis_repair/setup.c"
#include "unit_data.h"

#define P "CYD_VORBIS_OWNED_BOOK_"
static unsigned current_case, current_probe;
static bool failed;

static void require_unit(bool ok, const char *reason) {
    if (ok) return;
    failed = true;
    printf(P "FAILURE case=%u probe=%u reason=%s core=%d\n",
           current_case, current_probe, reason, xPortGetCoreID());
    fflush(stdout);
    for (;;) vTaskDelay(1); /* No reset, hidden retry or apparent COMPLETE. */
}

typedef struct { uint8_t *base, *data; size_t bytes; bool live; } allocation_t;
static allocation_t allocations[32];
static unsigned live_allocations;
static size_t owned_size(const void *data) {
    for (unsigned i = 0; i < 32; ++i)
        if (allocations[i].live && allocations[i].data == data) return allocations[i].bytes;
    require_unit(false, "owned_pointer_required");
    return 0;
}
static bool allocation_guards(const allocation_t *a) {
    for (unsigned i = 0; i < 16; ++i)
        if (a->base[i] != 0xa5 || a->data[a->bytes + i] != 0x5a) return false;
    return true;
}
static void all_guards(void) {
    for (unsigned i = 0; i < 32; ++i)
        if (allocations[i].live) require_unit(allocation_guards(allocations + i), "owned_allocation_guards");
}
void *media_lib_module_calloc(const char *module, size_t count, size_t bytes) {
    require_unit(module && !strcmp(module, "AUD_Codec") && count && bytes && count <= SIZE_MAX / bytes,
                 "bounded_allocator_arguments");
    bytes *= count;
    require_unit(bytes <= 8192, "declared_allocation_bound");
    unsigned slot = 0;
    while (slot < 32 && allocations[slot].live) ++slot;
    require_unit(slot < 32, "allocation_tracking_capacity");
    uint8_t *base = calloc(1, bytes + 32);
    require_unit(base != NULL, "actual_allocation_succeeded");
    memset(base, 0xa5, 16);
    memset(base + 16 + bytes, 0x5a, 16);
    allocations[slot] = (allocation_t){base, base + 16, bytes, true};
    ++live_allocations;
    return base + 16;
}
void media_lib_free(void *data) {
    if (!data) return;
    for (unsigned i = 0; i < 32; ++i) {
        allocation_t *a = allocations + i;
        if (a->live && a->data == data) {
            require_unit(allocation_guards(a), "freed_allocation_guards");
            free(a->base);
            a->live = false;
            --live_allocations;
            return;
        }
    }
    require_unit(false, "single_owned_free");
}

typedef struct {
    const uint8_t *data;
    size_t bytes, position, end;
    oggpack_buffer *tag;
    bool eop;
} bit_view_t;
static bit_view_t view;
static void begin_bits(oggpack_buffer *tag, const uint8_t *data, size_t bytes, size_t start, size_t end) {
    require_unit(data && start <= end && end <= bytes * 8U, "valid_bounded_bitspan");
    memset(tag, 0, sizeof(*tag));
    view = (bit_view_t){data, bytes, start, end, tag, false};
}
static long look_bits(int bits) {
    require_unit(bits >= 0 && bits <= 32, "bounded_bit_width");
    if (view.eop || (size_t)bits > view.end - view.position) return -1;
    uint32_t value = 0;
    for (int i = 0; i < bits; ++i) {
        size_t position = view.position + (size_t)i;
        value |= (uint32_t)((view.data[position / 8U] >> (position % 8U)) & 1U) << i;
    }
    return (long)(int32_t)value;
}
long tremor_oggpack_read(oggpack_buffer *tag, int bits) {
    require_unit(tag == view.tag, "explicit_bitreader_owner");
    long value = look_bits(bits);
    if (view.eop || (size_t)bits > view.end - view.position) { view.eop = true; return -1; }
    view.position += (size_t)bits;
    return value;
}
int tremor_oggpack_eop(oggpack_buffer *tag) {
    require_unit(tag == view.tag, "explicit_bitreader_owner");
    return view.eop;
}
static uint8_t table_u8(const codebook *b, size_t offset) {
    require_unit(offset < owned_size(b->dec_table), "decode_table_byte_bound");
    return ((const uint8_t *)b->dec_table)[offset];
}
static uint32_t table_u32(const codebook *b, size_t offset) {
    require_unit(offset < owned_size(b->dec_table) / sizeof(uint32_t), "decode_table_word_bound");
    return ((const uint32_t *)b->dec_table)[offset];
}

/* Bounded public-Tremor consumer seam; production parser is not reimplemented. */
static uint32_t public_leaf(const codebook *b) {
    require_unit(b->dec_nodeb == 1 || b->dec_nodeb == 4, "declared_consumer_node_format");
    int bits = b->dec_maxlength;
    long look = look_bits(bits);
    while (look < 0 && bits > 1) look = look_bits(--bits);
    require_unit(look >= 0, "valid_codeword_bits_available");
    uint32_t chase = 0;
    int used = 0;
    for (; used < bits; ++used) {
        unsigned bit = ((uint32_t)look >> used) & 1U;
        if (b->dec_nodeb == 4) {
            require_unit(b->dec_leafw == 1, "declared_word_leaf_format");
            chase = table_u32(b, chase * 2U + bit);
            if (chase & UINT32_C(0x80000000)) { chase &= UINT32_C(0x7fffffff); break; }
        } else if (b->dec_leafw == 1) {
            chase = table_u8(b, chase * 2U + bit);
            if (chase & 0x80U) { chase &= 0x7fU; break; }
        } else {
            require_unit(b->dec_leafw == 2, "declared_split_leaf_format");
            uint32_t next = table_u8(b, chase + bit);
            if (next & 0x80U) {
                size_t tail = chase + bit + 1U + (!bit || (table_u8(b, chase) & 0x80U));
                chase = ((next << 8U) | table_u8(b, tail)) & 0x7fffU;
                break;
            }
            chase = next;
        }
    }
    require_unit(used < bits, "valid_codeword_selected_leaf");
    view.position += (size_t)used + 1U;
    require_unit(view.position <= view.end, "valid_codeword_consumed_bound");
    return chase;
}
static uint32_t public_vector(const codebook *b, int32_t *output) {
    uint32_t entry = public_leaf(b), unpack = entry;
    require_unit(b->dim > 0 && b->dim <= 16 && b->q_bits == 2 && (b->dec_type == 1 || b->dec_type == 3),
                 "declared_vector_formats");
    if (b->dec_type == 1) {
        for (long i = 0; i < b->dim; ++i) { output[i] = (int32_t)(unpack & 3U); unpack >>= 2U; }
    } else {
        require_unit(entry < (uint32_t)b->used_entries && b->q_pack == 16 && b->dim == 16,
                     "wide_compact_row_index_stride");
        size_t offset = (size_t)entry * (size_t)b->q_pack;
        require_unit(offset + (size_t)b->dim <= owned_size(b->q_val), "wide_owned_row_bound");
        for (long i = 0; i < b->dim; ++i) output[i] = ((const uint8_t *)b->q_val)[offset + (size_t)i];
    }
    /* Explicit point0 only. These fixtures have finite nonzero min/delta;
     * the public product fits signed32. No opaque backend point is assumed. */
    require_unit(b->q_minp == -30 && b->q_delp == -28 && b->q_min == -(INT32_C(1) << 30) &&
                 b->q_del == (INT32_C(1) << 28), "point0_quantization_contract");
    int32_t add = b->q_min >> 30;
    for (long i = 0; i < b->dim; ++i) {
        int64_t product = (int64_t)output[i] * b->q_del;
        require_unit(product >= 0 && product <= INT32_MAX, "valid_vector_product_bound");
        output[i] = add + ((int32_t)product >> 28);
        if (b->q_seq && i) output[i] += output[i - 1];
    }
    return entry;
}

static void print_hex(const void *data, size_t bytes) {
    const uint8_t *p = data;
    for (size_t i = 0; i < bytes; ++i) printf("%02x", p[i]);
}
static uint8_t wide_qval[4][64], wide_table[4][6];
static int32_t wide_vectors[4][4][16];
static unsigned total_probes;

static void run_case(unsigned index) {
    current_case = index; current_probe = 0;
    const unit_case_t *c = unit_cases + index;
    require_unit(!live_allocations && !failed && xPortGetCoreID() == 0, "fresh_case_core0");
    oggpack_buffer bits;
    begin_bits(&bits, c->setup, c->setup_bytes, c->book_first_bit, c->book_end_bit);
    codebook b = {0};
    int rc = repair_vorbis_book_unpack(&bits, &b); /* Actual unchanged production function. */
    require_unit(rc == 0 && !view.eop && view.position == c->book_end_bit, "actual_parser_success_exact_book_bits");
    require_unit(b.dim == c->dim && b.entries == c->entries && b.used_entries == c->used_entries &&
        b.dec_maxlength == c->max_length && b.dec_nodeb == c->node_bytes && b.dec_leafw == c->leaf_words &&
        b.dec_type == c->dec_type && b.q_bits == 2 && b.q_seq == c->sequence && b.q_pack == c->q_pack &&
        b.q_min == -(INT32_C(1) << 30) && b.q_minp == -30 && b.q_del == (INT32_C(1) << 28) && b.q_delp == -28,
        "actual_returned_fields");
    size_t table_bytes = owned_size(b.dec_table), qbytes = b.q_val ? owned_size(b.q_val) : 0;
    require_unit(table_bytes == c->table_bytes && qbytes == c->qval_bytes, "actual_array_sizes");
    require_unit(!qbytes || !memcmp(b.q_val, c->qval, qbytes), "actual_owned_quantized_rows");
    if (index >= 8 && index < 12) {
        static const uint8_t expected[] = {0x80, 1, 0x81, 2, 0x82, 0x83};
        require_unit(table_bytes == sizeof(expected) && !memcmp(b.dec_table, expected, sizeof(expected)), "actual_wide_leaf_table");
        memcpy(wide_qval[index - 8], b.q_val, 64);
        memcpy(wide_table[index - 8], b.dec_table, 6);
    }
    all_guards();
    printf(P "FIELDS case=%u id=%s dim=%ld entries=%ld used=%ld maxlen=%d nodeb=%d leafw=%d type=%d"
        " q_min=%" PRId32 " q_minp=%d q_del=%" PRId32 " q_delp=%d seq=%d q_bits=%d q_pack=%d table_bytes=%u qval_bytes=%u core=%d table=",
        index, c->id, b.dim, b.entries, b.used_entries, b.dec_maxlength, b.dec_nodeb, b.dec_leafw, b.dec_type,
        b.q_min, b.q_minp, b.q_del, b.q_delp, b.q_seq, b.q_bits, b.q_pack,
        (unsigned)table_bytes, (unsigned)qbytes, xPortGetCoreID());
    print_hex(b.dec_table, table_bytes); printf(" qval=");
    if (qbytes) print_hex(b.q_val, qbytes); else printf("-");
    printf("\n");
    for (unsigned i = 0; i < c->probe_count; ++i) {
        current_probe = i;
        const unit_probe_t *p = c->probes + i;
        uint8_t wire[4] = {(uint8_t)p->wire, (uint8_t)(p->wire >> 8), (uint8_t)(p->wire >> 16), (uint8_t)(p->wire >> 24)};
        begin_bits(&bits, wire, sizeof(wire), 0, p->bits);
        int32_t vector[16] = {0};
        uint32_t leaf = public_vector(&b, vector);
        require_unit(leaf == p->leaf && !view.eop && view.position == p->bits, "actual_leaf_and_consumption");
        require_unit(!memcmp(vector, p->expected, (size_t)b.dim * sizeof(int32_t)), "actual_public_consumer_vector");
        all_guards();
        if (index >= 8 && index < 12) memcpy(wide_vectors[index - 8][i], vector, sizeof(vector));
        printf(P "VECTOR case=%u probe=%u original=%u wire=%" PRIu32 " bits=%u leaf=%" PRIu32 " consumed=%u core=%d values=",
            index, i, p->original, p->wire, p->bits, leaf, (unsigned)view.position, xPortGetCoreID());
        for (long j = 0; j < b.dim; ++j) printf("%s%" PRId32, j ? "," : "", vector[j]);
        printf("\n"); ++total_probes;
    }
    repair_vorbis_book_clear(&b);
    require_unit(!live_allocations, "actual_clear_releases_all_owned_arrays");
    printf(P "CASE case=%u id=%s probes=%u parser_bits=%u live=0 core=%d\n", index, c->id, c->probe_count,
        c->book_end_bit - c->book_first_bit, xPortGetCoreID());
    vTaskDelay(1);
}
void app_main(void) {
    require_unit(xPortGetCoreID() == 0, "coordinator_core0");
    printf(P "BEGIN contract=%s cases=%u probes=%u core=%d\n", UNIT_CONTRACT_SHA256, UNIT_CASE_COUNT, UNIT_PROBE_COUNT, xPortGetCoreID());
    for (unsigned i = 0; i < UNIT_CASE_COUNT; ++i) run_case(i);
    for (unsigned pair = 0; pair < 2; ++pair) {
        unsigned first = pair * 2U, second = first + 1U;
        require_unit(!memcmp(wide_qval[first], wide_qval[second], 64) &&
            !memcmp(wide_table[first], wide_table[second], 6) &&
            !memcmp(wide_vectors[first], wide_vectors[second], sizeof(wide_vectors[first])), "actual_sparse_dense_public_equality");
        printf(P "PAIR first=%u second=%u seq=%u qval_equal=1 table_equal=1 vectors_equal=1 core=%d\n",
            first + 8U, second + 8U, pair, xPortGetCoreID());
    }
    require_unit(!failed && !live_allocations && total_probes == UNIT_PROBE_COUNT, "complete_unit_accounting");
    printf(P "COMPLETE cases=%u probes=%u live=0 pairs=2 core=%d\n", UNIT_CASE_COUNT, total_probes, xPortGetCoreID());
    fflush(stdout);
    /* app_main returns into SDK idle. Root must separately record owned QEMU
     * shutdown; COMPLETE alone is not an actual exit0 qualification. */
}
