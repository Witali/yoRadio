const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const nativeRoot = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) =>
  fs.readFileSync(path.join(nativeRoot, ...parts), "utf8");

test("repository default setup and build select native ESP-IDF firmware", () => {
  const setup = fs.readFileSync(path.join(root, "setup.ps1"), "utf8");
  const build = fs.readFileSync(path.join(root, "build.ps1"), "utf8");

  assert.match(setup, /idf\\esp32c3-oled-native\\setup\.ps1/);
  assert.match(build, /idf\\esp32c3-oled-native\\build\.ps1/);
  assert.match(build, /IdfArguments = @\("build"\)/);
  assert.doesNotMatch(setup + build, /arduino-cli/);
});

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
  const defaults = read("sdkconfig.defaults");

  assert.match(board, /BOARD_OLED_SDA GPIO_NUM_5/);
  assert.match(board, /BOARD_OLED_SCL GPIO_NUM_6/);
  assert.match(board, /BOARD_AUDIO_LEFT_DATA GPIO_NUM_10/);
  assert.match(board, /BOARD_AUDIO_RIGHT_DATA GPIO_NUM_3/);
  assert.match(board, /BOARD_BOOT_BUTTON GPIO_NUM_9/);
  assert.match(defaults, /CONFIG_YORADIO_AUDIO_LEVEL_LED_GPIO=8/);
  assert.match(audio, /audio_level_led_update_peak\(peak\)/);
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

test("native OLED brightness uses the shared 0..100 setting and persists it", () => {
  const component = read("main", "CMakeLists.txt");
  const header = read("main", "oled_display.h");
  const display = read("main", "oled_display.c");
  const settings = read("main", "display_settings.c");
  const app = read("main", "app_main.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(component, /display_settings\.c/);
  assert.match(header, /oled_display_set_brightness/);
  assert.match(display, /brightness \* 255U \+ 50U\) \/ 100U/);
  assert.match(display, /\{0x81, controller_contrast\}/);
  assert.match(settings, /DISPLAY_NVS_NAMESPACE "display"/);
  assert.match(settings, /DISPLAY_NVS_BRIGHTNESS "brightness"/);
  assert.match(settings, /nvs_get_u8/);
  assert.match(settings, /nvs_set_u8/);
  assert.match(settings, /nvs_commit/);
  assert.match(app, /display_settings_init\(&s_display\)/);
  assert.match(websocket, /display_settings_get_brightness\(\)/);
  assert.match(websocket, /strcmp\(command, "brightness"\)/);
  assert.match(websocket, /display_settings_set_brightness[\s\S]*true/);
  assert.match(websocket, /\\"br\\":%u/);
});

test("native OLED uses 15-pixel Spleen rows, inverse station and smooth scroll", () => {
  const header = read("main", "oled_display.h");
  const source = read("main", "oled_display.c");
  const app = read("main", "app_main.c");
  const font = read("main", "font8x15.h");

  assert.match(header, /oled_display_draw_large_text/);
  assert.match(header, /OLED_LARGE_GLYPH_WIDTH 8/);
  assert.match(header, /OLED_LARGE_GLYPH_HEIGHT 15/);
  assert.match(source, /font8x15 \+ \(size_t\)glyph \* OLED_LARGE_GLYPH_HEIGHT/);
  assert.match(source, /font8x15_unicode_80_bf/);
  assert.match(source, /\*glyph = 0x7f/);
  assert.match(font, /Spleen 8x16/);
  assert.match(font, /Fixed 8x15 cells/);
  assert.match(font, /font8x15\[3840\]/);
  assert.match(app, /state->station[\s\S]*state->title/);
  assert.match(app, /state->station[\s\S]*station_scroll->enabled, true/);
  assert.match(app, /state->title[\s\S]*title_scroll->enabled, false/);
  assert.match(app, /DISPLAY_SCROLL_HOLD_MS 3500U/);
  assert.match(app, /DISPLAY_SCROLL_STEP_MS 35U/);
  assert.match(app, /IPSTR[\s\S]*oled_display_draw_compact_text/);
  assert.doesNotMatch(app, /state->stream_format[\s\S]*oled_display_draw/);
});

test("native OLED normalizes dash variants before the replacement glyph", () => {
  const source = read("main", "oled_display.c");
  const normalization = source.indexOf("is_ascii_dash_equivalent(codepoint)");
  const unicodeLookup = source.indexOf("font8x15_unicode_80_bf[index]");
  const fallback = source.indexOf("*glyph = 0x7f");

  for (const codepoint of [
    "0x2010",
    "0x2011",
    "0x2012",
    "0x2013",
    "0x2014",
    "0x2015",
    "0x2212",
  ]) {
    assert.match(source, new RegExp(`case ${codepoint}:`));
  }
  assert.match(
    source,
    /is_ascii_dash_equivalent\(codepoint\)[\s\S]*\*glyph = '-'/,
  );
  assert.ok(normalization >= 0);
  assert.ok(normalization < unicodeLookup);
  assert.ok(unicodeLookup < fallback);
});

test("native radio requests and publishes ICY song metadata", () => {
  const audio = read("main", "audio_service.c");
  const state = read("main", "native_state.h");
  const controls = read("main", "radio_control.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(audio, /Icy-MetaData", "1"/);
  assert.match(audio, /icy-metaint/);
  assert.match(audio, /StreamTitle='/);
  assert.match(audio, /native_state_set_title\(s_state, title\)/);
  assert.match(state, /char title\[192\]/);
  assert.match(websocket, /json_escape\(state\.title, title/);
  assert.match(controls, /native_state_set_station\(s_state, s_candidate_name\)/);
});

test("native WebUI publishes ICY or decoder bitrate instead of a constant zero", () => {
  const audio = read("main", "audio_service.c");
  const stateHeader = read("main", "native_state.h");
  const stateSource = read("main", "native_state.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(stateHeader, /uint32_t bitrate_kbps/);
  assert.match(stateHeader, /native_state_set_bitrate/);
  assert.match(stateSource, /state->bitrate_kbps = bitrate_kbps/);
  assert.match(audio, /get_response_header[\s\S]*"icy-br"/);
  assert.match(audio, /ICY bitrate: %lu kbit\/s/);
  assert.match(audio, /state_set_decoder_bitrate\(info->bitrate\)/);
  assert.match(audio, /state_set_decoder_bitrate\(latest_info\.bitrate\)/);
  assert.match(audio, /BITRATE_UPDATE_INTERVAL_US 1000000LL/);
  assert.match(audio, /STREAM_BITRATE_INTERVAL_US 5000000LL/);
  assert.match(
    audio,
    /meter->audio_bytes \* 8000000ULL[\s\S]*elapsed_us/,
  );
  assert.match(audio, /stream_bitrate_add\(command\.generation, &bitrate_meter/);
  assert.match(audio, /atomic_store\(&s_measured_bitrate_ready, true\)/);
  assert.match(audio, /Measured stream bitrate: %llu bit\/s/);
  assert.match(
    audio,
    /state_set_decoder_bitrate[\s\S]*atomic_load\(&s_measured_bitrate_ready\)[\s\S]*return/,
  );
  assert.match(
    audio,
    /frame\.decoded_size[\s\S]*esp_audio_simple_dec_get_info\(decoder, &latest_info\)[\s\S]*state_set_decoder_bitrate\(latest_info\.bitrate\)/,
  );
  assert.ok(
    audio.indexOf('client, "icy-br"') <
      audio.indexOf("state_set_decoder_bitrate(latest_info.bitrate)"),
    "decoder bitrate must override the earlier ICY fallback",
  );
  assert.match(websocket, /\\"bitrate\\",\\"value\\":%lu/);
  assert.match(websocket, /state\.bitrate_kbps/);
  assert.doesNotMatch(websocket, /\\"bitrate\\",\\"value\\":0/);
});

test("native BOOT gestures match the documented one-button controls", () => {
  const app = read("main", "app_main.c");
  const component = read("main", "CMakeLists.txt");
  const controls = read("main", "radio_control.c");

  assert.match(component, /radio_control\.c/);
  assert.match(app, /BUTTON_CLICK_WINDOW_MS 400/);
  assert.match(app, /BUTTON_HOLD_MS 800/);
  assert.match(app, /const bool next = clicks >= 2/);
  assert.match(app, /next \? radio_control_next\(\)/);
  assert.match(app, /: radio_control_toggle\(\)/);
  assert.match(app, /radio_control_previous\(\)/);
  assert.match(app, /xTaskCreate\(button_task, "boot_button", 4096/);
  assert.match(app, /BOOT two clicks: next station/);
  assert.match(controls, /static char s_playlist_line\[768\]/);
  assert.match(controls, /static char s_candidate_url\[512\]/);
  assert.doesNotMatch(controls, /char line\[768\]/);
});

test("single-core pipeline never pins work to nonexistent core 1", () => {
  const app = read("main", "app_main.c");
  const audio = read("main", "audio_service.c");

  assert.doesNotMatch(app, /xTaskCreatePinnedToCore/);
  assert.doesNotMatch(audio, /xTaskCreatePinnedToCore/);
  assert.match(audio, /xTaskCreate\(output_task/);
});

test("single-core decoder yields to idle and drops obsolete station data", () => {
  const audio = read("main", "audio_service.c");

  assert.match(audio, /\(stats\.calls & 31U\) == 0U[\s\S]*vTaskDelay\(1\)/);
  assert.match(
    audio,
    /packet->generation != atomic_load\(&s_generation\)[\s\S]*vRingbufferReturnItem\(s_encoded, packet\)/,
  );
  assert.match(
    audio,
    /packet->generation != atomic_load\(&s_generation\)[\s\S]*vRingbufferReturnItem\(s_pcm, packet\)/,
  );
  assert.match(audio, /packet->generation == failed_generation/);
  assert.match(audio, /failed_generation = generation/);
});

test("native ESP-IDF decoders advance past consumed compressed input", () => {
  const sources = [
    read("main", "audio_service.c"),
    fs.readFileSync(
      path.join(root, "idf", "esp32-cyd2usb-native", "main", "audio_service.c"),
      "utf8",
    ),
  ];

  for (const audio of sources) {
    assert.match(
      audio,
      /raw\.consumed = 0;[\s\S]*esp_audio_simple_dec_process[\s\S]*raw\.buffer \+= raw\.consumed;[\s\S]*raw\.len -= raw\.consumed;/,
    );
    assert.match(audio, /raw\.consumed > raw\.len/);
    assert.match(audio, /decoder made no input progress/);
  }
});

test("native decoder reports measured real-time headroom", () => {
  const audio = read("main", "audio_service.c");

  assert.match(audio, /esp_timer_get_time\(\)/);
  assert.match(audio, /stats\.decode_us \+= decode_call_us/);
  assert.match(audio, /stats->audio_us \+= frames \* 1000000ULL \/ info->sample_rate/);
  assert.match(audio, /"PERF %s: window %llu ms, audio %llu ms, decode %llu ms "/);
  assert.match(audio, /stats->audio_us \* 100ULL \/[\s\S]*stats->decode_us/);
});

test("native audio pipeline batches PCM and caches stable stream layout", () => {
  const audio = read("main", "audio_service.c");
  const output = read("main", "native_audio_output.c");

  assert.match(audio, /#define PCM_RING_SIZE \(16 \* 1024\)/);
  assert.match(audio, /#define PCM_PACKET_DATA_SIZE 7168/);
  assert.match(audio, /bool stream_info_ready = false/);
  assert.match(
    audio,
    /esp_audio_simple_dec_get_info\(decoder, &latest_info\)[\s\S]*!stream_info_ready[\s\S]*stream_info = latest_info[\s\S]*stream_info_ready = true/,
  );
  assert.match(output, /scale_sample_q15/);
  assert.match(output, /channel_gain_q15/);
  assert.doesNotMatch(output, /scale_sample\([^_]/);
});

test("native FLAC reuses the optimized yoRadio decoder without Arduino Core", () => {
  const audio = read("main", "audio_service.c");
  const cmake = read("components", "custom_flac", "CMakeLists.txt");
  const adapter = read("components", "custom_flac", "custom_flac_adapter.cpp");

  assert.match(cmake, /yoRadio\/src\/audioI2S\/flac_decoder/);
  assert.match(cmake, /flac_decoder\.cpp/);
  assert.match(adapter, /FLACDecoder_AllocateBuffers\(max_block_size/);
  assert.match(adapter, /FLACDecode\(decoder->input/);
  assert.match(audio, /custom_flac_decoder_feed/);
  assert.doesNotMatch(adapter, /#include\s+[<"]Arduino\.h[>"]/);
});

test("native FLAC decoder is selectable at compile time", () => {
  const kconfig = read("main", "Kconfig.projbuild");
  const defaults = read("sdkconfig.defaults");
  const audio = read("main", "audio_service.c");

  assert.match(kconfig, /choice YORADIO_FLAC_DECODER/);
  assert.match(kconfig, /YORADIO_FLAC_DECODER_CUSTOM/);
  assert.match(kconfig, /YORADIO_FLAC_DECODER_ESPRESSIF/);
  assert.match(defaults, /CONFIG_YORADIO_FLAC_DECODER_CUSTOM=y/);
  assert.match(
    audio,
    /CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF[\s\S]*esp_flac_dec_register/,
  );
  assert.match(
    audio,
    /CONFIG_YORADIO_FLAC_DECODER_CUSTOM[\s\S]*custom_flac_decoder_feed/,
  );
});

test("native MP3 and AAC alternatives are selectable at compile time", () => {
  const kconfig = fs.readFileSync(
    path.join(root, "idf", "components", "custom_legacy_codecs", "Kconfig"),
    "utf8",
  );
  const defaults = read("sdkconfig.defaults");
  const audio = read("main", "audio_service.c");
  const component = fs.readFileSync(
    path.join(
      root,
      "idf",
      "components",
      "custom_legacy_codecs",
      "CMakeLists.txt",
    ),
    "utf8",
  );
  const adapter = fs.readFileSync(
    path.join(
      root,
      "idf",
      "components",
      "custom_legacy_codecs",
      "custom_legacy_adapter.cpp",
    ),
    "utf8",
  );

  for (const symbol of [
    "YORADIO_MP3_DECODER_ESPRESSIF",
    "YORADIO_MP3_DECODER_HELIX",
    "YORADIO_MP3_DECODER_MINIMP3",
    "YORADIO_AAC_DECODER_ESPRESSIF",
    "YORADIO_AAC_DECODER_HELIX",
  ]) {
    assert.match(kconfig, new RegExp(symbol));
  }
  assert.match(kconfig, /default YORADIO_MP3_DECODER_MINIMP3/);
  assert.match(defaults, /CONFIG_YORADIO_MP3_DECODER_MINIMP3=y/);
  assert.match(defaults, /CONFIG_YORADIO_AAC_DECODER_ESPRESSIF=y/);
  assert.match(component, /aac_decoder\/aac_decoder\.cpp/);
  assert.match(component, /mp3_decoder\/mp3_decoder\.cpp/);
  assert.match(adapter, /MINIMP3_IMPLEMENTATION/);
  assert.match(adapter, /AACDecode\(decoder->input/);
  assert.match(adapter, /MP3Decode\(decoder->input/);
  assert.match(adapter, /mp3dec_decode_frame/);
  assert.match(audio, /custom_legacy_decoder_feed/);
});

test("minimp3 is the default for every Arduino and native board path", () => {
  const selector = fs.readFileSync(
    path.join(
      root,
      "yoRadio",
      "src",
      "audioI2S",
      "mp3_decoder",
      "Mp3DecoderSelector.cpp",
    ),
    "utf8",
  );
  const config = fs.readFileSync(
    path.join(root, "yoRadio", "src", "core", "config.cpp"),
    "utf8",
  );
  const c3Defaults = read("sdkconfig.defaults");
  const cydDefaults = fs.readFileSync(
    path.join(root, "idf", "esp32-cyd2usb-native", "sdkconfig.defaults"),
    "utf8",
  );
  const cydAudio = fs.readFileSync(
    path.join(
      root,
      "idf",
      "esp32-cyd2usb-native",
      "main",
      "audio_service.c",
    ),
    "utf8",
  );

  assert.match(selector, /selectedBackend = MP3_DECODER_MINIMP3/);
  assert.match(config, /store\.mp3Decoder = 1; \/\/ minimp3/);
  assert.match(c3Defaults, /CONFIG_YORADIO_MP3_DECODER_MINIMP3=y/);
  assert.match(cydDefaults, /CONFIG_YORADIO_MP3_DECODER_MINIMP3=y/);
  assert.match(cydAudio, /custom_legacy_decoder_feed/);
  assert.doesNotMatch(
    c3Defaults + cydDefaults,
    /^(?!#).*CONFIG_YORADIO_MP3_DECODER_ESPRESSIF=y/m,
  );
});

test("native benchmark build reads codec fixtures only from dedicated flash", () => {
  const audio = read("main", "audio_service.c");
  const app = read("main", "app_main.c");

  assert.match(audio, /#ifdef YORADIO_CODEC_BENCHMARK/);
  assert.match(audio, /ESP_PARTITION_TYPE_DATA[\s\S]*"codec_test"/);
  assert.match(audio, /CODEC_FIXTURE_MAGIC 0x59434658UL/);
  assert.match(audio, /sizeof\(codec_fixture_header_t\) \+ offset/);
  assert.match(audio, /benchmark_autostart\(\)/);
  assert.match(app, /Codec benchmark mode: network, WebUI and display disabled/);
});

test("native partition table stays compatible with min_spiffs", () => {
  const partitions = read("partitions.csv");

  assert.match(partitions, /app0,\s+app,\s+ota_0,\s+0x10000,\s+0x1E0000/);
  assert.match(partitions, /app1,\s+app,\s+ota_1,\s+0x1F0000,\s+0x1E0000/);
  assert.match(partitions, /spiffs,\s+data,\s+spiffs,\s+0x3D0000,\s+0x20000/);
});

test("native C3 uses wifi.csv as its only persistent credential source", () => {
  const network = read("main", "network_service.c");

  assert.match(network, /read_credentials\(&s_station_config\)/);
  assert.match(network, /esp_wifi_set_storage\(WIFI_STORAGE_RAM\)/);
  assert.doesNotMatch(network, /esp_wifi_get_config/);
});

test("native C3 refreshes Wi-Fi signal strength for WebSocket status", () => {
  const network = read("main", "network_service.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(network, /static void rssi_task/);
  assert.match(network, /esp_wifi_sta_get_ap_info\(&access_point\)/);
  assert.match(network, /native_state_set_wifi_rssi\(s_state, access_point\.rssi\)/);
  assert.match(network, /xTaskCreate\(rssi_task, "wifi_rssi"/);
  assert.match(websocket, /WS_STATUS_INTERVAL_MS 2000/);
  assert.match(websocket, /\{\\"id\\":\\"rssi\\",\\"value\\":%d\}/);
});

test("native stream connection reports HTTP failures and follows redirects", () => {
  const audio = read("main", "audio_service.c");

  assert.match(audio, /esp_http_client_get_errno\(client\)/);
  assert.match(audio, /esp_http_client_get_status_code\(client\)/);
  assert.match(audio, /esp_http_client_set_redirection\(client\)/);
  assert.match(audio, /Stream response: HTTP %d/);
  assert.match(
    read("sdkconfig.defaults"),
    /CONFIG_ESP_HTTP_CLIENT_MAX_SAVED_RESPONSE_HEADERS=24/,
  );
});

test("native audio buffers backpressure instead of dropping a live stream", () => {
  const audio = read("main", "audio_service.c");

  assert.match(
    audio,
    /xRingbufferSendAcquire\(s_encoded[\s\S]*pdMS_TO_TICKS\(250\)[\s\S]*atomic_load\(&s_generation\) != generation/,
  );
  assert.match(
    audio,
    /xRingbufferSendAcquire\(s_pcm[\s\S]*pdMS_TO_TICKS\(250\)[\s\S]*atomic_load\(&s_generation\) != generation/,
  );
});

test("native WebUI uses only the standard ESP-IDF HTTP and WebSocket server", () => {
  const component = read("main", "CMakeLists.txt");
  const config = read("sdkconfig.defaults");
  const web = read("main", "web_service.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(component, /esp_http_server/);
  assert.match(component, /websocket_service\.c/);
  assert.match(config, /CONFIG_HTTPD_WS_SUPPORT=y/);
  assert.match(web, /websocket_service_register\(server, state\)/);
  assert.match(web, /config\.max_open_sockets = 7/);
  assert.match(web, /httpd_resp_set_hdr\(request, "Connection", "close"\)/);
  assert.match(web, /httpd_sess_trigger_close\(request->handle/);
  assert.match(web, /strcmp\(uri, "\/variables\.js"\)/);
  assert.match(web, /equalizerEnabled=false/);
  assert.match(web, /\.uri = "\/upload"/);
  assert.match(web, /\.uri = "\/webboard"/);
  assert.match(web, /webboard_upload_handler/);
  assert.match(web, /receive_multipart/);
  assert.match(websocket, /\.uri = "\/ws"/);
  assert.match(websocket, /\.is_websocket = true/);
  assert.match(websocket, /httpd_ws_recv_frame/);
  assert.match(websocket, /httpd_ws_send_frame/);
  assert.match(websocket, /httpd_ws_send_data/);
  assert.match(websocket, /strcmp\(command, "next"\)/);
  assert.match(websocket, /strcmp\(command, "prev"\)/);
  assert.doesNotMatch(web + websocket, /AsyncWebServer|AsyncWebSocket|Arduino/);
});

test("native settings page is complete in client mode and Wi-Fi-only in AP mode", () => {
  const websocket = read("main", "websocket_service.c");
  const original = fs.readFileSync(
    path.join(root, "yoRadio", "src", "core", "netserver.cpp"),
    "utf8",
  );

  assert.match(
    original,
    /APPEND_GROUP\("group_wifi"\);[\s\S]*if \(network\.status == CONNECTED\) \{[\s\S]*APPEND_GROUP\("group_system"\)/,
  );

  for (const group of [
    "group_system",
    "group_display",
    "group_oled",
    "group_controls",
    "group_timezone",
    "group_wifi",
    "group_buffer",
    "group_wortc",
  ]) {
    assert.match(websocket, new RegExp(`\\\\\"${group}\\\\\"`));
  }
  assert.match(
    websocket,
    /!client_mode[\s\S]*\{\\"act\\":\[\\"group_wifi\\"\]\}/,
  );
  assert.match(
    websocket,
    /getactive[\s\S]*state\.network_mode == NATIVE_NETWORK_CLIENT[\s\S]*send_active_settings\(request, client_mode\)/,
  );
  assert.doesNotMatch(websocket, /send_settings_snapshot/);
  for (const command of [
    "getsystem",
    "getscreen",
    "gettimezone",
    "getweather",
    "getcontrols",
  ]) {
    assert.match(websocket, new RegExp(`strcmp\\(command, \"${command}\"\\)`));
  }
});

test("native WebUI reuses shared pages and recovers an empty filesystem", () => {
  const component = read("main", "CMakeLists.txt");
  const bridge = read("main", "web_pages_bridge.cpp");
  const web = read("main", "web_service.c");
  const sharedPages = fs.readFileSync(
    path.join(root, "yoRadio", "src", "core", "netserver.h"),
    "utf8",
  );

  assert.match(component, /web_pages_bridge\.cpp/);
  assert.match(bridge, /YORADIO_WEB_PAGES_ONLY/);
  assert.match(bridge, /yoRadio\/src\/core\/netserver\.h/);
  assert.match(sharedPages, /const char emptyfs_html\[\]/);
  assert.match(sharedPages, /const char index_html\[\]/);
  assert.match(web, /!web_ui_available\(\)[\s\S]*send_recovery_page/);
  assert.match(web, /yoradio_emptyfs_html\(\)/);
  assert.match(web, /yoradio_index_html\(\)/);
  assert.match(web, /open_nonempty_file/);
  assert.match(web, /Rejecting uncompressed WebUI asset/);
  assert.match(web, /\/spiffs\/www\/%s\.gz/);
  assert.match(web, /Content-Encoding", "gzip"/);
  assert.match(web, /strcmp\(field, "www"\)/);
  assert.match(web, /strcmp\(field, "data"\)/);
  assert.match(web, /\.uri = "\/emergency"/);
});

test("shared playlist editor reloads an uploaded native playlist", () => {
  const websocket = read("main", "websocket_service.c");

  assert.match(websocket, /strcmp\(command, "submitplaylist"\)/);
  assert.match(websocket, /\/data\/playlist\.csv/);
  assert.match(websocket, /strcmp\(command, "submitplaylistdone"\)/);
});

test("native SPIFFS image contains the shared WebUI and repository playlist", () => {
  const component = read("main", "CMakeLists.txt");

  assert.match(component, /file\(COPY "\$\{YORADIO_ROOT\}\/data\/"/);
  assert.match(component, /playlist\.csv" COPYONLY/);
  assert.match(component, /spiffs_create_partition_image\(spiffs "\$\{NATIVE_SPIFFS_ROOT\}"/);
});
