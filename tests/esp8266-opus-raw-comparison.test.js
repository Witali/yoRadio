const test=require('node:test'),assert=require('node:assert/strict');
const {stats,compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
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
