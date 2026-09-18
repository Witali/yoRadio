const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),dir='firmware/development/esp8266-opus-ebands-quant-candidate-v1';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8')),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs'),{validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs'),{evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');
test('quant pair result recomputes all30 trials, including outliers, and the75% gate',()=>{
 const r=read(dir+'/comparison.json'),groups={},fixtures=read('firmware/development/esp8266-opus-asm-library/fixtures/manifest.json');
 for(const name of['before','candidate','after']){
  const ota=read(dir+'/ota-'+name+'.json');assert.equal(ota.pass,true);assert.equal(ota.sha256,r.pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);assert.equal(r.inputs[name].length,10);
  groups[name]=r.inputs[name].map(e=>{assert.equal(hash(e.file),e.sha256);const run=read(e.file);validateRun(run,fixtures,ota.after.app_address);return run;});
 }
 assert.equal(new Set(Object.values(r.inputs).flat().map(x=>x.sha256)).size,30);
 const initial=compare(groups.before,groups.candidate),repeated=compare(groups.after,groups.candidate);assert.deepEqual(r.initial,initial);assert.deepEqual(r.repeated,repeated);
 assert.deepEqual(r.selection.initial,selectHighBitrate(initial.cases));assert.deepEqual(r.selection.repeated,selectHighBitrate(repeated.cases));assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(initial.cases,75));
 assert.equal(r.pair.proof.static_ram_delta,0);assert.equal(r.pair.proof.stack_delta,0);assert.throws(()=>compare(groups.before,groups.candidate.slice(1)),/ten runs/);
 assert.ok(groups.before[3].final.results[4].task_us*4.8/groups.before[3].final.results[4].samples>90,'Control outlier must not disappear');
 assert.equal(Math.min(...groups.candidate.flatMap(x=>x.final.results.map(r=>r.min_dram))),904);
 const bad=structuredClone(groups.candidate[0]);bad.final.results[4].pcm_hash^=1;assert.throws(()=>validateRun(bad,fixtures,bad.before.data.app_address));
});
test('ordinary accepted ASM radio restored over OTA, not the rejected raw candidate',()=>{
 const initial=read(dir+'/initial-readonly.json'),after=read(dir+'/restored.json'),ota=read(dir+'/ota-restore.json'),ordinary='firmware/development/esp8266-opus-live-asm-quietclock-20260917';
 const m=read(ordinary+'/manifest.json');assert.equal(m.opus_benchmark,false);assert.equal(m.data_gpio,3);assert.equal(m.i2s,true);
 assert.equal(m.accepted_asm_variant,'esp8266-opus-ebands-final-candidate-v2');assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(ordinary+'/app.bin'));assert.equal(after.status.app_address,ota.target);
 assert.equal(after.status.playing,false);assert.equal(after.status.error,'');assert.equal(after.status.station,initial.status.station);
 assert.ok(after.command.messages.length>0,'WebSocket must respond after restore');
});
