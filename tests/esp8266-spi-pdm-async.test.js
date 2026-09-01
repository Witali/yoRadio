const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main");
const output = fs.readFileSync(path.join(root, "native_audio_output.c"), "utf8");
const component = fs.readFileSync(path.join(root, "CMakeLists.txt"), "utf8");
const board = fs.readFileSync(path.join(root, "board_config.h"), "utf8");
const input = fs.readFileSync(path.join(root, "input_service.c"), "utf8");
const radio = fs.readFileSync(path.join(root, "radio_control.c"), "utf8");
const network = fs.readFileSync(path.join(root, "network_service.c"), "utf8");
const pdmConfig = fs.readFileSync(path.join(root, "spi_pdm_config.h"), "utf8");
const kconfig = fs.readFileSync(path.join(root, "Kconfig.projbuild"), "utf8");
const pdm8Profile = fs.readFileSync(
  path.join(root, "..", "sdkconfig.helix-sso-qio80-pdm8.defaults"),
  "utf8",
);

test("ESP8266 keeps 16x PDM by default and offers an explicit 384 kHz PDM8 profile", () => {
  assert.match(kconfig, /default YORADIO_SPI_PDM_OVERSAMPLE_16/);
  assert.match(pdm8Profile, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);
  assert.match(pdm8Profile, /CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y/);
  assert.match(pdmConfig, /BOARD_SPI_PDM_OVERSAMPLE 8U/);
  assert.match(pdmConfig, /BOARD_SPI_PDM_BIT_RATE_HZ 384615U/);
  assert.match(pdmConfig, /BOARD_SPI_PDM_CLOCK_PREDIV 25U/);
  assert.match(output, /SPI1\.clock\.clkdiv_pre = BOARD_SPI_PDM_CLOCK_PREDIV/);
});

test("ESP8266 SPI-PDM drains a bounded queue from the transfer-done interrupt", () => {
  assert.match(output, /#define SPI_PDM_QUEUE_CHUNKS 12U/);
  assert.match(output, /\.intr_enable = \{\.trans_done = 1\}/);
  assert.match(output, /\.event_cb = spi_pdm_event/);
  assert.match(
    output,
    /IRAM_ATTR spi_pdm_event[\s\S]*SPI_TRANS_DONE_EVENT[\s\S]*spi_pdm_start_next_locked\(\)[\s\S]*vTaskNotifyGiveFromISR/,
  );
});

test("ESP8266 SPI-PDM producer sleeps only when its bounded queue is full", () => {
  assert.match(
    output,
    /spi_pdm_acquire[\s\S]*s_spi_queue_count < SPI_PDM_QUEUE_CHUNKS/,
  );
  assert.match(output, /spi_pdm_commit[\s\S]*spi_pdm_start_next_locked\(\)/);
  assert.match(output, /ulTaskNotifyTake\(pdTRUE,/);
  assert.doesNotMatch(output, /while \(SPI1\.cmd\.usr\)/);
  assert.doesNotMatch(output, /spi_trans\(HSPI_HOST/);
  assert.doesNotMatch(component, /--wrap=spi_trans/);
});

test("ESP8266 PDM producer fills a reserved queue slot without an intermediate copy", () => {
  const write = output.slice(
    output.indexOf("esp_err_t native_audio_output_write"),
    output.indexOf("void native_audio_output_silence"),
  );
  assert.match(
    output,
    /spi_pdm_acquire\(&?chunk\)[\s\S]*\(\*chunk\)->words\[word\][\s\S]*spi_pdm_commit\(\*chunk,/,
  );
  assert.doesNotMatch(write, /uint32_t words\[SPI_PDM_CHUNK_WORDS\]/);
  assert.doesNotMatch(
    output,
    /chunk->words\[index\]\s*=\s*words\[index\]/,
  );
});

test("ESP8266 SPI-PDM drains queued sound before forcing silence", () => {
  assert.match(
    output,
    /void native_audio_output_silence\(void\)[\s\S]*spi_pdm_wait_idle\(\)[\s\S]*spi_pdm_acquire\(&silence\)[\s\S]*spi_pdm_commit\(silence, SPI_PDM_CHUNK_BITS\)[\s\S]*spi_pdm_wait_idle\(\)/,
  );
});

test("ESP8266 input task has enough board-specific stack to open SPIFFS playlist", () => {
  assert.match(board, /#define BOARD_TASK_STACK_INPUT 3072/);
  assert.match(input, /xTaskCreate\(input_task, "input", BOARD_TASK_STACK_INPUT,/);
});
test("ESP8266 audio profile can auto-start a reproducible HTTP stream", () => {
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE=1/);
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE_URL/);
  assert.match(
    radio,
    /#ifdef YORADIO_ESP8266_AUDIO_PROFILE_URL[\s\S]*audio_service_play\([\s\S]*YORADIO_ESP8266_AUDIO_PROFILE_URL/,
  );
});
test("ESP8266 audio profile can use an explicit static IPv4 test network", () => {
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP/);
  assert.match(network, /#ifdef YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP/);
  assert.match(network, /tcpip_adapter_dhcpc_stop\(TCPIP_ADAPTER_IF_STA\)/);
  assert.match(network, /tcpip_adapter_set_ip_info/);
});
test("ESP8266 audio profile reports whole-CPU load and heap use", () => {
  const profile = fs.readFileSync(
    path.join(root, "audio_profile_wrappers.cpp"),
    "utf8",
  );
  const defaults = fs.readFileSync(
    path.join(root, "..", "sdkconfig.audio-profile.defaults"),
    "utf8",
  );

  assert.match(defaults, /CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y/);
  assert.match(profile, /uxTaskGetSystemState/);
  assert.match(profile, /cpu busy=%u\.%u%% idle=%u\.%u%%/);
  assert.match(profile, /esp_get_free_heap_size\(\)/);
  assert.match(profile, /esp_get_minimum_free_heap_size\(\)/);
  assert.match(profile, /heap total=%u used=%u free=%u min_free=%u/);
});
test("ESP8266 streaming profile reports internal MP3 and AAC decoder stages", () => {
  const profile = fs.readFileSync(
    path.join(root, "audio_profile_wrappers.cpp"),
    "utf8",
  );
  const defaults = fs.readFileSync(
    path.join(root, "..", "sdkconfig.audio-profile-qio80-pdm8.defaults"),
    "utf8",
  );

  assert.match(profile, /codec_stage=%s time=%u\.%03u ms/);
  assert.match(profile, /helix_stage_profile_begin/);
  assert.match(profile, /helix_stage_profile_end/);
  assert.match(profile, /"huffman", "dequant", "stereo_filter", "imdct"/);
  assert.match(defaults, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);
  assert.match(defaults, /CONFIG_YORADIO_HELIX_AAC=y/);
  assert.match(defaults, /CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y/);
  assert.match(defaults, /CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y/);
});
test("ESP8266 decode-only profile bypasses PDM while counting decoded PCM", () => {
  const profile = fs.readFileSync(
    path.join(root, "audio_profile_wrappers.cpp"),
    "utf8",
  );

  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY/);
  assert.ok(
    profile.includes("#if YORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY"),
  );
  assert.ok(profile.includes("esp_err_t result = ESP_OK;"));
  assert.ok(profile.includes("__real_native_audio_output_write("));
  assert.ok(
    profile.includes(
      "s_audio_us += static_cast<uint64_t>(sample_count / channels)",
    ),
  );
});
