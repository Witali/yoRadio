// Publish only a verified complete radio; never promote a raw benchmark.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function validate(m,p,profile){
 assert.ok(['accepted-asm','c'].includes(profile));
 for(const k of ['opus_benchmark','opus_benchmark_output','opus_function_profile','freertos_runtime_stats','opus_stream_test','opus_pcm_queue','opus_low_ram','sdk_rx_diag','tone_test','web_profile','memory_profile','spiffs_log','spiffs_log_http'])
   assert.equal(m[k],false,k+' must stay disabled');
 assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_input_bytes,1024);assert.equal(m.opus_scratch_bytes,6144);
 assert.equal(m.dma_words_per_buffer,512);assert.equal(m.i2s,true);assert.equal(m.data_gpio,3);
 assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');
 if(profile==='accepted-asm'){
  assert.equal(m.post_link_live_accepted,true);assert.equal(m.accepted_asm_variant,'esp8266-opus-ebands-final-candidate-v2');
  assert.equal(m.opus_backend,'bands-tell-inline-asm');assert.equal(p.records.length,18);
  assert.equal(p.app_sha256,m.app_sha256);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
  for(const name of require('./live_variant_v2.cjs').names)assert.deepEqual(p.after.functions[name].graph,p.accepted.functions[name].graph,name);
 }else assert.equal(m.opus_backend,'c');
}
function main(source,variant,profile){
 assert.ok(/^[a-zA-Z0-9_-]+$/.test(source)&&/^[a-zA-Z0-9_-]+$/.test(variant)&&source!==variant);
 const from=path.join(root,'firmware/development',source),to=path.join(root,'firmware/development',variant);
 const m=read(path.join(from,'manifest.json')),p=profile==='accepted-asm'?read(path.join(from,'preflight.json')):null;
 validate(m,p,profile);
 const app=fs.readFileSync(path.join(from,'app.bin'));assert.equal(hash(app),m.app_sha256.toLowerCase());assert.equal(app.length,m.bytes);assert.ok(app.length<=0xf0000);
 fs.mkdirSync(to,{recursive:true});
 for(const name of profile==='accepted-asm'?['app.bin','manifest.json','preflight.json','sdkconfig','app.elf.gz','base.elf.gz','packaging.log']:['app.bin','manifest.json','sdkconfig'])fs.copyFileSync(path.join(from,name),path.join(to,name));
 const selection={profile,default_firmware:true,accepted_chain:profile==='accepted-asm'?18:0,
   source_artifact:source,source_revision:m.source_revision,app_sha256:m.app_sha256,
   build_only:true,live_qualified:false,known_limitations:'Opus live continuity still unqualified; prior DMA128 diagnostic profile failed station tests. Ordinary DMA512 retained.'};
 fs.writeFileSync(path.join(to,'selection.json'),JSON.stringify(selection,null,2)+'\n');
 fs.writeFileSync(path.join(to,'CHANGELOG.md'),'# '+new Date().toISOString().slice(0,10)+' — ESP8266 main radio\n\n'+
   'Source: `'+m.source_revision+'`. Profile: `'+profile+'`. SHA256: `'+m.app_sha256+'`.\n\n'+
   'MP3 Helix SSO, AAC and Opus. I2S PDM32 GPIO3, CPU160/QIO40, DMA 2×512 words. '+
   'Accepted ASM chain: '+selection.accepted_chain+' stages. No benchmark, Opus PCM queue, reduced scratch or stream profiling. '+
   'Build verified, not flashed or qualified for uninterrupted live Opus playback.\n');
 console.log(JSON.stringify(selection));
}
module.exports={validate};if(require.main===module)main(...process.argv.slice(2));
