// Recompute intrusive live-memory observations. Not a CPU/continuity gate.
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
const artifact=path.join(root,'firmware/development/esp8266-opus-live-memory-diag-v1');
const json=f=>JSON.parse(fs.readFileSync(f,'utf8').replace(/^\uFEFF/,''));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const range=a=>a.length?{min:Math.min(...a),max:Math.max(...a)}:null;
const states=['CLOSED','LISTEN','SYN_SENT','SYN_RCVD','ESTABLISHED','FIN_WAIT_1','FIN_WAIT_2','CLOSE_WAIT','CLOSING','LAST_ACK','TIME_WAIT'];
function analyze(run){
 const memories=run.samples.filter(s=>s.memory?.http===200).map(s=>s.memory.body);
 const audio=run.samples.filter(s=>s.audio?.http===200).map(s=>s.audio.body);
 const inits=run.samples.filter(s=>s.init?.http===200).map(s=>s.init.body);
 const closing=memories.filter(m=>m.tcp_valid&&m.client.ooseq>0&&m.client.pcbs>0&&
   (m.client.states&~((1<<5)|(1<<6)))===0);
 return {
  observations:run.samples.length,observable:run.observable,start_error:run.start_error??null,
  request_errors:run.samples.flatMap(s=>Object.entries(s).filter(([k])=>k.endsWith('_error')).map(([route,error])=>({sample:s.index,route,error}))),
  final_error:run.status?.body?.error??null,final_connecting:run.status?.body?.connecting??null,
  last_init:inits.at(-1)??null,dram_sampled:range(memories.map(m=>m.current_dram)),
  largest_sampled:range(memories.map(m=>m.largest_dram)),tcp_age_ms:range(memories.map(m=>m.tcp_age_ms)),
  client_ooseq_payload:range(memories.map(m=>m.client.ooseq)),
  closing_only_ooseq_samples:closing.map(m=>({at_ms:m.heap_ms,age_ms:m.tcp_age_ms,dram:m.current_dram,
   states:states.filter((_,i)=>m.client.states&(1<<i)),pcbs:m.client.pcbs,payload:m.client.ooseq})),
  sdk_rx_failures:Object.fromEntries(['rx_custom_fail','rx_enqueue_nomem','rx_enqueue_full','tx_transform_fail','tx_driver_fail'].map(k=>[k,range(audio.map(a=>a[k]))])),
  rx_custom_live:range(audio.map(a=>a.rx_custom_live)),audio_stack_free:range(audio.map(a=>a.audio_stack_free)),
  pcm_frames_counter:range(audio.map(a=>a.pcm_frames)),
  transport_phases:[...new Set(audio.map(a=>a.transport_phase))].sort(),
  heap_valid:memories.every(m=>m.heap_valid),
 };
}
function report(dir=path.join(artifact,'evidence')){
 const summary=json(path.join(dir,'runs/summary.json'));
 assert.equal(summary.requested,10);assert.equal(summary.attempts.length,10);
 const ota=json(path.join(dir,'ota-diag.json')),restore=json(path.join(dir,'restore.json'));
 const manifest=json(path.join(artifact,'manifest.json'));
 assert.equal(ota.pass,true);assert.equal(restore.pass,true);
 assert.equal(ota.sha256,sha(path.join(artifact,'app.bin')));
 assert.equal(ota.sha256,manifest.app_sha256.toLowerCase());
 assert.equal(manifest.opus_backend,'c');assert.equal(manifest.memory_profile,true);
 assert.equal(manifest.opus_benchmark,false);assert.equal(manifest.freertos_runtime_stats,false);
 const runs=summary.attempts.map((a,i)=>{
  assert.equal(a.attempt,i+1);const f=path.join(dir,'runs',a.file),r=json(f);
  assert.equal(r.samples.length,8);assert.equal(r.observable,true);
  return {attempt:i+1,file:a.file,sha256:sha(f),...analyze(r)};
 });
 const before=json(path.join(dir,'initial.json')),after=json(path.join(dir,'restored-snapshot.json'));
 assert.equal(before.playlist.wire_sha256,after.playlist.wire_sha256);
 assert.equal(before.status.station,after.status.station);assert.equal(after.status.playing,false);
 assert.equal(after.status.error,'');assert.ok(after.index.messages.length);
 return {scope:'Intrusive C-backend RAM/TCP diagnosis: three sequential HTTP requests per sample. Not ASM CPU or uninterrupted playback qualification.',
  app_sha256:ota.sha256,restored_app_sha256:restore.sha256,
  runs,totals:{requests_failed:runs.reduce((n,r)=>n+r.request_errors.length,0),
   closing_only_ooseq_observations:runs.reduce((n,r)=>n+r.closing_only_ooseq_samples.length,0),
   last_init_stages:runs.reduce((a,r)=>{const k=r.last_init?.stage??'unobserved';a[k]=(a[k]??0)+1;return a;},{})},
  limitations:['Snapshots are sequential, not simultaneous. TCP cache age is explicit.',
   'OOO counters are payload, not allocated pbuf RAM; netconn mailboxes and driver buffers are not included.',
   'Non-port80 PCBs are grouped as client, not identified individually by connection or radio URL.',
   'Latched init diagnostics can belong to an internal reconnect; do not count them as every init attempt.',
   'Stopped neutral DMA underruns are not active-audio gaps. PCM counters do not prove continuity.',
   'No A/B speed claim or proof of the first timeout cause follows from this experiment.'],
  restored:{status:after.status,playlist_sha256:after.playlist.wire_sha256,websocket_messages:after.index.messages.length}};
}
function archive(source){
 const dest=path.join(artifact,'evidence');fs.mkdirSync(dest,{recursive:true});
 const copy=(s,d)=>{if(fs.existsSync(d))assert.equal(sha(s),sha(d),'refuse replacing evidence '+d);else fs.copyFileSync(s,d);};
 for(const name of ['initial.json','ota-diag.json','restore.json','restored-snapshot.json','stop-diag.json','probe.log','server.jsonl'])copy(path.join(source,name),path.join(dest,name));
 fs.mkdirSync(path.join(dest,'runs'),{recursive:true});
 for(const name of fs.readdirSync(path.join(source,'runs')))copy(path.join(source,'runs',name),path.join(dest,'runs',name));
 for(const [name,src]of Object.entries({'build.log':'.build/opus-live-memory-diag-v1-build.log','host-tests.log':'.build/opus-live-memory-diag-host-tests-v2.log','host-tests-initial-mock-failure.log':'.build/opus-live-memory-diag-host-tests.log'}))copy(path.join(root,src),path.join(dest,name));
 const cache=fs.readFileSync(path.join(root,'.build/esp8266-opus-live-memory-diag-v1/CMakeCache.txt'),'utf8');
 const nm=cache.match(/^CMAKE_NM:FILEPATH=(.+)$/m)[1].trim(),size=nm.replace(/nm(\.exe)?$/,'size$1');
 const elf=variant=>path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf');
 const layout=Object.fromEntries(['esp8266-opus-live-memory-diag-v1','esp8266-opus-live512-idle3s-20260913'].map(v=>[v,{elf_sha256:sha(elf(v)),
  sections:execFileSync(size,['-A',elf(v)],{encoding:'utf8'}).split(/\r?\n/).filter(s=>/^\.(iram|dram|flash)/.test(s)),
  sampler_symbols:execFileSync(nm,['-S','--size-sort',elf(v)],{encoding:'utf8'}).split(/\r?\n/).filter(s=>/s_tcp_|sdk_rx_diag|memory_profile_json/.test(s))}]));
 fs.writeFileSync(path.join(dest,'layout.json'),JSON.stringify(layout,null,2)+'\n');
 const names=['memory_profile.c','memory_profile.h','memory_tcp_snapshot.h','web_service.c','CMakeLists.txt'];
 const sources=names.map(n=>({path:'esp8266/rtos-sdk-native/main/'+n,sha256:sha(path.join(root,'esp8266/rtos-sdk-native/main',n))}));
 fs.writeFileSync(path.join(dest,'source-hashes.json'),JSON.stringify(sources,null,2)+'\n');
 const result=report(dest);fs.writeFileSync(path.join(artifact,'observations.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result.totals));
}
module.exports={analyze,report,archive};
if(require.main===module){if(process.argv[2]==='archive')archive(path.resolve(process.argv[3]));else console.log(JSON.stringify(report(),null,2));}
