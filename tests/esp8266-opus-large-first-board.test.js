const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const f=require('../tools/esp8266_opus_profile/report_large_first.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const dest=path.join(f.art(f.early),'board-20260917');
test('allocation report retains all thirty attempts and recomputes real continuity',()=>{
 const r=read(path.join(f.art(f.early),'comparison.json'));
 for(const[n,k]of[['control','reference'],['candidate','experiment'],['early','early']]){
  assert.deepEqual(f.series(path.join(dest,n)),r[k]);assert.equal(r[k].attempts,10);
  for(const row of r[k].rows)if(row.init_diagnostic?.stage){assert.equal(row.init_diagnostic.reserve_bytes,4096);assert.ok(row.init_diagnostic.requested_bytes>0);}
 }
 assert.equal(r.reference.init_stages['8'],8);assert.equal(r.experiment.init_stages['8'],9);
 assert.equal(r.static_ram_delta,0);assert.equal(r.early_create_frame_delta,16);
 assert.equal(r.decoder_runtime_objects_identical,115);
 for(const m of[r.control,r.candidate,r.early_candidate]){assert.equal(m.opus_backend,'c');assert.equal(m.opus_benchmark,false);assert.equal(m.opus_scratch_bytes,6144);}
});
test('allocation report rejects a dropped attempt and a falsely qualified stopped window',t=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'opus-allocation-evidence-'));
 t.after(()=>fs.rmSync(tmp,{recursive:true,force:true}));
 fs.cpSync(path.join(dest,'control'),tmp,{recursive:true});
 const p=path.join(tmp,'live-series.json'),s=read(p);s.results.pop();fs.writeFileSync(p,JSON.stringify(s));
 assert.throws(()=>f.series(tmp));
 fs.copyFileSync(path.join(dest,'control/live-series.json'),p);
 const run=path.join(tmp,'live-run4.json'),r=read(run);r.pass=true;fs.writeFileSync(run,JSON.stringify(r));
 assert.throws(()=>f.series(tmp));
});
test('allocation experiment restores the prior app and preserves playlist and controls',()=>{
 const a=read(path.join(dest,'initial.json')),b=read(path.join(dest,'restored.json')),
  ota=read(path.join(dest,'ota-restore.json')),root=read(path.join(dest,'restored-root.json'));
 assert.equal(ota.pass,true);assert.equal(ota.sha256,'661becd301b07885d493ceb1b513d9e874b7d86e4ada8231da8657aa90983c4b');
 assert.equal(b.status.app_address,ota.target);assert.equal(b.status.playing,false);assert.equal(b.status.error,'');
 assert.equal(b.status.station,a.status.station);assert.equal(b.playlist.wire_sha256,a.playlist.wire_sha256);
 for(const r of[a,b]){assert.ok(r.index.messages.some(m=>m.current===167));const values=r.index.messages.flatMap(m=>m.payload||[]);assert.ok(values.some(v=>v.id==='volume'&&v.value===100));assert.ok(values.some(v=>v.id==='balance'&&v.value===0));}
 assert.equal(root.http,200);assert.equal(root.encoding,'gzip');assert.equal(root.bytes,27249);
 assert.ok(root.ms>0&&root.ms<500); // Single stopped HTTP sample, not a live/WebUI SLA.
});
