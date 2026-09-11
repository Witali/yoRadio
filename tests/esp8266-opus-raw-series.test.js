const test=require('node:test'),assert=require('node:assert/strict');
const {classify}=require('../tools/esp8266_opus_profile/classify_raw_run.cjs');
const report=()=>({after:{data:{}},fixtures:{fixtures:[{name:'sample',samples:960,packet_count:1,expected_hash:123}]},
  final:{state:3,error:0,physical_output:false,rounds:10,results:[{error:0,pcm_hash:123,samples:9600,packets:10,task_us:100000,min_dram:6000}]}});
test('raw series verifies PCM and retains terminal device failures without counting them as speed passes',()=>{
  assert.deepEqual(classify(report()),{completed:true,min_dram:6000,cases:[{name:'sample',cpu_budget_percent:50}]});
  const r=report();r.final.state=4;r.final.error=-9001;r.error='Device benchmark error -9001';
  assert.deepEqual(classify(r),{completed:false,device_error:-9001});
});
test('raw series does not restart unknown/physical/missing observations or incorrect PCM',()=>{
  for(const change of [r=>r.final.state=2,r=>delete r.after,r=>r.final.physical_output=true,
    r=>delete r.fixtures,r=>r.error='timeout',r=>r.final.results[0].pcm_hash++,
    r=>r.final.results[0].samples++,r=>r.final.results[0].packets++,r=>r.final.results[0].task_us=NaN,
    r=>{r.final.state=4;delete r.final.error;}]) {
    const r=report();change(r);assert.throws(()=>classify(r));
  }
});
