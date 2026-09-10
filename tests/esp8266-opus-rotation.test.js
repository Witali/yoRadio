const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {run}=require('../tools/esp8266_opus_profile/check_rotation_lx106.cjs');
const {root,component,execute,hostPath}=require('../tools/esp8266_opus_profile/build_host.cjs');
test('LX106 rotation instruction model matches sanitized C fallback and preserves ABI',{timeout:180000},()=>{
  const r=run();assert.equal(r.passed,true);assert.equal(r.cases,512);assert.equal(r.stack_bytes,16);
  assert.equal(r.instruction_model_exact,true);assert.equal(r.c_fallback_asan_ubsan,true);
});
test('rotation experiment is default off and a host with the flag keeps C',()=>{
  const header=path.join(component,'opus_rotation.h'),args=['-E','-dM','-x','c','-include',hostPath(header),'/dev/null'];
  assert.match(execute('gcc',args),/^#define YORADIO_OPUS_USE_LX106_ROTATION 0$/m);
  assert.match(execute('gcc',['-DYORADIO_OPUS_ROTATION_LX106=1',...args]),/^#define YORADIO_OPUS_USE_LX106_ROTATION 0$/m);
  assert.throws(()=>execute('gcc',['-DYORADIO_OPUS_ROTATION_LX106=2',...args]),/must be 0 or 1/);
  assert.match(fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),/option\(YORADIO_OPUS_ROTATION_LX106 [^\n]+ OFF\)/);
  assert.match(fs.readFileSync(path.join(root,'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'),'utf8'),/OpusRotationLx106.*requires diagnostic Opus/);
});
