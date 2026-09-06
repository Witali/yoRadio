const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const report='docs/benchmarks/esp8266-rcpdm-6144-legacy-2026-09-06/results.json';
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);

test('legacy comparison holds rates fixed and exactly preserves all archived controls',()=>{
  const r=read(report),controls={};
  assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);
  assert.equal(r.bit_rate_hz,6144000);assert.equal(r.pcm_rate,48000);assert.equal(r.cases.length,31);
  assert.deepEqual(r.quality_integration_band_hz,[20,20001]);
  for(const [key,c] of Object.entries(r.controls)){assert.equal(hash(c.path),c.sha256);controls[key]=read(c.path);}
  for(const [name,cfg] of Object.entries(r.configs)){
    assert.equal(cfg.bits,128);assert.equal(cfg.bit_rate_hz,6144000);
    if(name.endsWith('-legacy')){
      assert.equal(cfg.state_bytes,4);assert.equal(cfg.dither,0);assert.equal(cfg.feedback_enabled,false);
      assert.equal(cfg.interpolate,false);assert.equal(cfg.alpha,1/64);assert.equal(cfg.fixed_delay_seconds,0);
    }else assert.deepEqual(cfg,controls.modern.configs[name]);
  }
  const hits={response:0,modern:0,legacy:0},legacyMap={'rc128-legacy':'rc128-a64','simple128-legacy':'simple128-a64',pdm128:'pdm128'};
  for(const row of r.cases){
    assert.equal(row.proofs.modern.reference_frames_per_variant,row.quality.frames);
    assert.equal(row.proofs.legacy.reference_word_state_checks,row.quality.frames*12);
    assert.equal(Object.keys(row.bitstream_sha256).length,7);
    for(const tag of row.reverified){
      ++hits[tag];
      const before=controls[tag].cases.find(c=>tag==='response'?c.hz===row.hz:c.id===row.id);
      assert.equal(row.pcm_sha256,before.pcm_sha256);
      const mappings=tag==='legacy'?legacyMap:Object.fromEntries(Object.keys(controls.modern.configs).map(n=>[n,n]));
      const quality=tag==='response'?row.quality:row.quality_historical_band;
      for(const [name,archived] of Object.entries(mappings)){
        assert.equal(row.bitstream_sha256[name],before.bitstream_sha256[archived]);
        for(const [filt,values] of Object.entries(before.quality.models[archived]))for(const [key,value] of Object.entries(values)){
          if(typeof value==='number')close(quality.models[name][filt][key],value);
          else assert.equal(quality.models[name][filt][key],value);
        }
        if(tag==='response')assert.deepEqual(row.response[name],before.response[name]);
      }
    }
  }
  assert.deepEqual(hits,{response:21,modern:12,legacy:9});
  for(const curves of Object.values(r.curves))for(const curve of Object.values(curves)){
    assert.equal(curve.frequencies_hz.length,21);assert.equal(curve.frequencies_hz.at(-1),20000);
    for(const key of ['gain_db','raw_phase_degrees','group_delay_us'])assert.ok(curve[key].every(Number.isFinite));
  }
});

test('legacy LSB probe uses identical inputs, verifies PDM and does not invent seed variation',()=>{
  const r=read(report),old=read(r.controls.modern.path),lsb=r.lsb;
  assert.equal(lsb.windows,8);assert.equal(lsb.seed_independent,true);
  assert.deepEqual(lsb.modern_summaries,old.lsb.summaries);
  for(const name of ['pdm128','rc128-legacy','simple128-legacy']){
    const row=lsb.models[name];assert.equal(row.gains.length,8);
    assert.equal(row.summary.seeds_are_independent_noise_trials,false);
    const re=row.gains.reduce((s,g)=>s+g.real,0)/8,im=row.gains.reduce((s,g)=>s+g.imag,0)/8;
    close(row.summary.gain_magnitude,Math.hypot(re,im));
    close(row.summary.dc_plus_lsb,row['dc-plus'].mean_pcm_lsb-row.zero.mean_pcm_lsb);
    close(row.summary.dc_minus_lsb,row['dc-minus'].mean_pcm_lsb-row.zero.mean_pcm_lsb);
  }
  for(const signal of ['zero','dc-plus','dc-minus','tone-plus','tone-minus'])
    assert.equal(lsb.models.pdm128[signal].bitstream_sha256,old.lsb.seeds[0].models.pdm128[signal].bitstream_sha256);
});

test('legacy quiet-signal dead zone is confirmed by output words and DC/LSB probes',()=>{
  const r=read(report),zero=r.cases.find(c=>c.id==='zero');
  for(const name of ['rc128-legacy','simple128-legacy']){
    for(const level of [60,80]){
      const c=r.cases.find(c=>c.id===`tone-1000hz-${level}db`);
      assert.equal(c.idle[name].alternating_only,true);
      assert.equal(c.idle[name].constant_word,zero.idle[name].constant_word);
      assert.equal(c.quality.models[name].rc10us.tone_detected,false);
      assert.equal(c.quality.models[name].rc10us.sinad_db,null);
    }
    const probe=r.lsb.models[name].summary;
    assert.equal(probe.gain_magnitude,0);assert.equal(probe.dc_plus_lsb,0);assert.equal(probe.dc_minus_lsb,0);
  }
  for(const name of ['rc128-half','simple128-half']){
    assert.equal(r.cases.find(c=>c.id==='tone-1000hz-60db').quality.models[name].rc10us.tone_detected,true);
    assert.ok(Math.abs(r.lsb.modern_summaries[name].gain_magnitude-1)<.01);
  }
});
