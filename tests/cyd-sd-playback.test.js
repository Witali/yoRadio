const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("CYD2USB assigns hardware SPI to display and SD while touch is software SPI", () => {
  const options = read("yoRadio", "myoptions.h");
  assert.match(options, /#define\s+DSP_HSPI\s+true/);
  assert.match(options, /#define\s+TS_SOFTSPI\s+true/);
  assert.match(options, /#define\s+TS_SPIPINS\s+25,\s*39,\s*32/);
  assert.match(options, /#define\s+SDC_CS\s+5/);
  assert.match(options, /#define\s+SDSPISPEED\s+20000000/);
});

test("CYD2USB Arduino build selects the verified 80 MHz QIO flash profile", () => {
  const flashScript = read(
    ".agents", "skills", "flash-reset-esp32", "scripts", "flash_yoradio.ps1"
  );
  assert.match(flashScript, /FlashMode=qio,FlashFreq=80/);
  assert.match(flashScript, /QIO-aware bootloader/);
  assert.match(flashScript, /"--flash-mode", "dio"/);
});

test("software XPT2046 backend is selected without claiming a hardware SPI host", () => {
  const touchscreen = read("yoRadio", "src", "core", "touchscreen.cpp");
  const softTouch = read("yoRadio", "src", "core", "softxpt2046.cpp");
  assert.match(touchscreen, /#if TS_SOFTSPI[\s\S]*SoftXPT2046Touchscreen ts\(TS_CS, TS_SPIPINS\)/);
  assert.match(softTouch, /transfer16\(0xC1\)/);
  assert.match(softTouch, /transfer16\(0xD1\)/);
  assert.doesNotMatch(softTouch, /SPIClass|beginTransaction/);
});

test("SD index includes every local codec supported by the audio engine", () => {
  const manager = read("yoRadio", "src", "core", "sdmanager.cpp");
  for (const extension of [".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg", ".oga", ".opus"]) {
    assert.ok(manager.includes(`_endsWith(fn, "${extension}")`), `${extension} is not indexed`);
  }
  assert.match(manager, /strncasecmp\(/);
});
