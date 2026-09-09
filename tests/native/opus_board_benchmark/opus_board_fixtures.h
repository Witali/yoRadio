#pragma once
#include <stdint.h>
typedef struct { uint32_t offset, length; } opus_bench_packet_t;
typedef struct {
    uint32_t first_packet, packet_count, expected_hash, samples, bitrate_kbps;
} opus_bench_fixture_t;
#define OPUS_BENCH_FIXTURE_COUNT 2U
#define OPUS_BENCH_PACKET_COUNT 2U
#define OPUS_BENCH_PAYLOAD_BYTES 12U
/* Odd lengths exercise the real module's padded word copies. Two independent
 * cases use the same two packets, so fresh-init and case reset are observable. */
static const uint32_t opus_bench_payload[] __attribute__((aligned(4))) = {
    0x00a51201U, 0xaa7f8002U, 0x00000055U,
};
static const opus_bench_packet_t opus_bench_packets[] __attribute__((aligned(4))) = {
    { 0, 3 }, { 4, 5 },
};
/* PCM samples: 0,32767,-32768,-1,1234,-2345,42,-42; FNV-1a over LE bytes. */
static const opus_bench_fixture_t opus_bench_fixtures[] __attribute__((aligned(4))) = {
    { 0, 2, 0x03c13f4fU, 8, 12 }, { 0, 2, 0x03c13f4fU, 8, 510 },
};
