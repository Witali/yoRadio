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
const i2s = readMain("esp8266_nodac_i2s.c");

test("Wemos onboard LED reports Wi-Fi and playback without a worker task", () => {
  assert.match(board, /BOARD_STATUS_LED_GPIO 2/);
  assert.match(board, /BOARD_STATUS_LED_ACTIVE_LOW 1/);
  assert.match(kconfig, /config YORADIO_STATUS_LED[\s\S]*default y/);
  assert.match(kconfig, /depends on !YORADIO_AUDIO_OUTPUT_I2S_PCM/);
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

test("NoDAC releases the fixed I2S clock pads after DMA starts", () => {
  assert.match(i2s, /s_ws_mux_before = READ_PERI_REG\(PERIPHS_IO_MUX_GPIO2_U\)/);
  assert.match(i2s, /PIN_FUNC_SELECT\(PERIPHS_IO_MUX_GPIO2_U, FUNC_I2SO_WS\)/);
  assert.match(
    i2s,
    /while \(!s_free_count[\s\S]*WRITE_PERI_REG\(PERIPHS_IO_MUX_GPIO2_U, s_ws_mux_before\)/,
  );
  assert.match(
    i2s,
    /WRITE_PERI_REG\(PERIPHS_IO_MUX_MTDO_U, s_bck_mux_before\)/,
  );
});