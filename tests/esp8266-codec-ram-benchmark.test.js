const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("ESP8266 RAM codec benchmark embeds golden fixtures and bypasses services", () => {
  const cmake = read("esp8266", "rtos-sdk-native", "main", "CMakeLists.txt");
  const app = read("esp8266", "rtos-sdk-native", "main", "app_main.c");
  const benchmark = read(
    "esp8266", "rtos-sdk-native", "main", "codec_ram_benchmark.cpp",
  );

  assert.match(cmake, /YORADIO_ESP8266_CODEC_RAM_BENCHMARK/);
  assert.match(cmake, /tests\/fixtures\/helix_golden\/stereo-320\.mp3/);
  assert.match(cmake, /tests\/fixtures\/helix_golden\/stereo-320\.aac/);
  assert.match(
    app,
    /YORADIO_ESP8266_CODEC_RAM_BENCHMARK[\s\S]*codec_ram_benchmark_run\(\)[\s\S]*#else/,
  );
  assert.match(benchmark, /memcpy\(frame_ram, fixture\.data, fixture\.size\)/);
  assert.match(benchmark, /kMeasuredFrames\s*=\s*200/);
  assert.match(benchmark, /esp_timer_get_time\(\)[\s\S]*helix_codec_commit/);
  assert.match(benchmark, /s_stage_started\[stage\] = esp_timer_get_time\(\)/);
  assert.match(benchmark, /stage=%s time=%u us avg=%u us max=%u us/);
  assert.match(benchmark, /elapsed_signed < 0[\s\S]*rejected_samples/);
  assert.doesNotMatch(benchmark, /soc_get_ccount\(\)/);
  assert.match(cmake, /YORADIO_ESP8266_HELIX_STAGE_PROFILE/);
  assert.doesNotMatch(benchmark, /network_service|native_audio_output|lwip_/);
});

test("ESP8266 Helix stage hooks cover both MP3 and AAC hot paths", () => {
  const mp3 = read(
    "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.cpp",
  );
  const aac = read(
    "yoRadio", "src", "audioI2S", "aac_decoder", "aac_decoder.cpp",
  );
  for(const source of [mp3, aac]) {
    assert.match(source, /HELIX_PROFILE_BEGIN\(HELIX_STAGE_HUFFMAN\)/);
    assert.match(source, /HELIX_PROFILE_BEGIN\(HELIX_STAGE_DEQUANT\)/);
    assert.match(source, /HELIX_PROFILE_BEGIN\(HELIX_STAGE_IMDCT\)/);
  }
  assert.match(mp3, /HELIX_PROFILE_BEGIN\(HELIX_STAGE_SYNTHESIS\)/);
  assert.match(mp3, /HELIX_PROFILE_BEGIN\(HELIX_STAGE_SYNTHESIS_DCT\)/);
  assert.match(
    mp3,
    /HELIX_PROFILE_BEGIN\(HELIX_STAGE_SYNTHESIS_POLYPHASE\)/,
  );
});
