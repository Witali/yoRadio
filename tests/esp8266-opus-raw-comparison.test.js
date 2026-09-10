const test=require('node:test'),assert=require('node:assert/strict');
const {stats,compare,compareArtifacts,auditAttempts}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
test('attempt audit retains a terminal failure and forbids dropping completed or unfinished attempts',()=>{
  const good={file:'attempt1.json',sha256:'a',report:{final:{state:3}}};
  const bad={file:'attempt2.json',sha256:'b',report:{error:'allocation',final:{state:4,error:-9001,dram_before:16000,dram_after:16000}}};
  const last={file:'attempt3.json',sha256:'c',report:{final:{state:3}}};
  const r=auditAttempts([good,bad,last],[good,last]);
  assert.equal(r.recorded,3);assert.equal(r.failed[0].device_error,-9001);
  assert.throws(()=>auditAttempts([good,bad,last],[last]),/omitted/);
  assert.throws(()=>auditAttempts([{...good,report:{final:{state:2}}}],[good]),/Unfinished/);
});
test('A/B permits only the selected feature and artifact identity differences',()=>{
  for(const feature of ['opus_fir_flash_word','opus_pulse_flash_word']) {
    const a={cpu_mhz:160,source_revision:'same',[feature]:false,bytes:10,app_sha256:'a'};
    const b={...a,[feature]:true,bytes:12,app_sha256:'b'};
    compareArtifacts(a,b,feature);
    assert.throws(()=>compareArtifacts(a,{...b,cpu_mhz:80},feature),/cpu_mhz/);
    assert.throws(()=>compareArtifacts(a,{...b,source_revision:'other'},feature),/source_revision/);
    assert.throws(()=>compareArtifacts(a,b,'cpu_mhz'),/Unknown/);
  }
});
const make=()=>Array.from({length:10},()=>({final:{state:3,error:0,physical_output:false,dram_after:25000,
  results:Array.from({length:5},(_,id)=>({id,error:0,samples:115200,packets:120,
    pcm_hash:123+id,task_us:1200000,wall_us:1300000,max_wall_us:30000,
    scratch_bytes:5488,scratch_words:15600,min_dram:5000,stack_free_lifetime:1700}))},
  comparison:Array.from({length:5},(_,i)=>({name:'case'+i})),snapshots:[]}));
test('raw A/B reports true medians and retains a slow outlier and observation timeout',()=>{
  assert.deepEqual(stats([1,2,3,4]),{min:1,median:2.5,mean:2.5,p95:4,max:4});
  const a=make(),b=make();b[9].final.results[0].task_us=2400000;b[9].final.results[0].wall_us=2500000;
  b[9].snapshots.push({error:'timeout'});
  const r=compare(a,b);assert.equal(r.cases[0].median_task_reduction_percent,0);
  assert.equal(r.candidate.cases[0].task_budget_percent.max,100);
  assert.deepEqual(r.candidate.observation_errors,[{run:10,error:'timeout'}]);
});
test('raw A/B refuses missing runs, output benchmarks, failed runs and PCM changes',()=>{
  assert.throws(()=>compare(make().slice(1),make()),/ten/);
  for(const change of [r=>r.error='timeout',r=>r.final.state=4,
    r=>r.final.physical_output=true,r=>r.final.results[0].pcm_hash++,
    r=>r.final.results[0].min_dram=0]) {
    const b=make();change(b[5]);assert.throws(()=>compare(make(),b));
  }
});
test('different task/wall timing windows retain positive overhead without clamping or dropping the run',()=>{
  const a=make(),b=make();b[5].final.results[0].wall_us=1199656;
  b[5].final.empty_task_us=42;
  const r=compare(a,b);
  assert.equal(r.candidate.runs,10);assert.equal(r.candidate.cases[0].task_budget_percent.median,50);
  assert.deepEqual(r.candidate.timing_window_excesses,[{run:6,id:0,task_us:1200000,
    wall_us:1199656,excess_us:344,empty_task_us:42,packets:120}]);
  b[5].final.results[0].wall_us=0;assert.throws(()=>compare(a,b));
});
