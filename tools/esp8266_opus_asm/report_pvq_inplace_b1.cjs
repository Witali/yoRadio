// Complete A/B/A only; never filter bad attempts or replace observations.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs'),f=require('./pvq_inplace_b1.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {assertCompleteRun}=require('./report_pvq_n3_diff.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs'),{evaluateRawCpuTarget}=require('./cpu_target.cjs');
const experiment=path.join(root,'.build/opus-inplace-b1-board'),dest=f.art('candidate');
function saveEvidence(from,to){
 const b=fs.readFileSync(from);fs.mkdirSync(path.dirname(to),{recursive:true});
 if(fs.existsSync(to))assert.equal(hash(fs.readFileSync(to)),hash(b),'Do not overwrite evidence');else fs.copyFileSync(from,to);
 return{file:path.relative(root,to).replaceAll('\\','/'),sha256:hash(b)};
}
function report(){
 for(const group of['before','candidate','after'])for(let i=1;i<=10;i++)assertCompleteRun(f.read(path.join(experiment,group,'run'+i+'.json')));
 const pair=f.verifyPair(),groups={},fixtures=f.read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 const evidence=[];
 for(const name of['before','candidate','after']){
  const otaFile=path.join(experiment,'ota-'+name+'.json'),ota=f.read(otaFile);
  assert.equal(ota.pass,true);assert.equal(ota.sha256,pair.manifests[name==='candidate'?'candidate':'control'].app_sha256);
  groups[name]=archive(path.join(experiment,name),path.join(dest,name));
  for(const row of groups[name])validateRun(row.report,fixtures,ota.after.app_address);
  evidence.push(saveEvidence(otaFile,path.join(dest,'ota-'+name+'.json')));
 }
 const host=f.read(path.join(root,'.build/opus-algorithm-candidates/inplace-b1/results.json'));
 assert.equal(host.passed,true);assert.equal(host.cases.length,24);for(const c of host.cases)assert.equal(c.pcm.exact,true);
 evidence.push(saveEvidence(path.join(root,'.build/opus-algorithm-candidates/inplace-b1/results.json'),path.join(dest,'host-pcm.json')));
 for(const name of['initial.json','before-restore.json','ota-restore.json','restored-webui.json'])evidence.push(saveEvidence(path.join(experiment,name),path.join(dest,name)));
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report));
 const repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const selection={initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)};
 const memory=Object.fromEntries(Object.entries(groups).map(([name,rows])=>{
  const results=rows.flatMap(r=>r.report.final.results);
  return[name,{min_dram:Math.min(...results.map(x=>x.min_dram)),stack_free_lifetime:Math.min(...results.map(x=>x.stack_free_lifetime)),
   scratch_byte_peak:Math.max(...results.map(x=>x.scratch_bytes)),scratch_word_peak:Math.max(...results.map(x=>x.scratch_words)),
   max_192_wall_us:Math.max(...results.filter(x=>x.id===4).map(x=>x.max_wall_us))}];
 }));
 const result={initial,repeated,selection,memory,evidence,
  pair:{parent_elf_sha256:pair.proof.parent_elf_sha256,candidate_elf_sha256:pair.proof.candidate_elf_sha256,manifests:pair.manifests},
  accepted_for_experimental_asm:selection.initial.accepted_for_experimental_asm&&selection.repeated.accepted_for_experimental_asm,
  inputs:Object.fromEntries(Object.entries(groups).map(([name,rows])=>[name,rows.map(({report,...row})=>row)])),
  scope:'All30 independent A/B/A attempts, 15s polling, RAM packets, CPU160/QIO40, no output/function/stage profilers. Includes outliers. Not live qualification.',
  current_cpu_target:evaluateRawCpuTarget(initial.cases,75)};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median})));
 console.log(JSON.stringify({selection,memory,accepted:result.accepted_for_experimental_asm,target:result.current_cpu_target}));return result;
}
module.exports={report,experiment,saveEvidence};if(require.main===module)report();
