const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const sem=require('../tools/esp8266_opus_asm/quant_decode_proof.cjs'),f=require('../tools/esp8266_opus_asm/quant_decode.cjs');
const audit=require('../tools/esp8266_opus_asm/audit_quant_decode.cjs');
const root=path.resolve(__dirname,'..');
const parent=()=>f.read(path.join(root,'firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json'));
const evidence=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
function mutation(fn,from,to){const x=structuredClone(fn);x.disassembly=x.disassembly.replace(from,to);assert.notEqual(x.disassembly,fn.disassembly);return x;}

test('decode-only reachability needs explicit context and private-frame contracts',()=>{
 const fn=parent().actual_functions.quant_all_bands,yes=audit.analyze(fn);
 assert.equal(yes.removed_instructions,557);assert.equal(yes.removed_bytes,1551);assert.equal(yes.branches.length,32);
 assert.equal(yes.ctx_encode_at_store,0);assert.equal(yes.frame_bytes,384);
 assert.equal(audit.analyze(fn,{encodeZero:false,immutableContext:false,immutableResynth:false}).removed_instructions,0);
 assert.equal(audit.analyze(fn,{immutableContext:false,immutableResynth:false,privateFrame:false}).removed_instructions,13);
 assert.equal(audit.analyze(fn,{privateFrame:false}).removed_instructions,220);
 assert.ok(!yes.calls_live.some(r=>/ec_enc|ec_encode|alg_quant|stereo_itheta/.test(r.text)));
});

test('new stack escapes, encode stores, partial writes or a stack pivot reject the audit',()=>{
 const fn=parent().actual_functions.quant_all_bands;
 for(const[from,to]of[
  ['addi\ta12, a1, 32','addi\ta12, a1, 100'],
  ['s32i.n\ta13, a1, 32','s32i.n\ta12, a1, 32'],
  ['s32i.n\ta8, a1, 36','s16i\ta8, a1, 36'],
  ['or\ta1, a1, a1','mov.n\ta1, a2']])assert.throws(()=>audit.analyze(mutation(fn,from,to)));
});

test('native zero caller, immutable context fields and literal false matches are checked',()=>{
 const p=evidence(),c=sem.contract({functions:p.functions},path.join(root,'.build',f.parent,'yoradio_esp8266_helix_native.elf'));
 assert.equal(c.caller.argument,'a2=0');assert.equal(c.source.context_bytes,60);
 assert.equal(c.references.direct_calls.length,1);assert.equal(c.references.indirect_calls.length,11);
 assert.equal(c.references.literal_false_matches.length,2);assert.equal(c.references.instruction_false_matches.length,2);
 assert.deepEqual(c.references.address_references,[]);
 const caller=p.functions.celt_decode_with_ec_dred;
 // The same registers are reused earlier: mutate the actual argument setup,
 // not the first textual occurrence elsewhere in this large caller.
 for(const [pc,from,to]of[['40244d6a','movi.n\ta8, 0','movi.n\ta8, 1'],['40244da8','mov.n\ta2, a8','mov.n\ta2, a3']]){
  const line=caller.disassembly.split(/\r?\n/).find(s=>s.startsWith(pc+':'));assert.ok(line&&line.includes(from));
  assert.throws(()=>sem.callerArguments(mutation(caller,line,line.replace(from,to))));
 }
});

test('every removed instruction is commented; no RAM or frame increase',()=>{
 const p=evidence(),fn=p.functions.quant_all_bands,c=sem.compile(fn),s=sem.selection(fn);
 assert.equal(c.kept_instructions,2786);assert.equal(c.source_instructions,3370);
 assert.equal(c.source_instructions-c.removed_dead-c.kept_instructions,27);
 assert.equal(c.removed_checks,27);assert.equal(p.semantic.checks_replaced_with_jump,5);
 for(const r of s.rows.filter(r=>s.dead.has(r.address)))assert.ok(c.text.includes(r.text));
 assert.match(c.text,/original384-byte frame/);assert.match(c.text,/\.space 9416/);
 assert.deepEqual(sem.prove(fn,p.actual_functions.quant_all_bands),p.semantic);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
});

test('linked arithmetic, memory, literal, call and branch mutations cannot pass',()=>{
 const p=evidence(),before=p.functions.quant_all_bands,after=p.actual_functions.quant_all_bands;
 for(const[from,to]of[
  ['movi\ta9, 384','movi\ta9, 388'],
  ['s32i\ta13, a1, 372','s32i\ta13, a1, 368'],
  ['402428c4 <yoradio_opus_scratch_mark>','402428d8 <yoradio_opus_scratch_mark>']])assert.throws(()=>sem.prove(before,mutation(after,from,to)));
 const literal=after.disassembly.match(/l32r\t([^,]+), ([0-9a-f]+) <[^>]*>/);assert.ok(literal);
 assert.throws(()=>sem.prove(before,mutation(after,literal[0],literal[0].replace(literal[2],(parseInt(literal[2],16)+4).toString(16)))));
 const branch=after.disassembly.match(/b(?:eqz|nez|ge|lt)\t[^\n]+/);assert.ok(branch);
 const destination=branch[0].match(/([0-9a-f]+) <[^>]*>/);assert.ok(destination);
 assert.throws(()=>sem.prove(before,mutation(after,branch[0],branch[0].replace(destination[1],after.address.toString(16)))));
});

test('bounded C semantic model passes all24 PCM/state/ASan/UBSan cases',()=>{
 const models=f.cModels(),bands=models.find(m=>m.source==='upstream/celt/bands.c');
 assert.match(fs.readFileSync(bands.file,'utf8'),/^#undef YORADIO_OPUS_CELT_DECODE_ONLY\n#define YORADIO_OPUS_CELT_DECODE_ONLY 1\n/);
 const report=f.read(path.join(root,'.build/opus-bands-quant-decode/correctness.json'));
 assert.equal(report.passed,true);assert.equal(report.cases.length,24);
 assert.ok(report.cases.some(c=>c.name==='stereo-510'));assert.ok(report.cases.every(c=>c.pcm.exact));
});
