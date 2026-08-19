const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("ESP32-C3 BOOT enables the one-button radio layout", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");
  const options = read("yoRadio", "src", "core", "options.h");

  assert.match(profile, /BTN_CENTER\s+9/);
  assert.match(profile, /BTN_CENTER_ONEBUTTON_RADIO\s+1/);
  assert.match(options, /#define BTN_CENTER_ONEBUTTON_RADIO 0/);
});

test("one-button center gestures control playback and station selection", () => {
  const controls = read("yoRadio", "src", "core", "controls.cpp");
  const longPress = controls.match(
    /void onBtnLongPressStart\(int id\) \{([\s\S]*?)void onBtnLongPressStop/,
  );
  const doubleClick = controls.match(
    /void onBtnDoubleClick\(int id\) \{([\s\S]*?)void setIRTolerance/,
  );

  assert.ok(longPress);
  assert.ok(doubleClick);
  assert.match(longPress[1], /case EVT_BTNCENTER:[\s\S]*BTN_CENTER_ONEBUTTON_RADIO[\s\S]*player\.prev\(\)/);
  assert.match(doubleClick[1], /case EVT_BTNCENTER:[\s\S]*BTN_CENTER_ONEBUTTON_RADIO[\s\S]*player\.next\(\)/);
  assert.match(controls, /case EVT_BTNCENTER:[\s\S]*player\.toggle\(\)/);
});
