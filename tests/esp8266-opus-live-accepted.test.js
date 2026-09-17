const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/live_accepted.cjs');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {sections,inspectImage}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const directory=path.join(root,'firmware/development',f.variant);
const read=n=>JSON.parse(fs.readFileSync(path.join(directory,n),'utf8'));
test('all accepted ASM patches are relocated into ordinary radio without RAM/stack growth',()=>{
 const p=read('preflight.json'),m=read('manifest.json');
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/live_accepted.cjs')));
 assert.equal(p.records.length,18);assert.equal(m.opus_benchmark,false);assert.equal(m.opus_benchmark_output,false);assert.equal(m.freertos_runtime_stats,false);assert.equal(m.tone_test,false);assert.equal(m.i2s,true);assert.equal(m.data_gpio,3);
 let elf=zlib.gunzipSync(fs.readFileSync(path.join(directory,'base.elf.gz')));
 assert.equal(hash(elf),p.base_elf_sha256);
 for(const r of p.records){
  const old=path.join(root,'firmware/development',r.variant);
  assert.equal(sourceHash(path.join(old,'patches.s')),r.source_sha256_lf);assert.equal(sourceHash(path.join(old,'preflight.json')),r.original_proof_sha256_lf);
  assert.equal(hash(fs.readFileSync(path.join(old,'patches.elf'))),r.original_object_sha256);
  elf=frozen.patchElf(elf,r.patches);
 }
 assert.equal(hash(elf),p.candidate_elf_sha256);assert.deepEqual(elf,zlib.gunzipSync(fs.readFileSync(path.join(directory,'app.elf.gz'))));
 assert.deepEqual(p.after.sections,p.before.sections);assert.deepEqual(p.after.function_sizes,p.before.function_sizes);
 for(const name of f.names)assert.deepEqual(p.after.functions[name].graph,p.accepted.functions[name].graph);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 const app=fs.readFileSync(path.join(directory,'app.bin'));assert.equal(hash(app),m.app_sha256);assert.equal(app.length,m.bytes);
 // Verify loaded application segments actually contain the checked ELF bytes.
 for(const segment of inspectImage(app).segments){
  const s=sections(elf).find(s=>s.type===1&&segment.address>=s.address&&segment.address<s.address+s.bytes);
  assert.ok(s,'Unmapped image segment');
  // SDK esptool ESP8266V3FirmwareImage.save strips the rodata eight-byte
  // section prefix, before writing the segment. Other sections are direct.
  const skip=s.name==='.flash.rodata'?8:0;
  const offset=s.offset+segment.address-s.address+skip;
  const bytes=Math.min(segment.bytes,s.bytes-(segment.address-s.address)-skip);
  assert.equal(hash(app.subarray(segment.offset,segment.offset+bytes)),hash(elf.subarray(offset,offset+bytes)),s.name);
  assert.ok(segment.bytes-bytes<=3);assert.ok(app.subarray(segment.offset+bytes,segment.offset+segment.bytes).every(b=>b===0));
 }
});
test('address mapping refuses unknown targets, changed graph, size or instruction layout',()=>{
 const p=read('preflight.json'),raw=require('../tools/esp8266_opus_asm/report_layout.cjs').inspect('esp8266-opus-folding-control-v1',f.names);
 const map=f.mapping(raw,p.before);assert.throws(()=>map.move(0x12345678),/Unmapped/);
 const changed=structuredClone(p.before);changed.functions.quant_partition.graph[0]='bad';assert.throws(()=>f.mapping(raw,changed),/baseline graph/);
 changed.functions.quant_partition.graph=p.before.functions.quant_partition.graph;changed.functions.quant_partition.bytes++;assert.throws(()=>f.mapping(raw,changed),/size/);
 assert.equal(p.literal_readers.before.length,1);assert.equal(p.literal_readers.after.length,1);
});
