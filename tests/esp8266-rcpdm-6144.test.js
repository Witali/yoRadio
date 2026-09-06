const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');
const root=path.resolve(__dirname,'..'),report='docs/benchmarks/esp8266-rcpdm-6144-2026-09-06/results.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);

test('native 6.144 MHz paths emit 128 fresh bits and match independent references',t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-6144-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir,'rcpdm_6144_quality'),proof=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(proof.pass,true);assert.equal(proof.frames_per_variant,141312);
  assert.equal(proof.word_state_checks,2826240);assert.equal(proof.bits_per_sample,128);
  assert.equal(proof.rc_shift,6);assert.equal(proof.rc_state_bytes,16);assert.equal(proof.pdm_state_bytes,4);
  const samples=[0,1,-1,12345,-32768,32767,0,0,17],pcm=Buffer.alloc(samples.length*2);
  samples.forEach((sample,i)=>pcm.writeInt16LE(sample,i*2));
  const file=path.join(dir,'pcm.s16le'),prefix=path.join(dir,'out');fs.writeFileSync(file,pcm);
  const result=JSON.parse(execute(exe,[file,prefix,'8266']).stdout);
  assert.equal(result.reference_frames_per_variant,samples.length);assert.equal(result.same_prng,true);
  let accumulator=0n;const expected=Buffer.alloc(samples.length*16);let pos=0;
  for(const pcm of samples)for(let word=0;word<4;++word){
    let packed=0;
    for(let bit=0;bit<32;++bit){
      accumulator+=BigInt(pcm+32768);const high=accumulator>=65536n;
      if(high)accumulator-=65536n;packed=((packed<<1)|Number(high))>>>0;
    }
    expected.writeUInt32LE(packed,pos);pos+=4;
  }
  assert.deepEqual(fs.readFileSync(prefix+'.pdm128.bin'),expected);
  for(const name of ['rc128-full','rc128-half','simple128-full','simple128-half'])assert.equal(fs.statSync(prefix+'.'+name+'.bin').size,expected.length);
  assert.notDeepEqual(fs.readFileSync(prefix+'.rc128-full.bin'),fs.readFileSync(prefix+'.rc128-half.bin'));
  t.diagnostic(JSON.stringify(proof));
});

test('6.144 MHz quality report has matched rates/inputs and unchanged archived controls',()=>{
  const r=read(report);assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);
  assert.equal(r.cases.length,12);assert.equal(r.bit_rate_hz,6144000);assert.equal(r.pcm_rate,48000);
  const names=['pdm128','rc128-full','rc128-half','simple128-full','simple128-half'];assert.deepEqual(Object.keys(r.configs),names);
  for(const name of names){
    const cfg=r.configs[name];assert.equal(cfg.bits,128);assert.equal(cfg.bit_rate_hz,6144000);
    if(name==='pdm128')assert.equal(cfg.fixed_delay_seconds,0);
    else {assert.equal(cfg.shift,6);assert.equal(cfg.alpha,1/64);assert.equal(cfg.fixed_delay_seconds,127/(2*6144000));}
  }
  assert.equal(r.configs['rc128-half'].dither,4);assert.equal(r.configs['rc128-half'].dither_relative_to_original,.5);
  assert.deepEqual({...r.configs['simple128-half'],method:'predictive_feedback'},r.configs['rc128-half']);
  assert.deepEqual({...r.configs['simple128-full'],method:'predictive_feedback'},r.configs['rc128-full']);
  for(const [name,control] of Object.entries(r.baseline_reports)){
    assert.equal(control.sha256,hash(control.path));assert.equal(control.reverified_cases,9);
    const old=read(control.path),variant=name==='pdm128'?'pdm128':'feedback128';
    for(const before of old.cases){
      const row=r.cases.find(c=>c.id===before.id);assert.equal(row.pcm_sha256,before.pcm_sha256);
      assert.equal(row.bitstream_sha256[name],before.bitstream_sha256[variant]);
      for(const [filt,metrics] of Object.entries(before.quality.models[variant]))for(const [key,value] of Object.entries(metrics)){
        const got=row.quality.models[name][filt][key];if(typeof value==='number')close(got,value);else assert.equal(got,value);
      }
    }
  }
  for(const row of r.cases){
    assert.equal(row.proof.reference_frames_per_variant,row.quality.frames);
    if(row.delay)for(const name of names)for(const [filt,values] of Object.entries(row.delay[name])){
      close(values.raw_snr_db,row.quality.models[name][filt].snr_to_input_db);
      if(name==='pdm128')close(values.raw_snr_db,values.aligned_snr_db);
    }
  }
  const lsb=r.lsb;assert.deepEqual(lsb.seeds.map(s=>s.seed),[1,8266,2654435769]);
  assert.equal(lsb.window_seconds,1);assert.equal(lsb.windows_per_seed,8);
  for(const name of names){
    const gains=lsb.seeds.flatMap(s=>s.models[name].gains);assert.equal(gains.length,24);
    const real=gains.reduce((sum,g)=>sum+g.real,0)/24,imag=gains.reduce((sum,g)=>sum+g.imag,0)/24;
    close(lsb.summaries[name].gain_magnitude,Math.hypot(real,imag));
    close(lsb.summaries[name].window_gain_min,Math.min(...gains.map(g=>Math.hypot(g.real,g.imag))));
    close(lsb.summaries[name].window_gain_max,Math.max(...gains.map(g=>Math.hypot(g.real,g.imag))));
    assert.equal(lsb.summaries[name].seeds_are_independent_noise_trials,name!=='pdm128');
  }
});

test('ordinary PDM weak-tone loss is verified from bits, not called infinite SINAD',()=>{
  const r=read(report),weak=read('docs/benchmarks/esp8266-rcpdm-6144-2026-09-06/weak-pdm.json');
  assert.equal(weak.report_sha256,hash(report));
  const observation=weak.cases.find(c=>c.id==='tone-1000hz-80db');
  assert.equal(observation.pcm_min,-3);assert.equal(observation.pcm_max,3);
  assert.ok(observation.nonzero_pcm_samples>0);
  assert.equal(observation.variants.pdm128.alternating_only,true);
  assert.equal(observation.variants.pdm128.constant_word,'0x55555555');
  assert.equal(observation.variants.pdm128.words_checked,480000);
  const row=r.cases.find(c=>c.id===observation.id),zero=r.cases.find(c=>c.id==='zero');
  assert.equal(row.bitstream_sha256.pdm128,zero.bitstream_sha256.pdm128);
  assert.equal(row.quality.models.pdm128.rc10us.tone_detected,false);
  assert.equal(row.quality.models.pdm128.rc10us.sinad_db,null);
  for(const name of ['rc128-half','simple128-half']){
    assert.equal(observation.variants[name].alternating_only,false);
    assert.equal(row.quality.models[name].rc10us.tone_detected,true);
    assert.ok(Math.abs(r.lsb.summaries[name].gain_magnitude-1)<.01);
  }
});
