const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main");
const app = fs.readFileSync(path.join(root, "app_main.c"), "utf8");
const bench = fs.readFileSync(path.join(root, "audio_output_benchmark.c"), "utf8");
const cmake = fs.readFileSync(path.join(root, "CMakeLists.txt"), "utf8");

test("ESP8266 output benchmark generates deterministic PCM without Wi-Fi or codecs", () => {
  assert.match(cmake, /option\(YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK/);
  assert.match(cmake, /audio_output_benchmark\.c/);
  assert.match(
    app,
    /YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK[\s\S]*audio_output_benchmark_run\(\)[\s\S]*#elif YORADIO_ESP8266_CODEC_RAM_BENCHMARK/,
  );
  assert.match(bench, /#define BENCHMARK_FRAMES 128U/);
  assert.match(bench, /static int16_t s_pcm\[BENCHMARK_FRAMES \* BENCHMARK_CHANNELS\]/);
  assert.match(bench, /native_audio_output_write\(/);
  assert.doesNotMatch(bench, /helix_codec|network_service|lwip|WiFi/);
});

test("ESP8266 output benchmark reports queue wait, CPU idle, and heap", () => {
  assert.match(bench, /audio_output_benchmark_spi_wait_begin/);
  assert.match(bench, /spi_wait=.*calls=.*avg=.*max=/);
  assert.match(bench, /uxTaskGetSystemState/);
  assert.match(bench, /cpu busy=.*idle=/);
  assert.match(bench, /esp_get_free_heap_size/);
  assert.match(bench, /esp_get_minimum_free_heap_size/);
});
