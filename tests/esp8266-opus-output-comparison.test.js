const test=require('node:test'),assert=require('node:assert/strict');
const {summarize,matched}=require('../tools/esp8266_opus_profile/compare_output_series.cjs');
function reports(){return Array.from({length:10},()=>({after:{data:{min_heap:6000}},snapshots:[],
  fixtures:{fixtures:[{name:'fixture',expected_hash:123,samples:11520,packet_count:12}]},
  final:{state:3,error:0,physical_output:true,rounds:100,results:[{
    pcm_hash:123,samples:1152000,packets:1200,output_samples:1152000,pipeline_wall_us:24000000,
    pipeline_task_us:18000000,wall_us:14000000,output_wall_us:7000000,max_wall_us:15000,max_output_us:10000,
    dma_eofs:2400,dma_misses:0,fifo_empty_seen:0,min_dram:6000,stack_free_lifetime:1600,error:0}]}}));}
test('output A/B retains discontinuities, low RAM and observation failures across every attempt',()=>{
  const r=reports();assert.equal(summarize(r).all_observed_gates_pass,true);
  r[0].final.results[0].dma_misses=2;r[1].final.results[0].min_dram=364;
  r[2].snapshots.push({error:'timeout'});
  r[3].final.state=4;r[3].final.error=-9001;
  const s=summarize(r);assert.equal(s.attempted.length,10);assert.equal(s.completed,9);
  assert.equal(s.cases[0].continuous,8);assert.deepEqual(s.cases[0].low_ram_attempts,[2]);
  assert.equal(s.cases[0].min_dram.min,364);assert.equal(s.cases[0].dma_misses.max,2);
  assert.equal(s.device_failures[0].attempt,4);assert.equal(s.observation_errors[0].attempt,3);
  assert.equal(s.all_observed_gates_pass,false);
});
test('clock-corrupt attempts and changed fixtures cannot silently produce a qualified speed result',()=>{
  let r=reports();r[0].final.results[0].max_wall_us=0xffff0000;
  let s=summarize(r);assert.deepEqual(s.cases[0].invalid_timing_attempts,[1]);
  assert.equal(s.cases[0].completed,10);assert.equal(s.all_observed_gates_pass,false);
  r=reports();r[0].fixtures.fixtures[0].name='different';assert.throws(()=>summarize(r));
  assert.throws(()=>summarize(reports().slice(1)));
  r=reports();r[0].final.state=2;assert.throws(()=>summarize(r));
});
test('publication output A/B rejects changed decoder or unrelated settings',()=>{
  const a={opus_pcm_publish:false,opus_benchmark_output:true,diagnostic:true,source_revision:'same',cpu_mhz:160};
  const b={...a,opus_pcm_publish:true};matched(a,b);
  assert.throws(()=>matched(a,{...b,cpu_mhz:80}));
  assert.throws(()=>matched(a,{...b,source_revision:'new'}));
});
