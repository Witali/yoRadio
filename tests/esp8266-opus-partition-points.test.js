const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/partition_points.cjs'),sem=require('../tools/esp8266_opus_asm/partition_points_proof.cjs');
const {hash,sourceHash,component}=require('../tools/esp8266_opus_asm/export.cjs'),{verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const proof=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
test('pointwise partition keeps every remaining internal address and the complete decoder contract',()=>{
 const p=proof();assert.deepEqual(f.prove(p.functions,p.actual_functions,p.patches),p.semantic);
 assert.equal(p.patches.length,5);assert.equal(p.patches.reduce((s,p)=>s+p.bytes,0),16);
 assert.equal(p.semantic.pointwise.frame_bytes,112);assert.equal(p.semantic.pointwise.zero_loads.length,2);
 assert.equal(p.semantic.pointwise.constant_branches.length,3);assert.equal(p.semantic.pointwise.unknown_encode_disables_specialization,true);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 assert.equal(p.functions.quant_partition.address,p.actual_functions.quant_partition.address);
 assert.equal(p.functions.quant_partition.bytes,2382);assert.equal(p.actual_functions.quant_partition.bytes,2382);
});
test('specialization fails closed without encode=0 and rejects nonzero MOVI or wrong jump target',()=>{
 const p=proof(),a=p.functions.quant_partition,b=p.actual_functions.quant_partition;
 assert.throws(()=>sem.findPatches(a,{encodeZero:false}));
 const wrong=structuredClone(b);assert.ok(wrong.disassembly.includes('movi.n\ta7, 0'));
 wrong.disassembly=wrong.disassembly.replace('movi.n\ta7, 0','movi.n\ta7, 1');
 assert.throws(()=>sem.prove(a,wrong,p.patches));
 const wrongJump=structuredClone(b);assert.ok(wrongJump.disassembly.includes('4024e36e <'));
 wrongJump.disassembly=wrongJump.disassembly.replace(/j\t4024e36e </,'j\t4024e403 <');
 assert.notEqual(wrongJump.disassembly,b.disassembly);assert.throws(()=>sem.prove(a,wrongJump,p.patches));
 const wrongPatch=structuredClone(p.patches);wrongPatch[2].target++;
 assert.throws(()=>sem.prove(a,b,wrongPatch));
});
test('pointwise rejects interior entries and changes to other decoder instructions',()=>{
 const p=proof(),a=p.functions.quant_partition,b=p.actual_functions.quant_partition;
 // Preserve a valid program graph while introducing an encoder-side entry
 // into the two overwritten bytes following the narrow constant branch.
 const bad=structuredClone(a);bad.disassembly=bad.disassembly.replace(/j\t4024e3e8 </,'j\t4024dbd5 <');
 assert.notEqual(bad.disassembly,a.disassembly);assert.throws(()=>sem.findPatches(bad),/Interior patch entry|strictly/);
 const other=structuredClone(b);other.disassembly=other.disassembly.replace('addi\ta1, a1, -112','addi\ta1, a1, -108');
 assert.notEqual(other.disassembly,b.disassembly);assert.throws(()=>sem.prove(a,other,p.patches));
});
test('pointwise image preserves all unrelated bytes and does not include prior failed candidates',()=>{
 const {proof:p,manifests}=f.verifyPair();
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/partition_points.cjs')));
 assert.deepEqual(p.dependencies,f.depHashes());assert.equal(p.app_bytes,903216);
 assert.equal(manifests.control.app_sha256,'9069d279220b60c7da9b8615fa0d47e54e9e5ace2428ac66ba1a00300ad87164');
 for(const key of['post_link_partition_frozen_variant','post_link_pvq_dim_pointer_variant','post_link_micro_bundle_variant'])assert.equal(manifests.candidate[key],undefined);
 for(const n of f.names.slice(1))assert.deepEqual(p.functions[n],p.actual_functions[n]);
 const narrow=p.patches.find(p=>p.address===0x4024dbd3);assert.equal(narrow.bytes,5);assert.equal(narrow.after_hex.slice(-4),'0000');
});
test('host invariant and all24 PCM/state/PLC/reset/OOM cases remain exact through510kbps',()=>{
 const file=path.join(component,'upstream/celt/bands.c'),before=hash(fs.readFileSync(file)),models=f.cModels();
 assert.equal(hash(fs.readFileSync(file)),before);assert.equal(models.length,1);assert.match(fs.readFileSync(models[0].file,'utf8'),/if \(ctx->encode != 0\) abort/);
 const h=f.read(path.join(f.art('candidate'),'host.json'));assert.equal(h.kind,'partition-points');assert.equal(h.passed,true);
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/partition_points.cjs')));
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));
 for(const c of h.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);verifyStates(c.reference,c.candidate,c.name==='mixed');}
});
