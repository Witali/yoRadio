const test = require('node:test'), assert = require('node:assert/strict');
const {CURRENT_RAW_CPU_TARGET_PERCENT, evaluateRawCpuTarget} = require('../tools/esp8266_opus_asm/cpu_target.cjs');
const {selectHighBitrate} = require('../tools/esp8266_opus_asm/selection.cjs');
const cases = median => [{name: 'stereo-192', candidate: {task_budget_percent: {median}}}];

test('current 75% raw CPU target uses an inclusive, unrounded median threshold', () => {
  assert.equal(CURRENT_RAW_CPU_TARGET_PERCENT, 75);
  for (const [value, pass] of [[74.999, true], [75, true], [75.001, false], [79.62652083333333, false], [101, false]]) {
    const result = evaluateRawCpuTarget(cases(value));
    assert.equal(result.raw_cpu_target_met, pass);
    assert.equal(result.measured_median_percent, value);
    assert.equal(result.maximum_percent, 75);
    assert.match(result.scope, /Does not qualify continuous I2S PDM or WebUI/);
  }
});

test('raw target rejects missing, ambiguous and invalid evidence or thresholds', () => {
  for (const value of [0, -1, NaN, Infinity, '80', undefined])
    assert.throws(() => evaluateRawCpuTarget(cases(value)));
  for (const limit of [0, -1, NaN, Infinity, 101, '80'])
    assert.throws(() => evaluateRawCpuTarget(cases(75), limit));
  assert.throws(() => evaluateRawCpuTarget([]));
  assert.throws(() => evaluateRawCpuTarget([...cases(75), ...cases(75)]));
  assert.equal(evaluateRawCpuTarget(cases(75), 70).raw_cpu_target_met, false);
});

test('active CPU target is independent of historical 70% field and relative-speed acceptance', () => {
  const rows = ['mono-12', 'mono-24', 'stereo-64', 'stereo-128', 'stereo-192'].map((name, i) => ({
    name, median_task_reduction_percent: i < 3 ? 0 : -1,
    candidate: {task_budget_percent: {median: [23, 54, 65, 70, 75][i]}}
  }));
  const relative = selectHighBitrate(rows);
  assert.equal(relative.target_192_cpu_at_most_70, false);
  assert.equal(relative.accepted_for_experimental_asm, false);
  assert.equal(evaluateRawCpuTarget(rows).raw_cpu_target_met, true);
});
