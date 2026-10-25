// Exact dyadic residue and coupling from public Vorbis I sections4.3/8/9.2.2.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
#include "native_vorbis_residue.h"
#include <limits.h>
#include <string.h>

enum { MAX_CHANNELS = 255, MAX_LIMBS = 34 };

typedef struct {
    native_vorbis_mapping_setup_t mapping;
    native_vorbis_residue_layout_t layout;
    uint8_t active[MAX_CHANNELS];
} residue_context_t;

static unsigned integer_log(uint32_t value) {
    unsigned result = 0;
    while (value) { ++result; value >>= 1; }
    return result;
}

static unsigned trailing_zeroes(uint32_t value) {
    unsigned result = 0;
    while (!(value & 1U)) { ++result; value >>= 1; }
    return result;
}

static uint32_t partition_count(const native_vorbis_residue_setup_t *residue,
                                uint32_t bins, uint32_t channels, uint32_t *begin) {
    uint32_t size = bins * (residue->type == 2 ? channels : 1);
    *begin = residue->begin < size ? residue->begin : size;
    uint32_t end = residue->end < size ? residue->end : size;
    return end > *begin ? (end - *begin) / residue->partition_size : 0;
}

// Bound absolute affine terms together; no expansion or quantization rounding.
static bool book_range(const native_vorbis_quant_layout_t *book,
                       int32_t *lower, int32_t *upper) {
    uint32_t minimum = book->minimum_bits & UINT32_C(0x1fffff);
    uint32_t delta = book->delta_bits & UINT32_C(0x1fffff);
    if (!minimum && !delta) return false;
    int32_t top = INT32_MIN;
    const uint32_t words[2] = {book->minimum_bits, book->delta_bits};
    for (unsigned i = 0; i < 2; ++i) {
        uint32_t mantissa = words[i] & UINT32_C(0x1fffff);
        if (!mantissa) continue;
        int32_t exponent = (int32_t)((words[i] >> 21) & 1023U) - 788;
        int32_t low = exponent + (int32_t)trailing_zeroes(mantissa);
        int32_t high = exponent + (int32_t)integer_log(mantissa);
        if (low < *lower) *lower = low;
        if (high > top) top = high;
    }
    uint32_t maximum = (UINT32_C(1) << book->value_bits) - 1;
    uint32_t weights = (minimum ? 1U : 0U) + (delta ? maximum : 0U);
    if (book->sequence_p) weights *= book->dimensions;
    top += (int32_t)integer_log(weights - 1);
    if (top > *upper) *upper = top;
    return true;
}

static native_vorbis_numeric_status_t prepare(
    const native_vorbis_setup_t *setup, uint32_t mapping_index, size_t bins,
    const uint8_t *floor_present, size_t flag_count, residue_context_t *context) {
    native_vorbis_numeric_status_t status = native_vorbis_setup_mapping(
        setup, mapping_index, &context->mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    const native_vorbis_mapping_setup_t *mapping = &context->mapping;
    if (!bins || bins > 4096 || !mapping->channels || mapping->channels > MAX_CHANNELS ||
        flag_count != mapping->channels || !floor_present) return NATIVE_VORBIS_NUMERIC_INVALID;
    for (uint32_t i = 0; i < mapping->channels; ++i) {
        if (floor_present[i] > 1) return NATIVE_VORBIS_NUMERIC_INVALID;
        context->active[i] = floor_present[i];
    }
    // Exactly one forward-order pass, not a transitive graph closure.
    for (uint32_t i = 0; i < mapping->coupling_count; ++i) {
        uint32_t m = mapping->coupling_pairs[2 * i], a = mapping->coupling_pairs[2 * i + 1];
        if (context->active[m] || context->active[a]) context->active[m] = context->active[a] = 1;
    }
    native_vorbis_residue_layout_t result = {0};
    result.mapping = mapping_index;
    result.bins = (uint32_t)bins;
    result.channels = mapping->channels;
    result.sample_count = (uint64_t)mapping->channels * bins;
    int32_t lower = INT32_MAX, upper = INT32_MIN;
    bool nonzero = false;
    for (uint32_t submap = 0; submap < mapping->submap_count; ++submap) {
        uint32_t channels = 0, active = 0;
        for (uint32_t i = 0; i < mapping->channels; ++i) if (mapping->mux[i] == submap) {
            ++channels;
            active += context->active[i];
        }
        if (!channels) continue;
        native_vorbis_residue_setup_t residue;
        status = native_vorbis_setup_residue(setup, mapping->submaps[3 * submap + 2], &residue);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        for (uint32_t i = 0; i < residue.stage_book_count; ++i) {
            const native_vorbis_quant_layout_t *book = &setup->books[residue.books[i]].quantization.layout;
            if (book_range(book, &lower, &upper)) nonzero = true;
        }
        uint32_t begin;
        uint32_t partitions = partition_count(&residue, (uint32_t)bins, channels, &begin);
        uint64_t scratch = active && residue.classifications > 1 ?
            (uint64_t)partitions * (residue.type == 2 ? 1 : active) : 0;
        if (scratch > result.classification_count) result.classification_count = scratch;
    }
    if (nonzero) {
        upper += 3; // Eight passes, each contributing at most one scalar per bin.
        result.exponent = lower;
        result.magnitude_bits = (uint32_t)(upper - lower);
        result.limbs = (result.magnitude_bits + 32) / 32;
        // 21-bit packed mantissas, E[-788,235] and M+D<2^32 prove this bound.
        if (result.limbs > MAX_LIMBS) return NATIVE_VORBIS_NUMERIC_RANGE;
        result.limb_count = result.sample_count * result.limbs;
    }
    context->layout = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_residue_measure(
    const native_vorbis_setup_t *setup, uint32_t mapping, size_t bins,
    const uint8_t *floor_present, size_t flag_count,
    native_vorbis_residue_layout_t *layout) {
    if (!layout) return NATIVE_VORBIS_NUMERIC_INVALID;
    residue_context_t context;
    native_vorbis_numeric_status_t status = prepare(setup, mapping, bins, floor_present, flag_count, &context);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *layout = context.layout;
    return status;
}

static bool same_numeric_layout(const native_vorbis_residue_layout_t *a,
                                const native_vorbis_residue_layout_t *b) {
    return a->mapping == b->mapping && a->bins == b->bins && a->channels == b->channels &&
        a->limbs == b->limbs && a->magnitude_bits == b->magnitude_bits &&
        a->exponent == b->exponent && a->sample_count == b->sample_count && a->limb_count == b->limb_count;
}

// Exact signed addition of one <=53-bit integer times a power of two.
static void add_term(uint32_t *sample, const native_vorbis_residue_layout_t *layout,
                     uint32_t packed, uint32_t multiplier) {
    uint64_t value = (uint64_t)(packed & UINT32_C(0x1fffff)) * multiplier;
    if (!value) return;
    int32_t exponent = (int32_t)((packed >> 21) & 1023U) - 788;
    while (!(value & 1U)) { value >>= 1; ++exponent; }
    uint32_t shift = (uint32_t)(exponent - layout->exponent);
    uint32_t word = shift / 32, bit = shift % 32;
    uint64_t carry = 0;
    bool negative = (packed >> 31) != 0;
    for (uint32_t i = word; i < layout->limbs; ++i) {
        uint32_t part;
        if (bit) {
            part = (uint32_t)value << bit;
            value >>= 32 - bit;
            bit = 0;
        } else {
            part = (uint32_t)value;
            value >>= 32;
        }
        if (negative) {
            uint64_t subtract = (uint64_t)part + carry;
            carry = (uint64_t)sample[i] < subtract;
            sample[i] = (uint32_t)((uint64_t)sample[i] - subtract);
        } else {
            uint64_t sum = (uint64_t)sample[i] + part + carry;
            sample[i] = (uint32_t)sum;
            carry = sum >> 32;
        }
    }
}

// Sequential reconstruction is O(dimensions), including sequence1 and lookup1.
static void add_vector(const native_vorbis_quantization_t *book, uint32_t entry,
                       const native_vorbis_residue_setup_t *residue,
                       const native_vorbis_residue_layout_t *layout,
                       const uint8_t *bundle, uint32_t channels, uint32_t stream,
                       uint32_t offset, uint32_t word, uint32_t words, uint32_t *output) {
    const native_vorbis_quant_layout_t *q = &book->layout;
    uint32_t remainder = entry, minimum = 0, delta = 0;
    uint64_t row = (uint64_t)entry * q->dimensions;
    for (uint32_t i = 0; i < q->dimensions; ++i) {
        uint64_t index;
        if (q->lookup_type == 1) {
            index = remainder % (uint32_t)q->multiplicand_count;
            remainder /= (uint32_t)q->multiplicand_count;
        } else index = row + i;
        uint32_t scalar = book->multiplicands[(size_t)index];
        if (q->sequence_p) { ++minimum; delta += scalar; }
        else { minimum = 1; delta = scalar; }
        uint32_t position = offset + (residue->type == 0 ? word + i * words : word * q->dimensions + i);
        uint32_t channel = residue->type == 2 ? bundle[position % channels] : bundle[stream];
        uint32_t bin = residue->type == 2 ? position / channels : position;
        size_t destination = ((size_t)channel * layout->bins + bin) * layout->limbs;
        add_term(output + destination, layout, q->minimum_bits, minimum);
        add_term(output + destination, layout, q->delta_bits, delta);
    }
}

static native_vorbis_numeric_status_t read_word(const native_vorbis_codebook_t *book,
                                               native_vorbis_packet_t *packet, uint32_t *entry) {
    if (packet->end_of_packet) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    return native_vorbis_codebook_decode(book, packet, entry);
}

static unsigned popcount(uint32_t value) {
    unsigned result = 0;
    while (value) { result += value & 1U; value >>= 1; }
    return result;
}

static native_vorbis_numeric_status_t decode_bundle(
    const native_vorbis_setup_t *setup, const native_vorbis_residue_setup_t *residue,
    const native_vorbis_residue_layout_t *layout, native_vorbis_packet_t *packet,
    const uint8_t *bundle, uint32_t channels, bool active, uint8_t *classes,
    uint32_t *output, bool publish, native_vorbis_residue_packet_t *state) {
    uint32_t begin, partitions = partition_count(residue, layout->bins, channels, &begin);
    if (!active || !partitions) return NATIVE_VORBIS_NUMERIC_OK;
    uint32_t streams = residue->type == 2 ? 1 : channels;
    const native_vorbis_codebook_t *phrasebook = &setup->books[residue->classbook];
    uint32_t dimensions = phrasebook->layout.quantization.dimensions;
    for (unsigned pass = 0; pass < 8; ++pass) {
        uint32_t partition = 0;
        while (partition < partitions) {
            if (!pass) for (uint32_t stream = 0; stream < streams; ++stream) {
                uint32_t entry;
                native_vorbis_numeric_status_t status = read_word(phrasebook, packet, &entry);
                if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
                ++state->classwords;
                if (residue->classifications > 1) {
                    // Reduce all declared entries modulo base^dimensions. The
                    // final short group consumes the leading digits, not low ones.
                    for (uint32_t j = dimensions; j; --j) {
                        uint32_t digit = entry % residue->classifications;
                        entry /= residue->classifications;
                        if (partition + j - 1 < partitions)
                            classes[(size_t)stream * partitions + partition + j - 1] = (uint8_t)digit;
                    }
                }
            }
            for (uint32_t k = 0; k < dimensions && partition < partitions; ++k, ++partition) {
                for (uint32_t stream = 0; stream < streams; ++stream) {
                    uint32_t cls = residue->classifications == 1 ? 0 : classes[(size_t)stream * partitions + partition];
                    uint32_t cascade = residue->cascades[cls];
                    if (!(cascade & (UINT32_C(1) << pass))) continue;
                    uint32_t index = residue->book_offsets[cls] + popcount(cascade & ((UINT32_C(1) << pass) - 1));
                    const native_vorbis_codebook_t *book = &setup->books[residue->books[index]];
                    uint32_t words = residue->partition_size / book->layout.quantization.dimensions;
                    uint32_t offset = begin + partition * residue->partition_size;
                    for (uint32_t word = 0; word < words; ++word) {
                        uint32_t entry;
                        native_vorbis_numeric_status_t status = read_word(book, packet, &entry);
                        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
                        ++state->vectors;
                        state->values += book->layout.quantization.dimensions;
                        if (publish && layout->limbs)
                            add_vector(&book->quantization, entry, residue, layout, bundle, channels,
                                       stream, offset, word, words, output);
                    }
                }
            }
        }
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t decode_mapping(
    const native_vorbis_setup_t *setup, const residue_context_t *context,
    native_vorbis_packet_t *packet, uint8_t *classes, uint32_t *output,
    bool publish, native_vorbis_residue_packet_t *state) {
    const native_vorbis_mapping_setup_t *mapping = &context->mapping;
    uint8_t bundle[MAX_CHANNELS];
    for (uint32_t submap = 0; submap < mapping->submap_count; ++submap) {
        native_vorbis_residue_setup_t residue;
        native_vorbis_numeric_status_t status = native_vorbis_setup_residue(
            setup, mapping->submaps[3 * submap + 2], &residue);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        uint32_t channels = 0;
        bool active = false;
        for (uint32_t i = 0; i < mapping->channels; ++i) if (mapping->mux[i] == submap) {
            if (context->active[i]) active = true;
            if (residue.type == 2 || context->active[i]) bundle[channels++] = (uint8_t)i;
        }
        if (!channels) continue;
        status = decode_bundle(setup, &residue, &context->layout, packet, bundle,
                               channels, active, classes, output, publish, state);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_residue_packet(
    const native_vorbis_setup_t *setup, const native_vorbis_residue_layout_t *layout,
    const uint8_t *floor_present, size_t flag_count, native_vorbis_packet_t *packet,
    uint8_t *classifications, size_t classification_capacity,
    uint32_t *output, size_t limb_capacity, native_vorbis_residue_packet_t *state) {
    if (!layout || !packet || !state) return NATIVE_VORBIS_NUMERIC_INVALID;
    residue_context_t context;
    native_vorbis_numeric_status_t status = prepare(
        setup, layout->mapping, layout->bins, floor_present, flag_count, &context);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!same_numeric_layout(layout, &context.layout) ||
        layout->classification_count != context.layout.classification_count)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t next = *packet;
    uint64_t ignored;
    status = native_vorbis_packet_read(&next, 0, &ignored);
    if (status != NATIVE_VORBIS_NUMERIC_OK && status != NATIVE_VORBIS_NUMERIC_TRUNCATED) return status;
    if (layout->limb_count > SIZE_MAX / sizeof(*output) || layout->classification_count > SIZE_MAX)
        return NATIVE_VORBIS_NUMERIC_RANGE;
    if (layout->limb_count > limb_capacity || layout->classification_count > classification_capacity)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if ((layout->limb_count && !output) || (layout->classification_count && !classifications))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_residue_packet_t checked = {0};
    status = decode_mapping(setup, &context, &next, classifications, NULL, false, &checked);
    if (status != NATIVE_VORBIS_NUMERIC_OK && status != NATIVE_VORBIS_NUMERIC_TRUNCATED) return status;
    if (layout->limb_count) memset(output, 0, (size_t)layout->limb_count * sizeof(*output));
    next = *packet;
    native_vorbis_residue_packet_t result = {0};
    status = decode_mapping(setup, &context, &next, classifications, output, true, &result);
    if (status != NATIVE_VORBIS_NUMERIC_OK && status != NATIVE_VORBIS_NUMERIC_TRUNCATED) return status;
    result.stopped_on_eop = status == NATIVE_VORBIS_NUMERIC_TRUNCATED;
    *packet = next;
    *state = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool sample_valid(const uint32_t *sample, const native_vorbis_residue_layout_t *layout) {
    uint32_t word = layout->magnitude_bits / 32, bit = layout->magnitude_bits % 32;
    uint32_t low_mask = bit ? (UINT32_C(1) << bit) - 1 : 0;
    bool negative = (sample[layout->limbs - 1] >> 31) != 0;
    bool lower_nonzero = false;
    for (uint32_t i = 0; i < word; ++i) if (sample[i]) lower_nonzero = true;
    if (sample[word] & low_mask) lower_nonzero = true;
    for (uint32_t i = word; i < layout->limbs; ++i) {
        uint32_t mask = i == word ? ~low_mask : UINT32_MAX;
        if ((sample[i] & mask) != (negative ? mask : 0)) return false;
    }
    // Sign extension alone would admit the excluded -2^magnitude_bits boundary.
    return !negative || lower_nonzero;
}

static bool positive(const uint32_t *sample, uint32_t limbs) {
    if (sample[limbs - 1] >> 31) return false;
    for (uint32_t i = 0; i < limbs; ++i) if (sample[i]) return true;
    return false;
}

static void combine(const uint32_t *m, const uint32_t *a, uint32_t *result,
                    uint32_t limbs, bool subtract) {
    uint64_t carry = 0;
    for (uint32_t i = 0; i < limbs; ++i) {
        if (subtract) {
            uint64_t term = (uint64_t)a[i] + carry;
            carry = (uint64_t)m[i] < term;
            result[i] = (uint32_t)((uint64_t)m[i] - term);
        } else {
            uint64_t sum = (uint64_t)m[i] + a[i] + carry;
            result[i] = (uint32_t)sum;
            carry = sum >> 32;
        }
    }
}

native_vorbis_numeric_status_t native_vorbis_residue_inverse_coupling(
    const native_vorbis_setup_t *setup, const native_vorbis_residue_layout_t *layout,
    uint32_t *output, size_t limb_capacity) {
    if (!layout || !layout->channels || layout->channels > MAX_CHANNELS)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    uint8_t flags[MAX_CHANNELS];
    memset(flags, 1, sizeof(flags));
    residue_context_t context;
    native_vorbis_numeric_status_t status = prepare(
        setup, layout->mapping, layout->bins, flags, layout->channels, &context);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!same_numeric_layout(layout, &context.layout) ||
        layout->classification_count > context.layout.classification_count)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (layout->limb_count > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (layout->limb_count > limb_capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (layout->limb_count && !output) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!layout->limbs) return NATIVE_VORBIS_NUMERIC_OK;
    for (size_t i = 0; i < (size_t)layout->sample_count; ++i)
        if (!sample_valid(output + i * layout->limbs, layout)) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t temporary[MAX_LIMBS];
    const native_vorbis_mapping_setup_t *mapping = &context.mapping;
    for (uint32_t i = mapping->coupling_count; i; --i) {
        uint32_t magnitude = mapping->coupling_pairs[2 * (i - 1)];
        uint32_t angle = mapping->coupling_pairs[2 * (i - 1) + 1];
        for (uint32_t bin = 0; bin < layout->bins; ++bin) {
            uint32_t *m = output + ((size_t)magnitude * layout->bins + bin) * layout->limbs;
            uint32_t *a = output + ((size_t)angle * layout->bins + bin) * layout->limbs;
            bool m_positive = positive(m, layout->limbs), a_positive = positive(a, layout->limbs);
            combine(m, a, temporary, layout->limbs, m_positive == a_positive);
            if (a_positive) memcpy(a, temporary, layout->limbs * sizeof(*a));
            else {
                memcpy(a, m, layout->limbs * sizeof(*a));
                memcpy(m, temporary, layout->limbs * sizeof(*m));
            }
        }
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}
