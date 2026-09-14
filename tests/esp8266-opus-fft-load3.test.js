const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/fft_load3.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs'),{sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const dir=f.art('candidate'),read=f.read;
test('FFT three-load actual opcodes preserve all registers and ordered memory reads',()=>{
  const p=read(path.join(dir,'preflight.json'));assert.equal(p.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/fft_load3.cjs')));assert.equal(p.asm_sha256_lf,sourceHash(f.sourceFile));assert.equal(p.asm_sha256_lf,sourceHash(path.join(dir,'patches.s')));
  assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);assert.equal(p.patches.length,1);const patch=p.patches[0];
  const old=p.functions.opus_fft_impl,newFn=p.actual_functions.opus_fft_impl;const {before_hex,after_hex,...spec}=patch;assert.deepEqual(f.findPatch(old),spec);
  const inside=fn=>base.rows(fn.disassembly).filter(r=>r.address>=patch.address&&r.address<patch.address+patch.bytes);
  assert.deepEqual(inside(newFn).map(r=>r.bytes),[3,2,3]);assert.deepEqual(inside(newFn).map(r=>r.text),f.replacement);
  assert.deepEqual(f.prove(inside(old).map(r=>r.text),inside(newFn).map(r=>r.text)),p.symbolic);
  const outside=fn=>base.rows(fn.disassembly).filter(r=>r.address<patch.address||r.address>=patch.address+patch.bytes);
  assert.deepEqual(outside(old),outside(newFn));for(const n of f.names.filter(n=>n!=='opus_fft_impl'))assert.deepEqual(p.functions[n],p.actual_functions[n]);
});
test('FFT compact load proof fails on register, address, order and branch mutations',()=>{
  for(const bad of[['l32i a3, a1, 36',...f.replacement.slice(1)],['l32i a3, a1, 32','l32i a2, a3, 4','l32i a3, a3, 0'],['l32i a3, a1, 32','l32i a2, a3, 0','l32i a4, a3, 4'],['l32i a3, a1, 32','s32i a2, a3, 0','l32i a3, a3, 4']])assert.throws(()=>f.prove(f.original,bad));
  const fn=read(path.join(dir,'preflight.json')).functions.opus_fft_impl;
  assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+'\n40254120: 000006 j 40254128 <bad>\n'}),/Interior entry/);
  assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+'\n40254120: 0000a0 jx a2\n'}),/Indirect/);
});
test('FFT candidate differs only inside the eight-byte range and image checksums',()=>{
  const p=read(path.join(dir,'preflight.json')),a=zlib.gunzipSync(fs.readFileSync(path.join(dir,'parent.elf.gz'))),b=base.patchElf(a,p.patches);
  assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
  const object=fs.readFileSync(path.join(dir,'patches.o')),s=sections(object).find(s=>s.name==='.text.patch0');assert.equal(s.bytes,8);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),p.patches[0].after_hex);
  const manifests={},apps={};for(const t of['control','candidate']){manifests[t]=read(path.join(f.art(t),'manifest.json'));apps[t]=fs.readFileSync(path.join(f.art(t),'app.bin'));assert.equal(hash(apps[t]),manifests[t].app_sha256);assert.equal(apps[t].length,manifests[t].bytes);assert.equal(manifests[t].post_link_recipe_sha256_lf,p.recipe_sha256_lf);assert.equal(manifests[t].post_link_asm_sha256_lf,p.asm_sha256_lf);}
  f.manifestPair(manifests.control,manifests.candidate);assert.deepEqual(base.compareApps(apps.control,apps.candidate,p.patches),p.imageProof);
  assert.equal(hash(apps.control),require('../tools/esp8266_opus_asm/report_mdct_post_pair.cjs').verifyPair().manifests.candidate.app_sha256);
});
