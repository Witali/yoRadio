// Recompute physical evidence, independently of the report's stored verdict.
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=file=>JSON.parse(fs.readFileSync(path.resolve(root,file),'utf8'));
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,file))).digest('hex');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');
const fixtures=read('firmware/development/esp8266-opus-asm-library/fixtures/manifest.json');
for(const kind of ['logn-word','exp2-table32','exp2-word','byte-phase']) test(kind+' physical A/B/A keeps all30 attempts, exact PCM, RAM and CPU gates',()=>{
  const dir='firmware/development/esp8266-opus-pvq-'+kind+'-candidate-v1';
  const report=read(dir+'/comparison.json'),groups={};
  assert.equal(report.pair.proof.static_ram_delta,0);
  assert.equal(report.pair.proof.stack_delta,0);
  for(const name of ['before','candidate','after']){
    const ota=read(dir+'/ota-'+name+'.json');assert.equal(ota.pass,true);
    assert.equal(ota.sha256,report.pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
    assert.equal(report.inputs[name].length,10);
    groups[name]=report.inputs[name].map(entry=>{
      assert.equal(hash(entry.file),entry.sha256);
      const run=read(entry.file);validateRun(run,fixtures,ota.after.app_address);return run;
    });
  }
  assert.equal(new Set(Object.values(report.inputs).flat().map(r=>r.sha256)).size,30);
  const initial=compare(groups.before,groups.candidate),repeated=compare(groups.after,groups.candidate);
  assert.deepEqual(report.initial,initial);assert.deepEqual(report.repeated,repeated);
  assert.deepEqual(report.selection.initial,selectHighBitrate(initial.cases));
  assert.deepEqual(report.selection.repeated,selectHighBitrate(repeated.cases));
  assert.deepEqual(report.current_cpu_target,evaluateRawCpuTarget(initial.cases,80));
  assert.deepEqual(report.aspirational_78_cpu_target,evaluateRawCpuTarget(initial.cases,78));
  const corrupt=structuredClone(groups.candidate[0]);corrupt.final.results[4].pcm_hash^=1;
  assert.throws(()=>validateRun(corrupt,fixtures,corrupt.before.data.app_address));
  assert.throws(()=>compare(groups.before,groups.candidate.slice(1)),/ten runs/);
});
test('adjacent experiments share one physical control, not an extra ten runs',()=>{
  const a=read('firmware/development/esp8266-opus-pvq-logn-word-candidate-v1/comparison.json');
  const b=read('firmware/development/esp8266-opus-pvq-exp2-table32-candidate-v1/comparison.json');
  const c=read('firmware/development/esp8266-opus-pvq-exp2-word-candidate-v1/comparison.json');
  assert.deepEqual(a.inputs.after.map(r=>r.sha256),b.inputs.before.map(r=>r.sha256));
  assert.deepEqual(b.inputs.after.map(r=>r.sha256),c.inputs.before.map(r=>r.sha256));
  const hashes=[a,b,c].flatMap(r=>Object.values(r.inputs).flat().map(x=>x.sha256));
  assert.equal(hashes.length,90);assert.equal(new Set(hashes).size,70);
});

test('byte-phase experiment restores the prior radio app, settings and playlist',()=>{
  const dir='firmware/development/esp8266-opus-pvq-byte-phase-candidate-v1';
  const before=read(dir+'/initial.json'),after=read(dir+'/restored.json');
  const ota=read(dir+'/ota-restore.json'),http=read(dir+'/restored-root.json');
  const ordinary='firmware/development/esp8266-opus-live512-idle3s-20260913';
  const manifest=read(ordinary+'/manifest.json');
  assert.equal(manifest.opus_benchmark,false);
  assert.equal(ota.pass,true);assert.equal(ota.sha256,hash(ordinary+'/app.bin'));
  assert.equal(after.status.app_address,ota.target);
  assert.equal(after.status.playing,false);assert.equal(after.status.error,'');
  assert.equal(after.status.station,before.status.station);
  assert.equal(after.playlist.wire_sha256,before.playlist.wire_sha256);
  for(const r of [before,after]){
    assert.ok(r.index.messages.some(m=>m.current===167));
    const values=r.index.messages.flatMap(m=>m.payload||[]);
    assert.ok(values.some(v=>v.id==='volume'&&v.value===100));
    assert.ok(values.some(v=>v.id==='balance'&&v.value===0));
  }
  assert.equal(http.http,200);assert.equal(http.encoding,'gzip');
  assert.equal(http.bytes,27249);
  assert.equal(http.sha256,'7fdfd886707344338e824fe30430ee327482d627c153e322f7cc2fa321989a3f');
  assert.ok(Number.isFinite(http.ms)&&http.ms>0); // One stopped sample, not a live SLA.
});
