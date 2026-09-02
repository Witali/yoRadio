const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native");
const readMain = (name) =>
  fs.readFileSync(path.join(root, "main", name), "utf8");

const app = readMain("app_main.c");
const board = readMain("board_config.h");
const component = readMain("CMakeLists.txt");
const kconfig = readMain("Kconfig.projbuild");
const led = readMain("status_led.c");

test("SPI-PDM profile can use the Wemos status LED without a worker task", () => {
  assert.match(board, /BOARD_STATUS_LED_GPIO 2/);
  assert.match(board, /BOARD_STATUS_LED_ACTIVE_LOW 1/);
  assert.match(kconfig, /config YORADIO_STATUS_LED[\s\S]*default y/);
  assert.match(kconfig, /depends on YORADIO_AUDIO_OUTPUT_SPI_PDM/);
  assert.match(kconfig, /owns GPIO2 as WS for the entire transfer/);
  assert.match(component, /"status_led\.c"/);
  assert.match(
    app,
    /native_audio_output_init\(\)[\s\S]*status_led_init\(\)[\s\S]*network_service_start\(\)/,
  );
  assert.match(app, /web_service_poll\(\);[\s\S]*status_led_poll\(\);/);
  assert.doesNotMatch(led, /xTaskCreate|xTimerCreate/);
});

test("status LED is off without client Wi-Fi, steady idle and 500-ms blinking while playing", () => {
  assert.match(led, /network_service_connected\(\)/);
  assert.match(led, /if \(!connected\)[\s\S]*set_output\(false\)/);
  assert.match(led, /if \(!state\.playing\)[\s\S]*set_output\(true\)/);
  assert.match(led, /STATUS_LED_HALF_PERIOD_MS 500U/);
  assert.match(led, /now - s_blink_started/);
  assert.match(
    led,
    /BOARD_STATUS_LED_ACTIVE_LOW \? !on : on/,
  );
});
