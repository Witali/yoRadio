// Exact dyadic floor1 multiplication. The table is copied from Xiph libvorbis.
#include "native_vorbis_floor1_product.h"
#include <limits.h>
#include <string.h>
#include "floor1_table.h"

enum { SOURCE_LIMBS = 34, PRODUCT_LIMBS = 36 };

static uint32_t integer_log(uint32_t value) {
    uint32_t result = 0;
    while (value) { ++result; value >>= 1; }
    return result;
}

// Reading the binary32 table by memcpy avoids type punning and performs no
// floating multiplication. All256 entries are positive normals in (0,1].
static void factor(uint8_t index, uint32_t *mantissa, int32_t *exponent) {
    uint32_t bits;
    memcpy(&bits, &native_floor1_from_db[index], sizeof(bits));
    *mantissa = (bits & UINT32_C(0x7fffff)) | UINT32_C(0x800000);
    *exponent = (int32_t)((bits >> 23) & 255U) - 150;
    while (!(*mantissa & 1U)) { *mantissa >>= 1; ++*exponent; }
}

static bool source_valid(const native_vorbis_residue_layout_t *source) {
    if (!source || !source->bins || source->bins > 4096 || !source->channels ||
        source->channels > 255 ||
        source->sample_count != (uint64_t)source->bins * source->channels ||
        source->limb_count != source->sample_count * source->limbs)
        return false;
    if (!source->limbs)
        return !source->magnitude_bits && !source->exponent;
    return source->limbs <= SOURCE_LIMBS && source->magnitude_bits &&
        source->magnitude_bits <= SOURCE_LIMBS * 32 - 1 &&
        source->limbs == (source->magnitude_bits + 32) / 32;
}

native_vorbis_numeric_status_t native_vorbis_floor1_scale_measure(
    const native_vorbis_residue_layout_t *source,
    const uint8_t *indices, size_t count,
    native_vorbis_floor1_product_layout_t *layout) {
    if (!layout || !source_valid(source) || count != source->bins)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor1_product_layout_t value = {.bins = source->bins};
    if (source->limbs) {
        if (!indices) return NATIVE_VORBIS_NUMERIC_INVALID;
        int32_t low = 0, high = INT32_MIN;
        for (size_t i = 0; i < count; ++i) {
            uint32_t mantissa;
            int32_t exponent;
            factor(indices[i], &mantissa, &exponent);
            if (exponent < low) low = exponent;
            int32_t top = exponent + (int32_t)integer_log(mantissa - 1);
            if (top > high) high = top;
        }
        int64_t exponent = (int64_t)source->exponent + low;
        if (exponent < INT32_MIN || exponent > INT32_MAX)
            return NATIVE_VORBIS_NUMERIC_RANGE;
        value.exponent = (int32_t)exponent;
        value.magnitude_bits = source->magnitude_bits + (uint32_t)(high - low);
        value.limbs = (value.magnitude_bits + 32) / 32;
        if (value.limbs > PRODUCT_LIMBS) return NATIVE_VORBIS_NUMERIC_RANGE;
        value.limb_count = (uint64_t)value.bins * value.limbs;
    }
    *layout = value;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool sample_valid(const uint32_t *sample,
                         const native_vorbis_residue_layout_t *source) {
    uint32_t word = source->magnitude_bits / 32;
    uint32_t bit = source->magnitude_bits % 32;
    uint32_t low_mask = bit ? (UINT32_C(1) << bit) - 1 : 0;
    bool negative = (sample[source->limbs - 1] >> 31) != 0;
    bool lower_nonzero = (sample[word] & low_mask) != 0;
    for (uint32_t i = 0; i < word; ++i) lower_nonzero |= sample[i] != 0;
    for (uint32_t i = word; i < source->limbs; ++i) {
        uint32_t mask = i == word ? ~low_mask : UINT32_MAX;
        if ((sample[i] & mask) != (negative ? mask : 0)) return false;
    }
    return !negative || lower_nonzero;
}

static void multiply(const uint32_t *input, uint32_t input_limbs,
    uint32_t mantissa, uint32_t shift, uint32_t *output, uint32_t limbs) {
    uint32_t extension = input[input_limbs - 1] >> 31 ? UINT32_MAX : 0;
    uint64_t carry = 0;
    for (uint32_t i = 0; i < limbs; ++i) {
        uint32_t word = i < input_limbs ? input[i] : extension;
        uint64_t product = (uint64_t)word * mantissa + carry;
        output[i] = (uint32_t)product;
        carry = product >> 32;
    }
    uint32_t words = shift / 32, bits = shift % 32;
    for (uint32_t i = limbs; i; --i) {
        uint32_t at = i - 1, value = 0;
        if (at >= words) {
            uint32_t from = at - words;
            value = output[from] << bits;
            if (bits && from) value |= output[from - 1] >> (32 - bits);
        }
        output[at] = value;
    }
}

native_vorbis_numeric_status_t native_vorbis_floor1_scale(
    const native_vorbis_residue_layout_t *source,
    const uint32_t *spectrum, size_t spectrum_capacity, uint32_t channel,
    const uint8_t *indices, size_t count,
    uint32_t *output, size_t output_capacity,
    native_vorbis_floor1_product_t *result) {
    if (!result || !source || channel >= source->channels)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor1_product_t value = {0};
    native_vorbis_numeric_status_t status = native_vorbis_floor1_scale_measure(
        source, indices, count, &value.layout);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (spectrum_capacity > SIZE_MAX / sizeof(*spectrum) ||
        output_capacity > SIZE_MAX / sizeof(*output) ||
        source->limb_count > SIZE_MAX / sizeof(*spectrum) ||
        value.layout.limb_count > SIZE_MAX / sizeof(*output))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    if (spectrum_capacity < source->limb_count || output_capacity < value.layout.limb_count)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (source->limbs) {
        if (!spectrum || !output) return NATIVE_VORBIS_NUMERIC_INVALID;
        const uint32_t *input = spectrum + (size_t)channel * source->bins * source->limbs;
        for (size_t bin = 0; bin < source->bins; ++bin)
            if (!sample_valid(input + bin * source->limbs, source))
                return NATIVE_VORBIS_NUMERIC_INVALID;
        for (size_t bin = 0; bin < source->bins; ++bin) {
            uint32_t mantissa;
            int32_t exponent;
            factor(indices[bin], &mantissa, &exponent);
            uint32_t shift = (uint32_t)((int64_t)source->exponent + exponent - value.layout.exponent);
            multiply(input + bin * source->limbs, source->limbs, mantissa, shift,
                output + bin * value.layout.limbs, value.layout.limbs);
        }
        value.samples = output;
    }
    *result = value;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t prepare_frame(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity, bool *zero) {
    if (!frame || !frame->setup || !frame->floors || !frame->floor_count ||
        frame->floor_count > 255 || channel >= frame->floor_count ||
        !source_valid(&frame->spectrum_layout) ||
        frame->spectrum_layout.channels != frame->floor_count ||
        frame->spectrum_layout.bins != frame->prefix.blocksize / 2 ||
        frame->spectrum_layout.mapping != frame->prefix.mapping)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_mapping_setup_t mapping;
    native_vorbis_numeric_status_t status = native_vorbis_setup_mapping(
        frame->setup, frame->prefix.mapping, &mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    const native_vorbis_frame_floor_t *record = &frame->floors[channel];
    if (mapping.channels != frame->floor_count || record->state.type != 1 ||
        record->state.present > 1 ||
        record->state.floor_index != mapping.submaps[3 * mapping.mux[channel] + 1])
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor1_setup_t floor;
    status = native_vorbis_setup_floor1(frame->setup, record->state.floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *zero = !record->state.present || !frame->spectrum_layout.limbs;
    if (*zero) return NATIVE_VORBIS_NUMERIC_OK;
    if (!frame->floor1 || record->value_offset > frame->floor1_count ||
        floor.post_count > frame->floor1_count - record->value_offset ||
        record->state.value_count != floor.post_count)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (curve_capacity < frame->spectrum_layout.bins) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!curve) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t y[65];
    uint8_t active[65];
    status = native_vorbis_floor1_reconstruct(frame->setup, record->state.floor_index,
        frame->floor1 + record->value_offset, floor.post_count, y, active, 65);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return native_vorbis_floor1_curve(frame->setup, record->state.floor_index,
        y, active, floor.post_count, curve, frame->spectrum_layout.bins, curve_capacity);
}

native_vorbis_numeric_status_t native_vorbis_frame_floor1_measure(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity,
    native_vorbis_floor1_product_layout_t *layout) {
    if (!layout) return NATIVE_VORBIS_NUMERIC_INVALID;
    bool zero;
    native_vorbis_numeric_status_t status = prepare_frame(frame, channel, curve, curve_capacity, &zero);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!zero) return native_vorbis_floor1_scale_measure(&frame->spectrum_layout,
        curve, frame->spectrum_layout.bins, layout);
    *layout = (native_vorbis_floor1_product_layout_t){.bins = frame->spectrum_layout.bins};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_frame_floor1_product(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity,
    uint32_t *output, size_t output_capacity,
    native_vorbis_floor1_product_t *result) {
    if (!result) return NATIVE_VORBIS_NUMERIC_INVALID;
    bool zero;
    native_vorbis_numeric_status_t status = prepare_frame(frame, channel, curve, curve_capacity, &zero);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (!zero) return native_vorbis_floor1_scale(&frame->spectrum_layout,
        frame->spectrum, (size_t)frame->spectrum_layout.limb_count, channel,
        curve, frame->spectrum_layout.bins, output, output_capacity, result);
    if (output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    *result = (native_vorbis_floor1_product_t){.layout = {.bins = frame->spectrum_layout.bins}};
    return NATIVE_VORBIS_NUMERIC_OK;
}
