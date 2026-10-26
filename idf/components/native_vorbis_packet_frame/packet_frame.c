// Compose the existing exact packet stages without floating table expansion.
#include "native_vorbis_packet_frame.h"
#include <string.h>

enum { MAX_CHANNELS = 255 };

static native_vorbis_numeric_status_t prefix_mapping(
    const native_vorbis_setup_t *setup, native_vorbis_packet_t *packet,
    native_vorbis_audio_prefix_t *prefix, native_vorbis_mapping_setup_t *mapping) {
    native_vorbis_numeric_status_t status = native_vorbis_audio_prefix(setup, packet, prefix);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_setup_mapping(setup, prefix->mapping, mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    return mapping->channels && mapping->channels <= MAX_CHANNELS ?
        NATIVE_VORBIS_NUMERIC_OK : NATIVE_VORBIS_NUMERIC_INVALID;
}

static native_vorbis_numeric_status_t channel_floor(
    const native_vorbis_setup_t *setup, const native_vorbis_mapping_setup_t *mapping,
    uint32_t channel, native_vorbis_frame_floor_t *record, uint32_t *count) {
    uint32_t submap = mapping->mux[channel];
    if (submap >= mapping->submap_count) return NATIVE_VORBIS_NUMERIC_INVALID;
    uint32_t index = mapping->submaps[3 * submap + 1], type;
    native_vorbis_numeric_status_t status = native_vorbis_setup_floor_type(setup, index, &type);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    native_vorbis_frame_floor_t result = {.state = {
        .floor_index = index, .type = type, .selected_book = UINT32_MAX}};
    if (type == 0) {
        native_vorbis_floor0_setup_t floor;
        status = native_vorbis_setup_floor0(setup, index, &floor);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        result.state.amplitude.amplitude_bits = floor.amplitude_bits;
        result.state.amplitude.amplitude_offset = floor.amplitude_offset;
        *count = floor.order;
    } else if (type == 1) {
        native_vorbis_floor1_setup_t floor;
        status = native_vorbis_setup_floor1(setup, index, &floor);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        *count = floor.post_count;
    } else return NATIVE_VORBIS_NUMERIC_INVALID;
    *record = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

native_vorbis_numeric_status_t native_vorbis_frame_measure(
    const native_vorbis_setup_t *setup, const native_vorbis_packet_t *packet,
    native_vorbis_frame_requirements_t *requirements) {
    if (!packet || !requirements) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t next = *packet;
    native_vorbis_mapping_setup_t mapping;
    native_vorbis_frame_requirements_t result = {0};
    native_vorbis_numeric_status_t status = prefix_mapping(setup, &next, &result.prefix, &mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    result.floor_count = mapping.channels;
    for (uint32_t channel = 0; channel < mapping.channels; ++channel) {
        native_vorbis_frame_floor_t record;
        uint32_t count;
        status = channel_floor(setup, &mapping, channel, &record, &count);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        if (record.state.type == 0) result.floor0_values += count;
        else result.floor1_values += count;
    }
    uint8_t present[MAX_CHANNELS];
    memset(present, 1, sizeof(present));
    status = native_vorbis_residue_measure(setup, result.prefix.mapping,
        result.prefix.blocksize / 2, present, mapping.channels, &result.residue_bound);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    *requirements = result;
    return NATIVE_VORBIS_NUMERIC_OK;
}

static void publish_zero(native_vorbis_packet_t *packet, const native_vorbis_packet_t *next,
    const native_vorbis_frame_workspace_t *workspace, native_vorbis_packet_frame_t *frame,
    native_vorbis_packet_frame_t *result, bool floor_eop) {
    for (uint32_t channel = 0; channel < frame->floor_count; ++channel) {
        workspace->floors[channel].state.present = 0;
        workspace->floors[channel].state.value_count = 0;
        workspace->floors[channel].value_offset = 0;
    }
    frame->spectrum_layout = (native_vorbis_residue_layout_t){
        .mapping = frame->prefix.mapping, .bins = frame->prefix.blocksize / 2,
        .channels = frame->floor_count,
        .sample_count = (uint64_t)frame->floor_count * (frame->prefix.blocksize / 2)};
    frame->implicit_zero = true;
    frame->floor_eop = floor_eop;
    *packet = *next;
    *result = *frame;
}

native_vorbis_numeric_status_t native_vorbis_frame_decode(
    const native_vorbis_setup_t *setup, native_vorbis_packet_t *packet,
    const native_vorbis_frame_workspace_t *workspace,
    native_vorbis_packet_frame_t *result) {
    if (!packet || !workspace || !result) return NATIVE_VORBIS_NUMERIC_INVALID;
    native_vorbis_packet_t next = *packet;
    native_vorbis_packet_frame_t frame = {.setup = setup};
    native_vorbis_mapping_setup_t mapping;
    native_vorbis_numeric_status_t status = prefix_mapping(setup, &next, &frame.prefix, &mapping);
    if (status != NATIVE_VORBIS_NUMERIC_OK) {
        if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) packet->end_of_packet = true;
        return status;
    }
    if (workspace->floor_capacity > SIZE_MAX / sizeof(*workspace->floors) ||
        workspace->floor0_capacity > SIZE_MAX / sizeof(*workspace->floor0) ||
        workspace->floor1_capacity > SIZE_MAX / sizeof(*workspace->floor1) ||
        workspace->spectrum_capacity > SIZE_MAX / sizeof(*workspace->spectrum))
        return NATIVE_VORBIS_NUMERIC_RANGE;
    if (workspace->floor_capacity < mapping.channels) return NATIVE_VORBIS_NUMERIC_CAPACITY;
    if (!workspace->floors) return NATIVE_VORBIS_NUMERIC_INVALID;
    frame.floor_count = mapping.channels;
    frame.floors = workspace->floors;
    for (uint32_t channel = 0; channel < mapping.channels; ++channel) {
        uint32_t count;
        status = channel_floor(setup, &mapping, channel, &workspace->floors[channel], &count);
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    }
    uint8_t present[MAX_CHANNELS];
    size_t count0 = 0, count1 = 0;
    bool any_present = false;
    for (uint32_t channel = 0; channel < mapping.channels; ++channel) {
        native_vorbis_frame_floor_t *floor = &workspace->floors[channel];
        if (floor->state.type == 0) {
            floor->value_offset = count0;
            status = native_vorbis_floor0_packet(setup, floor->state.floor_index, &next,
                workspace->floor0 ? workspace->floor0 + count0 : NULL,
                workspace->floor0_capacity - count0, &floor->state);
            if (status == NATIVE_VORBIS_NUMERIC_OK) count0 += floor->state.value_count;
        } else {
            floor->value_offset = count1;
            status = native_vorbis_floor1_packet(setup, floor->state.floor_index, &next,
                workspace->floor1 ? workspace->floor1 + count1 : NULL,
                workspace->floor1_capacity - count1, &floor->state);
            if (status == NATIVE_VORBIS_NUMERIC_OK) count1 += floor->state.value_count;
        }
        if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
        if (next.end_of_packet) {
            publish_zero(packet, &next, workspace, &frame, result, true);
            return NATIVE_VORBIS_NUMERIC_OK;
        }
        present[channel] = (uint8_t)floor->state.present;
        any_present = any_present || floor->state.present != 0;
    }
    if (!any_present) {
        publish_zero(packet, &next, workspace, &frame, result, false);
        return NATIVE_VORBIS_NUMERIC_OK;
    }
    status = native_vorbis_residue_measure(setup, frame.prefix.mapping, frame.prefix.blocksize / 2,
        present, mapping.channels, &frame.spectrum_layout);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_residue_packet(setup, &frame.spectrum_layout, present, mapping.channels,
        &next, workspace->classifications, workspace->classification_capacity,
        workspace->spectrum, workspace->spectrum_capacity, &frame.residue);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    status = native_vorbis_residue_inverse_coupling(setup, &frame.spectrum_layout,
        workspace->spectrum, workspace->spectrum_capacity);
    if (status != NATIVE_VORBIS_NUMERIC_OK) return status;
    frame.floor0_count = count0;
    frame.floor1_count = count1;
    frame.floor0 = count0 ? workspace->floor0 : NULL;
    frame.floor1 = count1 ? workspace->floor1 : NULL;
    frame.spectrum = frame.spectrum_layout.limb_count ? workspace->spectrum : NULL;
    frame.implicit_zero = frame.spectrum_layout.limbs == 0;
    *packet = next;
    *result = frame;
    return NATIVE_VORBIS_NUMERIC_OK;
}
