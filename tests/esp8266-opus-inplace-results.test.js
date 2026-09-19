const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs');
const f=require('../tools/esp8266_opus_asm/pvq_inplace_b1.cjs'),dir=f.art('candidate');
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {assertCompleteRun}=require('../tools/esp8266_opus_asm/report_pvq_n3_diff.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');
const result=()=>f.read(path.join(dir,'comparison.json'));
test('in-place report refuses partial/nonterminal/error observations',()=>{
 const r=f.read(path.join(dir,'after/run10.json'));assertCompleteRun(r);
 for(const edit of[x=>delete x.after,x=>x.final.state=2,x=>x.final.error=1,x=>x.comparison=[]]){
  const x=structuredClone(r);edit(x);assert.throws(()=>assertCompleteRun(x));
 }
 assert.throws(()=>assertCompleteRun({}));
});
test('all30 in-place attempts and150 PCM results are retained with correct OTA identities',()=>{
 const r=result(),seen=new Set(),fixtures=f.read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const group of['before','candidate','after']){
  assert.equal(r.inputs[group].length,10);const ota=f.read(path.join(dir,'ota-'+group+'.json'));
  assert.equal(ota.pass,true);assert.equal(ota.sha256,r.pair.manifests[group==='candidate'?'candidate':'control'].app_sha256);
  for(const item of r.inputs[group]){
   assert.ok(!seen.has(item.file));seen.add(item.file);const bytes=fs.readFileSync(path.join(root,item.file));
   assert.equal(hash(bytes),item.sha256);validateRun(JSON.parse(bytes),fixtures,ota.after.app_address);
  }
 }
 assert.equal(seen.size,30);const p=f.read(path.join(dir,'preflight.json'));assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
});
test('in-place statistics and decisions reproduce including all low-memory measurements',()=>{
 const r=result(),runs=g=>r.inputs[g].map(i=>f.read(path.join(root,i.file)));
 const a=compare(runs('before'),runs('candidate')),a2=compare(runs('after'),runs('candidate'));
 assert.deepEqual(r.initial,a);assert.deepEqual(r.repeated,a2);
 const selection={initial:selectHighBitrate(a.cases),repeated:selectHighBitrate(a2.cases)};
 assert.deepEqual(r.selection,selection);assert.equal(r.accepted_for_experimental_asm,selection.initial.accepted_for_experimental_asm&&selection.repeated.accepted_for_experimental_asm);
 assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(a.cases,75));
 for(const group of['before','candidate','after']){
  const values=runs(group).flatMap(x=>x.final.results),saved=r.memory[group];
  assert.equal(saved.min_dram,Math.min(...values.map(x=>x.min_dram)));
  assert.equal(saved.scratch_byte_peak,Math.max(...values.map(x=>x.scratch_bytes)));
  assert.equal(saved.scratch_word_peak,Math.max(...values.map(x=>x.scratch_words)));
  assert.equal(saved.stack_free_lifetime,Math.min(...values.map(x=>x.stack_free_lifetime)));
 }
});
test('ordinary firmware restored after terminal benchmark with working status and playlist',()=>{
 const before=f.read(path.join(dir,'before-restore.json'));assert.equal(before.final.state,3);assert.equal(before.final.error,0);assert.equal(before.start,undefined);
 const ota=f.read(path.join(dir,'ota-restore.json')),ordinary=f.read(path.join(root,'firmware/development/esp8266-main/manifest.json'));
 assert.equal(ota.pass,true);assert.equal(ota.sha256,ordinary.app_sha256.toLowerCase());assert.equal(ota.upload.http,200);
 const ui=f.read(path.join(dir,'restored-webui.json'));
 assert.equal(ui.status.app_address,ota.after.app_address);assert.equal(ui.status.error,'');assert.equal(ui.status.playing,false);
 assert.ok(ui.index.messages.some(m=>m.payload?.some(p=>p.id==='playerwrap'&&p.value==='stopped')));
 assert.equal(ui.playlist.http,200);assert.ok(ui.playlist.wire_bytes>0);
 for(const item of result().evidence)assert.equal(hash(fs.readFileSync(path.join(root,item.file))),item.sha256);
});
test('slow A2/run7 and its timeout remain in the rejected in-place result',()=>{
 const slow=f.read(path.join(dir,'after/run7.json')),r=result();
 assert.equal(slow.final.state,3);assert.equal(slow.final.error,0);
 assert.ok(slow.snapshots.some(s=>s.error==='request timeout'));
 assert.equal(Math.min(...slow.final.results.map(x=>x.min_dram)),1040);
 assert.equal(slow.final.results[4].task_us,2158539);assert.equal(slow.final.results[4].max_wall_us,27983);
 assert.equal(r.inputs.after.length,10);assert.equal(r.accepted_for_experimental_asm,false);
 assert.equal(r.selection.initial.accepted_for_experimental_asm,false);assert.equal(r.selection.repeated.accepted_for_experimental_asm,false);
});
