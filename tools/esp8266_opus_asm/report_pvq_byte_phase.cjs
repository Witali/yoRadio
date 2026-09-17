const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root}=require('./export.cjs'),f=require('./pvq_byte_phase.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const {evaluateRawCpuTarget}=require('./cpu_target.cjs');
const dest=f.art('candidate'),experiment=path.join(root,'.build/opus-byte-phase-board-20260917'),read=f.read;
function report(){
 const pair=f.verifyPair(),groups={},fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const[name,dir]of[['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  const rows=archive(path.join(experiment,name),path.join(dest,dir));assert.equal(rows.length,10);
  for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);
  groups[name]=rows;fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report));
 const repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const result={pair,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},
  inputs:Object.fromEntries(Object.entries(groups).map(([k,rs])=>[k,rs.map(({report,...r})=>r)])),
  scope:'All30 independent frozen-layout a10 byte-phase A/B/A raw attempts retained. Packets in RAM; no output or function/stage profiler. Not live qualification.',
  current_cpu_target:evaluateRawCpuTarget(initial.cases,80),aspirational_78_cpu_target:evaluateRawCpuTarget(initial.cases,78)};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={report,experiment};if(require.main===module)report();
