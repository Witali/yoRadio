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
  assert.equal(result.simple_reference_frames,141312);assert.equal(result.simple_tie_checks,2);
  assert.ok(result.simple_different_words>1000);
  assert.equal(result.no_dither_frames_per_method,141312);assert.equal(result.disabled_prng_unchanged,true);
  assert.equal(result.prng_and_interpolation_identical,true);assert.equal(result.off_error_ignored,true);
  assert.ok(result.different_words>1000);t.diagnostic(JSON.stringify(result));
  const pcm=path.join(dir,'pcm.s16le');fs.writeFileSync(pcm,Buffer.from([0,0,1,0,255,255,255,127,0,128]));
  const prefix=path.join(dir,'out');const saved=JSON.parse(execute(exe,[pcm,prefix,'8266']).stdout);
  assert.equal(saved.on_reference_frames,5);
  for(const mode of ['on','off'])assert.equal(fs.statSync(prefix+'.'+mode+'.bin').size,20);
  const simple=JSON.parse(execute(exe,[pcm,prefix+'-simple','8266','simple']).stdout);
  assert.equal(simple.method,'simple');assert.equal(simple.on_reference_frames,5);
  for(const mode of ['on','off'])assert.equal(fs.statSync(prefix+'-simple.'+mode+'.bin').size,20);
  for(const method of ['predictive','simple']){
    const paths=[];
    for(const seed of ['1','8266']){
      const output=prefix+'-'+method+'-nodither-'+seed;
      const proof=JSON.parse(execute(exe,[pcm,output,seed,...(method==='simple'?['simple']:[]),'no-dither']).stdout);
      assert.equal(proof.method,method);assert.equal(proof.dither,0);assert.equal(proof.on_reference_frames,5);paths.push(output);
    }
    for(const mode of ['on','off'])assert.deepEqual(fs.readFileSync(paths[0]+'.'+mode+'.bin'),fs.readFileSync(paths[1]+'.'+mode+'.bin'));
  }
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

test('Simple on/off archive matches the predictive experiment except for decision rule',()=>{
  const root=path.resolve(__dirname,'..');
  const read=dir=>JSON.parse(fs.readFileSync(path.join(root,'docs/benchmarks',dir,'results.json'),'utf8'));
  const p=read('esp8266-rcpdm-feedback-ab-2026-09-06'),s=read('esp8266-rcpdm-simple-feedback-ab-2026-09-06');
  assert.equal(s.complete,true);assert.equal(s.method,'simple');assert.equal(s.firmware_flashed,false);
  assert.equal(s.cases.length,12);assert.equal(s.seed,p.seed);
  assert.equal(s.pcm_rate,p.pcm_rate);assert.equal(s.common_grid_rate,p.common_grid_rate);
  assert.deepEqual(s.band_hz,p.band_hz);
  assert.equal(s.self_test.simple_reference_frames,141312);assert.equal(s.self_test.simple_tie_checks,2);
  for(const mode of ['on','off']){
    const {method,...cfg}=s.configs[mode];assert.equal(method,'simple');assert.deepEqual(cfg,p.configs[mode]);
  }
  for(const c of s.cases){
    const old=p.cases.find(row=>row.id===c.id);assert.ok(old);
    assert.equal(c.pcm_sha256,old.pcm_sha256);assert.equal(c.quality.segments,old.quality.segments);
    assert.equal(c.proof.method,'simple');assert.equal(c.proof.on_reference_frames,c.quality.frames);
    assert.equal(c.proof.prng_and_interpolation_identical,true);
    for(const mode of ['on','off'])assert.deepEqual(Object.keys(c.quality.models[mode]),Object.keys(old.quality.models[mode]));
    if(c.delay)assert.equal(c.delay.fixed_delay_seconds,old.delay.fixed_delay_seconds);
  }
  assert.deepEqual(s.lsb.pcm_sha256,p.lsb.pcm_sha256);assert.equal(s.lsb.window_seconds,p.lsb.window_seconds);
  assert.deepEqual(s.lsb.seeds.map(row=>row.seed),p.lsb.seeds.map(row=>row.seed));
});
