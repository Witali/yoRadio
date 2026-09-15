const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_byte_word.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_byte_word_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n));
const proof=()=>read('preflight.json');
function mutate(fn,from,to){assert.ok(fn.disassembly.includes(from));return {...fn,disassembly:fn.disassembly.replace(from,to)};}
test('PVQ word helper preserves all standard search results, SAR, table bounds, ABI and RAM',()=>{
 const pair=f.verifyPair(),p=pair.proof,s=p.semantic.search;
 assert.equal(p.patches.length,6);assert.equal(p.patches[0].address,sem.helper);assert.equal(p.patches[0].bytes,57);
 assert.equal(s.helper.instructions,9);assert.equal(s.helper.live_bytes,25);assert.equal(s.helper.records.length,4);
 assert.equal(s.numeric.cases,378304);assert.equal(s.numeric.word_loads,1218362);
 assert.equal(s.numeric.new_steps-s.numeric.old_steps,9*s.numeric.word_loads);
 assert.equal(p.table.address,sem.tableBase);assert.equal(p.table.bytes,392);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(pair.manifests.control.post_link_endpoint_cost_variant,'candidate');
});
test('PVQ word helper rejects reachable storage and using caller return/scratch before definition',()=>{
 const p=proof(),old=p.functions.quant_partition;
 const bad=mutate(old,'4024e1a6 <quant_partition+0x6aa>','4024ddec <quant_partition+0x2f0>');
 assert.throws(()=>sem.findPatches(bad),/Helper storage is reachable/);
 for(const reg of[0,11]){
  const badLive={...old,disassembly:old.disassembly.replace(/(4024e1c6:[^\n]*?)blt\s+a10, a8,/,'$1blt a'+reg+', a8,')};
  assert.notEqual(badLive.disassembly,old.disassembly);
  assert.throws(()=>sem.deadReg(badLive,0x4024e1c6,reg),new RegExp('Live a'+reg));
 }
});
test('PVQ word helper detects wrong byte extraction, SAR restore and unaligned/out-of-table loads',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 for(const [from,to]of[[/extui\s+a10, a10, 0, 8/,'extui a10, a10, 1, 8'],[/wsr\.sar\s+a11/,'wsr.sar a10'],[/srli\s+a10, a10, 2/,'srli a10, a10, 1']]){
  const bad={...now,disassembly:now.disassembly.replace(from,to)};
  assert.notEqual(bad.disassembly,now.disassembly);assert.throws(()=>sem.helperSymbolic(bad));
  assert.throws(()=>sem.numeric(old,bad));
 }
});
test('PVQ word host model exercises extraction with24 exact PCM/state/PLC/reset/OOM cases through510kbps',()=>{
 const h=read('host.json');assert.equal(h.passed,true);assert.equal(h.kind,'pvq-byte-word');
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
 assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.some(c=>c.name==='320-48frames'));
 assert.equal(h.recipe_sha256_lf,require('../tools/esp8266_opus_asm/export.cjs').sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_byte_word.cjs')));
});
