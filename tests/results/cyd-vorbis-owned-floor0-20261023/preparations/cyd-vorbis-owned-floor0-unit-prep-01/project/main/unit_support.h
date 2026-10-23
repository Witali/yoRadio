/* Exact controlled seams extracted from the reviewed owned-book unit. */
#pragma once
static unsigned current_case, current_probe;
static bool failed;

static void require_unit(bool ok, const char *reason) {
    if (ok) return;
    failed = true;
    printf(P "FAILURE case=%u probe=%u reason=%s core=%d\n",
           current_case, current_probe, reason, xPortGetCoreID());
    fflush(stdout);
    for (;;) vTaskDelay(1); /* No reset, hidden retry or apparent COMPLETE. */
}

typedef struct { uint8_t *base, *data; size_t bytes; bool live; } allocation_t;
static allocation_t allocations[32];
static unsigned live_allocations;
static size_t owned_size(const void *data) {
    for (unsigned i = 0; i < 32; ++i)
        if (allocations[i].live && allocations[i].data == data) return allocations[i].bytes;
    require_unit(false, "owned_pointer_required");
    return 0;
}
static bool allocation_guards(const allocation_t *a) {
    for (unsigned i = 0; i < 16; ++i)
        if (a->base[i] != 0xa5 || a->data[a->bytes + i] != 0x5a) return false;
    return true;
}
static void all_guards(void) {
    for (unsigned i = 0; i < 32; ++i)
        if (allocations[i].live) require_unit(allocation_guards(allocations + i), "owned_allocation_guards");
}
void *media_lib_module_calloc(const char *module, size_t count, size_t bytes) {
    require_unit(module && !strcmp(module, "AUD_Codec") && count && bytes && count <= SIZE_MAX / bytes,
                 "bounded_allocator_arguments");
    bytes *= count;
    require_unit(bytes <= 8192, "declared_allocation_bound");
    unsigned slot = 0;
    while (slot < 32 && allocations[slot].live) ++slot;
    require_unit(slot < 32, "allocation_tracking_capacity");
    uint8_t *base = calloc(1, bytes + 32);
    require_unit(base != NULL, "actual_allocation_succeeded");
    memset(base, 0xa5, 16);
    memset(base + 16 + bytes, 0x5a, 16);
    allocations[slot] = (allocation_t){base, base + 16, bytes, true};
    ++live_allocations;
    return base + 16;
}
void media_lib_free(void *data) {
    if (!data) return;
    for (unsigned i = 0; i < 32; ++i) {
        allocation_t *a = allocations + i;
        if (a->live && a->data == data) {
            require_unit(allocation_guards(a), "freed_allocation_guards");
            free(a->base);
            a->live = false;
            --live_allocations;
            return;
        }
    }
    require_unit(false, "single_owned_free");
}

typedef struct {
    const uint8_t *data;
    size_t bytes, position, end;
    oggpack_buffer *tag;
    bool eop;
} bit_view_t;
static bit_view_t view;
static void begin_bits(oggpack_buffer *tag, const uint8_t *data, size_t bytes, size_t start, size_t end) {
    require_unit(data && start <= end && end <= bytes * 8U, "valid_bounded_bitspan");
    memset(tag, 0, sizeof(*tag));
    view = (bit_view_t){data, bytes, start, end, tag, false};
}
static long look_bits(int bits) {
    require_unit(bits >= 0 && bits <= 32, "bounded_bit_width");
    if (view.eop || (size_t)bits > view.end - view.position) return -1;
    uint32_t value = 0;
    for (int i = 0; i < bits; ++i) {
        size_t position = view.position + (size_t)i;
        value |= (uint32_t)((view.data[position / 8U] >> (position % 8U)) & 1U) << i;
    }
    return (long)(int32_t)value;
}
long tremor_oggpack_read(oggpack_buffer *tag, int bits) {
    require_unit(tag == view.tag, "explicit_bitreader_owner");
    long value = look_bits(bits);
    if (view.eop || (size_t)bits > view.end - view.position) { view.eop = true; return -1; }
    view.position += (size_t)bits;
    return value;
}
int tremor_oggpack_eop(oggpack_buffer *tag) {
    require_unit(tag == view.tag, "explicit_bitreader_owner");
    return view.eop;
}
