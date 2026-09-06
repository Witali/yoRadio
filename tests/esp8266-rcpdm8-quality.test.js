const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
test('RCPDM8 preserves reference decisions, exposes idle lock, and groups into RCPDM32', t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm8-quality-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir);
  const checks=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(checks.pass,true); assert.equal(checks.comparisons,2959296);
  assert.equal(checks.quietToneChecks,96000); assert.equal(checks.matchedAlphaQ16,15025);
  const pcm=Buffer.alloc(257*2);
  for(let i=0;i<257;++i) pcm.writeInt16LE((i*997)%65536-32768,i*2);
  fs.writeFileSync(path.join(dir,'input.pcm'),pcm);
  execute(exe,[path.join(dir,'input.pcm'),path.join(dir,'out')]);
  for(const name of ['pdm8','rc8-a16','rc8-a4','rc8-matched']) assert.equal(fs.statSync(path.join(dir,`out.${name}.bin`)).size,257);
  for(const name of ['pdm32','rc32']) assert.equal(fs.statSync(path.join(dir,`out.${name}.bin`)).size,257*4);
});
