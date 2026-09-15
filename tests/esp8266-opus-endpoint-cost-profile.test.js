const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {cached,exhaustive}=require('../tools/esp8266_opus_asm/profile_endpoint_cost.cjs');
const {reference}=require('../tools/esp8266_opus_asm/pulse_inverse.cjs');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const report=()=>read('docs/benchmarks/esp8266-opus-endpoint-cost-2026-09-15/summary.json');
test('both cached endpoint costs preserve q and pulses2bits on all standard table budgets',()=>{
 const r=exhaustive();assert.equal(r.cases,378304);assert.equal(r.zero,1982);
 assert.equal(r.zero+r.lower+r.upper,r.cases);assert.deepEqual(r,report().exhaustive);
});
test('cached cost keeps zero sentinel and ties correct for duplicate costs and signed extremes',()=>{
 let cases=0;for(let h=1;h<=40;h++)for(const mode of[0,1,2,3]){
  const cache=[h,...Array.from({length:h},(_,i)=>mode===0?0:mode===1?255:mode===2?Math.floor(i/3):Math.floor(i*255/h))];
  for(const b of[-2147483647,-65536,...Array.from({length:260},(_,i)=>i-2),65536,2147483647]){
   const v=cached(cache,b),q=reference(cache,b);assert.equal(v.q,q);assert.equal(v.cost,q===0?0:cache[q]+1);cases++;
  }
 }assert.equal(cases,42240);
});
test('host endpoint census pins inputs and preserves all PCM, memory and prior call counts',()=>{
 const r=report(),old=read('docs/benchmarks/esp8266-opus-bits-fourth-2026-09-15/summary.json');
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 assert.equal(r.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/profile_endpoint_cost.cjs')));
 assert.equal(r.observer_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/endpoint_cost_probe.inc.c')));
 assert.equal(r.rate_sha256_lf,sourceHash(path.join(component,'upstream/celt/rate.h')));
 for(const c of r.cases){
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
  assert.equal(c.counts.zero+c.counts.lower+c.counts.upper,c.counts.calls);assert.ok(c.counts.same<=c.counts.calls);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(c.reference,k));assert.deepEqual(c.reference[k],c.probe[k]);}
  assert.equal(c.seconds,c.probe.samples/48000);assert.equal(c.calls_per_audio_second,c.counts.calls/c.seconds);
  assert.equal(c.cached_percent,c.counts.calls?100*(c.counts.lower+c.counts.upper)/c.counts.calls:null);
  const previous=old.cases.find(x=>x.name===c.name);assert.equal(c.fixture_sha256,previous.fixture_sha256);assert.equal(c.counts.calls,previous.counts.calls);
 }
 const c=r.cases.find(c=>c.name==='stereo-192');assert.deepEqual(c.counts,{calls:1765,zero:117,lower:698,upper:950,same:3});
 assert.equal(r.cases.find(c=>c.name==='mono-12').counts.calls,0);assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
