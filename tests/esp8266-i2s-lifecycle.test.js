const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const output = fs.readFileSync(
  path.resolve(
    __dirname,
    "..",
    "esp8266",
    "rtos-sdk-native",
    "main",
    "native_audio_output.c",
  ),
  "utf8",
);

test("ESP8266 keeps SLC DMA active while the radio is silent", () => {
  assert.match(
    output,
    /s_i2s_started = true;[\s\S]*i2s_zero_dma_buffer\(I2S_NUM_0\)/,
  );
  assert.match(
    output,
    /void native_audio_output_silence\(void\)[\s\S]*i2s_zero_dma_buffer\(I2S_NUM_0\)/,
  );
  assert.doesNotMatch(output, /i2s_stop\(I2S_NUM_0\)/);
});

test("ESP8266 re-primes the I2S clock before PCM after silence", () => {
  assert.match(
    output,
    /if \(!s_clock_primed \|\| sample_rate != s_sample_rate\)[\s\S]*i2s_set_clk\(I2S_NUM_0, sample_rate/,
  );
  assert.match(
    output,
    /void native_audio_output_silence\(void\)[\s\S]*s_clock_primed = false/,
  );
});
