// Host semantic/arena experiments, not a claim of LX106 CPU improvement.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath,component}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
const candidates=require('./algorithm_candidates.cjs');
const out=path.join(root,'.build/opus-algorithm-candidates');
function specs() {
 const dir=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const result=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(dir,f.name+'.opuspkt')}));
 result.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const phase=path.join(root,'tests/fixtures/opus_native/phase');
 for(const name of fs.readdirSync(phase).filter(n=>n.endsWith('.opuspkt')).sort())result.push({name:'phase-'+name,file:path.join(phase,name)});
 const {grouped}=require('../esp8266_opus_profile/run_block_regressions.cjs');
 for(const [name,input,count]of [['192-120ms',path.join(dir,'stereo-192.opuspkt'),6],['320-120ms',path.join(root,'.build/opus-high-compatibility/stereo-320-20ms.opuspkt'),6],['320-48frames',path.join(root,'.build/opus-high-compatibility/stereo-320-2.5ms.opuspkt'),48]]) {
  const file=path.join(out,name+'.opuspkt');fs.writeFileSync(file,grouped(fs.readFileSync(input),count));result.push({name,file});
 }
 result.push({name:'mixed',sequence:['mono-12','mono-24','stereo-64','stereo-192','mono-12'].map(n=>path.join(dir,n+'.opuspkt'))});
 return result;
}
function verifyState(a,b) {
 for(const key of ['samples','reset_exact','scratch_byte_capacity_bytes','scratch_word_capacity_bytes','persistent_bytes','sequence_packets','plc_frames','mono_state_bytes','stereo_state_bytes','packets','output_channels','sample_rate','arena_guards_ok','oom_reinitialized_exact']) {
  if(Object.hasOwn(a,key)) {assert.deepEqual(b[key],a[key],key);if(['reset_exact','arena_guards_ok','oom_reinitialized_exact'].includes(key))assert.equal(b[key],true,key);}
 }
 for(const key of ['scratch_byte_peak_bytes','scratch_word_peak_bytes']) {assert.ok(Number.isFinite(b[key]));assert.ok(b[key]<=a[key],key+' increased');}
}
function traceSummary(text) {
 let depth=0,maxDepth=0,pvq=null,synthesis=null,peakWords=0,peakBytes=0,wordPeakSite=null;
 const partitions={},pulses={};
 for(const line of text.trim().split(/\r?\n/).filter(Boolean)) {
  const [e,a,b,c,d]=line.split(',').map(Number);
  if(e===1) {depth++;maxDepth=Math.max(maxDepth,depth);const r=partitions[a+':'+b]??={n:a,lm:b,calls:0,leaves:0,nonzero:0,zero:0};r.calls++;}
  if(e===2)partitions[a+':'+b].leaves++;
  if(e===3)partitions[a+':'+b][d?'nonzero':'zero']++;
  if(e===4){assert.ok(depth>0);depth--;}
  if(e===5){assert.equal(pvq,null);pvq={n:a,k:b,blocks:c};const r=pulses[a+':'+c]??={n:a,blocks:c,calls:0,max_k:0};r.calls++;r.max_k=Math.max(r.max_k,b);}
  if(e===6){assert.ok(pvq);pvq=null;}
  if(e===7){if(c>peakWords){peakWords=c;wordPeakSite={count:a,element_bytes:b,pvq,synthesis};}peakBytes=Math.max(peakBytes,d);}
  if(e===8){assert.equal(synthesis,null);synthesis={n:a,lm:b};}
  if(e===9){assert.ok(synthesis);synthesis=null;}
 }
 assert.equal(depth,0);assert.equal(pvq,null);assert.equal(synthesis,null);
 return {partitions:Object.values(partitions),pulses:Object.values(pulses),max_partition_depth:maxDepth,allocation_peak_words:peakWords,allocation_peak_bytes:peakBytes,word_peak_site:wordPeakSite};
}
async function check(selected=candidates.kinds) {
 fs.mkdirSync(out,{recursive:true});
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'ebands-final'});
 const sources=JSON.parse(fs.readFileSync(path.join(base.out,'build.json'))).sources;
 const models=require('./ebands_final.cjs').cModels();
 const fixtures=specs(),report={scope:'Host C semantic candidates over accepted ebands-final mirror. ASan/UBSan and exact PCM; not target ASM or CPU timings. Original firmware and C fallback untouched.',recipe_sha256:sourceHash(__filename),model_sha256:sourceHash(path.join(__dirname,'algorithm_candidates.cjs')),compiler:base.compiler,variants:[]};
 const probe=(binary,f,pcm,env=[],self=true)=>JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',...env,hostPath(binary),...(f.sequence?['--sequence',hostPath(pcm),...f.sequence.map(hostPath)]:[hostPath(f.file),hostPath(pcm),...(self?['--self-test']:[])])]));
 const references=new Map();
 for(const kind of selected) {
  assert.ok(candidates.kinds.includes(kind));
  const changes=candidates.generate(kind,models),dir=path.join(out,kind),objects=[...base.objects];
  for(const change of changes) {
   const index=sources.indexOf(change.base);assert.ok(index>=0,change.base);
   const object=path.join(dir,path.basename(change.file)+'.o');
   execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(change.file),'-o',hostPath(object)]);objects[index]=object;
  }
  const binary=path.join(dir,'probe'),extra=[];
  if(kind==='observe') {
   const object=path.join(dir,'observer.o');execute('gcc',[...base.flags,'-c',hostPath(path.join(__dirname,'algorithm_observer.c')),'-o',hostPath(object)]);objects.push(object);extra.push('-Wl,--wrap=yoradio_opus_scratch_alloc');
  }
  execute('gcc',[...base.linkFlags,...objects.map(hostPath),...extra,'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
  const r={kind,source_hashes:changes.map(c=>({source:c.source,base_sha256:sourceHash(c.base),candidate_sha256:sourceHash(c.file)})),cases:[]};
  for(const f of fixtures) {
   if(kind==='observe'&&(f.sequence||f.name.startsWith('phase-')||f.name.includes('120ms')||f.name.includes('48frames')))continue;
   const key=f.name+(kind==='observe'?'-observed':''),a=path.join(out,key+'.reference.pcm'),b=path.join(dir,f.name+'.pcm'),trace=path.join(dir,f.name+'.csv');
   if(!references.has(key))references.set(key,probe(base.binary,f,a,[],kind!=='observe'));
   const reference=references.get(key),candidate=probe(binary,f,b,kind==='observe'?['YORADIO_ALGORITHM_TRACE='+hostPath(trace)]:[],kind!=='observe');
   const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,kind+'/'+f.name);
   if(kind==='observe')for(const field of ['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','arena_guards_ok'])assert.deepEqual(candidate[field],reference[field]);
   else verifyState(reference,candidate);
   const entry={name:f.name,fixture_sha256:f.file?hash(fs.readFileSync(f.file)):f.sequence.map(file=>hash(fs.readFileSync(file))),pcm,reference,candidate};
   if(kind==='observe') {const bytes=fs.readFileSync(trace);entry.trace_sha256=hash(bytes);entry.trace=traceSummary(bytes.toString());}
   r.cases.push(entry);console.log(kind,f.name,'exact; byte/word peak',reference.scratch_byte_peak_bytes+'/'+reference.scratch_word_peak_bytes,'->',candidate.scratch_byte_peak_bytes+'/'+candidate.scratch_word_peak_bytes);
  }
  r.passed=true;report.variants.push(r);fs.writeFileSync(path.join(dir,'results.json'),JSON.stringify(r,null,2)+'\n');
 }
 report.passed=true;fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={specs,verifyState,traceSummary,check};
if(require.main===module)check(process.argv.length>2?process.argv.slice(2):undefined).catch(e=>{console.error(e);process.exitCode=1;});
