const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {boundary,exhaustive}=require('../tools/esp8266_opus_asm/profile_pvq_boundaries.cjs');
const {reference}=require('../tools/esp8266_opus_asm/pulse_inverse.cjs');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const report=()=>read('docs/benchmarks/esp8266-opus-pvq-boundaries-2026-09-15/summary.json');
test('PVQ boundary guards preserve extreme indices for every standard table budget',()=>{
 const r=exhaustive();assert.equal(r.cases,378304);assert.equal(r.zero,1982);assert.equal(r.upper,371773);
 assert.equal(r.after_three,229512);assert.deepEqual(r,report().exhaustive);
});
test('PVQ boundary guards respect duplicate-cost ties and signed extremes without doubled-budget overflow',()=>{
 let cases=0;for(let h=1;h<=40;h++)for(const mode of[0,1,2,3]){
  const cache=[h,...Array.from({length:h},(_,i)=>mode===0?0:mode===1?255:mode===2?Math.floor(i/3):Math.floor(i*255/h))];
  for(const b of[-2147483647,-65536,...Array.from({length:260},(_,i)=>i-2),65536,2147483647]){
   const v=boundary(cache,b),q=reference(cache,b);if(v.zero)assert.equal(q,0);if(v.upper)assert.equal(q,h);
   assert.equal(v.zero&&v.upper,false);cases++;
  }
 }assert.equal(cases,42240);
 // Equal-to-maximum is not a safe largest-index guard for duplicate costs.
 const c=[40,...Array(40).fill(255)];assert.equal(boundary(c,256).upper,false);assert.notEqual(reference(c,256),40);
});
test('PVQ boundary census pins all inputs, exact PCM and RAM, and separates actual audio frequency',()=>{
 const r=report(),old=read('docs/benchmarks/esp8266-opus-endpoint-cost-2026-09-15/summary.json');
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 assert.equal(r.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/profile_pvq_boundaries.cjs')));
 assert.equal(r.observer_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/pvq_boundaries_probe.inc.c')));
 assert.equal(r.rate_sha256_lf,sourceHash(path.join(component,'upstream/celt/rate.h')));
 for(const c of r.cases){
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
  assert.ok(c.counts.zero_fast+c.counts.upper_fast<=c.counts.calls);assert.ok(c.counts.upper_loaded<=c.counts.upper_fast);
  assert.ok(c.counts.after_three<=c.counts.calls);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(c.reference,k));assert.deepEqual(c.reference[k],c.probe[k]);}
  assert.equal(c.seconds,c.probe.samples/48000);assert.equal(c.calls_per_audio_second,c.counts.calls/c.seconds);
  for(const k of['zero_fast','upper_fast','upper_loaded','after_three'])assert.equal(c.percent[k],c.counts.calls?100*c.counts[k]/c.counts.calls:null);
  const previous=old.cases.find(x=>x.name===c.name);assert.equal(c.fixture_sha256,previous.fixture_sha256);assert.equal(c.counts.calls,previous.counts.calls);
 }
 const c=r.cases.find(c=>c.name==='stereo-192');assert.deepEqual(c.counts,{calls:1765,zero_fast:117,upper_fast:48,upper_loaded:37,after_three:107});
 assert.equal(r.cases.find(c=>c.name==='mono-12').counts.calls,0);assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
