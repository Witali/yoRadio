// Frequency of exact PVQ boundary guards and earlier search convergence. Host only.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs'),{once}=require('./bands.cjs');
function boundary(cache,bits) {
 assert.ok(cache[0]>0);
 const zero=bits<=((cache[1]+1)>>1),upper=bits>cache[cache[0]]+1;
 assert.ok(!(zero&&upper));
 let lo=0,hi=cache[0],value=bits-1;
 for(let i=0;i<3;i++){const mid=(lo+hi+1)>>1;if(cache[mid]>=value)hi=mid;else lo=mid;}
 return {zero,upper,after_three:hi-lo<=1};
}
function exhaustive() {
 const {bits,offsets}=require('./pulse_lookup.cjs').tables(),{reference}=require('./pulse_inverse.cjs');
 const r={scope:'Uniform standard-table budgets, not stream frequency or CPU evidence',cases:0,zero:0,upper:0,after_three:0};
 for(const off of offsets)for(let b=-64;b<=16383;b++){
  const cache=bits.slice(off),v=boundary(cache,b),q=reference(cache,b);
  if(v.zero)assert.equal(q,0);if(v.upper)assert.equal(q,cache[0]);
  r.cases++;r.zero+=Number(v.zero);r.upper+=Number(v.upper);r.after_three+=Number(v.after_three);
 }return r;
}
async function profile() {
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const out=path.join(root,'.build/opus-pvq-boundaries-profile');fs.mkdirSync(out,{recursive:true});
 const model=require('./tell_inline.cjs').cModels().find(m=>m.source==='upstream/celt/bands.c');assert.ok(model);
 let text=fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n');
 const observer=path.join(__dirname,'pvq_boundaries_probe.inc.c');
 text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+fs.readFileSync(observer,'utf8')+'\n');
 text=once(text,'      q = bits2pulses(m, i, LM, b);','      q = y_boundary_probe(m, i, LM, b);');
 const source=path.join(out,'bands.model.c'),object=path.join(out,'bands.model.o'),binary=path.join(out,'observer');fs.writeFileSync(source,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const expected=path.join(base.out,'objects',path.basename(model.file)+'.o');assert.equal(base.objects.filter(p=>p===expected).length,1);
 execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===expected?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Host PVQ boundary guard census. Original q always returned; guarded indices checked. No target timing or live qualification.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),rate_sha256_lf:sourceHash(path.join(component,'upstream/celt/rate.h')),generated_model_sha256_lf:sourceHash(source),compiler:base.compiler,flags:base.flags,exhaustive:exhaustive(),cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_BITS_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,k));assert.deepEqual(reference[k],probe[k]);}
  const counts=JSON.parse(fs.readFileSync(stats));assert.ok(counts.zero_fast+counts.upper_fast<=counts.calls);assert.ok(counts.upper_loaded<=counts.upper_fast);assert.ok(counts.after_three<=counts.calls);
  const seconds=probe.samples/48000,entry={name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,calls_per_audio_second:counts.calls/seconds,percent:Object.fromEntries(['zero_fast','upper_fast','upper_loaded','after_three'].map(k=>[k,counts.calls?100*counts[k]/counts.calls:null]))};
  result.cases.push(entry);console.log(f.name,JSON.stringify({counts,percent:entry.percent}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={boundary,exhaustive,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});
