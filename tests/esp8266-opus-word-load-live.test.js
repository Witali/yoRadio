// These tests validate honest negative evidence, NOT successful live playback.
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const dir=path.join(root,'firmware/development/esp8266-opus-pvq-exp2-table32-candidate-v1/live-20260917');
const read=name=>JSON.parse(fs.readFileSync(path.join(dir,name),'utf8'));
const {summarize}=require('../tools/esp8266_opus_profile/run_stage_wall.cjs');
test('all ten live failures and the successful raw-only gate remain distinct',()=>{
  const series=read('runs/live-series.json');assert.equal(series.attempts,10);
  assert.equal(series.results.length,10);assert.equal(series.qualified,0);
  for(let i=1;i<=10;i++){
    const run=read('runs/live-run'+i+'.json'),trace=read('runs/live-trace'+i+'.json');
    assert.equal(run.start.http,202);assert.equal(run.start.body.queued,true);
    assert.deepEqual(trace.result,summarize(trace.samples,trace.seconds));
    const {runner_exit,...embedded}=run.trace;assert.deepEqual(embedded,trace);
    assert.equal(runner_exit,1);assert.equal(run.pass,false);
    assert.equal(trace.result.continuity.pass,false);
    assert.equal(run.init_diagnostic.body.stage,8);
    assert.equal(run.init_diagnostic.body.requested_bytes,6144);
    assert.equal(run.init_diagnostic.body.largest_dram,5076);
    assert.equal(run.init_diagnostic.body.reserve_bytes,4096);
    if(i>1){assert.equal(run.status.body.error,'DECODER INIT ERROR');assert.equal(trace.result.continuity.frames,0);}
  }
  const raw=JSON.parse(fs.readFileSync(path.join(dir,'../comparison.json'),'utf8'));
  assert.equal(raw.current_cpu_target.raw_cpu_target_met,true);
  assert.equal(raw.aspirational_78_cpu_target.raw_cpu_target_met,false);
});
test('own fixture, verified OTA restoration, station and playlist are retained',()=>{
  const fixture=fs.readFileSync(path.join(dir,'tone-noise-192.opus'));
  assert.equal(fixture.length,1527630);
  assert.equal(crypto.createHash('sha256').update(fixture).digest('hex'),'2f0c425a525f6d21bdc4c4ed0c070d9abe96fa71848102c1407538cad50ba028');
  const best=read('ota-best.json'),restore=read('ota-restore.json');
  assert.equal(best.pass,true);assert.equal(restore.pass,true);
  assert.equal(best.sha256,'7209b07ddde4febf7078e90100bfac3b3e4d9a7538e1ce44beaac95c30738649');
  assert.equal(restore.sha256,'661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b');
  const before=read('initial.json'),after=read('restored.json');
  assert.equal(after.status.app_address,restore.after.app_address);
  assert.equal(after.status.playing,false);assert.equal(after.status.connecting,false);
  assert.equal(after.status.error,'');assert.equal(after.status.network,1);
  assert.equal(after.status.station,before.status.station);
  assert.equal(after.playlist.http,200);assert.equal(after.playlist.wire_sha256,before.playlist.wire_sha256);
  const fields=after.index.messages.flatMap(v=>v.payload||[]);
  assert.ok(fields.some(v=>v.id==='volume'&&v.value===100));
  assert.ok(fields.some(v=>v.id==='playerwrap'&&v.value==='stopped'));
  assert.ok(after.index.messages.some(v=>v.current===167));
  assert.equal(read('restored-root.json').http_code,200);
});
