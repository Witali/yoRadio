#define WS_STATUS_POLL_MS 100
#define WS_STATUS_HEARTBEAT_MS 2000

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
static size_t s_last_ws_clients;

static void json_escape(const char *source, char *target, size_t target_size) {
    size_t written = 0;
    while (*source && written + 1 < target_size) {
        unsigned char value = (unsigned char)*source++;
        if ((value == '"' || value == '\\') && written + 2 < target_size) {
            target[written++] = '\\';
            target[written++] = (char)value;
        } else if (value >= 0x20) {
            target[written++] = (char)value;
        }
    }
    target[written] = '\0';
}

static esp_err_t ws_send_request(httpd_req_t *request, const char *text) {
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    return httpd_ws_send_frame(request, &frame);
}

static void ws_send_complete(esp_err_t result, int socket, void *argument) {
    atomic_uint *pending = argument;
    atomic_fetch_sub(pending, 1U);
    if (result != ESP_OK && s_server) {
        httpd_sess_trigger_close(s_server, socket);
    }
}

static esp_err_t ws_send_async(int socket, const char *text,
                               atomic_uint *pending) {
    httpd_ws_frame_t frame = {
        .final = true,
        .fragmented = false,
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)text,
        .len = strlen(text),
    };
    atomic_fetch_add(pending, 1U);
    esp_err_t result = httpd_ws_send_data_async(
        s_server, socket, &frame, ws_send_complete, pending);
    if (result != ESP_OK) atomic_fetch_sub(pending, 1U);
    return result;
}

static size_t broadcast_text(const char *text, atomic_uint *pending) {
    if (!s_server || !text || !pending) return 0;
    size_t count = CONFIG_LWIP_MAX_SOCKETS;
    int sockets[CONFIG_LWIP_MAX_SOCKETS];
    if (httpd_get_client_list(s_server, &count, sockets) != ESP_OK) return 0;
    size_t delivered = 0;
    size_t clients = 0;
    for (size_t index = 0; index < count; ++index) {
        if (httpd_ws_get_fd_info(s_server, sockets[index]) ==
            HTTPD_WS_CLIENT_WEBSOCKET) {
            ++clients;
            if (ws_send_async(sockets[index], text, pending) == ESP_OK) {
                ++delivered;
            }
        }
    }
    s_last_ws_clients = clients;
    return delivered;
}

static esp_err_t websocket_handler_awake(httpd_req_t *request) {
    if (request->method == HTTP_GET) {
        ESP_LOGI(TAG, "WebUI client connected on socket %d",
                 httpd_req_to_sockfd(request));
        return ESP_OK;
    }

    httpd_ws_frame_t frame = {0};
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, 0), TAG,
                        "read WebSocket frame size");
    if (frame.type != HTTPD_WS_TYPE_TEXT || frame.len == 0 || frame.len > 255) {
        return ESP_OK;
    }
    char payload[256];
    frame.payload = (uint8_t *)payload;
    ESP_RETURN_ON_ERROR(httpd_ws_recv_frame(request, &frame, sizeof(payload) - 1),
                        TAG, "read WebSocket frame");
    payload[frame.len] = '\0';
    handle_command(request, payload);
    return ESP_OK;
}

static esp_err_t websocket_handler(httpd_req_t *request) {
    if (!deep_sleep_clock_begin_activity()) return ESP_FAIL;
    esp_err_t result = websocket_handler_awake(request);
    deep_sleep_clock_end_activity();
    return result;
}

