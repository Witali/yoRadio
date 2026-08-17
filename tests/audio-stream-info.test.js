const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

function read(...parts) {
  return fs.readFileSync(path.join(__dirname, "..", ...parts), "utf8");
}

test("CYD player enables decoded stream information", () => {
  const options = read("yoRadio", "myoptions.h");
  assert.match(options, /#define SHOW_STREAM_INFO\s+true/);
});

test("audio callbacks retain decoder sample rate and channel count", () => {
  const config = read("yoRadio", "src", "core", "config.h");
  const handlers = read("yoRadio", "src", "core", "audiohandlers.h");

  assert.match(config, /uint32_t sampleRate/);
  assert.match(config, /uint8_t channels/);
  assert.match(handlers, /strstr\(info, "SampleRate: "\)/);
  assert.match(handlers, /strstr\(info, "Channels: "\)/);
  assert.match(handlers, /config\.station\.sampleRate = value/);
  assert.match(handlers, /config\.station\.channels = value/);
});

test("player shows codec, kHz and mono or stereo channel layout", () => {
  const display = read("yoRadio", "src", "core", "display.cpp");

  assert.match(display, /"%s %s kHz %s \(%u ch\)"/);
  assert.match(display, /config\.station\.channels == 1U \? "mono" : "stereo"/);
  assert.match(display, /case BF_MP3:\s+format = "MP3"/);
  assert.match(display, /case BF_AAC:\s+format = "AAC"/);
  assert.match(display, /case BF_FLAC:\s+format = "FLAC"/);
});

test("stream information is cleared between stations", () => {
  const config = read("yoRadio", "src", "core", "config.cpp");
  const player = read("yoRadio", "src", "core", "player.cpp");

  for (const source of [config, player]) {
    assert.match(source, /station\.sampleRate\s*=\s*0/);
    assert.match(source, /station\.channels\s*=\s*0/);
  }
});
