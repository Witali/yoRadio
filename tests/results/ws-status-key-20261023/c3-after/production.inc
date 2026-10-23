#define WS_STATUS_POLL_MS 100
#define WS_STATUS_HEARTBEAT_MS 2000
#define WS_FRAME_BUDGET_US 1000000LL
#define WS_MESSAGE_BUDGET_US 5000000ULL

#if !CONFIG_HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT
#error "Native WebSocket transport requires the public post-handshake callback"
#endif
#if !CONFIG_HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT
#error "Native WebSocket transport requires the public pre-handshake callback"
#endif
#if CONFIG_HTTPD_QUEUE_WORK_BLOCKING
#error "Native WebSocket publication requires non-blocking HTTPD work admission"
#endif

static const char *const TAG = "websocket";
static httpd_handle_t s_server;
static native_state_t *s_state;

typedef struct {
    bool audio_running;
    uint8_t volume;
    int8_t balance;
    uint32_t bitrate_kbps;
    uint32_t sample_rate_hz;
    uint8_t channels;
    uint8_t bits_per_sample;
    uint32_t pcm_sample_rate_hz;
    uint8_t pcm_channels;
    uint16_t current_item;
    bool station_uppercase;
    char station[144];
    char title[192];
    char codec[16];
    char stream_format[48];
} webui_status_key_t;

// Keep persistent broadcast workspace in BSS so the board-configured task
// stack remains headroom for nested HTTP/WebSocket calls.
static char s_broadcast_status[1280];
static char s_broadcast_current[48];
static webui_status_key_t s_previous_status_key;
static webui_status_key_t s_current_status_key;
static atomic_bool s_playlist_changed_pending;
static atomic_uint s_status_send_pending;
static atomic_uint s_current_send_pending;
static atomic_size_t s_last_ws_clients;
static atomic_uint s_completed_deliveries;

typedef struct {
    bool used, closing;
    int socket;
    int64_t send_deadline_us, receive_deadline_us;
    websocket_message_t message;
    uint8_t command[256];
} ws_client_t;

// Only the HTTPD task accesses session storage. The public free callback clears
// it before the fd can be reused; queued broadcasts capture no session or fd.
static ws_client_t s_clients[CONFIG_LWIP_MAX_SOCKETS];
static atomic_uint s_fragmented_clients;
static atomic_bool s_message_poll_pending;

static void ws_update_active(ws_client_t *client, bool was_active) {
    if (was_active && !client->message.active) atomic_fetch_sub(&s_fragmented_clients, 1U);
    else if (!was_active && client->message.active) atomic_fetch_add(&s_fragmented_clients, 1U);
}

static void ws_session_free(void *context) {
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        if (context == &s_clients[i]) {
            if (s_clients[i].message.active) atomic_fetch_sub(&s_fragmented_clients, 1U);
            memset(&s_clients[i], 0, sizeof(s_clients[i]));
            break;
        }
    }
}

static ws_client_t *ws_session(httpd_handle_t server, int socket) {
    if (server != s_server || socket < 0 || socket >= FD_SETSIZE) return NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (context == client && client->used && !client->closing &&
            client->socket == socket) return client;
    }
    return NULL;
}

static void ws_finish_client(ws_client_t *client, bool graceful) {
    if (!client || ws_session(s_server, client->socket) != client) return;
    client->closing = true;
    bool was_active = client->message.active;
    client->message.active = false;
    client->message.used = 0;
    ws_update_active(client, was_active);
    // HTTPD retains ownership of close(). No deferred fd-only close may affect
    // a replacement session that later receives the same descriptor.
    native_web_transport_shutdown(s_server, client->socket, graceful);
}

static void ws_fail_client(ws_client_t *client) {
    ws_finish_client(client, false);
}

static esp_err_t ws_send_control(ws_client_t *client, httpd_ws_type_t type,
                                 const uint8_t *payload, size_t size) {
    if (!client || ws_session(s_server, client->socket) != client) return ESP_ERR_INVALID_STATE;
    httpd_ws_frame_t frame = {.final = true, .type = type,
        .payload = (uint8_t *)payload, .len = size};
    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->send_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    return result;
}

static esp_err_t ws_close_client(ws_client_t *client, uint16_t code) {
    if (!client || ws_session(s_server, client->socket) != client) return ESP_FAIL;
    esp_err_t result = ESP_OK;
    if (!client->message.close_sent) {
        bool was_active = client->message.active;
        uint8_t payload[2] = {(uint8_t)(code >> 8U), (uint8_t)code};
        result = ws_send_control(client, HTTPD_WS_TYPE_CLOSE, payload, sizeof(payload));
        if (result == ESP_OK) {
            websocket_message_mark_close_sent(&client->message);
            ws_update_active(client, was_active);
        }
    }
    ws_fail_client(client);
    return result;
}

static void message_deadline_work(void *argument) {
    (void)argument;
    uint64_t now = (uint64_t)esp_timer_get_time();
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (!client->message.active || ws_session(s_server, client->socket) != client) continue;
        websocket_message_result_t result = websocket_message_expire(&client->message, now);
        ws_update_active(client, true);
        if (result.event == WEBSOCKET_MESSAGE_ERROR) (void)ws_close_client(client, result.close_code);
    }
    atomic_store(&s_message_poll_pending, false);
}

static void poll_message_deadlines(void) {
    bool expected = false;
    if (!atomic_load(&s_fragmented_clients) ||
        !atomic_compare_exchange_strong(&s_message_poll_pending, &expected, true)) return;
    if (httpd_queue_work(s_server, message_deadline_work, NULL) != ESP_OK)
        atomic_store(&s_message_poll_pending, false);
}

static void json_escape(const char *source, char *target, size_t target_size) {
    if (!target_size) return;
    json_buffer_t out;
    json_buffer_init(&out, target, target_size);
    json_buffer_string(&out, source);
    // The shared encoder appends whole escapes/UTF-8 sequences atomically.
    // Preserve its bounded valid prefix even when the complete field did not
    // fit, removing the quotes supplied separately by these legacy JSON forms.
    size_t length = out.length ? out.length - 1U : 0U;
    if (!out.failed && length) --length;
    if (length) memmove(target, target + 1, length);
    target[length] = '\0';
}

typedef struct {
    atomic_bool busy;
    const char *text;
    atomic_uint *pending;
} ws_broadcast_work_t;

static ws_broadcast_work_t s_status_work, s_current_work, s_playlist_work;

static void broadcast_work(void *argument) {
    ws_broadcast_work_t *work = argument;
    size_t count = CONFIG_LWIP_MAX_SOCKETS;
    int sockets[CONFIG_LWIP_MAX_SOCKETS];
    size_t clients = 0;
    if (httpd_get_client_list(s_server, &count, sockets) == ESP_OK) {
        for (size_t index = 0; index < count; ++index) {
            if (httpd_ws_get_fd_info(s_server, sockets[index]) ==
                HTTPD_WS_CLIENT_WEBSOCKET) {
                ++clients;
                ws_client_t *client = ws_session(s_server, sockets[index]);
                if (client && !client->message.close_sent && !client->message.close_received) {
                    if (!websocket_message_utf8_valid((const uint8_t *)work->text, strlen(work->text))) {
                        (void)ws_close_client(client, 1011);
                        continue;
                    }
                    httpd_ws_frame_t frame = {.final = true,
                        .type = HTTPD_WS_TYPE_TEXT, .payload = (uint8_t *)work->text,
                        .len = strlen(work->text)};
                    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
                    esp_err_t result = httpd_ws_send_frame_async(s_server, sockets[index], &frame);
                    client->send_deadline_us = 0;
                    if (result != ESP_OK) ws_fail_client(client);
                    else atomic_fetch_add(&s_completed_deliveries, 1U);
                }
            }
        }
    }
    atomic_store(&s_last_ws_clients, clients);
    atomic_fetch_sub(work->pending, 1U);
    atomic_store(&work->busy, false);
}

static bool broadcast_text(const char *text, atomic_uint *pending,
                            ws_broadcast_work_t *work) {
    if (!s_server || !text || !pending) return false;
    bool expected = false;
    if (!atomic_compare_exchange_strong(&work->busy, &expected, true)) return false;
    work->text = text;
    work->pending = pending;
    atomic_fetch_add(pending, 1U);
    if (httpd_queue_work(s_server, broadcast_work, work) == ESP_OK) return true;
    atomic_fetch_sub(pending, 1U);
    atomic_store(&work->busy, false);
    return false;
}

static void format_status(char *output, size_t output_size) {
    native_state_t state;
    native_state_snapshot(s_state, &state);
    char name[300];
    char title[400];
    char format[120];
    char current_name[144];
    radio_control_current_name(current_name, sizeof(current_name));
    json_escape(current_name, name, sizeof(name));
    json_escape(state.title, title, sizeof(title));
    json_escape(state.stream_format, format, sizeof(format));
    snprintf(output, output_size,
             "{\"payload\":[{\"id\":\"nameset\",\"value\":\"%s\"},"
             "{\"id\":\"meta\",\"value\":\"%s\"},"
             "{\"id\":\"volume\",\"value\":%u},"
             "{\"id\":\"balance\",\"value\":%d},"
             "{\"id\":\"rssi\",\"value\":%d},"
             "{\"id\":\"heap\",\"value\":%u},"
             "{\"id\":\"bitrate\",\"value\":%lu},"
             "{\"id\":\"fmt\",\"value\":\"%s\"},"
             "{\"id\":\"upst\",\"value\":%u},"
             "{\"id\":\"playerwrap\",\"value\":\"%s\"}]}",
             name, title, native_audio_output_get_volume(),
             native_audio_output_get_balance(), state.wifi_rssi,
             (unsigned)(state.audio_running
                            ? audio_service_buffer_fill_percent()
                            : 0U),
             (unsigned long)state.bitrate_kbps, format,
             display_settings_get_station_uppercase() ? 1U : 0U,
             state.audio_running ? "playing" : "stopped");
}

static void capture_status_key(webui_status_key_t *key) {
    native_state_t state;
    memset(key, 0, sizeof(*key));
    native_state_snapshot(s_state, &state);
    key->audio_running = state.audio_running;
    key->volume = native_audio_output_get_volume();
    key->balance = native_audio_output_get_balance();
    key->bitrate_kbps = state.bitrate_kbps;
    key->sample_rate_hz = state.sample_rate_hz;
    key->channels = state.channels;
    key->bits_per_sample = state.bits_per_sample;
    key->pcm_sample_rate_hz = state.pcm_sample_rate_hz;
    key->pcm_channels = state.pcm_channels;
    key->current_item = radio_control_current_item();
    key->station_uppercase = display_settings_get_station_uppercase();
    radio_control_current_name(key->station, sizeof(key->station));
    strlcpy(key->title, state.title, sizeof(key->title));
    strlcpy(key->codec, state.codec, sizeof(key->codec));
    strlcpy(key->stream_format, state.stream_format,
            sizeof(key->stream_format));
}

static bool status_keys_equal(const webui_status_key_t *left,
                              const webui_status_key_t *right) {
    // Structure assignments need not preserve padding. Compare the logical
    // strings too, so bytes beyond their terminating NUL do not trigger work.
    return left->audio_running == right->audio_running &&
           left->volume == right->volume &&
           left->balance == right->balance &&
           left->bitrate_kbps == right->bitrate_kbps &&
           left->sample_rate_hz == right->sample_rate_hz &&
           left->channels == right->channels &&
           left->bits_per_sample == right->bits_per_sample &&
           left->pcm_sample_rate_hz == right->pcm_sample_rate_hz &&
           left->pcm_channels == right->pcm_channels &&
           left->current_item == right->current_item &&
           left->station_uppercase == right->station_uppercase &&
           strcmp(left->station, right->station) == 0 &&
           strcmp(left->title, right->title) == 0 &&
           strcmp(left->codec, right->codec) == 0 &&
           strcmp(left->stream_format, right->stream_format) == 0;
}

typedef struct {
    int64_t started_us;
    uint64_t active_us;
    uint32_t polls;
    uint32_t publications;
    uint32_t deliveries;
} ws_profile_t;

static void profile_status_cycle(ws_profile_t *profile, int64_t cycle_started_us,
                                 uint32_t publications,
                                 uint32_t deliveries) {
    int64_t now_us = esp_timer_get_time();
    if (!profile->started_us) profile->started_us = cycle_started_us;
    profile->active_us += (uint64_t)(now_us - cycle_started_us);
    ++profile->polls;
    profile->publications += publications;
    profile->deliveries += deliveries;
    uint64_t window_us = (uint64_t)(now_us - profile->started_us);
    if (window_us < 5000000ULL) return;
    uint64_t tenths = profile->active_us * 1000ULL / window_us;
    ESP_LOGI(TAG,
             "PERF WS: active %llu us (%llu.%llu%%), polls %lu, "
             "publications %lu, deliveries %lu, clients %u",
             (unsigned long long)profile->active_us,
             (unsigned long long)(tenths / 10ULL),
             (unsigned long long)(tenths % 10ULL),
             (unsigned long)profile->polls,
             (unsigned long)profile->publications,
             (unsigned long)profile->deliveries,
             (unsigned)atomic_load(&s_last_ws_clients));
    memset(profile, 0, sizeof(*profile));
    profile->started_us = now_us;
}

static void status_task(void *argument) {
    (void)argument;
    bool have_previous = false;
    TickType_t last_sent = 0;
    ws_profile_t profile = {0};
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(WS_STATUS_POLL_MS));
        int64_t cycle_started_us = esp_timer_get_time();
        poll_reboot();
        web_tcp_probe_poll();
        poll_message_deadlines();
        uint32_t publications = 0;
        uint32_t deliveries = atomic_exchange(&s_completed_deliveries, 0U);
        capture_status_key(&s_current_status_key);
        TickType_t now = xTaskGetTickCount();
        bool changed = !have_previous ||
                       !status_keys_equal(&s_current_status_key,
                                          &s_previous_status_key);
        bool heartbeat = !last_sent ||
                         now - last_sent >=
                             pdMS_TO_TICKS(WS_STATUS_HEARTBEAT_MS);
        if (atomic_exchange(&s_playlist_changed_pending, false)) {
            ESP_LOGI(TAG, "Broadcasting playlist changed event");
            if (!broadcast_text(
                "{\"file\":\"/data/playlist.csv\"}",
                &s_status_send_pending, &s_playlist_work)) {
                atomic_store(&s_playlist_changed_pending, true);
            } else ++publications;
        }
        if ((changed || heartbeat) &&
            atomic_load(&s_status_send_pending) == 0U) {
            bool station_changed = !have_previous ||
                                   s_current_status_key.current_item !=
                                       s_previous_status_key.current_item;
            format_status(s_broadcast_status, sizeof(s_broadcast_status));
            bool publish_current = station_changed &&
                atomic_load(&s_current_send_pending) == 0U;
            if (publish_current) {
                snprintf(s_broadcast_current, sizeof(s_broadcast_current),
                         "{\"current\":%u}",
                         s_current_status_key.current_item);
            }
            bool status_queued = broadcast_text(
                s_broadcast_status, &s_status_send_pending, &s_status_work);
            if (status_queued) ++publications;
            bool current_queued = !station_changed;
            if (publish_current) {
                current_queued = broadcast_text(
                    s_broadcast_current, &s_current_send_pending, &s_current_work);
                if (current_queued) ++publications;
            }
            if (status_queued && current_queued) {
                s_previous_status_key = s_current_status_key;
                have_previous = true;
                last_sent = now;
            }
        }
        profile_status_cycle(&profile, cycle_started_us, publications,
                             deliveries);
    }
}

void websocket_service_notify_playlist_changed(void) {
    atomic_store(&s_playlist_changed_pending, true);
}

