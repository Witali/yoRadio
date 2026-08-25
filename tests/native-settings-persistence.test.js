const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("native boards share Arduino-compatible persistent audio settings", () => {
  const header = read(
    "idf",
    "components",
    "native_audio_settings",
    "native_audio_settings.h",
  );
  const source = read(
    "idf",
    "components",
    "native_audio_settings",
    "native_audio_settings.c",
  );
  const arduinoPlayer = read("yoRadio", "src", "core", "player.cpp");
  const arduinoConfig = read("yoRadio", "src", "core", "config.cpp");

  assert.match(header, /NATIVE_AUDIO_DEFAULT_VOLUME 192U/);
  assert.match(header, /NATIVE_AUDIO_VOLUME_SAVE_DELAY_MS 3000U/);
  assert.match(source, /AUDIO_NVS_NAMESPACE "audio"/);
  assert.match(source, /AUDIO_NVS_VOLUME "volume"/);
  assert.match(source, /AUDIO_NVS_BALANCE "balance"/);
  assert.match(source, /nvs_get_u8/);
  assert.match(source, /nvs_get_i8/);
  assert.match(source, /nvs_set_u8/);
  assert.match(source, /nvs_set_i8/);
  assert.match(source, /esp_timer_start_once/);
  assert.match(arduinoPlayer, /millis\(\)-_volTicks\)>3000/);
  assert.match(arduinoConfig, /setBalance[\s\S]*saveValue\(&store\.balance/);
});

for (const board of ["esp32c3-oled-native", "esp32-cyd2usb-native"]) {
  test(`${board} initializes and consumes shared audio settings`, () => {
    const project = read("idf", board, "CMakeLists.txt");
    const component = read("idf", board, "main", "CMakeLists.txt");
    const app = read("idf", board, "main", "app_main.c");
    const output = read("idf", board, "main", "native_audio_output.c");

    assert.match(project, /components\/native_audio_settings/);
    assert.match(component, /native_audio_settings/);
    assert.match(app, /native_audio_settings_init\(\)/);
    assert.match(output, /native_audio_settings_get_volume\(\)/);
    assert.match(output, /native_audio_settings_get_balance\(\)/);
    assert.match(output, /native_audio_settings_set_volume\(volume\)/);
    assert.match(output, /native_audio_settings_set_balance\(balance\)/);
  });
}

test("native balance direction matches Arduino on both ESP32 targets", () => {
  for (const board of ["esp32c3-oled-native", "esp32-cyd2usb-native"]) {
    const output = read("idf", board, "main", "native_audio_output.c");
    assert.match(
      output,
      /left_balance\s*=\s*balance < 0 \?[^;]+BALANCE_DENOMINATOR \+ balance/s,
    );
    assert.match(
      output,
      /right_balance\s*=\s*balance > 0 \?[^;]+BALANCE_DENOMINATOR - balance/s,
    );
  }
});

test("C3 persists Arduino three-state Smart Start and exposes it to WebUI", () => {
  const radio = read("idf", "esp32c3-oled-native", "main", "radio_control.c");
  const websocket = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "websocket_service.c",
  );

  assert.match(radio, /SMARTSTART_STOPPED 0U/);
  assert.match(radio, /SMARTSTART_PLAYING 1U/);
  assert.match(radio, /SMARTSTART_DISABLED 2U/);
  assert.match(radio, /nvs_get_u8\(handle, RADIO_NVS_SMARTSTART/);
  assert.match(radio, /nvs_set_u8\(handle, RADIO_NVS_SMARTSTART/);
  assert.match(radio, /s_smartstart == SMARTSTART_PLAYING[\s\S]*play_locked/);
  assert.match(radio, /radio_control_stop[\s\S]*update_smartstart_play_state\(false\)/);
  assert.match(websocket, /\\"sst\\":%u/);
  assert.match(websocket, /strcmp\(command, "smartstart"\)/);
  assert.match(websocket, /radio_control_stop\(\)/);
});

test("classic ESP32 native HTTP API reports and changes persisted gain", () => {
  const web = read("idf", "esp32-cyd2usb-native", "main", "web_service.c");
  const output = read(
    "idf",
    "esp32-cyd2usb-native",
    "main",
    "native_audio_output.c",
  );

  assert.match(web, /"\/api\/native\/settings"/);
  assert.match(web, /native_audio_output_set_volume/);
  assert.match(web, /native_audio_output_set_balance/);
  assert.match(web, /native_audio_output_get_volume/);
  assert.match(web, /native_audio_output_get_balance/);
  assert.match(output, /channel_gain_q15/);
  assert.match(output, /pcm_mono_sample[\s\S]*volume, balance/);
});

test("C3 persists, reports, and applies WebUI normalization settings", () => {
  const header = read(
    "idf",
    "components",
    "native_audio_settings",
    "native_audio_settings.h",
  );
  const settings = read(
    "idf",
    "components",
    "native_audio_settings",
    "native_audio_settings.c",
  );
  const websocket = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "websocket_service.c",
  );
  const output = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "native_audio_output.c",
  );
  const cmake = read("idf", "esp32c3-oled-native", "main", "CMakeLists.txt");

  assert.match(header, /NATIVE_AUDIO_DEFAULT_NORMALIZATION false/);
  assert.match(
    header, /NATIVE_AUDIO_DEFAULT_NORMALIZATION_TIME_MS 5000U/,
  );
  for (const key of ["normalize", "normgain", "normtarget", "normtime"]) {
    assert.match(settings, new RegExp(`AUDIO_NVS_[A-Z_]+ "${key}"`));
  }
  assert.match(settings, /nvs_get_u16\(\s*handle, AUDIO_NVS_NORMALIZATION_TIME/);
  assert.match(settings, /nvs_set_u16\(handle, key, value\)/);
  assert.match(settings, /native_audio_settings_set_normalization\(bool enabled\)/);
  assert.match(settings, /native_audio_settings_set_normalization_gain_db/);
  assert.match(settings, /native_audio_settings_set_normalization_target_dbfs/);
  assert.match(settings, /native_audio_settings_set_normalization_time_ms/);

  for (const command of ["normalization", "normgain", "normtarget", "normtime"]) {
    assert.match(websocket, new RegExp(`strcmp\\(command, "${command}"\\)`));
  }
  assert.match(websocket, /native_audio_settings_get_normalization\(\)/);
  assert.match(websocket, /native_audio_settings_get_normalization_gain_db\(\)/);
  assert.match(websocket, /native_audio_settings_get_normalization_target_dbfs\(\)/);
  assert.match(websocket, /native_audio_settings_get_normalization_time_ms\(\)/);
  assert.doesNotMatch(websocket, /\\"normalize\\":0,\\"normgain\\":20/);

  const normalize = output.indexOf("native_audio_normalizer_process_block");
  const volume = output.indexOf("scale_sample_q15(left, left_gain_q15)");
  assert.ok(normalize >= 0 && normalize < volume);
  assert.match(cmake, /AudioNormalizer\.cpp/);
});
