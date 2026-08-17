const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const source = fs.readFileSync(
  path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "PdmOutput.cpp"),
  "utf8",
);

test("PDM converter adapts to PCM rate while keeping a 6.144 MHz carrier", () => {
  assert.match(
    source,
    /I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG\(sampleRate\)/,
    "PDM must use Espressif's fixed-carrier high-SNR DAC profile",
  );
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
