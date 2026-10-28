// Shared bounded host/MCU pipeline. Only public owned Vorbis APIs are called.
#pragma once
#include "native_vorbis_synthesis.h"
#include "native_vorbis_setup_owner.h"
#include "native_vorbis_floor0_spectrum.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    const uint8_t *identification, *setup, *audio;
    size_t identification_bytes, setup_bytes, audio_bytes;
    // packet_offsets has packet_count+1 monotone entries; granules has count.
    // Every raw transported packet uses its complete octet extent. EOS is set
    // only on the final packet. All input storage stays immutable until return.
    const uint32_t *packet_offsets;
    const int64_t *granules;
    uint32_t packet_count;
} vorbis_synthesis_pipeline_case_t;

typedef struct {
    uint32_t packet, blocksize, channels, floor0_channels, floor1_channels;
    uint64_t consumed_bits;
    bool end_of_packet;
    native_vorbis_synthesis_result_t synthesis;
} vorbis_synthesis_pipeline_packet_t;

typedef struct {
    void *context;
    // Packet metadata precedes its PCM chunks, including empty prime packets.
    bool (*packet)(void *, const vorbis_synthesis_pipeline_packet_t *);
    // Chunks contain at most128 interleaved S16 samples and borrow their data
    // only during this call. A chunk can end between channels; concatenate it.
    bool (*pcm)(void *, uint32_t packet, const int16_t *, size_t samples);
    void (*error)(void *, uint32_t packet, const char *stage, int status,
        uint32_t channel, uint32_t route);
} vorbis_synthesis_pipeline_callbacks_t;

typedef struct {
    uint64_t packets, frames, pcm_samples, floor0_channels, floor1_channels;
    size_t allocations, releases, live_allocations, live_payload_bytes;
    size_t peak_allocations, peak_payload_bytes;
    uint32_t failed_packet, failed_channel, failed_route;
    int status;
} vorbis_synthesis_pipeline_result_t;

// Allocates checked actual-size buffers through malloc, reuses shared lookup
// and channel scratch, and frees every allocation on all return paths. Payload
// counters exclude the allocator's aligned size header. No global mutable
// storage, FILE interface, host-only allocator, saved coefficients/transforms,
// private decoder, network, task or physical-device API is used.
// Return0 means every packet and callback completed; other results retain the
// failing native status or a negative helper status. An error callback names
// the stage. Result is written after cleanup, including on failure.
int vorbis_synthesis_pipeline_run(const vorbis_synthesis_pipeline_case_t *,
    const vorbis_synthesis_pipeline_callbacks_t *, vorbis_synthesis_pipeline_result_t *);

#ifdef __cplusplus
}
#endif
