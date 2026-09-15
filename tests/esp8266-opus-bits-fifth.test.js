const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/bits_fifth.cjs'),sem=require('../tools/esp8266_opus_asm/bits_fifth_proof.cjs');
const {hash,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const {verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const proof=()=>f.read(path.join(f.art('candidate'),'preflight.json'));

test('linked last-step shortcut preserves image, all live registers and every standard-table budget',()=>{
 const {proof:p,manifests}=f.verifyPair();
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/bits_fifth.cjs')));
 assert.equal(manifests.control.app_sha256,'9069d279220b60c7da9b8615fa0d47e54e9e5ace2428ac66ba1a00300ad87164');
 assert.equal(manifests.candidate.post_link_partition_points_variant,undefined);
 assert.equal(p.patches.length,2);assert.deepEqual(p.patches.map(v=>v.bytes),[20,28]);
 assert.equal(p.app_bytes,903216);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 assert.equal(p.semantic.search.frame_bytes,112);assert.equal(p.semantic.search.numeric.cases,378304);
 assert.equal(p.semantic.search.numeric.shortcuts,377706);assert.equal(p.semantic.search.numeric.slow,598);
 assert.deepEqual(p.semantic.search.numeric.step_differences,{'2':371773,'4':5933,'-4':483,'-3':115});
 for(const n of f.names.slice(1))assert.deepEqual(p.functions[n],p.actual_functions[n]);
});
test('encoder storage is rejected unless the original private encode predicate is known zero',()=>{
 const p=proof(),bad=structuredClone(p.functions.quant_partition);
 assert.ok(bad.disassembly.includes('l32i.n\ta7, a12, 0'));
 bad.disassembly=bad.disassembly.replace('l32i.n\ta7, a12, 0','movi.n\ta7, 1');
 assert.throws(()=>sem.findPatches(bad));
 assert.deepEqual(sem.findPatches(p.functions.quant_partition),sem.spans);
});
test('scratch-register liveness refuses a downstream read before redefinition',()=>{
 const p=proof(),bad=structuredClone(p.actual_functions.quant_partition);
 assert.ok(bad.disassembly.includes('l32i.n\ta6, a12, 32'));
 bad.disassembly=bad.disassembly.replace('l32i.n\ta6, a12, 32','l32i.n\ta6, a10, 32');
 assert.throws(()=>sem.deadUntilDefinition(bad,sem.stops[0],10),/Live a10/);
 for(const pc of sem.stops)for(const r of[10,11])assert.ok(sem.deadUntilDefinition(p.actual_functions.quant_partition,pc,r).ends.length);
});
test('actual instruction model detects changed condition and out-of-row reads',()=>{
 const p=proof(),a=p.functions.quant_partition,b=structuredClone(p.actual_functions.quant_partition);
 assert.ok(b.disassembly.includes('bgei\ta10, 2,'));b.disassembly=b.disassembly.replace('bgei\ta10, 2,','bgei\ta10, 3,');
 assert.throws(()=>sem.numeric(a,b));
 const bad=structuredClone(a);
 // Pin an instruction inside the modeled search, not the earlier split check.
 bad.disassembly=bad.disassembly.replace(/^(4024e1ad:.*l8ui\ta4, a4), 0$/m,(_,prefix)=>prefix+', 255');
 assert.notEqual(bad.disassembly,a.disassembly);
 assert.throws(()=>sem.numeric(bad,p.actual_functions.quant_partition),/Out-of-row read/);
});
test('actual host shortcut preserves24 PCM/state/PLC/reset/OOM cases through510kbps without source changes',()=>{
 const file=path.join(component,'upstream/celt/bands.c'),before=hash(fs.readFileSync(file)),models=f.cModels();
 assert.equal(hash(fs.readFileSync(file)),before);assert.equal(models.length,1);
 assert.match(fs.readFileSync(models[0].file,'utf8'),/q = y_bits_fifth\(m, i, LM, b\)/);
 const h=f.read(path.join(f.art('candidate'),'host.json'));assert.equal(h.kind,'bits-fifth');assert.equal(h.passed,true);
 assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/bits_fifth.cjs')));
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));
 for(const c of h.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);verifyStates(c.reference,c.candidate,c.name==='mixed');}
});
