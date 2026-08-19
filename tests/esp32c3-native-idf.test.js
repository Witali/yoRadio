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

test("native OLED shows station and song in the shared Spleen font", () => {
  const header = read("main", "oled_display.h");
  const source = read("main", "oled_display.c");
  const app = read("main", "app_main.c");
  const font = read("main", "font6x12.h");

  assert.match(header, /oled_display_draw_large_text/);
  assert.match(source, /font6x12 \+ \(size_t\)glyph \* 9U/);
  assert.match(source, /font6x12_unicode_80_bf/);
  assert.match(source, /\*glyph = 0x7f/);
  assert.match(font, /Spleen 6x12/);
  assert.match(font, /font6x12\[2304\]/);
  assert.match(app, /state->station[\s\S]*state->title/);
  assert.match(app, /IPSTR[\s\S]*oled_display_draw_compact_text/);
  assert.doesNotMatch(app, /state->stream_format[\s\S]*oled_display_draw/);
});

test("native radio requests and publishes ICY song metadata", () => {
  const audio = read("main", "audio_service.c");
  const state = read("main", "native_state.h");
  const websocket = read("main", "websocket_service.c");

  assert.match(audio, /Icy-MetaData", "1"/);
  assert.match(audio, /icy-metaint/);
  assert.match(audio, /StreamTitle='/);
  assert.match(audio, /native_state_set_title\(s_state, title\)/);
  assert.match(state, /char title\[192\]/);
  assert.match(websocket, /json_escape\(state\.title, title/);
  assert.match(websocket, /native_state_set_station\(s_state, name\)/);
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

  assert.match(audio, /vTaskDelay\(1\);[\s\S]*generation != atomic_load\(&s_generation\)/);
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
