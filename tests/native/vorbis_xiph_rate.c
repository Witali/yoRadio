/* Independent unsigned sample-rate metadata checks. No setup header, DSP
   initialization, audio packet decoder or deferred target fixture executes. */
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#if defined(XIPH_RATE_ENCODER_HEADER_FIRST)
#include "vorbis/vorbisenc.h"
#elif defined(XIPH_RATE_FILE_HEADER_FIRST)
#include "vorbis/vorbisfile.h"
#else
#include "vorbis/codec.h"
#endif
#include "vorbis_xiph_alloc.h"

#ifndef NATIVE_VORBIS_XIPH_RATE_API
#error "The owned unsigned-rate public header must be selected first"
#endif
_Static_assert(NATIVE_VORBIS_XIPH_RATE_API == 1, "Reviewed rate API version");
_Static_assert(ULONG_MAX >= UINT32_MAX, "The rate field stores every uint32 value");
#if ULONG_MAX == 0xffffffffUL
_Static_assert(_Generic((native_xiph_sample_rate_t)0, unsigned long: 1, default: 0),
               "ILP32/LLP64 rate is unsigned long");
#else
_Static_assert(_Generic((native_xiph_sample_rate_t)0, long: 1, default: 0),
               "Wider long retains the upstream signed source type");
#endif
_Static_assert(_Generic(((vorbis_info *)0)->bitrate_nominal, long: 1, default: 0),
               "Signed bitrate hints retain their source type");

typedef struct {
  int version;
  int channels;
  long rate;
  long bitrate_upper;
  long bitrate_nominal;
  long bitrate_lower;
  long bitrate_window;
  void *codec_setup;
} upstream_info_layout_t;

_Static_assert(sizeof(vorbis_info) == sizeof(upstream_info_layout_t), "Original info size");
_Static_assert(_Alignof(vorbis_info) == _Alignof(upstream_info_layout_t), "Original info alignment");
#define ORIGINAL_OFFSET(member) \
  _Static_assert(offsetof(vorbis_info, member) == offsetof(upstream_info_layout_t, member), \
                 "Original info offset: " #member)
ORIGINAL_OFFSET(version);
ORIGINAL_OFFSET(channels);
ORIGINAL_OFFSET(rate);
ORIGINAL_OFFSET(bitrate_upper);
ORIGINAL_OFFSET(bitrate_nominal);
ORIGINAL_OFFSET(bitrate_lower);
ORIGINAL_OFFSET(bitrate_window);
ORIGINAL_OFFSET(codec_setup);
#undef ORIGINAL_OFFSET

#define CHECK(expression) do { \
  int condition = !!(expression); \
  assert(condition); \
  if (!condition) abort(); \
} while (0)

enum { ID_BYTES = 30, RATE_CAPACITY = 128 };
static const uint64_t guard = UINT64_C(0xa6713bd5c80249ef);
static unsigned scenarios;

typedef struct {
  unsigned channels;
  unsigned short_exponent;
  unsigned long_exponent;
  int32_t upper, nominal, lower;
} profile_t;

static const profile_t profiles[] = {
  {1, 6, 6, 0, 0, 0},
  {2, 6, 13, INT32_MAX, INT32_MIN, -1},
  {255, 13, 13, 1, -1, INT32_MIN},
  {4, 7, 10, INT32_MIN, INT32_MAX, 123456789}
};

static const unsigned char comment_header[] = {
  3, 'v', 'o', 'r', 'b', 'i', 's',
  1, 0, 0, 0, 'R', /* One-byte vendor. */
  0, 0, 0, 0, 1   /* Zero comments and the framing bit. */
};

static void policy(size_t ordinal, int zero_null) {
  xiph_port_test_reset(ordinal);
  xiph_port_test_zero_null(zero_null);
}

static void no_owners(void) {
  CHECK(xiph_port_test_live() == 0 && xiph_port_test_bytes() == 0);
}

static void put32(unsigned char *destination, uint32_t value) {
  for (unsigned byte = 0; byte < 4; byte++)
    destination[byte] = (unsigned char)(value >> (byte * 8));
}

static void identification(unsigned char output[ID_BYTES], uint32_t rate,
                           const profile_t *profile) {
  memset(output, 0, ID_BYTES);
  output[0] = 1;
  memcpy(output + 1, "vorbis", 6);
  output[11] = (unsigned char)profile->channels;
  put32(output + 12, rate);
  put32(output + 16, (uint32_t)profile->upper);
  put32(output + 20, (uint32_t)profile->nominal);
  put32(output + 24, (uint32_t)profile->lower);
  output[28] = (unsigned char)(profile->short_exponent | (profile->long_exponent << 4));
  output[29] = 1;
}

static int read_header(vorbis_info *info, vorbis_comment *comment,
                       const unsigned char *original, size_t bytes,
                       int number, int initial) {
  CHECK(original && bytes <= LONG_MAX && bytes <= SIZE_MAX - 16);
  unsigned char *allocation = malloc(bytes + 16);
  CHECK(allocation);
  unsigned char *input = allocation + 8;
  memcpy(allocation, &guard, 8);
  memcpy(input, original, bytes);
  memcpy(input + bytes, &guard, 8);
  ogg_packet packet;
  memset(&packet, 0, sizeof(packet));
  packet.packet = input;
  packet.bytes = (long)bytes;
  packet.packetno = number;
  packet.b_o_s = initial;
  unsigned char saved_packet[sizeof(packet)];
  memcpy(saved_packet, &packet, sizeof(packet));
  int status = vorbis_synthesis_headerin(info, comment, &packet);
  uint64_t before, after;
  memcpy(&before, allocation, 8);
  memcpy(&after, input + bytes, 8);
  CHECK(before == guard && after == guard);
  CHECK(memcmp(input, original, bytes) == 0);
  CHECK(memcmp(saved_packet, &packet, sizeof(packet)) == 0);
  free(allocation);
  return status;
}

static void initialize(vorbis_info *info, vorbis_comment *comment, int zero_null) {
  no_owners();
  policy(0, zero_null);
  vorbis_info_init(info);
  vorbis_comment_init(comment);
  CHECK(info->codec_setup && info->rate == 0 && comment->vendor == NULL);
  CHECK(xiph_port_test_failures() == 0);
}

static void close_headers(vorbis_info *info, vorbis_comment *comment, int zero_null) {
  policy(0, zero_null);
  vorbis_comment_clear(comment);
  vorbis_info_clear(info);
  vorbis_comment_clear(comment);
  vorbis_info_clear(info);
  CHECK(xiph_port_test_attempts() == 0);
  no_owners();
}

static void info_check(vorbis_info *info, uint32_t rate, const profile_t *profile) {
  CHECK(rate > 0 && info->rate > 0 && (uint64_t)info->rate == (uint64_t)rate);
  CHECK(info->version == 0 && info->channels == (int)profile->channels);
  CHECK(info->bitrate_upper == (long)profile->upper);
  CHECK(info->bitrate_nominal == (long)profile->nominal);
  CHECK(info->bitrate_lower == (long)profile->lower && info->bitrate_window == 0);
  CHECK(vorbis_info_blocksize(info, 0) == (long)(1U << profile->short_exponent));
  CHECK(vorbis_info_blocksize(info, 1) == (long)(1U << profile->long_exponent));
}

static void duplicate_check(vorbis_info *info, vorbis_comment *comment,
                            const unsigned char *bytes, size_t size,
                            int number, int initial, int zero_null) {
  unsigned char saved_info[sizeof(*info)], saved_comment[sizeof(*comment)];
  memcpy(saved_info, info, sizeof(*info));
  memcpy(saved_comment, comment, sizeof(*comment));
  size_t live = xiph_port_test_live(), owned_bytes = xiph_port_test_bytes();
  policy(0, zero_null);
  CHECK(read_header(info, comment, bytes, size, number, initial) == OV_EBADHEADER);
  CHECK(xiph_port_test_attempts() == 0 && xiph_port_test_failures() == 0);
  CHECK(xiph_port_test_live() == live && xiph_port_test_bytes() == owned_bytes);
  CHECK(memcmp(saved_info, info, sizeof(*info)) == 0);
  CHECK(memcmp(saved_comment, comment, sizeof(*comment)) == 0);
}

static void complete_headers(uint32_t rate, const profile_t *profile, int zero_null) {
  unsigned char id[ID_BYTES];
  identification(id, rate, profile);
  vorbis_info info;
  vorbis_comment comment;
  initialize(&info, &comment, zero_null);
  policy(0, zero_null);
  int status = read_header(&info, &comment, id, sizeof(id), 0, 1);
  CHECK(xiph_port_test_attempts() == 0 && xiph_port_test_failures() == 0);
  if (rate == 0) {
    CHECK(status == OV_EBADHEADER && info.rate == 0 && info.codec_setup == NULL);
    close_headers(&info, &comment, zero_null);
    scenarios++;
    return;
  }
  CHECK(status == 0);
  info_check(&info, rate, profile);
  duplicate_check(&info, &comment, id, sizeof(id), 0, 1, zero_null);
  policy(0, zero_null);
  CHECK(read_header(&info, &comment, comment_header, sizeof(comment_header), 1, 0) == 0);
  CHECK(xiph_port_test_failures() == 0 && comment.comments == 0);
  CHECK(comment.vendor && !strcmp(comment.vendor, "R"));
  CHECK(comment.user_comments && !comment.user_comments[0] && comment.comment_lengths);
  info_check(&info, rate, profile);
  duplicate_check(&info, &comment, comment_header, sizeof(comment_header), 1, 0, zero_null);
  policy(0, zero_null);
  /* This API uses vi only. No DSP initialization or audio decoding occurs. */
  vorbis_dsp_state state;
  memset(&state, 0, sizeof(state));
  state.vi = &info;
  CHECK(vorbis_granule_time(&state, 0) == 0.0);
  CHECK(vorbis_granule_time(&state, (ogg_int64_t)(uint64_t)rate) == 1.0);
  CHECK(vorbis_granule_time(&state, (ogg_int64_t)((uint64_t)rate * 2)) == 2.0);
  CHECK(vorbis_granule_time(&state, -1) == -1.0);
  CHECK(vorbis_granule_time(&state, INT64_MIN) == 0x1p63 / (double)rate);
  CHECK(vorbis_granule_time(&state, -2) == 0x1p64 / (double)rate);
  CHECK(xiph_port_test_attempts() == 0);
  close_headers(&info, &comment, zero_null);
  scenarios++;
}

static void prefix_trial(uint32_t rate, const profile_t *profile,
                         size_t prefix, int zero_null) {
  unsigned char id[ID_BYTES];
  identification(id, rate, profile);
  vorbis_info info;
  vorbis_comment comment;
  initialize(&info, &comment, zero_null);
  policy(0, zero_null);
  int status = read_header(&info, &comment, id, prefix, 0, 1);
  int expected = prefix < 7 ? OV_ENOTVORBIS : (prefix < 11 ? OV_EVERSION : OV_EBADHEADER);
  CHECK(status == expected && xiph_port_test_attempts() == 0);
  close_headers(&info, &comment, zero_null);
  scenarios++;
  /* Failure recovery is a fresh instance, not an unsupported partial retry. */
  complete_headers(rate ? rate : 1U, profile, zero_null);
}

static void add_rate(uint32_t rates[RATE_CAPACITY], size_t *count, uint32_t value) {
  for (size_t i = 0; i < *count; i++) if (rates[i] == value) return;
  CHECK(*count < RATE_CAPACITY);
  rates[(*count)++] = value;
}

static void invalid_controls(int zero_null) {
  const profile_t *profile = &profiles[1];
  for (unsigned kind = 0; kind < 9; kind++) {
    unsigned char id[ID_BYTES];
    identification(id, UINT32_MAX, profile);
    int expected = OV_EBADHEADER, initial = 1;
    if (kind == 0) { id[1] = 'x'; expected = OV_ENOTVORBIS; }
    if (kind == 1) { put32(id + 7, 1); expected = OV_EVERSION; }
    if (kind == 2) { put32(id + 7, UINT32_C(0x80000000)); expected = OV_EVERSION; }
    if (kind == 3) initial = 0;
    if (kind == 4) id[11] = 0;
    if (kind == 5) id[28] = 0x65;
    if (kind == 6) id[28] = 0xe6;
    if (kind == 7) id[28] = 0x6d;
    if (kind == 8) id[29] = 0;
    vorbis_info info;
    vorbis_comment comment;
    initialize(&info, &comment, zero_null);
    policy(0, zero_null);
    CHECK(read_header(&info, &comment, id, sizeof(id), 0, initial) == expected);
    CHECK(xiph_port_test_attempts() == 0 && xiph_port_test_failures() == 0);
    close_headers(&info, &comment, zero_null);
    scenarios++;
    complete_headers(UINT32_MAX, profile, zero_null);
  }
  vorbis_info info;
  vorbis_comment comment;
  initialize(&info, &comment, zero_null);
  duplicate_check(&info, &comment, comment_header, sizeof(comment_header), 1, 0, zero_null);
  close_headers(&info, &comment, zero_null);
  scenarios++;
  complete_headers(UINT32_MAX, profile, zero_null);
}

static void initial_allocation_failure(int zero_null) {
  unsigned char id[ID_BYTES];
  identification(id, UINT32_MAX, &profiles[0]);
  vorbis_info info;
  vorbis_comment comment;
  no_owners();
  policy(1, zero_null);
  vorbis_info_init(&info);
  vorbis_comment_init(&comment);
  CHECK(info.codec_setup == NULL && info.rate == 0);
  CHECK(xiph_port_test_attempts() == 1 && xiph_port_test_failures() == 1);
  CHECK(read_header(&info, &comment, id, sizeof(id), 0, 1) == OV_EFAULT);
  CHECK(xiph_port_test_attempts() == 1 && xiph_port_test_failures() == 1);
  close_headers(&info, &comment, zero_null);
  scenarios++;
  complete_headers(UINT32_MAX, &profiles[0], zero_null);
}

int xiph_rate_tests(void) {
  uint32_t rates[RATE_CAPACITY];
  size_t count = 0;
  scenarios = 0;
  no_owners();
  for (unsigned bit = 0; bit < 32; bit++) {
    uint64_t power = UINT64_C(1) << bit;
    add_rate(rates, &count, (uint32_t)(power - 1));
    add_rate(rates, &count, (uint32_t)power);
    if (power < UINT32_MAX) add_rate(rates, &count, (uint32_t)(power + 1));
  }
  static const uint32_t additional[] = {
    8000, 11025, 22050, 44100, 48000, 96000, 192000,
    UINT32_C(0x55555555), UINT32_C(0xaaaaaaaa),
    UINT32_C(0xffff0000), UINT32_C(0xfffffffe), UINT32_MAX
  };
  for (size_t i = 0; i < sizeof(additional) / sizeof(*additional); i++)
    add_rate(rates, &count, additional[i]);
  for (int zero = 0; zero < 2; zero++) {
    for (size_t index = 0; index < count; index++) {
      for (size_t profile = 0; profile < sizeof(profiles) / sizeof(*profiles); profile++) {
        complete_headers(rates[index], &profiles[profile], zero);
        if (rates[index] == 0) complete_headers(1, &profiles[profile], zero);
      }
      const profile_t *profile = &profiles[index % (sizeof(profiles) / sizeof(*profiles))];
      for (size_t prefix = 0; prefix < ID_BYTES; prefix++)
        prefix_trial(rates[index], profile, prefix, zero);
    }
    invalid_controls(zero);
    initial_allocation_failure(zero);
  }
  no_owners();
  policy(0, 0);
  CHECK(scenarios > 0 && scenarios <= INT_MAX);
  return (int)scenarios;
}
