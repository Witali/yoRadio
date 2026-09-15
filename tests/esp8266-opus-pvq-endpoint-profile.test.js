const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/profile_pvq_endpoint_word.cjs'),{root,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('endpoint observer preserves lower-zero guard and counts each original endpoint read',()=>{
 const input='static int y_endpoint_cost(\n'+f.endpointAnchor;const out=f.instrument(input,'OBSERVER');
 assert.ok(out.includes('lo==0?-1:y_endpoint_probe(m,cache+lo,0),upper=y_endpoint_probe(m,cache+hi,1)'));
 assert.throws(()=>f.instrument(input+input,'OBSERVER'));assert.throws(()=>f.instrument('','OBSERVER'));
});
test('endpoint observer rejects inconsistent phases and more lower than upper reads',()=>{
 assert.equal(f.validateCounts({lower:2,upper:3,phase:[[1,1,0,0],[1,0,1,1]]}),5);
 for(const c of[{lower:4,upper:3,phase:[[1,1,1,1],[1,1,1,0]]},{lower:2,upper:3,phase:[[1,1,0,0],[1,0,0,1]]},{lower:0,upper:0,phase:[[]]}])assert.throws(()=>f.validateCounts(c));
});
test('endpoint census preserves10 exact PCM/memory cases and independently matches first-search counts',()=>{
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
 const r=read('docs/benchmarks/esp8266-opus-pvq-endpoint-word-profile-2026-09-15/summary.json');
 const a4=read('docs/benchmarks/esp8266-opus-pvq-a4-word-profile-2026-09-15/summary.json');
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 for(const[field,file]of[['recipe_sha256_lf','profile_pvq_endpoint_word.cjs'],['observer_sha256_lf','pvq_endpoint_probe.inc.c'],['parent_recipe_sha256_lf','pvq_row_word.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 for(const c of r.cases){const other=a4.cases.find(x=>x.name===c.name);assert.ok(other);assert.equal(c.fixture_sha256,other.fixture_sha256);
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.loads_per_audio_second,f.validateCounts(c.counts)/c.seconds);assert.equal(c.counts.upper,other.counts.first);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);
 }
 assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
