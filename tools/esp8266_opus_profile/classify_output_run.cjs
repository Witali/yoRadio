// Permit the next attempt only after a terminal, understood observation.
// A completed measurement is NOT a continuity pass.
const assert=require('node:assert/strict');
const {analyzeOutput}=require('./output_benchmark_result.cjs');
function classify(report) {
  const s=report.final;
  assert.ok(s && [3,4].includes(s.state),'Non-terminal/unknown board state; do not restart');
  assert.equal(s.physical_output,true,'Expected physical-output firmware');
  assert.ok(report.after?.data,'Missing post-run observation; inspect board');
  if(s.state===4) {
    assert.notEqual(s.error,0,'Terminal error without error code');
    return {terminal:true,completed:false,device_error:s.error,continuous_cases:0};
  }
  assert.equal(s.error,0);
  assert.ok(!report.error || report.error==='Physical output continuity gate failed; results retained',
    'Unexpected validation failure; inspect report before another POST');
  const fixtures=report.fixtures?.fixtures;
  assert.ok(fixtures?.length,'Explicit fixture manifest required');
  assert.equal(s.results.length,fixtures.length);
  const cases=s.results.map((item,i)=>{
    const f=fixtures[i];
    assert.equal(item.pcm_hash,f.expected_hash,'PCM hash mismatch');
    assert.equal(item.samples,f.samples*s.rounds,'PCM sample count mismatch');
    assert.equal(item.packets,f.packet_count*s.rounds,'Packet count mismatch');
    return {name:f.name,...analyzeOutput(item)};
  });
  return {terminal:true,completed:true,continuous_cases:cases.filter(c=>c.pass).length,
    total_cases:cases.length,min_dram:Math.min(...s.results.map(c=>c.min_dram)),cases};
}
module.exports={classify};
if(require.main===module) {
  try { console.log(JSON.stringify(classify(JSON.parse(require('node:fs').readFileSync(process.argv[2],'utf8'))))); }
  catch(e) { console.error(e.message);process.exitCode=1; }
}
