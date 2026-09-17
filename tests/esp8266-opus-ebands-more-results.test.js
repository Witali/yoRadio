const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),dir='firmware/development/esp8266-opus-ebands-more-candidate-v1';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8')),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs'),{validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs'),{evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');
test('eBands A/B/A recomputes every raw trial and the unrounded75% gate',()=>{
 const r=read(dir+'/comparison.json'),groups={},fixtures=read('firmware/development/esp8266-opus-asm-library/fixtures/manifest.json');
 for(const name of['before','candidate','after']){
  const ota=read(dir+'/ota-'+name+'.json');assert.equal(ota.pass,true);assert.equal(ota.sha256,r.pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);assert.equal(r.inputs[name].length,10);
  groups[name]=r.inputs[name].map(e=>{assert.equal(hash(e.file),e.sha256);const run=read(e.file);validateRun(run,fixtures,ota.after.app_address);return run;});
 }
 assert.equal(new Set(Object.values(r.inputs).flat().map(x=>x.sha256)).size,30);
 const initial=compare(groups.before,groups.candidate),repeated=compare(groups.after,groups.candidate);assert.deepEqual(r.initial,initial);assert.deepEqual(r.repeated,repeated);
 assert.deepEqual(r.selection.initial,selectHighBitrate(initial.cases));assert.deepEqual(r.selection.repeated,selectHighBitrate(repeated.cases));assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(initial.cases,75));
 assert.equal(r.pair.proof.static_ram_delta,0);assert.equal(r.pair.proof.stack_delta,0);assert.throws(()=>compare(groups.before,groups.candidate.slice(1)),/ten runs/);
 const bad=structuredClone(groups.candidate[0]);bad.final.results[4].pcm_hash^=1;assert.throws(()=>validateRun(bad,fixtures,bad.before.data.app_address));
 const fast=structuredClone(groups.candidate[0]);fast.interval_ms=1500;assert.throws(()=>validateRun(fast,fixtures,fast.before.data.app_address));
});
test('Additional eBands experiment restores the previous ordinary image with saved settings and playlist',()=>{
 const before=read(dir+'/initial.json'),after=read(dir+'/restored.json'),ota=read(dir+'/ota-restore.json'),ordinary='firmware/development/esp8266-opus-live512-idle3s-20260913';
 assert.equal(read(ordinary+'/manifest.json').opus_benchmark,false);assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(ordinary+'/app.bin'));assert.equal(after.status.app_address,ota.target);
 assert.equal(after.status.playing,false);assert.equal(after.status.error,'');assert.equal(after.status.station,before.status.station);assert.equal(after.playlist.wire_sha256,before.playlist.wire_sha256);
 const values=r=>r.index.messages.flatMap(m=>m.payload||[]);for(const id of['volume','balance'])assert.deepEqual(values(after).filter(v=>v.id===id),values(before).filter(v=>v.id===id));assert.ok(after.index.messages.some(m=>m.current===167));
});
