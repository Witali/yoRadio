const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {parse,analyze,specialize,parentFile}=require('../tools/esp8266_opus_asm/partition_decode.cjs');
const text=fs.readFileSync(parentFile,'utf8').replace(/\r\n/g,'\n');
const path=require('node:path'),{root,hash}=require('../tools/esp8266_opus_asm/export.cjs');
test('only immutable ctx.encode makes the three partition branches constant',()=>{
 const p=parse(text),unknown=analyze(p,{encodeZero:false}),zero=analyze(p);
 assert.equal(unknown.branches.length,0);assert.equal(unknown.dead.length,0);
 assert.equal(zero.branches.length,3);assert.deepEqual(zero.branches.map(b=>b.taken),[false,true,true]);
 const r=specialize(text);assert.ok(r.proof.removed_instructions>100);
 assert.equal(parse(r.text).ops.filter(o=>o.op==='call0'&&['alg_quant','stereo_itheta','ec_encode','ec_enc_uint'].includes(o.args[0])).length,0);
 assert.ok(parse(r.text).ops.some(o=>o.op==='call0'&&o.args[0]==='alg_unquant'));
});
test('proof fails closed for ctx writes, escaped frame and unknown instruction',()=>{
 assert.throws(()=>analyze(parse(text.replace('\tl32i.n\ta8, a2, 8\t# ctx_143(D)->m, m','\ts32i a3,a2,0'))),/immutable encode/);
 assert.throws(()=>analyze(parse(text.replace('\ts32i\ta12, sp, 104','\ts32i\tsp, sp, 104'))),/pointer stored/);
 assert.throws(()=>analyze(parse(text.replace('\tmov.n\ta12, a2\t# ctx, ctx','\tmov.n\ta12, sp\t# escaped'))));
 assert.throws(()=>analyze(parse(text.replace('\tmov.n\ta12, a2\t# ctx, ctx','\tunknown_op a12, a2'))));
});
test('linked decoder projection is exact without RAM or stack growth',()=>{
 const {project}=require('../tools/esp8266_opus_asm/audit_partition_decode.cjs');
 const {normal}=require('../tools/esp8266_opus_asm/report_small_div_inline.cjs');
 const dir=path.join(root,'firmware/development/esp8266-opus-partition-decode-v1');
 const proof=JSON.parse(fs.readFileSync(path.join(dir,'preflight.json')));
 assert.equal(proof.passed,true);assert.equal(proof.static_ram_delta,0);
 const a=project(normal(proof.reference.functions.quant_partition.graph)),b=project(normal(proof.candidate.functions.quant_partition.graph));
 assert.deepEqual(a.graph,b.graph);assert.equal(a.branches.length,3);assert.equal(a.dead,179);
 assert.equal(b.branches.length,0);assert.equal(proof.recipe.stack_change_bytes,0);
 assert.equal(hash(fs.readFileSync(path.join(dir,'app.bin'))),proof.manifests[1].app_sha256.toLowerCase());
 assert.equal(proof.host.cases.length,24);assert.equal(proof.host.compound.length,3);
 const corrupt=proof.candidate.functions.quant_partition.graph.slice();
 const i=corrupt.findIndex(s=>s==='movi a2, 0');assert.ok(i>=0);corrupt[i]='movi a2, 1';
 assert.notDeepEqual(project(normal(corrupt)).graph,a.graph,'Arithmetic changes must not disappear in normalization');
});
