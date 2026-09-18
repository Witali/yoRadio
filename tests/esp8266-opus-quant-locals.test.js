const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const sem=require('../tools/esp8266_opus_asm/quant_locals_proof.cjs'),f=require('../tools/esp8266_opus_asm/quant_locals.cjs');
const flags=require('../tools/esp8266_opus_asm/quant_flags_proof.cjs'),{parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const root=path.resolve(__dirname,'..'),evidence=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
const original=()=>f.read(path.join(root,'firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json')).actual_functions.quant_all_bands;
function at(fn,address,change){
 const copy=structuredClone(fn),line=copy.disassembly.split(/\r?\n/).find(s=>s.startsWith(address.toString(16)+':'));
 assert.ok(line);const changed=change(line);assert.notEqual(changed,line);copy.disassembly=copy.disassembly.replace(line,changed);return copy;
}
test('23 local constants come from41 converged facts; none overlaps the18 ctx patches',()=>{
 const fn=original(),observed=sem.facts(fn),patches=sem.findPatches(fn);
 assert.equal(observed.load_values.length,41);assert.equal(patches.length,23);assert.ok(patches.every(p=>p.bytes===3));
 const ctx=flags.findPatches(fn);assert.ok(patches.every(p=>ctx.every(c=>c.address!==p.address)));
 for(const options of[{encodeZero:false},{immutableContext:false},{immutableResynth:false},{privateFrame:false}])assert.throws(()=>sem.findPatches(fn,options));
});
test('reused local slot132 is zero and one at different PCs, never a global constant',()=>{
 const patches=sem.findPatches(original()),get=pc=>patches.find(p=>p.address===pc);
 assert.equal(get(0x402521c5).slot,132);assert.equal(get(0x402521c5).value,0);
 assert.equal(get(0x40252a20).slot,132);assert.equal(get(0x40252a20).value,1);
 // Other reachable reads of SP192 are dynamic and must remain original L32I.
 const selected=new Set(patches.map(p=>p.address));
 for(const pc of[0x40250ba9,0x40252acf])assert.ok(!selected.has(pc));
});
test('partial local writes, changed initialization or stack escape invalidate the facts',()=>{
 const fn=original();
 for(const [pc,from,to]of[[0x402521ad,'s32i','s8i'],[0x40250a31,'a2, a1, 192','a0, a1, 192']])
  assert.throws(()=>sem.findPatches(at(fn,pc,line=>line.replace(from,to))));
 const changed=structuredClone(fn);changed.disassembly=changed.disassembly.replace('addi\ta12, a1, 32','addi\ta12, a1, 100');
 assert.notEqual(changed.disassembly,fn.disassembly);assert.throws(()=>sem.findPatches(changed));
});
test('linked proof preserves every PC/width and ctx read; wrong immediates/destinations fail',()=>{
 const p=evidence(),a=p.functions.quant_all_bands,b=p.actual_functions.quant_all_bands;
 assert.deepEqual(sem.prove(a,b,p.patches),p.semantic);assert.equal(p.semantic.patched_bytes,69);
 assert.equal(p.semantic.instructions,3370);assert.equal(p.semantic.frame_bytes,384);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 for(const patch of p.patches){
  for(const transform of[line=>line.replace(/, [01]$/,', '+(1-patch.value)),line=>line.replace(patch.register+',','a0,')])
   assert.throws(()=>sem.prove(a,at(b,patch.address,transform),p.patches));
 }
 for(const row of parsed(b).filter(r=>['call0','s32i','bne'].includes(r.op)).slice(0,8))
  assert.throws(()=>sem.prove(a,at(b,row.address,line=>line+' changed'),p.patches));
});
test('native caller/source/alias contract is rechecked on accepted linked ELF',()=>{
 const p=evidence(),c=sem.contract({functions:p.functions},path.join(root,'.build',f.parent,'yoradio_esp8266_helix_native.elf'));
 assert.deepEqual(c,p.contract);assert.equal(c.caller.argument,'a2=0');assert.equal(c.references.direct_calls.length,1);
 assert.equal(c.references.indirect_calls.length,11);assert.deepEqual(c.references.address_references,[]);
});
test('host origin checks pass24 exact PCM/state/ASan/UBSan scenarios including high bitrates',()=>{
 const source=fs.readFileSync(f.cModels().find(m=>m.source==='upstream/celt/bands.c').file,'utf8');
 assert.match(source,/if \(value != expected\) abort\(\)/);assert.match(source,/lowband_offset = y_quant_flag\(0, 0\)/);
 assert.match(source,/int resynth = y_quant_flag\(!encode \|\| theta_rdo, 1\)/);
 // Read the committed evidence, not an optional disposable host-build cache.
 const r=f.read(path.join(f.art('candidate'),'correctness.json'));
 assert.equal(r.passed,true);assert.equal(r.cases.length,24);assert.ok(r.cases.every(c=>c.pcm.exact));
 assert.ok(r.cases.some(c=>c.name==='stereo-510'));assert.ok(r.cases.some(c=>c.name==='320-48frames'));
});
