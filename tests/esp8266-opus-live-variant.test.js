// Offline checks for rebasing the accepted ASM chain into a new radio profile.
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/live_variant.cjs');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {sections,inspectImage}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
for(const [variant,input] of [['input2k',2048],['noooseq',1024],['noooseq-input2k',2048],['pcmqueue',1024]]) {
const directory=path.join(root,`firmware/development/esp8266-opus-live-asm-${variant}-20260917`);
const read=n=>JSON.parse(fs.readFileSync(path.join(directory,n),'utf8'));

test(`${variant} live profile preserves all18 accepted stages and exact loaded bytes`,()=>{
 const p=read('preflight.json'),m=read('manifest.json');
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm/live_variant.cjs')));
 assert.equal(p.records.length,18);
 assert.equal(m.opus_input_bytes,input);assert.equal(m.opus_scratch_bytes,6144);
 if(variant!=='input2k') assert.equal(m.tcp_queue_ooseq,false);
 if(variant==='pcmqueue') {
  assert.equal(m.opus_pcm_queue,true);assert.equal(m.opus_packet_dispatcher,'c-leased');
  assert.equal(m.opus_pcm_stack_bytes,1536);
 }
 assert.equal(m.opus_benchmark,false);assert.equal(m.tone_test,false);
 assert.equal(m.freertos_runtime_stats,false);assert.equal(m.i2s,true);assert.equal(m.data_gpio,3);
 let elf=zlib.gunzipSync(fs.readFileSync(path.join(directory,'base.elf.gz')));
 const original=Buffer.from(elf),touched=new Set();
 assert.equal(hash(elf),p.base_elf_sha256);
 for(const r of p.records){
  const old=path.join(root,'firmware/development',r.variant);
  assert.equal(sourceHash(path.join(old,'patches.s')),r.source_sha256_lf);
  assert.equal(sourceHash(path.join(old,'preflight.json')),r.original_proof_sha256_lf);
  for(const x of r.patches){const o=frozen.offsetAt(elf,x.address,x.bytes);for(let i=0;i<x.bytes;i++)touched.add(o+i);}
  elf=frozen.patchElf(elf,r.patches);
 }
 assert.equal(hash(elf),p.candidate_elf_sha256);
 assert.deepEqual(elf,zlib.gunzipSync(fs.readFileSync(path.join(directory,'app.elf.gz'))));
 for(let i=0;i<elf.length;i++)if(!touched.has(i))assert.equal(elf[i],original[i]);
 assert.deepEqual(p.after.sections,p.before.sections);
 assert.deepEqual(p.after.function_sizes,p.before.function_sizes);
 for(const name of f.names)assert.deepEqual(p.after.functions[name].graph,p.accepted.functions[name].graph);
 assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 const app=fs.readFileSync(path.join(directory,'app.bin'));
 assert.equal(hash(app),m.app_sha256);assert.equal(app.length,m.bytes);
 for(const segment of inspectImage(app).segments){
  const s=sections(elf).find(s=>s.type===1&&segment.address>=s.address&&segment.address<s.address+s.bytes);
  assert.ok(s);const skip=s.name==='.flash.rodata'?8:0;
  const offset=s.offset+segment.address-s.address+skip;
  const bytes=Math.min(segment.bytes,s.bytes-(segment.address-s.address)-skip);
  assert.equal(hash(app.subarray(segment.offset,segment.offset+bytes)),hash(elf.subarray(offset,offset+bytes)),s.name);
  assert.ok(segment.bytes-bytes<=3);assert.ok(app.subarray(segment.offset+bytes,segment.offset+segment.bytes).every(b=>b===0));
 }
});

}
test('rebase rejects path traversal and overwriting its input profile',()=>{
 for(const options of [{baseVariant:'../bad',variant:'test'},{baseVariant:'test',variant:'../bad'},{baseVariant:'same',variant:'same'}])
  assert.throws(()=>f.generate(options),/Distinct safe variant names/);
});
