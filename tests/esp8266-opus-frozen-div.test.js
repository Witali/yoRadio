const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const frozen=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const proof=read(path.join(frozen.art('asm'),'preflight.json'));
const elf=zlib.gunzipSync(fs.readFileSync(path.join(frozen.art('asm'),'linked.elf.gz')));
const asm=fs.readFileSync(path.join(frozen.art('asm'),'app.bin'));
const rom=fs.readFileSync(path.join(frozen.art('rom'),'app.bin'));
test('frozen ELF changes one aligned call target without moving any code or RAM',()=>{
 assert.equal(hash(elf),proof.parent_elf_sha256);assert.equal(elf.length,proof.elf_bytes);
 assert.equal(proof.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/frozen_div.cjs')));
 const {output,offset}=frozen.patchLiteral(elf,proof.literal,proof.helper,proof.rom);
 assert.equal(offset,proof.elf_offset);assert.equal(hash(output),proof.rom_elf_sha256);
 assert.deepEqual(frozen.sections(output),frozen.sections(elf));
 assert.deepEqual(output.subarray(0,offset),elf.subarray(0,offset));
 assert.deepEqual(output.subarray(offset+4),elf.subarray(offset+4));
 assert.equal(proof.calls.length,3);assert.ok(proof.calls.every(c=>c.literal===proof.literal));
 assert.equal(proof.static_ram_delta,0);
});
test('both SDK images have valid checksums/digests and only the literal/checksum/digest differ',()=>{
 assert.deepEqual(frozen.compareImages(asm,rom,proof.literal,proof.helper,proof.rom),proof.imageProof);
 for(const [target,bytes]of [['asm',asm],['rom',rom]]){
  const m=read(path.join(frozen.art(target),'manifest.json'));
  assert.equal(m.app_sha256,hash(bytes));assert.equal(m.bytes,bytes.length);
  assert.equal(m.post_link_division_target,target);assert.equal(m.post_link_recipe_sha256_lf,proof.recipe_sha256_lf);
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_function_profile,false);
 }
});
test('post-link patch refuses wrong, unaligned, absent and NOBITS targets',()=>{
 assert.throws(()=>frozen.patchLiteral(elf,proof.literal,proof.rom,proof.helper));
 assert.throws(()=>frozen.patchLiteral(elf,proof.literal+1,proof.helper,proof.rom));
 assert.throws(()=>frozen.patchLiteral(elf,0xfffffffc,proof.helper,proof.rom));
 const bss=frozen.sections(elf).find(s=>s.type===8&&s.bytes>=4);assert.ok(bss);
 assert.throws(()=>frozen.patchLiteral(elf,bss.address,proof.helper,proof.rom));
 assert.throws(()=>frozen.sections(elf.subarray(0,128)));
 const otherCpu=Buffer.from(elf);otherCpu.writeUInt16LE(3,18);assert.throws(()=>frozen.sections(otherCpu));
});
test('valid app checksum does not permit unrelated payload changes',()=>{
 const info=frozen.inspectImage(rom),bad=Buffer.from(rom),offset=info.segments[0].offset;
 assert.notEqual(offset,proof.imageProof.literal_offset);bad[offset]^=1;bad[info.checksumOffset]^=1;
 Buffer.from(hash(bad.subarray(0,info.checksumOffset+1)),'hex').copy(bad,info.checksumOffset+1);
 frozen.inspectImage(bad);
 assert.throws(()=>frozen.compareImages(asm,bad,proof.literal,proof.helper,proof.rom),/Other app bytes/);
 const checksum=Buffer.from(rom);checksum[info.checksumOffset]^=1;assert.throws(()=>frozen.inspectImage(checksum));
 const digest=Buffer.from(rom);digest[digest.length-1]^=1;assert.throws(()=>frozen.inspectImage(digest));
 assert.throws(()=>frozen.inspectImage(Buffer.concat([rom,Buffer.alloc(1)])));
});

test('frozen pair refuses mismatched benchmark, memory and platform settings',()=>{
 const {pairedManifests,verifyPair}=require('../tools/esp8266_opus_asm/report_frozen_div.cjs');
 const {manifests}=verifyPair();
 for(const change of [
  m=>{m.cpu_mhz=80;},m=>{m.flash='QIO80';},m=>{m.opus_input_bytes+=4;},
  m=>{m.opus_benchmark_output=true;},m=>{m.opus_function_profile=true;},
  m=>{m.opus_profile_stage=1;},m=>{m.post_link_division_target='rom';}
 ]){const b=structuredClone(manifests.asm);change(b);assert.throws(()=>pairedManifests(manifests.rom,b));}
});
