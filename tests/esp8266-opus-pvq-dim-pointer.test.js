const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/pvq_dim_pointer.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_dim_pointer_proof.cjs');
const {sourceHash,hash,component}=require('../tools/esp8266_opus_asm/export.cjs'),{verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const proof=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
test('PVQ pointer cache preserves all15 linked exits and6720 numeric unsigned/sign/boundary paths',()=>{
 const p=proof(),r=sem.prove(p.functions.decode_pulses,p.actual_functions.decode_pulses);
 assert.deepEqual(r,p.symbolic);assert.equal(r.symbolic.paths.length,15);assert.equal(r.numeric.cases,6720);
 assert.ok(r.numeric.exits.every(n=>n>0));assert.equal(r.old_instructions,116);assert.equal(r.new_instructions,103);
 assert.equal(r.live_bytes,261);assert.equal(r.frame_bytes,48);assert.equal(r.a0_restore,0x40253584);
 for(const x of r.symbolic.paths)assert.equal(x.old_steps-x.new_steps,x.stop-1-(x.stop===8?1:0));
 assert.equal(r.symbolic.paths[0].new_steps,12);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
});
test('PVQ proof rejects bad pointer steps, changed branch predicates, interior entry and a0 liveness violations',()=>{
 const p=proof(),a=p.functions.decode_pulses,b=p.actual_functions.decode_pulses;
 for(const [from,to]of[['addi\ta0, a0, -4','addi\ta0, a0, -8'],['l32i.n\ta4, a0, 0','l32i.n\ta4, a0, 4']]){
  assert.ok(b.disassembly.includes(from));assert.throws(()=>sem.prove(a,{...b,disassembly:b.disassembly.replace(from,to)}));
 }
 const rows=sem.inside(b),changed=rows.map(r=>r.text.startsWith('bltu a2, a4,')?{...r,text:r.text.replace('a2, a4','a4, a2')}:r);
 assert.throws(()=>sem.symbolic(sem.inside(a),changed));
 assert.throws(()=>sem.audit({...a,disassembly:a.disassembly+'\n40253220: 000006 j 402533bb <bad>\n'},true),/External interior entry/);
 assert.throws(()=>sem.audit({...a,disassembly:a.disassembly+'\n40253500: 002d mov.n a2, a0\n'},true),/a0 is not dead/);
 assert.throws(()=>sem.audit({...a,disassembly:a.disassembly.replace('l32i.n\ta0, a1, 44','l32i.n\ta0, a1, 40')},true));
});
test('PVQ pointer images keep all unrelated bytes, tables, RAM and existing accepted overlays',()=>{
 const {proof:p,manifests}=require('../tools/esp8266_opus_asm/report_pvq_dim_pointer.cjs').verifyPair();
 assert.equal(p.patches.length,1);assert.equal(p.patches[0].address,0x402533b9);assert.equal(p.patches[0].bytes,286);
 assert.equal(p.app_bytes,903216);assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_dim_pointer.cjs')));
 assert.equal(manifests.control.app_sha256,'9069d279220b60c7da9b8615fa0d47e54e9e5ace2428ac66ba1a00300ad87164');
 assert.equal(manifests.candidate.post_link_pvq_row_loop_variant,'candidate');assert.equal(manifests.candidate.post_link_micro_bundle_variant,undefined);
 for(const n of f.names.slice(1))assert.deepEqual(p.functions[n],p.actual_functions[n]);
 const rs=sem.inside(p.actual_functions.decode_pulses);assert.equal(rs.at(-1).address,0x402534d5);assert.equal(rs.at(-1).text,'mov a12, a8');
});
test('PVQ host mirror changes only many-dimensions search and preserves24 exact PCM/state/PLC/reset/OOM cases',()=>{
 const file=path.join(component,'upstream/celt/cwrs.c'),before=hash(fs.readFileSync(file)),models=f.cModels();
 assert.equal(hash(fs.readFileSync(file)),before);assert.equal(models.length,1);
 const text=fs.readFileSync(models[0].file,'utf8');
 assert.equal(text.split('do p=CELT_PVQ_U_ROW[--_k][_n];').length,2);assert.match(text,/do \{ --_k; p=\(\*--row_ptr\)\[_n\]; \}/);
 const h=f.read(path.join(f.art('candidate'),'host.json'));assert.equal(h.kind,'pvq-dim-pointer');assert.equal(h.passed,true);
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/pvq_dim_pointer.cjs')));
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));
 for(const c of h.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);verifyStates(c.reference,c.candidate,c.name==='mixed');}
});
