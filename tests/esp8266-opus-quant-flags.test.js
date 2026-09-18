const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const sem=require('../tools/esp8266_opus_asm/quant_flags_proof.cjs'),f=require('../tools/esp8266_opus_asm/quant_flags.cjs');
const {parsed}=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const root=path.resolve(__dirname,'..'),evidence=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
const original=()=>f.read(path.join(root,'firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json')).actual_functions.quant_all_bands;
function at(fn,address,change){
 const copy=structuredClone(fn),line=copy.disassembly.split(/\r?\n/).find(s=>s.startsWith(address.toString(16)+':'));
 assert.ok(line);const altered=change(line);assert.notEqual(altered,line);copy.disassembly=copy.disassembly.replace(line,altered);return copy;
}
test('each of18 reached flag loads has a converged value, not an assumed initializer',()=>{
 const fn=original(),facts=sem.facts(fn),patches=sem.findPatches(fn);
 assert.equal(facts.load_values.length,18);assert.equal(patches.length,18);
 assert.equal(patches.reduce((sum,p)=>sum+p.bytes,0),37);
 assert.ok(patches.every(p=>p.slot===32?p.value===0:p.slot===36&&p.value===1));
 for(const options of[{encodeZero:false},{immutableContext:false},{immutableResynth:false},{privateFrame:false}])assert.throws(()=>sem.findPatches(fn,options));
});
test('new stack aliases, partial flag writes and changed initializer sources reject specialization',()=>{
 const fn=original();
 for(const[from,to]of[['addi\ta12, a1, 32','addi\ta12, a1, 100'],['s32i.n\ta13, a1, 32','s32i.n\ta12, a1, 32'],['s32i.n\ta8, a1, 36','s16i\ta8, a1, 36']]){
  const changed=structuredClone(fn);assert.ok(changed.disassembly.includes(from));changed.disassembly=changed.disassembly.replace(from,to);assert.throws(()=>sem.findPatches(changed));
 }
});
test('linked pointwise proof keeps all3370 instruction addresses and the384-byte frame',()=>{
 const p=evidence(),result=sem.prove(p.functions.quant_all_bands,p.actual_functions.quant_all_bands,p.patches);
 assert.deepEqual(result,p.semantic);assert.equal(result.instructions,3370);assert.equal(result.frame_bytes,384);
 assert.equal(result.static_ram_delta,0);assert.equal(result.stack_delta,0);assert.equal(result.dynamic_instruction_count_delta,0);
 assert.equal(p.app_bytes,903216);assert.equal(p.patches.length,18);
 const source=sem.sourceFor(sem.findPatches(p.functions.quant_all_bands));
 assert.equal((source.match(/\.text\.patch/g)||[]).length,18);assert.doesNotMatch(source,/\.space|\bcall0\s+a/);
});
test('wrong MOVI values or destinations, changed calls, writes and branches cannot pass',()=>{
 const p=evidence(),a=p.functions.quant_all_bands,b=p.actual_functions.quant_all_bands;
 for(const patch of p.patches){
  for(const transform of[line=>line.replace(/, [01]$/,', '+(1-patch.value)),line=>line.replace(patch.register+',','a0,')])
   assert.throws(()=>sem.prove(a,at(b,patch.address,transform),p.patches));
 }
 for(const row of parsed(b).filter(r=>['call0','s32i','bne'].includes(r.op)).slice(0,8)){
  assert.throws(()=>sem.prove(a,at(b,row.address,line=>line+' changed'),p.patches));
 }
 const removed=structuredClone(p.patches);removed.pop();assert.throws(()=>sem.prove(a,b,removed));
});
test('linked caller and source contracts remain checked for arbitrary valid decoder packets',()=>{
 const p=evidence(),contract=sem.contract({functions:p.functions},path.join(root,'.build',f.parent,'yoradio_esp8266_helix_native.elf'));
 assert.deepEqual(contract,p.contract);assert.equal(contract.caller.argument,'a2=0');assert.equal(contract.references.direct_calls.length,1);
 assert.equal(contract.references.indirect_calls.length,11);assert.equal(contract.source.context_bytes,60);
 assert.deepEqual(contract.references.address_references,[]);
});
test('host semantic mirror checks flags at use and reproduces24 PCM/state/sanitizer cases',()=>{
 const file=f.cModels().find(m=>m.source==='upstream/celt/bands.c').file,source=fs.readFileSync(file,'utf8');
 assert.match(source,/if \(value != expected\) abort\(\)/);assert.match(source,/return y_quant_flag\(ctx->encode, 0\)/);
 assert.match(source,/y_quant_flag\(ctx->resynth, 1\)/);
 const r=f.read(path.join(root,'.build/opus-bands-quant-flags/correctness.json'));
 assert.equal(r.passed,true);assert.equal(r.cases.length,24);assert.ok(r.cases.every(c=>c.pcm.exact));
 assert.ok(r.cases.some(c=>c.name==='stereo-510'));assert.ok(r.cases.some(c=>c.name==='320-48frames'));
});
