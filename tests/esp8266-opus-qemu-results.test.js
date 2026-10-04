const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs');
const {parseOutput}=require('../tools/esp8266_opus_qemu/run.cjs');
const {summarize}=require('../tools/esp8266_opus_qemu/trace.cjs');
const {spawnSync}=require('node:child_process');
const dir=path.join(root,'tests/results/esp8266-opus-qemu-20261004');
const read=name=>fs.readFileSync(path.join(dir,name));
const json=name=>JSON.parse(read(name));
const summary=json('summary.json');
test('archived QEMU evidence has exact inventory hashes',()=>{
 const inventory=json('inventory.json');
 assert.equal(new Set(inventory.map(x=>x.name)).size,inventory.length);
 for(const item of inventory){assert.equal(path.basename(item.name),item.name);const data=read(item.name);assert.equal(data.length,item.bytes,item.name);assert.equal(hash(data),item.sha256,item.name);}
});
test('26 target-ASM PCM/arena/OOM cases pass with recorded source recipes',()=>{
 for(const label of ['accepted','n3_unroll4']){
  const r=json(label+'-extended.json');assert.equal(r.passed,true);assert.deepEqual(r,summary.correctness[label]);
  assert.equal(r.cases.length,13);assert.equal(r.oom_recovery_cases,13);assert.equal(r.state_bytes,6582);
  // Historical evidence pins the runner commit, not today's evolving runner.
  for(const [name,digest] of Object.entries(r.recipe_hashes)){
   const historical=spawnSync('git',['show','6006aefa:tools/esp8266_opus_qemu/'+name],{cwd:root,encoding:'utf8'});
   assert.equal(historical.status,0,historical.stderr);assert.equal(hash(historical.stdout.replace(/\r\n/g,'\n')),digest,name);
  }
  const selected=r.cases.map(c=>({...c,packet_count:c.packets,pcm_bytes:c.samples*2}));
  const p=parseOutput(zlib.gunzipSync(read(label+'-extended.stdout.log.gz')).toString(),selected);
  assert.equal(p.oom_recovery_cases,13);assert.equal(p.stack_used_in_harness,r.stack_used_in_harness);
 }
 assert.deepEqual(summary.correctness.accepted.cases,summary.correctness.n3_unroll4.cases);
 assert.equal(Math.max(...summary.correctness.accepted.cases.map(x=>x.byte_peak)),5488);
 assert.equal(Math.max(...summary.correctness.accepted.cases.map(x=>x.word_peak)),15600);
});
test('archived dynamic traces reproduce all instruction and load deltas',()=>{
 for(const [fixture,pair] of Object.entries(summary.profiles)){
  for(const label of ['accepted','n3_unroll4']){
   const prefix=label+'-'+fixture,trace=zlib.gunzipSync(read(prefix+'.trace.log.gz'));
   const r=json(prefix+'.json');assert.equal(hash(trace),r.instruction_trace.sha256);
   const parsed=summarize(trace.toString());assert.deepEqual(parsed,json(prefix+'.trace-summary.json'));
   assert.deepEqual(parsed.totals.pvq,pair[label]);
  }
  assert.equal(pair.instruction_delta,pair.n3_unroll4.instructions-pair.accepted.instructions);
  assert.equal(pair.load_delta,pair.n3_unroll4.load_instructions-pair.accepted.load_instructions);
 }
});
test('actual QEMU negative guard and deterministic replay remain recorded',()=>{
 assert.equal(summary.negative_guard,true);assert.equal(summary.deterministic_replay,true);
 assert.match(read('negative-canary.runner.log').toString(),/QEMU 20:/);
 assert.deepEqual(json('n3-replay-stereo-192.json').instruction_trace.totals.pvq,summary.profiles['stereo-192'].n3_unroll4);
});
