const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
test('RCPDM simple compares current state before update and preserves block continuity',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-simple-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir,'rcpdm_simple_quality');
  const checks=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(checks.pass,true); assert.equal(checks.word_state_comparisons,1972864);
  assert.equal(checks.continuity_checks,20000); assert.equal(checks.tie_checks,5);
  const pcm=Buffer.alloc(257*2);
  for(let i=0;i<257;++i) pcm.writeInt16LE((i*997)%65536-32768,i*2);
  const file=path.join(dir,'input.pcm'); fs.writeFileSync(file,pcm);
  execute(exe,[file,path.join(dir,'out')]);
  execute(build(dir),[file,path.join(dir,'reference')]);
  for(const [name,width] of [['rc8-a16',1],['rc8-a4',1],['rc32',4],['pdm8',1],['pdm32',4]]) {
    const base=fs.readFileSync(path.join(dir,`out.${name}.bin`));
    assert.equal(base.length,257*width);
    assert.deepEqual(base,fs.readFileSync(path.join(dir,`reference.${name}.bin`)));
    if(name.startsWith('rc')) assert.equal(fs.statSync(path.join(dir,`out.${name}-simple.bin`)).size,257*width);
  }
});
