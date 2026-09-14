const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
const main=path.join(root,'esp8266/rtos-sdk-native/main');
test('entropy IRAM exchange executes actual CMake guards and requires the matching control',()=>{
 const source=fs.readFileSync(path.join(main,'../components/opus_decoder/CMakeLists.txt'),'utf8');
 const begin=source.indexOf('option(YORADIO_OPUS_ENTROPY_IRAM_SWAP'),end=source.indexOf('option(YORADIO_OPUS_BANDS_TEXT_LITERALS');
 assert.ok(begin>0&&end>begin);
 const file=path.join(root,'.build/opus-entropy-iram-guard.cmake');
 fs.writeFileSync(file,'cmake_minimum_required(VERSION 3.13)\n'+source.slice(begin,end));
 const cmake='C:/Work/yoRadio/.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe';
 const required=['YORADIO_ESP8266_DIAGNOSTIC','CONFIG_YORADIO_OGG_OPUS','YORADIO_ESP8266_PDM32_IRAM',
  'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM','CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32'];
 const run=(extra=[],defaults=true)=>spawnSync(cmake,[...(defaults?required.map(n=>'-D'+n+'=ON'):[]),
  '-DYORADIO_OPUS_BACKEND=bands-tell-inline-asm',...extra,'-P',file],{encoding:'utf8'});
 assert.equal(run([],false).status,0,'off is inert');assert.equal(run(['-DYORADIO_OPUS_ENTROPY_IRAM_SWAP=ON']).status,0);
 for(const bad of [...required.map(n=>'-D'+n+'=OFF'),'-DYORADIO_OPUS_PVQ_IRAM=ON','-DYORADIO_OPUS_BACKEND=c']){
  const r=run(['-DYORADIO_OPUS_ENTROPY_IRAM_SWAP=ON',bad]);assert.notEqual(r.status,0);assert.match(r.stderr,/Entropy IRAM exchange requires/);
 }
 const fragment=fs.readFileSync(path.join(main,'../components/opus_decoder/opus_entropy_iram.lf'),'utf8').replace(/^#.*$/gm,'');
 assert.deepEqual([...fragment.matchAll(/entdec:(\S+) \(noflash_text\)/g)].map(m=>m[1]),['ec_decode','ec_dec_update','ec_dec_bit_logp']);
 assert.match(fs.readFileSync(path.join(main,'CMakeLists.txt'),'utf8'),/if\(YORADIO_ESP8266_PDM32_IRAM\)[\s\S]*list\(APPEND YORADIO_AUDIO_LDFRAGMENTS "pdm32_iram.lf"\)/);
});
test('exchanged PDM packer retains 493216 exact words and states under UBSan',()=>{
 const r=require('../tools/esp8266_audio_profile/check_pdm32_iram.cjs').checkBits({entropySwap:true});
 assert.equal(r.length,1);assert.equal(r[0].words,493216);assert.equal(r[0].passed,true);
});
test('actual linked ASM exchange preserves graphs, ISR placement and RAM budget',()=>{
 const {preflight,checkPlacement}=require('../tools/esp8266_opus_asm/entropy_iram.cjs'),p=preflight();
 assert.ok(p.static_iram_delta<=0);assert.equal(p.static_dram_delta,0);
 const b=structuredClone(p.candidate);b.sections['.iram0.text']=p.control.sections['.iram0.text']+4;
 assert.throws(()=>checkPlacement(p.control,b),/IRAM must not grow/);
 const c=structuredClone(p.candidate);c.functions.ec_decode.graph[0]='ret';
 assert.throws(()=>checkPlacement(p.control,c));
});
