// Summarize one selected-stage series; never compare different polling/source
// profiles as a speedup. Raw failures and low-RAM observations remain visible.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {stats,summarize}=require('./compare_raw.cjs');
const {analyzeStage}=require('./stage_profile_result.cjs');
const {sha256}=require('./fixtures.cjs');
function run(directory,output) {
  const manifest=JSON.parse(fs.readFileSync(path.join(directory,'manifest.json')));
  const app=fs.readFileSync(path.join(directory,'app.bin'));
  assert.equal(sha256(app),manifest.app_sha256.toLowerCase());assert.equal(app.length,manifest.bytes);
  assert.equal(manifest.opus_benchmark,true);assert.equal(manifest.opus_benchmark_output,false);
  const files=fs.readdirSync(directory).filter(n=>/^run[1-9]\d*\.json$/.test(n))
    .sort((a,b)=>Number(a.match(/\d+/)[0])-Number(b.match(/\d+/)[0]));
  assert.ok(files.length>=10,'Keep at least ten attempts');
  const entries=files.map(file=>{const data=fs.readFileSync(path.join(directory,file));return {file,sha256:sha256(data),report:JSON.parse(data)};});
  const failures=entries.filter(e=>e.report.error||e.report.final?.state!==3);
  const good=entries.filter(e=>!failures.includes(e));
  const report={scope:'One inclusive-wall stage profile, not a speed comparison or continuity proof',
    artifact:manifest,
    attempts:entries.map(e=>({file:e.file,sha256:e.sha256,error:e.report.error||null,state:e.report.final?.state??null})),
    all_attempts_complete:failures.length===0,successful:good.length,failed:failures.length};
  if(good.length>=10) {
    const runs=good.map(e=>e.report);report.raw=summarize(runs);
    const first=runs[0].final;
    assert.equal(first.profile_stage,manifest.opus_profile_stage);
    for(const r of runs){assert.equal(r.final.profile_stage,first.profile_stage);assert.equal(r.interval_ms,runs[0].interval_ms);}
    report.profile_stage=first.profile_stage;report.interval_ms=runs[0].interval_ms;
    report.clock_pair_ticks_min=stats(runs.map(r=>r.final.clock_pair_ticks_min));
    report.clock_pair_ticks_max=stats(runs.map(r=>r.final.clock_pair_ticks_max));
    report.stages=first.results.map((_,i)=>{
      const measured=runs.map(r=>analyzeStage(r.final,r.final.results[i]));
      return {name:runs[0].comparison[i].name,scope:measured[0].name,
        calls:stats(runs.map(r=>r.final.results[i].stage_calls)),
        inclusive_wall_percent:stats(measured.map(m=>m.wall_percent_of_decode)),
        max_scope_us:stats(measured.map(m=>m.max_wall_us))};
    });
    report.low_ram=runs.flatMap((r,index)=>r.final.results.filter(v=>v.min_dram<4096)
      .map(v=>({run:good[index].file,id:v.id,min_dram:v.min_dram})));
    report.ram_reserve_4096_pass=report.low_ram.length===0;
  }
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report.stages?.map(s=>({name:s.name,percent:s.inclusive_wall_percent.median,max_us:s.max_scope_us.max})),null,2));
  return report;
}
if(require.main===module)run(...process.argv.slice(2));module.exports={run};
