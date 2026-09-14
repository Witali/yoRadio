// Archive every raw physical attempt, including outliers. No live-audio claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root}=require('./export.cjs'),{archive}=require('./report_bands.cjs');
const {audit,control,candidate}=require('./audit_partition_decode.cjs');
const {validateRun}=require('./report_small_div_tail.cjs'),{compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs');
const experiment=path.join(root,'.build/opus-partition-decode-board'),dest=path.join(root,'firmware/development',candidate);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function report(){
 const proof=audit(),groups={};const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,subdir]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,proof.manifests[name==='candidate'?1:0].app_sha256.toLowerCase());
  const rows=archive(path.join(experiment,name),path.join(dest,subdir));for(const r of rows)validateRun(r.report,fixtures,ota.after.app_address);groups[name]=rows;
  fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(groups.before.map(r=>r.report),groups.candidate.map(r=>r.report)),repeated=compare(groups.after.map(r=>r.report),groups.candidate.map(r=>r.report));
 const result={proof,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:Object.fromEntries(Object.entries(groups).map(([k,rs])=>[k,rs.map(({report,...r})=>r)])),scope:'All30 raw A/B/A retained; output/function/stage profiling OFF; not live qualification'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));console.log(JSON.stringify(result.selection));return result;
}
module.exports={report,experiment,control,candidate};if(require.main===module)report();
