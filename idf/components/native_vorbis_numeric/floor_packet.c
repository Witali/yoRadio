// Public packet floors and integer floor1 equations, Vorbis I sections6/7/9.
// https://xiph.org/vorbis/doc/Vorbis_I_spec.html
#include "native_vorbis_floor_packet.h"
#include <limits.h>
#include <string.h>

static unsigned integer_log(uint32_t value) {
    unsigned width = 0;
    while (value) { ++width; value >>= 1; }
    return width;
}

static native_vorbis_numeric_status_t publish_unused(
    native_vorbis_packet_t *packet, const native_vorbis_packet_t *next,
    native_vorbis_floor_packet_t *state, const native_vorbis_floor_packet_t *result) {
    *packet = *next;
    *state = *result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_packet(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    native_vorbis_packet_t *packet, native_vorbis_affine_t *coefficients,
    size_t capacity, native_vorbis_floor_packet_t *state) {
    if (!packet || !state) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor0_setup_t floor;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor0(setup, floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_floor_packet_t result = {floor_index, 0, 0, 0, UINT32_MAX,
        {0, floor.amplitude_bits, floor.amplitude_offset}};
    native_vorbis_packet_t next = *packet;
    status = native_vorbis_packet_read(&next, floor.amplitude_bits, &result.amplitude.raw_amplitude);
    if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED ||
        (status == NATIVE_VORBIS_NUMERIC_OK && !result.amplitude.raw_amplitude))
        return publish_unused(packet, &next, state, &result);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (floor.order > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (floor.order && !coefficients) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint64_t selector;
    status = native_vorbis_packet_read(&next, integer_log(floor.book_count), &selector);
    if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) return publish_unused(packet, &next, state, &result);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (selector >= floor.book_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    result.selected_book = floor.books[(size_t)selector];
    if (result.selected_book >= setup->book_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    const native_vorbis_codebook_t *book = &setup->books[result.selected_book];
    uint32_t dimensions = book->layout.quantization.dimensions;
    if (!dimensions || !book->layout.quantization.lookup_type) return NATIVE_VORBIS_NUMERIC_INVALID;
    // The normative loop reads at least one vector, even when order is zero.
    size_t count = floor.order ? (floor.order - 1) / dimensions + 1 : 1;
    uint32_t entries[255];
    for (size_t i = 0; i < count; ++i) {
        status = native_vorbis_codebook_decode(book, &next, &entries[i]);
        if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) return publish_unused(packet, &next, state, &result);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    if (floor.order) {
        status = native_vorbis_floor0_lsp_from_entries(
            &book->quantization, entries, count, floor.order, coefficients, capacity);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    result.present = 1;
    result.value_count = floor.order;
    *packet = next;
    *state = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static uint32_t floor1_range(uint32_t multiplier) {
    static const uint32_t ranges[4] = {256, 128, 86, 64};
    return multiplier >= 1 && multiplier <= 4 ? ranges[multiplier - 1] : 0;
}

native_vorbis_numeric_status_t native_vorbis_floor1_packet(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    native_vorbis_packet_t *packet, uint32_t *raw_y,
    size_t capacity, native_vorbis_floor_packet_t *state) {
    if (!packet || !state) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor1_setup_t floor;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor1(setup, floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_floor_packet_t result = {floor_index, 1, 0, 0, UINT32_MAX, {0, 0, 0}};
    native_vorbis_packet_t next = *packet;
    uint64_t nonzero;
    status = native_vorbis_packet_read(&next, 1, &nonzero);
    if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED ||
        (status == NATIVE_VORBIS_NUMERIC_OK && !nonzero))
        return publish_unused(packet, &next, state, &result);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (floor.post_count > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!raw_y) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t values[65], range = floor1_range(floor.multiplier);
    if (!range || floor.post_count < 2 || floor.post_count > 65) return NATIVE_VORBIS_NUMERIC_INVALID;
    unsigned width = integer_log(range - 1);
    for (unsigned i = 0; i < 2; ++i) {
        uint64_t raw;
        status = native_vorbis_packet_read(&next, width, &raw);
        if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) return publish_unused(packet, &next, state, &result);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        values[i] = (uint32_t)raw;
    }
    uint32_t offset = 2;
    for (uint32_t i = 0; i < floor.partition_count; ++i) {
        native_vorbis_floor1_class_t cls;
        status = native_vorbis_setup_floor1_class(setup, &floor, floor.partitions[i], &cls);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        uint32_t selection = 0, mask = (UINT32_C(1) << cls.subclass_bits) - 1;
        if (cls.subclass_bits) {
            if (cls.masterbook >= setup->book_count) return NATIVE_VORBIS_NUMERIC_INVALID;
            status = native_vorbis_codebook_decode(&setup->books[cls.masterbook], &next, &selection);
            if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) return publish_unused(packet, &next, state, &result);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        }
        if (cls.dimensions > floor.post_count - offset) return NATIVE_VORBIS_NUMERIC_INVALID;
        for (uint32_t j = 0; j < cls.dimensions; ++j) {
            uint32_t book = cls.books[selection & mask];
            selection >>= cls.subclass_bits;
            values[offset + j] = 0;
            if (book == UINT32_MAX) continue;
            if (book >= setup->book_count) return NATIVE_VORBIS_NUMERIC_INVALID;
            status = native_vorbis_codebook_decode(&setup->books[book], &next, &values[offset + j]);
            if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) return publish_unused(packet, &next, state, &result);
            if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        }
        offset += cls.dimensions;
    }
    if (offset != floor.post_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    memcpy(raw_y, values, (size_t)floor.post_count * sizeof(*raw_y));
    result.present = 1;
    result.value_count = floor.post_count;
    *packet = next;
    *state = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor1_reconstruct(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const uint32_t *raw_y, size_t raw_count, uint32_t *final_y,
    uint8_t *active, size_t capacity) {
    native_vorbis_floor1_setup_t floor;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor1(setup, floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    uint32_t range = floor1_range(floor.multiplier);
    if (!raw_y || !final_y || !active || !range || raw_count != floor.post_count ||
        raw_count < 2 || raw_count > 65) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (raw_count > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    int64_t values[65];
    uint8_t flags[65] = {1, 1};
    values[0] = raw_y[0]; values[1] = raw_y[1];
    for (uint32_t i = 2; i < floor.post_count; ++i) {
        uint32_t low = 0, high = 1;
        for (uint32_t j = 0; j < i; ++j) {
            if (floor.x[j] < floor.x[i] && floor.x[j] > floor.x[low]) low = j;
            if (floor.x[j] > floor.x[i] && floor.x[j] < floor.x[high]) high = j;
        }
        int64_t dy = values[high] - values[low];
        int64_t dx = (int64_t)floor.x[high] - floor.x[low];
        if (dx <= 0) return NATIVE_VORBIS_NUMERIC_INVALID;
        int64_t displacement = (dy < 0 ? -dy : dy) * ((int64_t)floor.x[i] - floor.x[low]) / dx;
        int64_t predicted = values[low] + (dy < 0 ? -displacement : displacement);
        int64_t high_room = (int64_t)range - predicted, low_room = predicted;
        int64_t room = 2 * (high_room < low_room ? high_room : low_room);
        int64_t value = raw_y[i];
        if (value) {
            flags[i] = flags[low] = flags[high] = 1;
            if (value >= room)
                values[i] = high_room > low_room ? value : (int64_t)range - 1 - value;
            else values[i] = predicted + ((value & 1) ? -(value + 1) / 2 : value / 2);
        } else values[i] = predicted;
    }
    // Clamp after all predictions; a malformed early post must not silently
    // change the input used to predict a later post. Products stay below2^48
    // even for the arithmetic helper's full uint32 domain and X<=32768.
    for (size_t i = 0; i < raw_count; ++i) {
        final_y[i] = values[i] < 0 ? 0 : values[i] >= range ? range - 1 : (uint32_t)values[i];
        active[i] = flags[i];
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static void line_indices(uint32_t x0, uint32_t x1, int32_t y0, int32_t y1,
                         uint8_t *indices, size_t bins) {
    uint32_t dx = x1 - x0;
    int32_t dy = y1 - y0, base = dy / (int32_t)dx;
    int32_t step = base + (dy < 0 ? -1 : 1);
    uint32_t remainder = (uint32_t)(dy < 0 ? -dy : dy) -
        (uint32_t)(base < 0 ? -base : base) * dx;
    uint32_t error = 0;
    size_t end = x1 < bins ? x1 : bins;
    int32_t y = y0;
    for (size_t x = x0; x < end; ++x) {
        indices[x] = (uint8_t)y;
        error += remainder;
        if (error >= dx) { error -= dx; y += step; }
        else y += base;
    }
}

native_vorbis_numeric_status_t native_vorbis_floor1_curve(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const uint32_t *final_y, const uint8_t *active, size_t count,
    uint8_t *indices, size_t bins, size_t capacity) {
    native_vorbis_floor1_setup_t floor;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor1(setup, floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    uint32_t range = floor1_range(floor.multiplier);
    if (!final_y || !active || !indices || !range || count != floor.post_count ||
        count < 2 || count > 65 || !bins || bins > 4096) return NATIVE_VORBIS_NUMERIC_INVALID;
    if (bins > capacity) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!active[0] || !active[1]) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint8_t order[65];
    for (uint32_t i = 0; i < floor.post_count; ++i) {
        if (final_y[i] >= range || active[i] > 1) return NATIVE_VORBIS_NUMERIC_INVALID;
        uint32_t at = i;
        while (at && floor.x[order[at - 1]] > floor.x[i]) { order[at] = order[at - 1]; --at; }
        order[at] = (uint8_t)i;
    }
    uint32_t previous = order[0];
    for (uint32_t i = 1; i < floor.post_count; ++i) if (active[order[i]]) {
        uint32_t next = order[i];
        line_indices(floor.x[previous], floor.x[next], (int32_t)(final_y[previous] * floor.multiplier),
            (int32_t)(final_y[next] * floor.multiplier), indices, bins);
        previous = next;
        if (floor.x[next] >= bins) return NATIVE_VORBIS_NUMERIC_OK;
    }
    uint8_t tail = (uint8_t)(final_y[previous] * floor.multiplier);
    for (size_t i = floor.x[previous]; i < bins; ++i) indices[i] = tail;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_floor0_packet_gain(
    const native_vorbis_setup_t *setup, uint32_t floor_index,
    const native_vorbis_floor_packet_t *state,
    const native_vorbis_affine_t *coefficients, size_t count,
    uint32_t bin, native_vorbis_floor0_gain_t *gain) {
    if (!state || !gain || state->type != 0 || state->floor_index != floor_index || state->present > 1)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor0_setup_t floor;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor0(setup, floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!state->present) {
        native_vorbis_floor0_amplitude_t absent = {0, floor.amplitude_bits, floor.amplitude_offset};
        return native_vorbis_floor0_gain_from_denominator(&absent, NULL, gain);
    }
    if (state->value_count != floor.order || count != floor.order || !floor.rate ||
        !floor.bark_map_size || bin >= floor.bark_map_size ||
        state->amplitude.amplitude_bits != floor.amplitude_bits ||
        state->amplitude.amplitude_offset != floor.amplitude_offset)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (!floor.order) {
        const native_vorbis_scaled_t one = {0.5, 1};
        return native_vorbis_floor0_gain_from_denominator(&state->amplitude, &one, gain);
    }
    return native_vorbis_floor0_gain_from_affine(&state->amplitude, coefficients, count,
        bin, floor.bark_map_size, gain);
}
