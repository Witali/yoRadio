const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

test("ESP32-C3 OLED profile disables equalizer processing", () => {
  const profile = read("yoRadio", "boards", "esp32c3_oled_042.h");
  const options = read("yoRadio", "src", "core", "options.h");
  const player = read("yoRadio", "src", "core", "player.cpp");
  const audio = read("yoRadio", "src", "audioI2S", "Audio.cpp");

  assert.match(profile, /YORADIO_EQUALIZER_ENABLED\s+0/);
  assert.match(options, /YORADIO_EQUALIZER_ENABLED\s+1/);
  assert.match(player, /#elif I2S_DOUT!=255 \|\| I2S_INTERNAL\s+setEqualizerEnabled\(false\)/);
  assert.match(audio, /#if YORADIO_EQUALIZER_ENABLED\s+if\(m_equalizerEnabled\) \{\s+sample = IIR_filterChain0/);
  assert.match(audio, /#if YORADIO_EQUALIZER_ENABLED\s+void Audio::IIR_calculateCoefficients/);
});

test("disabled equalizer commands are blocked by firmware", () => {
  const config = read("yoRadio", "src", "core", "config.cpp");
  const server = read("yoRadio", "src", "core", "netserver.cpp");

  assert.match(config, /void Config::setTone[\s\S]*#if YORADIO_EQUALIZER_ENABLED/);
  assert.match(server, /#if YORADIO_EQUALIZER_ENABLED\s+if \(strcmp\(_wscmd, "trebble"\)/);
  assert.match(server, /#if YORADIO_EQUALIZER_ENABLED\s+if \(request->hasArg\("trebble"\)/);
  assert.match(server, /var equalizerEnabled=%s/);
});

test("shared WebUI hides tone controls when firmware disables them", () => {
  const compressed = fs.readFileSync(
    path.join(root, "yoRadio", "data", "www", "script.js.gz"),
  );
  const script = zlib.gunzipSync(compressed).toString("utf8");

  assert.match(script, /function applyPlayerCapabilities\(\)/);
  assert.match(script, /typeof equalizerEnabled !== 'undefined' && !equalizerEnabled/);
  assert.match(script, /\['bass', 'middle', 'trebble'\]/);
  assert.match(script, /control\.closest\('li'\)\.remove\(\)/);
  assert.match(script, /getId\('content'\)\.innerHTML = player;\s+applyPlayerCapabilities\(\);/);
});
