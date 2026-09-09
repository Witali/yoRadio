#ifndef YORADIO_NATIVE_OPUS_H
#define YORADIO_NATIVE_OPUS_H

#include "ogg_opus_demux.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NATIVE_OPUS_SAMPLE_RATE 48000u
#define NATIVE_OPUS_MAX_SAMPLES 960u
#define NATIVE_OPUS_MAX_PACKET OGG_OPUS_PACKET_BYTES
#define NATIVE_OPUS_IRAM_BYTES 16384u

enum {
    NATIVE_OPUS_NEED_INPUT = 0,
    NATIVE_OPUS_PACKET = 1,
    NATIVE_OPUS_ERR_ARGUMENT = -100,
    NATIVE_OPUS_ERR_MEMORY = -101,
    NATIVE_OPUS_ERR_HEADER = -102,
    NATIVE_OPUS_ERR_VERSION = -103,
    NATIVE_OPUS_ERR_MAPPING = -104,
    NATIVE_OPUS_ERR_DURATION = -105,
    NATIVE_OPUS_ERR_DECODE = -106,
    NATIVE_OPUS_ERR_GRANULE = -107,
    NATIVE_OPUS_ERR_CANCELLED = -108,
    NATIVE_OPUS_ERR_DEMUX = -109,
    NATIVE_OPUS_ERR_TRUNCATED = -110,
    NATIVE_OPUS_ERR_PACKET_SIZE = -111
};

/* PCM is mono, 48 kHz, valid only during this synchronous callback.
 * bitrate_bps describes the compressed packet before trimming. Returning
 * false cancels delivery and latches ERR_CANCELLED until reset. */
typedef bool (*native_opus_pcm_fn)(void *context, const int16_t *pcm,
                                  size_t samples, uint32_t bitrate_bps);

typedef struct {
    void *decoder_state;
    size_t decoder_state_bytes;
    void *scratch;
    size_t scratch_bytes;
    void *iram;
    size_t iram_bytes;
    int16_t *pcm;
    size_t pcm_samples;
    native_opus_pcm_fn output;
    void *output_ctx;
} native_opus_config_t;

/* Caller-owned storage. Only one active adapter may use the shared Opus
 * arenas; output callbacks must not re-enter the decoder. Counters cover
 * all chained logical streams since init/reset. No packet-time allocation.
 * Fields after input_channels are internal and must not be modified. */
typedef struct {
    ogg_opus_demux_t demux;
    native_opus_config_t config;
    uint64_t audio_packets;
    uint64_t decoded_samples;
    uint64_t output_samples;
    uint32_t chains;
    uint32_t bitrate_bps;
    int last_error;
    int libopus_error;
    int demux_error;
    unsigned input_channels;
    uint64_t chain_decoded;
    uint64_t granule_offset;
    uint64_t previous_granule;
    uint32_t skip_remaining;
    uint16_t pre_skip;
    uint8_t stage;
    bool granule_known;
    bool chain_eos;
    bool decoder_ready;
} native_opus_t;

size_t native_opus_decoder_size(void);
/* State must be aligned for native pointers and int32_t (4 bytes on ESP8266,
 * 8 on 64-bit hosts); scratch/IRAM need 4-byte alignment, PCM 2-byte alignment.
 * All five buffers (including this object) must be disjoint. IRAM has 16 KiB usable
 * capacity; extra supplied bytes are not used. Insufficient scratch during
 * decoding returns ERR_MEMORY, resets codec state and latches the error. */
int native_opus_init(native_opus_t *decoder, const native_opus_config_t *config);
/* Opt in for radio servers replaying cached headers at a live page boundary.
 * The ordinary init remains strict; reset preserves this option. */
int native_opus_init_ex(native_opus_t *decoder, const native_opus_config_t *config,
                        bool allow_live_join);
int native_opus_reset(native_opus_t *decoder);
/* Exact byte consumption, at most one Ogg packet (including headers) per
 * call. A PACKET result may consume zero bytes. Drain such results before
 * waiting for more input. Demux CRC is checked at page end: PCM from earlier
 * packets on that page may already have been delivered. */
int native_opus_feed(native_opus_t *decoder, const uint8_t *data, size_t length,
                     size_t *consumed);
/* Strict EOF validation; do not call while a live stream waits for input. */
int native_opus_finish(native_opus_t *decoder);
const char *native_opus_error_string(int error);

#ifdef __cplusplus
}
#endif
#endif
