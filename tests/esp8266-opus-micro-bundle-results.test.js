const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs'),f=require('../tools/esp8266_opus_asm/micro_bundle.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs'),{validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const read=f.read,dir=f.art('candidate');
const {evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');
test('micro-bundle physical report retains all30 attempts with exact PCM and independently checked CPU medians',()=>{
 const r=read(path.join(dir,'comparison.json')),pair=require('../tools/esp8266_opus_asm/report_micro_bundle.cjs').verifyPair();assert.deepEqual(r.pair,pair);
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')),groups={};
 for(const[name,sub]of[['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  assert.equal(r.inputs[name].length,10);assert.equal(fs.readdirSync(path.join(dir,sub)).filter(n=>/^run\d+\.json$/.test(n)).length,10);
  assert.equal(fs.readdirSync(path.join(dir,sub)).filter(n=>/^run\d+\.log$/.test(n)).length,10);
  const ota=read(path.join(dir,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  groups[name]=r.inputs[name].map((v,i)=>{const file=path.join(root,v.file);assert.equal(file,path.join(dir,sub,'run'+(i+1)+'.json'));const bytes=fs.readFileSync(file);assert.equal(hash(bytes),v.sha256);const x=JSON.parse(bytes);validateRun(x,fixtures,ota.after.app_address);return x;});
  const summary=name==='before'?r.initial.reference:name==='candidate'?r.initial.candidate:r.repeated.reference;
  for(let i=0;i<5;i++){
   const cpu=groups[name].map(x=>{const v=x.final.results[i];return 100*v.task_us/(v.samples/48000*1000000);}).sort((a,b)=>a-b);
   assert.ok(Math.abs((cpu[4]+cpu[5])/2-summary.cases[i].task_budget_percent.median)<1e-10);
   assert.equal(Math.max(...groups[name].map(x=>x.final.results[i].max_wall_us)),summary.cases[i].maximum_call_us.max);
   assert.equal(Math.min(...groups[name].map(x=>x.final.results[i].min_dram)),summary.cases[i].min_dram.min);
  }
 }
 assert.deepEqual(compare(groups.before,groups.candidate),r.initial);assert.deepEqual(compare(groups.after,groups.candidate),r.repeated);
 for(const k of['initial','repeated']){assert.deepEqual(selectHighBitrate(r[k].cases),r.selection[k]);}
 assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(r.initial.cases));assert.equal(r.current_cpu_target.maximum_percent,80);
 // All observations, including timing-window excess and HTTP errors, remain
 // in the independently re-computed compare() objects above; nothing filtered.
 const h=read(path.join(dir,'host.json'));assert.equal(h.passed,true);assert.equal(h.cases.length,24);assert.equal(h.compound.length,3);assert.ok(h.cases.some(c=>c.name==='stereo-510'));assert.ok(h.cases.every(c=>c.pcm.exact&&c.pcm.max_absolute_error===0));
});
test('micro-bundle experiment restores ordinary radio OTA with matching station, playlist, HTTP and WebSocket',()=>{
 const ota=read(path.join(dir,'restore-ota.json')),before=read(path.join(dir,'initial-snapshot.json')),after=read(path.join(dir,'restore-snapshot.json')),http=read(path.join(dir,'restore-root.json'));
 assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-live512-idle3s-20260913/app.bin'))));assert.equal(after.status.app_address,ota.after.app_address);
 assert.equal(after.status.playing,false);assert.equal(after.status.connecting,false);assert.equal(after.status.error,'');assert.equal(after.status.station,before.status.station);assert.equal(after.index.value,'getindex=1');
 assert.equal(after.index.messages.find(m=>Number.isInteger(m.current)).current,before.index.messages.find(m=>Number.isInteger(m.current)).current);
 assert.ok(after.index.messages.some(m=>m.payload?.some(p=>p.id==='playerwrap'&&p.value==='stopped')));assert.equal(after.playlist.wire_sha256,before.playlist.wire_sha256);assert.ok(after.playlist.wire_bytes>0);assert.equal(http.http,200);assert.ok(http.wire_bytes>0);assert.ok(http.ms>0);
});
