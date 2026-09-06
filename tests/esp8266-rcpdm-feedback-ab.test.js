const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
test('feedback ablation changes only error feedback; enabled model is production-bit-exact',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-feedback-ab-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir,'rcpdm_feedback_ab');
  const result=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(result.pass,true);assert.equal(result.frames,141312);
  assert.equal(result.prng_and_interpolation_identical,true);assert.equal(result.off_error_ignored,true);
  assert.ok(result.different_words>1000);t.diagnostic(JSON.stringify(result));
  const pcm=path.join(dir,'pcm.s16le');fs.writeFileSync(pcm,Buffer.from([0,0,1,0,255,255,255,127,0,128]));
  const prefix=path.join(dir,'out');const saved=JSON.parse(execute(exe,[pcm,prefix,'8266']).stdout);
  assert.equal(saved.on_reference_frames,5);
  for(const mode of ['on','off'])assert.equal(fs.statSync(prefix+'.'+mode+'.bin').size,20);
});

test('archived feedback ablation has matched controls and reproduces enabled baseline',()=>{
  const root=path.resolve(__dirname,'..');
  const read=file=>JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
  const r=read('docs/benchmarks/esp8266-rcpdm-feedback-ab-2026-09-06/results.json');
  const previous=read('docs/benchmarks/esp8266-rcpdm-feedback-2026-09-06/quality.json');
  assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);assert.equal(r.cases.length,12);
  const {feedback_enabled:on,...a}=r.configs.on,{feedback_enabled:off,...b}=r.configs.off;
  assert.equal(on,true);assert.equal(off,false);assert.deepEqual(a,b);
  assert.equal(a.bit_rate_hz,1536000);assert.equal(a.bits,32);assert.equal(a.shift,4);
  assert.equal(a.dither,2);assert.equal(a.interpolate,true);
  for(const c of r.cases){
    assert.equal(c.proof.frames,c.quality.frames);assert.equal(c.proof.on_reference_frames,c.quality.frames);
    assert.equal(c.proof.prng_and_interpolation_identical,true);
    const old=previous.cases.find(x=>x.id===c.id);
    if(old){assert.equal(c.pcm_sha256,old.pcm_sha256);assert.equal(c.bitstream_sha256.on,old.bitstream_sha256.feedback32);}
    if(c.delay)assert.equal(c.delay.fixed_delay_seconds,31/(2*1536000));
  }
  assert.deepEqual(r.lsb.seeds.map(s=>s.seed),[1,8266,2654435769]);
  assert.ok(Math.abs(r.lsb.summaries.on.gain_magnitude-1)<.01);
});
