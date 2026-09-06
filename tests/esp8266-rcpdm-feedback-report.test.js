const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const dir = path.join(root, 'docs/benchmarks/esp8266-rcpdm-feedback-2026-09-06');
const read = file => JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));

test('feedback report compares equal rates and preserves coherent LSB evidence', () => {
  const q = read('quality.json'), lsb = read('lsb.json'), delay = read('delay.json');
  assert.equal(q.cases.length, 9);
  assert.equal(q.state_bytes, 16);
  assert.equal(q.firmware_flashed, false);
  assert.equal(lsb.algorithm_sha256, q.source_sha256['esp8266/rtos-sdk-native/main/rc_pdm_feedback.h']);
  const baseline = JSON.parse(fs.readFileSync(path.join(root,
    'docs/benchmarks/esp8266-pdm-frequency-matrix-2026-09-06/results.json'), 'utf8'));
  for (const bits of [8, 16, 32, 64, 128]) {
    const c = q.configs[`feedback${bits}`];
    assert.equal(c.bit_rate_hz, 48000 * bits);
    assert.equal(c.alpha, 2 / bits);
    assert.equal(c.alpha, 1 / (2 ** c.shift));
    assert.equal(c.feedback_shift, 0);
    assert.equal(c.dither, 2);
    assert.equal(c.interpolate, true);
    for (const row of q.cases) {
      const old = baseline.cases.find(b => b.id === row.id);
      assert.equal(row.pcm_sha256, old.pcm_sha256);
      for (const [name, values] of Object.entries(row.baselines)) {
        assert.deepEqual(values, old.quality.models[name]);
      }
      const controls = Object.keys(row.baselines).filter(name => baseline.variants[name].bits === bits);
      assert.equal(controls.length, 3);
      for (const name of controls) assert.equal(baseline.variants[name].bit_rate_hz, c.bit_rate_hz);
      assert.equal(Object.keys(row.quality.models[`feedback${bits}`]).length, 3);
    }
  }
  assert.deepEqual(lsb.seeds.map(s => s.seed), [1, 8266, 2654435769]);
  assert.equal(lsb.checks.pass, true);
  assert.ok(Math.abs(lsb.checks.gain_magnitude - 1) < 0.1);
  assert.ok(lsb.checks.zero_coherent_noise_relative_tone < 0.1);
  assert.ok(Math.abs(lsb.checks.dc_plus_lsb - 1) < 0.1);
  assert.ok(Math.abs(lsb.checks.dc_minus_lsb + 1) < 0.1);
  assert.equal(delay.fixed_delay_seconds, 31 / (2 * 1536000));
  assert.equal(delay.cases.length, 5);
  for (const row of delay.cases) assert.equal(row.raw_db,
    q.cases.find(c => c.id === row.id).quality.models.feedback32.rc10us.snr_to_input_db);
});

test('new feedback backend stays opt-in and mutually exclusive with old experiments', () => {
  const readSource = file => fs.readFileSync(path.join(root, file), 'utf8');
  const kconfig = readSource('esp8266/rtos-sdk-native/main/Kconfig.projbuild');
  const block = kconfig.split('config YORADIO_RCPDM_FEEDBACK')[1].split('\nchoice ')[0];
  assert.match(block, /depends on YORADIO_AUDIO_OUTPUT_I2S_RCPDM/);
  assert.match(block, /default n/);
  assert.match(readSource('esp8266/rtos-sdk-native/sdkconfig.rcpdm-feedback.defaults'), /CONFIG_YORADIO_RCPDM_FEEDBACK=y/);
  assert.doesNotMatch(readSource('esp8266/rtos-sdk-native/sdkconfig.defaults'), /CONFIG_YORADIO_RCPDM_FEEDBACK=y/);
  assert.match(readSource('esp8266/rtos-sdk-native/main/CMakeLists.txt'), /RC-PDM feedback cannot be combined/);
});
