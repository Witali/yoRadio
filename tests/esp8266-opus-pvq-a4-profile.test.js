const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/profile_pvq_a4_word.cjs'),{root,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('a4 observer selects only first probe and short-circuit pre-split upper read',()=>{
 const input='static int y_endpoint_cost(\ni==0?cache[mid]:y_pvq_word8(m,cache+mid)\nLM != -1 && b > cache[cache[0]]+12 && N>2';
 const x=f.instrument(input,'OBSERVER');assert.match(x,/i==0\?y_a4_probe\(m,cache\+mid,0\):y_pvq_word8/);
 assert.match(x,/LM != -1 && b > y_a4_probe\(m,cache\+cache\[0\],1\)\+12 && N>2/);
 assert.throws(()=>f.instrument(input+input,'OBSERVER'));assert.throws(()=>f.instrument('', 'OBSERVER'));
});
test('a4 observer validates phase census and fails on missing or invalid counts',()=>{
 assert.equal(f.validateCounts({first:3,upper:2,phase:[1,2,1,1]}),5);
 for(const c of[{first:3,upper:2,phase:[1,2,1,0]},{first:3,upper:2,phase:[1,2,2]},{first:3,upper:-1,phase:[1,1,0,0]}])assert.throws(()=>f.validateCounts(c));
});
test('a4 host census preserves PCM and memory through510kbps with current hashed sources',()=>{
 const r=JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks/esp8266-opus-pvq-a4-word-profile-2026-09-15/summary.json')));
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 assert.equal(r.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/profile_pvq_a4_word.cjs')));
 assert.equal(r.observer_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/pvq_a4_probe.inc.c')));
 assert.equal(r.parent_recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/pvq_byte_word.cjs')));
 for(const c of r.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.loads_per_audio_second,f.validateCounts(c.counts)/c.seconds);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);}
 assert.ok(r.cases.some(c=>c.name==='stereo-510'));assert.equal(r.cases.find(c=>c.name==='stereo-192').counts.first,1765);
});
