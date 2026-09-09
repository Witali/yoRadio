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
});

test('real codec bridge and arena pair every allocation/free through OOM and switches', t => {
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-lifecycle-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const audio=path.join(root,'yoRadio/src/audioI2S');
  const bridge=path.join(root,'esp8266/rtos-sdk-native/components/helix_codecs');
  const sources=[path.join(audio,'mp3_decoder/mp3_decoder.cpp'),path.join(audio,'aac_decoder/aac_decoder.cpp'),
    path.join(bridge,'codec_bridge.cpp'),path.join(bridge,'CodecMemoryArena.cpp'),
    path.join(__dirname,'native/codec_lifecycle/test.cpp')];
  const includes=[path.join(__dirname,'native/codec_lifecycle'),path.join(__dirname,'native/esp8266_input/stubs'),
    path.join(__dirname,'native/helix_golden'),audio,path.join(audio,'mp3_decoder'),path.join(audio,'aac_decoder'),bridge];
  const defines=['YORADIO_ESP8266_NATIVE=1','YORADIO_HELIX_MP3_MONO=1','YORADIO_HELIX_MP3_SSO=1',
    'YORADIO_ESP8266_AAC_BLOCK_OUTPUT=1','YORADIO_ESP8266_AAC_PCM_BLOCK_FRAMES=512','CONFIG_YORADIO_STREAM_INPUT_BYTES=4096','PROGMEM='];
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
});
