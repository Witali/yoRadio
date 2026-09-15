const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_row_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_row_word_proof.cjs');
const first=require('../tools/esp8266_opus_asm/pvq_byte_word_proof.cjs'),{sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
test('row word preserves source, arbitrary SAR, complete table and actual split/search behavior without RAM growth',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,2);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,27);
 assert.equal(s.helper.instructions,9);assert.equal(s.helper.live_bytes,25);assert.equal(s.helper.records.length,4);
 assert.ok(s.helper.records.every(r=>r.source_preserved));assert.equal(s.storage.instructions,11);assert.equal(s.storage.incoming.length,1);
 assert.equal(s.numeric.byte_cases,392*64);assert.equal(s.numeric.prefix_cases,160080);
 assert.equal(s.numeric.added_word_loads,185168);assert.equal(s.numeric.new_steps-s.numeric.old_steps,9*185168);
 assert.ok(Object.keys(s.numeric.prefix_stops).length>=2);assert.equal(s.liveness.length,2);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.table.index_bytes,210);assert.equal(p.table.bytes,392);
});
test('row helper rejects changed incoming edges, outside instructions and live caller clobbers',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bad={...old,disassembly:old.disassembly.replace('4024e1a6 <quant_partition+0x6aa>','4024e3e8 <quant_partition+0x8ec>')};
 assert.notEqual(bad.disassembly,old.disassembly);assert.throws(()=>sem.findPatches(bad),/Changed incoming edge|reachable/i);
 for(const rn of[0,11]){
  const fn={...old,disassembly:old.disassembly.replace(/(4024db4a:[^\n]*?)bnei\s+a9, -1/,'$1bnei a'+rn+', -1')};
  assert.notEqual(fn.disassembly,old.disassembly);assert.throws(()=>first.deadReg(fn,0x4024db4a,rn),new RegExp('Live a'+rn));
 }
 const outside={...now,disassembly:now.disassembly.replace(/(4024db55:[^\n]*?)addi\.n\s+a4, a4, 12/,'$1addi.n a4, a4, 13')};
 assert.notEqual(outside.disassembly,now.disassembly);assert.throws(()=>sem.prove(old,outside),/Outside/);
});
test('row helper rejects wrong source, destination, shift, SAR restore and table word bounds',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const mutate=(from,to)=>{let active=false;return {...now,disassembly:now.disassembly.split('\n').map(l=>{
  if(l.includes('4024e3e8:'))active=true;if(l.includes('4024e403:'))active=false;return active?l.replace(from,to):l;
 }).join('\n')};};
 for(const [from,to]of[[/extui\s+a6, a6, 0, 8/,'extui a6, a6, 1, 8'],[/ssa8l\s+a2/,'ssa8l a6'],[/srli\s+a6, a2, 2/,'srli a2, a2, 2'],[/wsr\.sar\s+a11/,'wsr.sar a6']]){
  const bad=mutate(from,to);assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.helperSymbolic(bad));
 }
 const r=Array(16).fill(0);r[2]=sem.tableBase+sem.tableBytes;
 assert.throws(()=>sem.execute(now,r,[1],r[2],0,{stops:[sem.sites[0]+3]}),/Word outside/);
});
test('row host model preserves24 PCM/state/PLC/reset/OOM cases through510kbps and compound120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-row-word');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_row_word.cjs')));
});
