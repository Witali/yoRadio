const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {execute,hostPath,root,component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {analyzeStage}=require('../tools/esp8266_opus_profile/stage_profile_result.cjs');
test('stage ticks remain wall times, not task CPU, and bad metadata is rejected',()=>{
  const status={profile_stage:8,stage_clock_hz:1000000};
  const item={stage_ticks_lo:2000,stage_ticks_hi:0,stage_calls:2,stage_max_ticks:1000,wall_us:10000,task_us:9000};
  const value=analyzeStage(status,item);assert.equal(value.wall_us,2000);assert.equal(value.wall_percent_of_decode,20);
  assert.equal(value.max_wall_us,1000);assert.match(value.warning,/NOT exclusive/);
  assert.equal(analyzeStage({},item),null);
  assert.throws(()=>analyzeStage({...status,stage_clock_hz:80000000},item),/metadata/);
  assert.throws(()=>analyzeStage(status,{...item,stage_calls:0}),/Inconsistent/);
  const wrapped=analyzeStage(status,{...item,stage_ticks_hi:1,wall_us:4294967296+10000});
  assert.equal(wrapped.wall_us,4294967296+2000);
  assert.throws(()=>analyzeStage(status,{...item,stage_ticks_hi:1}),/exceeds outer/);
  assert.throws(()=>analyzeStage(status,{...item,stage_ticks_lo:4294967296}),/Invalid/);
  assert.throws(()=>analyzeStage(status,{...item,stage_ticks_hi:0xffffffff}),/Inconsistent/);
});
test('SDK epoch and CCOUNT are read coherently, decoder scope is not interrupt-masked',()=>{
  const source=fs.readFileSync(path.join(component,'opus_stage_profile.c'),'utf8');
  assert.match(source,/taskENTER_CRITICAL\(\);\s*uint32_t now = \(uint32_t\)esp_timer_get_time\(\);\s*taskEXIT_CRITICAL\(\);/);
  const header=fs.readFileSync(path.join(component,'opus_stage_profile.h'),'utf8');
  assert.doesNotMatch(header,/rsr\.ccount|taskENTER_CRITICAL/);
});
test('ESP8266 nano printf wire response uses only supported 32-bit words',()=>{
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const block=source.slice(source.indexOf('#if YORADIO_OPUS_PROFILE_STAGE',source.indexOf('opus_benchmark_case_snapshot')));
  assert.match(block,/stage_ticks_lo/);assert.match(block,/stage_ticks_hi/);
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
test('saved SDK stage series includes all attempts and the unsafe RAM observation',()=>{
  const dir=path.join(root,'firmware/development/esp8266-opus-stage-sdk-bands');
  const summary=JSON.parse(fs.readFileSync(path.join(dir,'summary.json'),'utf8'));
  assert.equal(summary.attempts.length,10);assert.equal(summary.successful,10);
  assert.equal(summary.ram_reserve_4096_pass,false);assert.ok(summary.low_ram.some(v=>v.run==='run6.json'&&v.min_dram===1052));
  for(let i=1;i<=10;i++) {
    const report=JSON.parse(fs.readFileSync(path.join(dir,'run'+i+'.json'),'utf8'));
    assert.equal(report.final.state,3);assert.equal(report.interval_ms,30000);
    assert.equal(report.final.stage_clock_hz,1000000);
    report.final.results.forEach((item,n)=>{
      const stage=analyzeStage(report.final,item);assert.ok(stage.wall_percent_of_decode>=0&&stage.wall_percent_of_decode<=100);
      assert.equal(item.packets,120);assert.equal(item.samples,115200);
      assert.equal(item.stage_calls,n?120:0);
    });
  }
});
