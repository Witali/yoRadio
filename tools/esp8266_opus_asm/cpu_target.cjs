const assert = require('node:assert/strict');

// Current user target. Historical selection.cjs reports retain their original
// 70% informational field; it is not the active goal or the acceptance gate.
const CURRENT_RAW_CPU_TARGET_PERCENT = 80;

function evaluateRawCpuTarget(cases, maximumPercent = CURRENT_RAW_CPU_TARGET_PERCENT) {
  assert.ok(Number.isFinite(maximumPercent) && maximumPercent > 0 && maximumPercent <= 100,
    'Raw CPU target must be in (0,100]');
  const matches = cases.filter(c => c.name === 'stereo-192');
  assert.equal(matches.length, 1, 'Exactly one stereo-192 case is required');
  const median = matches[0].candidate?.task_budget_percent?.median;
  assert.ok(Number.isFinite(median) && median > 0, 'Measured CPU median must be positive and finite');
  return {
    bitrate_kbps: 192,
    cpu_mhz: 160,
    maximum_percent: maximumPercent,
    measured_median_percent: median,
    raw_cpu_target_met: median <= maximumPercent,
    scope: 'Raw CPU threshold only; caller must validate RAM packets, exact PCM, memory and >=10 physical runs. Does not qualify continuous I2S PDM or WebUI.'
  };
}

module.exports = {CURRENT_RAW_CPU_TARGET_PERCENT, evaluateRawCpuTarget};
