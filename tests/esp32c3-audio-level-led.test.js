const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("ESP32-C3 profile enables the active-low GPIO8 audio indicator", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");
  const options = read("yoRadio", "src", "core", "options.h");

  assert.match(profile, /AUDIO_LEVEL_LED_PIN\s+8/);
  assert.match(profile, /AUDIO_LEVEL_LED_MAX_BRIGHTNESS\s+255/);
  assert.match(options, /AUDIO_LEVEL_LED_UPDATE_MS\s+50/);
  assert.match(options, /AUDIO_LEVEL_LED_PWM_HZ\s+5000/);
  assert.match(options, /AUDIO_LEVEL_LED_DECAY_STEP\s+8/);
});

test("audio LED follows the strongest normalized VU peak with decay", () => {
  const led = read("yoRadio", "src", "core", "audiolevelled.cpp");
  const audio = read("yoRadio", "src", "audioI2S", "Audio.cpp");
  const main = read("yoRadio", "src", "main.cpp");

  assert.match(led, /player\.get_VUlevel\(255\)/);
  assert.match(led, /min\(leftInverse, rightInverse\)/);
  assert.match(led, /255U - strongestInverse/);
  assert.match(led, /target >= envelope[\s\S]*envelope = target/);
  assert.match(led, /envelope -= AUDIO_LEVEL_LED_DECAY_STEP/);
  assert.match(led, /ledcAttach\(AUDIO_LEVEL_LED_PIN, AUDIO_LEVEL_LED_PWM_HZ, 8\)/);
  assert.match(led, /ledcWrite\(AUDIO_LEVEL_LED_PIN, 255U - brightness\)/);
  assert.match(audio, /!config\.store\.vumeter && AUDIO_LEVEL_LED_PIN == 255/);
  assert.match(main, /audioLevelLed::begin\(\)/);
  assert.match(main, /player\.loop\(\);[\s\S]*audioLevelLed::loop\(\)/);
});
