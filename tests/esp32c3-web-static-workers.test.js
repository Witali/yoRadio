const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const native = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) => fs.readFileSync(path.join(native, ...parts), "utf8");

test("native WebUI defaults to two static workers and a 20 second timeout", () => {
  const kconfig = read("main", "Kconfig.projbuild");
  const defaults = read("sdkconfig.defaults");

  assert.match(
    kconfig,
    /config YORADIO_WEB_SEND_TIMEOUT_SECONDS[\s\S]*range 5 120[\s\S]*default 20/,
  );
  assert.match(
    kconfig,
    /config YORADIO_WEB_STATIC_WORKERS[\s\S]*range 1 4[\s\S]*default 2/,
  );
  assert.match(defaults, /CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS=20/);
  assert.match(defaults, /CONFIG_YORADIO_WEB_STATIC_WORKERS=2/);
});

test("static files run asynchronously without blocking the WebSocket server", () => {
  const web = read("main", "web_service.c");
  const board = read("main", "board_config.h");

  assert.match(web, /httpd_req_async_handler_begin\(request, &async_request\)/);
  assert.match(web, /xQueueSend\(s_static_request_queue, &async_request, 0\)/);
  assert.match(
    web,
    /static_worker_task[\s\S]*serve_static_request\(request\)[\s\S]*httpd_req_async_handler_complete\(request\)/,
  );
  assert.match(
    web,
    /index < CONFIG_YORADIO_WEB_STATIC_WORKERS[\s\S]*xTaskCreate\(static_worker_task/,
  );
  assert.match(web, /WEB_STATIC_QUEUE_DEPTH WEB_MAX_OPEN_SOCKETS/);
  assert.match(board, /BOARD_TASK_STACK_WEB_STATIC \(2048 \+ CONFIG_YORADIO_WEB_FILE_CHUNK_BYTES\)/);

  const websocketRegistration = web.indexOf("websocket_service_register(server, state)");
  const staticRegistration = web.indexOf("httpd_register_uri_handler(server, &files)");
  assert.ok(websocketRegistration >= 0);
  assert.ok(staticRegistration > websocketRegistration);

  const dispatcherStart = web.indexOf("static esp_err_t static_handler(");
  const serverStart = web.indexOf("esp_err_t web_service_start(", dispatcherStart);
  const dispatcher = web.slice(dispatcherStart, serverStart);
  assert.doesNotMatch(dispatcher, /serve_static_request\(/);
});

test("HTTP send timeout and bounded WebSocket work keep their own scheduling", () => {
  const web = read("main", "web_service.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(
    web,
    /config\.send_wait_timeout = CONFIG_YORADIO_WEB_SEND_TIMEOUT_SECONDS/,
  );
  // Native RFC6455 framing now runs in the HTTPD task under a per-frame
  // deadline. Actual admission/backpressure/retry/deadline behavior is
  // executed by tests/run-c3-websocket-status.py and the TCP/TLS suites.
  assert.match(websocket, /httpd_queue_work\(s_server, broadcast_work, work\)/);
  assert.match(websocket, /send_deadline_us = esp_timer_get_time\(\) \+ WS_FRAME_BUDGET_US/);
  assert.match(websocket, /httpd_ws_send_frame_async\(s_server, sockets\[index\], &frame\)/);
  assert.doesNotMatch(websocket, /httpd_ws_send_data(?:_async)?\(/);
});

test("registered HTTP routes fit the handler table including WebSocket", () => {
  const web = read("main", "web_service.c");
  const capacity = Number(web.match(/config\.max_uri_handlers = (\d+)/)[1]);
  const declarations = [...web.matchAll(/httpd_uri_t \w+ = \{/g)].length;
  assert.ok(capacity >= declarations + 1, "Wildcard files route must fit after WebSocket registration");
});
