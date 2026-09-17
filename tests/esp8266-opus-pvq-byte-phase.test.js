const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_byte_phase.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_byte_phase_proof.cjs');
const read=n=>f.read(path.join(f.art('candidate'),n)),proof=()=>read('preflight.json');
function at(fn,pc,from,to){const out={...fn,disassembly:fn.disassembly.split('\n').map(l=>l.trimStart().startsWith(pc.toString(16)+':')?l.replace(from,to):l).join('\n')};assert.notEqual(out.disassembly,fn.disassembly);return out;}
test('phase leaf substitutes all six CALL0 sites with exact all-bit outputs and unchanged RAM',()=>{
 const p=f.verifyPair().proof,s=p.semantic;
 assert.equal(p.patches.length,7);assert.equal(p.patches.reduce((n,p)=>n+p.bytes,0),60);
 assert.equal(s.helper.addresses,392);assert.equal(s.helper.executed_per_phase,7);assert.equal(s.helper.old_executed,9);assert.equal(s.helper.live_bytes,37);
 assert.equal(s.helper.records.length,4);assert.equal(s.liveness.length,6);assert.ok(s.liveness.every(r=>r.register===11));
 assert.equal(s.storage.predecessor.dead,true);assert.equal(s.frame_bytes,112);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.app_bytes,903216);
 assert.equal(p.parent,'esp8266-opus-pvq-exp2-table32-candidate-v1');
});
test('phase proof rejects wrong extraction, phase branch, alignment, stack/SAR writes and a4 changes',()=>{
 const p=proof(),old=p.functions.quant_partition,now=p.actual_functions.quant_partition;
 const rows=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs').parsed(now);
 const ext=rows.find(r=>sem.helperInside(r.address)&&r.text==='extui a10, a10, 24, 8');
 const branch=rows.find(r=>sem.helperInside(r.address)&&r.op==='bbci');
 for(const [pc,from,to]of[
  [sem.helper,/a11, a10, 0, 2/,'a11, a10, 0, 1'],
  [sem.helper+3,/sub/,'add'],
  [ext.address,/24, 8/,'16, 8'],
  [branch.address,/a11, 1,/,'a11, 0,'],
  [sem.helper+6,/l32i.n/,'s32i.n'],
  [sem.helper+6,/l32i.n/,'wsr.sar'],
  [0x4024de0b,/ssa8l\s+a4/,'ssa8l a10'],
 ])assert.throws(()=>sem.prove(old,at(now,pc,from,to)));
 assert.throws(()=>sem.findPatches(at(old,sem.sites[0],/4024ddec/,'4024ddef')));
});
test('phase candidate authenticates dead storage and retains parent PCM evidence without relabeling it',()=>{
 const p=proof(),elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
 const off=require('../tools/esp8266_opus_asm/frozen_reloads.cjs').offsetAt(elf,sem.helper,sem.helperBytes);
 elf[off]^=1;assert.throws(()=>sem.storageBytesProof(elf),/storage changed/);
 const h=f.read(path.join(f.art('control'),'../esp8266-opus-pvq-exp2-table32-candidate-v1/host.json'));
 assert.equal(h.passed,true);assert.equal(h.kind,'pvq-exp2-table32');assert.equal(h.cases.length,24);
 assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));assert.equal(h.compound.length,3);
});
