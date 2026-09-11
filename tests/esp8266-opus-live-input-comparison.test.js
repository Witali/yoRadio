const test=require('node:test'),assert=require('node:assert/strict');
const {summarizeSeries,compareManifests}=require('../tools/esp8266_opus_profile/compare_live_input.cjs');
function report(){return {seconds:25,samples:[1000,28000].map(t=>({host_ms:t,
  health:{generation:1,uptime_ms:t,rx_bytes:t,pcm_frames:t*48,sample_rate:48000,
    pcm_age_ms:1,underruns:0,free_heap:6000,dma_eofs:t,output_enabled:true},
  profile:{profile_version:2,generation:1,uptime_ms:t,stages:Array.from({length:5},()=>[t*100,1000,t,0])}}))};}
test('live input comparison retains missing, slow and clock-invalid windows',()=>{
  const reports=Array.from({length:10},report);
  reports[2].samples[0]={host_ms:1000,error:'timeout'};
  reports[7].samples[1].health.underruns=900;
  reports[9].samples[1].profile.stages[0][1]=0xffffff4b;
  const r=summarizeSeries(reports);
  assert.equal(r.attempted,10);assert.equal(r.observed,9);assert.equal(r.qualified,7);
  assert.equal(r.all_qualified,false);assert.deepEqual(r.missing_windows,[3]);
  assert.equal(r.observed_only.underruns.max,900);
  assert.equal(r.windows[9].timing_valid,false);
  assert.throws(()=>summarizeSeries(reports.slice(1)),/ten/);
});
test('input A/B allows no other runtime configuration changes',()=>{
  const a={diagnostic:true,opus_stream_test:true,opus_benchmark:false,opus_scratch_bytes:6144,
    opus_input_bytes:1024,source_revision:'same',cpu_mhz:160};
  const b={...a,opus_input_bytes:2048};compareManifests(a,b);
  assert.throws(()=>compareManifests(a,{...b,cpu_mhz:80}),/cpu_mhz/);
  assert.throws(()=>compareManifests(a,{...b,source_revision:'other'}),/source_revision/);
});

test('stopped output retains idle DMA misses but is not a speed measurement',()=>{
  const reports=Array.from({length:10},report);
  const [a,b]=reports[4].samples;
  b.health.pcm_frames=a.health.pcm_frames;
  b.health.rx_bytes=a.health.rx_bytes;
  b.health.pcm_age_ms=27000;
  b.health.underruns=2540;
  const r=summarizeSeries(reports);
  assert.deepEqual(r.zero_pcm_windows,[5]);
  assert.equal(r.observed,10);assert.equal(r.qualified,9);
  assert.equal(r.windows[4].continuity.underruns,2540);
  assert.match(r.interpretation,/not decoder-speed measurements/);
});
