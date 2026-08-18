const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const audio = fs.readFileSync(
  path.join(root, "yoRadio", "src", "audioI2S", "Audio.cpp"),
  "utf8",
);
const player = fs.readFileSync(
  path.join(root, "yoRadio", "src", "core", "player.cpp"),
  "utf8",
);

test("built-in DAC startup is deferred until Player initialization", () => {
  const constructor = audio.slice(
    audio.indexOf("Audio::Audio("),
    audio.indexOf("bool Audio::beginOutput()"),
  );
  const internalDac = constructor.slice(
    constructor.indexOf("if (internalDAC)"),
    constructor.indexOf("else {", constructor.indexOf("if (internalDAC)")),
  );

  assert.doesNotMatch(internalDac, /i2s_driver_install/);
  assert.doesNotMatch(internalDac, /i2s_set_dac_mode/);
  assert.match(player, /#if I2S_INTERNAL\s+beginOutput\(\);/);
});

test("legacy DAC routes zero-filled DMA before the midpoint ramp", () => {
  const start = audio.slice(
    audio.indexOf("bool Audio::startDacOutput()"),
    audio.indexOf("bool Audio::writeDacBiasRamp()"),
  );

  const install = start.indexOf("i2s_driver_install");
  const route = start.indexOf("i2s_set_dac_mode");
  const ramp = start.indexOf("writeDacBiasRamp()");
  const silence = start.indexOf("fillDacSilence(true)");
  assert.ok(install >= 0 && route > install);
  assert.ok(ramp > route && silence > ramp);
});

test("DAC bias ramp lasts 100 ms and ends at unsigned midpoint", () => {
  const ramp = audio.slice(
    audio.indexOf("bool Audio::writeDacBiasRamp()"),
    audio.indexOf("void Audio::setBufsize"),
  );

  assert.match(ramp, /rampDurationMs = 100/);
  assert.match(ramp, /\* 128U\) \/ \(rampFrames - 1U\)/);
  assert.match(ramp, /\(code << 24\) \| \(code << 8\)/);
  assert.match(ramp, /idf6_dac_output_write/);
  assert.match(ramp, /i2s_write/);
  assert.doesNotMatch(ramp, /portMAX_DELAY/);
});

test("legacy DAC starts at a clock-safe bootstrap rate", () => {
  const constructor = audio.slice(
    audio.indexOf("Audio::Audio("),
    audio.indexOf("bool Audio::beginOutput()"),
  );
  assert.match(
    constructor,
    /internal DAC \(deferred startup\)[\s\S]*m_i2s_config\.sample_rate\s*=\s*48000/,
  );
});

test("sample-rate changes keep the DAC at midpoint", () => {
  const setter = audio.slice(
    audio.indexOf("bool Audio::setSampleRate"),
    audio.indexOf("uint32_t Audio::getSampleRate"),
  );

  assert.match(
    setter,
    /fillDacSilence\(true\)[\s\S]*idf6_dac_output_set_sample_rate[\s\S]*fillDacSilence\(true\)/,
  );
  assert.match(
    setter,
    /fillDacSilence\(true\)[\s\S]*i2s_set_sample_rates[\s\S]*fillDacSilence\(true\)/,
  );
});

test("silence writes require initialized output hardware", () => {
  const silence = audio.slice(
    audio.indexOf("void Audio::fillDacSilence"),
    audio.indexOf("void Audio::playI2Sremains"),
  );
  assert.match(silence, /!m_f_internalDAC \|\| !m_f_outputReady/);
  assert.match(silence, /0x80008000UL/);
});
