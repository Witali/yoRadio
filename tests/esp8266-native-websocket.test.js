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

test("ESP8266 Web API dispatches player commands without synchronous status sends", () => {
  const commands = source.slice(
    source.indexOf("static void handle_command"),
    source.indexOf("static esp_err_t websocket_handler"),
  );

  const playerCommands = commands.slice(
    commands.indexOf('strcmp(command, "play")'),
    commands.indexOf('strcmp(command, "volume")'),
  );
  for(const controlCall of [
    "radio_control_play",
    "radio_control_stop",
    "radio_control_toggle",
    "radio_control_next",
    "radio_control_previous",
  ]) {
    assert.ok(playerCommands.includes(controlCall));
  }
  assert.doesNotMatch(playerCommands, /send_initial_state/);
});
test("ESP8266 Web API publishes player, station and stream state after commands", () => {
  const initial = source.slice(
    source.indexOf("static esp_err_t send_initial_state"),
    source.indexOf("static esp_err_t send_active_settings"),
  );
  assert.match(initial, /format_status\(&state, s_async_message, sizeof\(s_async_message\)\)/);
  assert.match(initial, /ws_send\(request, s_async_message\)/);
  assert.doesNotMatch(initial, /s_send_pending/);
  assert.match(initial, /\{\\"current\\":%u\}/);
  assert.match(initial, /\{\\"playermode\\":\\"modeweb\\"\}/);
  assert.match(source, /\{\\"id\\":\\"playerwrap\\",\\"value\\":\\"%s\\"\}/);
  assert.match(source, /status->playing \? "playing" : "stopped"/);
  assert.match(source, /\{\\"id\\":\\"bitrate\\",\\"value\\":%lu\}/);
  assert.match(source, /\{\\"id\\":\\"rssi\\",\\"value\\":%d\}/);
});

test("ESP8266 bounds the persistent status buffer for audio heap", () => {
  assert.match(source, /#define WEB_STATUS_CAPACITY 1088U/);
});

test("ESP8266 throttles volatile telemetry without delaying player state", () => {
  assert.match(source, /status_requires_immediate_send/);
  assert.match(source, /current->playing != previous->playing/);
  assert.match(source, /current->station_index != previous->station_index/);
  assert.match(source, /current->codec != previous->codec/);
  assert.match(source, /current->title_hash != previous->title_hash/);
  assert.match(source, /current->station_hash != previous->station_hash/);
  const immediate = source.slice(
    source.indexOf("static bool status_requires_immediate_send"),
    source.indexOf("static void format_stream"),
  );
  assert.doesNotMatch(immediate, /rssi|buffer_percent/);
  assert.match(source, /WS_HEARTBEAT_MS 2000U/);
  assert.match(source, /if \(!immediate && !heartbeat\) return/);
  assert.doesNotMatch(source, /memcmp\(&current, &s_previous_status/);
});
test("ESP8266 WebUI status uses a compact change key and bounded writer", () => {
  const key = source.slice(
    source.indexOf("typedef struct {", source.indexOf("WEB_STATIC_SCRATCH_SIZE")),
    source.indexOf("} web_status_key_t;") + "} web_status_key_t;".length,
  );
  assert.doesNotMatch(key, /char station|char title/);
  assert.match(key, /uint32_t station_hash/);
  assert.match(key, /uint32_t title_hash/);
  assert.match(source, /sizeof\(web_status_key_t\) <= 32U/);
  const formatter = source.slice(
    source.indexOf("static bool format_status"),
    source.indexOf("static esp_err_t ws_send"),
  );
  assert.doesNotMatch(formatter, /char station\[|char title\[|char escaped_stream\[/);
  assert.match(formatter, /json_writer_escaped\(&writer, status->station\)/);
  assert.match(formatter, /status->error\[0\] && !status->playing/);
  assert.match(formatter, /\? status->error : status->title/);
});

test("ESP8266 WebUI uses the reduced stack after removing status temporaries", () => {
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
  const initial = source.slice(source.indexOf("static esp_err_t send_initial_state"), source.indexOf("static esp_err_t send_active_settings"));
  assert.doesNotMatch(initial, /char body\[WEB_STATUS_CAPACITY\]/);
  assert.match(initial, /format_status\(&state, s_async_message, sizeof\(s_async_message\)\)/);
});

test("ESP8266 validates a saved fd before treating it as a WebSocket", () => {
  assert.match(httpServerHeader, /httpd_ws_client_info_t httpd_ws_get_fd_info/);
  assert.match(
    httpWebSocketSource,
    /sess->ws_handshake_done && !sess->ws_close/,
  );
  assert.match(
    source,
    /websocket_socket_active\(socket\)/,
  );
  assert.match(
    source,
    /static bool broadcast_message[\s\S]*websocket_socket_active\(socket\)/,
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
  // Actual filter equivalence, including extension case/query boundaries,
  // is compiled and executed in esp8266-playlist-streaming.test.js.
  assert.match(playlistSource, /return http && !ogg &&/);
  assert.match(playlistSource, /!has_unsupported_extension\(url\)/);
  const handler = source.slice(source.indexOf("static esp_err_t playlist_handler"), source.indexOf("static esp_err_t status_handler"));
  assert.match(handler, /playlist_service_count\(\)/);
  assert.match(handler, /read\(file, s_async_message/);
  assert.match(handler, /playlist_service_entry_supported\(line\)/);
  assert.match(handler, /if \(used == sizeof\(s_static_scratch\)\)/);
  assert.doesNotMatch(handler, /\bmalloc\b|\bcalloc\b/);
  assert.match(handler, /open\(PLAYLIST_PATH, O_RDONLY\)/);
});

test("ESP8266 radio retries short socket timeouts until the HTTP header deadline", () => {
  assert.match(audioSource, /#define SOCKET_READ_TIMEOUT_MS 200U/);
  assert.match(audioSource, /#define HTTP_HEADER_TIMEOUT_MS 10000U/);
  assert.match(audioSource, /#define HTTP_OPEN_ATTEMPTS 2U/);
  assert.match(
    audioSource,
    /HTTP_HEADER_TIMEOUT_MS \* 1000LL[\s\S]*errno == EAGAIN[\s\S]*errno == EWOULDBLOCK[\s\S]*header_deadline/,
  );
  assert.match(audioSource, /Open stream failed: stage %d errno %d heap %u/);
  assert.match(
    audioSource,
    /attempt < HTTP_OPEN_ATTEMPTS[\s\S]*open_http_stream\(command\.url, &stream\)[\s\S]*pdMS_TO_TICKS\(250U\)/,
  );
});

test("ESP8266 reconnects a clean radio EOF unless control changed", () => {
  assert.ok(audioSource.includes("feed == 0 && generation_current(command.generation)"));
  assert.ok(audioSource.includes('native_state_set_audio(false, true, "RECONNECTING")'));
  assert.equal((audioSource.match(/requeue_if_current\(&command\)/g) || []).length, 2);
  const retry = audioSource.slice(audioSource.indexOf("static void requeue_if_current"),
    audioSource.indexOf("static uint32_t advance_generation"));
  assert.match(retry, /taskENTER_CRITICAL\(\);\s+if \(generation_current\(command->generation\)\)\s+xQueueOverwrite\(s_commands, command\);\s+taskEXIT_CRITICAL\(\);/);
});
test("ESP8266 radio incrementally reuses the header buffer and preserves the body prefix", () => {
  assert.match(
    audioSource,
    /while \(!http_response_header_finished\(&headers\)\)[\s\S]*sizeof\(s_work\) - input_start[\s\S]*http_response_header_feed[\s\S]*body_size = \(size_t\)received - consumed;[\s\S]*memmove\(s_work, s_work \+ input_start \+ consumed, body_size\)/,
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
