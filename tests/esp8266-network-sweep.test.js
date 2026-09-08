const test=require('node:test'),assert=require('node:assert/strict');
const {analyze,stats}=require('../tools/esp8266_audio_profile/summarize_network_sweep.cjs');
function measurement(id,variant,error=0) {
  let s=`net_bench: case=${id} path=/mp3-128?rate=128 output=0 begin rssi=-80 round=${Math.floor(id/2)} fixture=1 variant=${variant} wait_ms=${variant?25:0} read_limit=1024 batch=1\n`;
  s+=`net_cpu: case=${id} valid=1 total_us=20000000 tasks_before=2 tasks_after=2\n`;
  s+=`net_cpu: case=${id} task=audio id=4 runtime_us=${variant?1000000:3000000} existed=1\n`;
  s+=`net_cpu: case=${id} task=IDLE id=2 runtime_us=${variant?19000000:17000000} existed=1\n`;
  s+=`net_bench: case=${id} wall_us=20000000 bytes=320000 error=${error}\n`;
  for(let i=0;i<20;i++)s+=`net_bench: case=${id} second=${i} bytes=16000 rssi=-80\n`;
  return s;
}
test('sweep requires ten attempts, retains failed samples, and compares matching rounds',()=>{
  let s='net_bench: begin cases=20 sweep=1\n';
  for(let i=0;i<20;i++)s+=measurement(i,i%2,i===7?-116:0);
  s+='net_bench: complete\n';
  const r=analyze(s);assert.equal(r.complete,true);assert.equal(r.finished,20);
  assert.deepEqual(r.groups.map(g=>g.attempts),[10,10]);
  assert.equal(r.groups[1].failed,1);assert.equal(r.groups[1].errors['-116'],1);
  assert.equal(r.groups[0].reader_percent_complete.median,15);
  assert.equal(r.groups[1].reader_percent_complete.median,5);
  assert.equal(r.paired.length,9);assert.ok(r.paired.every(p=>p.reader_delta_pp===-10));
  assert.equal(analyze(s,11).complete,false);
  assert.equal(analyze(s+'net_bench: begin cases=20').complete,false);
});
test('missing/open-failed cases are not mistaken for successful throughput',()=>{
  const r=analyze('net_bench: begin cases=2\n'+measurement(0,0)+
    'net_bench: case=1 path=/mp3-128?rate=128 output=0 begin rssi=-90 round=0 fixture=1 variant=1\n'+
    'net_bench: case=1 open=-4 errno=11 open_us=10000000\nnet_bench: complete',1);
  assert.equal(r.complete,true);assert.equal(r.groups[1].failed,1);
  assert.equal(r.groups[1].reader_percent_complete.n,0);
  assert.equal(analyze('net_bench: begin cases=2\n'+measurement(0,0),1).complete,false);
  assert.deepEqual(stats([]),{n:0});assert.equal(stats([4,1,2,3]).median,2.5);
});
test('Wi-Fi recovery is retained and separates paired samples',()=>{
  const s='net_bench: begin cases=2\n'+measurement(0,0)+
    'net_bench: recovery begin next_case=1 consecutive_failures=3\n'+
    'net_bench: recovery complete next_case=1 elapsed_ms=4000 rssi=-77\n'+
    measurement(1,1)+'net_bench: complete';
  const r=analyze(s,1);
  assert.equal(r.complete,true);assert.equal(r.raw.recoveries.length,2);
  assert.deepEqual(r.samples.map(c=>c.recovery_epoch),[0,1]);
  assert.equal(r.paired.length,0);
});
test('explicit campaign combination retains partial runs and requires a finished final run',()=>{
  const {combine}=require('../tools/esp8266_audio_profile/summarize_network_campaign.cjs');
  const first='net_bench: begin cases=4\n'+measurement(0,0)+measurement(1,1,-116)+'net_bench: complete';
  const last='net_bench: begin cases=2\n'+measurement(0,0)+measurement(1,1)+'net_bench: complete';
  const r=combine([first,last],2);
  assert.equal(r.complete,true);assert.equal(r.finished,4);
  assert.deepEqual(r.groups.map(g=>g.attempts),[2,2]);
  assert.equal(r.groups[1].failed,1);assert.equal(r.paired.length,1);
  assert.deepEqual(r.runs.map(e=>e.all_declared_finished),[false,true]);
  assert.equal(combine([last,first],2).complete,false);
  assert.throws(()=>combine([first+last]),/Split captures/);
});
test('cancelled short windows are not reported as error zero or a continuous success',()=>{
  const s='net_bench: begin cases=1\n'+measurement(0,0).replace('wall_us=20000000','wall_us=1000000')+'net_bench: complete';
  const r=analyze(s,1);
  assert.equal(r.groups[0].failed,1);
  assert.equal(r.groups[0].errors.incomplete_window,1);
  assert.equal(r.groups[0].kept_up_windows,0);
});
test('playback task residency is not mislabelled as receive-only CPU',()=>{
  const s='net_bench: begin cases=2\n'+measurement(0,0).replace('output=0','output=1')+
    measurement(1,1).replace('output=0','output=1')+'net_bench: complete';
  const r=analyze(s,1);
  assert.equal(r.samples[0].reader_percent,null);
  assert.equal(r.groups[0].reader_percent_complete.n,0);
  assert.equal(r.groups[0].audio_task_percent_complete.median,15);
  assert.equal(r.paired[0].reader_delta_pp,null);
  assert.equal(r.paired[0].audio_delta_pp,-10);
});
