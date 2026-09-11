const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');

test('PDM32 batch CMake option is OFF by default and rejects non-standard backends', t => {
  const source = fs.readFileSync(path.join(root, 'esp8266/rtos-sdk-native/main/CMakeLists.txt'), 'utf8');
  const start = source.indexOf('option(YORADIO_ESP8266_PDM32_BATCH');
  const end = source.indexOf('set(YORADIO_AUDIO_LDFRAGMENTS', start);
  assert.ok(start >= 0 && end > start);
  const block = source.slice(start, end);
  assert.match(block, /option\(YORADIO_ESP8266_PDM32_BATCH\s+"[^"]+" OFF\)/);
  assert.match(source, /YORADIO_ESP8266_PDM32_BATCH=\$<BOOL:\$\{YORADIO_ESP8266_PDM32_BATCH\}>/);
  const bundled = path.join(root, '.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const command = process.platform === 'win32' && fs.existsSync(bundled) ? bundled : 'cmake';
  const available = spawnSync(command, ['--version'], {encoding:'utf8'});
  if (available.error?.code === 'ENOENT') return t.skip('CMake unavailable');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pdm32-batch-cmake-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const script = path.join(dir, 'profile.cmake');
  fs.writeFileSync(script, 'cmake_minimum_required(VERSION 3.13)\n' + block);
  const run = options => spawnSync(command, [...options, '-P', script], {encoding:'utf8'});
  assert.equal(run([]).status, 0, 'default must allow ordinary non-PDM32 builds');
  for (const words of [256,512,768,1024]) for(const diag of [false,true])
  for(const queue of [false,true])
  for(const opus of [false,true]) for(const pdm of [false,true]) {
    const result = run(['-DYORADIO_ESP8266_DMA_BUFFER_WORDS='+words,
      '-DYORADIO_ESP8266_OPUS_PCM_QUEUE='+(queue?'ON':'OFF'),
      '-DYORADIO_ESP8266_DIAGNOSTIC='+ (diag?'ON':'OFF'),
      '-DCONFIG_YORADIO_OGG_OPUS='+ (opus?'ON':'OFF'),
      '-DCONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM='+ (pdm?'ON':'OFF'),
      '-DCONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=ON']);
    assert.equal(result.status === 0, words===512 || ((words===768 || (words===256 && queue)) && diag && opus && pdm), result.stdout+result.stderr);
  }
  for (const enabled of [false,true]) for (const pdm of [false,true]) for (const os32 of [false,true]) {
    const result = run(['-DYORADIO_ESP8266_PDM32_BATCH=' + (enabled ? 'ON':'OFF'),
      '-DCONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=' + (pdm ? 'ON':'OFF'),
      '-DCONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=' + (os32 ? 'ON':'OFF')]);
    assert.equal(result.status === 0, !enabled || (pdm && os32), result.stdout + result.stderr);
    if (result.status) assert.match(result.stderr, /requires standard I2S PDM32 output/);
  }
});

test('PCM consumer is diagnostic-only and rejects incompatible pipelines', t => {
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/CMakeLists.txt'),'utf8');
  const start=source.indexOf('option(YORADIO_ESP8266_OPUS_PCM_QUEUE');
  const block=source.slice(start,source.indexOf('if(YORADIO_ESP8266_SDK_RX_DIAG)',start));
  assert.match(block,/option\(YORADIO_ESP8266_OPUS_PCM_QUEUE "[^"]+" OFF\)/);
  const bundled=path.join(root,'.build/esp8266-tools/tools/cmake/3.13.4/bin/cmake.exe');
  const command=process.platform==='win32'&&fs.existsSync(bundled)?bundled:'cmake';
  if(spawnSync(command,['--version']).error?.code==='ENOENT')return t.skip('CMake unavailable');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pcm-gate-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const script=path.join(dir,'profile.cmake');fs.writeFileSync(script,'cmake_minimum_required(VERSION 3.13)\n'+block);
  const required=['YORADIO_ESP8266_DIAGNOSTIC','CONFIG_YORADIO_OGG_OPUS','YORADIO_OPUS_PCM_LEASES',
    'CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM','CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32'];
  const forbidden=['YORADIO_ESP8266_OPUS_BENCHMARK','YORADIO_ESP8266_KARADIO_PIPELINE',
    'YORADIO_ESP8266_OPUS_PCM_PUBLISH','YORADIO_ESP8266_AUDIO_PROFILE','YORADIO_ESP8266_WEB_AUDIO_PAUSE'];
  const valid=Object.fromEntries([...required.map(k=>[k,'ON']),...forbidden.map(k=>[k,'OFF']),['YORADIO_ESP8266_OPUS_PCM_QUEUE','ON']]);
  const run=values=>spawnSync(command,[...Object.entries(values).map(([k,v])=>'-D'+k+'='+v),'-P',script],{encoding:'utf8'});
  assert.equal(run({}).status,0);assert.equal(run(valid).status,0);
  for(const k of [...required,...forbidden]) {
    const result=run({...valid,[k]:valid[k]==='ON'?'OFF':'ON'});
    assert.notEqual(result.status,0,k);assert.match(result.stderr,/PCM queue requires/);
  }
});

test('maximal diagnostic audio JSON fits existing shared scratch', () => {
  const source=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const start=source.indexOf('int body_size = snprintf(body, sizeof(s_async_message),');
  assert.ok(start>=0);
  const format=source.slice(start,source.indexOf('(unsigned)health.generation',start));
  const strings=[...format.matchAll(/"(?:[^"\\]|\\.)*"/g)].map(m=>JSON.parse(m[0])).join('');
  const maximal=strings.replace(/%u/g,'4294967295').replace(/%d/g,'-2147483648').replace(/%s/g,'false');
  assert.doesNotThrow(()=>JSON.parse(maximal));
  const capacity=Number(source.match(/#define WEB_STATUS_CAPACITY (\d+)U/)[1]);
  assert.ok(Buffer.byteLength(maximal)<capacity,Buffer.byteLength(maximal)+' >= '+capacity);
  assert.match(source.slice(start),/body_size < 0 \|\| \(size_t\)body_size >= sizeof\(s_async_message\)/);
});
