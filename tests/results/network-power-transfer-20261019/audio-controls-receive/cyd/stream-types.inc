#define STREAM_CHUNK_SIZE 2048
#define MAX_HTTP_REDIRECTS 5
#define STREAM_READ_TIMEOUT_MS 250
typedef struct {
    uint32_t generation;
    native_codec_t requested_codec;
    bool maintenance;
    bool restore;
    char url[512];
} play_command_t;
typedef struct {
    uint32_t generation;
    native_codec_t codec;
    uint16_t data_size;
    uint8_t end_of_stream;
    uint8_t data[];
} encoded_packet_t;
typedef struct {
    uint32_t interval;
    uint32_t bitrate_kbps;
    bool seen, valid;
} stream_headers_t;
typedef struct {
    uint32_t generation;
    native_codec_t codec;
    bool first;
    stream_probe_t probe;
    stream_bitrate_meter_t bitrate;
} stream_input_t;
enum {AUDIO_START_OFF,AUDIO_STARTING,AUDIO_START_READY};
#define STREAM_INPUT_ACTIVE(generation) (atomic_load(&s_generation) == (generation) && atomic_load(&s_failed_generation) != (generation))
