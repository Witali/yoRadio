const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const nativeRoot = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) =>
  fs.readFileSync(path.join(nativeRoot, ...parts), "utf8");

test("ESP32-C3 native target is Arduino-free and selects the RISC-V chip", () => {
  const project = read("CMakeLists.txt");
  const component = read("main", "CMakeLists.txt");
  const sdkconfig = read("sdkconfig.defaults");
  const setup = read("setup.ps1");

  assert.match(project, /project\(yoradio_esp32c3_oled_native\)/);
  assert.match(sdkconfig, /CONFIG_IDF_TARGET="esp32c3"/);
  assert.match(sdkconfig, /CONFIG_FREERTOS_UNICORE=y/);
  assert.match(setup, /install\.ps1"\) esp32c3/);
  assert.match(setup, /esp-adf-libs/);
  assert.doesNotMatch(component, /REQUIRES[\s\S]*\b(?:arduino|Adafruit)\b/);
  assert.match(component, /target_compile_options\([^)]*PRIVATE -O3\)/);
});

test("native board profile maps OLED, controls and stereo PDM pins", () => {
  const board = read("main", "board_config.h");
  const audio = read("main", "native_audio_output.c");

  assert.match(board, /BOARD_OLED_SDA GPIO_NUM_5/);
  assert.match(board, /BOARD_OLED_SCL GPIO_NUM_6/);
  assert.match(board, /BOARD_AUDIO_LEFT_DATA GPIO_NUM_10/);
  assert.match(board, /BOARD_AUDIO_RIGHT_DATA GPIO_NUM_3/);
  assert.match(board, /BOARD_BOOT_BUTTON GPIO_NUM_9/);
  assert.match(board, /BOARD_AUDIO_LED GPIO_NUM_8/);
  assert.match(audio, /I2S_PDM_TX_SLOT_DAC_DEFAULT_CONFIG/);
  assert.match(audio, /I2S_SLOT_MODE_STEREO/);
  assert.match(audio, /\.dout2 = BOARD_AUDIO_RIGHT_DATA/);
  assert.match(audio, /pdm_queue_frame\(int16_t left, int16_t right\)/);
  assert.doesNotMatch(audio, /pcm_mono_sample/);
});

test("native OLED driver uses the 72x40 geometry and controller offset", () => {
  const header = read("main", "oled_display.h");
  const source = read("main", "oled_display.c");

  assert.match(header, /OLED_DISPLAY_WIDTH 72/);
  assert.match(header, /OLED_DISPLAY_HEIGHT 40/);
  assert.match(source, /OLED_COLUMN_OFFSET 28/);
  assert.match(source, /0xa8, 0x27/);
  assert.match(source, /0xad, 0x30/);
  assert.match(source, /BOARD_OLED_CONTRAST/);
});

test("single-core pipeline never pins work to nonexistent core 1", () => {
  const app = read("main", "app_main.c");
  const audio = read("main", "audio_service.c");

  assert.doesNotMatch(app, /xTaskCreatePinnedToCore/);
  assert.doesNotMatch(audio, /xTaskCreatePinnedToCore/);
  assert.match(audio, /xTaskCreate\(output_task/);
});

test("native partition table stays compatible with min_spiffs", () => {
  const partitions = read("partitions.csv");

  assert.match(partitions, /app0,\s+app,\s+ota_0,\s+0x10000,\s+0x1E0000/);
  assert.match(partitions, /app1,\s+app,\s+ota_1,\s+0x1F0000,\s+0x1E0000/);
  assert.match(partitions, /spiffs,\s+data,\s+spiffs,\s+0x3D0000,\s+0x20000/);
});

