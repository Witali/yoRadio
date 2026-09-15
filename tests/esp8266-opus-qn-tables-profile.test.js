const test=require('node:test'),assert=require('node:assert/strict');
const f=require('../tools/esp8266_opus_asm/profile_qn_tables.cjs');
const fs=require('node:fs'),path=require('node:path'),{root,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
test('QN observer changes only unique original-value table reads and counters',()=>{
 const text=Object.values(f.anchors).join('\n'),out=f.instrument(text,'OBSERVER');
 assert.ok(out.includes('y_qn_exp2(exp2_table8,qb&0x7,stereo)'));assert.ok(out.includes('y_qn_logn(m,i,stereo)'));
 assert.ok(out.includes(f.anchors.search));assert.ok(out.includes(f.anchors.partition));
 assert.throws(()=>f.instrument(text+text,'OBSERVER'));assert.throws(()=>f.instrument('','OBSERVER'));
});
test('QN census validates table totals, actual splits and unsplittable N=2',()=>{
 const c={logn:[3,2],exp2:[2,1],logn_index:[5,...Array(20).fill(0)],exp2_index:[3,...Array(7).fill(0)],partition:10,partition_n2:2,search:7,search_n2:2};
 assert.equal(f.validateCounts(c),8);
 for(const patch of [{partition:11},{partition_n2:3},{exp2:[4,1]},{logn:[-3,2]},{logn_index:[]},{search_n2:8}])assert.throws(()=>f.validateCounts({...c,...patch}));
});
test('QN census retains exact PCM and memory on ten files and authenticates linked tables',()=>{
 const r=JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks/esp8266-opus-qn-tables-profile-2026-09-15/summary.json')));
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);assert.deepEqual(r.linked_inventory,f.linkedInventory());
 for(const [field,file]of [['recipe_sha256_lf','profile_qn_tables.cjs'],['observer_sha256_lf','qn_tables_probe.inc.c'],['parent_recipe_sha256_lf','pvq_index_half.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 for(const c of r.cases){
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.pcm.snr_db,'Infinity');
  assert.equal(c.table_reads_per_audio_second,f.validateCounts(c.counts)/c.seconds);
  for(const k of ['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);
 }
 const c=r.cases.find(c=>c.name==='stereo-192');assert.deepEqual(c.counts.logn,[1261,231]);assert.deepEqual(c.counts.exp2,[1261,231]);assert.equal(c.counts.search_n2,2);
 assert.equal(r.cases.find(c=>c.name==='stereo-320-5ms').counts.search_n2,890);
});
