#define WS_CLIENT_LIMIT 2U
#define WS_COMMAND_LIMIT 96U
#define WS_STATUS_BYTES 5120U
#define WS_POLL_MS 100U
#define WS_HEARTBEAT_US 2000000LL
#define WS_TASK_STACK 2048U
#define WS_FRAME_BUDGET_US 1000000LL
#define WS_MESSAGE_BUDGET_US 5000000ULL

typedef struct {
    bool used, closing, initialized;
    int socket;
    uint32_t status_revision, playlist_revision;
    uint16_t item;
    int64_t sent_us;
    int64_t frame_deadline_us;
    int64_t receive_deadline_us;
    websocket_message_t message;
    uint8_t command[WS_COMMAND_LIMIT + 1U];
} ws_client_t;

typedef struct {
    uint32_t generation, bitrate;
    uint16_t item, count;
    uint8_t volume, fill;
    int8_t balance, rssi;
    bool running, pending, smartstart, normalization;
    uint8_t normgain;
    int8_t normtarget;
    uint16_t normtime;
    char station[96], name[144], title[192], format[48];
} ws_status_key_t;

static httpd_handle_t s_server;
static native_state_t *s_state;
static atomic_bool s_running, s_task_alive, s_work_pending;
static atomic_uint s_playlist_revision;
// Only the HTTPD task touches these objects. Queued work contains no payload or
// captured fd, and every send completes before this workspace is reused.
static ws_client_t s_clients[WS_CLIENT_LIMIT];
static ws_status_key_t s_previous, s_current;
static bool s_have_previous;
static uint32_t s_status_revision;
static char s_status[WS_STATUS_BYTES];
static int s_sockets[CONFIG_LWIP_MAX_SOCKETS];


static esp_err_t handle_command(ws_client_t *,char *);
static esp_err_t send_status(ws_client_t *,bool);
static void session_free(void *context) {
    ws_client_t *client = context;
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (client == &s_clients[i]) {
            memset(client, 0, sizeof(*client));
            break;
        }
    }
}
static bool current_client(const ws_client_t *client) {
    return client && client->used && !client->closing &&
        httpd_sess_get_ctx(s_server, client->socket) == client;
}
static int send_complete_frame_bytes(httpd_handle_t server, int socket, const char *data, size_t size, int flags) {
    ws_client_t *client = NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) if (context == &s_clients[i]) client = &s_clients[i];
    if (!client || !current_client(client)) return HTTPD_SOCK_ERR_FAIL;
    // Application frames share one deadline across IDF's header and payload
    // writes. SDK-generated PONG/CLOSE writes each get a finite fallback budget.
    int64_t deadline = client->frame_deadline_us ? client->frame_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t written = 0;
    while (written < size) {
        if (!atomic_load(&s_running)) return HTTPD_SOCK_ERR_FAIL;
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t sent = native_web_transport_send(server, socket,
            data + written, size - written, flags | MSG_DONTWAIT, &writable);
        if (sent > 0) {
            if ((size_t)sent > size - written) return HTTPD_SOCK_ERR_FAIL;
            written += (size_t)sent;
            continue;
        }
        if (!sent || (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR)) return HTTPD_SOCK_ERR_FAIL;
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
        struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL), .tv_usec = (long)(remaining % 1000000LL)};
        fd_set writable_set;
        FD_ZERO(&writable_set); FD_SET(socket, &writable_set);
        // Use lwIP directly: CYD intentionally has CONFIG_VFS_SUPPORT_SELECT=n.
        int ready = lwip_select(socket + 1, writable ? NULL : &writable_set,
                               writable ? &writable_set : NULL, NULL, &wait);
        if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
        if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        // Yield after no progress, including spurious readiness/EINTR, so a slow
        // peer cannot turn the HTTPD task into a one-second CPU spin.
        vTaskDelay(1);
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)written;
}
static int receive_complete_frame_bytes(httpd_handle_t server, int socket, char *data, size_t size, int flags) {
    ws_client_t *client = NULL;
    void *context = httpd_sess_get_ctx(server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) if (context == &s_clients[i]) client = &s_clients[i];
    if (!client || !current_client(client)) return HTTPD_SOCK_ERR_FAIL;
    int64_t deadline = client->receive_deadline_us ? client->receive_deadline_us :
        esp_timer_get_time() + WS_FRAME_BUDGET_US;
    size_t received = 0;
    while (received < size) {
        if (!atomic_load(&s_running)) return HTTPD_SOCK_ERR_FAIL;
        if (esp_timer_get_time() >= deadline) return HTTPD_SOCK_ERR_TIMEOUT;
        bool writable;
        ssize_t count = native_web_transport_recv(server, socket,
            data + received, size - received, flags | MSG_DONTWAIT, &writable);
        if (count > 0) {
            if ((size_t)count > size - received) return HTTPD_SOCK_ERR_FAIL;
            received += (size_t)count;
            // A peek never consumes bytes: appending another peek would duplicate
            // the same prefix. Return the available prefix without reading again.
            if (flags & MSG_PEEK) break;
            continue;
        }
        if (!count) return 0;
        if (errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        int64_t remaining = deadline - esp_timer_get_time();
        if (remaining <= 0) return HTTPD_SOCK_ERR_TIMEOUT;
        struct timeval wait = {.tv_sec = (long)(remaining / 1000000LL), .tv_usec = (long)(remaining % 1000000LL)};
        fd_set readable;
        FD_ZERO(&readable); FD_SET(socket, &readable);
        int ready = lwip_select(socket + 1, writable ? NULL : &readable,
                               writable ? &readable : NULL, NULL, &wait);
        if (!ready) return HTTPD_SOCK_ERR_TIMEOUT;
        if (ready < 0 && errno != EINTR) return HTTPD_SOCK_ERR_FAIL;
        vTaskDelay(1);
    }
    return esp_timer_get_time() >= deadline ? HTTPD_SOCK_ERR_TIMEOUT : (int)received;
}
static void fail_client(ws_client_t *client) {
    if (!current_client(client)) return;
    client->closing = true;
    // HTTPD owns close(). Immediate shutdown wakes its receive loop without a
    // queued fd/session-pointer close that could hit a subsequently reused fd.
    native_web_transport_shutdown(s_server, client->socket, false);
}
static ws_client_t *find_client(int socket) {
    void *context = httpd_sess_get_ctx(s_server, socket);
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (context == &s_clients[i]) return &s_clients[i];
    }
    if (context) return NULL; // Do not replace another service's session owner.
    for (size_t i = 0; i < WS_CLIENT_LIMIT; ++i) {
        if (!s_clients[i].used) {
            s_clients[i] = (ws_client_t){.used = true, .socket = socket,
                .playlist_revision = atomic_load(&s_playlist_revision)};
            websocket_message_init(&s_clients[i].message, s_clients[i].command,
                sizeof(s_clients[i].command), WS_MESSAGE_BUDGET_US);
            httpd_sess_set_ctx(s_server, socket, &s_clients[i], session_free);
            if (httpd_sess_get_ctx(s_server, socket) == &s_clients[i]) {
                if (httpd_sess_set_send_override(s_server, socket, send_complete_frame_bytes) == ESP_OK &&
                    httpd_sess_set_recv_override(s_server, socket, receive_complete_frame_bytes) == ESP_OK)
                    return &s_clients[i];
                httpd_sess_set_ctx(s_server, socket, NULL, NULL);
            }
            memset(&s_clients[i], 0, sizeof(s_clients[i]));
            return NULL;
        }
    }
    return NULL;
}
static esp_err_t send_text(ws_client_t *client, const char *text) {
    if (!current_client(client) || client->message.close_sent ||
        client->message.close_received) return ESP_ERR_INVALID_STATE;
    httpd_ws_frame_t frame = {.final = true, .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text, .len = strlen(text)};
    client->frame_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->frame_deadline_us = 0;
    if (result != ESP_OK) fail_client(client);
    return result;
}
static esp_err_t send_control(ws_client_t *client, httpd_ws_type_t type,
                               const uint8_t *payload, size_t size) {
    if (!current_client(client)) return ESP_ERR_INVALID_STATE;
    // A received Close is already marked ws_close by SDK. Its session context
    // still owns this fd; ws_get_fd_info is therefore not an ownership test.
    httpd_ws_frame_t frame = {.final = true, .type = type,
        .payload = (uint8_t *)payload, .len = size};
    client->frame_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = httpd_ws_send_frame_async(s_server, client->socket, &frame);
    client->frame_deadline_us = 0;
    if (result == ESP_OK && type == HTTPD_WS_TYPE_CLOSE)
        websocket_message_mark_close_sent(&client->message);
    if (result != ESP_OK) fail_client(client);
    return result;
}
static esp_err_t close_with_code(ws_client_t *client, uint16_t code) {
    uint8_t payload[2] = {(uint8_t)(code >> 8U), (uint8_t)code};
    if (!client->message.close_sent)
        (void)send_control(client, HTTPD_WS_TYPE_CLOSE, payload, sizeof(payload));
    fail_client(client);
    return ESP_FAIL;
}
static esp_err_t receive_and_handle(httpd_req_t *request, ws_client_t *client) {
    httpd_ws_frame_t frame = {0};
    esp_err_t result = httpd_ws_recv_frame(request, &frame, 0);
    if (result != ESP_OK) return result;
    bool control = (unsigned)frame.type >= 8U;
    if (frame.len > (control ? 125U : WS_COMMAND_LIMIT))
        return close_with_code(client, control ? 1002U : 1009U);
    uint8_t payload[125];
    if (frame.len) {
        frame.payload = payload;
        result = httpd_ws_recv_frame(request, &frame, sizeof(payload));
        if (result != ESP_OK) return result;
    }
    websocket_message_result_t message = websocket_message_feed(&client->message,
        (uint8_t)frame.type, frame.final, payload, frame.len,
        (uint64_t)esp_timer_get_time());
    switch (message.event) {
    case WEBSOCKET_MESSAGE_ERROR: return close_with_code(client, message.close_code);
    case WEBSOCKET_MESSAGE_NONE:
    case WEBSOCKET_MESSAGE_PONG: return ESP_OK;
    case WEBSOCKET_MESSAGE_PING:
        return send_control(client, HTTPD_WS_TYPE_PONG, message.data, message.size);
    case WEBSOCKET_MESSAGE_CLOSE:
        if (client->message.close_sent) return ESP_OK;
        return send_control(client, HTTPD_WS_TYPE_CLOSE, message.data, message.size);
    case WEBSOCKET_MESSAGE_BINARY:
        // Radio commands use text; RFC 6455 permits closing unsupported data.
        return close_with_code(client, 1003U);
    case WEBSOCKET_MESSAGE_TEXT:
        if (!message.size) return send_text(client, "{\"commandError\":\"Empty command\"}");
        if (memchr(message.data, 0, message.size))
            return send_text(client, "{\"commandError\":\"Invalid command\"}");
        return handle_command(client, (char *)client->command);
    }
    return ESP_FAIL;
}
static esp_err_t websocket_handler(httpd_req_t *request) {
    // Pinned HTTPD consumes valid upgrades itself. An ordinary GET reached
    // this handler without an upgrade and must remain an HTTP error response.
    if (request->method == HTTP_GET)
        return httpd_resp_send_err(request, HTTPD_400_BAD_REQUEST,
                                   "WebSocket upgrade required");
    if (!atomic_load(&s_running)) return ESP_ERR_INVALID_STATE;
    ws_client_t *client = find_client(httpd_req_to_sockfd(request));
    if (!client) return ESP_ERR_NO_MEM;
    // The first opcode byte was read by HTTPD before dispatch. Header length,
    // mask and payload reads made by the handler share this single deadline.
    client->receive_deadline_us = esp_timer_get_time() + WS_FRAME_BUDGET_US;
    esp_err_t result = receive_and_handle(request, client);
    client->receive_deadline_us = 0;
    return result;
}
static esp_err_t websocket_handshake_transport(httpd_req_t *request) {
    if (!atomic_load(&s_running)) return ESP_ERR_INVALID_STATE;
    // IDF consumes the upgrade GET without invoking websocket_handler. Install
    // both overrides before SDK reads any opcode/control bytes on this session.
    return find_client(httpd_req_to_sockfd(request)) ? ESP_OK : ESP_ERR_NO_MEM;
}
esp_err_t websocket_service_register(httpd_handle_t server, native_state_t *state) {
    if (!server || !state) return ESP_ERR_INVALID_ARG;
    if (s_server) return ESP_ERR_INVALID_STATE;
    httpd_uri_t route = {.uri = "/ws", .method = HTTP_GET, .handler = websocket_handler,
        .is_websocket = true, .handle_ws_control_frames = true,
        .ws_pre_handshake_cb = websocket_handshake_transport,
        .ws_post_handshake_cb = websocket_handshake_transport};
    esp_err_t result = httpd_register_uri_handler(server, &route);
    if (result == ESP_OK) { s_server = server; s_state = state; }
    return result;
}
