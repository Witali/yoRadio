const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/pvq_row_loop.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_row_proof.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const p=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
test('PVQ linked loop preserves registers/read order by induction with four instructions per continuing probe',()=>{
 const r=p();assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_row_loop.cjs')));assert.equal(r.asm_sha256_lf,sourceHash(f.sourceFile));assert.equal(r.proof_sha256_lf,sourceHash(f.proofFile));
 assert.deepEqual(sem.prove(r.functions.decode_pulses,r.actual_functions.decode_pulses),r.symbolic);assert.equal(r.symbolic.induction.old_loop_instructions,6);assert.equal(r.symbolic.induction.new_loop_instructions,4);assert.equal(r.symbolic.induction.table_reads_unchanged,true);assert.equal(r.symbolic.reachable_old,13);assert.equal(r.symbolic.reachable_new,10);
 assert.equal(r.symbolic.numeric.cases,2298);assert.equal(r.symbolic.numeric.probes,2035278);assert.equal(r.static_ram_delta,0);assert.equal(r.stack_delta,0);
});
test('PVQ patch cannot admit new interior entries, extra loads, changed return registers or a reversed branch',()=>{
 const r=p(),before=r.functions.decode_pulses,after=r.actual_functions.decode_pulses;
 for(const[from,to]of[['addi\ta6, a15, -4','addi\ta6, a15, -8'],['l32i.n\ta8, a6, 0','l32i.n\ta8, a6, 4'],['slli\ta9, a3, 16','slli\ta11, a3, 16'],['bltu\ta2, a8','bgeu\ta2, a8']]){
  assert.ok(after.disassembly.includes(from),from);assert.throws(()=>sem.prove(before,{...after,disassembly:after.disassembly.replace(from,to)}));
 }
 assert.throws(()=>sem.audit({...before,disassembly:before.disassembly+'\n40253100: 000006 j 40253338 <bad>\n'},sem.oldOps),/interior entry/);
 const oldRows=sem.inside(before),newRows=sem.inside(after),bad=newRows.map(x=>x.text==='mov a3, a12'?{...x,text:'mov a3, a13'}:x);
 assert.throws(()=>sem.numeric(oldRows,bad));
});
test('PVQ fixed-address images differ in one35-byte block only, valid checksums, no RAM growth or rejected FFT inheritance',()=>{
 const {proof:r,manifests}=require('../tools/esp8266_opus_asm/report_pvq_row_loop.cjs').verifyPair();assert.equal(r.patches.length,1);assert.equal(r.patches[0].address,0x40253331);assert.equal(r.patches[0].bytes,35);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));assert.equal(hash(a),r.parent_elf_sha256);assert.equal(hash(base.patchElf(a,r.patches)),r.candidate_elf_sha256);
 assert.equal(manifests.candidate.post_link_post_pair_variant,'candidate');assert.equal(manifests.candidate.post_link_fft_schedule_variant,undefined);assert.equal(manifests.candidate.post_link_fft_load3_variant,undefined);
 assert.equal(manifests.control.app_sha256,manifests.candidate.post_link_parent_app_sha256);assert.equal(r.app_bytes,903216);
 for(const name of f.names.slice(1))assert.deepEqual(r.functions[name],r.actual_functions[name]);
});
