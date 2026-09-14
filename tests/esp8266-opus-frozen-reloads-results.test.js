const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs');
const f=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const dir=f.art('candidate');
test('all thirty frozen reload measurements are retained, exact and reproducible',()=>{
 const r=read(path.join(dir,'comparison.json')),pair=require('../tools/esp8266_opus_asm/report_frozen_reloads.cjs').verifyPair();
 assert.deepEqual(r.pair,pair);const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')),groups={};
 for(const [name,sub]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  assert.equal(r.inputs[name].length,10);assert.equal(fs.readdirSync(path.join(dir,sub)).filter(n=>/^run\d+\.json$/.test(n)).length,10);
  const ota=read(path.join(dir,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  groups[name]=r.inputs[name].map((v,i)=>{const file=path.join(root,v.file);assert.equal(file,path.join(dir,sub,'run'+(i+1)+'.json'));const b=fs.readFileSync(file);assert.equal(hash(b),v.sha256);const x=JSON.parse(b);validateRun(x,fixtures,ota.after.app_address);return x;});
 }
 assert.deepEqual(compare(groups.before,groups.candidate),r.initial);assert.deepEqual(compare(groups.after,groups.candidate),r.repeated);
 for(const k of ['initial','repeated']){assert.deepEqual(selectHighBitrate(r[k].cases),r.selection[k]);assert.equal(r.selection[k].target_192_cpu_at_most_70,false);}
 assert.equal(r.selection.initial.accepted_for_experimental_asm,false,'No joint 128/192 benefit over first control');
 const h=read(path.join(dir,'host-parent.json'));assert.equal(h.cases.length,11);assert.equal(h.passed,true);assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
});
test('ordinary firmware is restored OTA with stopped station and unchanged playlist',()=>{
 const ota=read(path.join(dir,'restore-ota.json')),before=read(path.join(dir,'initial-snapshot.json')),after=read(path.join(dir,'restore-snapshot.json')),http=read(path.join(dir,'restore-root.json'));
 const ordinary=path.join(root,'firmware/development/esp8266-opus-live512-idle3s-20260913/app.bin');
 assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(fs.readFileSync(ordinary)));assert.equal(after.status.app_address,ota.after.app_address);
 assert.equal(after.status.playing,false);assert.equal(after.status.connecting,false);assert.equal(after.status.error,'');assert.equal(after.status.station,before.status.station);
 // Snapshot contains the actual WebSocket getindex exchange and playlist body.
 assert.equal(after.index.value,'getindex=1');
 assert.equal(after.index.messages.find(m=>Number.isInteger(m.current)).current,before.index.messages.find(m=>Number.isInteger(m.current)).current);
 assert.ok(after.index.messages.some(m=>m.payload?.some(p=>p.id==='playerwrap'&&p.value==='stopped')));
 assert.deepEqual(after.playlist.wire_sha256,before.playlist.wire_sha256);assert.ok(after.playlist.wire_bytes>0);
 assert.equal(http.http,200);assert.ok(http.wire_bytes>0);assert.ok(http.ms>0);
});
