const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/fft_schedule.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const dir=f.art('candidate'),read=f.read;
const inside=(fn,p)=>base.rows(fn.disassembly).filter(r=>r.address>=p.address&&r.address<p.address+p.bytes);
test('actual FFT scheduling preserves arbitrary registers, aliased reads and ordered stores',()=>{
 const p=read(path.join(dir,'preflight.json')),patch=p.patches[0];
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/fft_schedule.cjs')));
 assert.equal(p.asm_sha256_lf,sourceHash(f.sourceFile));assert.equal(p.asm_sha256_lf,sourceHash(path.join(dir,'patches.s')));
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.patches.length,1);
 const old=p.functions.opus_fft_impl,now=p.actual_functions.opus_fft_impl,{before_hex,after_hex,...spec}=patch;
 assert.deepEqual(f.findPatch(old),spec);assert.deepEqual(inside(now,patch).map(r=>r.bytes),[3,3,2,3,3,3,2]);
 assert.deepEqual(inside(now,patch).map(r=>r.text),f.replacement);
 assert.deepEqual(f.prove(inside(old,patch).map(r=>r.text),inside(now,patch).map(r=>r.text)),p.symbolic);
 const outside=fn=>base.rows(fn.disassembly).filter(r=>r.address<patch.address||r.address>=patch.address+patch.bytes);
 assert.deepEqual(outside(old),outside(now));
 assert.ok(p.symbolic.after.registers[6].includes('ITE('),'Twiddle alias must not be silently assumed absent');
 for(const n of f.names.filter(n=>n!=='opus_fft_impl'))assert.deepEqual(p.functions[n],p.actual_functions[n]);
});
test('648 numeric cases exercise PCM/twiddle overlap with metadata and written stack words',()=>{
 const p=read(path.join(dir,'preflight.json')),ops=inside(p.actual_functions.opus_fft_impl,p.patches[0]).map(r=>r.text);
 assert.deepEqual(f.numericProof(f.original,ops),p.numeric);assert.equal(p.numeric.cases,648);
 const bad=[...ops.slice(0,4),ops[6],ops[4],ops[5]];
 assert.throws(()=>f.numericProof(f.original,bad),'Reading twiddle before stores must fail on overlap');
});
test('scheduling proof rejects wrong addresses, reordered writes, early twiddle and interior entries',()=>{
 const replace=(i,op)=>f.replacement.map((x,j)=>j===i?op:x),q=f.replacement;
 const mutations=[replace(0,'l32i a3, a1, 36'),replace(1,'l32i a4, a1, 156'),replace(4,'s32i a2, a1, 100'),replace(5,'s32i a2, a1, 164'),replace(6,'l32i a6, a4, 4'),[...q.slice(0,4),q[5],q[4],q[6]],[...q.slice(0,4),q[6],q[4],q[5]],replace(4,'s32i a2, a3, 0')];
 for(const bad of mutations)assert.throws(()=>f.prove(f.original,bad));
 const fn=read(path.join(dir,'preflight.json')).functions.opus_fft_impl;
 assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+'\n40254120: 000006 j 40254134 <bad>\n'}),/Interior entry/);
 assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+'\n40254120: 0000a0 jx a2\n'}),/Indirect/);
});
test('only nineteen linked bytes plus valid image checksums differ; parent is accepted MDCT',()=>{
 const r=require('../tools/esp8266_opus_asm/report_fft_schedule.cjs').verifyPair(),p=r.proof;
 assert.equal(p.patches[0].bytes,19);assert.equal(p.symbolic.old_instructions,8);assert.equal(p.symbolic.new_instructions,7);
 const a=zlib.gunzipSync(fs.readFileSync(path.join(dir,'parent.elf.gz'))),b=base.patchElf(a,p.patches);
 assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
 const object=fs.readFileSync(path.join(dir,'patches.o')),s=sections(object).find(s=>s.name==='.text.patch0');
 assert.equal(s.bytes,19);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),p.patches[0].after_hex);
 assert.equal(r.manifests.candidate.post_link_fft_load3_variant,undefined,'Rejected load3 must not be inherited');
});
