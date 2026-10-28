// Preserve exact front-end residue until multiplication by a floor0 factor.
#include "native_vorbis_floor0_spectrum.h"
#include "product.h"
#include <float.h>
#include <limits.h>
#include <math.h>
#include <string.h>

_Static_assert(sizeof(double) == sizeof(uint64_t) && DBL_MANT_DIG == 53 &&
    DBL_MAX_EXP == 1024 && FLT_RADIX == 2, "binary64 storage required");

typedef struct {
    native_vorbis_floor0_setup_t floor;
    const native_vorbis_frame_floor_t *record;
    const native_vorbis_affine_t *angles;
    const uint32_t *samples;
} channel_view_t;

static bool add_checked(int64_t a, int64_t b, int64_t *result) {
    if ((b > 0 && a > INT64_MAX - b) || (b < 0 && a < INT64_MIN - b)) return false;
    *result = a + b;
    return true;
}

static bool subtract_checked(int64_t a, int64_t b, int64_t *result) {
    if ((b > 0 && a < INT64_MIN + b) || (b < 0 && a > INT64_MAX + b)) return false;
    *result = a - b;
    return true;
}

static native_vorbis_numeric_status_t frame_view(
    const native_vorbis_packet_frame_t *frame, uint32_t channel, channel_view_t *view) {
    if (!frame || !frame->setup || !frame->floors || !frame->floor_count ||
        frame->floor_count > 255 || channel >= frame->floor_count ||
        !native_floor0_source_valid(&frame->spectrum_layout) ||
        frame->spectrum_layout.channels != frame->floor_count ||
        frame->prefix.blocksize < 64 || frame->prefix.blocksize > 8192 ||
        (frame->prefix.blocksize & (frame->prefix.blocksize - 1)) ||
        frame->spectrum_layout.bins != frame->prefix.blocksize / 2 ||
        frame->spectrum_layout.mapping != frame->prefix.mapping)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (frame->spectrum_layout.limb_count > SIZE_MAX / sizeof(*frame->spectrum) ||
        frame->floor0_count > SIZE_MAX / sizeof(*frame->floor0)) return NATIVE_VORBIS_NUMERIC_RANGE;
    native_vorbis_mapping_setup_t mapping;
    native_vorbis_numeric_status_t status = native_vorbis_setup_mapping(
        frame->setup, frame->prefix.mapping, &mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    const native_vorbis_frame_floor_t *record = &frame->floors[channel];
    if (mapping.channels != frame->floor_count || !mapping.submap_count ||
        mapping.submap_count > 16 || !mapping.mux || !mapping.submaps ||
        mapping.mux[channel] >= mapping.submap_count || record->state.type != 0 ||
        record->state.present > 1 ||
        record->state.floor_index != mapping.submaps[3 * mapping.mux[channel] + 1])
        return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_floor0_setup_t floor;
    status = native_vorbis_setup_floor0(frame->setup, record->state.floor_index, &floor);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (floor.order > 255 || floor.rate > 65535 || floor.bark_map_size > 65535 ||
        floor.amplitude_bits > 63 || floor.amplitude_offset > 255)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    *view = (channel_view_t){.floor = floor, .record = record};
    return NATIVE_VORBIS_NUMERIC_OK;
}

static double affine_term(uint32_t packed, uint32_t multiplier) {
    // The integer has at most53 bits; scaling remains normal and finite.
    uint64_t magnitude = (uint64_t)(packed & UINT32_C(0x1fffff)) * multiplier;
    double value = (double)magnitude;
    if (packed & UINT32_C(0x80000000)) value = -value;
    int exponent = (int)((packed >> 21) & 1023U) - 788;
    return scalbn(value, exponent);
}

static bool affine_zero(const native_vorbis_affine_t *value) {
    double minimum = affine_term(value->minimum_bits, value->minimum_multiplier);
    double delta = affine_term(value->delta_bits, value->delta_multiplier);
    // Every exact nonzero sum is an integer multiple of2^-788, too large to
    // underflow. The terms themselves are exact and their sum cannot overflow.
    return minimum + delta == 0.0;
}

static native_vorbis_numeric_status_t active_domain(
    const native_vorbis_packet_frame_t *frame, channel_view_t *view,
    native_vorbis_floor0_route_t *route) {
    const native_vorbis_floor_packet_t *state = &view->record->state;
    const native_vorbis_floor0_setup_t *floor = &view->floor;
    if (state->value_count != floor->order ||
        view->record->value_offset > frame->floor0_count ||
        floor->order > frame->floor0_count - view->record->value_offset ||
        (floor->order && !frame->floor0) ||
        state->amplitude.amplitude_bits != floor->amplitude_bits ||
        state->amplitude.amplitude_offset != floor->amplitude_offset ||
        !floor->amplitude_bits || !state->amplitude.raw_amplitude ||
        state->amplitude.raw_amplitude > (UINT64_C(1) << floor->amplitude_bits) - 1)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    view->angles = floor->order ? frame->floor0 + view->record->value_offset : NULL;
    *route = NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE;
    if (!floor->rate || !floor->bark_map_size) {
        *route = NATIVE_VORBIS_FLOOR0_UNDEFINED_MAPPING;
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    for (uint32_t i = 0; i < floor->order; i += 2) {
        if (affine_zero(&view->angles[i])) {
            *route = floor->amplitude_offset ? NATIVE_VORBIS_FLOOR0_UNDEFINED_POLE :
                NATIVE_VORBIS_FLOOR0_UNDEFINED_INDETERMINATE;
            break;
        }
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t selected_samples(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    channel_view_t *view, bool *zero) {
    *zero = true;
    uint32_t limbs = frame->spectrum_layout.limbs;
    if (!limbs) return NATIVE_VORBIS_NUMERIC_OK;
    if (!frame->spectrum) return NATIVE_VORBIS_NUMERIC_INVALID;
    view->samples = frame->spectrum + (size_t)channel * frame->spectrum_layout.bins * limbs;
    for (uint32_t bin = 0; bin < frame->spectrum_layout.bins; ++bin) {
        const uint32_t *sample = view->samples + (size_t)bin * limbs;
        if (!native_floor0_sample_valid(sample, &frame->spectrum_layout))
            return NATIVE_VORBIS_NUMERIC_INVALID;
        if (!native_floor0_sample_zero(sample, limbs)) *zero = false;
    }
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t publish_route(
    native_vorbis_floor0_spectrum_plan_t *candidate, native_vorbis_floor0_route_t route,
    uint32_t bin, native_vorbis_floor0_spectrum_plan_t *plan) {
    candidate->route = route;
    candidate->route_sample = bin;
    candidate->factors = NULL;
    candidate->bark_map = NULL;
    candidate->exponent = 0;
    candidate->zero = false;
    *plan = *candidate;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static native_vorbis_numeric_status_t factor_from_gain(
    const native_vorbis_floor0_gain_t *gain, int32_t residue_exponent,
    native_vorbis_floor0_factor_t *factor, uint32_t *fraction_bits) {
    if (gain->kind != NATIVE_VORBIS_FLOOR0_PRESENT ||
        !isfinite(gain->log2_gain.mantissa) ||
        (gain->log2_gain.mantissa != 0.0 &&
         (fabs(gain->log2_gain.mantissa) < 0.5 || fabs(gain->log2_gain.mantissa) >= 1.0)))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    int64_t retained = 53 - (int64_t)gain->log2_gain.exponent;
    *fraction_bits = retained < 0 ? 0 : retained > 53 ? 53 : (uint32_t)retained;
    if (gain->log2_gain.mantissa != 0.0 && gain->log2_gain.exponent >= 53)
        return NATIVE_VORBIS_NUMERIC_RANGE;
    double logarithm = gain->log2_gain.exponent < -1074 ? 0.0 :
        scalbn(gain->log2_gain.mantissa, gain->log2_gain.exponent);
    // The accepted stored logarithm has magnitude<2^52. Truncation and the
    // following floor correction therefore cannot overflow signed64.
    int64_t integer = (int64_t)logarithm;
    if (logarithm < (double)integer) --integer;
    double fraction = logarithm - (double)integer;
    if (fraction < 0.0 || fraction > 1.0) return NATIVE_VORBIS_NUMERIC_RANGE;
    double coefficient = exp2(fraction);
    if (!isfinite(coefficient) || coefficient < 1.0 || coefficient > 2.0)
        return NATIVE_VORBIS_NUMERIC_RANGE;
    uint64_t bits;
    memcpy(&bits, &coefficient, sizeof(bits));
    int64_t exponent;
    if (!add_checked(integer, (int64_t)((bits >> 52) & 2047U) - 1075, &exponent) ||
        !add_checked(exponent, residue_exponent, &exponent)) return NATIVE_VORBIS_NUMERIC_RANGE;
    *factor = (native_vorbis_floor0_factor_t){
        .mantissa = (bits & UINT64_C(0x000fffffffffffff)) | (UINT64_C(1) << 52),
        .exponent = exponent};
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_frame_floor0_prepare(
    const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint16_t *bark_map, size_t map_capacity,
    native_vorbis_floor0_factor_t *factors, size_t factor_capacity,
    native_vorbis_floor0_spectrum_plan_t *plan) {
    if (!plan) return NATIVE_VORBIS_NUMERIC_INVALID;
    channel_view_t view;
    native_vorbis_numeric_status_t status = frame_view(frame, channel, &view);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_floor0_spectrum_plan_t candidate = {.frame = frame, .channel = channel,
        .bins = frame->spectrum_layout.bins, .route = NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE,
        .minimum_log_fraction_bits = 53, .route_sample = UINT32_MAX};
    if (!view.record->state.present) {
        candidate.zero = true;
        *plan = candidate;
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    native_vorbis_floor0_route_t route;
    status = active_domain(frame, &view, &route);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (route != NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE)
        return publish_route(&candidate, route, route == NATIVE_VORBIS_FLOOR0_UNDEFINED_MAPPING ?
            UINT32_MAX : 0, plan);
    bool zero;
    status = selected_samples(frame, channel, &view, &zero);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    if (zero) {
        candidate.zero = true;
        *plan = candidate;
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    if (map_capacity > SIZE_MAX / sizeof(*bark_map) ||
        factor_capacity > SIZE_MAX / sizeof(*factors)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (map_capacity < candidate.bins || factor_capacity < candidate.bins)
        return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!bark_map || !factors) return NATIVE_VORBIS_NUMERIC_INVALID;
    status = native_vorbis_floor0_bark_map(view.floor.rate, candidate.bins,
        view.floor.bark_map_size, bark_map, map_capacity);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    bool unity = !view.floor.amplitude_offset || (!view.floor.order &&
        view.record->state.amplitude.raw_amplitude ==
            (UINT64_C(1) << view.floor.amplitude_bits) - 1);
    uint32_t previous_bark = UINT32_MAX;
    native_vorbis_floor0_factor_t cached = {0};
    uint32_t cached_fraction_bits = 53;
    int64_t minimum_top = INT64_MAX, maximum_top = INT64_MIN;
    uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS];
    for (uint32_t bin = 0; bin < candidate.bins; ++bin) {
        const uint32_t *sample = view.samples + (size_t)bin * frame->spectrum_layout.limbs;
        if (native_floor0_sample_zero(sample, frame->spectrum_layout.limbs)) {
            factors[bin] = (native_vorbis_floor0_factor_t){0};
            continue;
        }
        if (unity) {
            factors[bin] = (native_vorbis_floor0_factor_t){.mantissa = UINT64_C(1) << 52,
                .exponent = (int64_t)frame->spectrum_layout.exponent - 52};
        } else {
            if (bark_map[bin] != previous_bark) {
                native_vorbis_floor0_gain_t gain;
                status = native_vorbis_floor0_packet_gain(frame->setup,
                    view.record->state.floor_index, &view.record->state,
                    view.angles, view.floor.order, bark_map[bin], &gain);
                ++candidate.gain_evaluations;
                candidate.approximate = true;
                if (status != NATIVE_VORBIS_NUMERIC_OK && status != NATIVE_VORBIS_NUMERIC_RANGE)
                    return status;
                if (status != NATIVE_VORBIS_NUMERIC_OK ||
                    factor_from_gain(&gain, frame->spectrum_layout.exponent,
                        &cached, &cached_fraction_bits) != NATIVE_VORBIS_NUMERIC_OK) {
                    candidate.minimum_log_fraction_bits = 0;
                    return publish_route(&candidate, NATIVE_VORBIS_FLOOR0_NEEDS_PRECISION, bin, plan);
                }
                previous_bark = bark_map[bin];
            }
            factors[bin] = cached;
            if (cached_fraction_bits < candidate.minimum_log_fraction_bits)
                candidate.minimum_log_fraction_bits = cached_fraction_bits;
        }
        bool negative;
        int32_t highest = native_floor0_product(sample, frame->spectrum_layout.limbs,
            factors[bin].mantissa, magnitude, &negative);
        int64_t top;
        if (highest < 0 || !add_checked(factors[bin].exponent, highest, &top))
            return publish_route(&candidate, NATIVE_VORBIS_FLOOR0_NEEDS_WIDER, bin, plan);
        if (top < minimum_top) minimum_top = top;
        if (top > maximum_top) maximum_top = top;
    }
    int64_t span;
    if (!subtract_checked(maximum_top, minimum_top, &span) || span > 1660 ||
        !subtract_checked(maximum_top, 638, &candidate.exponent))
        return publish_route(&candidate, NATIVE_VORBIS_FLOOR0_NEEDS_WIDER, UINT32_MAX, plan);
    candidate.factors = factors;
    candidate.bark_map = bark_map;
    *plan = candidate;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static bool working_top(int64_t exponent, int32_t highest, int64_t common, int32_t *top) {
    int64_t physical, relative;
    if (!add_checked(exponent, highest, &physical) || !subtract_checked(physical, common, &relative) ||
        relative < -1022 || relative > 638) return false;
    *top = (int32_t)relative;
    return true;
}

native_vorbis_numeric_status_t native_vorbis_frame_floor0_materialize(
    const native_vorbis_floor0_spectrum_plan_t *plan,
    double *output, size_t output_capacity,
    native_vorbis_transform_block_t *result) {
    if (!plan || !result || plan->route != NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE ||
        plan->minimum_log_fraction_bits > 53 || plan->route_sample != UINT32_MAX)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    channel_view_t view;
    native_vorbis_numeric_status_t status = frame_view(plan->frame, plan->channel, &view);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    const native_vorbis_packet_frame_t *frame = plan->frame;
    if (plan->bins != frame->spectrum_layout.bins || plan->gain_evaluations > plan->bins)
        return NATIVE_VORBIS_NUMERIC_INVALID;
    if (output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_NUMERIC_RANGE;
    if (output_capacity < plan->bins) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!output) return NATIVE_VORBIS_NUMERIC_INVALID;
    bool zero = !view.record->state.present;
    if (!zero) {
        native_vorbis_floor0_route_t route;
        status = active_domain(frame, &view, &route);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        if (route != NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE) return NATIVE_VORBIS_NUMERIC_INVALID;
        status = selected_samples(frame, plan->channel, &view, &zero);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    if (zero != plan->zero || (zero && (plan->exponent || plan->factors || plan->bark_map ||
        plan->gain_evaluations || plan->approximate))) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t magnitude[NATIVE_FLOOR0_PRODUCT_LIMBS];
    if (!zero) {
        if (!plan->factors || !plan->bark_map) return NATIVE_VORBIS_NUMERIC_INVALID;
        for (uint32_t bin = 0; bin < plan->bins; ++bin) {
            const uint32_t *sample = view.samples + (size_t)bin * frame->spectrum_layout.limbs;
            const native_vorbis_floor0_factor_t *factor = &plan->factors[bin];
            bool sample_zero = native_floor0_sample_zero(sample, frame->spectrum_layout.limbs);
            if (plan->bark_map[bin] >= view.floor.bark_map_size ||
                (sample_zero && (factor->mantissa || factor->exponent)) ||
                (!sample_zero && (factor->mantissa < (UINT64_C(1) << 52) ||
                                 factor->mantissa >= (UINT64_C(1) << 53))))
                return NATIVE_VORBIS_NUMERIC_INVALID;
            if (!sample_zero) {
                bool negative;
                int32_t highest = native_floor0_product(sample, frame->spectrum_layout.limbs,
                    factor->mantissa, magnitude, &negative), top;
                if (highest < 0 || !working_top(factor->exponent, highest, plan->exponent, &top))
                    return NATIVE_VORBIS_NUMERIC_RANGE;
            }
        }
    }
    for (uint32_t bin = 0; bin < plan->bins; ++bin) {
        if (zero || !plan->factors[bin].mantissa) {
            output[bin] = 0.0;
        } else {
            bool negative;
            int32_t highest = native_floor0_product(
                view.samples + (size_t)bin * frame->spectrum_layout.limbs,
                frame->spectrum_layout.limbs, plan->factors[bin].mantissa, magnitude, &negative);
            int32_t top = 0;
            // The immutable successful-plan preflight proved this call valid.
            (void)working_top(plan->factors[bin].exponent, highest, plan->exponent, &top);
            output[bin] = native_floor0_round(magnitude, (uint32_t)highest, top, negative);
        }
    }
    *result = (native_vorbis_transform_block_t){.count = plan->bins,
        .exponent = zero ? 0 : plan->exponent, .samples = output};
    return NATIVE_VORBIS_NUMERIC_OK;
}
