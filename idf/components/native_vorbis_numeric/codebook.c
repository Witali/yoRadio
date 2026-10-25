// Public-packet codebooks, Vorbis I sections2/3 and singleton errata20150226.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
#include "native_vorbis_codebook.h"
#include <limits.h>

static bool extent_valid(const uint8_t *data, size_t bytes, uint64_t bits) {
    return (!bits || data) && bits / 8 <= bytes &&
           (bits / 8 < bytes || bits % 8 == 0);
}

static bool cursor_valid(const native_vorbis_packet_t *packet) {
    return packet && extent_valid(packet->data, packet->bytes, packet->bits) &&
           packet->position <= packet->bits;
}

native_vorbis_numeric_status_t native_vorbis_packet_init(
    native_vorbis_packet_t *packet, const uint8_t *data, size_t bytes,
    uint64_t bits, uint64_t start_bit) {
    if (!packet || !extent_valid(data, bytes, bits) || start_bit > bits)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    *packet = (native_vorbis_packet_t){data, bytes, bits, start_bit, false};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_packet_read(
    native_vorbis_packet_t *packet, unsigned width, uint64_t *value) {
    if (!value || width > 64 || !cursor_valid(packet))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (packet->end_of_packet) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    if (width > packet->bits - packet->position) {
        packet->end_of_packet = true;
        return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    }
    uint64_t result = 0;
    for (unsigned i = 0; i < width; ++i) {
        uint64_t bit = packet->position + i;
        result |= (uint64_t)((packet->data[(size_t)(bit / 8)] >> (bit % 8)) & 1U) << i;
    }
    packet->position += width;
    *value = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t field(
    native_vorbis_packet_t *packet, unsigned width, uint32_t *value) {
    uint64_t result;
    native_vorbis_numeric_status_t status = native_vorbis_packet_read(packet, width, &result);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *value = (uint32_t)result;
    return status;
}

// The free subtrees form a frontier with at most one node at each depth.
// A deeper frontier node is always lexically before every shallower node.
// Thus the deepest free node at depth<=length is the lowest unused code.
// Splitting its left branch inserts right siblings only at empty depths.
typedef struct {
    uint32_t prefix[33];
    uint64_t available;
    uint32_t used, maximum;
} frontier_t;

static native_vorbis_numeric_status_t add_word(
    frontier_t *tree, uint32_t entry, unsigned length, native_vorbis_codeword_t *words) {
    if (!length || length > 32) return NATIVE_VORBIS_NUMERIC_INVALID;
    unsigned depth = length;
    while (!(tree->available & (UINT64_C(1) << depth))) {
        if (!depth) return NATIVE_VORBIS_NUMERIC_INVALID; // Overpopulated.
        --depth;
    }
    uint32_t code = tree->prefix[depth];
    tree->available &= ~(UINT64_C(1) << depth);
    for (unsigned next = depth + 1; next <= length; ++next) {
        tree->prefix[next] = code | (UINT32_C(1) << (32 - next));
        tree->available |= UINT64_C(1) << next;
    }
    if (words) words[tree->used] = (native_vorbis_codeword_t){code, entry, length};
    ++tree->used;
    if (length > tree->maximum) tree->maximum = length;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static unsigned integer_log(uint32_t value) {
    unsigned width = 0;
    while (value) { ++width; value >>= 1; }
    return width;
}

// A second pass may write words only after complete validation and capacity
// preflight. Inputs are immutable, so that pass follows the same validated path.
static native_vorbis_numeric_status_t parse_lengths(
    native_vorbis_packet_t *packet, uint32_t *dimensions, uint32_t *entries,
    uint32_t *used, uint32_t *maximum, native_vorbis_codeword_t *words) {
    uint32_t sync, ordered;
    native_vorbis_numeric_status_t status = field(packet, 24, &sync);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (sync != UINT32_C(0x564342)) return NATIVE_VORBIS_NUMERIC_INVALID;
    status = field(packet, 16, dimensions);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = field(packet, 24, entries);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = field(packet, 1, &ordered);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    frontier_t tree = {{0}, UINT64_C(1), 0, 0};
    if (ordered) {
        uint32_t length;
        status = field(packet, 5, &length);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        ++length;
        uint32_t current = 0;
        while (current < *entries) {
            if (length > 32) return NATIVE_VORBIS_NUMERIC_INVALID;
            uint32_t count;
            status = field(packet, integer_log(*entries - current), &count);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
            if (count > *entries - current) return NATIVE_VORBIS_NUMERIC_INVALID;
            for (uint32_t i = 0; i < count; ++i) {
                status = add_word(&tree, current + i, length, words);
                if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
            }
            current += count;
            ++length; // A zero run is a legal gap, not an unbounded retry.
        }
    } else {
        uint32_t sparse;
        status = field(packet, 1, &sparse);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        for (uint32_t entry = 0; entry < *entries; ++entry) {
            uint32_t present = 1, length;
            if (sparse) {
                status = field(packet, 1, &present);
                if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
            }
            if (!present) continue;
            status = field(packet, 5, &length);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
            status = add_word(&tree, entry, length + 1, words);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        }
    }
    // Empty metadata follows the public Xiph setup/init behavior. It has no
    // decodable symbol; it is not a zero-bit singleton. Nonempty trees must be
    // complete except for exactly one length1 word (2015 singleton erratum).
    if ((tree.used == 1 && tree.maximum != 1) ||
        (tree.used > 1 && tree.available)) return NATIVE_VORBIS_NUMERIC_INVALID;
    *used = tree.used;
    *maximum = tree.maximum;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_codebook_measure(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    uint64_t start_bit, native_vorbis_codebook_layout_t *layout) {
    if (!layout) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t cursor;
    native_vorbis_numeric_status_t status = native_vorbis_packet_init(
        &cursor, packet, packet_bytes, packet_bits, start_bit);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_codebook_layout_t result = {0};
    result.start_bit = start_bit;
    uint32_t dimensions, entries;
    status = parse_lengths(&cursor, &dimensions, &entries,
                           &result.used_entries, &result.maximum_length, NULL);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_quantization_measure(packet, packet_bytes, packet_bits,
        cursor.position, dimensions, entries, &result.quantization);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *layout = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool quant_equal(const native_vorbis_quant_layout_t *a,
                        const native_vorbis_quant_layout_t *b) {
    return a->dimensions == b->dimensions && a->entries == b->entries &&
        a->lookup_type == b->lookup_type && a->minimum_bits == b->minimum_bits &&
        a->delta_bits == b->delta_bits && a->value_bits == b->value_bits &&
        a->sequence_p == b->sequence_p && a->multiplicand_count == b->multiplicand_count &&
        a->start_bit == b->start_bit && a->multiplicand_bit == b->multiplicand_bit &&
        a->end_bit == b->end_bit;
}

static bool layouts_equal(const native_vorbis_codebook_layout_t *a,
                          const native_vorbis_codebook_layout_t *b) {
    return a->start_bit == b->start_bit && a->used_entries == b->used_entries &&
        a->maximum_length == b->maximum_length && quant_equal(&a->quantization, &b->quantization);
}

// Constant auxiliary storage heapsort. Generic qsort implementations may use
// heap or recursion; setup storage and stack must remain explicit on both MCUs.
static void exchange(native_vorbis_codeword_t *a, native_vorbis_codeword_t *b) {
    native_vorbis_codeword_t temporary = *a;
    *a = *b;
    *b = temporary;
}

static void sift(native_vorbis_codeword_t *words, size_t count, size_t root) {
    while (root < count / 2) {
        size_t child = root * 2 + 1;
        if (child + 1 < count && words[child].code < words[child + 1].code) ++child;
        if (words[root].code >= words[child].code) return;
        exchange(&words[root], &words[child]);
        root = child;
    }
}

static void sort_words(native_vorbis_codeword_t *words, size_t count) {
    for (size_t i = count / 2; i; --i) sift(words, count, i - 1);
    for (size_t end = count; end > 1; --end) {
        exchange(&words[0], &words[end - 1]);
        sift(words, end - 1, 0);
    }
}

native_vorbis_numeric_status_t native_vorbis_codebook_materialize(
    const uint8_t *packet, size_t packet_bytes, uint64_t packet_bits,
    const native_vorbis_codebook_layout_t *layout,
    native_vorbis_codeword_t *words, size_t word_capacity,
    uint16_t *multiplicands, size_t multiplicand_capacity, native_vorbis_codebook_t *book) {
    if (!layout || !book) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_codebook_layout_t measured;
    native_vorbis_numeric_status_t status = native_vorbis_codebook_measure(
        packet, packet_bytes, packet_bits, layout->start_bit, &measured);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!layouts_equal(layout, &measured)) return NATIVE_VORBIS_NUMERIC_INVALID;
#if SIZE_MAX < UINT64_MAX
    if (measured.quantization.multiplicand_count > SIZE_MAX / sizeof(*multiplicands))
        return NATIVE_VORBIS_NUMERIC_RANGE;
#endif
    if (measured.used_entries > word_capacity ||
        measured.quantization.multiplicand_count > multiplicand_capacity)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if ((measured.used_entries && !words) ||
        (measured.quantization.multiplicand_count && !multiplicands))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_quantization_t quantization;
    status = native_vorbis_quantization_materialize(packet, packet_bytes, packet_bits,
        &measured.quantization, multiplicands, multiplicand_capacity, &quantization);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_packet_t cursor;
    (void)native_vorbis_packet_init(&cursor, packet, packet_bytes, packet_bits, measured.start_bit);
    uint32_t dimensions, entries, used, maximum;
    (void)parse_lengths(&cursor, &dimensions, &entries, &used, &maximum, words);
    sort_words(words, measured.used_entries);
    *book = (native_vorbis_codebook_t){measured,
        measured.used_entries ? words : NULL, measured.used_entries, quantization};
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool book_valid(const native_vorbis_codebook_t *book) {
    if (!book) return false;
    const native_vorbis_codebook_layout_t *l = &book->layout;
    return l->quantization.dimensions <= 65535 && l->quantization.entries <= UINT32_C(0xffffff) &&
        l->used_entries <= l->quantization.entries && book->word_count == l->used_entries &&
        (!l->used_entries || book->words) &&
        (l->used_entries ? (l->maximum_length >= 1 && l->maximum_length <= 32) : !l->maximum_length) &&
        (l->used_entries != 1 || l->maximum_length == 1) &&
        quant_equal(&l->quantization, &book->quantization.layout);
}

native_vorbis_numeric_status_t native_vorbis_codebook_decode(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet, uint32_t *entry) {
    if (!entry || !book_valid(book) || !cursor_valid(packet) || !book->word_count)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (packet->end_of_packet) return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    if (!packet->bits || packet->position == packet->bits) {
        packet->end_of_packet = true;
        return NATIVE_VORBIS_NUMERIC_TRUNCATED;
    }
    const native_vorbis_codeword_t *word;
    if (book->word_count == 1) {
        word = &book->words[0]; // The erratum tolerates both bit0 and bit1.
        if (word->length != 1 || word->code) return NATIVE_VORBIS_NUMERIC_INVALID;
    } else {
        uint64_t remaining = packet->bits - packet->position;
        unsigned width = book->layout.maximum_length;
        if (remaining < width) width = (unsigned)remaining;
        uint32_t key = 0;
        for (unsigned i = 0; i < width; ++i) {
            uint64_t bit = packet->position + i;
            if ((packet->data[(size_t)(bit / 8)] >> (bit % 8)) & 1U)
                key |= UINT32_C(1) << (31 - i);
        }
        size_t low = 0, high = book->word_count;
        while (high - low > 1) {
            size_t middle = low + (high - low) / 2;
            if (book->words[middle].code <= key) low = middle;
            else high = middle;
        }
        word = &book->words[low];
        if (!word->length || word->length > 32 || word->length > book->layout.maximum_length)
            return NATIVE_VORBIS_NUMERIC_INVALID;
        if (word->length > remaining) {
            packet->end_of_packet = true;
            return NATIVE_VORBIS_NUMERIC_TRUNCATED;
        }
        uint32_t mask = UINT32_MAX << (32 - word->length);
        if ((key & mask) != word->code) return NATIVE_VORBIS_NUMERIC_INVALID;
    }
    if (word->entry >= book->layout.quantization.entries) return NATIVE_VORBIS_NUMERIC_INVALID;
    packet->position += word->length;
    *entry = word->entry;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t vq_valid(const native_vorbis_codebook_t *book) {
    if (!book_valid(book) || !book->word_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    return native_vorbis_quantization_vector(&book->quantization, 0, 0, NULL, 0);
}

native_vorbis_numeric_status_t native_vorbis_codebook_vector(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet,
    size_t prefix, native_vorbis_affine_t *output, size_t capacity) {
    native_vorbis_numeric_status_t status = vq_valid(book);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!cursor_valid(packet) || prefix > book->layout.quantization.dimensions || (prefix && !output))
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (prefix > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!prefix) return NATIVE_VORBIS_NUMERIC_OK;
    native_vorbis_packet_t next = *packet;
    uint32_t entry;
    status = native_vorbis_codebook_decode(book, &next, &entry);
    if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) packet->end_of_packet = true;
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_quantization_vector(&book->quantization, entry, prefix, output, capacity);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *packet = next;
    return status;
}

native_vorbis_numeric_status_t native_vorbis_codebook_floor0_lsp(
    const native_vorbis_codebook_t *book, native_vorbis_packet_t *packet,
    size_t order, native_vorbis_affine_t *output, size_t capacity) {
    native_vorbis_numeric_status_t status = vq_valid(book);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!cursor_valid(packet) || !output || !order || order > 255)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (capacity < order) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    size_t count = (order - 1) / book->layout.quantization.dimensions + 1;
    uint32_t entries[255];
    native_vorbis_packet_t next = *packet;
    for (size_t i = 0; i < count; ++i) {
        status = native_vorbis_codebook_decode(book, &next, &entries[i]);
        if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) packet->end_of_packet = true;
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    status = native_vorbis_floor0_lsp_from_entries(
        &book->quantization, entries, count, order, output, capacity);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *packet = next;
    return status;
}
