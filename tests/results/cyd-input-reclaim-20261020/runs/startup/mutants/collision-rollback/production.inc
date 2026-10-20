#define STREAM_CHUNK_SIZE 2048
#define DECODE_BUFFER_INITIAL 12288
#define ENCODED_RING_SIZE (16 * 1024)
#define PCM_RING_SIZE (8 * 1024)
#define PCM_PACKET_DATA_SIZE 3072
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
    uint32_t generation;
    uint32_t sample_rate;
    uint8_t bits_per_sample;
    uint8_t channels;
    uint16_t data_size;
    uint32_t end_of_stream;
    uint8_t data[];
} pcm_packet_t;

static const char *const TAG = "audio";
static native_state_t *s_state;
static QueueHandle_t s_commands;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
static adaptive_input_t *s_encoded;
#define encoded_acquire adaptive_input_acquire
static BaseType_t encoded_commit(adaptive_input_t *input, encoded_packet_t *packet) {
    return adaptive_input_commit_size(input, packet, sizeof(*packet) + packet->data_size);
}
#define encoded_receive adaptive_input_receive
#define encoded_return adaptive_input_return
#else
static RingbufHandle_t s_encoded;
#define encoded_acquire xRingbufferSendAcquire
#define encoded_commit xRingbufferSendComplete
#define encoded_receive xRingbufferReceive
#define encoded_return vRingbufferReturnItem
#endif
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
static bool s_encoded_control_attached;
#endif
static RingbufHandle_t s_pcm;
static atomic_uint s_generation;
static atomic_uint s_decoder_released_generation;
static atomic_uint s_failed_generation;
static SemaphoreHandle_t s_control_lock;
enum { AUDIO_START_OFF, AUDIO_STARTING, AUDIO_START_READY };
static atomic_uint s_start_state;
static uint8_t *s_stream_buffer;
// Output/LED initialization has process lifetime. Retain successful setup
// across pipeline-allocation retries instead of allocating driver buffers twice.
static bool s_output_initialized, s_led_initialized;

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
static play_command_t s_last_command;
static bool s_last_command_valid, s_maintenance_resume;

static bool maintenance_active(void) {
    return atomic_load(&s_maintenance_phase) != MAINTENANCE_OFF;
}

static bool maintenance_acked(unsigned bits) {
    return (atomic_load(&s_maintenance_acks) & bits) == bits;
}

// State lock is held. The caller has validated this maintenance generation.
static void maintenance_state_locked(uint32_t generation, bool quiet) {
    esp_err_t error = atomic_load(&s_maintenance_error);
    const char *status = error == ESP_ERR_TIMEOUT
        ? (quiet ? "maintenance timeout; cleanup complete" : "maintenance timeout; cleanup pending")
        : error != ESP_OK
        ? (quiet ? "maintenance failed; cleanup complete" : "maintenance failed; cleanup pending")
        : (quiet ? "maintenance paused" : "maintenance cleanup pending");
    native_state_begin_audio_locked(s_state, generation, NULL, status);
    s_state->audio_pending = !quiet;
    s_state->audio_failed = error != ESP_OK;
}

static void maintenance_publish_state(uint32_t generation, bool quiet,
                                       TickType_t timeout) {
    portENTER_CRITICAL(&s_maintenance_token_lock);
    uint64_t epoch = s_maintenance_epoch;
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    if (!maintenance_active() || generation != atomic_load(&s_generation) ||
        xSemaphoreTake(s_state->lock, timeout) != pdTRUE) return;
    portENTER_CRITICAL(&s_maintenance_token_lock);
    bool current = epoch == s_maintenance_epoch && maintenance_active() &&
                   generation == atomic_load(&s_generation);
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    // OFF publication also takes the state lock, so it cannot race this
    // recheck/write and leave a late cleanup status over resumed playback.
    if (current) maintenance_state_locked(generation, quiet);
    xSemaphoreGive(s_state->lock);
}

// All owners are quiescent before this runs, so the queued restore cannot be
// consumed until OFF is published. No blocking state/NVS/driver calls here.
static esp_err_t maintenance_finish_locked(bool resume) {
    if (xSemaphoreTake(s_state->lock, 0) != pdTRUE) return ESP_ERR_TIMEOUT;
    if (resume && s_maintenance_resume && s_last_command_valid) {
        play_command_t command = s_last_command;
        command.generation = atomic_load(&s_generation) + 1U;
        command.maintenance = false;
        command.restore = true;
        if (xQueueOverwrite(s_commands, &command) != pdTRUE) {
            xSemaphoreGive(s_state->lock);
            return ESP_FAIL;
        }
        maintenance_state_locked(atomic_load(&s_generation), true);
        // This is an accepted pending Play even before the stream owner
        // consumes it. A second maintenance must retain that resume intent.
        s_state->audio_generation = command.generation;
        s_state->audio_pending = true;
        s_state->audio_failed = false;
        const char *status = atomic_load(&s_maintenance_error) == ESP_ERR_TIMEOUT
            ? "maintenance timeout; resume pending"
            : atomic_load(&s_maintenance_error) != ESP_OK
            ? "maintenance failed; resume pending" : "maintenance resume pending";
        strlcpy(s_state->stream_format, status, sizeof(s_state->stream_format));
        atomic_store(&s_generation, command.generation);
        s_last_command = command;
        network_service_audio_accept(command.generation, true);
    } else {
        maintenance_state_locked(atomic_load(&s_generation), true);
        if (atomic_load(&s_maintenance_error) == ESP_OK)
            strlcpy(s_state->stream_format, "stopped", sizeof(s_state->stream_format));
    }
    native_audio_output_request_pause(false);
    portENTER_CRITICAL(&s_maintenance_token_lock);
    atomic_store(&s_maintenance_phase, MAINTENANCE_OFF);
    portEXIT_CRITICAL(&s_maintenance_token_lock);
    xSemaphoreGive(s_state->lock);
    return ESP_OK;
}

static void maintenance_try_abort(void) {
    unsigned phase = atomic_load(&s_maintenance_phase);
    if ((phase != MAINTENANCE_ABORTING && phase != MAINTENANCE_END_RESUME &&
         phase != MAINTENANCE_END_STOP) ||
        atomic_load(&s_maintenance_waiter) || !maintenance_acked(MAINTENANCE_ALL) ||
        xSemaphoreTake(s_control_lock, 0) != pdTRUE) return;
    phase = atomic_load(&s_maintenance_phase);
    if ((phase == MAINTENANCE_ABORTING || phase == MAINTENANCE_END_RESUME ||
         phase == MAINTENANCE_END_STOP) && !atomic_load(&s_maintenance_waiter) &&
        maintenance_acked(MAINTENANCE_ALL))
        (void)maintenance_finish_locked(phase != MAINTENANCE_END_STOP);
    xSemaphoreGive(s_control_lock);
}

static void maintenance_ack(unsigned bit) {
    atomic_fetch_or(&s_maintenance_acks, bit);
    maintenance_try_abort();
}

static void maintenance_park(uint32_t generation) {
    // A subsequent maintenance can start before a parked owner observes OFF.
    // The new generation must make that owner leave and acknowledge anew.
    while (maintenance_active() && atomic_load(&s_generation) == generation) {
        maintenance_try_abort();
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

static void maintenance_output_error(esp_err_t result) {
    int expected = ESP_OK;
    atomic_compare_exchange_strong(&s_maintenance_error, &expected, result);
    unsigned phase = MAINTENANCE_REQUESTED;
    atomic_compare_exchange_strong(&s_maintenance_phase, &phase, MAINTENANCE_ABORTING);
}

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

typedef struct {
    TaskFunction_t run;
    const char *name;
    uint32_t stack_size;
    UBaseType_t priority;
    BaseType_t core;
} pipeline_task_t;

static void gated_pipeline_task(void *argument) {
    const pipeline_task_t *task = argument;
    // A task may run immediately on either core after creation. Until notified
    // it owns no pipeline resources, so failed startup can safely delete it.
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    task->run(NULL);
    vTaskDelete(NULL);
}

static void discard_pipeline_startup(TaskHandle_t *tasks, bool codecs_registered) {
    for (unsigned i = 0; i < 3; ++i) {
        if (tasks[i]) vTaskDelete(tasks[i]);
    }
    if (s_pcm) vRingbufferDelete(s_pcm);
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    if (s_encoded) adaptive_input_destroy(s_encoded);
#else
    if (s_encoded) vRingbufferDelete(s_encoded);
#endif
    if (s_commands) vQueueDelete(s_commands);
    if (s_control_lock) vSemaphoreDelete(s_control_lock);
    free(s_stream_buffer);
    s_pcm = NULL;
    s_encoded = NULL;
    s_commands = NULL;
    s_control_lock = NULL;
    s_stream_buffer = NULL;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    s_start_control_attached = s_encoded_control_attached = false;
#endif
    if (codecs_registered) decoder_unregister_codecs();
    s_state = NULL;
    // Last publication: readers seeing OFF cannot observe freed resources.
    atomic_store(&s_start_state, AUDIO_START_OFF);
}

esp_err_t audio_service_start(native_state_t *state) {
    if (!state || !state->lock) return ESP_ERR_INVALID_ARG;
    unsigned expected = AUDIO_START_OFF;
    if (!atomic_compare_exchange_strong(&s_start_state, &expected, AUDIO_STARTING))
        return ESP_ERR_INVALID_STATE;
    static const pipeline_task_t task_config[3] = {
        {stream_task, "radio_stream", BOARD_TASK_STACK_RADIO_STREAM, 3, 0},
        {decoder_task, "audio_decode", BOARD_TASK_STACK_AUDIO_DECODER, 5, 1},
        {output_task, "audio_output", BOARD_TASK_STACK_AUDIO_OUTPUT, 6, 1},
    };
    TaskHandle_t tasks[3] = {NULL};
    bool codecs_registered = false;
    esp_err_t result = ESP_ERR_NO_MEM;
    s_state = state;
    atomic_init(&s_generation, 0);
    atomic_init(&s_decoder_released_generation, 0);
    atomic_init(&s_failed_generation, 0);
    s_stream_buffer = malloc(STREAM_CHUNK_SIZE);
    if (!s_stream_buffer) goto failed;
    s_control_lock = xSemaphoreCreateMutex();
    if (!s_control_lock) goto failed;
    s_commands = xQueueCreate(1, sizeof(play_command_t));
    if (!s_commands) goto failed;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    s_encoded = adaptive_input_create(ENCODED_RING_SIZE,
        4 * (sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE),
        sizeof(encoded_packet_t) + STREAM_CHUNK_SIZE);
#else
    s_encoded = xRingbufferCreate(ENCODED_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
#endif
    if (!s_encoded) goto failed;
    s_pcm = xRingbufferCreate(PCM_RING_SIZE, RINGBUF_TYPE_NOSPLIT);
    if (!s_pcm) goto failed;
#ifdef CONFIG_YORADIO_STREAM_CONFIRM
    if (!adaptive_input_attach_control(s_encoded, s_start_control, sizeof(s_start_control)))
        goto failed;
    s_start_control_attached = s_encoded_control_attached = true;
#endif
    esp_audio_err_t registration = decoder_register_codecs();
    if (registration != ESP_AUDIO_ERR_OK) {
        ESP_LOGE(TAG, "Decoder registration failed: %d", registration);
        result = registration == ESP_AUDIO_ERR_MEM_LACK ? ESP_ERR_NO_MEM : ESP_FAIL;
        goto failed;
    }
    codecs_registered = true;
    for (unsigned i = 0; i < 3; ++i) {
        if (xTaskCreatePinnedToCore(gated_pipeline_task, task_config[i].name,
                task_config[i].stack_size, (void *)&task_config[i], task_config[i].priority,
                &tasks[i], task_config[i].core) != pdPASS) goto failed;
    }
    if (!s_output_initialized) {
        result = native_audio_output_init();
        if (result != ESP_OK) goto failed;
        s_output_initialized = true;
    }
    if (!s_led_initialized) {
        result = audio_level_led_init();
        if (result != ESP_OK) goto failed;
        s_led_initialized = true;
    }
    native_health_track_task(NATIVE_HEALTH_STREAM, tasks[0]);
    native_health_track_task(NATIVE_HEALTH_DECODE, tasks[1]);
    native_health_track_task(NATIVE_HEALTH_OUTPUT, tasks[2]);
    atomic_store(&s_start_state, AUDIO_START_READY);
#ifdef CONFIG_YORADIO_TLS_INPUT_RECLAIM
    // All fallible startup work has committed. A rejected optional binding
    // must not roll back READY or destroy a pool published to another task.
    if (!native_input_reclaim_bind(s_encoded))
        { ESP_LOGW(TAG, "TLS input reclamation not attached"); result=ESP_FAIL; goto failed; }
#endif
    for (unsigned i = 0; i < 3; ++i) xTaskNotifyGive(tasks[i]);
    ESP_LOGI(TAG,
             "Pipeline ready: %s, 16 KiB compressed + 8 KiB PCM, free heap %u",
             native_audio_output_name(),
             (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT));
    return ESP_OK;
failed:
    discard_pipeline_startup(tasks, codecs_registered);
    return result;
}

esp_err_t audio_service_play(const char *url, native_codec_t codec) {
    if (!url || !url[0] || strlen(url) >= sizeof(((play_command_t *)0)->url)) {
        return ESP_ERR_INVALID_ARG;
    }
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return ESP_ERR_INVALID_STATE;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        xSemaphoreGive(s_control_lock);
        return ESP_ERR_INVALID_STATE;
    }
    play_command_t command = {
        .generation = atomic_fetch_add(&s_generation, 1) + 1,
        .requested_codec = codec,
    };
    network_service_audio_accept(command.generation, true);
    strlcpy(command.url, url, sizeof(command.url));
    native_state_begin_audio(s_state, command.generation, url, "connecting");
    native_state_set_connecting(s_state, command.generation);
    esp_err_t result = xQueueOverwrite(s_commands, &command) == pdTRUE
                         ? ESP_OK : ESP_FAIL;
    s_last_command_valid = result == ESP_OK;
    if (s_last_command_valid) s_last_command = command;
    if (result != ESP_OK) {
        native_state_set_audio(s_state, command.generation, false, "command failed");
        network_service_audio_finish(command.generation);
    }
    xSemaphoreGive(s_control_lock);
    return result;
}

void audio_service_stop(void) {
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return;
    xSemaphoreTake(s_control_lock, portMAX_DELAY);
    if (maintenance_active()) {
        s_maintenance_resume = false;
        xSemaphoreGive(s_control_lock);
        return;
    }
    uint32_t generation = atomic_fetch_add(&s_generation, 1) + 1;
    network_service_audio_accept(generation, false);
    native_state_begin_audio(s_state, generation, NULL, "stopped");
    xSemaphoreGive(s_control_lock);
}

native_input_health_t audio_service_input_health(void) {
    native_input_health_t result = {0};
    if (atomic_load(&s_start_state) != AUDIO_START_READY) return result;
#ifdef CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER
    result.leased = true;
    if (s_encoded) {
        adaptive_input_stats_t stats = adaptive_input_stats(s_encoded);
        result.available = true;
        result.resident=stats.resident; result.minimum=stats.minimum;
        result.target=stats.target; result.limit=stats.limit;
        result.ready=stats.ready; result.reading=stats.reading;
        result.writing=stats.writing; result.released=stats.released;
        size_t ready_headers=(size_t)stats.ready*sizeof(encoded_packet_t);
        size_t reading_headers=(size_t)stats.reading*sizeof(encoded_packet_t);
        result.ready_payload_bytes=(uint32_t)(stats.ready_bytes>=ready_headers
            ? stats.ready_bytes-ready_headers : 0);
        result.reading_payload_bytes=(uint32_t)(stats.reading_bytes>=reading_headers
            ? stats.reading_bytes-reading_headers : 0);
    }
#endif
    return result;
}
