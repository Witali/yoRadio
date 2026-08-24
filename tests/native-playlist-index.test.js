const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("native C3 uses the Arduino-compatible playlist offset index", () => {
  const source = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "radio_control.c",
  );
  const header = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "radio_control.h",
  );

  assert.match(source, /PLAYLIST_INDEX_PATH "\/spiffs\/data\/index\.dat"/);
  assert.match(source, /long position = ftell\(playlist\)/);
  assert.match(source, /fwrite\(&offset, sizeof\(offset\), 1, index\)/);
  assert.match(source, /s_playlist_count = count/);
  assert.match(source, /load_playlist_index_locked\(\)/);
  assert.match(source, /build_playlist_index_locked\(\)/);
  assert.match(header, /radio_control_reindex_playlist\(void\)/);

  const stationStart = source.indexOf("static bool playlist_station");
  const countStart = source.indexOf("static uint16_t playlist_count");
  const playStart = source.indexOf("static esp_err_t play_locked");
  assert.ok(stationStart >= 0 && countStart > stationStart && playStart > countStart);
  const station = source.slice(stationStart, countStart);
  const count = source.slice(countStart, playStart);
  assert.match(station, /fseek\(index, index_position, SEEK_SET\)/);
  assert.match(station, /fread\(&offset, sizeof\(offset\), 1, index\)/);
  assert.match(station, /fseek\(playlist, \(long\)offset, SEEK_SET\)/);
  assert.doesNotMatch(station, /while\s*\(.*fgets/);
  assert.match(count, /return s_playlist_count/);
  assert.doesNotMatch(count, /fgets|fopen/);
});

test("native C3 rebuilds the playlist index after every upload path", () => {
  const web = read(
    "idf",
    "esp32c3-oled-native",
    "main",
    "web_service.c",
  );
  const saveStart = web.indexOf("static esp_err_t save_playlist");
  const wifiStart = web.indexOf("static esp_err_t save_wifi", saveStart);
  assert.ok(saveStart >= 0 && wifiStart > saveStart);
  const savePlaylist = web.slice(saveStart, wifiStart);
  assert.match(savePlaylist, /radio_control_reindex_playlist\(\)/);
  assert.match(web, /save_playlist\(data, size\)/);
  assert.match(web, /save_playlist\(payload, payload_end - payload\)/);
});
