const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");
const main = (...parts) =>
  read("esp8266", "rtos-sdk-native", "main", ...parts);
const httpd = (...parts) =>
  read("esp8266", "rtos-sdk-native", "components", "esp_http_server", ...parts);

const webSource = main("web_service.c");
const boardConfig = main("board_config.h");
const kconfig = main("Kconfig.projbuild");
const sdkDefaults = read("esp8266", "rtos-sdk-native", "sdkconfig.defaults");
const publicHeader = httpd("include", "esp_http_server.h");
const privateHeader = httpd("src", "esp_httpd_priv.h");
const sessionSource = httpd("src", "httpd_sess.c");
const txrxSource = httpd("src", "httpd_txrx.c");

function bodyFrom(source, signature, nextSignature) {
  const start = source.indexOf(signature);
  assert.notEqual(start, -1, `missing ${signature}`);
  const end = nextSignature ? source.indexOf(nextSignature, start) : source.length;
  assert.notEqual(end, -1, `missing ${nextSignature}`);
  return source.slice(start, end);
}

test("ESP8266 backports the standard asynchronous HTTP request API", () => {
  assert.match(publicHeader, /httpd_req_async_handler_begin\(httpd_req_t \*r, httpd_req_t \*\*out\)/);
  assert.match(publicHeader, /httpd_req_async_handler_complete\(httpd_req_t \*r\)/);
  assert.match(privateHeader, /bool for_async_req/);

  const begin = bodyFrom(
    txrxSource,
    "esp_err_t httpd_req_async_handler_begin",
    "esp_err_t httpd_req_async_handler_complete",
  );
  assert.match(begin, /malloc\(sizeof\(\*async\)\)[\s\S]*memcpy\(async, r, sizeof\(\*async\)\)/);
  assert.match(begin, /malloc\(sizeof\(\*async_aux\)\)[\s\S]*memcpy\(async_aux, r_aux, sizeof\(\*async_aux\)\)/);
  assert.match(begin, /calloc\(hd->config\.max_resp_headers, sizeof\(struct resp_hdr\)\)/);
  assert.match(begin, /r_aux->sd->for_async_req = true/);

  const complete = bodyFrom(
    txrxSource,
    "esp_err_t httpd_req_async_handler_complete",
    "size_t httpd_unrecv",
  );
  assert.match(complete, /ra->sd->for_async_req = false/);
  assert.match(complete, /free\(ra->resp_hdrs\)[\s\S]*free\(ra\)[\s\S]*free\(r\)/);
  assert.match(complete, /httpd_queue_work\(handle, httpd_async_wakeup, NULL\)/);
});

test("ESP8266 HTTP server does not poll or LRU-purge worker-owned sockets", () => {
  assert.match(
    sessionSource,
    /hd->hd_sd\[i\]\.fd != -1 && !hd->hd_sd\[i\]\.for_async_req/,
  );
  assert.match(
    sessionSource,
    /if \(sd->for_async_req\) \{\s*return false;\s*\}/,
  );
  assert.match(
    sessionSource,
    /!hd->hd_sd\[i\]\.for_async_req &&[\s\S]*hd->hd_sd\[i\]\.lru_counter < lru_counter/,
  );
});

test("ESP8266 serves static WebUI resources on the shared HTTP task stack", () => {
  const handler = bodyFrom(webSource, "static esp_err_t static_handler", "static esp_err_t register_get");
  assert.match(handler, /return serve_static_request\(request\)/);
  assert.doesNotMatch(webSource, /httpd_req_async_handler_begin\(request/);
  assert.doesNotMatch(webSource, /xTaskCreate\(static_worker_task/);
  assert.doesNotMatch(webSource, /xQueueCreate\(WEB_STATIC_QUEUE_DEPTH/);
});

test("ESP8266 keeps status, WebSocket and static routes on the shared HTTP task", () => {
  assert.match(webSource, /config\.max_open_sockets = WEB_MAX_OPEN_SOCKETS/);
  assert.match(
    webSource,
    /config\.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS/,
  );
  assert.match(webSource, /register_get\(pages\[index\], static_handler\)/);
  assert.match(webSource, /register_get\(assets\[index\], static_handler\)/);
  assert.match(webSource, /register_get\("\/variables\.js", static_handler\)/);
  assert.match(webSource, /register_get\("\/data\/playlist\.csv", static_handler\)/);
  assert.match(webSource, /register_get\("\/api\/native\/status", status_handler\)/);
  assert.match(webSource, /\.handler = websocket_handler/);
  assert.doesNotMatch(webSource, /register_get\("\/api\/native\/status", static_handler\)/);
});

test("ESP8266 WebUI shares the HTTP stack to preserve RAM for streaming", () => {
  assert.doesNotMatch(kconfig, /config YORADIO_WEB_STATIC_WORKERS/);
  assert.match(kconfig, /config YORADIO_WEB_SEND_TIMEOUT_SECONDS[\s\S]*default 20/);
  assert.doesNotMatch(boardConfig, /BOARD_TASK_STACK_WEB_STATIC/);
  assert.doesNotMatch(sdkDefaults, /CONFIG_YORADIO_WEB_STATIC_WORKERS/);
  assert.match(sdkDefaults, /CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS=20/);
  assert.match(kconfig, /config YORADIO_WIFI_RECOVERY_AP_TIMEOUT_SECONDS[\s\S]*default 30/);
  assert.match(sdkDefaults, /CONFIG_YORADIO_WIFI_RECOVERY_AP_TIMEOUT_SECONDS=30/);
  assert.match(sdkDefaults, /CONFIG_LWIP_MAX_ACTIVE_TCP=5/);
  assert.match(sdkDefaults, /CONFIG_LWIP_TCP_MSS=536/);
  assert.match(sdkDefaults, /CONFIG_LWIP_TCP_SND_BUF_DEFAULT=2440/);
  assert.match(sdkDefaults, /CONFIG_LWIP_TCP_WND_DEFAULT=2440/);
});

test("ESP8266 releases short HTTP connections after each response", () => {
  const prepare = bodyFrom(
    webSource,
    "static void prepare_short_response",
    "static esp_err_t finish_short_response",
  );
  const finish = bodyFrom(
    webSource,
    "static esp_err_t finish_short_response",
    "static const char *asset_type",
  );
  const staticResponses = bodyFrom(webSource, "static esp_err_t page_handler", "static esp_err_t serve_static_request");
  assert.match(prepare, /httpd_resp_set_hdr\(request, "Connection", "close"\)/);
  assert.match(finish, /httpd_sess_trigger_close\(request->handle,[\s\S]*httpd_req_to_sockfd\(request\)\)/);
  assert.match(staticResponses, /prepare_short_response\(request\)/);
});

test("ESP8266 bounds simultaneous HTTP sessions without LRU eviction", () => {
  assert.match(webSource, /#define WEB_MAX_OPEN_SOCKETS 4U/);
  assert.match(webSource, /config\.backlog_conn = 1/);
  assert.match(webSource, /config\.lru_purge_enable = false/);
});

test("ESP8266 strips cache-busting query from static file lookup", () => {
  const pathLength = bodyFrom(
    webSource,
    "static size_t request_path_length",
    "static bool request_path_equals",
  );
  assert.match(pathLength, /strchr\(request->uri, '\?'\)/);
  const asset = bodyFrom(
    webSource,
    "static esp_err_t asset_handler",
    "static esp_err_t playlist_handler",
  );
  assert.match(asset, /uri_length = request_path_length\(request\)/);
  const dispatch = bodyFrom(
    webSource,
    "static esp_err_t serve_static_request",
    "static esp_err_t static_handler",
  );
  assert.match(dispatch, /request_path_equals\(request, "\/variables\.js"\)/);
  assert.match(dispatch, /request_path_equals\(request, "\/settings\.html"\)/);
});

test("ESP8266 chunks embedded HTML below its TCP send window", () => {
  const chunked = bodyFrom(webSource, "static esp_err_t send_chunked_string", "static void json_escape");
  assert.match(chunked, /remaining > 512U \? 512U : remaining/);
  assert.match(chunked, /httpd_resp_send_chunk\(request, text, count\)/);
  assert.match(chunked, /httpd_resp_send_chunk\(request, NULL, 0\)/);
  const page = bodyFrom(webSource, "static esp_err_t page_handler", "static esp_err_t variables_handler");
  assert.match(page, /send_chunked_string\(request, yoradio_index_html\(\)\)/);
});

test("ESP8266 HTTP send loop is nonblocking, bounded and retryable", () => {
  const sendAll = bodyFrom(
    txrxSource,
    "static esp_err_t httpd_send_all",
    "static size_t httpd_recv_pending",
  );
  assert.match(sendAll, /MSG_DONTWAIT/);
  assert.match(sendAll, /HTTPD_SEND_RETRY_TIMEOUT_MS/);
  assert.match(sendAll, /HTTPD_SOCK_ERR_TIMEOUT[\s\S]*EAGAIN[\s\S]*EWOULDBLOCK[\s\S]*EINTR/);
  assert.match(sendAll, /vTaskDelay\(pdMS_TO_TICKS\(1\)\)/);
  assert.match(sendAll, /return ESP_FAIL/);

  const defaultSend = bodyFrom(
    txrxSource,
    "int httpd_default_send",
    "int httpd_default_recv",
  );
  assert.match(defaultSend, /errno == EAGAIN[\s\S]*errno == EWOULDBLOCK[\s\S]*errno == EINTR/);
  assert.match(defaultSend, /return HTTPD_SOCK_ERR_TIMEOUT/);
});