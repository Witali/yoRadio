const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/profile_pvq_qn.cjs'),{root,sourceHash,hash}=require('../tools/esp8266_opus_asm/export.cjs');

test('qn observer is exact-anchor and preserves the original returned value',()=>{
 const input='static int compute_qn(\n'+f.anchor,out=f.instrument(input,'OBSERVER');
 assert.ok(out.includes('y_qn_observe(qb,qn,stereo);\n'+f.anchor));
 assert.throws(()=>f.instrument('', 'OBSERVER'));assert.throws(()=>f.instrument(input+input,'OBSERVER'));
});
test('qn census separates unchanged low branch and stereo from target table reads',()=>{
 const empty=()=>({total:0,low:0,qb:Array(61).fill(0)}),c={nonstereo:empty(),stereo:empty()};
 c.nonstereo.total=3;c.nonstereo.low=1;c.nonstereo.qb[0]=c.nonstereo.qb[60]=1;
 c.stereo.total=2;c.stereo.qb[3]=2;assert.equal(f.validateCounts(c),2);
 for(const mutate of [x=>x.nonstereo.qb.pop(),x=>x.nonstereo.total++,x=>x.stereo.low=-1,x=>x.stereo.qb[0]=NaN]){
  const bad=structuredClone(c);mutate(bad);assert.throws(()=>f.validateCounts(bad));
 }
 const table=f.qnTable();assert.equal(table.length,61);assert.equal(table[0],2);assert.equal(table[60],256);
 const exp2=[16384,17866,19483,21247,23170,25267,27554,30048];
 for(let qb=4;qb<=64;qb++)assert.equal(table[qb-4],2*Math.floor((Math.floor(exp2[qb%8]/2**(14-Math.floor(qb/8)))+1)/2));
});
test('saved qn census retains ten exact PCM/state/memory cases through510kbps',()=>{
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-qn-profile-2026-09-17');
 const r=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));
 assert.equal(r.passed,true);assert.equal(r.cases.length,10);assert.equal(new Set(r.cases.map(c=>c.name)).size,10);
 for(const[field,file]of [['recipe_sha256_lf','profile_pvq_qn.cjs'],['observer_sha256_lf','pvq_qn_probe.inc.c'],['parent_recipe_sha256_lf','pvq_exp2_table32.cjs']])assert.equal(r[field],sourceHash(path.join(root,'tools/esp8266_opus_asm',file)));
 assert.deepEqual(r.table_qb4_to64,f.qnTable());assert.equal(r.table_word_bytes,244);
 const model=zlib.gunzipSync(fs.readFileSync(path.join(dir,'bands.model.c.gz'))).toString('utf8');
 assert.equal(r.generated_model_sha256_lf,hash(model.replace(/\r\n/g,'\n')));
 assert.ok(r.flags.includes('-fsanitize=address,undefined'));
 for(const c of r.cases){
  assert.deepEqual(c.counts,JSON.parse(fs.readFileSync(path.join(dir,c.name+'.counts.json'))));
  assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
  assert.equal(c.eligible_per_audio_second,f.validateCounts(c.counts)/c.seconds);
  for(const k of ['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok'])assert.deepEqual(c.reference[k],c.probe[k]);
 }assert.ok(r.cases.some(c=>c.name==='stereo-510'));
 const target=r.cases.find(c=>c.name==='stereo-192');
 assert.equal(target.counts.nonstereo.total,1261);assert.equal(target.seconds,0.24);
 assert.ok(target.counts.nonstereo.qb[60]>0); // qb=64 remains supported, not capped at observed lower values.
});
