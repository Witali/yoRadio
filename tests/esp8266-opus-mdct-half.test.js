const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/mdct_half.cjs'),base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash}=require('../tools/esp8266_opus_asm/export.cjs');
const proof=JSON.parse(fs.readFileSync(path.join(f.art('candidate'),'preflight.json'))),fn=f.names[0];
const old=proof.functions[fn].disassembly,now=proof.actual_functions[fn].disassembly;
test('actual MDCT ASM preserves every register bit for all words and both halfword parities',()=>{
 assert.deepEqual(f.proofBlocks(old,now,proof.patches),proof.symbolicProof);assert.equal(proof.symbolicProof.symbolic_paths,10);
 const bad=now.replace('srai\ta10, a2, 16','srai\ta10, a2, 15');assert.notEqual(bad,now);assert.throws(()=>f.proofBlocks(old,bad,proof.patches));
});
test('selector matching refuses interior entries, duplicate/missing source, and aliasing registers',()=>{
 for(const s of f.specs){const p=f.findPatch(proof.functions[fn],s);assert.equal(p.bytes,17);assert.throws(()=>f.findPatch({...proof.functions[fn],disassembly:old+'\n40249000: 000000 j '+(p.address+2).toString(16)+' <bad>'},s),/Interior/);}
 assert.throws(()=>f.findPatch({...proof.functions[fn],disassembly:old+'\n'+old},f.specs[0]),/unique/);
 assert.throws(()=>f.findPatch({...proof.functions[fn],disassembly:''},f.specs[0]),/unique/);assert.throws(()=>f.findPatch(proof.functions[fn],{...f.specs[0],word:f.specs[0].out}));
});
test('assembled code has exact local targets, operation order and untouched instructions outside selectors',()=>{
 f.validateActual(old,now,proof.patches);const bad=now.replace('bbsi\ta4, 1,','bbsi\ta4, 2,');assert.notEqual(bad,now);assert.throws(()=>f.validateActual(old,bad,proof.patches));
 assert.throws(()=>f.validateActual(old,now.replace('addi\ta1, a1, -96','addi\ta1, a1, -112'),proof.patches));
});
test('five 17-byte patches cannot alter other ELF bytes or RAM/stack/address metadata',()=>{
 const a=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz'))),b=base.patchElf(a,proof.patches);assert.equal(hash(b),proof.candidate_elf_sha256);assert.equal(a.length,b.length);
 const allowed=new Set(proof.patches.flatMap(p=>Array.from({length:p.bytes},(_,i)=>base.offsetAt(a,p.address,p.bytes)+i)));for(let i=0;i<a.length;i++)if(!allowed.has(i))assert.equal(a[i],b[i]);
 assert.equal(proof.static_ram_delta,0);assert.equal(proof.stack_delta,0);assert.throws(()=>base.patchElf(a,[...proof.patches,proof.patches[0]]));
});
test('image hashes, recipe and exact opcode evidence validate; mixed benchmark profiles refused',()=>{
 const {manifests}=require('../tools/esp8266_opus_asm/report_mdct_half.cjs').verifyPair();for(const change of [m=>m.cpu_mhz=80,m=>m.flash='QIO80',m=>m.opus_benchmark_output=true,m=>m.opus_function_profile=true,m=>m.opus_input_bytes+=4]){const b=structuredClone(manifests.candidate);change(b);assert.throws(()=>f.manifestPair(manifests.control,b));}
});
