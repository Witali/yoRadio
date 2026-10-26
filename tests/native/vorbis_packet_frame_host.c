/* Exact frame capture plus guarded capacity/refusal/retry controls. */
#include "native_vorbis_packet_frame.h"
#include "native_vorbis_setup_owner.h"
#include <assert.h>
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef NDEBUG
#error "Frame capture requires active assertions"
#endif
_Static_assert(SIZE_MAX >= UINT32_MAX, "The host capture needs at least 32-bit size_t");

typedef struct allocation allocation_t;
struct allocation {
    allocation_t *previous, *next;
    unsigned char *data, *before;
    size_t bytes;
    unsigned tag;
};

enum {
    TAG_OWNER = 1, TAG_INPUT, TAG_WORKSPACE, TAG_SNAPSHOT,
    PREFIX_BYTES = ((sizeof(allocation_t) + sizeof(uint64_t) +
        _Alignof(max_align_t) - 1) / _Alignof(max_align_t)) * _Alignof(max_align_t)
};

typedef struct { unsigned char *data; size_t bytes; uint64_t bits; } packet_input_t;
typedef struct { FILE *file; uint64_t hash; } emitter_t;

static allocation_t *allocations;
static size_t live_allocations, live_bytes;
static uint64_t checks, refusal_total;
static unsigned owner_cookie;
static const uint64_t CANARY = UINT64_C(0xc91b4e7da630258f);

static void require(bool condition) {
    assert(condition);
    if (!condition) abort();
}

static void check(bool condition) {
    require(condition);
    require(checks != UINT64_MAX);
    ++checks;
}

static void guards(const allocation_t *allocation) {
    uint64_t before, after;
    memcpy(&before, allocation->data - sizeof(before), sizeof(before));
    memcpy(&after, allocation->data + allocation->bytes, sizeof(after));
    check(before == CANARY && after == CANARY);
}

static allocation_t *find_allocation(const void *data) {
    for (allocation_t *at = allocations; at; at = at->next)
        if (at->data == data) return at;
    return NULL;
}

static void *tracked_allocate(size_t bytes, unsigned tag) {
    check(bytes <= SIZE_MAX - PREFIX_BYTES - sizeof(uint64_t));
    unsigned char *base = malloc(PREFIX_BYTES + bytes + sizeof(uint64_t));
    check(base != NULL);
    allocation_t *allocation = (void *)base;
    unsigned char *data = base + PREFIX_BYTES;
    check((uintptr_t)data % _Alignof(max_align_t) == 0);
    *allocation = (allocation_t){NULL, allocations, data, NULL, bytes, tag};
    if (allocations) allocations->previous = allocation;
    allocations = allocation;
    memcpy(data - sizeof(CANARY), &CANARY, sizeof(CANARY));
    memcpy(data + bytes, &CANARY, sizeof(CANARY));
    if (bytes) memset(data, 0xa5, bytes);
    check(live_bytes <= SIZE_MAX - bytes && live_allocations < SIZE_MAX);
    live_bytes += bytes;
    ++live_allocations;
    return data;
}

static void release_one(allocation_t *allocation) {
    if (!allocation) abort();
    check(allocation != NULL && allocation->before == NULL);
    guards(allocation);
    if (allocation->previous) allocation->previous->next = allocation->next;
    else allocations = allocation->next;
    if (allocation->next) allocation->next->previous = allocation->previous;
    check(live_allocations && live_bytes >= allocation->bytes);
    --live_allocations;
    live_bytes -= allocation->bytes;
    if (allocation->bytes) memset(allocation->data, 0xdd, allocation->bytes);
    free(allocation);
}

static void tracked_free(void *data) {
    if (!data) return;
    allocation_t *allocation = find_allocation(data);
    if (!allocation) abort();
    check(allocation != NULL);
    guards(allocation);
    allocation_t *snapshot = NULL;
    if (allocation->before) {
        snapshot = find_allocation(allocation->before);
        if (!snapshot || snapshot == allocation) abort();
        check(allocation->tag != TAG_SNAPSHOT && allocation->bytes != 0);
        check(snapshot != allocation && snapshot->tag == TAG_SNAPSHOT);
        check(snapshot->before == NULL && snapshot->bytes == allocation->bytes);
        check(snapshot->data == allocation->before);
        guards(snapshot);
        check(memcmp(snapshot->data, allocation->data, allocation->bytes) == 0);
    }
    allocation->before = NULL;
    release_one(allocation);
    if (snapshot) release_one(snapshot);
}

static void freeze(void *data) {
    allocation_t *allocation = find_allocation(data);
    if (!allocation) abort();
    check(allocation != NULL && allocation->before == NULL);
    check(allocation->tag != TAG_SNAPSHOT);
    if (allocation->bytes) {
        allocation->before = tracked_allocate(allocation->bytes, TAG_SNAPSHOT);
        memcpy(allocation->before, allocation->data, allocation->bytes);
    }
}

static void validate_allocations(void) {
    size_t count = 0, bytes = 0;
    for (allocation_t *at = allocations; at; at = at->next) {
        guards(at);
        check(at->tag != TAG_SNAPSHOT || at->before == NULL);
        if (at->before) check(memcmp(at->before, at->data, at->bytes) == 0);
        check(bytes <= SIZE_MAX - at->bytes);
        bytes += at->bytes;
        ++count;
    }
    check(count == live_allocations && bytes == live_bytes);
}

static void *owner_allocate(void *context, size_t bytes) {
    check(context == &owner_cookie && bytes != 0);
    return tracked_allocate(bytes, TAG_OWNER);
}

static void owner_release(void *context, void *data) {
    check(context == &owner_cookie && data != NULL);
    allocation_t *allocation = find_allocation(data);
    check(allocation != NULL && allocation->tag == TAG_OWNER);
    tracked_free(data);
}

static uint64_t read_integer(FILE *input, unsigned width) {
    require(width <= 8);
    uint64_t result = 0;
    for (unsigned byte = 0; byte < width; ++byte) {
        int value = fgetc(input);
        require(value != EOF);
        result |= (uint64_t)(unsigned)value << (8 * byte);
    }
    return result;
}

static void emit_integer(emitter_t *output, uint64_t value, unsigned width) {
    require(width <= 8);
    unsigned char bytes[8];
    for (unsigned byte = 0; byte < width; ++byte) {
        bytes[byte] = (unsigned char)(value >> (8 * byte));
        output->hash ^= bytes[byte];
        output->hash *= UINT64_C(1099511628211);
    }
    if (output->file) require(fwrite(bytes, 1, width, output->file) == width);
}

static void prefix_put(emitter_t *out, const native_vorbis_audio_prefix_t *prefix) {
    emit_integer(out, prefix->mode, 4); emit_integer(out, prefix->blockflag, 4);
    emit_integer(out, prefix->previous_window, 4); emit_integer(out, prefix->next_window, 4);
    emit_integer(out, prefix->mapping, 4); emit_integer(out, prefix->blocksize, 4);
}

static void layout_put(emitter_t *out, const native_vorbis_residue_layout_t *layout) {
    emit_integer(out, layout->mapping, 4); emit_integer(out, layout->bins, 4);
    emit_integer(out, layout->channels, 4); emit_integer(out, layout->limbs, 4);
    emit_integer(out, layout->magnitude_bits, 4); emit_integer(out, (uint32_t)layout->exponent, 4);
    emit_integer(out, layout->sample_count, 8); emit_integer(out, layout->limb_count, 8);
    emit_integer(out, layout->classification_count, 8);
}

static void requirements_put(emitter_t *out, const native_vorbis_frame_requirements_t *requirements) {
    prefix_put(out, &requirements->prefix);
    emit_integer(out, requirements->floor_count, 4);
    emit_integer(out, requirements->floor0_values, 8);
    emit_integer(out, requirements->floor1_values, 8);
    layout_put(out, &requirements->residue_bound);
}

static void frame_put(emitter_t *out, const native_vorbis_packet_frame_t *frame) {
    prefix_put(out, &frame->prefix);
    emit_integer(out, frame->floor_count, 4);
    emit_integer(out, frame->floor0_count, 8); emit_integer(out, frame->floor1_count, 8);
    emit_integer(out, frame->implicit_zero, 4); emit_integer(out, frame->floor_eop, 4);
    layout_put(out, &frame->spectrum_layout);
    emit_integer(out, frame->residue.classwords, 8); emit_integer(out, frame->residue.vectors, 8);
    emit_integer(out, frame->residue.values, 8); emit_integer(out, frame->residue.stopped_on_eop, 4);
    for (uint32_t channel = 0; channel < frame->floor_count; ++channel) {
        const native_vorbis_frame_floor_t *floor = &frame->floors[channel];
        const native_vorbis_floor_packet_t *state = &floor->state;
        emit_integer(out, state->floor_index, 4); emit_integer(out, state->type, 4);
        emit_integer(out, state->present, 4); emit_integer(out, state->value_count, 4);
        emit_integer(out, state->selected_book, 4); emit_integer(out, state->amplitude.raw_amplitude, 8);
        emit_integer(out, state->amplitude.amplitude_bits, 4);
        emit_integer(out, state->amplitude.amplitude_offset, 4);
        emit_integer(out, floor->value_offset, 8);
    }
    for (size_t i = 0; i < frame->floor0_count; ++i) {
        emit_integer(out, frame->floor0[i].minimum_bits, 4);
        emit_integer(out, frame->floor0[i].delta_bits, 4);
        emit_integer(out, frame->floor0[i].minimum_multiplier, 4);
        emit_integer(out, frame->floor0[i].delta_multiplier, 4);
    }
    for (size_t i = 0; i < frame->floor1_count; ++i) emit_integer(out, frame->floor1[i], 4);
    for (uint64_t i = 0; i < frame->spectrum_layout.limb_count; ++i)
        emit_integer(out, frame->spectrum[(size_t)i], 4);
}

static uint64_t frame_hash(const native_vorbis_packet_frame_t *frame, const native_vorbis_packet_t *packet) {
    emitter_t out = {NULL, UINT64_C(14695981039346656037)};
    frame_put(&out, frame);
    emit_integer(&out, packet->position, 8);
    emit_integer(&out, packet->end_of_packet, 4);
    return out.hash;
}

static packet_input_t read_packet(FILE *input) {
    size_t bytes = (size_t)read_integer(input, 4);
    packet_input_t packet = {tracked_allocate(bytes, TAG_INPUT), bytes, 0};
    require(fread(packet.data, 1, packet.bytes, input) == packet.bytes);
    packet.bits = read_integer(input, 8);
    check(packet.bits / 8 <= packet.bytes &&
        (packet.bits / 8 < packet.bytes || packet.bits % 8 == 0));
    freeze(packet.data);
    return packet;
}

static void *workspace_array(uint64_t count, size_t unit) {
    check(unit != 0 && count <= SIZE_MAX / unit);
    return count ? tracked_allocate((size_t)count * unit, TAG_WORKSPACE) : NULL;
}

static bool packet_same(const native_vorbis_packet_t *a, const native_vorbis_packet_t *b) {
    return a->data == b->data && a->bytes == b->bytes && a->bits == b->bits &&
        a->position == b->position && a->end_of_packet == b->end_of_packet;
}

static void validate_frame(const native_vorbis_setup_t *setup,
    const native_vorbis_frame_workspace_t *workspace, const native_vorbis_packet_frame_t *frame) {
    check(frame->setup == setup && frame->floor_count == setup->layout.identification.channels);
    check(frame->floors == workspace->floors && frame->floor_count <= workspace->floor_capacity);
    check(frame->floor0_count <= workspace->floor0_capacity && frame->floor1_count <= workspace->floor1_capacity);
    check(frame->floor0 == (frame->floor0_count ? workspace->floor0 : NULL));
    check(frame->floor1 == (frame->floor1_count ? workspace->floor1 : NULL));
    check(frame->spectrum_layout.limb_count <= workspace->spectrum_capacity);
    check(frame->spectrum_layout.classification_count <= workspace->classification_capacity);
    check(frame->spectrum == (frame->spectrum_layout.limb_count ? workspace->spectrum : NULL));
    check(frame->implicit_zero == (frame->spectrum_layout.limb_count == 0));
    bool any_present = false;
    for (uint32_t i = 0; i < frame->floor_count; ++i) {
        const native_vorbis_frame_floor_t *floor = &frame->floors[i];
        check(floor->state.type <= 1 && floor->state.present <= 1);
        size_t count = floor->state.type == 0 ? frame->floor0_count : frame->floor1_count;
        check(floor->value_offset <= count && floor->state.value_count <= count - floor->value_offset);
        if (!floor->state.present) check(floor->state.value_count == 0);
        any_present = any_present || floor->state.present != 0;
        if (frame->floor_eop) check(!floor->state.present && !floor->state.value_count && !floor->value_offset);
    }
    if (!any_present) {
        check(frame->implicit_zero && !frame->floor0_count && !frame->floor1_count);
        check(!frame->residue.classwords && !frame->residue.vectors && !frame->residue.values && !frame->residue.stopped_on_eop);
    }
    validate_allocations();
}

static void expect_failure(const native_vorbis_setup_t *setup, const native_vorbis_packet_t *initial,
    const native_vorbis_frame_workspace_t *workspace, native_vorbis_numeric_status_t expected) {
    native_vorbis_packet_t packet = *initial;
    native_vorbis_packet_frame_t frame;
    unsigned char before[sizeof(frame)];
    memset(&frame, 0xa5, sizeof(frame)); memcpy(before, &frame, sizeof(frame));
    check(native_vorbis_frame_decode(setup, &packet, workspace, &frame) == expected);
    native_vorbis_packet_t wanted = *initial;
    if (expected == NATIVE_VORBIS_NUMERIC_TRUNCATED) wanted.end_of_packet = true;
    check(packet_same(&packet, &wanted) && memcmp(&frame, before, sizeof(frame)) == 0);
    validate_allocations();
}

static void retry(const native_vorbis_setup_t *setup, const native_vorbis_packet_t *initial,
    const native_vorbis_frame_workspace_t *workspace, uint64_t wanted_hash) {
    native_vorbis_packet_t packet = *initial;
    native_vorbis_packet_frame_t frame;
    check(native_vorbis_frame_decode(setup, &packet, workspace, &frame) == NATIVE_VORBIS_NUMERIC_OK);
    validate_frame(setup, workspace, &frame);
    check(frame_hash(&frame, &packet) == wanted_hash);
}

static void invalid_controls(const native_vorbis_setup_t *setup,
    const native_vorbis_packet_t *initial, const native_vorbis_frame_workspace_t *workspace,
    bool valid_prefix) {
    native_vorbis_packet_t packet = *initial;
    native_vorbis_packet_frame_t frame;
    native_vorbis_frame_requirements_t requirements;
    unsigned char frame_before[sizeof(frame)], requirements_before[sizeof(requirements)];
    memset(&frame, 0xa5, sizeof(frame)); memcpy(frame_before, &frame, sizeof(frame));
    memset(&requirements, 0xa5, sizeof(requirements)); memcpy(requirements_before, &requirements, sizeof(requirements));
    check(native_vorbis_frame_measure(NULL, &packet, &requirements) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_measure(setup, NULL, &requirements) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_measure(setup, &packet, NULL) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(memcmp(&requirements, requirements_before, sizeof(requirements)) == 0);
    check(native_vorbis_frame_decode(NULL, &packet, workspace, &frame) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_decode(setup, NULL, workspace, &frame) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_decode(setup, &packet, NULL, &frame) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_decode(setup, &packet, workspace, NULL) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(packet_same(&packet, initial) && memcmp(&frame, frame_before, sizeof(frame)) == 0);
    if (valid_prefix) {
        native_vorbis_frame_workspace_t altered = *workspace;
        altered.floor_capacity = SIZE_MAX / sizeof(*altered.floors) + 1;
        expect_failure(setup, initial, &altered, NATIVE_VORBIS_NUMERIC_RANGE);
        altered = *workspace;
        altered.floor0_capacity = SIZE_MAX / sizeof(*altered.floor0) + 1;
        expect_failure(setup, initial, &altered, NATIVE_VORBIS_NUMERIC_RANGE);
        altered = *workspace;
        altered.floor1_capacity = SIZE_MAX / sizeof(*altered.floor1) + 1;
        expect_failure(setup, initial, &altered, NATIVE_VORBIS_NUMERIC_RANGE);
        altered = *workspace;
        altered.spectrum_capacity = SIZE_MAX / sizeof(*altered.spectrum) + 1;
        expect_failure(setup, initial, &altered, NATIVE_VORBIS_NUMERIC_RANGE);
    }
    validate_allocations();
}

static uint32_t capacity_controls(const native_vorbis_setup_t *setup,
    const native_vorbis_packet_t *initial, const native_vorbis_frame_workspace_t *workspace,
    const native_vorbis_packet_frame_t *captured, uint64_t wanted_hash) {
    size_t needs[5] = {captured->floor_count, captured->floor0_count, captured->floor1_count,
        (size_t)captured->spectrum_layout.limb_count, (size_t)captured->spectrum_layout.classification_count};
    bool floor_eop = captured->floor_eop;
    uint32_t refusals = 0;
    for (unsigned pool = 0; pool < 5; ++pool) {
        if (!needs[pool]) continue;
        native_vorbis_frame_workspace_t altered = *workspace;
        switch (pool) {
        case 0: altered.floor_capacity = needs[pool] - 1; break;
        case 1: altered.floor0_capacity = needs[pool] - 1; break;
        case 2: altered.floor1_capacity = needs[pool] - 1; break;
        case 3: altered.spectrum_capacity = needs[pool] - 1; break;
        default: altered.classification_capacity = needs[pool] - 1; break;
        }
        expect_failure(setup, initial, &altered, NATIVE_VORBIS_NUMERIC_CAPACITY);
        ++refusals;
        retry(setup, initial, workspace, wanted_hash);
    }
    native_vorbis_frame_workspace_t exact = *workspace;
    exact.floor_capacity = needs[0];
    if (!floor_eop) {
        exact.floor0_capacity = needs[1]; exact.floor0 = needs[1] ? workspace->floor0 : NULL;
        exact.floor1_capacity = needs[2]; exact.floor1 = needs[2] ? workspace->floor1 : NULL;
    }
    exact.spectrum_capacity = needs[3]; exact.spectrum = needs[3] ? workspace->spectrum : NULL;
    exact.classification_capacity = needs[4]; exact.classifications = needs[4] ? workspace->classifications : NULL;
    retry(setup, initial, &exact, wanted_hash);
    return refusals;
}

static void run_case(FILE *input, emitter_t *out, uint32_t index) {
    uint64_t starting_checks = checks;
    check(!allocations && live_allocations == 0 && live_bytes == 0);
    uint32_t name_bytes = (uint32_t)read_integer(input, 4);
    check(name_bytes != 0);
    for (uint32_t i = 0; i < name_bytes; ++i) {
        int c = (int)read_integer(input, 1);
        check((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
            (c >= '0' && c <= '9') || c == '-' || c == '_');
    }
    packet_input_t info = read_packet(input), setup_input = read_packet(input), payload = read_packet(input);
    uint64_t start = read_integer(input, 8), initial_eop = read_integer(input, 4);
    check(initial_eop <= 1);
    native_vorbis_setup_allocator_t allocator = {&owner_cookie, owner_allocate, owner_release};
    native_vorbis_setup_owner_t *owner = NULL;
    check(native_vorbis_setup_owner_replace(&owner, info.data, info.bytes, info.bits,
        setup_input.data, setup_input.bytes, setup_input.bits, &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
    const native_vorbis_setup_t *setup = native_vorbis_setup_owner_view(owner);
    check(setup != NULL);
    for (allocation_t *at = allocations; at; at = at->next)
        if (at->tag == TAG_OWNER) freeze(at->data);
    native_vorbis_packet_t initial;
    check(native_vorbis_packet_init(&initial, payload.data, payload.bytes, payload.bits, start) == NATIVE_VORBIS_NUMERIC_OK);
    initial.end_of_packet = initial_eop != 0;
    native_vorbis_frame_requirements_t requirements;
    unsigned char requirements_before[sizeof(requirements)];
    memset(&requirements, 0xa5, sizeof(requirements));
    memcpy(requirements_before, &requirements, sizeof(requirements));
    native_vorbis_packet_t measured_packet = initial;
    native_vorbis_numeric_status_t measured = native_vorbis_frame_measure(setup, &measured_packet, &requirements);
    check(packet_same(&measured_packet, &initial));
    if (measured != NATIVE_VORBIS_NUMERIC_OK)
        check(memcmp(&requirements, requirements_before, sizeof(requirements)) == 0);
    emit_integer(out, index, 4); emit_integer(out, (uint32_t)(int32_t)measured, 4);
    native_vorbis_frame_workspace_t workspace = {0};
    if (measured == NATIVE_VORBIS_NUMERIC_OK) {
        requirements_put(out, &requirements);
        workspace.floors = workspace_array(requirements.floor_count, sizeof(*workspace.floors));
        workspace.floor_capacity = requirements.floor_count;
        workspace.floor0 = workspace_array(requirements.floor0_values, sizeof(*workspace.floor0));
        workspace.floor0_capacity = (size_t)requirements.floor0_values;
        workspace.floor1 = workspace_array(requirements.floor1_values, sizeof(*workspace.floor1));
        workspace.floor1_capacity = (size_t)requirements.floor1_values;
        workspace.spectrum = workspace_array(requirements.residue_bound.limb_count, sizeof(*workspace.spectrum));
        workspace.spectrum_capacity = (size_t)requirements.residue_bound.limb_count;
        workspace.classifications = workspace_array(requirements.residue_bound.classification_count, sizeof(*workspace.classifications));
        workspace.classification_capacity = (size_t)requirements.residue_bound.classification_count;
    }
    native_vorbis_packet_frame_t frame;
    unsigned char frame_before[sizeof(frame)];
    memset(&frame, 0xa5, sizeof(frame)); memcpy(frame_before, &frame, sizeof(frame));
    native_vorbis_packet_t packet = initial;
    native_vorbis_numeric_status_t status = native_vorbis_frame_decode(setup, &packet, &workspace, &frame);
    emit_integer(out, (uint32_t)(int32_t)status, 4);
    uint64_t position = packet.position;
    bool eop = packet.end_of_packet;
    uint32_t refusals = 0;
    if (status == NATIVE_VORBIS_NUMERIC_OK) {
        validate_frame(setup, &workspace, &frame);
        frame_put(out, &frame);
        uint64_t wanted_hash = frame_hash(&frame, &packet);
        refusals = capacity_controls(setup, &initial, &workspace, &frame, wanted_hash);
    } else {
        native_vorbis_packet_t wanted = initial;
        if (status == NATIVE_VORBIS_NUMERIC_TRUNCATED) wanted.end_of_packet = true;
        check(packet_same(&packet, &wanted) && memcmp(&frame, frame_before, sizeof(frame)) == 0);
    }
    invalid_controls(setup, &initial, &workspace, measured == NATIVE_VORBIS_NUMERIC_OK);
    validate_allocations();
    native_vorbis_setup_owner_clear(&owner);
    check(owner == NULL);
    tracked_free(workspace.classifications); tracked_free(workspace.spectrum);
    tracked_free(workspace.floor1); tracked_free(workspace.floor0); tracked_free(workspace.floors);
    tracked_free(payload.data); tracked_free(setup_input.data); tracked_free(info.data);
    check(!allocations && live_allocations == 0 && live_bytes == 0);
    refusal_total += refusals;
    emit_integer(out, position, 8); emit_integer(out, eop, 4); emit_integer(out, 7, 4);
    emit_integer(out, refusals, 4); emit_integer(out, checks - starting_checks, 8);
}

int main(int argc, char **argv) {
    require(argc == 3);
    FILE *input = fopen(argv[1], "rb"), *output = fopen(argv[2], "wb");
    require(input != NULL && output != NULL);
    unsigned char magic[8];
    require(fread(magic, 1, sizeof(magic), input) == sizeof(magic));
    require(memcmp(magic, "VFRAME01", sizeof(magic)) == 0);
    require(fwrite("VFOUT001", 1, sizeof(magic), output) == sizeof(magic));
    uint32_t cases = (uint32_t)read_integer(input, 4);
    require(cases != 0);
    emitter_t emitter = {output, UINT64_C(14695981039346656037)};
    emit_integer(&emitter, cases, 4);
    for (uint32_t i = 0; i < cases; ++i) run_case(input, &emitter, i);
    require(fgetc(input) == EOF && !ferror(input));
    require(fclose(input) == 0);
    require(fclose(output) == 0);
    require(!allocations && live_allocations == 0 && live_bytes == 0);
    printf("FRAME_CAPTURE cases=%" PRIu32 " pool_refusals=%" PRIu64 " checks=%" PRIu64
        " live=0 bytes=0\n", cases, refusal_total, checks);
    return 0;
}
