#pragma once
#include <stdint.h>
struct helix_timing_fixture_t { uint32_t kind,first,count,samples; };
struct helix_timing_packet_t { uint32_t offset,bytes; };
#define HELIX_TIMING_CASES 2U
#define HELIX_TIMING_PACKETS 4U
#define HELIX_TIMING_PAYLOAD_BYTES 16U
static const helix_timing_fixture_t helix_timing_fixtures[]={{1,0,2,2304},{2,2,2,2048}};
static const helix_timing_packet_t helix_timing_packets[]={{0,4},{4,4},{8,4},{12,4}};
static const uint32_t helix_timing_payload[]={1,2,3,4};
