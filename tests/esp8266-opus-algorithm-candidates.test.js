const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const model=require('../tools/esp8266_opus_asm/algorithm_candidates.cjs');
const n4=require('../tools/esp8266_opus_asm/analyze_n4_prefix.cjs');
const dir=path.join(root,'docs/benchmarks/esp8266-opus-algorithm-candidates-2026-09-19');
const read=name=>JSON.parse(fs.readFileSync(path.join(dir,name)));
const upstream=name=>fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt',name),'utf8').replace(/\r\n/g,'\n');
test('N4 lookup covers every index in its domain with exact rank and p',()=>{
 const pre=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-pvq-prefix-word-candidate-v1/preflight.json'))),row=pre.table.rows.find(r=>r.n===4);
 assert.deepEqual(n4.verify(row),read('n4-prefix/analysis.json').unit);
 assert.throws(()=>n4.lookup(63));assert.throws(()=>n4.lookup(65536));
 const bad=structuredClone(row);bad.values[10]++;assert.throws(()=>n4.verify(bad));
 const table=model.n4Table().entries;table[0]^=1;assert.notDeepEqual(n4.lookup(64,table),n4.lookup(64));
});
test('in-place model preserves a guarded fallback, raw mask order, and no scratch fast path',()=>{
 for(const kind of ['inplace-b1','inplace-all']) {
  const s=model.transformVq(upstream('vq.c'),kind),norm=model.functionText(s,'static void research_normalise16('),f=model.functionText(s,'unsigned alg_unquant(');
  assert.ok(!norm.includes('OPUS_RESTRICT'));assert.ok(norm.includes('MULT16_16(g, X[i])'));
  assert.ok(f.includes('K<=32767'));assert.ok(f.indexOf('return collapse_mask;')<f.indexOf('SAVE_STACK;'));
  assert.ok(f.includes('Ryy = decode_pulses(iy, N, K, dec);'));
  if(kind==='inplace-all')assert.ok(f.indexOf('research_mask16(X,N,B)')<f.indexOf('research_normalise16(X,N,Ryy,gain)'));
  else assert.ok(f.includes('&& B<=1'));
 }
});
test('all five semantic candidates pass 24 full-stream cases without larger arena peaks',()=>{
 const r=read('results.json');assert.equal(r.passed,true);assert.equal(r.variants.length,6);
 assert.equal(r.recipe_sha256,sourceHash(path.join(root,'tools/esp8266_opus_asm/check_algorithm_candidates.cjs')));
 assert.equal(r.model_sha256,sourceHash(path.join(root,'tools/esp8266_opus_asm/algorithm_candidates.cjs')));
 for(const v of r.variants.filter(v=>v.kind!=='observe')) {
  assert.equal(v.cases.length,24);
  for(const c of v.cases) {
   assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.candidate.reset_exact,true);
   if(c.name!=='mixed'){assert.equal(c.candidate.arena_guards_ok,true);assert.equal(c.candidate.oom_reinitialized_exact,true);}
   for(const p of ['scratch_byte_peak_bytes','scratch_word_peak_bytes'])assert.ok(c.candidate[p]<=c.reference[p]);
  }
  for(const name of ['stereo-510','stereo-320-20ms','320-48frames','mixed'])assert.ok(v.cases.some(c=>c.name===name));
 }
});
test('direct raw-vector, red-zone and zero-gain mask checks are retained',()=>{
 const d=read('direct/results.json');assert.equal(d.cases[0].vectors,84018);assert.equal(d.cases[0].guards,true);
 assert.equal(d.cases[1].normalisations,27200);assert.equal(d.cases[1].zero_gain_mask_preserved,true);
 assert.ok(d.cases.every(c=>c.exact));
});
test('observed peak is in synthesis, not the removed PVQ allocation',()=>{
 const r=read('results.json'),v=r.variants.find(v=>v.kind==='observe');assert.equal(v.cases.length,10);
 const c=v.cases.find(c=>c.name==='stereo-192');assert.equal(c.trace.max_partition_depth,5);
 assert.deepEqual(c.trace.word_peak_site,{count:960,element_bytes:4,pvq:null,synthesis:{n:960,lm:3}});
 const p=c.trace.partitions;assert.equal(p.reduce((s,x)=>s+x.calls,0),3026);
 assert.equal(p.filter(x=>x.n===2||x.n===4).reduce((s,x)=>s+x.leaves,0),485);
 assert.equal(p.filter(x=>x.n===2||x.n===4&&x.lm===-1).reduce((s,x)=>s+x.calls,0),8);
 assert.ok(p.some(x=>x.n===4&&x.calls>x.leaves),'N4 can still split; unconditional leaf is invalid');
 for(const v of r.variants.filter(v=>v.kind.startsWith('inplace'))) {
  const c=v.cases.find(c=>c.name==='stereo-192');assert.equal(c.candidate.scratch_word_peak_bytes,15600);assert.equal(c.candidate.scratch_byte_peak_bytes,5488);
 }
});
test('LX106 audit retains the short-leaf frame regression instead of promoting it',()=>{
 const r=read('lx106.json'),frame=(unit,role,name)=>Number(unit[role].stack.find(s=>s.split('\t')[0].endsWith(':'+name)).split('\t')[1]);
 const n=r.variants.find(v=>v.kind==='n4-prefix').units[0];assert.equal(frame(n,'control','decode_pulses'),48);assert.equal(frame(n,'candidate','decode_pulses'),48);
 assert.equal(n.candidate.sections['.rodata.research_n4_table'],1044);
 const l=r.variants.find(v=>v.kind==='short-leaf-cache').units[0];assert.equal(frame(l,'control','quant_partition'),160);assert.equal(frame(l,'candidate','quant_partition'),176);
 for(const v of r.variants)for(const u of v.units)for(const s of ['.data','.bss'])assert.equal(u.candidate.sections[s]||0,u.control.sections[s]||0);
});
test('saved search estimates are bounds on reads, not speed measurements',()=>{
 const a=read('n4-prefix/analysis.json'),c=a.cases.find(c=>c.name==='stereo-192');
 assert.equal(c.baseline_reads,24259);assert.equal(c.candidate_reads_min,21111);assert.equal(c.candidate_reads_max,21227);
 assert.match(a.scope,/Not CPU/);assert.equal(a.unit.flash_data_bytes,1044);
});
test('all archived evidence matches its inventory',()=>{
 for(const f of read('inventory.json').files){const bytes=fs.readFileSync(path.join(dir,f.name));assert.equal(bytes.length,f.bytes);assert.equal(hash(bytes),f.sha256,f.name);}
});
