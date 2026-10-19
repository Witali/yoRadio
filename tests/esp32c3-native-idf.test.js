const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.resolve(__dirname, "..");
const nativeRoot = path.join(root, "idf", "esp32c3-oled-native");
const read = (...parts) => {
  const name = parts.join("/");
  const shared = name === "main/radio_control.c" ? "radio_control_impl.h" :
    name === "main/radio_control.h" ? "radio_control.h" : null;
  return fs.readFileSync(shared ? path.join(root, "idf/components/native_storage/include", shared) :
    path.join(nativeRoot, ...parts), "utf8");
};
const shared = (component, ...parts) => fs.readFileSync(
  path.join(root, "idf", "components", component, ...parts), "utf8",
);
const section = (source, first, next) => {
  const start = source.indexOf(first);
  const end = source.indexOf(next, start + first.length);
  assert.ok(start >= 0 && end > start, `source section ${first} .. ${next}`);
  return source.slice(start, end);
};

test("repository default setup and build select native ESP-IDF firmware", () => {
  const setup = fs.readFileSync(path.join(root, "setup.ps1"), "utf8");
  const build = fs.readFileSync(path.join(root, "build.ps1"), "utf8");

  assert.match(setup, /idf\\esp32c3-oled-native\\setup\.ps1/);
  assert.match(build, /idf\\esp32c3-oled-native\\build\.ps1/);
  assert.match(build, /IdfArguments = @\("build"\)/);
  assert.doesNotMatch(setup + build, /arduino-cli/);
});

test("debug and production profiles compile the same sources", () => {
  const build = read("build.ps1");
  const productionBuild = read("build-production.ps1");
  const defaults = read("sdkconfig.defaults");
  const productionDefaults = read("sdkconfig.production.defaults");

  assert.match(productionBuild, /Join-Path \$PSScriptRoot "build\.ps1"/);
  assert.match(
    productionBuild,
    /SdkconfigDefaults = @\([\s\S]*"sdkconfig\.defaults"[\s\S]*"sdkconfig\.production\.defaults"/,
  );
  assert.doesNotMatch(productionBuild, /main\/|main\\|src\/|src\\/);
  assert.match(build, /SdkconfigDefaults/);

  assert.match(defaults, /CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y/);
  assert.match(defaults, /CONFIG_LOG_DEFAULT_LEVEL_INFO=y/);
  assert.match(defaults, /CONFIG_LOG_MAXIMUM_LEVEL=3/);
  assert.match(defaults, /CONFIG_ESP_SYSTEM_PANIC_PRINT_REBOOT=y/);

  const productionSettings = productionDefaults
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
  assert.ok(productionSettings.length > 0);
  assert.ok(productionSettings.every((line) => /^CONFIG_[A-Z0-9_]+=/.test(line)));
  assert.match(productionDefaults, /CONFIG_LOG_MAXIMUM_LEVEL=0/);
  assert.match(productionDefaults, /CONFIG_ESP_CONSOLE_NONE=y/);
});

test("production builds save the application under firmware", () => {
  const productionBuild = read("build-production.ps1");
  const agentRules = fs.readFileSync(path.join(root, "AGENTS.md"), "utf8");
  const firmwareReadme = fs.readFileSync(
    path.join(root, "firmware", "README.md"),
    "utf8",
  );

  assert.match(
    productionBuild,
    /firmware\\development\\esp32c3-oled-native-production/,
  );
  assert.match(productionBuild, /Join-Path \$resolvedFirmwareOutput "app\.bin"/);
  assert.match(
    productionBuild,
    /Copy-Item -LiteralPath \$applicationImage -Destination \$savedImage -Force/,
  );
  assert.match(agentRules, /Save every successful production firmware build/);
  assert.match(firmwareReadme, /firmware\/development\/<variant>\/app\.bin/);
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

test("native task stacks are configured by each board profile", () => {
  const c3Board = read("main", "board_config.h");
  const c3Sources = [
    read("main", "app_main.c"),
    read("main", "encoder_input.c"),
    read("main", "audio_service.c"),
    read("main", "network_service.c"),
    read("main", "web_service.c"),
    read("main", "websocket_service.c"),
  ].join("\n");
  const cydRoot = path.join(root, "idf", "esp32-cyd2usb-native", "main");
  const cydBoard = fs.readFileSync(path.join(cydRoot, "board_config.h"), "utf8");
  const cydSources = ["app_main.c", "audio_service.c"]
    .map((file) => fs.readFileSync(path.join(cydRoot, file), "utf8"))
    .join("\n");

  for (const symbol of [
    "BOARD_TASK_STACK_DISPLAY",
    "BOARD_TASK_STACK_RADIO_STREAM",
    "BOARD_TASK_STACK_AUDIO_DECODER",
    "BOARD_TASK_STACK_AUDIO_OUTPUT",
  ]) {
    assert.match(c3Board, new RegExp(`#define ${symbol} \\d+`));
    assert.match(cydBoard, new RegExp(`#define ${symbol} \\d+`));
    assert.match(c3Sources, new RegExp(symbol));
    assert.match(cydSources, new RegExp(symbol));
  }
  assert.match(c3Board, /BOARD_TASK_STACK_ROTARY_ENCODER 4096/);
  assert.match(c3Sources, /BOARD_TASK_STACK_ROTARY_ENCODER/);
  assert.match(c3Board, /BOARD_TASK_STACK_WEBSOCKET_STATUS 8192/);
  assert.match(c3Sources, /BOARD_TASK_STACK_WEBSOCKET_STATUS/);
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

test("native OLED presents a legible full-screen yoRadio boot logo first", () => {
  const header = read("main", "oled_display.h");
  const display = read("main", "oled_display.c");
  const logo = read("main", "boot_logo_72x40.h");
  const app = read("main", "app_main.c");
  const bytes = [...logo.matchAll(/0x([0-9a-f]{2})/gi)].map((match) =>
    Number.parseInt(match[1], 16),
  );

  assert.equal(bytes.length, 72 * 40 / 8);
  assert.ok(bytes.filter(Boolean).length > 100);
  const verticalCentroid = (firstX, lastX) => {
    let pixels = 0;
    let yTotal = 0;
    for (let y = 0; y < 40; ++y) {
      for (let x = firstX; x <= lastX; ++x) {
        if ((bytes[Math.floor(y / 8) * 72 + x] >> (y % 8)) & 1) {
          ++pixels;
          yTotal += y;
        }
      }
    }
    return yTotal / pixels;
  };
  assert.ok(
    Math.abs(verticalCentroid(0, 25) - verticalCentroid(28, 71)) < 1,
    "Radio word must be vertically centered with the ё mark",
  );
  assert.match(logo, /original 21x32 `ё` mark/);
  assert.match(logo, /crisp Spleen bitmap face/);
  assert.match(header, /oled_display_show_boot_logo/);
  assert.match(
    display,
    /memcpy\(display->framebuffer, boot_logo_72x40,[\s\S]*oled_display_present\(display\)/,
  );

  const init = app.indexOf("oled_display_init(&s_display)");
  const bootLogo = app.indexOf("oled_display_show_boot_logo(&s_display)");
  const settings = app.indexOf("display_settings_init(&s_display)");
  const displayTask = app.indexOf('xTaskCreate(display_task, "display"');
  assert.ok(init >= 0);
  assert.ok(init < bootLogo);
  assert.ok(bootLogo < settings);
  assert.ok(settings < displayTask);
  assert.match(app, /DISPLAY_BOOT_LOGO_MS 1500U/);
  assert.match(app, /esp_timer_get_time\(\) < s_boot_logo_until_us/);
});

test("stopped-radio screensaver draws a full-screen clock and wakes on BOOT", () => {
  const header = read("main", "oled_display.h");
  const display = read("main", "oled_display.c");
  const app = read("main", "app_main.c");
  const settings = read("main", "display_settings.c");
  const websocket = read("main", "websocket_service.c");
  const options = zlib.gunzipSync(
    fs.readFileSync(path.join(root, "yoRadio", "data", "www", "options.html.gz")),
  ).toString("utf8");

  assert.match(header, /oled_display_draw_clock/);
  assert.match(display, /CLOCK_DIGIT_WIDTH 13/);
  assert.match(display, /CLOCK_DIGIT_HEIGHT 30/);
  assert.match(display, /static const uint8_t segments\[10\]/);
  assert.match(display, /const int digit_x\[\] = \{2, 18, 40, 56\}/);
  const displayWidth = Number(
    header.match(/OLED_DISPLAY_WIDTH (\d+)/)[1],
  );
  const digitWidth = Number(
    display.match(/CLOCK_DIGIT_WIDTH (\d+)/)[1],
  );
  const digitPositions = display
    .match(/const int digit_x\[\] = \{([^}]+)\}/)[1]
    .split(",")
    .map(Number);
  assert.ok(
    digitPositions.every(
      (position) => position >= 0 && position + digitWidth <= displayWidth,
    ),
    "all clock digits must fit within the OLED width",
  );
  assert.match(app, /CLOCK_VALID_AFTER_EPOCH 1704067200LL/);
  assert.match(app, /localtime_r\(&now, &local_time\)/);
  assert.match(
    app,
    /screensaver_active[\s\S]*screensaver_power_off[\s\S]*draw_screensaver_clock\(clock_tick\)/,
  );
  assert.match(app, /time\(NULL\)/);
  assert.match(
    app,
    /xQueueReceive\(s_button_edge_queue[\s\S]*if \(event\.pressed\) display_settings_note_activity\(\)/,
  );
  assert.match(settings, /display_settings_get_screensaver_timeout\(\)/);
  assert.match(settings, /display_settings_get_screensaver_blank\(\)/);
  assert.match(websocket, /strcmp\(command, "screensavertimeout"\)/);
  assert.match(websocket, /strcmp\(command, "screensaverblank"\)/);
  assert.match(options, /<select id="scrb" data-command="screensaverblank">/);
  assert.match(options, /<option value="0">clock<\/option>/);
  assert.match(options, /<option value="1">blank<\/option>/);
});

test("native SNTP delegates name lifetime and applies checked settings after IP", () => {
  const board = read("main", "board_config.h");
  const timeService = read("main", "time_service.c");
  const timeHeader = read("main", "time_service.h");
  const network = read("main", "network_service.c");

  const context = shared("native_time", "native_time_sntp_context.c");
  assert.match(read("main", "CMakeLists.txt"), /\bnative_time\b/);
  assert.match(timeService, /#include "native_time_sntp\.h"/);
  assert.match(timeService, /runtime_settings_get_time_snapshot\(/);
  assert.match(timeService, /native_time_sntp_apply\(&config\)/);
  assert.match(timeService, /native_time_sntp_restart\(\)/);
  assert.doesNotMatch(timeService, /esp_sntp_(?:stop|init|restart|setservername)\(/);
  assert.match(context, /native_time_sntp_config_t s_banks\[2\]/);
  assert.match(context, /bank_referenced\(bank\)/);
  assert.match(context, /sntp_setserver\(\(uint8_t\)index, NULL\)/);
  assert.match(board, /BOARD_TASK_STACK_TIME_SYNC 2048/);
  assert.match(timeService, /TIME_SYNC_TASK_PRIORITY 1/);
  assert.match(
    timeService,
    /xTaskCreate\(time_sync_task,[\s\S]*TIME_SYNC_TASK_PRIORITY/,
  );
  assert.match(
    timeService,
    /time_service_notify_network_ready\(void\)[\s\S]*native_time_sntp_notify_network_ready\(\)[\s\S]*atomic_store\(&s_network_ready_seen, true\)[\s\S]*xTaskNotify\(task, TIME_SYNC_EVENT_NETWORK_READY, eSetBits\)/,
  );
  assert.doesNotMatch(
    timeService,
    /time_service_notify_network_ready\(void\)[\s\S]*esp_sntp_restart\(\)/,
  );
  assert.match(
    timeService,
    /time_sync_notification\(void \*context,[\s\S]*const struct timeval \*synced_time\)[\s\S]*xTaskNotify\(task, TIME_SYNC_EVENT_COMPLETED, eSetBits\)/,
  );
  assert.match(
    timeService,
    /TIME_SYNC_EVENT_COMPLETED[\s\S]*ESP_LOGI\(TAG, "SNTP synchronized"\)/,
  );
  assert.match(timeHeader, /time_service_notify_network_ready/);
  assert.match(
    network,
    /IP_EVENT_STA_GOT_IP[\s\S]*time_service_notify_network_ready\(\)/,
  );
  // Actual bank/DNS lifetime: run-native-time.py;
  // actual controller/worker and coherent settings: run-c3-time-service.py,
  // run-c3-time-settings.py. These checks retain the target wiring contract.
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
  assert.match(app, /station_text[\s\S]*secondary_text/);
  assert.match(app, /station_text[\s\S]*station_scroll->enabled, true/);
  assert.match(app, /secondary_text[\s\S]*title_scroll->enabled, false/);
  assert.match(app, /DISPLAY_SCROLL_HOLD_MS 3500U/);
  assert.match(app, /DISPLAY_SCROLL_STEP_MS 35U/);
  assert.match(app, /IPSTR[\s\S]*oled_display_draw_compact_text/);
  assert.doesNotMatch(app, /oled_display_draw[^;]*state->stream_format/);
});

test("native OLED defaults to software scroll and keeps hardware scroll optional", () => {
  const kconfig = read("main", "Kconfig.projbuild");
  const defaults = read("sdkconfig.defaults");
  const header = read("main", "oled_display.h");
  const display = read("main", "oled_display.c");
  const app = read("main", "app_main.c");
  const readme = read("README.md");

  assert.match(kconfig, /config YORADIO_OLED_HW_SCROLL[\s\S]*default n/);
  assert.match(defaults, /# CONFIG_YORADIO_OLED_HW_SCROLL is not set/);
  assert.match(header, /OLED_HARDWARE_SCROLL_MAX_GLYPHS 15/);
  assert.match(header, /oled_display_start_text_scroll/);
  assert.match(header, /oled_display_stop_scroll/);
  assert.match(display, /OLED_CONTROLLER_WIDTH 128/);
  assert.match(
    display,
    /0x27,[\s\S]*OLED_SCROLL_INTERVAL_5_FRAMES[\s\S]*0x2f/,
  );
  assert.match(display, /const uint8_t command = 0x2e/);
  assert.match(
    display,
    /glyph_count <= OLED_HARDWARE_SCROLL_MAX_GLYPHS/,
  );
  assert.match(app, /#if CONFIG_YORADIO_OLED_HW_SCROLL/);
  assert.match(app, /oled_display_start_text_scroll/);
  assert.match(app, /advance_scroll\(&station_scroll/);
  assert.match(app, /&s_display, 0, 16, secondary_text/);
  assert.match(readme, /Software text scrolling is enabled[\s\S]*by default/);
});

test("native OLED alternates ICY title with live stream parameters", () => {
  const app = read("main", "app_main.c");
  const audio = read("main", "audio_service.c");
  const stateHeader = read("main", "native_state.h");
  const stateSource = read("main", "native_state.c");

  assert.match(stateHeader, /uint32_t sample_rate_hz/);
  assert.match(stateHeader, /uint8_t channels/);
  assert.match(stateHeader, /char codec\[16\]/);
  assert.match(stateHeader, /native_state_set_stream_info/);
  assert.match(stateSource, /state->sample_rate_hz = info->sample_rate_hz/);
  assert.match(stateSource, /state->channels = info->channels/);
  assert.match(audio, /update_stream_info\(context->generation/);
  assert.match(app, /native_state_format_stream_details\(state, output, output_size\)/);
  assert.match(stateSource, /state->bitrate_kbps[\s\S]*"%s %lu kbps"/);

  assert.match(app, /show_stream_info = audio_info && !state\.title\[0\]/);
  assert.match(app, /completed == DISPLAY_SCROLL_TITLE[\s\S]*show_stream_info = !show_stream_info/);
  assert.match(app, /DISPLAY_SECONDARY_PAGE_MS 5000U/);
  assert.match(app, /strlcpy\(secondary_text, wanted_secondary[\s\S]*reset_scroll/);
  assert.doesNotMatch(app, /update_scroll_dimensions/);
  assert.doesNotMatch(app, /stream info\.\.\./i);
  assert.match(app, /bool secondary_initialized = false/);
  assert.match(app, /else if \(!secondary_initialized\)/);
});

test("native WebUI and OLED share the confirmed decoded format", () => {
  const stateSource = read("main", "native_state.c");
  const app = read("main", "app_main.c");
  const websocket = read("main", "websocket_service.c");
  assert.match(stateSource, /snprintf\(state->stream_format/);
  assert.match(app, /native_state_format_stream_details/);
  assert.match(websocket, /json_escape\(state.stream_format, format/);
  // Executable callback/state/JSON coverage: run-esp32c3-stream-format.py.
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
  assert.match(
    fs.readFileSync(path.join(root, "idf", "components", "native_stream", "icy_title.c"), "utf8"),
    /StreamTitle='/,
  );
  assert.match(audio, /native_state_set_stream_title\(s_state, generation, title\)/);
  assert.match(audio, /publish_icy_title\(uint32_t generation/);
  assert.match(audio, /icy_title_feed\(&s_icy_title, buffer \+ offset, chunk\)/);
  assert.match(audio, /publish_icy_title\(command.generation,\s*icy_title_finish\(&s_icy_title\)\)/);
  assert.match(
    read("main", "native_state.c"),
    /native_state_set_stream_title[\s\S]*audio_generation == generation[\s\S]*strlcpy\(state->title/,
  );
  assert.match(
    audio,
    /audio_service_stop[\s\S]*advance_generation\(NATIVE_CODEC_AUTO\)/,
  );
  assert.match(
    audio,
    /audio_service_stop[\s\S]*advance_generation\(NATIVE_CODEC_AUTO\)[\s\S]*state_set_audio\(generation, false, "stopped"\)/,
  );
  assert.doesNotMatch(audio, /close_active_http_stream/);
  assert.match(audio, /#define STREAM_READ_TIMEOUT_MS CONFIG_YORADIO_STREAM_READ_TIMEOUT_MS/);
  assert.match(
    read("main", "Kconfig.projbuild"),
    /config YORADIO_STREAM_READ_TIMEOUT_MS[\s\S]*?default 250/,
  );
  assert.match(
    audio,
    /open_stream\(client, command\.url, retry\.deadline_us,[\s\S]*esp_http_client_set_timeout_ms\(client, STREAM_READ_TIMEOUT_MS\)/,
  );
  assert.match(
    audio,
    /stream_http_read\(&reader, client,[\s\S]*atomic_load\(&s_generation\) != command\.generation[\s\S]*received == -ESP_ERR_HTTP_EAGAIN/,
  );
  assert.match(
    audio,
    /atomic_load\(&s_generation\) != command\.generation[\s\S]*dispose_http_client\(client\)/,
  );
  assert.match(state, /char title\[192\]/);
  assert.match(websocket, /json_escape\(state\.title, title/);
  assert.match(controls, /native_state_set_station\(s_state, s_candidate_name\)/);
});

test("native HTTPS station switching releases incompatible codec memory before TLS", () => {
  const audio = read("main", "audio_service.c");
  const sdkconfig = fs.readFileSync(
    path.join(nativeRoot, "sdkconfig.defaults"),
    "utf8",
  );

  assert.match(audio, /\.crt_bundle_attach = esp_crt_bundle_attach/);
  assert.match(sdkconfig, /CONFIG_MBEDTLS_CERTIFICATE_BUNDLE=y/);
  assert.match(sdkconfig, /CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384/);
  assert.match(sdkconfig, /# CONFIG_MBEDTLS_DYNAMIC_BUFFER is not set/);
  assert.doesNotMatch(sdkconfig, /^CONFIG_MBEDTLS_DYNAMIC_BUFFER=y$/m);
  assert.match(audio, /atomic_uint s_decoder_released_generation/);
  assert.match(
    audio,
    /atomic_load\(&s_decoder_released_generation\) !=[\s\S]*command\.generation[\s\S]*esp_http_client_config_t config/,
  );
  const generationResetStart = audio.indexOf("if (generation != current_generation)");
  const generationResetEnd = audio.indexOf("size_t item_size", generationResetStart);
  const generationReset = audio.slice(generationResetStart, generationResetEnd);
  assert.match(generationReset, /esp_audio_simple_dec_close\(decoder\)/);
  assert.match(
    generationReset,
    /custom_legacy_decoder_destroy\(legacy_decoder\)[\s\S]*custom_legacy_decoder_discard_arena\(\)[\s\S]*atomic_store\(&s_decoder_released_generation/,
  );
  assert.match(
    generationReset,
    /target_codec == NATIVE_CODEC_AUTO[\s\S]*codec_uses_custom_legacy\(target_codec\)[\s\S]*free\(output\)/,
  );
  // PCM can exist even when open failed: release must not depend on a handle.
  assert.doesNotMatch(generationReset, /had_simple_decoder/);
  assert.match(generationReset, /atomic_store\(&s_decoder_released_generation/);
  assert.match(audio, /stream_probe_feed\(probe, data, size, &consumed\)/);
  assert.match(
    audio,
    /advance_generation\(codec\)[\s\S]*requested_codec = codec/,
  );
  assert.match(audio, /state_set_audio\(generation, false, "NO MEMORY"\)/);
  assert.match(
    audio,
    /open_result == ESP_AUDIO_ERR_MEM_LACK[\s\S]*"NO MEMORY"[\s\S]*"DECODER ERROR"/,
  );
  assert.match(
    audio,
    /pipeline_receive\([\s\S]*pdMS_TO_TICKS\(20\), &stats\.input_empty\)/,
  );
});

test("native WebUI publishes ICY or decoder bitrate instead of a constant zero", () => {
  const audio = read("main", "audio_service.c");
  const stateHeader = read("main", "native_state.h");
  const stateSource = read("main", "native_state.c");
  const websocket = read("main", "websocket_service.c");
  const meter = shared("native_stream", "include", "stream_bitrate.h");

  assert.match(stateHeader, /uint32_t bitrate_kbps/);
  assert.match(stateHeader, /native_state_set_bitrate/);
  assert.match(stateSource, /state->bitrate_kbps = bitrate_kbps/);
  assert.match(audio, /get_response_header[\s\S]*"icy-br"/);
  assert.match(audio, /ICY bitrate: %lu kbit\/s/);
  assert.match(audio, /state_set_decoder_bitrate\(context->generation, info->bitrate\)/);
  assert.match(audio, /state_set_decoder_bitrate\(generation, latest_info\.bitrate\)/);
  assert.match(audio, /BITRATE_UPDATE_INTERVAL_US 1000000LL/);
  assert.match(audio, /#include "stream_bitrate\.h"/);
  assert.match(meter, /STREAM_BITRATE_WINDOW_US INT64_C\(5000000\)/);
  assert.match(audio, /stream_bitrate_meter_add\([\s\S]*meter, audio_bytes, esp_timer_get_time\(\)/);
  assert.match(audio, /stream_bitrate_add\(command\.generation, &bitrate_meter/);
  for (const source of ["ICY", "DECODER", "MEASURED"]) {
    assert.match(audio, new RegExp(`native_state_publish_bitrate\\([\\s\\S]*NATIVE_BITRATE_${source}`));
  }
  const publication = section(stateSource, "void native_state_publish_bitrate(", "static void format_rate(");
  assert.match(publication, /xSemaphoreTake\(state->lock,[\s\S]*state->audio_generation == generation[\s\S]*source >= state->bitrate_source/);
  assert.match(publication, /state->bitrate_kbps = bitrate_kbps;[\s\S]*state->bitrate_source = source;/);
  assert.match(
    audio,
    /frame\.decoded_size[\s\S]*esp_audio_simple_dec_get_info\(decoder, &latest_info\)[\s\S]*state_set_decoder_bitrate\(generation, latest_info\.bitrate\)/,
  );
  assert.ok(
    audio.indexOf('client, "icy-br"') <
      audio.indexOf("state_set_decoder_bitrate(generation, latest_info.bitrate)"),
    "decoder bitrate must override the earlier ICY fallback",
  );
  assert.match(websocket, /\\"bitrate\\",\\"value\\":%lu/);
  assert.match(websocket, /state\.bitrate_kbps/);
  assert.doesNotMatch(websocket, /\\"bitrate\\",\\"value\\":0/);
  // Exact meter arithmetic is executed by run-stream-bitrate.py; stale-stream
  // and ICY/decoder/measured priority interleavings by run-c3-bitrate.py.
});

test("native BOOT gestures match the documented one-button controls", () => {
  const app = read("main", "app_main.c");
  const component = read("main", "CMakeLists.txt");
  const controls = read("main", "radio_control.c");

  assert.match(component, /radio_control\.c/);
  assert.match(app, /BUTTON_CLICK_WINDOW_MS 400/);
  assert.match(app, /BUTTON_HOLD_MS 800/);
  assert.match(app, /BUTTON_EDGE_QUEUE_LENGTH 32/);
  assert.match(app, /BUTTON_TASK_PRIORITY 8/);
  assert.match(app, /xQueueCreate\(BUTTON_EDGE_QUEUE_LENGTH/);
  assert.match(app, /gpio_install_isr_service\(0\)/);
  assert.match(app, /gpio_isr_handler_add\(BOARD_BOOT_BUTTON, button_gpio_isr/);
  assert.match(app, /gpio_set_intr_type\(BOARD_BOOT_BUTTON, GPIO_INTR_ANYEDGE\)/);
  assert.match(app, /xQueueSendFromISR\(s_button_edge_queue/);
  assert.match(app, /xQueueReceive\(s_button_edge_queue/);
  assert.match(app, /const bool next = button->clicks >= 2/);
  assert.match(app, /BUTTON_ACTION_NEXT[\s\S]*return radio_control_next\(\)/);
  assert.match(app, /BUTTON_ACTION_TOGGLE[\s\S]*return radio_control_toggle\(\)/);
  assert.match(app, /BUTTON_ACTION_PREVIOUS[\s\S]*return radio_control_previous\(\)/);
  assert.match(app, /result == ESP_ERR_INVALID_STATE/);
  assert.match(app, /BUTTON_ACTION_RETRY_MS 100/);
  assert.match(app, /Deferred BOOT action executed/);
  assert.match(app, /BUTTON_STATUS_DISPLAY_MS 2000U/);
  assert.match(app, /executing_action == BUTTON_ACTION_TOGGLE/);
  assert.match(
    app,
    /executing_action == BUTTON_ACTION_NEXT[\s\S]*show_button_status\([\s\S]*BUTTON_STATUS_NEXT/,
  );
  assert.match(
    app,
    /executing_action == BUTTON_ACTION_PREVIOUS[\s\S]*show_button_status\([\s\S]*BUTTON_STATUS_PREVIOUS/,
  );
  assert.match(app, /state_before_action\.audio_running/);
  assert.match(
    app,
    /BUTTON_STATUS_NEXT:[\s\S]*return "next"[\s\S]*BUTTON_STATUS_PREVIOUS:[\s\S]*return "prev"/,
  );
  assert.match(app, /state\.audio_running \|\| unavailable \? secondary_text : ""/);
  assert.match(app, /button_status_visible[\s\S]*button_status_scroll/);
  assert.match(
    app,
    /xTaskCreate\(button_task, "boot_button",[\s\S]*BOARD_TASK_STACK_BOOT_BUTTON/,
  );
  assert.match(app, /BOOT two clicks: next station/);
  const isr = app.match(/static void button_gpio_isr[\s\S]*?\n}/)?.[0] ?? "";
  assert.doesNotMatch(isr, /radio_control_/);
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
    /packet->generation != atomic_load\(&s_generation\)[\s\S]*encoded_return\(s_encoded, packet\)/,
  );
  assert.match(audio, /#define encoded_return vRingbufferReturnItem/);
  assert.match(audio, /#define encoded_return adaptive_input_return/);
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

test("native audio pipeline batches PCM using the current decoded layout", () => {
  const audio = read("main", "audio_service.c");
  const output = read("main", "native_audio_output.c");
  const component = read("main", "CMakeLists.txt");

  assert.match(audio, /runtime_settings_get_audio_buffer_blocks\(\) \* 1600U/);
  assert.match(audio,
               /xRingbufferCreate\(encoded_ring_size, RINGBUF_TYPE_NOSPLIT\)/);
  assert.match(read("main", "Kconfig.projbuild"), /config YORADIO_ADAPTIVE_INPUT_BUFFER\b/);
  assert.match(component,
    /if\(CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER\)\s*target_sources\([^)]*"adaptive_input\.c"\)\s*endif\(\)/);
  assert.match(read("main", "adaptive_input.c"), /components\/native_stream\/adaptive_input\.c/);
  assert.match(audio, /adaptive_input_create\(encoded_ring_size,[\s\S]*sizeof\(encoded_packet_t\) \+ STREAM_CHUNK_SIZE\)/);
  assert.match(audio, /tls_input_reserve_bind\(s_encoded\)/);
  assert.match(audio, /#define PCM_RING_SIZE \(8 \* 1024\)/);
  assert.match(audio, /#define PCM_PACKET_DATA_SIZE 3584/);
  assert.match(audio, /bool stream_info_ready = false/);
  assert.match(
    audio,
    /esp_audio_simple_dec_get_info\(decoder, &latest_info\)[\s\S]*stream_info_ready = update_stream_info\(/,
  );
  assert.match(output, /scale_sample_q15/);
  assert.match(output, /channel_gain_q15/);
  assert.doesNotMatch(output, /scale_sample\([^_]/);
  assert.match(
    audio,
    /native_audio_output_init\(\)[\s\S]*xRingbufferCreate\(encoded_ring_size/,
  );
  assert.match(
    output,
    /native_audio_output_init\(void\)[\s\S]*pdm_begin\(\)/,
  );
  assert.match(output, /#define PDM_DMA_DESCRIPTORS 4U/);
  const begin = section(output, "static esp_err_t pdm_begin(", "static int16_t interpolate_sample(");
  assert.match(begin, /if \(s_pdm\)[\s\S]*if \(s_pdm_running\) return ESP_OK/);
  assert.match(begin, /ESP_RETURN_ON_ERROR\(native_audio_output_pause\(\)/);
  assert.match(output, /native_audio_normalizer_process_block/);
  assert.match(output, /normalizer_config_cache_t/);
  assert.match(
    output,
    /sync_normalizer_configuration[\s\S]*s_normalizer_config\.valid[\s\S]*return;/,
  );
  assert.match(
    output,
    /native_audio_output_write_pcm[\s\S]*sync_normalizer_configuration\(\)/,
  );
  assert.match(output, /PERF PCM:/);
  // Queue ownership/capacity: run-adaptive-input.py. Full staged/direct output
  // and checked pause/recreation: run-c3-output-pause.py and run-output-task-boundaries.py.
});

test("native FLAC reuses the optimized yoRadio decoder without Arduino Core", () => {
  const audio = read("main", "audio_service.c");
  const shim = read("components", "custom_flac", "CMakeLists.txt");
  const shared = (...parts) => fs.readFileSync(path.join(root, "idf", "components", "custom_flac", ...parts), "utf8");
  const cmake = shared("CMakeLists.txt");
  const adapter = shared("custom_flac_adapter.cpp");
  assert.match(shim, /include\(.*components\/custom_flac\/CMakeLists\.txt/);
  const decoder = fs.readFileSync(
    path.join(root, "yoRadio", "src", "audioI2S", "flac_decoder", "flac_decoder.cpp"), "utf8");

  assert.match(cmake, /yoRadio\/src\/audioI2S\/flac_decoder/);
  assert.match(cmake, /flac_decoder\.cpp/);
  assert.match(cmake, /FLAC_OUTPUT_FRAMES=512/);
  assert.match(adapter, /FLACDecoder_AllocateBuffers\(max_block_size/);
  assert.match(
    adapter,
    /required \+ kInputAlignment - 1[\s\S]*~\(kInputAlignment - 1\)/,
  );
  assert.match(adapter, /kFeedChunkSize = 512/);
  assert.match(adapter, /kInitialInputCapacity = 512/);
  assert.match(adapter, /kInputSlack = kFeedChunkSize/);
  assert.match(adapter, /std::min\(kFeedChunkSize, size - offset\)/);
  assert.doesNotMatch(adapter, /capacity \*= 2/);
  assert.match(adapter, /FLACDecode\(decoder->input/);
  assert.match(adapter, /kWorkspaceAttempts = 4/);
  assert.match(adapter, /vTaskDelay\(pdMS_TO_TICKS\(5\)\)/);
  assert.match(adapter, /int16_t pcm\[kPcmSamplesPerCall\]/);
  assert.match(cmake, /FLAC_SEGMENTED_WORKSPACE=1/);
  assert.match(decoder, /kWorkspaceSegmentSamples = 1024/);
  assert.match(decoder, /struct SampleBuffer[\s\S]*operator\[\]/);
  assert.match(decoder, /segments\[segment\] =\s*allocateSamples/);
  assert.match(adapter, /FLACDecoder_FreeBuffers[\s\S]*reserve_input[\s\S]*reserve_workspace/);
  assert.match(adapter, /reserve_workspace[\s\S]*FLACSetRawBlockParams/);
  assert.doesNotMatch(decoder, /int16_t\* samplesBuffer/);
  assert.match(adapter, /FLACDecoder_AllocateBuffers[\s\S]*reserve_input/);
  assert.match(adapter, /reserve_input[\s\S]*FLACDecoder_FreeBuffers/);
  assert.doesNotMatch(adapter, /decoder->pcm/);
  assert.match(audio, /result == -5 \|\| result == -6 \? "NO MEMORY"/);
  assert.match(audio, /custom_flac_decoder_feed/);
  assert.doesNotMatch(adapter, /#include\s+[<"]Arduino\.h[>"]/);
});

test("native decoder errors and EOF release independent PCM before terminal publication", () => {
  const audio = read("main", "audio_service.c");
  // The QEMU suite executes release (twice after failed open) against the
  // real library. These checks cover its placement in the network pipeline.
  assert.match(audio, /if \(packet->end_of_stream \|\| failed_generation == generation\) \{\s*decoder_resources_release\(&decoder, &aac_decoder, &output, &output_size\);\s*\}\s*return_decoded_packet\(packet, failed_generation\)/);
  assert.match(audio, /"DECODER INIT ERROR"\);\s*failed_generation = packet->generation;\s*return_decoded_packet\(packet, failed_generation\)/);
  assert.match(audio, /failed_generation = generation;\s*decoder_resources_release\(&decoder, &aac_decoder, &output, &output_size\)/);
});

test("native FLAC decoder is selectable at compile time", () => {
  const kconfig = read("main", "Kconfig.projbuild");
  const defaults = read("sdkconfig.defaults");
  const audio = read("main", "audio_service.c");

  assert.match(kconfig, /choice YORADIO_FLAC_DECODER/);
  assert.match(kconfig, /YORADIO_FLAC_DECODER_CUSTOM/);
  assert.match(kconfig, /YORADIO_FLAC_DECODER_ESPRESSIF/);
  assert.match(defaults, /CONFIG_YORADIO_FLAC_DECODER_CUSTOM=y/);
  assert.match(audio, /registration_result = decoder_register_codecs\(\)/);
  assert.match(
    read("main", "decoder_registration.c"),
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
  assert.match(kconfig, /default YORADIO_MP3_DECODER_ESPRESSIF/);
  assert.match(defaults, /CONFIG_YORADIO_MP3_DECODER_ESPRESSIF=y/);
  assert.doesNotMatch(
    defaults,
    /^(?!#).*CONFIG_YORADIO_MP3_DECODER_(?:HELIX|MINIMP3)=y/m,
  );
  assert.match(defaults, /CONFIG_YORADIO_AAC_DECODER_ESPRESSIF=y/);
  assert.match(defaults, /CONFIG_YORADIO_AAC_PLUS=y/);
  assert.doesNotMatch(
    defaults,
    /^(?!#).*CONFIG_YORADIO_AAC_DECODER_HELIX=y/m,
  );
  assert.match(component, /aac_decoder\/aac_decoder\.cpp/);
  assert.match(component, /mp3_decoder\/mp3_decoder\.cpp/);
  assert.match(adapter, /MINIMP3_IMPLEMENTATION/);
  assert.match(adapter, /AACDecode\(decoder->input/);
  assert.match(adapter, /MP3Decode\(decoder->input/);
  assert.match(adapter, /mp3dec_decode_frame/);
  assert.match(audio, /custom_legacy_decoder_feed/);
});

test("native ESP-IDF boards default to Espressif MP3", () => {
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
  assert.match(c3Defaults, /CONFIG_YORADIO_MP3_DECODER_ESPRESSIF=y/);
  assert.doesNotMatch(
    c3Defaults,
    /^(?!#).*CONFIG_YORADIO_MP3_DECODER_(?:HELIX|MINIMP3)=y/m,
  );
  assert.match(cydDefaults, /CONFIG_YORADIO_MP3_DECODER_ESPRESSIF=y/);
  assert.match(cydAudio, /custom_legacy_decoder_feed/);
  assert.doesNotMatch(
    cydDefaults,
    /^(?!#).*CONFIG_YORADIO_MP3_DECODER_(?:HELIX|MINIMP3)=y/m,
  );
});


test("shared WebUI does not expose MP3 backend selection", () => {
  const options = zlib.gunzipSync(
    fs.readFileSync(
      path.join(root, "yoRadio", "data", "www", "options.html.gz"),
    ),
  ).toString("utf8");

  assert.doesNotMatch(options, /id="mp3decoder"/i);
  assert.doesNotMatch(options, /Helix \(legacy\)/i);
  assert.doesNotMatch(options, /minimp3 \(new\)/i);
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

test("native partition table reserves 256 KiB for SPIFFS with dual OTA", () => {
  const partitions = read("partitions.csv");

  assert.match(partitions, /app0,\s+app,\s+ota_0,\s+0x10000,\s+0x1D0000/);
  assert.match(partitions, /app1,\s+app,\s+ota_1,\s+0x1E0000,\s+0x1D0000/);
  assert.match(partitions, /spiffs,\s+data,\s+spiffs,\s+0x3B0000,\s+0x40000/);
});

test("native C3 uses wifi.csv as its only persistent credential source", () => {
  const network = read("main", "network_service.c");

  assert.match(network, /read_credentials\(&s_station_config\)/);
  assert.match(network, /esp_wifi_set_storage\(WIFI_STORAGE_RAM\)/);
  assert.doesNotMatch(network, /esp_wifi_get_config/);
});

test("native C3 wires generation-aware audio power intents to the network owner", () => {
  const network = read("main", "network_service.c");
  const audio = read("main", "audio_service.c");

  assert.match(network, /active \? WIFI_PS_NONE : WIFI_PS_MIN_MODEM/);
  assert.match(audio, /play_locked[\s\S]*network_service_audio_accept\(command\.generation, true\)/);
  assert.match(audio, /audio_service_play[\s\S]*xSemaphoreTake\(s_control_lock, portMAX_DELAY\)[\s\S]*play_locked\(url, codec\)/);
  assert.match(audio, /audio_service_stop[\s\S]*network_service_audio_accept\(generation, false\)/);
  assert.match(
    audio,
    /network_service_audio_receive\(command\.generation\)[\s\S]*network_service_audio_finish\(command\.generation\)/,
  );
  assert.doesNotMatch(
    audio,
    /ESP_RETURN_ON_ERROR\(network_service_audio_/,
  );
  assert.match(network, /native_network_power_poll\(/);
  assert.doesNotMatch(audio, /network_service_set_streaming\(/);
});

test("native audio buffers cover high-bitrate remote streams", () => {
  const c3Defaults = read("sdkconfig.defaults");
  const c3Audio = read("main", "audio_service.c");
  const cydDefaults = fs.readFileSync(
    path.join(root, "idf", "esp32-cyd2usb-native", "sdkconfig.defaults"),
    "utf8",
  );
  const cydAudio = fs.readFileSync(
    path.join(root, "idf", "esp32-cyd2usb-native", "main", "audio_service.c"),
    "utf8",
  );

  for (const defaults of [c3Defaults, cydDefaults]) {
    assert.match(defaults, /CONFIG_LWIP_TCP_WND_DEFAULT=11520/);
    assert.match(defaults, /CONFIG_LWIP_TCP_RECVMBOX_SIZE=10/);
  }
  assert.match(c3Audio, /AUDIO_DECODE_PRIORITY = 7/);
  assert.match(c3Audio, /BOARD_TASK_STACK_AUDIO_DECODER, NULL, AUDIO_DECODE_PRIORITY, NULL/);
  assert.match(c3Audio, /BOARD_TASK_STACK_AUDIO_OUTPUT, NULL, AUDIO_OUTPUT_PRIORITY, NULL/);
  assert.match(c3Audio, /#ifdef CONFIG_YORADIO_OUTPUT_TASK_FIRST[\s\S]*AUDIO_DECODE_PRIORITY \+ 1[\s\S]*#else[\s\S]*AUDIO_DECODE_PRIORITY - 1/);
  assert.match(cydAudio, /#define ENCODED_RING_SIZE \(16 \* 1024\)/);
  assert.match(cydAudio, /16 KiB compressed \+ 8 KiB PCM/);
});

test("native C3 refreshes Wi-Fi signal strength for WebSocket status", () => {
  const network = read("main", "network_service.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(network, /static void rssi_task/);
  assert.match(network, /esp_wifi_sta_get_ap_info\(&access_point\)/);
  assert.match(network, /native_state_set_wifi_rssi\(s_state, access_point\.rssi\)/);
  assert.match(network, /xTaskCreate\(rssi_task, "wifi_rssi"/);
  assert.match(websocket, /WS_STATUS_HEARTBEAT_MS 2000/);
  assert.match(websocket, /PERF WS:/);
  assert.match(websocket, /\{\\"id\\":\\"rssi\\",\\"value\\":%d\}/);
});

test("native WebUI publishes player changes promptly and uses buffer percent", () => {
  const audio = read("main", "audio_service.c");
  const audioHeader = read("main", "audio_service.h");
  const controls = read("main", "radio_control.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(
    audio,
    /play_locked[\s\S]*native_state_set_connecting\(s_state, command\.generation\)/,
  );
  assert.match(audio, /open_stream[\s\S]*state_set_audio\(command\.generation, true, "connected"\)/);
  assert.match(audio, /state_set_audio\(generation, true, codec_name\(\*codec\)\)/);
  // EOF ordering is executed by run-esp32c3-eof.py. The network reader must
  // not publish stopped before buffered decoder callbacks and PCM complete.
  assert.match(audioHeader, /audio_service_buffer_fill_percent/);
  assert.match(
    audio,
    /s_encoded_usable_size = xRingbufferGetCurFreeSize\(s_encoded\)/,
  );
  assert.match(
    audio,
    /audio_service_buffer_fill_percent[\s\S]*used_size \* 100U/,
  );
  assert.match(audio,
    /audio_service_buffer_fill_percent[\s\S]*adaptive_input_stats\(s_encoded\)[\s\S]*stats\.occupied \* 100U \/ stats\.resident/);
  assert.match(websocket, /WS_STATUS_POLL_MS 100/);
  assert.match(websocket, /WS_STATUS_HEARTBEAT_MS 2000/);
  assert.match(websocket, /PERF WS:/);
  assert.match(websocket, /BOARD_TASK_STACK_WEBSOCKET_STATUS/);
  assert.match(websocket, /capture_status_key/);
  assert.match(
    websocket,
    /memcmp\(&s_current_status_key, &s_previous_status_key/,
  );
  assert.match(websocket, /static char s_broadcast_status\[1280\]/);
  assert.match(websocket, /static char s_broadcast_current\[48\]/);
  assert.match(websocket, /static webui_status_key_t s_previous_status_key/);
  assert.match(
    websocket,
    /publish_current = station_changed &&[\s\S]*atomic_load\(&s_current_send_pending\) == 0U/,
  );
  assert.match(websocket, /snprintf\(s_broadcast_current,[\s\S]*\\"current\\":%u/);
  assert.match(websocket,
    /current_queued = broadcast_text\(\s*s_broadcast_current, &s_current_send_pending, &s_current_work\)/);
  assert.match(websocket,
    /if \(status_queued && current_queued\)[\s\S]*s_previous_status_key = s_current_status_key/);
  assert.match(websocket, /audio_service_buffer_fill_percent\(\)/);
  assert.match(
    websocket,
    /state\.audio_running[\s\S]*audio_service_buffer_fill_percent\(\)/,
  );
  assert.doesNotMatch(websocket, /heap_caps_get_free_size/);
  assert.match(
    controls,
    /radio_control_init[\s\S]*playlist_station\(s_current_item/,
  );
  assert.match(controls, /native_state_set_station\(s_state, s_current_name\)/);
  // Actual queue-failure/reused-session handling: run-c3-websocket-io.py;
  // application/SDK framing over TCP and TLS: run-websocket-integration.py
  // and run-websocket-tls-integration.py. Queue occupancy is executed by
  // run-adaptive-input.py, rather than inferred from free heap.
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
    /encoded_acquire\(s_encoded[\s\S]*pdMS_TO_TICKS\(250\)[\s\S]*atomic_load\(&s_generation\) != generation/,
  );
  assert.match(audio, /#define encoded_acquire xRingbufferSendAcquire/);
  assert.match(audio, /#define encoded_acquire adaptive_input_acquire/);
  assert.match(
    audio,
    /pipeline_acquire\(s_pcm[\s\S]*pdMS_TO_TICKS\(250\), &stats->pcm_full\)[\s\S]*atomic_load\(&s_generation\) != generation/,
  );
});

test("native WebUI uses only the standard ESP-IDF HTTP and WebSocket server", () => {
  const component = read("main", "CMakeLists.txt");
  const config = read("sdkconfig.defaults");
  const web = read("main", "web_service.c");
  const websocket = read("main", "websocket_service.c");

  assert.match(component, /esp_http_server/);
  assert.match(component, /\bnative_web_transport\b/);
  assert.match(component, /\bnative_storage\b/);
  assert.match(component, /websocket_service\.c/);
  assert.match(component, /"web_wifi\.c"/);
  assert.match(config, /CONFIG_HTTPD_WS_SUPPORT=y/);
  assert.match(web, /websocket_service_register\(server, state\)/);
  assert.match(web, /#define WEB_MAX_OPEN_SOCKETS 7/);
  assert.match(web, /config\.max_open_sockets = WEB_MAX_OPEN_SOCKETS/);
  assert.match(web, /httpd_resp_set_hdr\(request, "Connection", "close"\)/);
  assert.match(web, /native_web_transport_prepare\(&config\)/);
  assert.ok(web.indexOf("native_web_transport_prepare(&config)") <
    web.indexOf("httpd_start(&server, &config)"));
  const finish = section(web, "static esp_err_t finish_static_response(",
                         "static bool embedded_script_size(");
  assert.match(finish, /shutdown\(httpd_req_to_sockfd\(request\), SHUT_RDWR\)/);
  assert.doesNotMatch(finish, /httpd_sess_trigger_close/);
  const worker = section(web, "static void static_worker_task(",
                         "static esp_err_t start_static_workers(");
  assert.ok(worker.indexOf("serve_static_request(request)") <
    worker.indexOf("httpd_req_async_handler_complete(request)"));
  assert.match(web, /strcmp\(uri, "\/variables\.js"\)/);
  assert.match(web, /equalizerEnabled=false/);
  assert.match(web, /\.uri = "\/upload"/);
  assert.match(web, /\.uri = "\/webboard"/);
  assert.match(web, /webboard_upload_handler/);
  const upload = read("main", "web_upload.c");
  assert.match(read("main", "web_multipart.h"), /components\/native_storage\/include\/web_multipart\.h/);
  assert.match(upload, /mp_form_data_boundary\(type, boundary, sizeof\(boundary\)\)/);
  assert.match(upload, /mp_init\(&parser, boundary, web_file_form_part, form\)/);
  assert.match(upload, /mp_feed\(&parser, chunk, \(size_t\)received\)/);
  const receiver = section(upload, "static bool receive_form(", "static bool upload_destination(");
  assert.match(receiver, /complete = mp_complete\(&parser\)/);
  assert.match(receiver, /done:[\s\S]*native_wifi_erase\(chunk, sizeof\(chunk\)\);[\s\S]*return complete;/);
  assert.match(websocket, /\.uri = "\/ws"/);
  assert.match(websocket, /\.is_websocket = true/);
  assert.match(websocket, /httpd_ws_recv_frame/);
  assert.match(websocket, /httpd_ws_send_frame/);
  assert.match(websocket, /httpd_ws_send_frame_async/);
  assert.match(websocket, /httpd_queue_work\(s_server, broadcast_work, work\)/);
  assert.match(websocket, /httpd_sess_set_send_override\(s_server, socket, ws_send_complete\)/);
  assert.match(websocket, /httpd_sess_set_recv_override\(s_server, socket, ws_receive_complete\)/);
  assert.match(section(websocket, "static int ws_send_complete(", "static int ws_receive_complete("),
    /native_web_transport_send\([\s\S]*ws_wait\(socket, writable, deadline\)/);
  assert.match(section(websocket, "static int ws_receive_complete(", "static void ws_finish_client("),
    /native_web_transport_recv\([\s\S]*ws_wait\(socket, writable, deadline\)/);
  assert.doesNotMatch(websocket, /httpd_ws_send_data\(/);
  assert.match(websocket, /atomic_load\(&s_status_send_pending\) == 0U/);
  assert.match(section(websocket, "static void ws_finish_client(", "static void ws_fail_client("),
    /ws_session\(s_server, client->socket\) != client[\s\S]*native_web_transport_shutdown\(s_server, client->socket, graceful\)/);
  assert.match(websocket, /strcmp\(command, "next"\)/);
  assert.match(websocket, /strcmp\(command, "prev"\)/);
  assert.doesNotMatch(web + websocket, /AsyncWebServer|AsyncWebSocket|Arduino/);
  // Actual static async-session ordering: run-native-static-lifetime.py.
  // Transport partial/WANT/deadline/session semantics: run-native-web-transport.py,
  // run-c3-websocket-io.py and the TCP/TLS integration runners cited above.
  // Shared multipart acceptance/rejection executes in run-multipart-headers.py
  // and run-cyd-uploads.py (which also compiles the actual C3 upload handler).
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
  const upload = read("main", "web_upload.c");
  const form = shared("native_storage", "include", "web_file_form.h");
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
  assert.match(read("main", "web_file_form.h"), /components\/native_storage\/include\/web_file_form\.h/);
  assert.match(form, /strcmp\(name \+ n - 3, "\.gz"\)/);
  assert.match(section(web, "static FILE *open_nonempty_file(", "static bool web_asset_available("),
    /web_upload_open_file\(path\)[\s\S]*fgetc\(file\) == EOF[\s\S]*fseek\(file, 0, SEEK_SET\)/);
  const open = section(upload, "FILE *web_upload_open_file(", "bool web_upload_publish_file(");
  assert.match(open, /xSemaphoreTake\(s_storage_lock,[\s\S]*native_file_recover\(path, backup\)[\s\S]*fopen\(path, "rb"\)/);
  assert.match(web, /\/spiffs\/www\/%s\.gz/);
  assert.match(web, /Content-Encoding", "gzip"/);
  assert.match(form, /strcmp\(field, "www"\)/);
  assert.match(form, /strcmp\(field, "data"\)/);
  assert.match(web, /\.uri = "\/emergency"/);
  // Real production nonempty/open/read/error/recovery paths are exercised by
  // run-web-warning-regressions.py and run-native-static-lifetime.py; shared
  // file transactions and C3 upload namespace rules by run-cyd-uploads.py.
});

test("native playlist reload event is emitted only after a successful upload", () => {
  const websocket = read("main", "websocket_service.c");
  const websocketHeader = read("main", "websocket_service.h");
  const web = read("main", "web_service.c");

  assert.match(websocket, /strcmp\(command, "submitplaylist"\)/);
  assert.match(websocket, /strcmp\(command, "submitplaylistdone"\)/);
  assert.match(websocketHeader, /websocket_service_notify_playlist_changed/);
  assert.match(
    websocket,
    /static atomic_bool s_playlist_changed_pending/,
  );
  assert.match(
    websocket,
    /atomic_exchange\(&s_playlist_changed_pending, false\)[\s\S]*?"\{\\"file\\":\\"\/data\/playlist\.csv\\"\}"/,
  );
  assert.match(
    websocket,
    /websocket_service_notify_playlist_changed[\s\S]*?atomic_store\(&s_playlist_changed_pending, true\)/,
  );
  const upload = read("main", "web_upload.c");
  assert.match(upload,
    /for \(unsigned i = 0; ok && i < form\.files; \+\+i\)[\s\S]*if \(form\.playlist\[i\]\)[\s\S]*ok = radio_control_publish_playlist\(temporary,\s*web_upload_publish_playlist\) == ESP_OK;\s*playlist_saved = ok;/);
  assert.match(section(upload, "bool web_upload_publish_playlist(", "// All three routes"),
    /xSemaphoreTake\(s_storage_lock,[\s\S]*native_file_replace_pair\(/);
  const catalog = read("main", "radio_control.c");
  assert.match(section(catalog, "esp_err_t radio_control_publish_playlist(", "esp_err_t radio_control_play("),
    /write_playlist_index_candidate_locked\(csv_temporary, &count\)[\s\S]*if \(result == ESP_OK\)[\s\S]*publisher\(csv_temporary, PLAYLIST_INDEX_TEMP_PATH\)/);
  assert.match(upload, /if \(playlist_saved\) websocket_service_notify_playlist_changed\(\)/);
  // Actual complete-parser-before-publication, candidate-index failure,
  // pair rollback, response failure and notifications: run-cyd-uploads.py;
  // catalog preparation/validation: run-playlist-index.py.
});

test("native SPIFFS image contains the shared WebUI and repository playlist", () => {
  const component = read("main", "CMakeLists.txt");

  assert.match(component, /file\(COPY "\$\{YORADIO_ROOT\}\/data\/"/);
  assert.match(component, /playlist\.csv" COPYONLY/);
  assert.match(component, /spiffs_create_partition_image\(spiffs "\$\{NATIVE_SPIFFS_ROOT\}"/);
});

test("native radio persists and restores the last selected station", () => {
  const controls = read("main", "radio_control.c");

  assert.match(controls, /RADIO_NVS_NAMESPACE "radio"/);
  assert.match(controls, /RADIO_NVS_LAST_STATION "last_station"/);
  assert.match(
    controls,
    /load_last_station\(&saved_item\)[\s\S]*s_current_item = saved_item/,
  );
  assert.match(
    controls,
    /audio_service_play\(s_candidate_url,[\s\S]*s_current_item = item[\s\S]*save_last_station\(item\)/,
  );
  assert.match(
    controls,
    /nvs_set_u16\(handle, RADIO_NVS_LAST_STATION, item\)[\s\S]*nvs_commit\(handle\)/,
  );
  assert.match(
    controls,
    /playlist_station\(s_current_item,[\s\S]*s_current_item = 1/,
  );
});
