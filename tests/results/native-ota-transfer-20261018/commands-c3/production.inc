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


static bool maintenance_active(void) {
    return atomic_load(&s_maintenance_phase) != MAINTENANCE_OFF;
}

static uint32_t advance_generation(native_codec_t target_codec) {
    portENTER_CRITICAL(&s_generation_lock);
    uint32_t generation = atomic_load(&s_generation) + 1U;
    // Publish the target first. Once the decoder observes the new generation,
    // it can release an incompatible arena before the stream allocates TLS.
    atomic_store(&s_decoder_target_codec, (unsigned)target_codec);
    atomic_store(&s_generation, generation);
    portEXIT_CRITICAL(&s_generation_lock);
    native_state_begin_stream(s_state, generation);
    return generation;
}

static void state_set_audio(uint32_t generation, bool running,
                             const char *format) {
    native_state_set_audio(s_state, generation, running, format);
}

static esp_err_t play_locked(const char *url, native_codec_t codec) {
    if (maintenance_active()) return ESP_ERR_INVALID_STATE;
    // Power-save changes are best effort: a transient Wi-Fi driver error must
    // not reject an otherwise valid Play command.
    network_service_set_streaming(true);
    play_command_t command = {
        .generation = advance_generation(codec),
        .requested_codec = codec,
    };
    strlcpy(command.url, url, sizeof(command.url));
    strlcpy(s_last_url, url, sizeof(s_last_url));
    s_last_codec = codec;
    native_state_set_station(s_state, url);
    // Clear a previous station's playing state before the command is queued.
    // The stream task switches it back after open_stream() succeeds.
    native_state_set_connecting(s_state, command.generation);
    if (xQueueOverwrite(s_commands, &command) == pdTRUE) {
        s_last_command_valid = true;
        s_last_generation = command.generation;
        return ESP_OK;
    }
    s_last_command_valid = false;
    if (atomic_load(&s_generation) == command.generation) {
        state_set_audio(command.generation, false, "command failed");
        network_service_set_streaming(false);
    }
    return ESP_FAIL;
}

esp_err_t audio_service_play(const char *url, native_codec_t codec) {
    if (!url || !url[0] || strlen(url) >= sizeof(((play_command_t *)0)->url))
        return ESP_ERR_INVALID_ARG;
    if (!s_control_lock || !s_commands) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    esp_err_t result = play_locked(url, codec);
    xSemaphoreGive(s_control_lock);
    return result;
}

esp_err_t audio_service_resume(void) {
    if (!s_control_lock || !s_commands) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_INVALID_STATE;
    }
    if (!s_last_url[0]) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_INVALID_STATE;
    }
    char url[sizeof(s_last_url)];
    native_state_t state;
    native_state_snapshot(s_state, &state);
    strlcpy(url, s_last_url, sizeof(url));
    esp_err_t result = play_locked(url, s_last_codec);
    if (result == ESP_OK) native_state_set_station(s_state, state.station);
    xSemaphoreGive(s_control_lock);
    return result;
}

void audio_service_stop(void) {
    if (!s_control_lock) return;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        s_maintenance_resume = false;
        xSemaphoreGive(s_control_lock);
        return;
    }
    uint32_t generation = advance_generation(NATIVE_CODEC_AUTO);
    network_service_set_streaming(false);
    // advance_generation clears the title under the state mutex. A separate
    // unguarded clear here could erase metadata from a concurrent newer Play.
    state_set_audio(generation, false, "stopped");
    xSemaphoreGive(s_control_lock);
}
