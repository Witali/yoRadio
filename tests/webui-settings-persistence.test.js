const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.join(__dirname, "..");
const nativeMain = path.join(root, "idf", "esp32c3-oled-native", "main");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("native WebUI returns persisted values instead of settings constants", () => {
  const ws = read("idf", "esp32c3-oled-native", "main", "websocket_service.c");

  for (const getter of [
    "runtime_settings_get_audio_info",
    "runtime_settings_get_softap_delay_min",
    "runtime_settings_get_audio_buffer_blocks",
    "runtime_settings_get_watchdog",
    "display_settings_get_screen_on",
    "display_settings_get_numbered_playlist",
    "display_settings_get_screensaver_enabled",
    "display_settings_get_screensaver_timeout",
    "display_settings_get_screensaver_blank",
    "display_settings_get_screensaver_playing_enabled",
    "display_settings_get_screensaver_playing_timeout",
    "display_settings_get_screensaver_playing_blank",
    "runtime_settings_get_timezone_hour",
    "runtime_settings_get_timezone_minute",
    "runtime_settings_get_time_sync_interval_min",
    "runtime_settings_get_volume_steps",
  ]) {
    assert.match(ws, new RegExp(`${getter}\\(`), `missing ${getter}`);
  }

  assert.doesNotMatch(ws, /\\"aif\\":1,\\"vu\\":0,\\"softr\\":0/);
  assert.doesNotMatch(ws, /\\"nump\\":0,[\\s\\S]*\\"dspon\\":1/);
  assert.doesNotMatch(ws, /request, "\{\\"vols\\":8/);
});

test("every supported native settings command has a persistent setter", () => {
  const ws = read("idf", "esp32c3-oled-native", "main", "websocket_service.c");
  const commands = {
    audioinfo: "runtime_settings_set_audio_info",
    softap: "runtime_settings_set_softap_delay_min",
    abuff: "runtime_settings_set_audio_buffer_blocks",
    watchdog: "runtime_settings_set_watchdog",
    tzh: "runtime_settings_set_timezone_hour",
    tzm: "runtime_settings_set_timezone_minute",
    sntp1: "runtime_settings_set_sntp1",
    sntp2: "runtime_settings_set_sntp2",
    timeint: "runtime_settings_set_time_sync_interval_min",
    volsteps: "runtime_settings_set_volume_steps",
    screenon: "display_settings_set_screen_on",
    numplaylist: "display_settings_set_numbered_playlist",
    screensaverenabled: "display_settings_set_screensaver_enabled",
    screensavertimeout: "display_settings_set_screensaver_timeout",
    screensaverblank: "display_settings_set_screensaver_blank",
    screensaverplayingenabled: "display_settings_set_screensaver_playing_enabled",
    screensaverplayingtimeout: "display_settings_set_screensaver_playing_timeout",
    screensaverplayingblank: "display_settings_set_screensaver_playing_blank",
  };

  for (const [command, setter] of Object.entries(commands)) {
    assert.match(ws, new RegExp(`strcmp\\(command, "${command}"\\)`));
    assert.match(ws, new RegExp(`${setter}\\(`), `${command} is not persisted`);
  }
});

test("runtime settings use NVS and affect audio pipeline behavior", () => {
  const runtime = fs.readFileSync(path.join(nativeMain, "runtime_settings.c"), "utf8");
  const audio = fs.readFileSync(path.join(nativeMain, "audio_service.c"), "utf8");

  assert.match(runtime, /#define SETTINGS_NVS_NAMESPACE "runtime"/);
  for (const key of ["audioinfo", "softap", "abuff", "watchdog", "tzh", "tzm", "sntp1", "sntp2", "timeint", "volsteps"]) {
    assert.match(runtime, new RegExp(`"${key}"`), `missing NVS key ${key}`);
  }
  assert.match(audio, /runtime_settings_get_audio_buffer_blocks\(\) \* 1600U/);
  assert.match(audio, /xRingbufferCreate\(encoded_ring_size/);
  assert.match(audio, /runtime_settings_get_watchdog\(\)/);
  assert.match(audio, /STREAM_STALL_TIMEOUT_US/);
});

test("display settings are persisted and applied to SSD1306", () => {
  const display = fs.readFileSync(path.join(nativeMain, "display_settings.c"), "utf8");
  const app = fs.readFileSync(path.join(nativeMain, "app_main.c"), "utf8");
  const oled = fs.readFileSync(path.join(nativeMain, "oled_display.c"), "utf8");

  for (const key of ["screen_on", "numbered", "saver_en", "saver_timeout", "saver_blank",
    "play_saver_en", "play_saver_t", "play_saver_b"]) {
    assert.match(display, new RegExp(`"${key}"`), `missing display NVS key ${key}`);
  }
  assert.match(app, /display_settings_screensaver_active\(/);
  assert.match(app, /display_settings_get_numbered_playlist\(/);
  assert.match(app, /runtime_settings_get_audio_info\(/);
  assert.match(oled, /on \? 0xaf : 0xae/);
});

test("Wi-Fi upload keeps all five rows and retry order", () => {
  const network = fs.readFileSync(path.join(nativeMain, "network_service.c"), "utf8");
  const web = fs.readFileSync(path.join(nativeMain, "web_service.c"), "utf8");

  assert.match(network, /#define WIFI_MAX_CREDENTIALS 5/);
  assert.match(network, /s_credentials\[s_credential_count\+\+\]/);
  assert.match(network, /s_credential_index \+ 1U < s_credential_count/);
  assert.match(network, /fwrite\(data, 1, size, file\) == size/);
  assert.match(web, /network_service_save_credentials_file\(data, size\)/);
  assert.doesNotMatch(web, /network_service_save_credentials\(ssid, password\)/);
});

test("shared WebUI hides native controls that cannot be applied", () => {
  const script = zlib.gunzipSync(
    fs.readFileSync(path.join(root, "yoRadio", "data", "www", "script.js.gz"))
  ).toString("utf8");
  const ws = read("idf", "esp32c3-oled-native", "main", "websocket_service.c");

  assert.match(script, /typeof data\.hide !== 'undefined'/);
  assert.match(script, /function hideUnsupportedSetting\(id\)/);
  assert.match(script, /element\.closest\('\.inputwrap'\)/);
  for (const id of ["telnet", "skipup", "mdnsnamerow", "radiolink"]) {
    assert.ok(ws.includes(`\\"${id}\\"`), `native hide list is missing ${id}`);
  }
});
