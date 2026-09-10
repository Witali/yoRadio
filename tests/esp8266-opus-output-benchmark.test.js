const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), os = require('node:os');
const {spawnSync} = require('node:child_process');
const {analyzeOutput} = require('../tools/esp8266_opus_profile/output_benchmark_result.cjs');
const root = path.resolve(__dirname,'..');
test('physical benchmark requires actual DMA and 20 seconds without misses, not just decode success', () => {
  const item = {samples:1152000,output_samples:1152000,pipeline_wall_us:24000000,
    pipeline_task_us:18000000,output_wall_us:7000000,wall_us:15000000,
    dma_eofs:2300,dma_misses:0,packets:1200,min_dram:6000,error:0};
  assert.equal(analyzeOutput(item).pass,true);
  assert.equal(analyzeOutput(item).pipeline_cpu_budget_percent,75);
  for (const patch of [{dma_misses:1},{dma_eofs:0},{output_samples:0},{pipeline_wall_us:30000000},
    {error:-9008},{samples:1152960},{pipeline_task_us:30000000},{wall_us:undefined}])
    assert.equal(analyzeOutput({...item,...patch}).pass,false,JSON.stringify(patch));
  assert.equal(analyzeOutput({...item,samples:115200,output_samples:115200,pipeline_wall_us:2400000}).pass,false);
});
test('actual output CMake gate requires diagnostic raw benchmark and a real PDM32 backend', () => {
  const source = fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/CMakeLists.txt'),'utf8');
  const start = source.indexOf('option(YORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT');
  const end = source.indexOf('set(YORADIO_ESP8266_OPUS_BENCHMARK_FIXTURES',start);
  assert.ok(start>=0 && end>start);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'opus-output-profile-'));
  try {
    const file=path.join(dir,'check.cmake'); fs.writeFileSync(file,source.slice(start,end));
    const cmake=process.platform==='win32' ? path.join(root,'.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe') : 'cmake';
    for (const output of [0,1]) for (const raw of [0,1]) for (const pdm of [0,1]) for (const discard of [0,1]) {
      const run=spawnSync(cmake,[`-DYORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT=${output}`,
        `-DYORADIO_ESP8266_OPUS_BENCHMARK=${raw}`,`-DCONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=${pdm}`,
        '-DCONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=1',`-DYORADIO_ESP8266_AUDIO_PROFILE_DECODE_ONLY=${discard}`,
        '-P',file],{encoding:'utf8'});
      assert.equal(run.status===0,!output || !!(raw&&pdm&&!discard),run.stdout+run.stderr);
    }
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
  const builder = fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  assert.match(builder,/\$OpusBenchmarkOutput -and -not \$OpusBenchmark/);
  assert.match(builder,/-DYORADIO_ESP8266_OPUS_BENCHMARK_OUTPUT=\$taskOpusBenchmarkOutput/);
  assert.match(builder,/opus_benchmark_output=\[bool\]\$OpusBenchmarkOutput/);
});
