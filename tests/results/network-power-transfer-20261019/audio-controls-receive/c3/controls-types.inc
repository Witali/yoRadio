typedef struct {
    uint32_t generation;
    native_codec_t requested_codec;
    bool maintenance, restore;
#ifdef YORADIO_CODEC_BENCHMARK
    uint32_t fixture_size;
#endif
    char url[512];
} play_command_t;
enum { MAINTENANCE_OFF, MAINTENANCE_REQUESTED, MAINTENANCE_HELD,
       MAINTENANCE_ABORTING, MAINTENANCE_END_RESUME, MAINTENANCE_END_STOP };
enum { MAINTENANCE_STREAM = 1U, MAINTENANCE_DECODER = 2U,
       MAINTENANCE_OUTPUT = 4U, MAINTENANCE_ALL = 7U };
static atomic_uint s_maintenance_phase;
static atomic_uint s_maintenance_acks;
static atomic_int s_maintenance_error;
static atomic_bool s_maintenance_waiter;
static portMUX_TYPE s_maintenance_token_lock = portMUX_INITIALIZER_UNLOCKED;
// Control lock owns intent/token data. Owners only inspect the atomic phase
// and acknowledgements; they never retain the HTTP caller's token/storage.
static uint64_t s_maintenance_epoch;
static uint32_t s_last_generation;
static atomic_bool s_stream_retry_pending;
static bool s_last_command_valid, s_maintenance_resume;

