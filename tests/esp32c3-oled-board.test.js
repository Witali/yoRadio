const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("ESP32-C3 profile selects the onboard OLED and stereo PDM pins", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");

  assert.match(profile, /DSP_MODEL\s+DSP_SSD1306_72X40/);
  assert.match(profile, /I2C_SDA\s+5/);
  assert.match(profile, /I2C_SCL\s+6/);
  assert.match(profile, /I2S_BCLK\s+255/);
  assert.match(profile, /I2S_LRC\s+255/);
  assert.match(profile, /I2S_DOUT\s+255/);
  assert.match(profile, /I2S_INTERNAL\s+true/);
  assert.match(profile, /I2S_INTERNAL_OUTPUT\s+AUDIO_OUTPUT_PDM/);
  assert.match(profile, /I2S_PDM_DOUT\s+10/);
  assert.match(profile, /I2S_PDM_DOUT2\s+3/);
  assert.match(profile, /BTN_CENTER\s+9/);
});

test("all profile-controlled tasks are pinned to the only C3 core", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");
  for (const task of [
    "PLAYER_TASK_CORE_ID",
    "DSP_TASK_CORE_ID",
    "SEARCH_WIFI_CORE_ID",
    "WATCHDOG_TASK_CORE_ID",
    "SYNC_TASK_CORE",
    "CONFIG_ASYNC_TCP_RUNNING_CORE",
  ]) {
    assert.match(profile, new RegExp(`#define\\s+${task}\\s+0`));
  }
});

test("72x40 driver uses the controller-specific geometry and init sequence", () => {
  const header = read("yoRadio", "src", "displays", "SSD1306_72x40.h");
  const source = read("yoRadio", "src", "displays", "SSD1306_72x40.cpp");

  assert.match(header, /kWidth = 72/);
  assert.match(header, /kHeight = 40/);
  assert.match(header, /kColumnOffset = 28/);
  assert.match(source, /0xa8, 0x27/);
  assert.match(source, /0xad, 0x30/);
  assert.match(source, /0xda, 0x12/);
  assert.match(source, /static_cast<uint8_t>\(0xb0 \| page\)/);
});

test("72x40 OLED applies the saved 0..100 contrast setting", () => {
  const driver = read("yoRadio", "src", "displays", "SSD1306_72x40.cpp");
  const display = read("yoRadio", "src", "displays", "displaySSD1306.cpp");
  const controller = read("yoRadio", "src", "core", "display.cpp");

  assert.match(driver, /void SSD1306_72x40::setContrast\(uint8_t percent\)/);
  assert.match(driver, /percent\) \* 255U \+ 50U\) \/ 100U/);
  assert.match(driver, /\{0x81, controllerContrast\}/);
  assert.match(display, /DSP_MODEL==DSP_SSD1306_72X40[\s\S]*setContrast\(config\.store\.contrast\)/);
  assert.match(controller, /DSP_MODEL==DSP_NOKIA5110 \|\| DSP_MODEL==DSP_SSD1306_72X40/);
});

test("display objects exist before the single-core display task starts", () => {
  const source = read("yoRadio", "src", "core", "display.cpp");
  const init = source.match(/void Display::init\(\) \{([\s\S]*?)\n\}/);

  assert.ok(init, "Display::init() must exist");
  assert.ok(init[1].indexOf("_pager = new Pager()") >= 0);
  assert.ok(init[1].indexOf("_createDspTask()") >= 0);
  assert.ok(
    init[1].indexOf("_pager = new Pager()") < init[1].indexOf("_createDspTask()"),
    "the display task must not run before Pager construction",
  );
});

test("the C3 profile is opt-in and leaves the CYD profile as the default", () => {
  const options = read("yoRadio", "myoptions.h");
  const boardInclude = options.indexOf("YORADIO_BOARD_ESP32C3_OLED_042");
  const cydProfile = options.indexOf("ESP32-2432S028 CYD2USB");

  assert.ok(boardInclude >= 0);
  assert.ok(cydProfile > boardInclude);
  assert.match(options, /#else[\s\S]*ESP32-2432S028 CYD2USB/);
});
