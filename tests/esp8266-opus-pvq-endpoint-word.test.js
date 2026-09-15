const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_endpoint_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_endpoint_word_proof.cjs');
const first=require('../tools/esp8266_opus_asm/pvq_byte_word_proof.cjs'),{sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
test('endpoint word accesses preserve complete linked search, cost, SAR and all live registers without RAM growth',()=>{
 const p=f.verifyPair().proof,s=p.semantic.search;
 assert.equal(p.patches.length,4);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,48);
 assert.equal(p.patches[0].after_hex.slice(52),'00'.repeat(22));
 assert.equal(s.helper.instructions,9);assert.equal(s.helper.live_bytes,26);assert.equal(s.helper.records.length,4);assert.equal(s.helper.continuation,sem.lowerContinue);
 assert.equal(s.storage.instructions,19);assert.equal(s.storage.incoming.length,1);assert.equal(s.upper_helper.live_bytes,25);
 assert.equal(s.outside_view.omitted_proven_dead.length,120);
 assert.equal(s.numeric.byte_cases,50176);assert.equal(s.numeric.search_cases,378304);assert.equal(s.numeric.upper_reads,403392);
 assert.equal(s.numeric.lower_reads,400917);assert.equal(s.numeric.added_word_loads,804309);
 assert.equal(s.numeric.added_word_loads,s.numeric.upper_reads+s.numeric.lower_reads);
 assert.equal(s.numeric.new_steps-s.numeric.old_steps,9*s.numeric.added_word_loads);assert.equal(Object.keys(s.numeric.stops).length,2);
 assert.equal(s.liveness.length,4);assert.equal(Object.keys(s.interrupt_context.sha256_lf).length,4);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);assert.equal(p.table.bytes,392);
});
test('endpoint proof rejects bypassed upper setup, changed incoming storage and live a0',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bypass={...old,disassembly:old.disassembly.replace('4024e21d <quant_partition+0x721>','4024e21f <quant_partition+0x723>')};
 assert.notEqual(bypass.disassembly,old.disassembly);assert.throws(()=>sem.findPatches(bypass),/Bypassed upper address setup/);
 const enter={...old,disassembly:old.disassembly.replace('4024e1a6 <quant_partition+0x6aa>','4024e403 <quant_partition+0x907>')};
 assert.notEqual(enter.disassembly,old.disassembly);assert.throws(()=>sem.findPatches(enter),/Changed incoming edge|reachable/i);
 const live={...old,disassembly:old.disassembly.replace(/(4024e22d:[^\n]*?)mov\.n\s+a10, a10/,'$1mov.n a10, a0')};
 assert.notEqual(live.disassembly,old.disassembly);assert.throws(()=>first.deadReg(live,sem.lowerContinue,0),/Live a0/);
 const outside={...now,disassembly:now.disassembly.replace(/(4024db55:[^\n]*?)addi\.n\s+a4, a4, 12/,'$1addi.n a4, a4, 13')};
 assert.throws(()=>sem.prove(old,outside),/Outside/);
 const missing={...now,disassembly:now.disassembly.split('\n').filter(l=>!l.includes('4024e222:')).join('\n')};
 assert.throws(()=>sem.outsideViewProof(old,missing),/Outside live instruction omitted/);
});
test('lower fixed-return fragment rejects wrong SAR, extraction and continuation or out-of-table word',()=>{
 const p=proof(),now=p.actual_functions.quant_partition;
 const mutate=(from,to)=>{let active=false;return {...now,disassembly:now.disassembly.split('\n').map(l=>{
  if(l.includes('4024e403:'))active=true;if(l.includes('4024e434:'))active=false;return active?l.replace(from,to):l;
 }).join('\n')};};
 for(const[from,to]of[[/rsr\.sar\s+a0/,'rsr.sar a10'],[/ssa8l\s+a11/,'ssa8l a10'],[/extui\s+a11, a11, 0, 8/,'extui a11, a11, 1, 8'],[/wsr\.sar\s+a0/,'wsr.sar a11'],[/4024e22d </,'4024e22f <']]){
  const bad=mutate(from,to);assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.helperSymbolic(bad));
 }
 const r=Array(16).fill(0);r[11]=sem.tableBase+sem.tableBytes;
 assert.throws(()=>sem.execute(now,r,[1],r[11],0,{start:sem.lowerSite,stops:[sem.lowerContinue]}),/Word outside/);
});
test('endpoint host model preserves24 exact PCM/state/PLC/reset/OOM cases through510kbps and120ms',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-endpoint-word');assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_endpoint_word.cjs')));
});
