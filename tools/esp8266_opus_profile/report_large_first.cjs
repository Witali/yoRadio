// Archive every physical attempt, including failed requests and stopped DMA.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {hash}=require('../esp8266_opus_asm/export.cjs');
const {summarize}=require('./run_stage_wall.cjs');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'.build/opus-large-first-20260917');
const control='esp8266-opus-small-first-c-control-20260917',candidate='esp8266-opus-large-first-c-20260917';
const early='esp8266-opus-early-reserve-c-20260917';
const art=v=>path.join(root,'firmware/development',v);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function series(dir){
 const summary=read(path.join(dir,'live-series.json'));assert.equal(summary.attempts,10);assert.equal(summary.results.length,10);
 const rows=[];
 for(let i=1;i<=10;i++){
  const r=read(path.join(dir,'live-run'+i+'.json')),trace=read(path.join(dir,'live-trace'+i+'.json'));
  assert.equal(summary.results[i-1].attempt,i);assert.equal(trace.seconds,25);
  assert.deepEqual(trace.result,summarize(trace.samples,25));
  const {runner_exit,...saved}=r.trace;assert.deepEqual(saved,trace);
  const pass=r.start?.http===202&&r.start.body?.queued===true&&r.status?.http===200&&r.status.body?.playing===true&&r.status.body?.codec==='OPUS'&&trace.result?.continuity?.pass===true&&!trace.result?.profile_error;
  assert.equal(r.pass,pass);assert.equal(summary.results[i-1].pass,pass);
  assert.deepEqual(summary.results[i-1].init_diagnostic,r.init_diagnostic);
  rows.push({attempt:i,pass,start_error:r.start_error??null,status_error:r.status_error??null,
   status:r.status?.body??null,continuity:trace.result.continuity,
   profile_error:trace.result.profile_error??null,init_diagnostic:r.init_diagnostic?.body??null,
   init_diagnostic_error:r.init_diagnostic_error??null,
   run_sha256:hash(fs.readFileSync(path.join(dir,'live-run'+i+'.json'))),
   trace_sha256:hash(fs.readFileSync(path.join(dir,'live-trace'+i+'.json')))});
 }
 const stages={};for(const r of rows){const k=r.init_diagnostic?String(r.init_diagnostic.stage):'unavailable';stages[k]=(stages[k]??0)+1;}
 const qualified=rows.filter(r=>r.pass).length;assert.equal(summary.qualified,qualified);
 return{attempts:10,qualified,startup_playing:rows.filter(r=>r.status?.playing).length,init_stages:stages,rows};
}
function save(file,data){fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file))assert.deepEqual(fs.readFileSync(file),data,'Existing evidence differs: '+file);else fs.writeFileSync(file,data);}
function archive(from,to){for(const e of fs.readdirSync(from,{withFileTypes:true})){const a=path.join(from,e.name),b=path.join(to,e.name);if(e.isDirectory())archive(a,b);else save(b,fs.readFileSync(a));}}
function report(){
 const a=read(path.join(art(control),'manifest.json')),b=read(path.join(art(candidate),'manifest.json')),c=read(path.join(art(early),'manifest.json'));
 const identity=['built_utc','source_revision','app_sha256','bytes','codec_bridge_sha256'];
 for(const other of[b,c])for(const k of new Set([...Object.keys(a),...Object.keys(other)]))if(!identity.includes(k))assert.deepEqual(a[k],other[k],k);
 for(const m of[a,b,c]){assert.equal(m.opus_backend,'c');assert.equal(m.opus_benchmark,false);assert.equal(m.opus_input_bytes,1024);assert.equal(m.opus_scratch_bytes,6144);assert.equal(m.dma_words_per_buffer,512);assert.equal(m.stream_idle_timeout_ms,3000);assert.equal(m.flash,'QIO40');assert.equal(m.cpu_mhz,160);}
 for(const[v,m]of[[control,a],[candidate,b],[early,c]]){const app=fs.readFileSync(path.join(art(v),'app.bin'));assert.equal(hash(app),m.app_sha256.toLowerCase());assert.equal(app.length,m.bytes);}
 const layout=read(path.join(base,'layout.json')),objects=read(path.join(base,'decoder-objects.json')),stack=read(path.join(base,'allocator-stack.json'));
 assert.ok(objects.pass&&objects.objects===115&&objects.records.length===115);
 for(const[k,n]of Object.entries(layout.reference.sections))if(!k.startsWith('.flash.'))assert.equal(layout.candidate.sections[k],n,k);
 const frames={};for(const v of[control,candidate]){frames[v]={};for(const[name,f]of Object.entries(stack[v].functions)){const first=f.disassembly.split('\n')[0];const m=first.match(/addi\s+a1, a1, -(\d+)/);assert.ok(m);frames[v][name]=Number(m[1]);}}
 assert.deepEqual(frames[control],frames[candidate]);
 const earlyStatic=read(path.join(base,'early-static.json')),earlyLayout=read(path.join(base,'layout-early.json'));assert.equal(earlyStatic.objects_identical,115);
 for(const[k,n]of Object.entries(layout.reference.sections))if(!k.startsWith('.flash.'))assert.equal(earlyLayout.candidate.sections[k],n,k);
 const earlyFrames={};for(const[name,f]of Object.entries(earlyStatic.stack.functions)){const m=f.disassembly.split('\n')[0].match(/addi\s+a1, a1, -(\d+)/);assert.ok(m);earlyFrames[name]=Number(m[1]);}
 assert.equal(earlyFrames.helix_codec_create,80);assert.equal(frames[candidate].helix_codec_create,64);
 const result={schema:1,scope:'Three matched C-backend allocation-order profiles, ten starts each. NOT a new ASM speed result. Stopped neutral DMA counters do not quantify active-audio underruns.',control:a,candidate:b,early_candidate:c,static_ram_delta:0,allocator_stack_frames:frames[candidate],early_allocator_stack_frames:earlyFrames,early_create_frame_delta:16,decoder_runtime_objects_identical:115,reference:series(path.join(base,'control')),experiment:series(path.join(base,'candidate')),early:series(path.join(base,'early'))};
 const dest=path.join(art(early),'board-20260917');archive(base,dest);
 save(path.join(art(early),'comparison.json'),Buffer.from(JSON.stringify(result,null,2)+'\n'));
 console.log(JSON.stringify({control:result.reference.init_stages,candidate:result.experiment.init_stages,early:result.early.init_stages,qualified:[result.reference.qualified,result.experiment.qualified,result.early.qualified],startup_playing:[result.reference.startup_playing,result.experiment.startup_playing,result.early.startup_playing]}));return result;
}
module.exports={series,report,base,control,candidate,early,art};if(require.main===module)report();
