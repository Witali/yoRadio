// Algorithmic workload experiment, NOT an ASM optimization or timing claim.
// Same immutable U table: model U(n,j)>i by j>target, using the exact decoded
// L1 pulse vector. The already-loaded U(n,n) is a known successful lower bound.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
function search(n,k,target,kind){
 assert.ok(n>=3&&k>=n&&target>=n&&target<=k);
 let loads=0,lo=n,hi=k+1;
 const probe=j=>{assert.ok(j>=n&&j<=k);loads++;return j<=target;};
 if(kind==='linear') {let j=k;while(!probe(j))j--;return{index:j,loads};}
 if(kind==='prefix2') {
  for(let t=0;t<2&&hi-lo>1;t++){const j=hi-1;if(probe(j))return{index:j,loads};hi=j;}
 } else if(kind==='gallop') {
  for(let distance=0,step=1;;distance+=step,step*=2){
   const j=k-distance;if(j<=n)break;
   if(probe(j)){lo=j;break;}hi=j;
  }
 } else assert.equal(kind,'binary');
 while(hi-lo>1){const mid=lo+((hi-lo)>>1);if(probe(mid))lo=mid;else hi=mid;}
 return{index:lo,loads};
}
function selfTest(){let cases=0;
 for(let n=3;n<=14;n++)for(let k=n;k<=176;k++)for(let t=n;t<=k;t++){
  for(const mode of['linear','binary','prefix2','gallop'])assert.equal(search(n,k,t,mode).index,t);
  cases++;
 }
 return{cases,algorithms:4,scope:'Index search correctness for every bracket/answer in the tested range; not all Opus data or target timings.'};
}
function summarize(rows){
 const modes=['linear','binary','prefix2','gallop'],totals=Object.fromEntries(modes.map(m=>[m,0])),hist={};
 for(const[n,k,t]of rows){
  const len=k-t+1;hist[len]=(hist[len]||0)+1;
  for(const mode of modes){const r=search(n,k,t,mode);assert.equal(r.index,t);totals[mode]+=r.loads;}
 }
 return{rows:rows.length,table_probes:totals,linear_probe_histogram:hist,
  relative_probe_reduction_percent:Object.fromEntries(modes.slice(1).map(m=>[m,totals.linear?100*(1-totals[m]/totals.linear):null]))};
}
async function analyze(){
 const unit=selfTest(),base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'ebands-final'});
 const out=path.join(root,'.build/opus-pvq-search-analysis'),source=path.join(__dirname,'pvq_search_observer.c');fs.mkdirSync(out,{recursive:true});
 const object=path.join(out,'observer.o'),binary=path.join(out,'observer');
 execute('gcc',[...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 execute('gcc',[...base.linkFlags,...base.objects.map(hostPath),hostPath(object),'-Wl,--wrap=decode_pulses','-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const specs=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 specs.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={scope:'Host-only exact-decoder observer and abstract table-probe counts. No firmware changes, target CPU measurement or RAM/stack proof for a replacement. Branch/address arithmetic and cache effects are not priced.',
  recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(source),cwrs_sha256_lf:sourceHash(path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/cwrs.c')),unit,cases:[]};
 for(const f of specs){
  const a=path.join(out,f.name+'.base.pcm'),b=path.join(out,f.name+'.observed.pcm'),trace=path.join(out,f.name+'.jsonl');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(a)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_PVQ_SEARCH_TRACE='+hostPath(trace),hostPath(binary),hostPath(f.file),hostPath(b)]));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  for(const key of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,key));assert.deepEqual(probe[key],reference[key]);}
  const text=fs.readFileSync(trace,'utf8').trim(),counts=summarize(text?text.split(/\r?\n/).map(JSON.parse):[]);
  const entry={name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),trace_sha256:hash(fs.readFileSync(trace)),seconds:probe.samples/48000,pcm,reference,probe,counts};
  result.cases.push(entry);console.log(f.name,JSON.stringify(counts.table_probes));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={search,selfTest,summarize,analyze};if(require.main===module)analyze().catch(e=>{console.error(e);process.exitCode=1;});
