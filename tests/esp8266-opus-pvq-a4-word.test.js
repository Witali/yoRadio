const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_a4_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_a4_word_proof.cjs');
const first=require('../tools/esp8266_opus_asm/pvq_byte_word_proof.cjs'),{sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
test('two a4 word probes preserve actual search, split branches, SAR and all live registers without RAM growth',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,3);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,25);
 assert.equal(p.patches[0].before_hex,'00'.repeat(25));
 assert.equal(s.helper.instructions,9);assert.equal(s.helper.live_bytes,25);assert.equal(s.helper.reference.records.length,4);
 assert.equal(s.numeric.search_cases,378304);assert.equal(s.numeric.upper_cases,79902);
 assert.equal(s.numeric.added_word_loads,458206);assert.equal(s.numeric.new_steps-s.numeric.old_steps,9*458206);
 assert.equal(Object.keys(s.numeric.upper_stops).length,2);assert.equal(s.liveness.length,4);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.table.index_bytes,210);assert.equal(p.table.bytes,392);
});
test('a4 helper rejects reachable padding, changing outside bytes and live caller clobbers',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bad={...old,disassembly:old.disassembly.replace('4024e1a6 <quant_partition+0x6aa>','4024de08 <quant_partition+0x30c>')};
 assert.notEqual(bad.disassembly,old.disassembly);assert.throws(()=>sem.findPatches(bad),/External entry/);
 for(const rn of[0,11]){
  const fn={...old,disassembly:old.disassembly.replace(/(4024db55:[^\n]*?)addi\.n\s+a4, a4, 12/,'$1addi.n a4, a'+rn+', 12')};
  assert.notEqual(fn.disassembly,old.disassembly);assert.throws(()=>first.deadReg(fn,0x4024db55,rn),new RegExp('Live a'+rn));
 }
 const outside={...now,disassembly:now.disassembly.replace(/(4024db55:[^\n]*?)addi\.n\s+a4, a4, 12/,'$1addi.n a4, a4, 13')};
 assert.notEqual(outside.disassembly,now.disassembly);assert.throws(()=>sem.prove(old,outside),/Outside/);
});
test('a4 helper detects wrong extraction, SAR restore, alignment and accumulator register',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [from,to]of[[/extui\s+a4, a4, 0, 8/,'extui a4, a4, 1, 8'],[/ssa8l\s+a4/,'ssa8l a10'],[/srli\s+a4, a4, 2/,'srli a4, a4, 1']]){
  const bad={...now,disassembly:now.disassembly.replace(from,to)};assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.helperSymbolic(old,bad));
 }
 // Alter the second helper only, leaving the first helper's identical WSR intact.
 const lines=now.disassembly.split('\n');let active=false;
 const changed=lines.map(l=>{if(l.includes('4024de08:'))active=true;if(l.includes('4024de25:'))active=false;return active?l.replace(/wsr\.sar\s+a11/,'wsr.sar a4'):l;}).join('\n');
 assert.notEqual(changed,now.disassembly);assert.throws(()=>sem.helperSymbolic(old,{...now,disassembly:changed}));
});
test('a4 host model has24 exact PCM/state/PLC/reset/OOM cases, compound120ms and510kbps',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-a4-word');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_a4_word.cjs')));
});
