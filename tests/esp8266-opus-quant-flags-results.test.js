const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'firmware/development/esp8266-opus-quant-flags-candidate-v1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),result=()=>read(path.join(dir,'comparison.json'));
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');

test('all30 physical attempts match hashes, PCM and confirmed OTA slots',()=>{
 const r=result(),seen=new Set(),fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const group of ['before','candidate','after']){
  assert.equal(r.inputs[group].length,10);const ota=read(path.join(dir,'ota-'+group+'.json'));
  assert.equal(ota.pass,true);assert.equal(ota.sha256,r.pair.manifests[group==='candidate'?'candidate':'control'].app_sha256);
  for(const item of r.inputs[group]){
   assert.ok(!seen.has(item.file));seen.add(item.file);const bytes=fs.readFileSync(path.join(root,item.file));
   assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),item.sha256);
   validateRun(JSON.parse(bytes),fixtures,ota.after.app_address);
  }
 }
 assert.equal(seen.size,30);assert.equal(r.pair.proof.static_ram_delta,0);assert.equal(r.pair.proof.stack_delta,0);
});
test('medians, outliers and speed/75-percent gates reproduce from every saved attempt',()=>{
 const r=result(),runs=group=>r.inputs[group].map(i=>read(path.join(root,i.file)));
 const a=compare(runs('before'),runs('candidate')),a2=compare(runs('after'),runs('candidate'));
 assert.deepEqual(r.initial,a);assert.deepEqual(r.repeated,a2);
 const first=selectHighBitrate(a.cases),last=selectHighBitrate(a2.cases);
 assert.deepEqual(r.selection,{initial:first,repeated:last});
 assert.equal(r.accepted_for_experimental_asm,first.accepted_for_experimental_asm&&last.accepted_for_experimental_asm);
 assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(a.cases,75));
});
test('terminal benchmark is followed by ordinary-radio OTA and HTTP/WS/playlist responses',()=>{
 const before=read(path.join(dir,'before-restore.json'));assert.equal(before.state,3);assert.equal(before.error,0);
 const ota=read(path.join(dir,'ota-restore.json'));
 const ordinary=read(path.join(root,'firmware/development/esp8266-opus-live-asm-heapreserve-20260918/manifest.json'));
 assert.equal(ota.pass,true);assert.equal(ota.sha256,ordinary.app_sha256.toLowerCase());
 assert.equal(ota.upload.http,200);assert.equal(ota.upload.body,'OK');assert.notEqual(ota.before.app_address,ota.after.app_address);
 const ui=read(path.join(dir,'restored-webui.json'));
 assert.equal(ui.status.app_address,ota.after.app_address);assert.equal(ui.status.firmware,'esp8266-native');
 assert.equal(ui.status.playing,false);assert.equal(ui.status.error,'');assert.ok(ui.audio);
 assert.equal(ui.index.value,'getindex=1');assert.ok(ui.index.messages.length>0);
 assert.ok(ui.index.messages.some(m=>m.payload?.some(p=>p.id==='playerwrap'&&p.value==='stopped')));
 assert.equal(ui.playlist.http,200);assert.equal(ui.playlist.wire_bytes,13016);
 assert.equal(ui.playlist.wire_sha256,'79b401c4d433e39ab1134a9d0776f62eea888eedffaa79c3a35851ae2fac5185');
});
