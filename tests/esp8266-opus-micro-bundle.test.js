const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/micro_bundle.cjs'),mul=require('../tools/esp8266_opus_asm/mdct_mul16.cjs');
const {sourceHash,hash,component}=require('../tools/esp8266_opus_asm/export.cjs'),{verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const proof=()=>f.read(path.join(f.art('candidate'),'preflight.json'));

test('three-component frozen bundle preserves PCM semantics, ABI and RAM on the current accepted layout',()=>{
 const p=proof();assert.deepEqual(f.prove(p.functions,p.actual_functions,p.patches),p.semantic);
 assert.equal(p.semantic.components,3);assert.equal(p.patches.length,18);
 assert.equal(p.semantic.entropy.numeric.cases,81120);assert.equal(p.semantic.entropy.symbolic.shift_counts,32);
 assert.equal(p.semantic.fft.removed_private_stack_reads,1);assert.equal(p.semantic.numeric.cases,589824);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 const products=p.semantic.mul_widths.products.filter(p=>p.eligible);
 assert.equal(products.length,16);assert.ok(products.every(p=>p.instruction.startsWith('mul16s ')));
});
test('bundle rejects overlapping overlays, stale MDCT offsets and invalid operand-width assumptions',()=>{
 const p=proof();f.disjoint(p.patches);
 assert.throws(()=>f.disjoint([...p.patches,{address:p.patches[0].address+1,bytes:3}]),/Overlapping/);
 const stale=structuredClone(p.patches);stale[6].address=0x402473d7;
 assert.throws(()=>f.prove(p.functions,p.actual_functions,stale));
 const wrong=structuredClone(p.actual_functions);
 assert.ok(wrong.clt_mdct_backward_c.disassembly.includes('mul16s'));
 wrong.clt_mdct_backward_c.disassembly=wrong.clt_mdct_backward_c.disassembly.replace('mul16s','mull');
 assert.throws(()=>f.prove(p.functions,wrong,p.patches));
 const orig=p.functions.clt_mdct_backward_c.disassembly,rows=require('../tools/esp8266_opus_asm/frozen_reloads.cjs').rows(orig);
 const unsafe=mul.widths(orig).products.find(p=>!p.eligible);assert.ok(unsafe);
 const row=rows.find(r=>r.address===unsafe.address);
 assert.throws(()=>mul.validateActual(orig,orig,[{address:row.address,instruction:'mul16s '+row.args}]));
});
test('bundle artifacts pin source dependencies and only eighteen disjoint byte ranges',()=>{
 const pair=f.verifyPair(),p=pair.proof;assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/micro_bundle.cjs')));
 assert.deepEqual(p.dependencies,f.depHashes());assert.equal(p.app_bytes,903216);
 assert.equal(pair.manifests.control.app_sha256,'9069d279220b60c7da9b8615fa0d47e54e9e5ace2428ac66ba1a00300ad87164');
 assert.equal(pair.manifests.candidate.post_link_pvq_row_loop_variant,'candidate');
 assert.equal(pair.manifests.candidate.post_link_partition_frozen_variant,undefined);
 assert.equal(pair.manifests.candidate.post_link_fft_schedule_variant,undefined);
 assert.equal(p.patches.reduce((s,p)=>s+p.bytes,0),91);
});
test('bundle host model preserves all24 cases, state sizes and original decoder sources through510kbps',()=>{
 const file=path.join(component,'upstream/celt/entdec.c'),before=hash(fs.readFileSync(file)),models=f.cModels();
 assert.equal(hash(fs.readFileSync(file)),before);assert.equal(models.length,1);
 const h=f.read(path.join(f.art('candidate'),'host.json'));
 assert.equal(h.kind,'micro-bundle');assert.equal(h.passed,true);
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/micro_bundle.cjs')));
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));
 for(const c of h.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);verifyStates(c.reference,c.candidate,c.name==='mixed');}
});
