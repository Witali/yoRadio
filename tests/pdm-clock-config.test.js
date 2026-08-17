const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(
  path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "PdmOutput.cpp"),
  "utf8",
);

test("PDM hardware always runs at 48 kHz with a 6.144 MHz carrier", () => {
  assert.match(source, /kPdmOutputSampleRate\s*=\s*48000/);
  assert.match(source, /kPdmCarrierRate\s*=\s*6144000/);
  assert.match(
    source,
    /I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG\(kPdmOutputSampleRate\)/,
    "PDM must use the fixed 48 kHz high-SNR DAC profile",
  );
});

test("PDM linearly upsamples source rates below 48 kHz", () => {
  assert.match(source, /inputSampleRate == kPdmOutputSampleRate/);
  assert.match(source, /while \(phase <= kPdmOutputSampleRate\)/);
  assert.match(source, /phase \* kInterpolationScale/);
  assert.doesNotMatch(source, /(?:^|\s)int64_t scaled/);
  assert.match(source, /resamplerNextPhase = phase - kPdmOutputSampleRate/);
  assert.match(source, /resetResampler\(\);[\s\S]*memset\(sampleBuffer/);
});

test("minimal IDF build corrects fractional fp/fs PDM clock calculation", () => {
  const cmake = fs.readFileSync(
    path.join(__dirname, "..", "idf", "esp32-cyd2usb-minimal", "CMakeLists.txt"),
    "utf8",
  );

  assert.match(cmake, /YORADIO_DAC_BACKEND STREQUAL "pdm"/);
  assert.match(cmake, /uint64_t\)rate \* I2S_LL_PDM_BCK_FACTOR/);
  assert.match(cmake, /pdm_tx_clk->up_sample_fp\) \/[\s\S]*pdm_tx_clk->up_sample_fs/);
  assert.match(cmake, /list\(FILTER i2s_driver_sources EXCLUDE REGEX/);
});
