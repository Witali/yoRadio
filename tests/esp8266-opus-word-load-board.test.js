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
for(const kind of ['logn-word','exp2-table32','exp2-word']) test(kind+' physical A/B/A keeps all30 attempts, exact PCM, RAM and CPU gates',()=>{
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
  assert.deepEqual(report.current_cpu_target,evaluateRawCpuTarget(initial.cases));
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
