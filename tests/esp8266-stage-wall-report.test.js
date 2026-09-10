const test = require('node:test'), assert = require('node:assert/strict');
const {summarize} = require('../tools/esp8266_opus_profile/run_stage_wall.cjs');
function sample(t) {
  return {host_ms:t, health:{generation:1,uptime_ms:t,rx_bytes:t,pcm_frames:t*48,
    sample_rate:48000,pcm_age_ms:1,underruns:0,free_heap:6000,dma_eofs:t,output_enabled:true},
    profile:{generation:1,uptime_ms:t,stages:[[t*100,300,10,0],[t*500,15000,20,0],
      [t*300,13000,30,0],[t*50,1000,40,0]]}};
}
test('wall report retains continuity failures and labels wall time as not CPU', () => {
  const a=sample(1000), b=sample(28000);
  let r=summarize([a,b]);
  assert.equal(r.continuity.pass,true);
  assert.deepEqual(r.stages.map(s=>s.wall_percent),[10,50,30,5]);
  assert.match(r.timing_kind,/NOT CPU/);
  b.health.underruns=7; b.profile.stages[1][3]=6;
  r=summarize([a,b]);
  assert.equal(r.continuity.pass,false);
  assert.equal(r.stages[1].misses,6);
  assert.equal(r.unattributed_misses_approx,1);
});
test('counter rollover works; reset/generation/missing samples cannot pass', () => {
  const a=sample(1000), b=sample(28000);
  a.profile.stages[0][0]=0xfffffff0; b.profile.stages[0][0]=0x10;
  assert.equal(summarize([a,b]).stages[0].wall_ms,0.032);
  b.profile.generation=2;
  assert.match(summarize([a,b]).profile_error,/mismatch/);
  b.profile.generation=1; b.profile.uptime_ms=1;
  assert.match(summarize([a,b]).profile_error,/mismatch/);
  assert.match(summarize([{error:'timeout'},b]).profile_error,/missing/);
});

test('v2 separates empty-input waits from post-decode pacing, retaining every miss', () => {
  const a=sample(1000), b=sample(28000);
  for(const s of [a,b]) {
    s.profile.profile_version=2;
    s.profile.stages.push([s.host_ms*20,1000,s.host_ms,0]);
  }
  b.health.underruns=9;
  b.profile.stages[3][3]=2;b.profile.stages[4][3]=7;
  const r=summarize([a,b]);
  assert.equal(r.continuity.pass,false);
  assert.deepEqual(r.stages.slice(3).map(s=>[s.name,s.wall_percent,s.misses]),
    [['post_decode_wait',5,2],['input_wait',2,7]]);
  assert.equal(r.unattributed_misses_approx,0);
  b.profile.stages[0][1]=0xffffff4b;
  const badClock=summarize([a,b]);
  assert.equal(badClock.timing_valid,false);
  assert.match(badClock.profile_error,/clock/);
  assert.equal(badClock.stages[4].misses,7);
  b.profile.profile_version=3;
  assert.match(summarize([a,b]).profile_error,/invalid stages/);
  delete b.profile.profile_version;b.profile.stages.pop();
  assert.match(summarize([a,b]).profile_error,/version mismatch/);
});
