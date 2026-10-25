// Original quantization fields and exact lookup recurrence, Vorbis I 3.2/6.2.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
#include "native_vorbis_quant.h"
#include <stdbool.h>
#include <limits.h>

static bool root_power_le(uint32_t base, uint32_t dimensions, uint32_t entries) {
    if (base <= 1) return base <= entries;
    uint32_t product = 1;
    for (uint32_t i = 0; i < dimensions; ++i) {
        if (product > entries / base) return false;
        product *= base;
    }
    return true;
}

native_vorbis_numeric_status_t native_vorbis_quantization_count(
    uint32_t dimensions, uint32_t entries, uint32_t lookup_type, uint64_t *count) {
    if (!count || dimensions > 65535 || entries > UINT32_C(0xffffff) || lookup_type > 2 ||
        (lookup_type == 1 && !dimensions)) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint64_t result = 0;
    if (lookup_type == 2) result = (uint64_t)dimensions * entries;
    if (lookup_type == 1 && entries) {
        uint32_t low = 1, high = entries;
        while (low < high) {
            uint32_t middle = low + (high - low + 1) / 2;
            if (root_power_le(middle, dimensions, entries)) low = middle;
            else high = middle - 1;
        }
        result = low;
    }
    *count = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool packet_extent(const uint8_t *packet, size_t bytes, uint64_t bits) {
    return (!bits || packet) && bits / 8 <= bytes &&
           (bits / 8 < bytes || bits % 8 == 0);
}

static uint32_t read_bits(const uint8_t *packet, uint64_t *position, unsigned width) {
    uint32_t value = 0;
    for (unsigned i = 0; i < width; ++i) {
        uint64_t bit = *position + i;
        value |= (uint32_t)((packet[(size_t)(bit / 8)] >> (bit % 8)) & 1U) << i;
    }
    *position += width;
    return value;
}

native_vorbis_numeric_status_t native_vorbis_quantization_measure(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    uint64_t start_bit, uint32_t dimensions, uint32_t entries,
    native_vorbis_quant_layout_t *layout) {
    if (!layout || dimensions > 65535 || entries > UINT32_C(0xffffff) ||
        !packet_extent(packet, packet_bytes, packet_bits) || start_bit > packet_bits)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (packet_bits - start_bit < 4) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    uint64_t position = start_bit;
    native_vorbis_quant_layout_t result = {0};
    result.dimensions = dimensions;
    result.entries = entries;
    result.start_bit = start_bit;
    result.lookup_type = read_bits(packet, &position, 4);
    native_vorbis_numeric_status_t status = native_vorbis_quantization_count(
        dimensions, entries, result.lookup_type, &result.multiplicand_count);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (result.lookup_type) {
        if (packet_bits - position < 69) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
        result.minimum_bits = read_bits(packet, &position, 32);
        result.delta_bits = read_bits(packet, &position, 32);
        result.value_bits = read_bits(packet, &position, 4) + 1;
        result.sequence_p = read_bits(packet, &position, 1);
    }
    result.multiplicand_bit = position;
    uint64_t span = result.multiplicand_count * result.value_bits;
    // The fields cap span below2^44, independently of the target size_t width.
    if (span > packet_bits - position) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    result.end_bit = position + span;
    *layout = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool layouts_equal(const native_vorbis_quant_layout_t *a,
                           const native_vorbis_quant_layout_t *b) {
    return a->dimensions == b->dimensions && a->entries == b->entries &&
        a->lookup_type == b->lookup_type && a->minimum_bits == b->minimum_bits &&
        a->delta_bits == b->delta_bits && a->value_bits == b->value_bits &&
        a->sequence_p == b->sequence_p && a->multiplicand_count == b->multiplicand_count &&
        a->start_bit == b->start_bit && a->multiplicand_bit == b->multiplicand_bit &&
        a->end_bit == b->end_bit;
}

native_vorbis_numeric_status_t native_vorbis_quantization_materialize(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    const native_vorbis_quant_layout_t *layout, uint16_t *storage,
    size_t capacity, native_vorbis_quantization_t *book) {
    if (!layout || !book) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_quant_layout_t measured;
    native_vorbis_numeric_status_t status = native_vorbis_quantization_measure(
        packet, packet_bytes, packet_bits, layout->start_bit, layout->dimensions,
        layout->entries, &measured);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!layouts_equal(layout, &measured)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (measured.multiplicand_count > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (measured.multiplicand_count && !storage) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint64_t position = measured.multiplicand_bit;
    for (size_t i = 0; i < (size_t)measured.multiplicand_count; ++i)
        storage[i] = (uint16_t)read_bits(packet, &position, measured.value_bits);
    *book = (native_vorbis_quantization_t){measured,
        measured.multiplicand_count ? storage : NULL, (size_t)measured.multiplicand_count};
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t book_valid(const native_vorbis_quantization_t *book) {
    if (!book) return NATIVE_VORBIS_NUMERIC_INVALID;
    const native_vorbis_quant_layout_t *l = &book->layout;
    uint64_t count;
    native_vorbis_numeric_status_t status = native_vorbis_quantization_count(
        l->dimensions, l->entries, l->lookup_type, &count);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (count != l->multiplicand_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!l->lookup_type) return NATIVE_VORBIS_NUMERIC_NO_LOOKUP;
    if (!l->dimensions || l->value_bits < 1 || l->value_bits > 16 || l->sequence_p > 1)
        return NATIVE_VORBIS_NUMERIC_INVALID;
#if SIZE_MAX < UINT64_MAX
    if (count > SIZE_MAX) return NATIVE_VORBIS_NUMERIC_RANGE;
#endif
    if (count > book->storage_count || (count && !book->multiplicands))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    return NATIVE_VORBIS_NUMERIC_OK;
}

// Check all requested values before the writing pass. No order-sized scratch.
static native_vorbis_numeric_status_t vector_pass(
    const native_vorbis_quantization_t *book, uint32_t entry, size_t prefix,
    native_vorbis_affine_t carry, native_vorbis_affine_t *output,
    native_vorbis_affine_t *last) {
    const native_vorbis_quant_layout_t *l = &book->layout;
    uint32_t remainder = entry, delta_multiplier = 0, minimum_multiplier = 0;
    uint64_t row = (uint64_t)entry * l->dimensions;
    uint32_t maximum = (UINT32_C(1) << l->value_bits) - 1;
    for (size_t i = 0; i < prefix; ++i) {
        uint64_t index;
        if (l->lookup_type == 1) {
            index = remainder % (uint32_t)l->multiplicand_count;
            remainder /= (uint32_t)l->multiplicand_count;
        } else index = row + i;
        uint32_t q = book->multiplicands[(size_t)index];
        if (q > maximum) return NATIVE_VORBIS_NUMERIC_INVALID;
        if (l->sequence_p) { delta_multiplier += q; ++minimum_multiplier; }
        else { delta_multiplier = q; minimum_multiplier = 1; }
        if (delta_multiplier > UINT32_MAX - carry.delta_multiplier ||
            minimum_multiplier > UINT32_MAX - carry.minimum_multiplier)
            return NATIVE_VORBIS_NUMERIC_RANGE;
        native_vorbis_affine_t value = {l->minimum_bits, l->delta_bits,
            minimum_multiplier + carry.minimum_multiplier,
            delta_multiplier + carry.delta_multiplier};
        if (output) output[i] = value;
        *last = value;
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_quantization_vector(
    const native_vorbis_quantization_t *book, uint32_t entry, size_t prefix,
    native_vorbis_affine_t *output, size_t capacity) {
    native_vorbis_numeric_status_t status = book_valid(book);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (entry >= book->layout.entries || prefix > book->layout.dimensions || (prefix && !output))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (prefix > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    native_vorbis_affine_t last = {0}, carry = {0};
    status = vector_pass(book, entry, prefix, carry, NULL, &last);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return vector_pass(book, entry, prefix, carry, output, &last);
}

native_vorbis_numeric_status_t native_vorbis_quantization_scalar(
    const native_vorbis_quantization_t *book, uint32_t entry, uint32_t component,
    native_vorbis_affine_t *output) {
    native_vorbis_numeric_status_t status = book_valid(book);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!output || entry >= book->layout.entries || component >= book->layout.dimensions)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_affine_t result = {0}, carry = {0};
    status = vector_pass(book, entry, (size_t)component + 1, carry, NULL, &result);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *output = result;
    return status;
}

native_vorbis_numeric_status_t native_vorbis_floor0_lsp_from_entries(
    const native_vorbis_quantization_t *book, const uint32_t *entries,
    size_t entry_count, size_t order, native_vorbis_affine_t *output, size_t capacity) {
    native_vorbis_numeric_status_t status = book_valid(book);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!entries || !output || !order || order > 255 ||
        entry_count != (order - 1) / book->layout.dimensions + 1)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (capacity < order) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    for (unsigned pass = 0; pass < 2; ++pass) {
        native_vorbis_affine_t carry = {0};
        size_t produced = 0;
        for (size_t i = 0; i < entry_count; ++i) {
            if (entries[i] >= book->layout.entries) return NATIVE_VORBIS_NUMERIC_INVALID;
            size_t prefix = order - produced;
            if (prefix > book->layout.dimensions) prefix = book->layout.dimensions;
            native_vorbis_affine_t last = carry;
            status = vector_pass(book, entries[i], prefix, carry,
                                 pass ? output + produced : NULL, &last);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
            carry = last;
            produced += prefix;
        }
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}
