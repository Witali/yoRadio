const test=require('node:test'),assert=require('node:assert/strict');
const {classify}=require('../tools/esp8266_opus_profile/classify_output_run.cjs');
function report() {
  return {after:{data:{free_heap:24000}},fixtures:{fixtures:[{name:'fixture',expected_hash:123,samples:11520,packet_count:12}]},
    final:{state:3,error:0,physical_output:true,rounds:100,results:[{
      pcm_hash:123,samples:1152000,packets:1200,output_samples:1152000,
      pipeline_wall_us:24000000,pipeline_task_us:18000000,wall_us:14000000,
      output_wall_us:7000000,dma_eofs:2400,dma_misses:0,fifo_empty_seen:0,min_dram:6000,error:0}]}};
}
test('physical series retains failed continuity without claiming successful playback',()=>{
  let r=report();assert.equal(classify(r).continuous_cases,1);
  r.final.results[0].dma_misses=1;
  r.error='Physical output continuity gate failed; results retained';
  const result=classify(r);
  assert.equal(result.completed,true);assert.equal(result.continuous_cases,0);
  assert.equal(result.cases[0].pipeline_cpu_budget_percent,75);
  r=report();r.final.state=4;r.final.error=-9001;
  assert.deepEqual(classify(r),{terminal:true,completed:false,device_error:-9001,continuous_cases:0});
});
test('unknown running state, wrong firmware and bad PCM never authorize another attempt',()=>{
  for(const mutate of [r=>delete r.final,r=>r.final.state=2,r=>r.final.physical_output=false,
    r=>delete r.after,r=>delete r.fixtures,r=>r.error='request timeout',
    r=>r.final.results[0].pcm_hash++,r=>r.final.results[0].samples++,
    r=>r.final.results[0].packets++]) {
    const r=report();mutate(r);assert.throws(()=>classify(r));
  }
});
