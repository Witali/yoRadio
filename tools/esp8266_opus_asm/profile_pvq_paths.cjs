// Host-only workload counts. Existing target sources/build profiles untouched.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function profile(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const out=path.join(root,'.build/opus-pvq-path-profile'),source=path.join(__dirname,'pvq_path_profile.c');fs.mkdirSync(out,{recursive:true});
 const object=path.join(out,'observer.o'),binary=path.join(out,'observer');
 execute('gcc',[...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 execute('gcc',[...base.linkFlags,...base.objects.map(hostPath),hostPath(object),'-Wl,--wrap=decode_pulses','-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const unitSource=path.join(__dirname,'pvq_path_profile_test.c'),unitBinary=path.join(out,'observer-unit');
 execute('gcc',[...base.flags,hostPath(unitSource),'-o',hostPath(unitBinary)]);
 const unit=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_PVQ_COUNTS='+hostPath(path.join(out,'unit-counts.json')),hostPath(unitBinary)]));
 assert.equal(unit.passed,true);assert.equal(unit.cases,9);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={scope:'Host semantic search counts derived from exact decoded PVQ pulses, not a literal ASM branch counter. No target timing, speedup or RAM claim. One pass, no self-test/PLC repetition.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(source),unit_source_sha256_lf:sourceHash(unitSource),cwrs_source_sha256_lf:sourceHash(path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/cwrs.c')),compiler:base.compiler,flags:base.flags,unit,cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_PVQ_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const key of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,key),key);assert.deepEqual(reference[key],probe[key],key);}
  const counts=JSON.parse(fs.readFileSync(stats));assert.equal(counts.dimensions,counts.many_pulses+counts.many_dimensions_zero+counts.dimension_searches);assert.equal(counts.many_pulses,counts.column_searches+counts.row_searches);assert.equal(counts.dimension_extra_probes,counts.dimension_probes-counts.dimension_searches);
  assert.equal(counts.dimension_probe_histogram.reduce((a,b)=>a+b,0),counts.dimension_searches);
  const seconds=probe.samples/48000,entry={name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,calls_per_audio_second:counts.calls/seconds,dimension_extra_probes_per_audio_second:counts.dimension_extra_probes/seconds};
  result.cases.push(entry);console.log(f.name,JSON.stringify({exact:pcm.exact,calls:counts.calls,searches:counts.dimension_searches,extra_probes:counts.dimension_extra_probes,extra_per_second:entry.dimension_extra_probes_per_audio_second}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});
