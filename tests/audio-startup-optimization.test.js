const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.join(__dirname, "..");

function read(...parts) {
  return fs.readFileSync(path.join(root, ...parts), "utf8");
}

test("web radio waits for an 80 percent startup buffer", () => {
  const source = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  assert.match(source, /InBuff\.capacity\(\) \* 80U \/ 100U/);
  assert.match(source, /bufferFilled\(\) >= startupBufferTarget/);
  assert.match(source, /stream ready, buffered %u\/%u bytes/);
});

test("I2S audio buffer defaults and migrates to fourteen blocks", () => {
  const header = read("yoRadio", "src", "core", "config.h");
  const source = read("yoRadio", "src", "core", "config.cpp");

  assert.match(header, /#define CONFIG_VERSION\s+13/);
  assert.match(header, /#define DEFAULT_AUDIO_BUFFER_BLOCKS 14/);
  assert.match(source, /case 9:[\s\S]*store\.abuff < DEFAULT_AUDIO_BUFFER_BLOCKS/);
  assert.match(source, /case 10:[\s\S]*store\.abuff < DEFAULT_AUDIO_BUFFER_BLOCKS/);
  assert.match(source, /store\.abuff = VS1053_CS==255\?DEFAULT_AUDIO_BUFFER_BLOCKS:10/);
});

test("WebUI shows the new audio buffer default", () => {
  const optionsPath = path.join(root, "yoRadio", "data", "www", "options.html.gz");
  const html = zlib.gunzipSync(fs.readFileSync(optionsPath)).toString("utf8");
  const input = html.match(/<input[^>]*id="abuff"[^>]*>/)?.[0];

  assert.ok(input, "audio buffer input is missing");
  assert.match(input, /value="14"/);
});
