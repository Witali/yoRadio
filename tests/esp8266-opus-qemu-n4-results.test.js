const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs'),{parseOutput}=require('../tools/esp8266_opus_qemu/run.cjs');
const {summarize}=require('../tools/esp8266_opus_qemu/trace.cjs');
const {packets}=require('../tools/esp8266_opus_profile/run_block_regressions.cjs');
const dir=path.join(root,'tests/results/esp8266-opus-qemu-n4-20261004-v2');
const read=n=>fs.readFileSync(path.join(dir,n)),json=n=>JSON.parse(read(n));
const summary=json('summary.json');
test('N4 archive is complete and byte-exact, including compressed input packets',()=>{
 const inventory=json('inventory.json');assert.equal(new Set(inventory.map(i=>i.name)).size,inventory.length);
 assert.deepEqual(fs.readdirSync(dir).filter(n=>n!=='inventory.json').sort(),inventory.map(i=>i.name).sort());
 for(const item of inventory){assert.equal(path.basename(item.name),item.name);const data=read(item.name);assert.equal(data.length,item.bytes);assert.equal(hash(data),item.sha256,item.name);}
 for(const f of summary.correctness.accepted.fixtures)assert.equal(hash(zlib.gunzipSync(read(f.name+'.opuspkt.gz'))),f.packet_sha256,f.name);
});
test('48 target-ASM cases include phase, mixed and high-bitrate modes with exact PCM and no arena growth',()=>{
 for(const kind of ['accepted','n4']){
  const r=json(kind+'-extended.json');assert.deepEqual(r,summary.correctness[kind]);assert.equal(r.passed,true);assert.equal(r.cases.length,24);assert.equal(r.oom_recovery_cases,24);
  for(const [name,digest] of Object.entries(r.recipe_hashes))assert.equal(hash(fs.readFileSync(path.join(root,'tools/esp8266_opus_qemu',name),'utf8').replace(/\r\n/g,'\n')),digest,name);
  const f=r.cases.map(c=>({...c,packet_count:c.packets,pcm_bytes:c.samples*2}));
  const parsed=parseOutput(zlib.gunzipSync(read(kind+'-extended.stdout.log.gz')).toString(),f);assert.equal(parsed.oom_recovery_cases,24);
  for(const name of ['mixed','320-48frames','192-120ms','stereo-510','phase-stereo-10ms-vbr-packed20.opuspkt'])assert.ok(r.cases.some(c=>c.name===name));
 }
 const a=summary.correctness.accepted,b=summary.correctness.n4;assert.deepEqual(a.cases,b.cases);assert.equal(a.state_bytes,b.state_bytes);assert.equal(a.stack_used_in_harness,b.stack_used_in_harness);
 assert.equal(Math.max(...b.cases.map(c=>c.byte_peak)),5968);assert.equal(Math.max(...b.cases.map(c=>c.word_peak)),15600);
});
test('all low/high-bitrate trace counts reproduce, with SILK-only zero counts verified by TOC',()=>{
 for(const [fixture,pair] of Object.entries(summary.profiles))for(const kind of ['accepted','n4']){
  const prefix=kind+'-'+fixture,r=json(prefix+'.json'),trace=zlib.gunzipSync(read(prefix+'.trace.log.gz'));
  assert.equal(hash(trace),r.instruction_trace.sha256);
  const silk=packets(zlib.gunzipSync(read(fixture+'.opuspkt.gz'))).every(p=>(p[0]>>>3)<12);assert.equal(r.instruction_trace.silk_only,silk);
  const parsed=summarize(trace.toString(),{helperName:kind==='n4'?'N4':'N3',allowEmpty:silk});assert.deepEqual(parsed,json(prefix+'.trace-summary.json'));assert.deepEqual(parsed.totals.pvq,pair[kind]);
 }
 for(const p of Object.values(summary.profiles)){assert.equal(p.instruction_delta,p.n4.instructions-p.accepted.instructions);assert.equal(p.load_delta,p.n4.load_instructions-p.accepted.load_instructions);}
 assert.equal(summary.profiles['mono-12'].n4.instructions,0);
 assert.equal(summary.profiles['stereo-128'].instruction_delta,4253);assert.equal(summary.profiles['stereo-192'].instruction_delta,887);
 assert.equal(summary.deterministic_replay,true);assert.deepEqual(json('n4-replay-192.json').instruction_trace.totals.pvq,summary.profiles['stereo-192'].n4);
});
test('first failed attempt remains: the runner rejected an empty SILK PVQ trace, not corrupt PCM',()=>{
 const failed=path.join(root,'tests/results/esp8266-opus-qemu-n4-20261004');
 assert.match(fs.readFileSync(path.join(failed,'accepted-mono-12.runner.log'),'utf8'),/assert.ok\(executions\)/);
 for(const label of ['accepted','n4']){
  const r=JSON.parse(fs.readFileSync(path.join(failed,label+'-extended.json')));assert.equal(r.passed,true);assert.equal(r.cases.length,24);
 }
 const text=zlib.gunzipSync(fs.readFileSync(path.join(failed,'accepted-mono-12.stdout.log.gz'))).toString();assert.match(text.slice(-200),/\r?\nPASS\r?\n$/);
});
