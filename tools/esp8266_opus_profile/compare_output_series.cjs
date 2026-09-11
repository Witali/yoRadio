// Compare complete attempted series, including discontinuities and low RAM.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {classify}=require('./classify_output_run.cjs');
const {stats}=require('./compare_raw.cjs');
const {sha256}=require('./fixtures.cjs');
const {targetEvidence}=require('./compare_publication.cjs');
const {root}=require('./build_host.cjs');
const maybeStats=values=>values.length?stats(values):null;
function summarize(reports) {
  assert.ok(reports.length>=10,'At least ten attempted runs required');
  const attempted=reports.map((r,i)=>({attempt:i+1,...classify(r)}));
  const completed=reports.map((r,i)=>({r,attempt:i+1})).filter(({r})=>r.final.state===3);
  const fixtures=reports.find(r=>r.fixtures)?.fixtures;
  assert.ok(fixtures?.fixtures?.length,'No explicit fixtures');
  for(const r of reports)assert.deepEqual(r.fixtures,fixtures,'Fixture identity changed');
  const cases=fixtures.fixtures.map((f,i)=>{
    const rows=completed.map(({r,attempt})=>({attempt,item:r.final.results[i],value:classify(r).cases[i]}));
    const timed=rows.filter(({item})=>['samples','pipeline_wall_us','pipeline_task_us','wall_us','output_wall_us','max_wall_us','max_output_us']
      .every(k=>Number.isSafeInteger(item[k])&&item[k]>=0) && item.samples>0 &&
      item.pipeline_wall_us>0 && item.pipeline_wall_us<3600000000 &&
      item.pipeline_task_us<=item.pipeline_wall_us && item.max_wall_us<0x80000000 && item.max_output_us<0x80000000);
    return {name:f.name,completed:rows.length,continuous:rows.filter(r=>r.value.pass).length,
      low_ram_attempts:rows.filter(r=>r.item.min_dram<4096).map(r=>r.attempt),
      invalid_timing_attempts:rows.filter(r=>!timed.includes(r)).map(r=>r.attempt),
      pipeline_cpu_budget_percent:maybeStats(timed.map(r=>r.value.pipeline_cpu_budget_percent)),
      decode_wall_budget_percent:maybeStats(timed.map(r=>r.value.decode_wall_budget_percent)),
      dma_misses:maybeStats(rows.map(r=>r.item.dma_misses)),
      pcm_elapsed_ratio:maybeStats(timed.map(r=>r.value.ratio)),
      min_dram:maybeStats(rows.map(r=>r.item.min_dram)),
      max_decode_call_us:maybeStats(timed.map(r=>r.item.max_wall_us)),
      stack_free_lifetime:maybeStats(rows.map(r=>r.item.stack_free_lifetime))};
  });
  return {attempted,completed:completed.length,cases,
    observation_errors:reports.flatMap((r,i)=>(r.snapshots||[]).filter(s=>s.error).map(s=>({attempt:i+1,error:s.error}))),
    device_failures:attempted.filter(a=>!a.completed),
    global_min_heap:maybeStats(reports.map(r=>r.after?.data?.min_heap).filter(Number.isFinite)),
    all_observed_gates_pass:completed.length===reports.length && cases.every(c=>c.continuous===reports.length &&
      !c.low_ram_attempts.length&&!c.invalid_timing_attempts.length) && reports.every(r=>r.after.data.min_heap>=4096)};
}
function matched(a,b) {
  assert.equal(a.opus_pcm_publish,false);assert.equal(b.opus_pcm_publish,true);
  for(const m of [a,b]){assert.equal(m.opus_benchmark_output,true);assert.equal(m.diagnostic,true);}
  for(const k of new Set([...Object.keys(a),...Object.keys(b)]))
    if(!['opus_pcm_publish','built_utc','bytes','app_sha256'].includes(k))assert.deepEqual(b[k],a[k],k);
}
function load(directory) {
  const read=file=>fs.readFileSync(path.join(directory,file),'utf8').replace(/^\uFEFF/,'');
  const manifest=JSON.parse(read('manifest.json')),app=fs.readFileSync(path.join(directory,'app.bin'));
  assert.equal(sha256(app),manifest.app_sha256.toLowerCase());assert.equal(app.length,manifest.bytes);
  const files=fs.readdirSync(directory).filter(f=>/^attempt[1-9]\d*\.json$/.test(f))
    .sort((a,b)=>Number(a.match(/\d+/)[0])-Number(b.match(/\d+/)[0]));
  const inputs=files.map((file,i)=>{
    assert.equal(file,`attempt${i+1}.json`,'Attempt omitted');
    const text=read(file);return {file,sha256_lf:sha256(Buffer.from(text.replace(/\r\n/g,'\n'))),report:JSON.parse(text)};
  });
  return {manifest,inputs:inputs.map(({report,...value})=>value),...summarize(inputs.map(i=>i.report))};
}
function compare(a,b,out) {
  const reference=load(a),candidate=load(b);matched(reference.manifest,candidate.manifest);
  assert.equal(reference.attempted.length,candidate.attempted.length);
  const target={before:targetEvidence(path.join(root,'.build',path.basename(a))),
    after:targetEvidence(path.join(root,'.build',path.basename(b)))};
  assert.equal(target.before.isr_section_sha256,target.after.isr_section_sha256);
  for(const k of Object.keys(target.before.sections).filter(k=>!k.startsWith('.flash')))
    assert.equal(target.before.sections[k],target.after.sections[k],k);
  const result={scope:'Own flash packets -> Opus -> PDM/DMA, Wi-Fi/WebUI enabled; pipeline CPU includes hash/output/charged ISR. Not pure decoder CPU. All attempted runs retained. Sequential A/B.',
    reference,candidate,target,qualified_candidate:candidate.all_observed_gates_pass,
    note:'Observed RAM floor is 4096B. Sampling is not a worst-case memory proof; a completed run is not automatically continuous audio.'};
  fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({off:reference.cases,on:candidate.cases,qualified_candidate:result.qualified_candidate},null,2));
  return result;
}
module.exports={summarize,matched,compare};
if(require.main===module){const [a,b,out]=process.argv.slice(2);assert.ok(a&&b&&out);compare(a,b,out);}
