const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(
  path.resolve(
    __dirname,
    "..",
    "esp8266",
    "rtos-sdk-native",
    "main",
    "web_service.c",
  ),
  "utf8",
);
const audioSource = fs.readFileSync(
  path.resolve(
    __dirname,
    "..",
    "esp8266",
    "rtos-sdk-native",
    "main",
    "audio_service.c",
  ),
  "utf8",
);
const networkSource = fs.readFileSync(
  path.resolve(
    __dirname,
    "..",
    "esp8266",
    "rtos-sdk-native",
    "main",
    "network_service.c",
  ),
  "utf8",
);
const radioSource = fs.readFileSync(
  path.resolve(
    __dirname,
    "..",
    "esp8266",
    "rtos-sdk-native",
    "main",
    "radio_control.c",
  ),
  "utf8",
);

const playlistSource = fs.readFileSync(
  path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main", "playlist_service.c"),
  "utf8",
);
const httpServerHeader = fs.readFileSync(
  path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "components", "esp_http_server", "include", "esp_http_server.h"),
  "utf8",
);
const httpWebSocketSource = fs.readFileSync(
  path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "components", "esp_http_server", "src", "httpd_ws.c"),
  "utf8",
);
const httpParserSource = fs.readFileSync(
  path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "components", "esp_http_server", "src", "httpd_parse.c"),
  "utf8",
);

test("ESP8266 WebSocket handler completes HTTP upgrade before reading frames", () => {
  const handler = source.slice(source.indexOf("static esp_err_t websocket_handler"));
  const handshake = handler.indexOf("request->method == HTTP_GET");
  const receive = handler.indexOf("httpd_ws_recv_frame");

  assert.notEqual(handshake, -1);
  assert.notEqual(receive, -1);
  assert.ok(handshake < receive);
  assert.match(
    handler.slice(handshake, receive),
    /request->method == HTTP_GET[\s\S]*return ESP_OK;/,
  );
});

test("ESP8266 WebSocket handler reads a command in one bounded receive", () => {
  const handler = source.slice(source.indexOf("static esp_err_t websocket_handler"));

  assert.match(
    handler,
    /char payload\[WS_COMMAND_MAX \+ 1U\][\s\S]*\.payload = \(uint8_t \*\)payload/,
  );
  assert.match(
    handler,
    /httpd_ws_recv_frame\(request, &frame, sizeof\(payload\) - 1U\)/,
  );
  assert.doesNotMatch(
    handler,
    /httpd_ws_recv_frame\(request, &frame, 0\)/,
  );
});

test("ESP8266 Web API dispatches every player command and returns fresh state", () => {
  const commands = source.slice(
    source.indexOf("static void handle_command"),
    source.indexOf("static esp_err_t websocket_handler"),
  );

  assert.match(
    commands,
    /strcmp\(command, "play"\) == 0[\s\S]*radio_control_play\(\(uint16_t\)strtoul\(value, NULL, 10\)\)[\s\S]*send_initial_state\(request\)/,
  );
  for(const [wireCommand, controlCall] of [
    ["stop", "radio_control_stop"],
    ["toggle", "radio_control_toggle"],
    ["next", "radio_control_next"],
    ["prev", "radio_control_previous"],
  ]) {
    assert.match(
      commands,
      new RegExp(
        `strcmp\\(command, "${wireCommand}"\\) == 0[\\s\\S]*${controlCall}\\(\\)[\\s\\S]*send_initial_state\\(request\\)`,
      ),
    );
  }
});

test("ESP8266 Web API publishes player, station and stream state after commands", () => {
  const initial = source.slice(
    source.indexOf("static esp_err_t send_initial_state"),
    source.indexOf("static esp_err_t send_active_settings"),
  );
  assert.match(initial, /format_status\(&status, body, sizeof\(body\)\)/);
  assert.match(initial, /ws_send\(request, body\)/);
  assert.match(initial, /\{\\"current\\":%u\}/);
  assert.match(initial, /\{\\"playermode\\":\\"modeweb\\"\}/);
  assert.match(source, /\{\\"id\\":\\"playerwrap\\",\\"value\\":\\"%s\\"\}/);
  assert.match(source, /status->playing \? "playing" : "stopped"/);
  assert.match(source, /\{\\"id\\":\\"bitrate\\",\\"value\\":%lu\}/);
  assert.match(source, /\{\\"id\\":\\"rssi\\",\\"value\\":%d\}/);
});

test("ESP8266 WebUI keeps the profiled stack needed by getindex", () => {
  const board = fs.readFileSync(
    path.resolve(
      __dirname,
      "..",
      "esp8266",
      "rtos-sdk-native",
      "main",
      "board_config.h",
    ),
    "utf8",
  );
  assert.match(board, /BOARD_TASK_STACK_WEB 5120/);
});

test("ESP8266 validates a saved fd before treating it as a WebSocket", () => {
  assert.match(httpServerHeader, /httpd_ws_client_info_t httpd_ws_get_fd_info/);
  assert.match(
    httpWebSocketSource,
    /sess->ws_handshake_done && !sess->ws_close/,
  );
  assert.match(
    source,
    /websocket_socket_active\(s_ws_fd\)[\s\S]*httpd_sess_trigger_close\(s_server, s_ws_fd\)/,
  );
  assert.match(
    source,
    /static void async_send_work[\s\S]*websocket_socket_active\(socket\)/,
  );
});

test("ESP8266 parser accepts exactly HTTP 1.1", () => {
  assert.match(
    httpParserSource,
    /parser->http_major != 1\) \|\| \(parser->http_minor != 1/,
  );
});

test("ESP8266 HTTP task has enough stack for playlist-backed commands", () => {
  assert.match(source, /config\.stack_size = BOARD_TASK_STACK_WEB/);
});

test("ESP8266 exposes only board-supported stations with matching indices", () => {
  assert.match(playlistSource, /#define INDEX_VERSION 2U/);
  assert.match(playlistSource, /strncmp\(url, "http:\/\/", 7U\) == 0/);
  assert.match(playlistSource, /strncasecmp\(name, "Ogg ", 4U\) != 0/);
  for(const extension of ["ogg", "opus", "flac", "m3u8", "wav"]) {
    assert.match(playlistSource, new RegExp(`"\\.${extension}"`));
  }
  const handler = source.slice(source.indexOf("static esp_err_t playlist_handler"), source.indexOf("static esp_err_t status_handler"));
  assert.match(handler, /playlist_service_count\(\)/);
  assert.match(handler, /playlist_service_entry_supported\(line\)/);
  assert.match(handler, /open_nonempty\(PLAYLIST_PATH\)/);
});

test("ESP8266 radio retries short socket timeouts until the HTTP header deadline", () => {
  assert.match(audioSource, /#define SOCKET_READ_TIMEOUT_MS 200U/);
  assert.match(audioSource, /#define HTTP_HEADER_TIMEOUT_MS 10000U/);
  assert.match(audioSource, /#define HTTP_OPEN_ATTEMPTS 2U/);
  assert.match(
    audioSource,
    /HTTP_HEADER_TIMEOUT_MS \* 1000LL[\s\S]*errno == EAGAIN[\s\S]*errno == EWOULDBLOCK[\s\S]*header_deadline/,
  );
  assert.match(audioSource, /Open stream failed: %d \(errno %d\)/);
  assert.match(
    audioSource,
    /attempt < HTTP_OPEN_ATTEMPTS[\s\S]*open_http_stream\(command\.url, &stream\)[\s\S]*pdMS_TO_TICKS\(250U\)/,
  );
});

test("ESP8266 radio checks a header that exactly fills its receive buffer", () => {
  assert.match(
    audioSource,
    /while \(received_total < sizeof\(s_work\) - 1U[\s\S]*if \(!header_size\)\s*find_header_end\(s_work, received_total, &header_size\);[\s\S]*if \(!header_size\)/,
  );
});

test("ESP8266 waits for DHCP and releases recovery AP memory in client mode", () => {
  assert.match(networkSource, /CONFIG_YORADIO_WIFI_RECOVERY_AP_TIMEOUT_SECONDS \* 1000U/);
  assert.match(
    networkSource,
    /IP_EVENT_STA_GOT_IP[\s\S]*s_access_point[\s\S]*esp_wifi_set_mode\(WIFI_MODE_STA\)[\s\S]*s_access_point = false/,
  );
  assert.match(
    networkSource,
    /!\(bits & WIFI_CONNECTED_BIT\) && !s_connected/,
  );
  assert.match(
    networkSource,
    /select_credential\(0\)[\s\S]*esp_wifi_connect\(\)[\s\S]*next_ap_retry[\s\S]*pdMS_TO_TICKS\(5000U\)/,
  );
  assert.match(
    networkSource,
    /Wi-Fi supervisor exiting after DHCP[\s\S]*vTaskDelete\(NULL\)/,
  );
  assert.match(networkSource, /void network_service_poll\(void\)/);
});

test("ESP8266 recovery AP assigns clients an address for WebUI access", () => {
  assert.match(networkSource, /ip4addr_aton\("192\.168\.4\.1", &info\.ip\)/);
  assert.match(networkSource, /tcpip_adapter_dhcps_stop\(TCPIP_ADAPTER_IF_AP\)/);
  assert.match(networkSource, /tcpip_adapter_set_ip_info\(TCPIP_ADAPTER_IF_AP, &info\)/);
  assert.match(networkSource, /tcpip_adapter_dhcps_start\(TCPIP_ADAPTER_IF_AP\)/);
});

test("ESP8266 next/previous starts searching after the current station", () => {
  const radio = radioSource;
  assert.match(
    radio,
    /candidate = candidate >= count \? 1U : candidate \+ 1U;[\s\S]*playlist_service_find_http_index\([\s\S]*candidate, direction, &found\)/,
  );
  assert.match(radio, /candidate = candidate <= 1U \? count : candidate - 1U;/);
});
