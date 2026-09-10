const test=require('node:test'),assert=require('node:assert/strict');
const {run}=require('../tools/esp8266_opus_profile/check_hoist_reciprocal.cjs');
test('audit: one reciprocal evaluation is exact and replaces three target calls',{timeout:180000},()=>{
  const r=run();assert.equal(r.passed,true);assert.equal(r.host_asan_ubsan.cases,1720896);
  assert.equal(r.target[0].celt_rcp_call_sites,3);assert.equal(r.target[1].celt_rcp_call_sites,1);
});
