const assert = require('node:assert/strict');
function classify(report) {
  const s = report.final;
  assert.ok(s && [3,4].includes(s.state), 'Unknown/non-terminal board state; do not restart');
  assert.equal(s.physical_output, false, 'Expected decoder-only firmware');
  assert.ok(report.after?.data, 'Post-run board observation required');
  if (s.state === 4) {
    assert.ok(Number.isInteger(s.error) && s.error !== 0, 'Missing device error');
    return {completed:false, device_error:s.error};
  }
  assert.equal(s.error, 0);
  assert.ok(!report.error, report.error);
  const fixtures = report.fixtures?.fixtures;
  assert.ok(fixtures?.length, 'Explicit fixture manifest required');
  assert.ok(Number.isInteger(s.rounds) && s.rounds > 0);
  assert.equal(s.results.length, fixtures.length);
  const cases = s.results.map((v,i) => {
    const f = fixtures[i];
    assert.equal(v.error, 0);
    assert.equal(v.pcm_hash, f.expected_hash, 'PCM hash mismatch');
    assert.equal(v.samples, f.samples*s.rounds, 'PCM count mismatch');
    assert.equal(v.packets, f.packet_count*s.rounds, 'Packet count mismatch');
    assert.ok(Number.isSafeInteger(v.task_us) && v.task_us > 0);
    assert.ok(Number.isSafeInteger(v.min_dram) && v.min_dram > 0);
    return {name:f.name, cpu_budget_percent:v.task_us*4.8/v.samples};
  });
  return {completed:true, min_dram:Math.min(...s.results.map(v=>v.min_dram)), cases};
}
module.exports = {classify};
if (require.main === module) {
  try { console.log(JSON.stringify(classify(JSON.parse(require('node:fs').readFileSync(process.argv[2],'utf8'))))); }
  catch (e) { console.error(e.message); process.exitCode=1; }
}
