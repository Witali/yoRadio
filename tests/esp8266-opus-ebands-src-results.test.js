const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const result=()=>read(path.join(root,'firmware/development/esp8266-opus-ebands-src-candidate-v2/comparison.json'));
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {evaluateRawCpuTarget}=require('../tools/esp8266_opus_asm/cpu_target.cjs');

test('all thirty unique physical attempts match hashes, PCM and confirmed OTA slots',()=>{
 const r=result(),seen=new Set(),fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const group of ['before','candidate','after']){
  assert.equal(r.inputs[group].length,10);
  const ota=read(path.join(root,'firmware/development/esp8266-opus-ebands-src-candidate-v2/ota-'+group+'.json'));
  assert.equal(ota.pass,true);
  assert.equal(ota.sha256,r.pair.manifests[group==='candidate'?'candidate':'control'].app_sha256);
  for(const item of r.inputs[group]){
   assert.ok(!seen.has(item.file));seen.add(item.file);
   const bytes=fs.readFileSync(path.join(root,item.file));
   assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),item.sha256);
   validateRun(JSON.parse(bytes),fixtures,ota.after.app_address);
  }
 }
 assert.equal(seen.size,30);
 assert.equal(r.pair.proof.static_ram_delta,0);assert.equal(r.pair.proof.stack_delta,0);
});

test('medians, outliers and speed/75-percent gates reproduce from all saved attempts',()=>{
 const r=result(),runs=group=>r.inputs[group].map(i=>read(path.join(root,i.file)));
 const a=compare(runs('before'),runs('candidate')),a2=compare(runs('after'),runs('candidate'));
 assert.deepEqual(r.initial,a);assert.deepEqual(r.repeated,a2);
 const first=selectHighBitrate(a.cases),last=selectHighBitrate(a2.cases);
 assert.deepEqual(r.selection,{initial:first,repeated:last});
 assert.equal(r.accepted_for_experimental_asm,first.accepted_for_experimental_asm&&last.accepted_for_experimental_asm);
 assert.deepEqual(r.current_cpu_target,evaluateRawCpuTarget(a.cases,75));
});
