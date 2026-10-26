/* Reuse the unchanged guarded setup/packet fixture; its main is not executed. */
#define main native_packet_frame_capture_main
#include "vorbis_packet_frame_host.c"
#undef main
#include "native_vorbis_floor1_product.h"

static void product_layout_put(emitter_t *out,
    const native_vorbis_floor1_product_layout_t *layout) {
    emit_integer(out, layout->bins, 4);
    emit_integer(out, layout->limbs, 4);
    emit_integer(out, layout->magnitude_bits, 4);
    emit_integer(out, (uint32_t)layout->exponent, 4);
    emit_integer(out, layout->limb_count, 8);
}

static void product_put(emitter_t *out, const native_vorbis_floor1_product_t *product,
    const uint8_t *curve) {
    product_layout_put(out, &product->layout);
    uint32_t count = product->layout.limbs ? product->layout.bins : 0;
    emit_integer(out, count, 4);
    for (uint32_t bin = 0; bin < count; ++bin) emit_integer(out, curve[bin], 1);
    for (uint64_t i = 0; i < product->layout.limb_count; ++i)
        emit_integer(out, product->samples[i], 4);
}

static uint64_t product_hash(const native_vorbis_floor1_product_t *product,
    const uint8_t *curve) {
    emitter_t sink = {NULL, UINT64_C(14695981039346656037)};
    product_put(&sink, product, curve);
    return sink.hash;
}

static void product_failure(const native_vorbis_packet_frame_t *frame, uint32_t channel,
    uint8_t *curve, size_t curve_capacity, uint32_t *output, size_t capacity,
    uint32_t *expected, size_t expected_count, native_vorbis_numeric_status_t wanted) {
    native_vorbis_floor1_product_t result;
    unsigned char before[sizeof(result)];
    memset(&result, 0xa5, sizeof(result)); memcpy(before, &result, sizeof(result));
    check(native_vorbis_frame_floor1_product(frame, channel, curve, curve_capacity,
        output, capacity, &result) == wanted);
    check(memcmp(before, &result, sizeof(result)) == 0);
    if (output) check(memcmp(output, expected, expected_count * sizeof(*output)) == 0);
    ++refusal_total;
}

static uint32_t product_channel(const native_vorbis_packet_frame_t *frame,
    uint32_t channel, emitter_t *out) {
    uint64_t before_refusals = refusal_total;
    size_t bins = frame->spectrum_layout.bins;
    uint8_t *curve = workspace_array(bins, 1);
    native_vorbis_floor1_product_layout_t layout;
    unsigned char layout_before[sizeof(layout)];
    memset(&layout, 0xa5, sizeof(layout)); memcpy(layout_before, &layout, sizeof(layout));
    native_vorbis_numeric_status_t measured = native_vorbis_frame_floor1_measure(
        frame, channel, curve, bins, &layout);
    emit_integer(out, (uint32_t)(int32_t)measured, 4);
    if (frame->floors[channel].state.type == 0) {
        check(measured == NATIVE_VORBIS_NUMERIC_INVALID);
        check(memcmp(layout_before, &layout, sizeof(layout)) == 0);
        uint32_t unchanged[2] = {UINT32_C(0x12345678), UINT32_C(0x87654321)};
        uint32_t *output = workspace_array(2, sizeof(*output));
        memcpy(output, unchanged, sizeof(unchanged));
        product_failure(frame, channel, curve, bins, output, 2,
            unchanged, 2, NATIVE_VORBIS_NUMERIC_INVALID);
        emit_integer(out, (uint32_t)(int32_t)NATIVE_VORBIS_NUMERIC_INVALID, 4);
        tracked_free(output); tracked_free(curve);
        return (uint32_t)(refusal_total - before_refusals);
    }
    check(measured == NATIVE_VORBIS_NUMERIC_OK && layout.bins == bins);
    check(layout.limb_count <= SIZE_MAX / sizeof(uint32_t));
    size_t count = (size_t)layout.limb_count;
    uint32_t *output = workspace_array(count, sizeof(*output));
    native_vorbis_floor1_product_t result;
    native_vorbis_numeric_status_t status = native_vorbis_frame_floor1_product(
        frame, channel, curve, bins, output, count, &result);
    check(status == NATIVE_VORBIS_NUMERIC_OK);
    check(result.samples == (count ? output : NULL));
    check(result.layout.bins == layout.bins && result.layout.limbs == layout.limbs &&
        result.layout.magnitude_bits == layout.magnitude_bits &&
        result.layout.exponent == layout.exponent && result.layout.limb_count == layout.limb_count);
    emit_integer(out, (uint32_t)(int32_t)status, 4);
    product_put(out, &result, curve);
    uint64_t canonical = product_hash(&result, curve);
    uint32_t *expected = workspace_array(count, sizeof(*expected));
    if (count) memcpy(expected, output, count * sizeof(*expected));

    product_failure(NULL, channel, curve, bins, output, count,
        expected, count, NATIVE_VORBIS_NUMERIC_INVALID);
    product_failure(frame, frame->floor_count, curve, bins, output, count,
        expected, count, NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_floor1_product(frame, channel, curve, bins,
        output, count, NULL) == NATIVE_VORBIS_NUMERIC_INVALID);
    check(native_vorbis_frame_floor1_measure(frame, channel, curve, bins, NULL) == NATIVE_VORBIS_NUMERIC_INVALID);
    product_failure(frame, channel, curve, bins, output, SIZE_MAX,
        expected, count, NATIVE_VORBIS_NUMERIC_RANGE);

    if (count) {
        product_failure(frame, channel, curve, bins - 1, output, count,
            expected, count, NATIVE_VORBIS_NUMERIC_CAPACITY);
        product_failure(frame, channel, NULL, bins, output, count,
            expected, count, NATIVE_VORBIS_NUMERIC_INVALID);
        product_failure(frame, channel, curve, bins, output, count - 1,
            expected, count, NATIVE_VORBIS_NUMERIC_CAPACITY);
        product_failure(frame, channel, curve, bins, NULL, count,
            expected, count, NATIVE_VORBIS_NUMERIC_INVALID);
        native_vorbis_floor1_product_layout_t refused;
        unsigned char refused_before[sizeof(refused)];
        memset(&refused, 0xa5, sizeof(refused)); memcpy(refused_before, &refused, sizeof(refused));
        check(native_vorbis_frame_floor1_measure(frame, channel, curve, bins - 1, &refused)
            == NATIVE_VORBIS_NUMERIC_CAPACITY);
        check(memcmp(refused_before, &refused, sizeof(refused)) == 0);
        ++refusal_total;
    } else {
        native_vorbis_floor1_product_t zero;
        check(native_vorbis_frame_floor1_product(frame, channel, NULL, 0, NULL, 0, &zero)
            == NATIVE_VORBIS_NUMERIC_OK);
        check(!zero.samples && zero.layout.bins == bins && !zero.layout.limbs &&
            !zero.layout.magnitude_bits && !zero.layout.exponent && !zero.layout.limb_count);
        native_vorbis_floor1_product_layout_t zero_layout;
        check(native_vorbis_frame_floor1_measure(frame, channel, NULL, 0, &zero_layout)
            == NATIVE_VORBIS_NUMERIC_OK);
        check(zero_layout.bins == bins && !zero_layout.limb_count);
    }
    check(native_vorbis_frame_floor1_product(frame, channel, curve, bins, output, count, &result)
        == NATIVE_VORBIS_NUMERIC_OK);
    check(product_hash(&result, curve) == canonical);
    if (count) check(memcmp(expected, output, count * sizeof(*expected)) == 0);
    validate_allocations();
    tracked_free(expected); tracked_free(output); tracked_free(curve);
    return (uint32_t)(refusal_total - before_refusals);
}

static void product_case(FILE *input, emitter_t *out, uint32_t index) {
    uint64_t starting_checks = checks;
    check(!allocations && live_allocations == 0 && live_bytes == 0);
    uint32_t name_bytes = (uint32_t)read_integer(input, 4);
    check(name_bytes && name_bytes <= 128);
    for (uint32_t i = 0; i < name_bytes; ++i) (void)read_integer(input, 1);
    packet_input_t info = read_packet(input), header = read_packet(input), payload = read_packet(input);
    uint64_t start = read_integer(input, 8), initial_eop = read_integer(input, 4);
    check(initial_eop <= 1);
    native_vorbis_setup_allocator_t allocator = {&owner_cookie, owner_allocate, owner_release};
    native_vorbis_setup_owner_t *owner = NULL;
    check(native_vorbis_setup_owner_replace(&owner, info.data, info.bytes, info.bits,
        header.data, header.bytes, header.bits, &allocator) == NATIVE_VORBIS_SETUP_OWNER_OK);
    const native_vorbis_setup_t *setup = native_vorbis_setup_owner_view(owner);
    check(setup != NULL);
    for (allocation_t *at = allocations; at; at = at->next)
        if (at->tag == TAG_OWNER) freeze(at->data);
    native_vorbis_packet_t packet;
    check(native_vorbis_packet_init(&packet, payload.data, payload.bytes, payload.bits, start)
        == NATIVE_VORBIS_NUMERIC_OK);
    packet.end_of_packet = initial_eop != 0;
    native_vorbis_frame_requirements_t requirements;
    native_vorbis_numeric_status_t measured = native_vorbis_frame_measure(setup, &packet, &requirements);
    emit_integer(out, index, 4); emit_integer(out, (uint32_t)(int32_t)measured, 4);
    native_vorbis_frame_workspace_t workspace = {0};
    if (measured == NATIVE_VORBIS_NUMERIC_OK) {
        workspace.floor_capacity = requirements.floor_count;
        workspace.floor0_capacity = (size_t)requirements.floor0_values;
        workspace.floor1_capacity = (size_t)requirements.floor1_values;
        workspace.spectrum_capacity = (size_t)requirements.residue_bound.limb_count;
        workspace.classification_capacity = (size_t)requirements.residue_bound.classification_count;
        workspace.floors = workspace_array(workspace.floor_capacity, sizeof(*workspace.floors));
        workspace.floor0 = workspace_array(workspace.floor0_capacity, sizeof(*workspace.floor0));
        workspace.floor1 = workspace_array(workspace.floor1_capacity, sizeof(*workspace.floor1));
        workspace.spectrum = workspace_array(workspace.spectrum_capacity, sizeof(*workspace.spectrum));
        workspace.classifications = workspace_array(workspace.classification_capacity, sizeof(*workspace.classifications));
    }
    native_vorbis_packet_frame_t frame;
    native_vorbis_numeric_status_t status = native_vorbis_frame_decode(setup, &packet, &workspace, &frame);
    emit_integer(out, (uint32_t)(int32_t)status, 4);
    uint32_t refusals = 0;
    if (status == NATIVE_VORBIS_NUMERIC_OK) {
        validate_frame(setup, &workspace, &frame);
        frame_put(out, &frame);
        unsigned char frame_before[sizeof(frame)];
        memcpy(frame_before, &frame, sizeof(frame));
        if (workspace.floors) freeze(workspace.floors);
        if (workspace.floor0) freeze(workspace.floor0);
        if (workspace.floor1) freeze(workspace.floor1);
        if (workspace.spectrum) freeze(workspace.spectrum);
        if (workspace.classifications) freeze(workspace.classifications);
        for (uint32_t channel = 0; channel < frame.floor_count; ++channel)
            refusals += product_channel(&frame, channel, out);
        check(memcmp(frame_before, &frame, sizeof(frame)) == 0);
    }
    emit_integer(out, packet.position, 8); emit_integer(out, packet.end_of_packet, 4);
    validate_allocations();
    native_vorbis_setup_owner_clear(&owner);
    tracked_free(workspace.classifications); tracked_free(workspace.spectrum);
    tracked_free(workspace.floor1); tracked_free(workspace.floor0); tracked_free(workspace.floors);
    tracked_free(payload.data); tracked_free(header.data); tracked_free(info.data);
    check(!allocations && live_allocations == 0 && live_bytes == 0);
    emit_integer(out, refusals, 4); emit_integer(out, checks - starting_checks, 8);
}

int main(int argc, char **argv) {
    require(argc == 3);
    FILE *input = fopen(argv[1], "rb"), *output = fopen(argv[2], "wb");
    require(input && output);
    unsigned char magic[8];
    require(fread(magic, 1, sizeof(magic), input) == sizeof(magic));
    require(memcmp(magic, "VFRAME01", sizeof(magic)) == 0);
    require(fwrite("VF1FRAME", 1, sizeof(magic), output) == sizeof(magic));
    uint32_t cases = (uint32_t)read_integer(input, 4);
    emitter_t emitter = {output, UINT64_C(14695981039346656037)};
    emit_integer(&emitter, cases, 4);
    for (uint32_t i = 0; i < cases; ++i) product_case(input, &emitter, i);
    require(fgetc(input) == EOF && !ferror(input));
    require(fclose(input) == 0 && fclose(output) == 0);
    require(!allocations && live_allocations == 0 && live_bytes == 0);
    printf("FLOOR1_FRAME_CAPTURE cases=%" PRIu32 " refusals=%" PRIu64 " checks=%" PRIu64
        " live=0 bytes=0\n", cases, refusal_total, checks);
    return 0;
}
