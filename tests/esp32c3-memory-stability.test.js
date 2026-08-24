const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.resolve(__dirname, "..");
const nativeMain = path.join(root, "idf", "esp32c3-oled-native", "main");
const read = (file) => fs.readFileSync(file, "utf8");

test("ESP32-C3 defaults to 16 KiB but permits a larger compressed-audio buffer", () => {
  const header = read(path.join(nativeMain, "runtime_settings.h"));
  const settings = read(path.join(nativeMain, "runtime_settings.c"));
  const websocket = read(path.join(nativeMain, "websocket_service.c"));
  const webUi = zlib.gunzipSync(
    fs.readFileSync(path.join(root, "yoRadio", "data", "www", "script.js.gz"))
  ).toString("utf8");

  assert.match(header, /RUNTIME_MAX_AUDIO_BUFFER_BLOCKS 14U/);
  assert.match(header, /RUNTIME_DEFAULT_AUDIO_BUFFER_BLOCKS 10U/);
  assert.match(settings, /nvs_open\(SETTINGS_NVS_NAMESPACE, NVS_READWRITE/);
  assert.match(settings, /u8 > RUNTIME_MAX_AUDIO_BUFFER_BLOCKS/);
  assert.match(settings, /nvs_set_u8\(handle, SETTINGS_NVS_AUDIO_BUFFER, u8\)/);
  assert.match(websocket, /\\"abuffmax\\":%u/);
  assert.match(websocket, /RUNTIME_MAX_AUDIO_BUFFER_BLOCKS/);
  assert.match(webUi, /id=="abuffmax"/);
  assert.match(webUi, /audioBuffer\.max=value/);
});

test("ESP32-C3 reuses stream workspaces and logs fragmentation headroom", () => {
  const defaults = read(
    path.join(root, "idf", "esp32c3-oled-native", "sdkconfig.defaults")
  );
  const audio = read(path.join(nativeMain, "audio_service.c"));

  assert.match(defaults, /# CONFIG_MBEDTLS_DYNAMIC_BUFFER is not set/);
  assert.doesNotMatch(defaults, /^CONFIG_MBEDTLS_DYNAMIC_BUFFER=y$/m);
  assert.match(audio, /static char s_icy_metadata\[ICY_METADATA_MAX \+ 1\]/);
  assert.doesNotMatch(audio, /malloc\(ICY_METADATA_MAX \+ 1\)/);
  assert.match(audio, /if \(output_size < DECODE_BUFFER_INITIAL\)/);
  assert.match(audio, /heap_caps_get_largest_free_block\(MALLOC_CAP_8BIT\)/);
  assert.match(audio, /heap_caps_get_minimum_free_size\(MALLOC_CAP_8BIT\)/);
  assert.match(audio, /uxTaskGetStackHighWaterMark\(NULL\)/);
  assert.match(audio, /log_runtime_memory\("after TLS handshake"\)/);
  assert.match(audio, /log_runtime_memory\("after first decoded frame"\)/);
  assert.match(audio, /log_runtime_memory\("at stream read failure"\)/);
});
