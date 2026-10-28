// Persistent ownership and transactional publication above the public DSP APIs.
#include "native_vorbis_decoder.h"
#include "native_vorbis_floor0_spectrum.h"

typedef struct {
    native_vorbis_imdct_plan_t plan;
    double *trig;
    int *bitrev;
} decoder_transform_t;

struct native_vorbis_decoder {
    native_vorbis_setup_allocator_t allocator;
    native_vorbis_setup_owner_t *setup_owner;
    native_vorbis_window_plan_t short_plan, long_plan;
    native_vorbis_synthesis_t synthesis;
    decoder_transform_t transforms[2];
    uint32_t channels, long_size;
    bool end_of_stream;
    double *short_coefficients, *long_coefficients, *history;
    int64_t *exponents;
    double **work;
    native_vorbis_transform_block_t *blocks;
    size_t *capacities;
    double *spectrum;
    uint8_t *curve;
    uint16_t *map;
    native_vorbis_floor0_factor_t *factors;
    uint32_t *product;
    size_t product_capacity;
    native_vorbis_frame_workspace_t frame;
};

static native_vorbis_decoder_status_t parser_status(native_vorbis_numeric_status_t status) {
    switch (status) {
    case NATIVE_VORBIS_NUMERIC_OK: return NATIVE_VORBIS_DECODER_OK;
    case NATIVE_VORBIS_NUMERIC_INVALID: return NATIVE_VORBIS_DECODER_INVALID;
    case NATIVE_VORBIS_NUMERIC_RANGE: return NATIVE_VORBIS_DECODER_RANGE;
    case NATIVE_VORBIS_NUMERIC_TRUNCATED: return NATIVE_VORBIS_DECODER_TRUNCATED;
    default: return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    }
}

static native_vorbis_decoder_status_t setup_status(native_vorbis_setup_owner_status_t status) {
    switch (status) {
    case NATIVE_VORBIS_SETUP_OWNER_OK: return NATIVE_VORBIS_DECODER_OK;
    case NATIVE_VORBIS_SETUP_OWNER_INVALID: return NATIVE_VORBIS_DECODER_INVALID;
    case NATIVE_VORBIS_SETUP_OWNER_RANGE: return NATIVE_VORBIS_DECODER_RANGE;
    case NATIVE_VORBIS_SETUP_OWNER_TRUNCATED: return NATIVE_VORBIS_DECODER_TRUNCATED;
    case NATIVE_VORBIS_SETUP_OWNER_NO_MEMORY: return NATIVE_VORBIS_DECODER_NO_MEMORY;
    default: return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    }
}

static native_vorbis_decoder_status_t floor0_status(native_vorbis_floor0_route_t route) {
    switch (route) {
    case NATIVE_VORBIS_FLOOR0_BINARY64_CANDIDATE: return NATIVE_VORBIS_DECODER_OK;
    case NATIVE_VORBIS_FLOOR0_NEEDS_WIDER: return NATIVE_VORBIS_DECODER_NEEDS_WIDER;
    case NATIVE_VORBIS_FLOOR0_NEEDS_PRECISION: return NATIVE_VORBIS_DECODER_NEEDS_PRECISION;
    case NATIVE_VORBIS_FLOOR0_UNDEFINED_MAPPING: return NATIVE_VORBIS_DECODER_UNDEFINED_MAPPING;
    case NATIVE_VORBIS_FLOOR0_UNDEFINED_POLE: return NATIVE_VORBIS_DECODER_UNDEFINED_POLE;
    case NATIVE_VORBIS_FLOOR0_UNDEFINED_INDETERMINATE:
        return NATIVE_VORBIS_DECODER_UNDEFINED_INDETERMINATE;
    default: return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    }
}

// Count remains uint64 here so the same check covers both host and MCU size_t.
static bool object_bytes(uint64_t count, size_t unit, size_t *bytes) {
    if (!unit || count > SIZE_MAX / unit) return false;
    *bytes = (size_t)count * unit;
    return true;
}

static void *allocate_array(native_vorbis_decoder_t *decoder, uint64_t count,
    size_t unit, native_vorbis_decoder_status_t *status) {
    size_t bytes;
    if (!object_bytes(count, unit, &bytes)) {
        *status = NATIVE_VORBIS_DECODER_RANGE;
        return NULL;
    }
    void *allocation = bytes ? decoder->allocator.allocate(decoder->allocator.context, bytes) : NULL;
    *status = bytes && !allocation ? NATIVE_VORBIS_DECODER_NO_MEMORY : NATIVE_VORBIS_DECODER_OK;
    return allocation;
}

static void release(native_vorbis_decoder_t *decoder, void *allocation) {
    if (allocation) decoder->allocator.release(decoder->allocator.context, allocation);
}

// Old scratch stays reusable if allocation fails. Scratch contents do not need
// copying: no earlier frame borrow survives an attempted process operation.
static void *grow_array(native_vorbis_decoder_t *decoder, void *previous,
    size_t *capacity, uint64_t count, size_t unit, native_vorbis_decoder_status_t *status) {
    if (count <= *capacity) {
        *status = NATIVE_VORBIS_DECODER_OK;
        return previous;
    }
    void *replacement = allocate_array(decoder, count, unit, status);
    if (*status != NATIVE_VORBIS_DECODER_OK) return previous;
    release(decoder, previous);
    *capacity = (size_t)count;
    return replacement;
}

static void destroy(native_vorbis_decoder_t *decoder) {
    if (!decoder) return;
    native_vorbis_setup_allocator_t allocator = decoder->allocator;
    native_vorbis_setup_owner_clear(&decoder->setup_owner);
    if (decoder->work) {
        for (uint32_t channel = 0; channel < decoder->channels; ++channel)
            release(decoder, decoder->work[channel]);
    }
    for (unsigned i = 0; i < 2; ++i) {
        release(decoder, decoder->transforms[i].trig);
        release(decoder, decoder->transforms[i].bitrev);
    }
    release(decoder, decoder->frame.floors);
    release(decoder, decoder->frame.floor0);
    release(decoder, decoder->frame.floor1);
    release(decoder, decoder->frame.spectrum);
    release(decoder, decoder->frame.classifications);
    release(decoder, decoder->product);
    release(decoder, decoder->curve);
    release(decoder, decoder->map);
    release(decoder, decoder->factors);
    release(decoder, decoder->spectrum);
    release(decoder, decoder->blocks);
    release(decoder, decoder->capacities);
    release(decoder, decoder->work);
    release(decoder, decoder->history);
    release(decoder, decoder->exponents);
    release(decoder, decoder->short_coefficients);
    release(decoder, decoder->long_coefficients);
    allocator.release(allocator.context, decoder);
}

static native_vorbis_decoder_status_t stream_storage(native_vorbis_decoder_t *decoder) {
    const native_vorbis_setup_t *setup = native_vorbis_setup_owner_view(decoder->setup_owner);
    uint32_t short_size = setup->layout.identification.blocksize_0;
    decoder->long_size = setup->layout.identification.blocksize_1;
    decoder->channels = setup->layout.identification.channels;
    uint32_t long_size = decoder->long_size;
    native_vorbis_synthesis_requirements_t requirements;
    if (native_vorbis_synthesis_measure(short_size, long_size, decoder->channels, &requirements) !=
        NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    native_vorbis_decoder_status_t status;
#define ALLOCATE(field, count) do { \
    decoder->field = allocate_array(decoder, count, sizeof(*decoder->field), &status); \
    if (status != NATIVE_VORBIS_DECODER_OK) return status; \
} while (0)
    ALLOCATE(short_coefficients, short_size / 2);
    if (short_size != long_size) ALLOCATE(long_coefficients, long_size / 2);
    ALLOCATE(history, requirements.history_samples);
    ALLOCATE(exponents, requirements.exponent_count);
    ALLOCATE(work, decoder->channels);
    // Destruction is safe even if allocation of a later channel fails.
    for (uint32_t channel = 0; channel < decoder->channels; ++channel) decoder->work[channel] = NULL;
    ALLOCATE(blocks, decoder->channels);
    ALLOCATE(capacities, decoder->channels);
    ALLOCATE(spectrum, long_size / 2);
    ALLOCATE(curve, long_size / 2);
    ALLOCATE(map, long_size / 2);
    ALLOCATE(factors, long_size / 2);
    for (uint32_t channel = 0; channel < decoder->channels; ++channel) {
        decoder->work[channel] = allocate_array(decoder, (uint64_t)long_size + 8,
            sizeof(*decoder->work[channel]), &status);
        if (status != NATIVE_VORBIS_DECODER_OK) return status;
        // Transform results borrow work[channel]+8, with long_size remaining.
        decoder->capacities[channel] = long_size;
    }
#undef ALLOCATE
    if (native_vorbis_window_prepare(short_size, decoder->short_coefficients, short_size / 2,
        &decoder->short_plan) != NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    if (short_size == long_size) decoder->long_plan = decoder->short_plan;
    else if (native_vorbis_window_prepare(long_size, decoder->long_coefficients, long_size / 2,
        &decoder->long_plan) != NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    if (native_vorbis_synthesis_init(&decoder->short_plan, &decoder->long_plan, decoder->channels,
        decoder->history, (size_t)requirements.history_samples,
        decoder->exponents, requirements.exponent_count, &decoder->synthesis) != NATIVE_VORBIS_NUMERIC_OK)
        return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    return NATIVE_VORBIS_DECODER_OK;
}

native_vorbis_decoder_status_t native_vorbis_decoder_replace(
    native_vorbis_decoder_t **decoder,
    const uint8_t *identification, size_t identification_bytes, uint64_t identification_bits,
    const uint8_t *setup, size_t setup_bytes, uint64_t setup_bits,
    const native_vorbis_setup_allocator_t *allocator) {
    if (!decoder || !allocator || !allocator->allocate || !allocator->release)
        return NATIVE_VORBIS_DECODER_INVALID;
    native_vorbis_setup_allocator_t callbacks = *allocator;
    native_vorbis_setup_owner_t *owned_setup = NULL;
    native_vorbis_decoder_status_t status = setup_status(native_vorbis_setup_owner_replace(
        &owned_setup, identification, identification_bytes, identification_bits,
        setup, setup_bytes, setup_bits, &callbacks));
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    native_vorbis_decoder_t *candidate = callbacks.allocate(callbacks.context, sizeof(*candidate));
    if (!candidate) {
        native_vorbis_setup_owner_clear(&owned_setup);
        return NATIVE_VORBIS_DECODER_NO_MEMORY;
    }
    *candidate = (native_vorbis_decoder_t){.allocator = callbacks, .setup_owner = owned_setup};
    status = stream_storage(candidate);
    if (status != NATIVE_VORBIS_DECODER_OK) {
        destroy(candidate);
        return status;
    }
    native_vorbis_decoder_t *previous = *decoder;
    *decoder = candidate;
    destroy(previous);
    return NATIVE_VORBIS_DECODER_OK;
}

// All outputs here are private locals until public measure/process succeeds.
// This preview performs integer metadata work only: no allocation or DSP math.
static native_vorbis_decoder_status_t preflight(const native_vorbis_decoder_t *decoder,
    const native_vorbis_decoder_packet_t *input, native_vorbis_packet_t *packet,
    native_vorbis_frame_requirements_t *frame, native_vorbis_timing_event_t *event,
    native_vorbis_decoder_requirements_t *requirements) {
    if (!decoder || !input) return NATIVE_VORBIS_DECODER_INVALID;
    if (decoder->end_of_stream) return NATIVE_VORBIS_DECODER_END_OF_STREAM;
    native_vorbis_decoder_status_t status = parser_status(native_vorbis_packet_init(
        packet, input->data, input->bytes, input->bits, 0));
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    status = parser_status(native_vorbis_frame_measure(
        native_vorbis_setup_owner_view(decoder->setup_owner), packet, frame));
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    *event = (native_vorbis_timing_event_t){.blocksize = frame->prefix.blocksize,
        .granule_position = input->granule_position,
        .end_of_stream = input->end_of_stream, .discontinuity = input->discontinuity};
    native_vorbis_timing_t timing = decoder->synthesis.timing;
    native_vorbis_timing_result_t span;
    status = parser_status(native_vorbis_timing_push(&timing, event, &span));
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    // count<=4096 and channels<=255 are established by the public components.
    *requirements = (native_vorbis_decoder_requirements_t){.blocksize = event->blocksize,
        .channels = decoder->channels, .pcm_samples = (uint64_t)span.count * decoder->channels,
        .timing = span};
    return NATIVE_VORBIS_DECODER_OK;
}

native_vorbis_decoder_status_t native_vorbis_decoder_measure(
    const native_vorbis_decoder_t *decoder, const native_vorbis_decoder_packet_t *input,
    native_vorbis_decoder_requirements_t *requirements) {
    if (!requirements) return NATIVE_VORBIS_DECODER_INVALID;
    native_vorbis_packet_t packet;
    native_vorbis_frame_requirements_t frame;
    native_vorbis_timing_event_t event;
    native_vorbis_decoder_requirements_t needed;
    native_vorbis_decoder_status_t status = preflight(decoder, input, &packet, &frame, &event, &needed);
    if (status == NATIVE_VORBIS_DECODER_OK) *requirements = needed;
    return status;
}

static native_vorbis_decoder_status_t frame_storage(native_vorbis_decoder_t *decoder,
    const native_vorbis_frame_requirements_t *requirements) {
    native_vorbis_decoder_status_t status;
    // These are the proven conservative all-present bounds, not a claim about
    // actual per-packet RAM. No representation or stream format cap is added.
#define GROW(field, capacity, count) do { \
    decoder->frame.field = grow_array(decoder, decoder->frame.field, &decoder->frame.capacity, \
        count, sizeof(*decoder->frame.field), &status); \
    if (status != NATIVE_VORBIS_DECODER_OK) return status; \
} while (0)
    GROW(floors, floor_capacity, requirements->floor_count);
    GROW(floor0, floor0_capacity, requirements->floor0_values);
    GROW(floor1, floor1_capacity, requirements->floor1_values);
    GROW(spectrum, spectrum_capacity, requirements->residue_bound.limb_count);
    GROW(classifications, classification_capacity, requirements->residue_bound.classification_count);
#undef GROW
    return NATIVE_VORBIS_DECODER_OK;
}

static native_vorbis_decoder_status_t transform_prepare(native_vorbis_decoder_t *decoder,
    unsigned which, uint32_t blocksize) {
    decoder_transform_t *transform = decoder->transforms + which;
    if (transform->plan.blocksize) return transform->plan.blocksize == blocksize ?
        NATIVE_VORBIS_DECODER_OK : NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    native_vorbis_imdct_requirements_t needed;
    if (native_vorbis_imdct_measure(blocksize, &needed) != NATIVE_VORBIS_NUMERIC_OK)
        return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    native_vorbis_decoder_status_t status;
    double *trig = allocate_array(decoder, needed.trig_count, sizeof(*trig), &status);
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    int *bitrev = allocate_array(decoder, needed.bitrev_count, sizeof(*bitrev), &status);
    if (status != NATIVE_VORBIS_DECODER_OK) {
        release(decoder, trig);
        return status;
    }
    native_vorbis_imdct_plan_t plan;
    if (native_vorbis_imdct_prepare(blocksize, trig, (size_t)needed.trig_count,
        bitrev, (size_t)needed.bitrev_count, &plan) != NATIVE_VORBIS_NUMERIC_OK) {
        release(decoder, bitrev);
        release(decoder, trig);
        return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    }
    // A failed construction never publishes a partial cache or dangling plan.
    *transform = (decoder_transform_t){.plan = plan, .trig = trig, .bitrev = bitrev};
    return NATIVE_VORBIS_DECODER_OK;
}

native_vorbis_decoder_status_t native_vorbis_decoder_process(
    native_vorbis_decoder_t *decoder, const native_vorbis_decoder_packet_t *input,
    int16_t *output, size_t output_capacity, native_vorbis_decoder_result_t *result) {
    if (!result) return NATIVE_VORBIS_DECODER_INVALID;
    native_vorbis_packet_t packet;
    native_vorbis_frame_requirements_t frame_needed;
    native_vorbis_timing_event_t event;
    native_vorbis_decoder_requirements_t needed;
    native_vorbis_decoder_status_t status = preflight(decoder, input, &packet, &frame_needed, &event, &needed);
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    if (output_capacity > SIZE_MAX / sizeof(*output)) return NATIVE_VORBIS_DECODER_RANGE;
    if (output_capacity < needed.pcm_samples) return NATIVE_VORBIS_DECODER_OUTPUT_CAPACITY;
    if (needed.pcm_samples && !output) return NATIVE_VORBIS_DECODER_INVALID;
    // Nothing above this point allocates, grows scratch or performs DSP math.
    status = frame_storage(decoder, &frame_needed);
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    native_vorbis_packet_frame_t frame;
    status = parser_status(native_vorbis_frame_decode(native_vorbis_setup_owner_view(decoder->setup_owner),
        &packet, &decoder->frame, &frame));
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    uint32_t blocksize = frame.prefix.blocksize, bins = blocksize / 2;
    unsigned which = blocksize == decoder->long_size &&
        decoder->short_plan.blocksize != decoder->long_size;
    status = transform_prepare(decoder, which, blocksize);
    if (status != NATIVE_VORBIS_DECODER_OK) return status;
    native_vorbis_decoder_result_t completed = {.blocksize = blocksize, .channels = decoder->channels,
        .consumed_bits = packet.position, .end_of_packet = packet.end_of_packet};
    for (uint32_t channel = 0; channel < decoder->channels; ++channel) {
        native_vorbis_transform_block_t spectrum;
        if (frame.floors[channel].state.type == 0) {
            native_vorbis_floor0_spectrum_plan_t plan;
            if (native_vorbis_frame_floor0_prepare(&frame, channel, decoder->map, decoder->long_size / 2,
                decoder->factors, decoder->long_size / 2, &plan) != NATIVE_VORBIS_NUMERIC_OK)
                return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
            status = floor0_status(plan.route);
            if (status != NATIVE_VORBIS_DECODER_OK) return status;
            if (native_vorbis_frame_floor0_materialize(&plan, decoder->spectrum, bins, &spectrum) !=
                NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
            ++completed.floor0_channels;
        } else if (frame.floors[channel].state.type == 1) {
            native_vorbis_floor1_product_layout_t layout;
            if (native_vorbis_frame_floor1_measure(&frame, channel, decoder->curve, decoder->long_size / 2,
                &layout) != NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
            decoder->product = grow_array(decoder, decoder->product, &decoder->product_capacity,
                layout.limb_count, sizeof(*decoder->product), &status);
            if (status != NATIVE_VORBIS_DECODER_OK) return status;
            native_vorbis_floor1_product_t product;
            if (native_vorbis_frame_floor1_product(&frame, channel, decoder->curve, decoder->long_size / 2,
                layout.limb_count ? decoder->product : NULL, (size_t)layout.limb_count, &product) !=
                NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
            if (native_vorbis_spectrum_to_binary64(&product, (size_t)layout.limb_count,
                decoder->spectrum, bins, &spectrum) != NATIVE_VORBIS_NUMERIC_OK)
                return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
            ++completed.floor1_channels;
        } else return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
        if (native_vorbis_imdct_transform_binary64(&decoder->transforms[which].plan,
            &spectrum, bins, decoder->work[channel], (size_t)decoder->long_size + 8,
            decoder->blocks + channel) != NATIVE_VORBIS_NUMERIC_OK)
            return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    }
    // This is the only operation that can write output, history or position.
    // Its own all-channel preflight precedes publication. It has no callbacks.
    if (native_vorbis_synthesis_push(&decoder->synthesis, &event, decoder->blocks,
        decoder->capacities, decoder->channels, output, output_capacity, &completed.synthesis) !=
        NATIVE_VORBIS_NUMERIC_OK) return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    decoder->end_of_stream = input->end_of_stream;
    *result = completed;
    return NATIVE_VORBIS_DECODER_OK;
}

native_vorbis_decoder_status_t native_vorbis_decoder_info(
    const native_vorbis_decoder_t *decoder, native_vorbis_decoder_info_t *info) {
    if (!decoder || !info) return NATIVE_VORBIS_DECODER_INVALID;
    *info = (native_vorbis_decoder_info_t){
        .identification = native_vorbis_setup_owner_view(decoder->setup_owner)->layout.identification,
        .timing = decoder->synthesis.timing, .end_of_stream = decoder->end_of_stream};
    return NATIVE_VORBIS_DECODER_OK;
}

native_vorbis_decoder_status_t native_vorbis_decoder_reset(native_vorbis_decoder_t *decoder) {
    if (!decoder) return NATIVE_VORBIS_DECODER_INVALID;
    if (native_vorbis_synthesis_reset(&decoder->synthesis) != NATIVE_VORBIS_NUMERIC_OK)
        return NATIVE_VORBIS_DECODER_NUMERIC_FAILURE;
    decoder->end_of_stream = false;
    return NATIVE_VORBIS_DECODER_OK;
}

void native_vorbis_decoder_clear(native_vorbis_decoder_t **decoder) {
    if (!decoder) return;
    native_vorbis_decoder_t *previous = *decoder;
    *decoder = NULL;
    destroy(previous);
}
