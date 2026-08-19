const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("native ESP-IDF application code remains entirely integer based", () => {
  const main = path.join(root, "idf", "esp32c3-oled-native", "main");
  const sources = fs
    .readdirSync(main)
    .filter((name) => /\.[ch]$/.test(name))
    .map((name) => fs.readFileSync(path.join(main, name), "utf8"))
    .join("\n");

  assert.doesNotMatch(sources, /\b(?:float|double|long double)\b/);
  assert.doesNotMatch(
    sources,
    /\b(?:sinf|cosf|tanf|sqrtf|powf|roundf|lrintf|fabsf|fmodf|atan2f|logf|expf)\s*\(/,
  );
});

test("C3 Arduino audio hot path uses fixed-point gain and time", () => {
  const audio = read("yoRadio", "src", "audioI2S", "Audio.cpp");
  const header = read("yoRadio", "src", "audioI2S", "AudioEx.h");

  assert.match(audio, /m_vol\) \* abs\(m_balance\) \+ 8U\) \/ 16U/);
  assert.match(audio, /s\[LEFTCHANNEL\] \* leftGain\) >> 8/);
  assert.doesNotMatch(audio, /float step = \(float\)m_vol/);
  assert.match(header, /uint64_t\s+m_audioCurrentTimeUs/);
  assert.match(audio, /static_cast<uint64_t>\(bd\) \* 8000000U/);
  assert.doesNotMatch(audio, /m_audioCurrentTime\s*\+=/);
  assert.match(header, /audioFileSeek\(uint16_t speedPermille\)/);
  assert.match(audio, /getSampleRate\(\)\) \* speedPermille \+ 500U/);

  const gain = (volume, balance) => {
    const attenuation = Math.floor((volume * Math.abs(balance) + 8) / 16);
    return {
      left: volume - (balance < 0 ? attenuation : 0),
      right: volume - (balance > 0 ? attenuation : 0),
    };
  };
  assert.deepEqual(gain(254, 0), { left: 254, right: 254 });
  assert.deepEqual(gain(254, -16), { left: 0, right: 254 });
  assert.deepEqual(gain(254, 16), { left: 254, right: 0 });
  assert.deepEqual(gain(128, 8), { left: 128, right: 64 });
});

test("AAC and FLAC bitrate estimates no longer require floating point", () => {
  const aac = read(
    "yoRadio",
    "src",
    "audioI2S",
    "aac_decoder",
    "aac_decoder.cpp",
  );
  const aacHeader = read(
    "yoRadio",
    "src",
    "audioI2S",
    "aac_decoder",
    "aac_decoder.h",
  );
  const flac = read(
    "yoRadio",
    "src",
    "audioI2S",
    "flac_decoder",
    "flac_decoder.cpp",
  );

  assert.match(aacHeader, /uint32_t frameBytes/);
  assert.doesNotMatch(aacHeader, /float compressionRatio/);
  assert.match(aac, /pcmBitrate \* m_AACDecInfo->frameBytes/);
  assert.match(flac, /encodedBits \* FLACMetadataBlock->sampleRate/);
  assert.doesNotMatch(flac, /float BitsPerSamp/);
});

test("C3 compile-time profile removes weather and floating-point EQ", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");
  const display = read(
    "yoRadio",
    "src",
    "displays",
    "conf",
    "displaySSD1306_72x40conf.h",
  );
  const audio = read("yoRadio", "src", "audioI2S", "Audio.cpp");
  const header = read("yoRadio", "src", "audioI2S", "AudioEx.h");
  const timekeeper = read("yoRadio", "src", "core", "timekeeper.cpp");

  assert.match(profile, /#define HIDE_WEATHER/);
  assert.match(display, /#define HIDE_WEATHER/);
  assert.match(timekeeper, /#ifdef HIDE_WEATHER\s+forceWeather = false/);
  assert.match(timekeeper, /#ifdef HIDE_WEATHER\s+const bool syncPending = forceTimeSync/);
  assert.match(audio, /#if YORADIO_EQUALIZER_ENABLED\s+void Audio::IIR_calculateCoefficients/);
  assert.match(header, /#if YORADIO_EQUALIZER_ENABLED\s+typedef struct _filter/);
});

test("integer ratios replace UI and storage floating-point calculations", () => {
  const mqtt = read(
    "yoRadio",
    "src",
    "async-mqtt-client",
    "AsyncMqttClient.cpp",
  );
  const fixed = read("yoRadio", "src", "core", "fixedpoint.h");
  const telnet = read("yoRadio", "src", "core", "telnet.cpp");
  const server = read("yoRadio", "src", "core", "netserver.cpp");
  const widgets = read("yoRadio", "src", "displays", "widgets", "widgets.cpp");

  assert.match(fixed, /numerator \* scale \+ denominator \/ 2U/);
  assert.match(mqtt, /_keepAlive\) \* 1000U \* 7U\) \/ 10U/);
  assert.doesNotMatch(mqtt, /1000 \* 0\.7/);
  assert.match(telnet, /fixedpoint::ratio\(fragmented, freeHeap, 10000U\)/);
  assert.match(server, /SPIFFS\.totalBytes\(\)\) \* 68U\) \/ 100U/);
  assert.match(widgets, /dsp\.height\(\) \+ _plItemHeight \/ 2U/);
  assert.doesNotMatch(widgets, /round\(\(float\)/);
});
