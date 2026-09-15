const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/profile_pvq_adjustment.cjs'),{root,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('adjustment observer changes only the decrement-loop cost calculation',()=>{
 const input='static unsigned quant_partition(\n'+f.anchor,out=f.instrument(input,'OBSERVER');
 assert.ok(out.includes('curr_bits = y_adjust_probe(m,i,LM,q);'));assert.throws(()=>f.instrument(input+input,'OBSERVER'));assert.throws(()=>f.instrument('','OBSERVER'));
});
test('adjustment census distinguishes q=0 calls from actual flash byte reads',()=>{
 const c={calls:3,loads:2,zero:1,phase:[1,0,1,0]};assert.equal(f.validateCounts(c),2);
 for(const change of[{calls:2},{zero:0},{loads:-1},{phase:[]},{phase:[0,0,0,0]}])assert.throws(()=>f.validateCounts({...c,...change}));
});
test('adjustment census preserves exact PCM and memory through510kbps; zero counts are not unreachable proofs',()=>{
 const r=JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks/esp8266-opus-pvq-adjustment-profile-2026-09-15/summary.json')));
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 for(const[field,file]of[['recipe_sha256_lf','profile_pvq_adjustment.cjs'],['observer_sha256_lf','pvq_adjust_probe.inc.c'],['parent_recipe_sha256_lf','pvq_index_half.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 for(const c of r.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.loads_per_audio_second,f.validateCounts(c.counts)/c.seconds);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);}
 assert.equal(r.cases.find(c=>c.name==='stereo-192').counts.loads,10);assert.equal(r.cases.find(c=>c.name==='mono-24').counts.zero,4);assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
