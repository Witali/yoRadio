const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const f=require('../tools/esp8266_opus_asm/ec_bits.cjs'),sem=require('../tools/esp8266_opus_asm/ec_bits_proof.cjs');
const {hash,sourceHash,component}=require('../tools/esp8266_opus_asm/export.cjs'),{verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const proof=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
test('ec_dec_bits actual tail preserves arbitrary32 bits, SAR, entropy state and full refill/EOF',()=>{
 const p=proof(),r=sem.prove(p.functions.ec_dec_bits,p.actual_functions.ec_dec_bits);assert.deepEqual(r,p.symbolic);
 assert.equal(r.symbolic.shift_counts,32);assert.equal(r.numeric.cases,81120);assert.equal(r.numeric.refills,32448);assert.equal(r.numeric.exhausted,20280);
 assert.equal(r.reachable_tail_old,14);assert.equal(r.reachable_tail_new,13);assert.equal(r.live_bytes,33);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
});
test('entropy proof rejects wrong bit operations, memory order, omitted SAR restore and bypass entries',()=>{
 const p=proof(),a=p.functions.ec_dec_bits,b=p.actual_functions.ec_dec_bits,old=sem.inside(a),rows=sem.inside(b);
 for(const [from,to]of[['xor\ta2, a7, a9','and\ta2, a7, a9'],['s32i.n\ta8, a2, 12','s32i.n\ta8, a2, 16']]){
  assert.ok(b.disassembly.includes(from));assert.throws(()=>sem.prove(a,{...b,disassembly:b.disassembly.replace(from,to)}));
 }
 assert.throws(()=>sem.symbolicProof(old,rows.map(r=>r.text==='xor a2, a7, a9'?{...r,text:'and a2, a7, a9'}:r)));
 assert.throws(()=>sem.symbolicProof(old,rows.filter((_,i)=>i!==5)),/strictly equal/);
 assert.throws(()=>sem.audit({...a,disassembly:a.disassembly+'\n40298540: 000006 j 40298579 <bad>\n'},sem.oldOps),/Interior tail entry/);
});
test('fixed images preserve all unrelated bytes/addresses and inherit only accepted PVQ/MDCT overlays',()=>{
 const {proof:p,manifests}=require('../tools/esp8266_opus_asm/report_ec_bits.cjs').verifyPair();
 assert.equal(p.patches.length,1);assert.equal(p.patches[0].address,0x40298575);assert.equal(p.patches[0].bytes,35);assert.equal(p.app_bytes,903216);
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ec_bits.cjs')));assert.equal(p.asm_sha256_lf,sourceHash(f.sourceFile));assert.equal(p.proof_sha256_lf,sourceHash(f.proofFile));
 assert.equal(manifests.candidate.post_link_pvq_row_loop_variant,'candidate');assert.equal(manifests.candidate.post_link_partition_frozen_variant,undefined);
 assert.equal(manifests.candidate.post_link_fft_schedule_variant,undefined);for(const n of f.names.slice(1))assert.deepEqual(p.functions[n],p.actual_functions[n]);
 const tail=sem.inside(p.actual_functions.ec_dec_bits).at(-1);assert.equal(tail.address+tail.bytes,0x40298596);assert.equal(p.patches[0].after_hex.slice(-4),'0000');
});
test('host mirror preserves original C and all24 PCM/memory/PLC/reset/OOM scenarios through510kbps',()=>{
 const file=path.join(component,'upstream/celt/entdec.c'),before=hash(fs.readFileSync(file)),models=f.cModels();assert.equal(hash(fs.readFileSync(file)),before);assert.equal(models.length,1);
 assert.match(fs.readFileSync(models[0].file,'utf8'),/ret=\(opus_uint32\)window \^/);
 const h=f.read(path.join(f.art('candidate'),'host.json'));assert.equal(h.passed,true);assert.equal(h.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/ec_bits.cjs')));
 assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));
 for(const c of h.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);verifyStates(c.reference,c.candidate,c.name==='mixed');}
});
