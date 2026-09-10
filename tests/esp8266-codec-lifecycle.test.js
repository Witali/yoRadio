const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');

test('native defaults and production manifest use a 4 KiB compressed input', () => {
  const read = p => fs.readFileSync(path.join(root,p),'utf8');
  assert.match(read('esp8266/rtos-sdk-native/sdkconfig.defaults'), /^CONFIG_YORADIO_STREAM_INPUT_BYTES=4096$/m);
  assert.match(read('esp8266/rtos-sdk-native/main/Kconfig.projbuild'), /config YORADIO_STREAM_INPUT_BYTES[\s\S]*?default 4096/);
  assert.match(read('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), /stream_input_bytes=4096/);
  assert.match(read('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), /Wrong cached Opus input size/);
  assert.match(read('esp8266/rtos-sdk-native/main/Kconfig.projbuild'), /config YORADIO_OPUS_SCRATCH_BYTES[\s\S]*?default 6144/);
  assert.match(read('tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), /opus_scratch_bytes=\$\(if \(\$taskOpusEnabled\) \{ 6144 \}/);
});

for (const [opusInput, opusScratch, diagnostics] of [[0,6144,0], [1024,6144,0], [1024,6144,1], [1536,6144,1], [2048,6144,1], [1024,7680,1], [1536,7680,1]]) {
const opusEnabled = opusInput !== 0;
test('real codec bridge and arena pair every allocation/free through OOM and switches' +
  (opusEnabled ? ' with Opus input ' + opusInput + ', scratch ' + opusScratch + ', diagnostics ' + diagnostics : ' with Opus disabled'), t => {
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-lifecycle-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const audio=path.join(root,'yoRadio/src/audioI2S');
  const bridge=path.join(root,'esp8266/rtos-sdk-native/components/helix_codecs');
  const sources=[path.join(audio,'mp3_decoder/mp3_decoder.cpp'),path.join(audio,'aac_decoder/aac_decoder.cpp'),
    path.join(bridge,'codec_bridge.cpp'),path.join(bridge,'CodecMemoryArena.cpp'),
    path.join(__dirname,'native/codec_lifecycle/test.cpp')];
  const includes=[path.join(__dirname,'native/codec_lifecycle'),path.join(__dirname,'native/esp8266_input/stubs'),
    path.join(__dirname,'native/helix_golden'),audio,path.join(audio,'mp3_decoder'),path.join(audio,'aac_decoder'),bridge,
    path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder')];
  const defines=['YORADIO_ESP8266_NATIVE=1','YORADIO_HELIX_MP3_MONO=1','YORADIO_HELIX_MP3_SSO=1',
    'YORADIO_ESP8266_AAC_BLOCK_OUTPUT=1','YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=512','CONFIG_YORADIO_STREAM_INPUT_BYTES=4096',
    'CONFIG_YORADIO_OGG_OPUS=' + Number(opusEnabled), 'CONFIG_YORADIO_OPUS_INPUT_BYTES=' + (opusInput || 1024),
    'CONFIG_YORADIO_OPUS_SCRATCH_BYTES=' + opusScratch, 'YORADIO_ESP8266_OPUS_STREAM_TEST=' + diagnostics,
    'YORADIO_ESP8266_OPUS_BENCHMARK=0', 'PROGMEM='];
  const exe=path.join(dir,process.platform==='win32'?'test.exe':'test');
  let build;
  if(process.platform==='win32') {
    const base='C:/Program Files/Microsoft Visual Studio';let vcvars;
    if(fs.existsSync(base)) for(const v of fs.readdirSync(base)) for(const e of fs.readdirSync(path.join(base,v))) {
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(p))vcvars=p;
    }
    if(!vcvars)return t.skip('Visual C++ build tools unavailable');
    const args=['/nologo','/std:c++17','/EHsc','/O2',...includes.map(p=>'/I'+p),...defines.map(d=>'/D'+d),...sources,'/Fe:'+exe];
    const batch=path.join(dir,'build.cmd');
    fs.writeFileSync(batch,`@call "${vcvars}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl ${args.map(a=>'"'+a+'"').join(' ')}\r\n`);
    build=spawnSync('cmd.exe',['/d','/c',batch],{cwd:dir,encoding:'utf8',timeout:60000});
  } else {
    build=spawnSync('c++',['-std=c++17','-O2',...includes.map(p=>'-I'+p),...defines.map(d=>'-D'+d),...sources,'-o',exe],{cwd:dir,encoding:'utf8',timeout:60000});
    if(build.error?.code==='ENOENT')return t.skip('C++ compiler unavailable');
  }
  assert.equal(build.status,0,build.stdout+'\n'+build.stderr);
  const run=spawnSync(exe,[],{encoding:'utf8',timeout:60000});
  assert.equal(run.status,0,run.stdout+'\n'+run.stderr);
  assert.match(run.stdout,/Codec lifecycle PASS/);
  t.diagnostic(run.stdout.trim());
  if (opusEnabled) {
    if (diagnostics) assert.match(run.stdout, /Opus init diagnostics: allocation stages, CAP8 before cleanup, native, reserve, retry PASS/);
    assert.ok(run.stdout.includes('Opus input ' + opusInput + ', scratch ' + opusScratch + ', reserve and allocation-free reset PASS'));
    const fallback=spawnSync(exe,['--dram-arena'],{encoding:'utf8',timeout:60000});
    assert.equal(fallback.status,0,fallback.stdout+'\n'+fallback.stderr);
    assert.match(fallback.stdout,/Opus refuses DRAM fallback arena without leaking/);
    t.diagnostic(fallback.stdout.trim());
  }
});
}
test('network reconnect keeps only Opus and still releases it for a cold open retry', () => {
  const audio=fs.readFileSync(path.resolve(__dirname,'../esp8266/rtos-sdk-native/main/audio_service.c'),'utf8');
  const start=audio.indexOf('if (feed == 0 && generation_current(command.generation))');
  assert.ok(start>=0);
  const recovery=audio.slice(start,audio.indexOf('continue;',start));
  assert.match(recovery,/release_codec\(&codec, &codec_kind, "stream reconnect"\)/);
  assert.match(recovery,/#if CONFIG_YORADIO_OGG_OPUS\s+if \(codec_kind != HELIX_CODEC_OPUS \|\| stream_closed != 0\)\s+#endif\s+release_codec/);
  assert.ok(recovery.indexOf('release_codec')<recovery.indexOf('requeue_if_current'));
  assert.match(audio,/opened = open_http_stream\(command.url, &stream\);\s+if \(opened == 0\) break;[\s\S]*release_codec\(&codec, &codec_kind, "connection retry"\)/);
});
