const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/endpoint_cost.cjs'),sem=require('../tools/esp8266_opus_asm/endpoint_cost_proof.cjs');
const prior=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
const proof=()=>read('preflight.json');
function mutate(fn,from,to){assert.ok(fn.disassembly.includes(from));return {...fn,disassembly:fn.disassembly.replace(from,to)};}
test('endpoint-cost reuses either cached byte with exact branches, addresses, q/cost, ABI and no RAM growth',()=>{
 const pair=f.verifyPair(),p=pair.proof,s=p.semantic.search;
 assert.equal(p.patches.length,8);assert.equal(p.patches.reduce((n,v)=>n+v.bytes,0),20);
 assert.equal(s.numeric.cases,378304);assert.equal(s.numeric.nonzero,376322);assert.equal(s.numeric.zero,1982);
 assert.equal(s.numeric.removed_reads,s.numeric.nonzero);assert.equal(s.numeric.old_steps,s.numeric.new_steps);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(pair.manifests.control.post_link_bits_fourth_variant,'candidate');
});
test('endpoint-cost proof rejects bypassing endpoint loads and any later use of the two dead registers',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const bad=mutate(old,'4024e1ba <quant_partition+0x6be>','4024e23c <quant_partition+0x740>');
 assert.throws(()=>sem.findPatches(bad),/Bypassed endpoint values/);
 for(const reg of[10,11]){
  const badLive={...now,disassembly:now.disassembly.replace(/(4024e241:[^\n]*?)l32i\.n\s+a6, a12, 32/,'$1mov.n a6, a'+reg)};
  assert.notEqual(badLive.disassembly,now.disassembly);
  assert.throws(()=>prior.deadUntilDefinition(badLive,0x4024e241,reg),new RegExp('Live a'+reg));
 }
});
test('endpoint-cost interpreter detects lost upper cost, wrong selected cost and out-of-row reads',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [from,to]of[[/mov\.n\s+a10, a10/,'mov.n a10, a4'],[/mov\.n\s+a8, a11/,'mov.n a8, a10'],[/(4024e1ad:[^\n]*?)l8ui\s+a4, a4, 0/,'$1l8ui a4, a4, 255']]){
  const bad={...now,disassembly:now.disassembly.replace(from,to)};
  assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.numeric(old,bad));
  assert.throws(()=>sem.prove(old,bad));
 }
});
test('endpoint-cost host semantic implementation preserves24 PCM/state/PLC/reset/OOM cases through510kbps',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'endpoint-cost');
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
 assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,require('../tools/esp8266_opus_asm/export.cjs').sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/endpoint_cost.cjs')));
});
