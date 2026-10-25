// Public-packet setup graph; Vorbis I sections4,6,7,8.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
#include "native_vorbis_setup.h"
#include <limits.h>

static native_vorbis_numeric_status_t read_field(
    native_vorbis_packet_t *p, unsigned width, uint32_t *value) {
    uint64_t raw;
    native_vorbis_numeric_status_t status = native_vorbis_packet_read(p, width, &raw);
    if (status == NATIVE_VORBIS_NUMERIC_OK) *value = (uint32_t)raw;
    return status;
}

#define READ(value, width) do { \
    status = read_field(p, width, &(value)); \
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status; \
} while (0)
#define REQUIRE(condition) do { \
    if (!(condition)) return NATIVE_VORBIS_NUMERIC_INVALID; \
} while (0)

static unsigned integer_log(uint32_t value) {
    unsigned bits = 0;
    while (value) { value >>= 1; ++bits; }
    return bits;
}

static bool block_valid(uint32_t value) {
    return value >= 64 && value <= 8192 && !(value & (value - 1));
}

static bool identification_valid(const native_vorbis_identification_t *id) {
    return id && id->channels >= 1 && id->channels <= 255 && id->sample_rate &&
        block_valid(id->blocksize_0) && block_valid(id->blocksize_1) &&
        id->blocksize_0 <= id->blocksize_1;
}

static bool identification_equal(const native_vorbis_identification_t *a,
                                  const native_vorbis_identification_t *b) {
    return a->channels == b->channels && a->sample_rate == b->sample_rate &&
        a->bitrate_maximum_bits == b->bitrate_maximum_bits &&
        a->bitrate_nominal_bits == b->bitrate_nominal_bits &&
        a->bitrate_minimum_bits == b->bitrate_minimum_bits &&
        a->blocksize_0 == b->blocksize_0 && a->blocksize_1 == b->blocksize_1;
}

static native_vorbis_numeric_status_t common_header(native_vorbis_packet_t *p, uint32_t type) {
    native_vorbis_numeric_status_t status;
    uint32_t value;
    READ(value, 8);
    REQUIRE(value == type);
    static const uint8_t signature[6] = {'v', 'o', 'r', 'b', 'i', 's'};
    for (unsigned i = 0; i < 6; ++i) {
        READ(value, 8);
        REQUIRE(value == signature[i]);
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_identification_parse(
    const uint8_t *data, size_t bytes, uint64_t bits, native_vorbis_identification_t *id) {
    if (!id) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t cursor, *p = &cursor;
    native_vorbis_numeric_status_t status = native_vorbis_packet_init(p, data, bytes, bits, 0);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = common_header(p, 1);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_identification_t result = {0};
    uint32_t version, small, large, framing;
    READ(version, 32);
    REQUIRE(!version);
    READ(result.channels, 8);
    READ(result.sample_rate, 32);
    READ(result.bitrate_maximum_bits, 32);
    READ(result.bitrate_nominal_bits, 32);
    READ(result.bitrate_minimum_bits, 32);
    READ(small, 4);
    READ(large, 4);
    READ(framing, 1);
    REQUIRE(small >= 6 && small <= 13 && large >= small && large <= 13 && framing);
    result.blocksize_0 = UINT32_C(1) << small;
    result.blocksize_1 = UINT32_C(1) << large;
    REQUIRE(identification_valid(&result));
    *id = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

typedef struct { uint32_t entries; uint16_t dimensions; uint8_t lookup_type, reserved; } book_fact_t;
typedef struct { uint32_t *data; uint32_t used; } configuration_t;

// All record counts are bounded by the format: at most64 descriptors per stage,
// 65 floor1 posts,512 active stage books/residue,256 coupling pairs/mapping.
// Even their combined uint32 pool is below2^18 words; these additions cannot wrap.
static uint32_t reserve(configuration_t *pool, uint32_t count) {
    uint32_t result = pool->used;
    pool->used += count;
    return result;
}
static void set(configuration_t *pool, uint32_t index, uint32_t value) {
    if (pool->data) pool->data[index] = value;
}
static void emit(configuration_t *pool, uint32_t value) {
    uint32_t index = reserve(pool, 1);
    set(pool, index, value);
}

static bool vector_book(const book_fact_t *books, uint32_t count, uint32_t index) {
    return index < count && books[index].dimensions && books[index].lookup_type;
}

static native_vorbis_numeric_status_t floor0_parse(
    native_vorbis_packet_t *p, configuration_t *pool, const book_fact_t *books,
    uint32_t book_count, uint32_t *record) {
    native_vorbis_numeric_status_t status;
    uint32_t order, rate, map, amplitude_bits, offset, count;
    READ(order, 8); READ(rate, 16); READ(map, 16); READ(amplitude_bits, 6);
    READ(offset, 8); READ(count, 4); ++count;
    *record = pool->used;
    emit(pool, 0); emit(pool, order); emit(pool, rate); emit(pool, map);
    emit(pool, amplitude_bits); emit(pool, offset); emit(pool, count);
    // Section6.2.1 gives no positive minima for these three unsigned fields.
    // Preserve zero metadata here; active curve-domain support is a later layer.
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t book;
        READ(book, 8);
        REQUIRE(vector_book(books, book_count, book));
        emit(pool, book);
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t floor1_parse(
    native_vorbis_packet_t *p, configuration_t *pool, uint32_t book_count, uint32_t *record) {
    native_vorbis_numeric_status_t status;
    uint32_t partitions, classes = 0, posts = 2, part[31], offsets[16], x[65];
    uint8_t occurrences[16] = {0};
    READ(partitions, 5);
    for (uint32_t i = 0; i < partitions; ++i) {
        READ(part[i], 4);
        ++occurrences[part[i]];
        if (part[i] + 1 > classes) classes = part[i] + 1;
    }
    for (uint32_t i = 0; i < classes; ++i) {
        uint32_t dimensions, subclass, master = UINT32_MAX;
        READ(dimensions, 3); ++dimensions; READ(subclass, 2);
        posts += dimensions * occurrences[i];
        if (subclass) { READ(master, 8); REQUIRE(master < book_count); }
        offsets[i] = pool->used;
        emit(pool, dimensions); emit(pool, subclass); emit(pool, master);
        for (uint32_t j = 0; j < (UINT32_C(1) << subclass); ++j) {
            uint32_t raw;
            READ(raw, 8);
            REQUIRE(!raw || raw - 1 < book_count);
            emit(pool, raw ? raw - 1 : UINT32_MAX);
        }
    }
    REQUIRE(posts <= 65); // Explicit normative limit in section7.2.2.
    uint32_t multiplier, range;
    READ(multiplier, 2); ++multiplier; READ(range, 4);
    x[0] = 0; x[1] = UINT32_C(1) << range;
    for (uint32_t i = 2; i < posts; ++i) {
        READ(x[i], range);
        for (uint32_t j = 0; j < i; ++j) REQUIRE(x[i] != x[j]);
    }
    *record = pool->used;
    emit(pool, 1); emit(pool, partitions); emit(pool, classes); emit(pool, multiplier);
    emit(pool, range); emit(pool, posts);
    for (uint32_t i = 0; i < partitions; ++i) emit(pool, part[i]);
    for (uint32_t i = 0; i < classes; ++i) emit(pool, offsets[i]);
    for (uint32_t i = 0; i < posts; ++i) emit(pool, x[i]);
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool classification_capacity(uint32_t classifications, const book_fact_t *book) {
    if (!book->dimensions || !book->entries) return false;
    if (classifications == 1) return true;
    uint32_t power = 1;
    for (uint32_t i = 0; i < book->dimensions; ++i) {
        if (power > book->entries / classifications) return false;
        power *= classifications;
    }
    return true;
}

static native_vorbis_numeric_status_t residue_parse(
    native_vorbis_packet_t *p, configuration_t *pool, const book_fact_t *books,
    uint32_t book_count, uint32_t type, uint32_t *record) {
    native_vorbis_numeric_status_t status;
    uint32_t begin, end, grouping, classes, classbook, cascades[64];
    READ(begin, 24); READ(end, 24); READ(grouping, 24); ++grouping;
    READ(classes, 6); ++classes; READ(classbook, 8);
    REQUIRE(classbook < book_count && classification_capacity(classes, &books[classbook]));
    for (uint32_t i = 0; i < classes; ++i) {
        uint32_t low, flag, high = 0;
        READ(low, 3); READ(flag, 1);
        if (flag) { READ(high, 5); }
        cascades[i] = low | (high << 3);
    }
    *record = reserve(pool, 7 + 2 * classes);
    set(pool, *record, type); set(pool, *record + 1, begin); set(pool, *record + 2, end);
    set(pool, *record + 3, grouping); set(pool, *record + 4, classes); set(pool, *record + 5, classbook);
    uint32_t active = 0;
    for (uint32_t i = 0; i < classes; ++i) {
        set(pool, *record + 7 + i, cascades[i]);
        set(pool, *record + 7 + classes + i, active);
        for (unsigned stage = 0; stage < 8; ++stage) if (cascades[i] & (UINT32_C(1) << stage)) {
            uint32_t book;
            READ(book, 8);
            REQUIRE(vector_book(books, book_count, book));
            REQUIRE(grouping % books[book].dimensions == 0);
            emit(pool, book); ++active;
        }
    }
    set(pool, *record + 6, active);
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t mapping_parse(
    native_vorbis_packet_t *p, configuration_t *pool, uint32_t channels,
    uint32_t floors, uint32_t residues, uint32_t *record) {
    native_vorbis_numeric_status_t status;
    uint32_t flag, submaps = 1, coupling = 0, reserved;
    READ(flag, 1);
    if (flag) { READ(submaps, 4); ++submaps; }
    READ(flag, 1);
    if (flag) { READ(coupling, 8); ++coupling; }
    *record = pool->used;
    emit(pool, submaps); emit(pool, coupling); emit(pool, channels);
    unsigned width = integer_log(channels - 1);
    for (uint32_t i = 0; i < coupling; ++i) {
        uint32_t magnitude, angle;
        READ(magnitude, width); READ(angle, width);
        REQUIRE(magnitude < channels && angle < channels && magnitude != angle);
        emit(pool, magnitude); emit(pool, angle);
    }
    READ(reserved, 2); REQUIRE(!reserved);
    for (uint32_t i = 0; i < channels; ++i) {
        uint32_t mux = 0;
        if (submaps > 1) { READ(mux, 4); REQUIRE(mux < submaps); }
        emit(pool, mux);
    }
    for (uint32_t i = 0; i < submaps; ++i) {
        uint32_t time, floor, residue;
        READ(time, 8); READ(floor, 8); READ(residue, 8);
        REQUIRE(floor < floors && residue < residues);
        emit(pool, time); emit(pool, floor); emit(pool, residue);
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t setup_parse(
    const uint8_t *data, size_t bytes, uint64_t bits,
    const native_vorbis_identification_t *id, const native_vorbis_setup_storage_t *storage,
    native_vorbis_setup_layout_t *layout) {
    native_vorbis_packet_t cursor, *p = &cursor;
    native_vorbis_numeric_status_t status = native_vorbis_packet_init(p, data, bytes, bits, 0);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = common_header(p, 5);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_setup_layout_t result = {0};
    result.identification = *id;
    configuration_t pool = {storage ? storage->configuration : NULL, 0};
    book_fact_t books[256];
    READ(result.book_count, 8); ++result.book_count;
    for (uint32_t i = 0; i < result.book_count; ++i) {
        native_vorbis_codebook_layout_t book;
        status = native_vorbis_codebook_measure(data, bytes, bits, p->position, &book);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        books[i] = (book_fact_t){book.quantization.entries, (uint16_t)book.quantization.dimensions,
            (uint8_t)book.quantization.lookup_type, 0};
        if (storage) {
            native_vorbis_codeword_t *words = book.used_entries ? storage->words + (size_t)result.codeword_count : NULL;
            uint16_t *q = book.quantization.multiplicand_count ? storage->multiplicands + (size_t)result.multiplicand_count : NULL;
            status = native_vorbis_codebook_materialize(data, bytes, bits, &book, words, book.used_entries,
                q, (size_t)book.quantization.multiplicand_count, &storage->books[i]);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        }
        result.codeword_count += book.used_entries;
        result.multiplicand_count += book.quantization.multiplicand_count;
        p->position = book.quantization.end_bit;
    }
    READ(result.time_count, 6); ++result.time_count;
    for (uint32_t i = 0; i < result.time_count; ++i) {
        uint32_t type;
        READ(type, 16); REQUIRE(!type);
    }
    READ(result.floor_count, 6); ++result.floor_count;
    result.floor_table = reserve(&pool, result.floor_count);
    for (uint32_t i = 0; i < result.floor_count; ++i) {
        uint32_t type, record;
        READ(type, 16); REQUIRE(type <= 1);
        status = type ? floor1_parse(p, &pool, result.book_count, &record) :
            floor0_parse(p, &pool, books, result.book_count, &record);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        set(&pool, result.floor_table + i, record);
    }
    READ(result.residue_count, 6); ++result.residue_count;
    result.residue_table = reserve(&pool, result.residue_count);
    for (uint32_t i = 0; i < result.residue_count; ++i) {
        uint32_t type, record;
        READ(type, 16); REQUIRE(type <= 2);
        status = residue_parse(p, &pool, books, result.book_count, type, &record);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        set(&pool, result.residue_table + i, record);
    }
    READ(result.mapping_count, 6); ++result.mapping_count;
    result.mapping_table = reserve(&pool, result.mapping_count);
    for (uint32_t i = 0; i < result.mapping_count; ++i) {
        uint32_t type, record;
        READ(type, 16); REQUIRE(!type);
        status = mapping_parse(p, &pool, id->channels, result.floor_count, result.residue_count, &record);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        set(&pool, result.mapping_table + i, record);
    }
    READ(result.mode_count, 6); ++result.mode_count;
    result.mode_table = reserve(&pool, result.mode_count);
    for (uint32_t i = 0; i < result.mode_count; ++i) {
        uint32_t blockflag, window, transform, mapping, record = pool.used;
        READ(blockflag, 1); READ(window, 16); READ(transform, 16); READ(mapping, 8);
        REQUIRE(!window && !transform && mapping < result.mapping_count);
        emit(&pool, blockflag); emit(&pool, mapping);
        set(&pool, result.mode_table + i, record);
    }
    uint32_t framing;
    READ(framing, 1); REQUIRE(framing);
    result.end_bit = p->position;
    result.configuration_count = pool.used;
    *layout = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_measure(
    const uint8_t *data, size_t bytes, uint64_t bits,
    const native_vorbis_identification_t *identification, native_vorbis_setup_layout_t *layout) {
    if (!layout || !identification_valid(identification)) return NATIVE_VORBIS_NUMERIC_INVALID;
    return setup_parse(data, bytes, bits, identification, NULL, layout);
}

static bool layout_equal(const native_vorbis_setup_layout_t *a, const native_vorbis_setup_layout_t *b) {
    return identification_equal(&a->identification, &b->identification) && a->end_bit == b->end_bit &&
        a->codeword_count == b->codeword_count && a->multiplicand_count == b->multiplicand_count &&
        a->book_count == b->book_count && a->time_count == b->time_count && a->floor_count == b->floor_count &&
        a->residue_count == b->residue_count && a->mapping_count == b->mapping_count && a->mode_count == b->mode_count &&
        a->configuration_count == b->configuration_count && a->floor_table == b->floor_table &&
        a->residue_table == b->residue_table && a->mapping_table == b->mapping_table && a->mode_table == b->mode_table;
}

native_vorbis_numeric_status_t native_vorbis_setup_materialize(
    const uint8_t *data, size_t bytes, uint64_t bits, const native_vorbis_setup_layout_t *layout,
    const native_vorbis_setup_storage_t *storage, native_vorbis_setup_t *setup) {
    if (!layout || !storage || !setup) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_setup_layout_t measured;
    native_vorbis_numeric_status_t status = native_vorbis_setup_measure(
        data, bytes, bits, &layout->identification, &measured);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!layout_equal(layout, &measured)) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (measured.codeword_count > SIZE_MAX / sizeof(*storage->words) ||
        measured.multiplicand_count > SIZE_MAX / sizeof(*storage->multiplicands))
        return NATIVE_VORBIS_NUMERIC_RANGE;
#if SIZE_MAX < UINT64_MAX
    if (measured.configuration_count > SIZE_MAX / sizeof(*storage->configuration))
        return NATIVE_VORBIS_NUMERIC_RANGE;
#endif
    if (measured.book_count > storage->book_capacity || measured.codeword_count > storage->word_capacity ||
        measured.multiplicand_count > storage->multiplicand_capacity ||
        measured.configuration_count > storage->configuration_capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!storage->books || !storage->configuration || (measured.codeword_count && !storage->words) ||
        (measured.multiplicand_count && !storage->multiplicands)) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_setup_layout_t written;
    // The identical immutable packet was fully validated before any writes.
    // All per-book slices and the configuration pool have been preflighted.
    status = setup_parse(data, bytes, bits, &measured.identification, storage, &written);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *setup = (native_vorbis_setup_t){written, storage->books, storage->configuration,
        written.book_count, written.configuration_count};
    return NATIVE_VORBIS_NUMERIC_OK;
}

#undef READ
#undef REQUIRE

static bool setup_valid(const native_vorbis_setup_t *setup) {
    if (!setup || !setup->books || !setup->configuration ||
        !identification_valid(&setup->layout.identification)) return false;
    const native_vorbis_setup_layout_t *l = &setup->layout;
    return l->book_count >= 1 && l->book_count <= 256 && l->book_count == setup->book_count &&
        l->time_count >= 1 && l->time_count <= 64 &&
        l->floor_count >= 1 && l->floor_count <= 64 &&
        l->residue_count >= 1 && l->residue_count <= 64 &&
        l->mapping_count >= 1 && l->mapping_count <= 64 &&
        l->mode_count >= 1 && l->mode_count <= 64 &&
        l->configuration_count == setup->configuration_count;
}

static bool span(const native_vorbis_setup_t *setup, uint32_t offset, uint32_t count,
                 const uint32_t **values) {
    if (offset > setup->configuration_count || count > setup->configuration_count - offset) return false;
    *values = setup->configuration + offset;
    return true;
}

static bool record(const native_vorbis_setup_t *setup, uint32_t table,
                   uint32_t count, uint32_t index, uint32_t minimum, const uint32_t **values) {
    const uint32_t *offsets;
    return setup_valid(setup) && index < count && span(setup, table, count, &offsets) &&
        span(setup, offsets[index], minimum, values);
}

native_vorbis_numeric_status_t native_vorbis_setup_floor_type(
    const native_vorbis_setup_t *setup, uint32_t index, uint32_t *type) {
    const uint32_t *r;
    if (!type || !setup || !record(setup, setup->layout.floor_table,
        setup->layout.floor_count, index, 1, &r) || r[0] > 1) return NATIVE_VORBIS_NUMERIC_INVALID;
    *type = r[0];
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_floor0(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_floor0_setup_t *floor) {
    const uint32_t *r;
    if (!floor || !setup || !record(setup, setup->layout.floor_table,
        setup->layout.floor_count, index, 7, &r) || r[0] != 0) return NATIVE_VORBIS_NUMERIC_INVALID;
    *floor = (native_vorbis_floor0_setup_t){r[1], r[2], r[3], r[4], r[5], r[6], r + 7};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_floor1(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_floor1_setup_t *floor) {
    const uint32_t *r;
    if (!floor || !setup || !record(setup, setup->layout.floor_table,
        setup->layout.floor_count, index, 6, &r) || r[0] != 1) return NATIVE_VORBIS_NUMERIC_INVALID;
    const uint32_t *partitions = r + 6, *classes = partitions + r[1], *x = classes + r[2];
    *floor = (native_vorbis_floor1_setup_t){r[1], r[2], r[3], r[4], r[5], partitions, classes, x};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_floor1_class(
    const native_vorbis_setup_t *setup, const native_vorbis_floor1_setup_t *floor,
    uint32_t index, native_vorbis_floor1_class_t *class_info) {
    const uint32_t *r;
    if (!class_info || !floor || !setup_valid(setup) || index >= floor->class_count ||
        !floor->class_offsets || !span(setup, floor->class_offsets[index], 3, &r) || r[1] > 3)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    *class_info = (native_vorbis_floor1_class_t){r[0], r[1], r[2], UINT32_C(1) << r[1], r + 3};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_residue(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_residue_setup_t *residue) {
    const uint32_t *r;
    if (!residue || !setup || !record(setup, setup->layout.residue_table,
        setup->layout.residue_count, index, 7, &r) || r[0] > 2) return NATIVE_VORBIS_NUMERIC_INVALID;
    const uint32_t *cascades = r + 7, *offsets = cascades + r[4], *books = offsets + r[4];
    *residue = (native_vorbis_residue_setup_t){r[0], r[1], r[2], r[3], r[4], r[5], r[6], cascades, offsets, books};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_mapping(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_mapping_setup_t *mapping) {
    const uint32_t *r;
    if (!mapping || !setup || !record(setup, setup->layout.mapping_table,
        setup->layout.mapping_count, index, 3, &r)) return NATIVE_VORBIS_NUMERIC_INVALID;
    const uint32_t *pairs = r + 3, *mux = pairs + 2 * r[1], *submaps = mux + r[2];
    *mapping = (native_vorbis_mapping_setup_t){r[0], r[1], r[2], pairs, mux, submaps};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_setup_mode(
    const native_vorbis_setup_t *setup, uint32_t index, native_vorbis_mode_setup_t *mode) {
    const uint32_t *r;
    if (!mode || !setup || !record(setup, setup->layout.mode_table,
        setup->layout.mode_count, index, 2, &r)) return NATIVE_VORBIS_NUMERIC_INVALID;
    *mode = (native_vorbis_mode_setup_t){r[0], r[1]};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_audio_prefix(
    const native_vorbis_setup_t *setup, native_vorbis_packet_t *packet,
    native_vorbis_audio_prefix_t *prefix) {
    if (!prefix || !packet || !setup_valid(setup)) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t next = *packet;
    native_vorbis_audio_prefix_t result = {0};
    uint32_t type;
    native_vorbis_numeric_status_t status = read_field(&next, 1, &type);
    if (status == NATIVE_VORBIS_NUMERIC_OK && type) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (status == NATIVE_VORBIS_NUMERIC_OK)
        status = read_field(&next, integer_log(setup->layout.mode_count - 1), &result.mode);
    native_vorbis_mode_setup_t mode;
    if (status == NATIVE_VORBIS_NUMERIC_OK) status = native_vorbis_setup_mode(setup, result.mode, &mode);
    if (status == NATIVE_VORBIS_NUMERIC_OK) {
        result.blockflag = mode.blockflag;
        result.mapping = mode.mapping;
        result.blocksize = mode.blockflag ? setup->layout.identification.blocksize_1 : setup->layout.identification.blocksize_0;
        if (mode.blockflag) {
            status = read_field(&next, 1, &result.previous_window);
            if (status == NATIVE_VORBIS_NUMERIC_OK) status = read_field(&next, 1, &result.next_window);
        }
    }
    if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) packet->end_of_packet = true;
    if (status == NATIVE_VORBIS_NUMERIC_OK) { *packet = next; *prefix = result; }
    return status;
}
