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

test("player shows compact mono, stereo, or multichannel stream layout without codec", () => {
  const display = read("yoRadio", "src", "core", "display.cpp");

  assert.match(display, /"%s kHz mono"/);
  assert.match(display, /"%s kHz stereo"/);
  assert.match(display, /"%s kHz %u channels"/);
  assert.match(display, /config\.station\.channels == 1U/);
  assert.match(display, /config\.station\.channels == 2U/);
  assert.doesNotMatch(display, /\(%u ch\)/);
});

test("stream information is cleared between stations", () => {
  const config = read("yoRadio", "src", "core", "config.cpp");
  const player = read("yoRadio", "src", "core", "player.cpp");

  for (const source of [config, player]) {
    assert.match(source, /station\.sampleRate\s*=\s*0/);
    assert.match(source, /station\.channels\s*=\s*0/);
  }
});
