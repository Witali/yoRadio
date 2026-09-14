const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash}=require('../tools/esp8266_opus_asm/export.cjs');
const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
const {candidate,control}=require('../tools/esp8266_opus_asm/report_partition_decode.cjs');
const dir=path.join(root,'firmware/development',candidate),read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
test('partition decoder-only archive retains all 30 actual A/B/A measurements and maxima',()=>{
 const result=read(path.join(dir,'comparison.json'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')),groups={};
 for(const [name,subdir]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  assert.equal(fs.readdirSync(path.join(dir,subdir)).filter(n=>/^run\d+\.json$/.test(n)).length,10);
  const inputs=result.inputs[name];assert.equal(inputs.length,10);
  const ota=read(path.join(dir,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,result.proof.manifests[name==='candidate'?1:0].app_sha256.toLowerCase());
  groups[name]=inputs.map((r,i)=>{
   const file=path.join(root,r.file);assert.equal(file,path.join(dir,subdir,'run'+(i+1)+'.json'));
   const bytes=fs.readFileSync(file);assert.equal(hash(bytes),r.sha256);
   const report=JSON.parse(bytes);validateRun(report,fixtures,ota.after.app_address);return report;
  });
 }
 assert.deepEqual(compare(groups.before,groups.candidate),result.initial);
 assert.deepEqual(compare(groups.after,groups.candidate),result.repeated);
 for(const name of ['initial','repeated']){
  assert.deepEqual(selectHighBitrate(result[name].cases),result.selection[name]);
  assert.equal(result.selection[name].accepted_for_experimental_asm,false);
  assert.equal(result.selection[name].target_192_cpu_at_most_70,false);
 }
 for(const [i,variant]of [control,candidate].entries()){
  const bytes=fs.readFileSync(path.join(root,'firmware/development',variant,'app.bin'));
  assert.equal(hash(bytes),result.proof.manifests[i].app_sha256.toLowerCase());assert.equal(bytes.length,result.proof.manifests[i].bytes);
 }
 assert.equal(result.proof.static_ram_delta,0);
});
test('ordinary firmware restored by OTA and HTTP/WebSocket state verified',()=>{
 const ota=read(path.join(dir,'restore-ota.json')),snapshot=read(path.join(dir,'restore-snapshot.json'));
 assert.equal(ota.pass,true);assert.equal(ota.sha256,'661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b');
 assert.equal(snapshot.status.app_address,ota.after.app_address);assert.equal(snapshot.status.playing,false);
 assert.equal(snapshot.status.connecting,false);assert.equal(snapshot.status.error,'');
 const initial=read(path.join(dir,'initial-snapshot.json')),rootResponse=read(path.join(dir,'restore-root.json'));
 assert.equal(rootResponse.http,200);assert.equal(rootResponse.html,true);
 assert.equal(snapshot.playlist.http,200);assert.equal(snapshot.playlist.wire_sha256,initial.playlist.wire_sha256);
 const payload=snapshot.index.messages.flatMap(m=>m.payload||[]);
 assert.equal(payload.find(p=>p.id==='nameset').value,snapshot.status.station);
 assert.equal(payload.find(p=>p.id==='connecting').value,false);
 assert.deepEqual(snapshot.index.messages.find(m=>m.current!==undefined),initial.index.messages.find(m=>m.current!==undefined));
 assert.equal(snapshot.status.station,initial.status.station);
});
