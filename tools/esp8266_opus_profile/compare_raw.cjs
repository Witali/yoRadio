#!/usr/bin/env node
// Strict repeated raw-codec A/B report. Includes every requested run, never
// drops slow measurements, observation errors or low-memory results.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {sha256} = require('./fixtures.cjs');

function stats(values) {
  assert.ok(values.length && values.every(Number.isFinite));
  const a = [...values].sort((x,y)=>x-y), n=a.length;
  return {min:a[0],median:n%2?a[n>>1]:(a[n/2-1]+a[n/2])/2,
    mean:a.reduce((s,v)=>s+v,0)/n,p95:a[Math.ceil(n*.95)-1],max:a[n-1]};
}
function summarize(reports) {
  assert.ok(reports.length>=10,'At least ten runs are required');
  for (const r of reports) {
    assert.ok(!r.error,r.error);assert.equal(r.final.state,3);
    assert.equal(r.final.error,0);assert.equal(r.final.physical_output,false);
    assert.equal(r.final.results.length,5);assert.equal(r.comparison.length,5);
    for (const [i,v] of r.final.results.entries()) {
      assert.equal(v.id,i);assert.equal(v.error,0);
      // These are intentionally different windows: wall surrounds decode,
      // task also includes snapshot/timer/yield bookkeeping. With little
      // preemption task can exceed wall; retain the excess, never clamp it.
      assert.ok(v.samples>0 && v.packets>0 && v.task_us>0 && v.wall_us>0);
      assert.ok(v.min_dram>0 && v.stack_free_lifetime>0);
      assert.equal(v.samples,reports[0].final.results[i].samples);
      assert.equal(v.packets,reports[0].final.results[i].packets);
      assert.equal(v.pcm_hash,reports[0].final.results[i].pcm_hash);
      assert.equal(v.scratch_bytes,reports[0].final.results[i].scratch_bytes);
      assert.equal(v.scratch_words,reports[0].final.results[i].scratch_words);
    }
  }
  return {runs:reports.length,
    timing_window_excesses:reports.flatMap((r,i)=>r.final.results.filter(v=>v.task_us>v.wall_us)
      .map(v=>({run:i+1,id:v.id,task_us:v.task_us,wall_us:v.wall_us,
        excess_us:v.task_us-v.wall_us,empty_task_us:r.final.empty_task_us??null,packets:v.packets}))),
    observation_errors:reports.flatMap((r,i)=>(r.snapshots||[]).filter(s=>s.error).map(s=>({run:i+1,error:s.error}))),
    dram_after:stats(reports.map(r=>r.final.dram_after)),
    cases:reports[0].final.results.map((first,i)=>{
      const values=reports.map(r=>r.final.results[i]);
      return {id:i,name:reports[0].comparison[i].name,samples_per_run:first.samples,
        packets_per_run:first.packets,pcm_hash:first.pcm_hash,
        scratch_bytes:first.scratch_bytes,scratch_words:first.scratch_words,
        task_budget_percent:stats(values.map(v=>v.task_us*4.8/v.samples)),
        wall_budget_percent:stats(values.map(v=>v.wall_us*4.8/v.samples)),
        maximum_call_us:stats(values.map(v=>v.max_wall_us)),
        min_dram:stats(values.map(v=>v.min_dram)),
        stack_free_lifetime:stats(values.map(v=>v.stack_free_lifetime))};
    })};
}
function compare(reference,candidate) {
  const a=summarize(reference),b=summarize(candidate);
  assert.equal(a.runs,b.runs);
  const cases=a.cases.map((v,i)=>{
    const w=b.cases[i];
    for (const k of ['id','samples_per_run','packets_per_run','pcm_hash','scratch_bytes','scratch_words'])
      assert.equal(w[k],v[k],`A/B mismatch ${v.name}: ${k}`);
    return {name:v.name,reference:v,candidate:w,
      median_task_reduction_percent:100*(1-w.task_budget_percent.median/v.task_budget_percent.median)};
  });
  return {schema_version:1,passed:true,
    scope:'Raw decoder only. Task CPU includes charged ISR/instrumentation; Wi-Fi and WebUI remain enabled. No network audio, demux, normalization or PDM. Sequential A/B, not interleaved.',
    percent_definition:'CPU budget = task microseconds / decoded audio duration * 100. Above 100 cannot sustain realtime even without output.',
    reference:a,candidate:b,cases};
}
function load(directory,count) {
  return Array.from({length:count},(_,i)=>{
    const file=path.join(directory,`run${i+1}.json`),data=fs.readFileSync(file);
    return {file:path.basename(file),sha256:sha256(data),report:JSON.parse(data)};
  });
}
function artifact(directory) {
  const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json'),'utf8'));
  assert.equal(manifest.opus_benchmark,true);assert.equal(manifest.opus_benchmark_output,false);
  const app=fs.readFileSync(path.join(directory,'app.bin'));
  assert.equal(sha256(app),manifest.app_sha256.toLowerCase());assert.equal(app.length,manifest.bytes);
  return manifest;
}
function auditAttempts(attempts,completed) {
  if(!attempts.length)return {recorded:completed.length,failed:[]};
  for(const a of attempts)assert.ok([3,4].includes(a.report.final?.state),'Unfinished attempt: '+a.file);
  const successful=attempts.filter(a=>a.report.final.state===3);
  assert.deepEqual(successful.map(a=>a.sha256),completed.map(a=>a.sha256),'Completed attempts omitted or reordered');
  return {recorded:attempts.length,failed:attempts.filter(a=>a.report.final.state===4).map(a=>({
    file:a.file,sha256:a.sha256,error:a.report.error,device_error:a.report.final.error,
    dram_before:a.report.final.dram_before,dram_after:a.report.final.dram_after}))};
}
function attemptFiles(directory) {
  return fs.readdirSync(directory).filter(f=>/^attempt[1-9]\d*\.json$/.test(f))
    .sort((a,b)=>Number(a.match(/\d+/)[0])-Number(b.match(/\d+/)[0]))
    .map(file=>{const data=fs.readFileSync(path.join(directory,file));return {file,sha256:sha256(data),report:JSON.parse(data)};});
}
function compareArtifacts(ma,mb,feature='opus_fir_flash_word') {
  assert.ok(['opus_fir_flash_word','opus_pulse_flash_word','opus_celt_decode_only'].includes(feature),'Unknown A/B switch');
  assert.equal(ma[feature],false);assert.equal(mb[feature],true);
  for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))
    if(![feature,'built_utc','app_sha256','bytes'].includes(k))
      assert.deepEqual(mb[k],ma[k],`Build settings differ: ${k}`);
}
if(require.main===module) {
  const args=process.argv.slice(2),value=(key)=>{const i=args.indexOf(key);assert.ok(i>=0,`Missing ${key}`);return args[i+1];};
  const count=args.includes('--runs')?Number(value('--runs')):10;
  assert.ok(Number.isInteger(count)&&count>=10&&count<=1000);
  const a=load(value('--reference'),count),b=load(value('--candidate'),count);
  const result=compare(a.map(v=>v.report),b.map(v=>v.report));
  const ma=artifact(value('--reference')),mb=artifact(value('--candidate'));
  const feature=args.includes('--switch')?value('--switch'):'opus_fir_flash_word';
  compareArtifacts(ma,mb,feature);
  result.artifacts={reference:ma,candidate:mb};
  result.switch=feature;
  result.attempts={reference:auditAttempts(attemptFiles(value('--reference')),a),candidate:auditAttempts(attemptFiles(value('--candidate')),b)};
  result.comparison_valid=true;
  result.passed=!result.attempts.reference.failed.length&&!result.attempts.candidate.failed.length;
  result.inputs={reference:a.map(({file,sha256})=>({file,sha256})),candidate:b.map(({file,sha256})=>({file,sha256}))};
  const output=path.resolve(value('--output'));fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  if(!result.passed)console.warn('Completed-run CPU comparison is valid, but failed attempts are retained: '+JSON.stringify(result.attempts));
  console.table(result.cases.map(c=>({name:c.name,off:c.reference.task_budget_percent.median,
    on:c.candidate.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
}
module.exports={stats,summarize,compare,compareArtifacts,auditAttempts};
