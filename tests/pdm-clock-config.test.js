const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(
  path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "PdmOutput.cpp"),
  "utf8",
);

test("PDM carrier tracks the current PCM sample rate", () => {
  assert.match(
    source,
    /I2S_PDM_TX_CLK_DEFAULT_CONFIG\(sampleRate\)/,
    "PDM must use Espressif's fixed 128x upsampling profile",
  );
  assert.doesNotMatch(
    source,
    /I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG\(sampleRate\)/,
    "the fixed-carrier DAC profile is inconsistent at 44.1 kHz in the new driver",
  );
  assert.match(source, /pdmClockConfig\.bclk_div\s*=\s*13/);
});

