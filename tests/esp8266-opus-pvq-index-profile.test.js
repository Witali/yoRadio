const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/profile_pvq_index_word.cjs'),{root,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('index observer replaces exactly the signed partition index read',()=>{
 const input='static unsigned quant_partition(\n'+f.anchor,out=f.instrument(input,'OBSERVER');
 assert.ok(out.includes('cache = m->cache.bits + y_index_probe(m,(LM+1)*m->nbEBands+i);'));
 assert.throws(()=>f.instrument(input+input,'OBSERVER'));assert.throws(()=>f.instrument('','OBSERVER'));
});
test('index observer rejects invalid positions, totals and alignment phases',()=>{
 const c={total:2,negative:1,last:1,phase:[1,0,1,0],positions:Array(105).fill(0)};c.positions[1]=c.positions[104]=1;
 assert.equal(f.validateCounts(c),2);
 for(const change of[{total:3},{negative:3},{last:0},{positions:[]},{phase:[0,1,1,0]}])assert.throws(()=>f.validateCounts({...c,...change}));
});
test('index census preserves10 exact PCM/memory cases and independently matches partition row counts',()=>{
 const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
 const r=read('docs/benchmarks/esp8266-opus-pvq-index-word-profile-2026-09-15/summary.json');
 const rows=read('docs/benchmarks/esp8266-opus-pvq-row-word-profile-2026-09-15/summary.json');
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);
 for(const[field,file]of[['recipe_sha256_lf','profile_pvq_index_word.cjs'],['observer_sha256_lf','pvq_index_probe.inc.c'],['parent_recipe_sha256_lf','pvq_endpoint_word.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 for(const c of r.cases){const other=rows.cases.find(x=>x.name===c.name);assert.ok(other);assert.equal(c.fixture_sha256,other.fixture_sha256);
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.loads_per_audio_second,f.validateCounts(c.counts)/c.seconds);assert.equal(c.loads_per_audio_second,other.loads_per_audio_second);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);
 }assert.ok(r.cases.some(c=>c.name==='stereo-510'));
});
