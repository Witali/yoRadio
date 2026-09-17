// Offline checks for rebasing the accepted ASM chain into a new radio profile.
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/live_variant.cjs');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const frozen=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {sections,inspectImage}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
for(const [variant,input] of [['input2k',2048],['noooseq',1024],['noooseq-input2k',2048],['pcmqueue',1024],['pcmqueue-tcp',1024],['pcmqueue128',1024],['rxdiag',1024],['refill',1024],['mss1460',1024],['refillqueue',1024],['rx16queue',1024],['rx16',1024],['txdiag',1024],['noled',1024],['apppcm',1024],['apppcm2k',2048],['apppcm2k256',2048],['appdiag',2048],['dma192',2048],['clockfast',2048],['appdma512',1024]]) {
const appConsumer=variant.startsWith('app')||['dma192','clockfast'].includes(variant);
const directory=path.join(root,`firmware/development/esp8266-opus-live-asm-${variant}-20260917`);
const read=n=>JSON.parse(fs.readFileSync(path.join(directory,n),'utf8'));

test(`${variant} live profile preserves all18 accepted stages and exact loaded bytes`,()=>{
 const p=read('preflight.json'),m=read('manifest.json');
 const recipe=['rxdiag','refill','mss1460','refillqueue','rx16queue','rx16','txdiag','noled'].includes(variant)||appConsumer?'live_variant_v2.cjs':'live_variant.cjs';
 assert.equal(p.recipe_sha256_lf,sourceHash(path.join(root,'tools/esp8266_opus_asm',recipe)));
 assert.equal(p.records.length,18);
 assert.equal(m.opus_input_bytes,input);assert.equal(m.opus_scratch_bytes,6144);
 const tcpQueue=['input2k','pcmqueue-tcp','pcmqueue128','rxdiag','refill','mss1460','refillqueue','rx16queue','rx16','txdiag','noled'].includes(variant)||appConsumer;
 const config=fs.readFileSync(path.join(directory,'sdkconfig'),'utf8');
 if(variant.startsWith('rx16')) {
  assert.equal(m.wifi_rx_buffers,16);assert.equal(m.wifi_continuous_rx_buffers,16);
  assert.match(config,/^CONFIG_ESP8266_WIFI_RX_BUFFER_NUM=16\r?$/m);
  assert.match(config,/^CONFIG_ESP8266_WIFI_LEFT_CONTINUOUS_RX_BUFFER_NUM=16\r?$/m);
 }
 if(variant==='mss1460') {
  assert.equal(m.tcp_full_mss,true);assert.equal(m.tcp_mss,1460);
  assert.equal(m.tcp_window_bytes,2920);
  assert.match(config,/^CONFIG_LWIP_TCP_MSS=1460\r?$/m);
  assert.match(config,/^CONFIG_LWIP_TCP_WND_DEFAULT=2920\r?$/m);
  assert.match(config,/^CONFIG_LWIP_TCP_SND_BUF_DEFAULT=2920\r?$/m);
 }
 assert.equal(/^CONFIG_LWIP_TCP_QUEUE_OOSEQ=y\r?$/m.test(config),tcpQueue);
 // The first dated input2k manifest predates the explicit OOSEQ field.
 if(variant!=='input2k') assert.equal(m.tcp_queue_ooseq,tcpQueue);
 if(variant.startsWith('pcmqueue') || variant==='refillqueue' || variant==='rx16queue') {
  assert.equal(m.opus_pcm_queue,true);assert.equal(m.opus_packet_dispatcher,'c-leased');
  assert.equal(m.opus_pcm_stack_bytes,1536);
 }
 if(appConsumer) {
  assert.equal(m.opus_pcm_queue,true);assert.equal(m.opus_pcm_app_task,true);
  assert.equal(m.opus_pcm_stack_bytes,0);assert.equal(m.opus_packet_dispatcher,'c-leased');
  assert.equal(m.dma_words_per_buffer,variant==='appdma512'?512:variant==='apppcm2k256'?256:variant==='dma192'?192:128);
  if(variant==='clockfast') assert.equal(m.pdm32_clock_compensate,true);
 }
 if(['txdiag','noled'].includes(variant)||appConsumer) {
  assert.equal(m.sdk_rx_diag,true);assert.equal(m.wifi_rx_buffers,14);
  assert.equal(m.audio_level_led,variant==='txdiag');
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
