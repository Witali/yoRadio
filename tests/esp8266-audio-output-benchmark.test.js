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
  assert.match(bench, /spi_wait=.*calls=.*avg=.*max=.*invalid=/);
  assert.match(bench, /spi_gap cycles=.*calls=.*avg=.*max=.*empty=/);
  assert.match(bench, /native_audio_output_reset_spi_stats/);
  assert.match(bench, /elapsed64 < 0 \|\| elapsed64 > 200000/);
  assert.match(bench, /uxTaskGetSystemState/);
  assert.match(bench, /cpu busy=.*idle=/);
  assert.match(bench, /esp_get_free_heap_size/);
  assert.match(bench, /esp_get_minimum_free_heap_size/);
});
test("ESP8266 gated tone profile emits an exact full-scale 1 kHz sine", () => {
  assert.match(cmake, /option\(YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST/);
  assert.match(
    cmake,
    /YORADIO_ESP8266_AUDIO_OUTPUT_TONE_TEST AND[\s\S]*NOT YORADIO_ESP8266_AUDIO_OUTPUT_BENCHMARK/,
  );
  const table = bench.match(
    /s_sine_1khz\[TONE_PERIOD_FRAMES\] = \{([\s\S]*?)\};/,
  );
  assert.ok(table);
  const actual = table[1].match(/-?\d+/g).map(Number);
  const expected = Array.from({ length: 48 }, (_, index) =>
    Math.round(32767 * Math.sin((2 * Math.PI * index) / 48)),
  );
  assert.deepEqual(actual, expected);
  assert.match(bench, /TONE_HALF_CYCLE_FRAMES \(BENCHMARK_SAMPLE_RATE \/ 2U\)/);
  assert.match(bench, /TONE_GATE_CYCLE_FRAMES BENCHMARK_SAMPLE_RATE/);
  assert.match(bench, /settings\.normalization_enabled = false/);
  assert.match(bench, /settings\.volume = 254/);
  assert.match(bench, /500 ms on \/ 500 ms silence/);
});

test("PDM comparison measures the actual packer before DMA without persisting test settings", () => {
  const output = fs.readFileSync(path.join(root, 'native_audio_output.c'), 'utf8');
  assert.match(cmake, /option\(YORADIO_ESP8266_OUTPUT_COMPARE[\s\S]*?OFF\)/);
  assert.match(cmake, /OUTPUT_COMPARE requires finite generated PCM and I2S PDM32 or RCPDM32/);
  assert.match(output, /#if YORADIO_ESP8266_OUTPUT_COMPARE\s+[\s\S]*?uint32_t native_audio_output_benchmark_pack32/);
  const wrapper = output.match(/uint32_t native_audio_output_benchmark_pack32[\s\S]*?return checksum;\s*}/)[0];
  assert.match(wrapper, /checksum \^= i2s_pdm_pack32\(pcm\[i\]\)/);
  assert.doesNotMatch(wrapper, /malloc|calloc|i2s_pdm_push|reserve|commit/);
  assert.ok(bench.indexOf('native_audio_output_benchmark_pack32(s_template') < bench.indexOf('result = native_audio_output_init()'));
  assert.match(bench, /persistent_settings_update_runtime\(&settings\)/);
  assert.doesNotMatch(bench, /persistent_settings_save|nvs_set/);
  assert.match(bench, /write_us - s_spi_wait_us/);
  assert.match(bench, /wall-time estimate, not total CPU load/);
  assert.equal((bench.match(/esp_timer_get_time\(\)/g) || []).length, 1);
  assert.match(bench, /taskENTER_CRITICAL\(\);\s*int64_t stamp = esp_timer_get_time\(\);\s*taskEXIT_CRITICAL\(\);/);
});
