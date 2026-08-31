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

test("ESP8266 HTTP task has enough stack for playlist-backed commands", () => {
  assert.match(source, /config\.stack_size = BOARD_TASK_STACK_WEB/);
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
  assert.match(networkSource, /#define WIFI_CONNECT_TIMEOUT_MS 30000U/);
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
