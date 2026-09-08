const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("native AAC block default matches a PDM32 DMA payload and retains A/B control", () => {
  const cmake = read("esp8266", "rtos-sdk-native", "components", "helix_codecs", "CMakeLists.txt");
  assert.match(cmake, /option\(YORADIO_ESP8266_AAC_BLOCK_OUTPUT[^\n]+ON\)/);
  assert.match(cmake, /set\(YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES "512" CACHE/);
  assert.match(cmake, /32\|64\|128\|256\|512/);
  const runner = read("tools", "esp8266_audio_profile", "run_aac_block_matrix.ps1");
  assert.match(runner, /--flash_mode keep --flash_size 4MB --flash_freq keep 0x10000/);
  assert.match(runner, /monitor_esp8266.py --port \$Port --reset/);
  assert.match(runner, /restore the ordinary app/);
});

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
  assert.match(benchmark, /kMeasuredFrames\s*=\s*YORADIO_ESP8266_CODEC_RAM_FRAMES/);
  assert.match(cmake, /set\(YORADIO_ESP8266_CODEC_RAM_FRAMES "200" CACHE/);
  assert.match(cmake, /YORADIO_ESP8266_CODEC_RAM_FRAMES GREATER 10000/);
  assert.match(benchmark, /kLifecycleCycles\s*=\s*50/);
  assert.match(benchmark, /lifecycle creates=%u switches=%u/);
  assert.match(benchmark, /delta != 0/);
  assert.match(benchmark, /esp_timer_get_time\(\)[\s\S]*helix_codec_commit/);
  assert.match(benchmark, /s_stage_started\[stage\] = esp_timer_get_time\(\)/);
  assert.match(benchmark, /stage=%s time=%u us avg=%u us max=%u us/);
  assert.match(benchmark, /elapsed_signed < 0[\s\S]*rejected_samples/);
  assert.doesNotMatch(benchmark, /soc_get_ccount\(\)/);
  assert.match(cmake, /YORADIO_ESP8266_HELIX_STAGE_PROFILE/);
  assert.doesNotMatch(benchmark, /network_service|lwip_/);
  assert.match(benchmark, /"Info"[\s\S]*"Xing"[\s\S]*"VBRI"/);
  assert.match(benchmark, /!index_frame && \(!independent_only \|\| reservoir == 0U\)/);
  assert.match(benchmark, /output\.pcm_or = 0/);
  assert.match(benchmark, /INVALID benchmark: PCM is all zero/);
});

test("RAM decoder-to-DMA comparison is opt-in and never persists test settings", () => {
  const cmake = read("esp8266", "rtos-sdk-native", "main", "CMakeLists.txt");
  const source = read("esp8266", "rtos-sdk-native", "main", "codec_ram_benchmark.cpp");
  assert.match(cmake, /option\(YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT[\s\S]*?OFF\)/);
  assert.match(cmake, /RAM audio output requires CODEC_RAM_BENCHMARK/);
  assert.match(cmake, /option\(YORADIO_ESP8266_DMA_COMMITTED_PREFIX[\s\S]*?ON\)/);
  assert.match(source, /#if YORADIO_ESP8266_CODEC_RAM_AUDIO_OUTPUT\s+if \(output->physical_output && native_audio_output_write/);
  assert.match(source, /persistent_settings_update_runtime\(&settings\)/);
  assert.doesNotMatch(source, /persistent_settings_(save|commit)|nvs_set|nvs_commit|nvs_flash_erase/);
  assert.match(source, /physical wall=%u us audio=%u us eof=%u underrun=%u partial=%u fifo_empty=%u prefix=%u/);
});

test("MP3 matrix runs stored 64/128/320 inputs and excludes AAC", () => {
  const cmake = read("esp8266", "rtos-sdk-native", "main", "CMakeLists.txt");
  const source = read("esp8266", "rtos-sdk-native", "main", "codec_ram_benchmark.cpp");
  assert.match(cmake, /option\(YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX[\s\S]*?OFF\)/);
  assert.match(cmake, /mp3_composite\/mix-064.mp3[\s\S]*mp3_composite\/mix-320.mp3/);
  for(const rate of [64,128,320]) assert.ok(source.includes('run_codec("MP3/mix/'+rate+'"'));
  assert.match(source, /#if CONFIG_YORADIO_HELIX_AAC && !YORADIO_ESP8266_CODEC_RAM_MP3_MATRIX/);
  assert.match(source, /#if CONFIG_YORADIO_HELIX_AAC\s+run_codec\("AAC"/);
  assert.match(source, /first_mp3_frame\(input, bytes, false\)/);
  assert.match(source, /cursor \+= size_t\(frame\.data - input\) \+ frame\.size/);
  assert.match(source, /memcpy\(input, fixture\.data \+ cursor, bytes\)/);
  assert.match(source, /helix_codec_write_pointer\(codec, &capacity\)/);
  assert.doesNotMatch(source, /kMaxFixtureBytes|48U \* 1024U/);
  const production = read("tools", "esp8266_audio_profile", "build_i2s_pdm_production.ps1");
  assert.match(production, /-DYORADIO_ESP8266_CODEC_RAM_MP3_MATRIX=OFF/);
});

test("AAC flash matrix is isolated and normal production clears it", () => {
  const cmake = read("esp8266", "rtos-sdk-native", "main", "CMakeLists.txt");
  const source = read("esp8266", "rtos-sdk-native", "main", "codec_ram_benchmark.cpp");
  assert.match(cmake, /option\(YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX[\s\S]*?OFF\)/);
  assert.match(cmake, /AAC matrix requires benchmark, AAC enabled, and MP3 matrix OFF/);
  for (const rate of [48, 64, 96])
    assert.ok(source.includes('run_codec("AAC/mix/'+rate+'"'));
  assert.match(source, /FrameView frame = first_aac_frame\(input, bytes\)/);
  assert.match(source, /#if YORADIO_ESP8266_CODEC_RAM_AAC_MATRIX\s+const helix_codec_kind_t initial_kind = HELIX_CODEC_AAC/);
  assert.match(read("tools", "esp8266_audio_profile", "build_i2s_pdm_production.ps1"),
    /-DYORADIO_ESP8266_CODEC_RAM_AAC_MATRIX=OFF/);
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
