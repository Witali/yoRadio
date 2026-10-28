// Transactional selection of the unchanged creator's basic integer arithmetic.
#include "native_vorbis_bigfloat.h"
#include <limits.h>
#include <string.h>

#define CONTEXT_COOKIE UINT64_C(0x6e76626632303235)
typedef union {
    max_align_t alignment;
    struct { size_t capacity; } record;
} allocation_header_t;

static bool active(const native_vorbis_bigfloat_context_t *context) {
    return context && context->cookie == CONTEXT_COOKIE;
}

static void increment(uint64_t *value) {
    if (*value != UINT64_MAX) ++*value;
}

static void allocation_failure(native_vorbis_bigfloat_context_t *context) {
    context->accounting.allocation_failed = true;
    increment(&context->accounting.failures);
}

static void release_block(native_vorbis_bigfloat_context_t *context,
    allocation_header_t *header) {
    size_t bytes = sizeof(*header) + header->record.capacity;
    --context->accounting.live_allocations;
    context->accounting.live_bytes -= bytes;
    context->allocator.release(context->allocator.opaque, header);
}

static void *engine_realloc(void *opaque, void *previous, size_t size) {
    native_vorbis_bigfloat_context_t *context = opaque;
    allocation_header_t *old = previous ? (allocation_header_t *)previous - 1 : NULL;
    if (!size) {
        if (old) release_block(context, old);
        return NULL;
    }
    // LibBF deliberately ignores shrink failures: satisfy them without allocation.
    if (old && size <= old->record.capacity) return previous;
    increment(&context->accounting.attempts);
    if (context->accounting.allocation_failed || size > SIZE_MAX - sizeof(allocation_header_t) ||
        context->accounting.live_allocations == SIZE_MAX ||
        context->accounting.live_bytes > SIZE_MAX - sizeof(allocation_header_t) - size) {
        allocation_failure(context);
        return NULL;
    }
    size_t bytes = sizeof(allocation_header_t) + size;
    allocation_header_t *replacement = context->allocator.allocate(context->allocator.opaque, bytes);
    if (!replacement) {
        allocation_failure(context);
        return NULL;
    }
    replacement->record.capacity = size;
    ++context->accounting.live_allocations;
    context->accounting.live_bytes += bytes;
    if (context->accounting.live_allocations > context->accounting.peak_allocations)
        context->accounting.peak_allocations = context->accounting.live_allocations;
    if (context->accounting.live_bytes > context->accounting.peak_bytes)
        context->accounting.peak_bytes = context->accounting.live_bytes;
    void *data = replacement + 1;
    if (old) {
        memcpy(data, previous, old->record.capacity);
        release_block(context, old);
    }
    return data;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_context_init(
    native_vorbis_bigfloat_context_t *context,
    const native_vorbis_bigfloat_allocator_t *allocator) {
    if (!context || !allocator || !allocator->allocate || !allocator->release)
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_bigfloat_allocator_t copy = *allocator;
    memset(context, 0, sizeof(*context));
    context->allocator = copy;
    bf_context_init(&context->engine, engine_realloc, context);
    context->cookie = CONTEXT_COOKIE;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_clear_failure(
    native_vorbis_bigfloat_context_t *context) {
    if (!active(context)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    context->accounting.allocation_failed = false;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_stats(
    const native_vorbis_bigfloat_context_t *context,
    native_vorbis_bigfloat_stats_t *result) {
    if (!active(context) || !result) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_bigfloat_stats_t copy = context->accounting;
    copy.ntt_initialized = context->engine.ntt_state != NULL;
    *result = copy;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_context_end(
    native_vorbis_bigfloat_context_t *context) {
    if (!active(context)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    bf_context_end(&context->engine);
    if (context->accounting.live_allocations) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    context->cookie = 0;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

static size_t trailing_bits(const bf_t *number) {
    size_t index = 0;
    while (number->tab[index] == 0) ++index;
    limb_t word = number->tab[index];
    size_t bits = index * LIMB_BITS;
    while (!(word & 1)) { word >>= 1; ++bits; }
    return bits;
}

static native_vorbis_bigfloat_status_t value_status(
    const native_vorbis_bigfloat_context_t *context, const bf_t *number) {
    if (!active(context) || !number || number->ctx != &context->engine ||
        (number->sign != 0 && number->sign != 1)) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    if (!number->len)
        return number->expn == BF_EXP_ZERO ? NATIVE_VORBIS_BIGFLOAT_OK : NATIVE_VORBIS_BIGFLOAT_ARITHMETIC;
    if (number->len > (NATIVE_VORBIS_BIGFLOAT_MAX_BITS + LIMB_BITS - 1) / LIMB_BITS ||
        number->expn < -NATIVE_VORBIS_BIGFLOAT_MAX_TOP || number->expn > NATIVE_VORBIS_BIGFLOAT_MAX_TOP)
        return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    if (!number->tab || !(number->tab[number->len - 1] >> (LIMB_BITS - 1)))
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    size_t width = (size_t)number->len * LIMB_BITS - trailing_bits(number);
    return width <= NATIVE_VORBIS_BIGFLOAT_MAX_BITS ? NATIVE_VORBIS_BIGFLOAT_OK :
        NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_init(
    native_vorbis_bigfloat_context_t *context, bf_t *number) {
    if (!active(context) || !number) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    bf_init(&context->engine, number);
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_clear(
    native_vorbis_bigfloat_context_t *context, bf_t *number) {
    native_vorbis_bigfloat_status_t status = value_status(context, number);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    bf_delete(number);
    bf_init(&context->engine, number);
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

static native_vorbis_bigfloat_status_t writable(native_vorbis_bigfloat_context_t *context, bf_t *destination) {
    native_vorbis_bigfloat_status_t status = value_status(context, destination);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    return context->accounting.allocation_failed ? NATIVE_VORBIS_BIGFLOAT_NO_MEMORY : NATIVE_VORBIS_BIGFLOAT_OK;
}

static native_vorbis_bigfloat_status_t publish(native_vorbis_bigfloat_context_t *context,
    bf_t *destination, bf_t *temporary, int flags) {
    native_vorbis_bigfloat_status_t status;
    if (context->accounting.allocation_failed || (flags & BF_ST_MEM_ERROR))
        status = NATIVE_VORBIS_BIGFLOAT_NO_MEMORY;
    else if (flags & (BF_ST_OVERFLOW | BF_ST_UNDERFLOW))
        status = NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    else if (flags & (BF_ST_INVALID_OP | BF_ST_DIVIDE_ZERO))
        status = NATIVE_VORBIS_BIGFLOAT_ARITHMETIC;
    else
        status = value_status(context, temporary);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) {
        bf_move(destination, temporary);
        bf_init(&context->engine, temporary);
    }
    bf_delete(temporary);
    return status;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_set_u64(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, uint64_t value) {
    native_vorbis_bigfloat_status_t status = writable(context, destination);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    bf_t temporary;
    bf_init(&context->engine, &temporary);
    return publish(context, destination, &temporary, bf_set_ui(&temporary, value));
}

static unsigned width32(uint32_t value) {
    unsigned width = 0;
    while (value) { value >>= 1; ++width; }
    return width;
}

static limb_t input_limb(const uint32_t *words, size_t count, size_t index) {
#if LIMB_BITS == 32
    return index < count ? words[index] : 0;
#else
    size_t low = index * 2;
    limb_t value = low < count ? words[low] : 0;
    if (low + 1 < count) value |= (limb_t)words[low + 1] << 32;
    return value;
#endif
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_import(
    native_vorbis_bigfloat_context_t *context, bf_t *destination,
    const uint32_t *words, size_t count, int64_t exponent, bool negative) {
    native_vorbis_bigfloat_status_t status = writable(context, destination);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    if (count > NATIVE_VORBIS_BIGFLOAT_MAX_WORDS) return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    if ((!count && (exponent || negative)) || (count && (!words || !words[count - 1])))
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    if (!count) return native_vorbis_bigfloat_set_u64(context, destination, 0);
    size_t width = (count - 1) * 32 + width32(words[count - 1]);
    // Do not add an untrusted signed64 exponent until its bounded range is proved.
    if (exponent < -(int64_t)NATIVE_VORBIS_BIGFLOAT_MAX_TOP - (int64_t)width ||
        exponent > (int64_t)NATIVE_VORBIS_BIGFLOAT_MAX_TOP - (int64_t)width)
        return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    bf_t temporary;
    bf_init(&context->engine, &temporary);
    limb_t length = (limb_t)((width + LIMB_BITS - 1) / LIMB_BITS);
    if (bf_resize(&temporary, length)) return publish(context, destination, &temporary, BF_ST_MEM_ERROR);
    unsigned shift = (unsigned)((LIMB_BITS - (width % LIMB_BITS)) % LIMB_BITS);
    for (size_t i = 0; i < length; ++i) {
        limb_t value = input_limb(words, count, i);
        temporary.tab[i] = shift ? (value << shift) | (i ? input_limb(words, count, i - 1) >> (LIMB_BITS - shift) : 0) : value;
    }
    temporary.sign = negative;
    temporary.expn = (slimb_t)(exponent + (int64_t)width);
    return publish(context, destination, &temporary, bf_normalize_and_round(&temporary, BF_PREC_INF, BF_RNDZ));
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_copy(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, const bf_t *source) {
    native_vorbis_bigfloat_status_t status = writable(context, destination);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = value_status(context, source);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    bf_t temporary;
    bf_init(&context->engine, &temporary);
    return publish(context, destination, &temporary, bf_set(&temporary, source));
}

static native_vorbis_bigfloat_status_t operation_parameters(uint32_t precision,
    native_vorbis_bigfloat_round_t rounding) {
    if (precision < 2 || (rounding != NATIVE_VORBIS_BIGFLOAT_DOWN && rounding != NATIVE_VORBIS_BIGFLOAT_UP))
        return NATIVE_VORBIS_BIGFLOAT_INVALID;
    return precision <= NATIVE_VORBIS_BIGFLOAT_MAX_BITS ? NATIVE_VORBIS_BIGFLOAT_OK : NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
}

static bf_flags_t rounding_flags(native_vorbis_bigfloat_round_t rounding) {
    return rounding == NATIVE_VORBIS_BIGFLOAT_DOWN ? BF_RNDD : BF_RNDU;
}

typedef int (*binary_operation_t)(bf_t *, const bf_t *, const bf_t *, limb_t, bf_flags_t);
static native_vorbis_bigfloat_status_t binary(native_vorbis_bigfloat_context_t *context,
    bf_t *destination, const bf_t *left, const bf_t *right, uint32_t precision,
    native_vorbis_bigfloat_round_t rounding, binary_operation_t operation) {
    native_vorbis_bigfloat_status_t status = writable(context, destination);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = value_status(context, left);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = value_status(context, right);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = operation_parameters(precision, rounding);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    bf_t temporary;
    bf_init(&context->engine, &temporary);
    return publish(context, destination, &temporary, operation(&temporary, left, right, precision, rounding_flags(rounding)));
}

#define BINARY_WRAPPER(name) \
native_vorbis_bigfloat_status_t native_vorbis_bigfloat_##name( \
    native_vorbis_bigfloat_context_t *context, bf_t *destination, const bf_t *left, \
    const bf_t *right, uint32_t precision, native_vorbis_bigfloat_round_t rounding) { \
    return binary(context, destination, left, right, precision, rounding, bf_##name); \
}
BINARY_WRAPPER(add)
BINARY_WRAPPER(sub)
BINARY_WRAPPER(mul)
BINARY_WRAPPER(div)
#undef BINARY_WRAPPER

static native_vorbis_bigfloat_status_t unary(native_vorbis_bigfloat_context_t *context,
    bf_t *destination, const bf_t *source, uint32_t precision,
    native_vorbis_bigfloat_round_t rounding, bool square_root) {
    native_vorbis_bigfloat_status_t status = writable(context, destination);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = value_status(context, source);
    if (status == NATIVE_VORBIS_BIGFLOAT_OK) status = operation_parameters(precision, rounding);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    bf_t temporary;
    bf_init(&context->engine, &temporary);
    int result;
    if (square_root) result = bf_sqrt(&temporary, source, precision, rounding_flags(rounding));
    else {
        result = bf_set(&temporary, source);
        if (!(result & BF_ST_MEM_ERROR) && !context->accounting.allocation_failed)
            result |= bf_round(&temporary, precision, rounding_flags(rounding));
    }
    return publish(context, destination, &temporary, result);
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_sqrt(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, const bf_t *source,
    uint32_t precision, native_vorbis_bigfloat_round_t rounding) {
    return unary(context, destination, source, precision, rounding, true);
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_round(
    native_vorbis_bigfloat_context_t *context, bf_t *destination, const bf_t *source,
    uint32_t precision, native_vorbis_bigfloat_round_t rounding) {
    return unary(context, destination, source, precision, rounding, false);
}

static uint32_t word32(const bf_t *source, size_t bit) {
    size_t index = bit / LIMB_BITS;
    if (index >= source->len) return 0;
    unsigned shift = (unsigned)(bit % LIMB_BITS);
    limb_t value = source->tab[index] >> shift;
#if LIMB_BITS == 32
    if (shift && index + 1 < source->len) value |= source->tab[index + 1] << (LIMB_BITS - shift);
#else
    if (shift > 32 && index + 1 < source->len) value |= source->tab[index + 1] << (LIMB_BITS - shift);
#endif
    return (uint32_t)value;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_measure_dyadic(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source, size_t *count) {
    if (!count) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_bigfloat_status_t status = value_status(context, source);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    *count = source->len ? ((size_t)source->len * LIMB_BITS - trailing_bits(source) + 31) / 32 : 0;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_export_dyadic(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source,
    uint32_t *words, size_t capacity, size_t *count, int64_t *exponent, bool *negative) {
    if (!count || !exponent || !negative) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    size_t needed;
    native_vorbis_bigfloat_status_t status = native_vorbis_bigfloat_measure_dyadic(context, source, &needed);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    if (capacity > SIZE_MAX / sizeof(*words)) return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    if (capacity < needed) return NATIVE_VORBIS_BIGFLOAT_CAPACITY;
    if (needed && !words) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    size_t first = needed ? trailing_bits(source) : 0;
    int64_t scale = needed ? (int64_t)source->expn - (int64_t)source->len * LIMB_BITS + (int64_t)first : 0;
    for (size_t i = 0; i < needed; ++i) words[i] = word32(source, first + 32 * i);
    *count = needed; *exponent = scale; *negative = needed && source->sign;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

static uint32_t integer_word(const bf_t *source, size_t index) {
    int64_t scale = (int64_t)source->expn - (int64_t)source->len * LIMB_BITS;
    int64_t bit = (int64_t)index * 32 - scale;
    if (bit >= 0) return word32(source, (size_t)bit);
    return bit <= -32 ? 0 : word32(source, 0) << (unsigned)-bit;
}

static bool floor_increment(const bf_t *source) {
    int64_t scale = (int64_t)source->expn - (int64_t)source->len * LIMB_BITS;
    return source->len && source->sign && scale < 0 && (int64_t)trailing_bits(source) < -scale;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_measure_floor(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source, size_t *count) {
    if (!count) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    native_vorbis_bigfloat_status_t status = value_status(context, source);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    size_t needed = source->len && source->expn > 0 ? ((size_t)source->expn + 31) / 32 : 0;
    if (floor_increment(source)) {
        bool carry = true;
        for (size_t i = 0; i < needed && carry; ++i) carry = integer_word(source, i) == UINT32_MAX;
        if (carry) ++needed;
    }
    *count = needed;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}

native_vorbis_bigfloat_status_t native_vorbis_bigfloat_export_floor(
    const native_vorbis_bigfloat_context_t *context, const bf_t *source,
    uint32_t *words, size_t capacity, size_t *count, bool *negative) {
    if (!count || !negative) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    size_t needed;
    native_vorbis_bigfloat_status_t status = native_vorbis_bigfloat_measure_floor(context, source, &needed);
    if (status != NATIVE_VORBIS_BIGFLOAT_OK) return status;
    if (capacity > SIZE_MAX / sizeof(*words)) return NATIVE_VORBIS_BIGFLOAT_ENGINE_LIMIT;
    if (capacity < needed) return NATIVE_VORBIS_BIGFLOAT_CAPACITY;
    if (needed && !words) return NATIVE_VORBIS_BIGFLOAT_INVALID;
    uint64_t carry = floor_increment(source);
    for (size_t i = 0; i < needed; ++i) {
        uint64_t value = (uint64_t)integer_word(source, i) + carry;
        words[i] = (uint32_t)value;
        carry = value >> 32;
    }
    *count = needed; *negative = needed && source->sign;
    return NATIVE_VORBIS_BIGFLOAT_OK;
}
