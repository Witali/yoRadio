const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const sem=require('../tools/esp8266_opus_asm/allocation_decode_proof.cjs'),f=require('../tools/esp8266_opus_asm/allocation_decode.cjs');
const audit=require('../tools/esp8266_opus_asm/audit_allocation_decode.cjs');
const old=require('../docs/results/esp8266-opus-allocation-decode-audit-20260918.json').linked.functions;
const root=path.resolve(__dirname,'..');
function mutation(fn,from,to){const x=structuredClone(fn);x.disassembly=x.disassembly.replace(from,to);assert.notEqual(x.disassembly,fn.disassembly);return x;}

test('all CFG paths produce disjoint scalar outputs and three bounded scratch arrays',()=>{
 const r=sem.callerPointers(old.celt_decode_with_ec_dred);
 assert.deepEqual(r.scalar_outputs,{intensity:236,dual_stereo:232,balance:180});
 assert.deepEqual(r.local_base_definitions,[0x40244678]);assert.equal(r.scratch_arrays.length,3);
});
test('changed local base, scalar offset, scratch origin or partial slot write is rejected',()=>{
 for(const[from,to]of[
  ['addi\ta8, a1, 80','addi\ta8, a1, 0'],
  ['movi\ta2, 156','movi\ta2, 4']]){
  const changed=mutation(old.celt_decode_with_ec_dred,from,to);
  assert.throws(()=>sem.callerPointers(changed));
 }
 const partial=structuredClone(old.celt_decode_with_ec_dred);
 // Change the relevant latest definition, not an earlier reused stack slot.
 partial.disassembly=partial.disassembly.replace(/(40244bd7:[^\n]*?)s32i/,'$1s16i');
 assert.notEqual(partial.disassembly,old.celt_decode_with_ec_dred.disassembly);
 assert.throws(()=>sem.callerPointers(partial));
 const changed=structuredClone(old.celt_decode_with_ec_dred);
 changed.disassembly=changed.disassembly.replace(/(40244bd1:[^\n]*)402428ec/,'$1402428d8');
 assert.notEqual(changed.disassembly,old.celt_decode_with_ec_dred.disassembly);
 assert.throws(()=>sem.callerPointers(changed));
});
test('specialization is decoder-only and source comments retain every removed instruction',()=>{
 const fn=old.clt_compute_allocation,c=sem.compile(fn),s=sem.selection(fn);
 assert.equal(c.removed_dead,67);assert.equal(c.removed_checks,3);assert.equal(c.kept_instructions,930);
 assert.equal(audit.analyze(fn,{encodeZero:false}).removed_instructions,0);
 for(const r of s.rows.filter(r=>s.dead.has(r.address)))assert.ok(c.text.includes(r.text));
 assert.match(c.text,/original192-byte frame/);assert.match(c.text,/\.space 2564/);
});
test('source and accepted ELF contain one zero-valued caller and only pinned ROM indirect division',()=>{
 const info={functions:old},elf=path.join(root,'.build',f.parent,'yoradio_esp8266_helix_native.elf');
 const c=sem.contract(info,elf);assert.equal(c.decoder_only,true);assert.equal(c.references.direct_calls.length,1);
 assert.equal(c.references.address_references.length,0);assert.equal(c.references.indirect_calls.length,3);
 assert.ok(c.references.indirect_calls.every(x=>x.target===0x4000e21c));
});
test('actual assembled candidate preserves every retained instruction, reference and branch successor',()=>{
 const p=f.read(path.join(f.art('candidate'),'preflight.json'));
 assert.deepEqual(sem.prove(p.functions.clt_compute_allocation,p.actual_functions.clt_compute_allocation),p.semantic);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 assert.ok(p.semantic.live_bytes<2564);assert.equal(p.semantic.retained_instructions,930);
});
test('arithmetic, stack, literal, call and branch changes are rejected by linked equivalence',()=>{
 const p=f.read(path.join(f.art('candidate'),'preflight.json')),before=p.functions.clt_compute_allocation,after=p.actual_functions.clt_compute_allocation;
 const substitutions=[
  ['movi\ta9, 192','movi\ta9, 196'],['s32i\ta12, a1, 184','s32i\ta12, a1, 180'],
  ['402428c4 <yoradio_opus_scratch_mark>','402428d8 <yoradio_opus_scratch_mark>']
 ];
 for(const[from,to]of substitutions)assert.throws(()=>sem.prove(before,mutation(after,from,to)));
 const literal=after.disassembly.match(/l32r\t([^,]+), ([0-9a-f]+) <[^>]*>/);assert.ok(literal);
 assert.throws(()=>sem.prove(before,mutation(after,literal[0],literal[0].replace(literal[2],(parseInt(literal[2],16)+4).toString(16)))));
 const branch=after.disassembly.match(/b(?:eqz|nez|ge|lt)\t[^\n]+/);assert.ok(branch);
 const destination=branch[0].match(/([0-9a-f]+) <[^>]*>/);assert.ok(destination);
 assert.throws(()=>sem.prove(before,mutation(after,branch[0],branch[0].replace(destination[1],after.address.toString(16)))));
});
test('exact PCM host model disables only the three encoder decisions',()=>{
 const models=f.cModels(),rate=models.find(m=>m.source==='upstream/celt/rate.c'),text=fs.readFileSync(rate.file,'utf8');
 assert.equal([...text.matchAll(/if \(0 \/\* decoder-only:/g)].length,3);assert.doesNotMatch(text,/if \(encode\)/);
 const report=f.read(path.join(root,'.build/opus-bands-allocation-decode/correctness.json'));
 assert.equal(report.passed,true);assert.equal(report.cases.length,24);assert.ok(report.cases.some(c=>c.name==='stereo-510'));
 assert.ok(report.cases.every(c=>c.pcm.exact));
});
