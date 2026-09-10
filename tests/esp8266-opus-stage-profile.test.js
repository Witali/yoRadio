const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {execute,hostPath,root,component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {analyzeStage}=require('../tools/esp8266_opus_profile/stage_profile_result.cjs');
test('stage cycles remain wall times, not task CPU, and bad metadata is rejected',()=>{
  const status={profile_stage:8,stage_clock_hz:160000000};
  const item={stage_cycles_lo:320000,stage_cycles_hi:0,stage_calls:2,stage_max_cycles:160000,wall_us:10000,task_us:9000};
  const value=analyzeStage(status,item);assert.equal(value.wall_us,2000);assert.equal(value.wall_percent_of_decode,20);
  assert.equal(value.max_wall_us,1000);assert.match(value.warning,/NOT exclusive/);
  assert.equal(analyzeStage({},item),null);
  assert.throws(()=>analyzeStage({...status,stage_clock_hz:80000000},item),/metadata/);
  assert.throws(()=>analyzeStage(status,{...item,stage_calls:0}),/Inconsistent/);
  const wrapped=analyzeStage(status,{...item,stage_cycles_hi:1});
  assert.equal(wrapped.wall_us,(4294967296+320000)/160);
  assert.throws(()=>analyzeStage(status,{...item,stage_cycles_lo:4294967296}),/Invalid/);
  assert.throws(()=>analyzeStage(status,{...item,stage_cycles_hi:0xffffffff}),/Inconsistent/);
});
test('ESP8266 nano printf wire response uses only supported 32-bit words',()=>{
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const block=source.slice(source.indexOf('#if YORADIO_OPUS_PROFILE_STAGE',source.indexOf('opus_benchmark_case_snapshot')));
  assert.match(block,/stage_cycles_lo/);assert.match(block,/stage_cycles_hi/);
  assert.doesNotMatch(block.split('#endif')[0],/%(?:ll|j|z)/);
});
test('selected stage counters, timer wrap and 64-bit totals under sanitizers',()=>{
  const out=path.join(root,'.build/opus-stage-unit');fs.mkdirSync(out,{recursive:true});
  const binary=hostPath(path.join(out,'counter'));
  execute('gcc',['-O3','-g','-std=c99','-fno-pie','-no-pie','-fsanitize=undefined,address',
    '-DYORADIO_OPUS_PROFILE_STAGE=8','-DYORADIO_OPUS_PROFILE_TEST_CLOCK=1','-I'+hostPath(component),
    hostPath(path.join(component,'opus_stage_profile.c')),hostPath(path.join(root,'tools/esp8266_opus_profile/stage_counter_probe.c')),'-o',binary]);
  execute('env',['ASAN_OPTIONS=detect_leaks=0',binary]);
});
test('off has no storage or callable instrumentation; invalid stage fails',()=>{
  const out=path.join(root,'.build/opus-stage-unit');fs.mkdirSync(out,{recursive:true});
  const object=hostPath(path.join(out,'off.o'));
  const args=['-O3','-I'+hostPath(component),'-c',hostPath(path.join(component,'opus_stage_profile.c')),'-o',object];
  execute('gcc',args);assert.equal(execute('nm',['--defined-only',object]).trim(),'');
  assert.throws(()=>execute('gcc',['-DYORADIO_OPUS_PROFILE_STAGE=12',...args]),/must be 0/);
});
test('non-diagnostic and physical-output stage profiles are rejected before configuring',()=>{
  const build=fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  assert.match(build,/if \(\$OpusProfileStage -and \(-not \$OpusBenchmark -or \$OpusBenchmarkOutput\)\)/);
  const cmake=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8');
  assert.match(cmake,/NOT YORADIO_ESP8266_DIAGNOSTIC OR NOT YORADIO_ESP8266_OPUS_BENCHMARK OR YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT/);
});
