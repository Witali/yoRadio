const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.join(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");
const gunzip = (name) => zlib.gunzipSync(
  fs.readFileSync(path.join(root, "yoRadio", "data", "www", name))
).toString("utf8");

test("WebUI exposes and applies the uppercase-station checkbox", () => {
  const options = gunzip("options.html.gz");
  const script = gunzip("script.js.gz");
  const style = gunzip("style.css.gz");

  assert.match(options, /id="upst"[^>]*data-command="stationuppercase"/);
  assert.match(script, /id=="upst"[\s\S]*station-uppercase/);
  assert.match(style, /\.station-uppercase #nameset\s*{\s*text-transform:\s*uppercase/);
  assert.doesNotMatch(style, /(?:^|\n)#nameset\s*{[^}]*text-transform:\s*uppercase/);
});

test("native firmware persists and renders the station case setting", () => {
  const settings = read("idf", "esp32c3-oled-native", "main", "display_settings.c");
  const websocket = read("idf", "esp32c3-oled-native", "main", "websocket_service.c");
  const display = read("idf", "esp32c3-oled-native", "main", "oled_display.c");
  const app = read("idf", "esp32c3-oled-native", "main", "app_main.c");

  assert.match(settings, /DISPLAY_NVS_STATION_UPPERCASE/);
  assert.match(settings, /nvs_set_u8[\s\S]*station uppercase/i);
  assert.match(websocket, /stationuppercase/);
  assert.match(websocket, /upst/);
  assert.match(display, /codepoint >= 'a'[\s\S]*codepoint >= 0x0430/);
  assert.match(app, /display_settings_get_station_uppercase/);
});

test("Arduino firmware shares the same persistent display setting", () => {
  const config = read("yoRadio", "src", "core", "config.h");
  const handler = read("yoRadio", "src", "core", "commandhandler.cpp");
  const server = read("yoRadio", "src", "core", "netserver.cpp");
  const display = read("yoRadio", "src", "core", "display.cpp");

  assert.match(config, /bool\s+stationUppercase/);
  assert.match(handler, /stationuppercase[\s\S]*store\.stationUppercase/);
  assert.match(server, /upst[\s\S]*store\.stationUppercase/);
  assert.match(display, /setUppercase\(config\.store\.stationUppercase\)/);
});
