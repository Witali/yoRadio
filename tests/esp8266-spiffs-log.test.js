const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),main=path.join(root,'esp8266/rtos-sdk-native/main');
const source=fs.readFileSync(path.join(main,'spiffs_log.c'),'utf8');
test('SPIFFS logging defaults off and never allocates/writes inside its hook',()=>{
  const cmake=fs.readFileSync(path.join(main,'CMakeLists.txt'),'utf8');
  assert.match(cmake,/option\(YORADIO_ESP8266_SPIFFS_LOG[\s\S]*?OFF\)/);
  assert.match(cmake,/if\(YORADIO_ESP8266_SPIFFS_LOG\)\s*list\(APPEND YORADIO_SOURCES "spiffs_log.c"\)/);
  assert.doesNotMatch(source,/\b(malloc|calloc|realloc|fopen|xTaskCreate|xQueueCreate)\s*\(/);
  const hook=source.slice(source.indexOf('static void queue_char'),source.indexOf('void spiffs_log_init'));
  assert.doesNotMatch(hook,/\b(open|write|close|stat|rename|unlink|vTaskDelay)\s*\(/);
  assert.match(source,/esp_log_set_putchar\(log_putchar\)/);
  const app=fs.readFileSync(path.join(main,'app_main.c'),'utf8');
  assert.ok(app.indexOf('spiffs_log_init()')<app.indexOf('native_state_init()'));
  assert.match(app,/storage_service_init\(\);\s*if \(result == ESP_OK\) \{\s*spiffs_log_mount_ready\(\)/);
  assert.match(app,/memory_profile_poll\(\);\s*spiffs_log_poll\(\)/);
  const web=fs.readFileSync(path.join(main,'web_service.c'),'utf8');
  assert.match(web,/#if YORADIO_ESP8266_SPIFFS_LOG_HTTP\s*#include "web_spiffs_log.inc"/);
  assert.match(cmake,/SPIFFS_LOG AND NOT YORADIO_ESP8266_DIAGNOSTIC/);
  assert.match(cmake,/SPIFFS_LOG_HTTP AND NOT YORADIO_ESP8266_SPIFFS_LOG/);
  const build=fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8');
  assert.match(build,/\[switch\]\$SpiffsLog/);
  assert.match(build,/spiffs_log=\[bool\]\$SpiffsLog/);
});
for(const http of [0,1,2]) test(`SPIFFS ${http===2?'HTTP handler':'logger HTTP='+http}: real C I/O and ownership failures`,t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'yoradio-spiffs-log-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const fixture=fs.readFileSync(path.join(__dirname,http===2?'native/esp8266_web_spiffs_log_test.c':'native/esp8266_spiffs_log_test.c'),'utf8');
  const code=http===2?fixture.replace('/* HANDLER */',fs.readFileSync(path.join(main,'web_spiffs_log.inc'),'utf8')):
    fixture.replace('/* LOGGER_IMPLEMENTATION */',source.slice(source.indexOf('#define LOG_FLUSH_MS')));
  const file=path.join(dir,'test.c'),exe=path.join(dir,process.platform==='win32'?'test.exe':'test');
  fs.writeFileSync(file,`#define YORADIO_ESP8266_SPIFFS_LOG_HTTP ${http?1:0}\n`+code);let build;
  if(process.platform==='win32') {
    const base='C:/Program Files/Microsoft Visual Studio';let vc;
    if(fs.existsSync(base))for(const v of fs.readdirSync(base))for(const e of fs.readdirSync(path.join(base,v))) {
      const p=path.join(base,v,e,'VC/Auxiliary/Build/vcvars64.bat');if(fs.existsSync(p))vc=p;
    }
    if(!vc)return t.skip('Visual C++ unavailable');
    const batch=path.join(dir,'build.cmd');
    fs.writeFileSync(batch,`@call "${vc}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c11 /W4 /WX /D_CRT_SECURE_NO_WARNINGS /DYORADIO_ESP8266_SPIFFS_LOG=1 /I"${main}" "${file}" /Fe:"${exe}"\r\n`);
    build=spawnSync('cmd.exe',['/d','/c',batch],{cwd:dir,encoding:'utf8',timeout:60000});
  }else{
    build=spawnSync('cc',['-std=c11','-Wall','-Wextra','-Werror','-DYORADIO_ESP8266_SPIFFS_LOG=1','-I'+main,file,'-o',exe],{cwd:dir,encoding:'utf8',timeout:60000});
    if(build.error?.code==='ENOENT')return t.skip('C compiler unavailable');
  }
  assert.equal(build.status,0,build.stdout+'\n'+build.stderr);
  const run=spawnSync(exe,[],{encoding:'utf8',timeout:10000});
  assert.equal(run.status,0,run.stdout+'\n'+run.stderr);
  assert.match(run.stdout,/(SPIFFS|HTTP) log PASS/);t.diagnostic(run.stdout.trim());
});
