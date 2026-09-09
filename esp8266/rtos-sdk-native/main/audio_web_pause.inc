/* Included after the command queue, generation and codec ownership helpers.
 * No task suspension, extra task/stack, URL copy or dynamically allocated state. */
#if YORADIO_ESP8266_WEB_AUDIO_PAUSE == 2
static bool s_web_pause_request, s_web_pause_hold, s_web_pause_ack;
static TickType_t s_web_pause_ended;

/* Caller holds the critical section. Unsigned elapsed time handles tick wrap. */
static bool web_pause_wanted_locked(void) {
    if (s_web_pause_hold &&
        (TickType_t)(xTaskGetTickCount() - s_web_pause_ended) >=
        pdMS_TO_TICKS(WEB_AUDIO_PAUSE_HOLD_MS))
        s_web_pause_hold = false;
    return s_web_pause_request || s_web_pause_hold;
}

static bool audio_web_pause_requested(void) {
    taskENTER_CRITICAL();
    bool wanted = web_pause_wanted_locked();
    taskEXIT_CRITICAL();
    return wanted;
}

esp_err_t audio_service_web_pause_begin(void) {
    if (!s_commands) return ESP_ERR_INVALID_STATE;
    taskENTER_CRITICAL();
    s_web_pause_request = true;
    taskEXIT_CRITICAL();
    TickType_t started = xTaskGetTickCount();
    for (;;) {
        taskENTER_CRITICAL();
        bool ready = s_web_pause_ack;
        taskEXIT_CRITICAL();
        if (ready) return ESP_OK;
        if ((TickType_t)(xTaskGetTickCount() - started) >=
            pdMS_TO_TICKS(WEB_AUDIO_PAUSE_ACK_MS)) {
            taskENTER_CRITICAL();
            s_web_pause_request = s_web_pause_hold = false;
            taskEXIT_CRITICAL();
            return ESP_ERR_TIMEOUT;
        }
        vTaskDelay(1); /* Let the audio owner finish its current operation. */
    }
}

void audio_service_web_pause_end(void) {
    taskENTER_CRITICAL();
    s_web_pause_ended = xTaskGetTickCount();
    s_web_pause_hold = true;
    s_web_pause_request = false;
    taskEXIT_CRITICAL();
}

static void audio_web_pause_gate(helix_codec_t **codec,
                                 helix_codec_kind_t *kind) {
    if (!audio_web_pause_requested()) return;
    native_audio_output_silence();
    release_codec(codec, kind, "WebUI pause");
    for (;;) {
        taskENTER_CRITICAL();
        bool wanted = web_pause_wanted_locked();
        /* Only this owner can acknowledge that socket/decoder are released. */
        s_web_pause_ack = wanted;
        taskEXIT_CRITICAL();
        if (!wanted) break;
        vTaskDelay(1);
    }
}

static bool audio_web_pause_checkpoint(http_stream_t *stream,
                                        const audio_command_t *command) {
    if (!audio_web_pause_requested()) return false;
    if (stream->socket >= 0) {
        close(stream->socket);
        stream->socket = -1;
    }
    if (generation_current(command->generation))
        native_state_set_audio(false, true, NULL);
    /* Stop/Next/Play win over a resume, including a concurrent queue update.
     * The existing command queue retains the URL; no second URL buffer. */
    requeue_if_current(command);
    return true;
}
#define AUDIO_WEB_QUEUE_WAIT pdMS_TO_TICKS(WEB_AUDIO_PAUSE_IDLE_POLL_MS)
#else
esp_err_t audio_service_web_pause_begin(void) { return ESP_OK; }
void audio_service_web_pause_end(void) {}
#define audio_web_pause_requested() false
#define audio_web_pause_gate(codec, kind) ((void)0)
#define audio_web_pause_checkpoint(stream, command) false
#define AUDIO_WEB_QUEUE_WAIT portMAX_DELAY
#endif
