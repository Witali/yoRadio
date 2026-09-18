const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const dir=path.join(__dirname,'../firmware/development/esp8266-opus-live-asm-current-20260918');
const read=name=>JSON.parse(fs.readFileSync(path.join(dir,name),'utf8').replace(/^\uFEFF/,''));

test('ordinary radio contains the full accepted 18-stage ASM chain and exact final image',()=>{
 const m=read('manifest.json'),p=read('preflight.json'),b=fs.readFileSync(path.join(dir,'app.bin'));
 const hash=crypto.createHash('sha256').update(b).digest('hex');
 assert.equal(hash,m.app_sha256);assert.equal(hash,p.app_sha256);assert.equal(b.length,m.bytes);
 assert.ok(b.length<=0xf0000);assert.equal(p.records.length,18);
 assert.equal(p.acceptedVariant,'esp8266-opus-ebands-final-candidate-v2');
 assert.equal(p.records.at(-1).variant,p.acceptedVariant);
 assert.ok(p.records.every(x=>!/quant-(decode|flags|locals)|allocation-decode|ebands-src/.test(x.variant)));
 for(const [name,fn]of Object.entries(p.after.functions))assert.deepEqual(fn.graph,p.accepted.functions[name].graph,name);
 assert.deepEqual(p.before.sections,p.after.sections);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
 const v=read('build-validation.json');assert.equal(v.app_sha256,hash);assert.equal(v.passed,true);
 for(const name of ['.iram0.vectors','.iram0.text','.iram0.bss','.dram0.data','.dram0.bss'])
  assert.equal(v.current_sections[name],v.previous_sections[name],name);
});

test('radio profile preserves physical PDM and excludes benchmark and flash logging',()=>{
 const m=read('manifest.json');assert.equal(m.source_revision,'a82a4551bb4579e97ff0dd84ff7f1a06ab928db1');
 for(const key of ['opus_benchmark','opus_benchmark_output','opus_function_profile','freertos_runtime_stats','spiffs_log','spiffs_log_http','audio_level_led'])assert.equal(m[key],false,key);
 for(const key of ['i2s','post_link_live_accepted','opus_word_asm','opus_pcm_queue','opus_pcm_app_task','pdm32_clock_compensate'])assert.equal(m[key],true,key);
 assert.equal(m.cpu_mhz,160);assert.equal(m.flash,'QIO40');assert.equal(m.data_gpio,3);
 assert.equal(m.opus_input_bytes,2048);assert.equal(m.opus_scratch_bytes,6144);
 assert.equal(m.dma_buffers,2);assert.equal(m.dma_words_per_buffer,128);
});

test('OTA boot is confirmed independently and HTTP/WS preserve the playlist',()=>{
 const m=read('manifest.json'),o=read('ota.json'),a=read('after-ota.json'),i=read('initial.json');
 assert.equal(o.sha256,m.app_sha256);assert.equal(o.pass,true);
 assert.equal(o.upload.http,200);assert.equal(o.upload.body,'OK');
 assert.notEqual(o.before.app_address,o.target);assert.equal(o.after.app_address,o.target);
 assert.equal(a.status.app_address,o.target);assert.equal(a.status.firmware,'esp8266-native');
 assert.equal(a.status.error,'');assert.equal(a.status.playing,false);
 assert.equal(a.playlist.http,200);assert.equal(a.playlist.wire_sha256,i.playlist.wire_sha256);
 assert.equal(a.index.value,'getindex=1');assert.ok(a.index.messages.some(x=>x.payload?.some(p=>p.id==='playerwrap'&&p.value==='stopped')));
});

test('playback failure remains recorded and final cleanup leaves the new app stopped',()=>{
 const q=read('quiet.json'),end=read('final-cleanup.json');
 const {analyze}=require('../tools/esp8266_opus_profile/run_quiet_window.cjs');
 assert.equal(q.no_runner_requests_ms,65000);assert.deepEqual(q.result,analyze(q.window));
 assert.equal(q.result.pass,false);assert.equal(q.window.underruns,1419);
 assert.match(read('play.json').error,/request timeout/);assert.match(read('stop.json').error,/WebSocket command timeout/);
 assert.equal(read('final.json').status.error,'CONNECTION ERROR');
 assert.equal(end.status.app_address,read('ota.json').target);assert.equal(end.status.playing,false);assert.equal(end.status.error,'');
 assert.equal(end.playlist.wire_sha256,read('initial.json').playlist.wire_sha256);
 assert.equal(read('stop-cleanup.json').command.value,'stop=1');
});
