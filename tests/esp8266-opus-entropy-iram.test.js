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

test('extra relaxation audit preserves branches and compares full anonymous readonly data',()=>{
 const {withoutIdentityMoves,stringAt,blockAt,audit}=require('../tools/esp8266_opus_asm/audit_entropy_relaxation.cjs');
 assert.deepEqual(withoutIdentityMoves(['beqz a2, instruction:2','mov a1, a1','mov a3, a3','ret ']),['beqz a2, instruction:1','ret ']);
 assert.deepEqual(withoutIdentityMoves(['mov a1, a2','ret ']),['mov a1, a2','ret ']);
 assert.throws(()=>withoutIdentityMoves(['j instruction:1','mov a1, a1']));
 const r=audit();assert.equal(r.passed,true);assert.equal(r.names.length,19);
 const {sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
 const base=path.join(root,'.build/esp8266-opus-entropy-control-v1/yoradio_esp8266_helix_native');
 const elf=fs.readFileSync(base+'.elf'),map=fs.readFileSync(base+'.map','utf8');
 const tamper=addr=>{const b=Buffer.from(elf),s=sections(b).find(s=>s.type===1&&addr>=s.address&&addr<s.address+s.bytes);assert.ok(s);b[s.offset+addr-s.address]^=1;return b;};
 const str=r.strings.find(s=>s.kind==='string'),data=r.strings.find(s=>s.kind==='rodata');assert.ok(str&&data);
 assert.equal(stringAt(elf,str.from),str.bytes_hex_including_nul);
 assert.notEqual(stringAt(tamper(str.from),str.from),str.bytes_hex_including_nul);
 assert.equal(blockAt(elf,map,data.from).size,12);
 assert.equal(blockAt(elf,map,data.from).bytes_hex,'060000000400000003000000');
 assert.notDeepEqual(blockAt(tamper(data.from),map,data.from),blockAt(elf,map,data.from));
 assert.equal(blockAt(elf,map,data.from+4),null,'Only entire input section may be compared');
 assert.equal(stringAt(elf,0x40100000),null);
});

test('all thirty entropy-placement measurements and the rejected result remain reproducible',()=>{
 const {hash}=require('../tools/esp8266_opus_asm/export.cjs');
 const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
 const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
 const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
 const dir=path.join(root,'firmware/development/esp8266-opus-entropy-iram-v1');
 const read=p=>JSON.parse(fs.readFileSync(p));
 const r=read(path.join(dir,'comparison.json')),fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 const groups={};
 for(const [n,sub]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  assert.equal(fs.readdirSync(path.join(dir,sub)).filter(x=>/^run\d+\.json$/.test(x)).length,10);
  const ota=read(path.join(dir,'ota-'+n+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,r.proof.manifests[n==='candidate'?1:0].app_sha256.toLowerCase());
  assert.equal(r.inputs[n].length,10);
  groups[n]=r.inputs[n].map((p,i)=>{
   const file=path.join(root,p.file);assert.equal(file,path.join(dir,sub,'run'+(i+1)+'.json'));
   const bytes=fs.readFileSync(file);assert.equal(hash(bytes),p.sha256);
   const v=JSON.parse(bytes);validateRun(v,fixtures,ota.after.app_address);return v;
  });
 }
 assert.deepEqual(compare(groups.before,groups.candidate),r.initial);
 assert.deepEqual(compare(groups.after,groups.candidate),r.repeated);
 for(const n of ['initial','repeated']){
  assert.deepEqual(selectHighBitrate(r[n].cases),r.selection[n]);
  assert.equal(r.selection[n].accepted_for_experimental_asm,false);
  assert.equal(r.selection[n].target_192_cpu_at_most_70,false);
 }
 assert.equal(r.proof.static_dram_delta,0);assert.equal(r.proof.static_iram_delta,-56);
});
