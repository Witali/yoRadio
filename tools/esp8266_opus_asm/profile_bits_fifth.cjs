// Host-only workload census for a future ASM last-search-step specialization.
// No target changes, new runtime tables, timing prediction or speed claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
const {once}=require('./bands.cjs');
function shortcut(cache,bits) {
 let lo=0,hi=cache[0];bits--;
 for(let i=0;i<5;i++){const mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;}
 const gap=hi-lo;
 if(gap>1){const mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;}
 return {q:bits-(lo===0?-1:cache[lo])<=cache[hi]-bits?lo:hi,gap};
}
function exhaustive() {
 const {bits,offsets}=require('./pulse_lookup.cjs').tables(),{reference}=require('./pulse_inverse.cjs');
 let cases=0,skippable=0;const gaps={};
 for(const off of offsets)for(let b=-64;b<=16383;b++){
  const cache=bits.slice(off),r=shortcut(cache,b);assert.equal(r.q,reference(cache,b));
  cases++;if(r.gap<=1)skippable++;gaps[r.gap]=(gaps[r.gap]||0)+1;
 }
 return {scope:'Uniform budgets on standard tables, NOT stream frequencies',cases,skippable,gaps};
}
async function profile() {
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const out=path.join(root,'.build/opus-bits-fifth-profile');fs.mkdirSync(out,{recursive:true});
 const model=require('./tell_inline.cjs').cModels().find(m=>m.source==='upstream/celt/bands.c');assert.ok(model);
 let text=fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n');
 const observer=path.join(__dirname,'bits_fifth_probe.inc.c');
 text=once(text,'#include "rate.h"\n','#include "rate.h"\n'+fs.readFileSync(observer,'utf8')+'\n');
 text=once(text,'      q = bits2pulses(m, i, LM, b);','      q = y_bits_fifth_probe(m, i, LM, b);');
 const source=path.join(out,'bands.model.c'),object=path.join(out,'bands.model.o'),binary=path.join(out,'observer');
 fs.writeFileSync(source,text);
 // Preserve celt/config.h precedence for WORD_SCRATCH/IRAM, as build_host does
 // for generated models. Replacing an arbitrary bands basename is unsafe.
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const expected=path.join(base.out,'objects',path.basename(model.file)+'.o');
 const old=base.objects.filter(p=>p===expected);assert.equal(old.length,1);
 execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===old[0]?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Actual host bits2pulses call census, not LX106 instruction timing. Decoder returns original result; shortcut checked independently on every call. No target firmware changes.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),rate_sha256_lf:sourceHash(path.join(component,'upstream/celt/rate.h')),generated_model_sha256_lf:sourceHash(source),compiler:base.compiler,flags:base.flags,exhaustive:exhaustive(),cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_BITS_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const key of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,key));assert.deepEqual(reference[key],probe[key]);}
  const counts=JSON.parse(fs.readFileSync(stats));assert.equal(counts.gaps_after_five.reduce((a,b)=>a+b,0),counts.calls);assert.equal(counts.skippable,counts.gaps_after_five[0]+counts.gaps_after_five[1]);
  const seconds=probe.samples/48000,entry={name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,calls_per_audio_second:counts.calls/seconds,skippable_percent:counts.calls?100*counts.skippable/counts.calls:null};
  result.cases.push(entry);console.log(f.name,JSON.stringify({calls:counts.calls,skip:counts.skippable,percent:entry.skippable_percent}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={shortcut,exhaustive,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});
