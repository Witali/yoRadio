const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/partition_frozen.cjs'),sem=require('../tools/esp8266_opus_asm/partition_frozen_proof.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');const p=()=>f.read(path.join(f.art('candidate'),'preflight.json'));
test('frozen quant_partition rebuilds from exact linked GCC code with pinned addresses and comments',()=>{
 const r=p(),fn=r.functions.quant_partition,x=sem.compile(fn);assert.equal(r.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/partition_frozen.cjs')));assert.equal(r.proof_sha256_lf,sourceHash(f.proofFile));assert.equal(hash(Buffer.from(x.text)),r.asm_sha256_lf);assert.equal(r.asm_sha256_lf,sourceHash(f.sourceFile));assert.deepEqual(x.analysis,r.raw_specialization);
 assert.equal(r.raw_specialization.removed_raw_instructions,185);assert.equal(r.raw_specialization.branches.length,3);assert.match(x.text,/original112-byte stack/);assert.match(x.text,/ROM L32R\/CALLX0 pairs retained/);assert.match(x.text,/original C\/GCC sources unchanged/);
 assert.deepEqual(sem.prove(fn,r.actual_functions.quant_partition),r.symbolic);assert.equal(r.symbolic.removed_linked_instructions,179);assert.equal(r.symbolic.live_bytes,1859);assert.equal(r.symbolic.padding_bytes,523);assert.equal(r.symbolic.callx_pairs_before,3);assert.equal(r.symbolic.callx_pairs_after,2);
 assert.deepEqual(sem.contract({functions:r.functions}),r.call_chain);assert.equal(r.static_ram_delta,0);assert.equal(r.stack_delta,0);
});
test('projection rejects arithmetic, literal-address, call-entry and encode-contract corruption',()=>{
 const r=p(),before=r.functions.quant_partition,after=r.actual_functions.quant_partition;
 const graph=after.graph.slice(),index=graph.findIndex(x=>x==='movi a2, 0');assert.ok(index>=0);graph[index]='movi a2, 1';assert.throws(()=>sem.prove(before,{...after,graph}));
 const literal=base.rows(after.disassembly).find(x=>x.op==='l32r'),oldAddress=sem.target(literal).toString(16),changedAddress=(sem.target(literal)+4).toString(16);
 assert.throws(()=>sem.prove(before,{...after,disassembly:after.disassembly.replace(oldAddress,changedAddress)}),/literal\/call addresses/);
 const callx=base.rows(before.disassembly).find(x=>x.op==='callx0');assert.throws(()=>sem.compile({...before,disassembly:before.disassembly+'\n4024dab0: 000006 j '+callx.address.toString(16)+' <bad>\n'}),/Bypassed/);
 const escaped=before.disassembly.replace('mov.n\ta12, a2','mov.n\ta12, a1');assert.notEqual(escaped,before.disassembly);assert.throws(()=>sem.compile({...before,disassembly:escaped}));
 const functions=structuredClone(r.functions),g=functions.celt_decode_with_ec_dred.graph;const zero=g.findIndex(s=>s==='movi a8, 0');assert.ok(zero>=0);g[zero]='movi a8, 1';assert.throws(()=>sem.contract({functions}));
});
test('only original2382-byte function range and image checksums change; accepted PVQ parent remains intact',()=>{
 const {proof:r,manifests}=require('../tools/esp8266_opus_asm/report_partition_frozen.cjs').verifyPair();assert.equal(r.patches.length,1);assert.equal(r.patches[0].address,0x4024dafc);assert.equal(r.patches[0].bytes,2382);assert.equal(r.app_bytes,903216);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),b=base.patchElf(a,r.patches);assert.equal(hash(a),r.parent_elf_sha256);assert.equal(hash(b),r.candidate_elf_sha256);
 for(const name of f.names.slice(1))assert.deepEqual(r.functions[name],r.actual_functions[name]);assert.equal(manifests.candidate.post_link_pvq_row_loop_variant,'candidate');assert.equal(manifests.candidate.post_link_post_pair_variant,'candidate');assert.equal(manifests.control.app_sha256,manifests.candidate.post_link_parent_app_sha256);
 const patch=Buffer.from(r.patches[0].after_hex,'hex');assert.ok(patch.subarray(r.symbolic.live_bytes).every(x=>x===0),'Padding contains no copied live instructions');
 const h=f.read(path.join(f.art('candidate'),'host-parent.json'));assert.equal(h.passed,true);assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
});
