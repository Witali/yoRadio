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

static int ws_wait(int socket, bool sending, int64_t deadline) {
    int64_t remaining = deadline - esp_timer_get_time();
    if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
    struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL),
        .tv_usec = (long)(remaining % 1000000LL)};
    fd_set ready_set;
    FD_ZERO(&ready_set);
    FD_SET(socket, &ready_set);
    int ready = lwip_select(socket + 1, sending ? NULL : &ready_set,
                           sending ? &ready_set : NULL, NULL, &wait);
    if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
    if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
    // Spurious readiness and EINTR must not spin the HTTPD task at full CPU.
    vTaskDelay(1);
    return ESP_OK;
}

static int ws_send_complete(httpd_handle_t server, int socket,
                            const char *data, size_t size, int flags) {
    ws_client_t *client = ws_session(server, socket);
    if (!client || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    // One deadline covers an application frame's header and payload. SDK
    // control replies get a separate finite fallback for each send call.
    int64_t deadline = client->send_deadline_us ? client->send_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t written = 0;
    while (written < size) {
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_send(server, socket,
            data + written, size - written, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - written) return HTTPD_SOCK_ERR_FAIL;
            written += (size_t)count;
            continue;
        }
        if (!count || (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR))
            return HTTPD_SOCK_ERR_FAIL;
        int result = ws_wait(socket, writable, deadline);
        if (result != ESP_OK) return result;
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)written;
}

static int ws_receive_complete(httpd_handle_t server, int socket,
                               char *data, size_t size, int flags) {
    ws_client_t *client = ws_session(server, socket);
    if (!client || size > INT_MAX) return HTTPD_SOCK_ERR_FAIL;
    int64_t deadline = client->receive_deadline_us ? client->receive_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t received = 0;
    while (received < size) {
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket,
            data + received, size - received, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - received) return HTTPD_SOCK_ERR_FAIL;
            received += (size_t)count;
            // A repeated peek returns the same prefix rather than advancing.
            if (flags & MSG_PEEK) break;
            continue;
        }
        if (!count) return 0;
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)
            return HTTPD_SOCK_ERR_FAIL;
        int result = ws_wait(socket, writable, deadline);
        if (result != ESP_OK) return result;
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)received;
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

static esp_err_t websocket_pre_handshake(httpd_req_t *request) {
    int socket = httpd_req_to_sockfd(request);
    if (socket < 0 || socket >= FD_SETSIZE ||
        httpd_sess_get_ctx(s_server, socket)) return ESP_FAIL;
    for (size_t i = 0; i < CONFIG_LWIP_MAX_SOCKETS; ++i) {
        ws_client_t *client = &s_clients[i];
        if (client->used) continue;
        *client = (ws_client_t){.used = true, .socket = socket};
        if (!websocket_message_init(&client->message, client->command,
                                     sizeof(client->command), WS_MESSAGE_BUDGET_US)) {
            memset(client, 0, sizeof(*client));
            return ESP_FAIL;
        }
        httpd_sess_set_ctx(s_server, socket, client, ws_session_free);
        if (httpd_sess_get_ctx(s_server, socket) != client) {
            memset(client, 0, sizeof(*client));
            return ESP_FAIL;
        }
        if (httpd_sess_set_send_override(s_server, socket, ws_send_complete) != ESP_OK ||
            httpd_sess_set_recv_override(s_server, socket, ws_receive_complete) != ESP_OK) {
            ws_fail_client(client);
            return ESP_FAIL;
        }
        return ESP_OK;
    }
    return ESP_ERR_NO_MEM;
}

static esp_err_t websocket_post_handshake(httpd_req_t *request) {
    return ws_session(s_server, httpd_req_to_sockfd(request)) ? ESP_OK : ESP_FAIL;
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

static esp_err_t ws_send_request(httpd_req_t *request, const char *text) {
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client || client->message.close_sent || client->message.close_received) return ESP_ERR_INVALID_STATE;
    if (!websocket_message_utf8_valid((const uint8_t *)text, strlen(text))) {
        (void)ws_close_client(client, 1011);
        return ESP_FAIL;
    }
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    client->send_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame(request, &frame);
    client->send_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    return result;
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

static esp_err_t websocket_handler_awake(httpd_req_t *request) {
    httpd_ws_frame_t frame = {0};
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, 0), TAG,
                        "read WebSocket frame size");
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client) return ESP_FAIL;
    if (frame.len > 255) {
        (void)ws_close_client(client, 1009);
        return ESP_FAIL;
    }
    char payload[256];
    frame.payload = (uint8_t *)payload;
    // IDF uses len==0 as its header-read sentinel, so an empty frame must not
    // enter the second read or it would consume the next frame's header.
    if (frame.len) {
        ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, sizeof(payload) - 1),
                            TAG, "read WebSocket frame");
    }
    bool was_active = client->message.active;
    websocket_message_result_t message = websocket_message_feed(&client->message,
        (uint8_t)frame.type, frame.final, (const uint8_t *)payload, frame.len,
        (uint64_t)esp_timer_get_time());
    ws_update_active(client, was_active);
    if (message.event == WEBSOCKET_MESSAGE_ERROR) {
        (void)ws_close_client(client, message.close_code);
        return ESP_FAIL;
    }
    if (message.event == WEBSOCKET_MESSAGE_PING)
        return ws_send_control(client, HTTPD_WS_TYPE_PONG, message.data, message.size);
    if (message.event == WEBSOCKET_MESSAGE_CLOSE) {
        esp_err_t result = ESP_OK;
        if (!client->message.close_sent) {
            result = ws_send_control(client, HTTPD_WS_TYPE_CLOSE, message.data, message.size);
            if (result == ESP_OK) websocket_message_mark_close_sent(&client->message);
        }
        ws_finish_client(client, result == ESP_OK);
        return result;
    }
    if (message.event == WEBSOCKET_MESSAGE_BINARY) {
        (void)ws_close_client(client, 1003);
        return ESP_FAIL;
    }
    if (message.event == WEBSOCKET_MESSAGE_TEXT && message.size) {
        if (memchr(message.data, 0, message.size))
            return ws_send_request(request, "{\"commandError\":\"Command contains NUL\"}");
        handle_command(request, (char *)client->command);
    }
    return ESP_OK;
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    // A successful upgrade is handled by pinned HTTPD before dispatch.
    if (request->method == HTTP_GET)
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "WebSocket upgrade required");
    if (!deep_sleep_clock_begin_activity()) return ESP_FAIL;
    ws_client_t *client = ws_session(s_server, httpd_req_to_sockfd(request));
    if (!client) {
        deep_sleep_clock_end_activity();
        return ESP_FAIL;
    }
    client->receive_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = websocket_handler_awake(request);
    client->receive_deadline_us = 0;
    if (result != ESP_OK) ws_fail_client(client);
    deep_sleep_clock_end_activity();
    return result;
}

esp_err_t websocket_service_register(httpd_handle_t server,
                                     native_state_t *state) {
    s_server = server;
    s_state = state;
    httpd_uri_t websocket = {
        .uri = "/ws",
        .method = HTTP_GET,
        .handler = websocket_handler,
        .is_websocket = true,
        .handle_ws_control_frames = true,
        .ws_pre_handshake_cb = websocket_pre_handshake,
        .ws_post_handshake_cb = websocket_post_handshake,
    };
    ESP_RETURN_ON_ERROR(httpd_register_uri_handler(server, &websocket), TAG,
                        "register native WebSocket route");
    ESP_RETURN_ON_FALSE(xTaskCreate(status_task, "websocket_status",
                                    BOARD_TASK_STACK_WEBSOCKET_STATUS,
                                    NULL, 2, NULL) == pdPASS,
                        ESP_ERR_NO_MEM, TAG, "start WebSocket status task");
    atomic_store(&s_reboot_ready, true);
    return ESP_OK;
}
