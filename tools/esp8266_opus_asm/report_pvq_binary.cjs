// Fresh raw A/B/A for the fixed-address PVQ row binary search experiment; retain every attempt.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root}=require('./export.cjs'),f=require('./pvq_binary.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs'),{evaluateRawCpuTarget}=require('./cpu_target.cjs');
const dest=f.art('candidate'),experiment=path.join(root,'.build/opus-pvq-binary-board-20260919');
function report(){
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
module.exports={report,experiment};if(require.main===module)report();
