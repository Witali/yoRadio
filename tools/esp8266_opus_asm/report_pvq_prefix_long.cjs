// Fresh raw A/B/A for the fixed-address PVQ packed prefix search experiment; retain every attempt.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root}=require('./export.cjs'),f=require('./pvq_prefix_long.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs'),{evaluateRawCpuTarget}=require('./cpu_target.cjs');
const dest=f.art('candidate'),experiment=path.join(root,'.build/opus-pvq-prefix-long-board-20260919');
function assertCompleteRun(r){
 assert.ok(r.before?.data&&r.after?.data,'Incomplete run: both application-slot snapshots required');
 assert.equal(r.final?.state,3,'Incomplete run: terminal decoder state required');
 assert.equal(r.final.error,0);assert.ok(!r.error,r.error);
 assert.equal(r.comparison?.length,5,'Incomplete run: PCM comparisons required');
}
function report(){
 // The producer writes intermediate JSON. Validate completion before either
 // expensive proof verification or immutable archival; do not freeze a partial run.
 for(const group of['before','candidate','after'])for(let i=1;i<=10;i++)
  assertCompleteRun(f.read(path.join(experiment,group,'run'+i+'.json')));
 const pair=f.verifyPair(),groups={},fixtures=f.read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const name of['before','candidate','after']){
  const ota=f.read(path.join(experiment,'ota-'+name+'.json'));
  assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  const rows=archive(path.join(experiment,name),path.join(dest,name));assert.equal(rows.length,10);
  for(const row of rows)validateRun(row.report,fixtures,ota.after.app_address);
  groups[name]=rows;fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report));
 const repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const selection={initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)};
 const result={pair,initial,repeated,selection,
  accepted_for_experimental_asm:selection.initial.accepted_for_experimental_asm&&selection.repeated.accepted_for_experimental_asm,
  inputs:Object.fromEntries(Object.entries(groups).map(([name,rows])=>[name,rows.map(({report,...row})=>row)])),
  scope:'All30 independent A/B/A attempts at15s polling. RAM packets, raw CPU, CPU160/QIO40; no output/function/stage profilers. Not live qualification.',
  current_cpu_target:evaluateRawCpuTarget(initial.cases,75)};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median})));
 console.log(JSON.stringify({selection,accepted:result.accepted_for_experimental_asm,target:result.current_cpu_target}));return result;
}
module.exports={report,experiment,assertCompleteRun};if(require.main===module)report();
