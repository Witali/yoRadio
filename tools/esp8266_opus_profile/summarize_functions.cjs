#!/usr/bin/env node
// Preserve all attempts; compare measured overhead, never subtract a guessed
// per-call cost or present instrumented self percentages as production shares.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {sha256}=require('./fixtures.cjs');
const {compare}=require('./compare_raw.cjs');
const {summarizeFunctions}=require('./function_profile_result.cjs');
const args=process.argv.slice(2);
function value(k){const i=args.indexOf(k);assert.ok(i>=0,'Missing '+k);return args[i+1];}
function load(dir){
 const files=fs.readdirSync(dir).filter(f=>/^run[1-9]\d*\.json$/.test(f))
  .sort((a,b)=>Number(a.match(/\d+/)[0])-Number(b.match(/\d+/)[0]));
 assert.ok(files.length>=10);
 return files.map((f,i)=>{assert.equal(f,`run${i+1}.json`);const data=fs.readFileSync(path.join(dir,f));
  return {file:f,sha256:sha256(data),report:JSON.parse(data)};});
}
function artifact(dir){
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json')));
 const app=fs.readFileSync(path.join(dir,'app.bin'));
 assert.equal(sha256(app),manifest.app_sha256.toLowerCase());assert.equal(app.length,manifest.bytes);
 assert.equal(manifest.diagnostic,true);assert.equal(manifest.opus_benchmark,true);
 assert.equal(manifest.opus_benchmark_output,false);return manifest;
}
const p=load(value('--profile')),c=load(value('--control'));
const pm=artifact(value('--profile-artifact')),cm=artifact(value('--control-artifact'));
assert.equal(pm.opus_function_profile,true);assert.equal(cm.opus_function_profile,false);
for(const k of new Set([...Object.keys(pm),...Object.keys(cm)]))
 if(!['opus_function_profile','opus_function_profile_coarse','app_sha256','bytes','built_utc'].includes(k))
  assert.deepEqual(pm[k],cm[k],'Build mismatch '+k);
const functions=summarizeFunctions(p.map(v=>v.report));
const overhead=compare(c.map(v=>v.report),p.map(v=>v.report));
const result={schema_version:1,created_utc:new Date().toISOString(),functions,
 measurement_warning:'Function durations and shares are instrumented, not production estimates. Wrapping very frequent symbols perturbs caller self time and flash cache. No guessed overhead correction. Cross-object calls only.',
 raw_cpu_comparison:overhead,artifacts:{profile:pm,control:cm},
 inputs:{profile:p.map(({file,sha256})=>({file,sha256})),control:c.map(({file,sha256})=>({file,sha256}))}};
const out=path.resolve(value('--output'));fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.table(functions.rows.map(r=>({function:r.name,calls_frame:r.calls_per_frame,
 mean_us:r.mean_cpu_us,max_cpu_us:r.max_cpu_us,self_percent:r.self_cpu_percent,inclusive_percent:r.inclusive_cpu_percent})));
console.table(overhead.cases.map(r=>({case:r.name,control:r.reference.task_budget_percent.median,
 profiled:r.candidate.task_budget_percent.median,overhead_percent:-r.median_task_reduction_percent})));
