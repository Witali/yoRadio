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

test("ESP8266 sends static WebUI resources from a bounded worker queue", () => {
  assert.match(webSource, /xQueueCreate\(WEB_STATIC_QUEUE_DEPTH, sizeof\(httpd_req_t \*\)\)/);
  assert.match(
    webSource,
    /xTaskCreate\(static_worker_task, name, BOARD_TASK_STACK_WEB_STATIC/,
  );
  assert.match(
    webSource,
    /httpd_req_async_handler_begin\(request, &async_request\)[\s\S]*xQueueSend\(s_static_request_queue, &async_request, 0\)/,
  );
  const worker = bodyFrom(webSource, "static void static_worker_task", "static esp_err_t start_static_workers");
  assert.match(worker, /serve_static_request\(request\)/);
  assert.match(worker, /httpd_req_async_handler_complete\(request\)/);
});

test("ESP8266 keeps status and WebSocket on the HTTP task while static routes are asynchronous", () => {
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

test("ESP8266 async WebUI defaults preserve RAM for streaming", () => {
  assert.match(kconfig, /config YORADIO_WEB_STATIC_WORKERS[\s\S]*range 1 2[\s\S]*default 1/);
  assert.match(kconfig, /config YORADIO_WEB_SEND_TIMEOUT_SECONDS[\s\S]*default 20/);
  assert.match(boardConfig, /#define BOARD_TASK_STACK_WEB_STATIC 3072/);
  assert.match(sdkDefaults, /CONFIG_YORADIO_WEB_STATIC_WORKERS=1/);
  assert.match(sdkDefaults, /CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS=20/);
});