/* Compile-only public-header ABI/type assertions, in every entry order. */
#ifndef NATIVE_RATE_LAYOUT_PROBE_H
#define NATIVE_RATE_LAYOUT_PROBE_H
#include <limits.h>
#include <stddef.h>
#ifndef NATIVE_VORBIS_XIPH_RATE_API
#error "The owned unsigned-rate header must be selected through every public entry"
#endif
#ifdef __cplusplus
#define RATE_ASSERT static_assert
#define RATE_ALIGN alignof
template<class A, class B> struct rate_same_type { static constexpr bool value = false; };
template<class T> struct rate_same_type<T,T> { static constexpr bool value = true; };
RATE_ASSERT((rate_same_type<native_xiph_sample_rate_t, unsigned long>::value),
            "ESP32 rate source type");
#else
#define RATE_ASSERT _Static_assert
#define RATE_ALIGN _Alignof
RATE_ASSERT(_Generic((native_xiph_sample_rate_t)0, unsigned long: 1, default: 0),
            "ESP32 rate source type");
#endif
typedef struct {
    int version;
    int channels;
    long rate;
    long bitrate_upper;
    long bitrate_nominal;
    long bitrate_lower;
    long bitrate_window;
    void *codec_setup;
} rate_original_info_layout;
RATE_ASSERT(NATIVE_VORBIS_XIPH_RATE_API == 1, "Owned API version");
RATE_ASSERT(ULONG_MAX == 0xffffffffUL, "ESP32 unsigned-long range");
RATE_ASSERT((native_xiph_sample_rate_t)0xffffffffUL > 0, "Positive complete uint32 rate");
RATE_ASSERT(sizeof(vorbis_info) == sizeof(rate_original_info_layout), "Original info size");
RATE_ASSERT(RATE_ALIGN(vorbis_info) == RATE_ALIGN(rate_original_info_layout), "Original info alignment");
#define RATE_OFFSET(name) RATE_ASSERT(offsetof(vorbis_info,name) == offsetof(rate_original_info_layout,name), "Original offset " #name)
RATE_OFFSET(version);
RATE_OFFSET(channels);
RATE_OFFSET(rate);
RATE_OFFSET(bitrate_upper);
RATE_OFFSET(bitrate_nominal);
RATE_OFFSET(bitrate_lower);
RATE_OFFSET(bitrate_window);
RATE_OFFSET(codec_setup);
#undef RATE_OFFSET
#undef RATE_ALIGN
#undef RATE_ASSERT
#endif
