const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const report=()=>JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks/esp8266-opus-pvq-path-profile-2026-09-14/summary.json')));
test('PVQ host profile pins its implementation and uses real memory fields, exact PCM and sanitizers',()=>{
 const r=report();assert.equal(r.passed,true);assert.deepEqual(r.unit,{passed:true,cases:9});
 for(const[key,file]of Object.entries({recipe_sha256_lf:'tools/esp8266_opus_asm/profile_pvq_paths.cjs',observer_sha256_lf:'tools/esp8266_opus_asm/pvq_path_profile.c',unit_source_sha256_lf:'tools/esp8266_opus_asm/pvq_path_profile_test.c',cwrs_source_sha256_lf:'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt/cwrs.c'}))assert.equal(r[key],sourceHash(path.join(root,file)));
 assert.ok(r.flags.includes('-fsanitize=address,undefined'));assert.equal(r.cases.length,10);
 const fixtures=JSON.parse(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json')));
 for(const f of fixtures.fixtures){const c=r.cases.find(c=>c.name===f.name);assert.equal(c.fixture_sha256,hash(fs.readFileSync(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures',f.name+'.opuspkt'))));}
 assert.equal(r.cases.find(c=>c.name==='stereo-510').fixture_sha256,hash(fs.readFileSync(path.join(root,'tests/fixtures/opus_native/stereo-510.opuspkt'))));
 for(const c of r.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);assert.equal(c.pcm.reference_pcm_sha256,c.pcm.actual_pcm_sha256);assert.equal(c.reference.arena_guards_ok,true);assert.equal(c.probe.arena_guards_ok,true);
  for(const key of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes']){assert.ok(Number.isInteger(c.reference[key]),key);assert.equal(c.reference[key],c.probe[key]);}
  assert.equal(c.seconds,c.probe.samples/48000);assert.equal(c.calls_per_audio_second,c.counts.calls/c.seconds);
 }
});
test('PVQ counts conserve coordinates/searches and identify high-rate row search rather than rare extra dimension probes',()=>{
 const r=report();for(const c of r.cases){const x=c.counts;assert.equal(x.dimensions,x.many_pulses+x.many_dimensions_zero+x.dimension_searches);assert.equal(x.many_pulses,x.row_searches+x.column_searches);assert.equal(x.dimension_extra_probes,x.dimension_probes-x.dimension_searches);
  assert.equal(x.dimension_probe_histogram.length,33);assert.equal(x.dimension_probe_histogram[32],0,'Weighted sum valid only when overflow bucket empty');assert.equal(x.dimension_probe_histogram.reduce((a,b)=>a+b,0),x.dimension_searches);assert.equal(x.dimension_probe_histogram.reduce((a,b,i)=>a+b*i,0),x.dimension_probes);
  assert.equal(c.dimension_extra_probes_per_audio_second,x.dimension_extra_probes/c.seconds);
 }
 const x=r.cases.find(c=>c.name==='stereo-192').counts;assert.equal(x.calls,1648);assert.equal(x.dimensions,9456);assert.equal(x.many_pulses,5921);assert.equal(x.row_searches,5205);assert.equal(x.row_probes,24259);assert.equal(x.dimension_extra_probes,301);assert.equal(x.dimension_probe_histogram[1],1316);
 const low=r.cases.find(c=>c.name==='mono-12');assert.equal(low.counts.calls,0);assert.equal(low.probe.modes.SILK,12);
 assert.match(r.scope,/not a literal ASM branch counter/);assert.match(r.scope,/No target timing/);
});
