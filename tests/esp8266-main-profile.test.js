const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const {validate}=require('../tools/esp8266_opus_asm/publish_main.cjs');
const {names}=require('../tools/esp8266_opus_asm/live_variant_v2.cjs');
function fixture(){
 const m={opus_profile_stage:0,opus_input_bytes:1024,opus_scratch_bytes:6144,dma_words_per_buffer:512,i2s:true,data_gpio:3,cpu_mhz:160,flash:'QIO40',post_link_live_accepted:true,accepted_asm_variant:'esp8266-opus-ebands-final-candidate-v2',opus_backend:'bands-tell-inline-asm',app_sha256:'test'};
 for(const k of ['opus_benchmark','opus_benchmark_output','opus_function_profile','freertos_runtime_stats','opus_stream_test','opus_pcm_queue','opus_low_ram','sdk_rx_diag','tone_test','web_profile','memory_profile','spiffs_log','spiffs_log_http'])m[k]=false;
 const p={records:Array(18).fill({}),app_sha256:'test',static_ram_delta:0,stack_delta:0,after:{functions:{}},accepted:{functions:{}}};
 for(const n of names){p.after.functions[n]={graph:['ret']};p.accepted.functions[n]={graph:['ret']};}
 return {m,p};
}
test('main is accepted ASM with ordinary DMA512 and no runtime diagnostics',()=>{const {m,p}=fixture();validate(m,p,'accepted-asm');});
test('unpatched, rejected or partial chains cannot become main',()=>{
 for(const change of [m=>m.post_link_live_accepted=false,m=>m.accepted_asm_variant='rejected',m=>m.opus_backend='c']){const {m,p}=fixture();change(m);assert.throws(()=>validate(m,p,'accepted-asm'));}
 const {m,p}=fixture();p.records.pop();assert.throws(()=>validate(m,p,'accepted-asm'));
});
test('failed diagnostic output profile and workloads cannot be promoted',()=>{
 for(const key of ['opus_pcm_queue','opus_stream_test','opus_low_ram','opus_benchmark','spiffs_log_http']){const {m,p}=fixture();m[key]=true;assert.throws(()=>validate(m,p,'accepted-asm'));}
 const {m,p}=fixture();m.dma_words_per_buffer=128;assert.throws(()=>validate(m,p,'accepted-asm'));
});
test('changed graph or RAM footprint rejects publication',()=>{
 const {m,p}=fixture();p.after.functions[names[0]].graph=['bad'];assert.throws(()=>validate(m,p,'accepted-asm'));
 const x=fixture();x.p.static_ram_delta=4;assert.throws(()=>validate(x.m,x.p,'accepted-asm'));
});
test('C fallback stays explicit',()=>{const {m}=fixture();m.opus_backend='c';validate(m,null,'c');});
test('main wrapper is default and has no hardware deployment side effects',()=>{
 const s=fs.readFileSync('esp8266/rtos-sdk-native/build.ps1','utf8');assert.match(s,/\$Profile = 'accepted-asm'/);assert.match(s,/DmaBufferWords=512/);assert.match(s,/live_variant_v2.cjs/);assert.match(s,/publish_main.cjs/);assert.doesNotMatch(s,/write_flash|\/update|--command.*play=/);
});
