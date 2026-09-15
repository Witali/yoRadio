const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {shortcut,exhaustive}=require('../tools/esp8266_opus_asm/profile_bits_fourth.cjs');
const {reference}=require('../tools/esp8266_opus_asm/pulse_inverse.cjs');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const report=()=>read('docs/benchmarks/esp8266-opus-bits-fourth-2026-09-15/summary.json');
test('fourth-step shortcut preserves selection over all standard tables and 378304 budgets',()=>{
 const r=exhaustive();assert.equal(r.cases,378304);assert.equal(r.skippable,295452);
 assert.deepEqual(r.gaps,{0:225977,1:69475,2:82159,3:693});assert.deepEqual(r,report().exhaustive);
});
test('fourth-step shortcut preserves endpoints, ties, duplicate costs and signed extremes',()=>{
 let cases=0;for(let h=1;h<=40;h++)for(const mode of[0,1,2,3]){
  const cache=[h,...Array.from({length:h},(_,i)=>mode===0?0:mode===1?255:mode===2?Math.floor(i/3):Math.floor(i*255/h))];
  for(const b of[-2147483647,-65536,...Array.from({length:260},(_,i)=>i-2),65536,2147483647]){assert.equal(shortcut(cache,b).q,reference(cache,b));cases++;}
 }assert.equal(cases,42240);
});
test('fourth-step host census preserves PCM and memory and reproduces prior fifth-step counts',()=>{
 const r=report(),old=read('docs/benchmarks/esp8266-opus-bits-fifth-2026-09-15/summary.json');
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 assert.equal(r.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/profile_bits_fourth.cjs')));
 assert.equal(r.observer_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/bits_fourth_probe.inc.c')));
 assert.equal(r.rate_sha256_lf,sourceHash(path.join(component,'upstream/celt/rate.h')));
 for(const c of r.cases){
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
  for(const stage of[4,5]){const gaps=c.counts['gaps_after_'+stage];assert.equal(gaps.length,256);assert.equal(gaps.reduce((a,b)=>a+b,0),c.counts.calls);assert.equal(c.counts[stage===4?'fourth':'fifth'],gaps[0]+gaps[1]);}
  assert.ok(c.counts.fourth<=c.counts.fifth);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(c.reference,k));assert.deepEqual(c.reference[k],c.probe[k]);}
  assert.equal(c.seconds,c.probe.samples/48000);assert.equal(c.calls_per_audio_second,c.counts.calls/c.seconds);
  assert.equal(c.fourth_percent,c.counts.calls?100*c.counts.fourth/c.counts.calls:null);
  const prior=old.cases.find(x=>x.name===c.name);assert.equal(c.fixture_sha256,prior.fixture_sha256);
  assert.equal(c.counts.calls,prior.counts.calls);assert.equal(c.counts.fifth,prior.counts.skippable);
 }
 const high=r.cases.find(c=>c.name==='stereo-192');assert.equal(high.counts.calls,1765);assert.equal(high.counts.fourth,765);
 assert.equal(r.cases.find(c=>c.name==='mono-12').counts.calls,0);assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
