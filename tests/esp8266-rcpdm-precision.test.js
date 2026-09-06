const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
test('RCPDM higher precision preserves RC decisions and does not cure quiet-tone deadband',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-precision-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir,'rcpdm_precision');
  const checks=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(checks.pass,true); assert.equal(checks.comparisons,675360);
  assert.equal(checks.quiet_tone_checks,384000);
  assert.ok(checks.forced_bit_max_error_pcm<checks.forced_bit_bound_pcm);
  const pcm=Buffer.alloc(257*2);
  for(let i=0;i<257;++i) pcm.writeInt16LE((i*997)%65536-32768,i*2);
  const file=path.join(dir,'input.pcm'); fs.writeFileSync(file,pcm);
  execute(exe,[file,path.join(dir,'out')]);
  const previous=build(dir); execute(previous,[file,path.join(dir,'reference')]);
  for(const [config,width,old] of [['rc8-a16',1,'rc8-a16'],['rc8-a4',1,'rc8-a4'],['rc32-a16',4,'rc32']]) {
    for(const precision of ['fixed32','fixed48','double'])
      assert.equal(fs.statSync(path.join(dir,`out.${config}-${precision}.bin`)).size,257*width);
    assert.deepEqual(fs.readFileSync(path.join(dir,`out.${config}-fixed32.bin`)),fs.readFileSync(path.join(dir,`reference.${old}.bin`)));
  }
  assert.deepEqual(fs.readFileSync(path.join(dir,'out.pdm32.bin')),fs.readFileSync(path.join(dir,'reference.pdm32.bin')));
});
