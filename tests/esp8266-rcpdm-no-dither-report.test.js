const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),base='docs/benchmarks/esp8266-rcpdm-no-dither-2026-09-06';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');

test('dither removal preserves matched controls, verifies PRNG bypass and reports lost tones honestly',()=>{
  for(const method of ['predictive','simple']){
    const r=read(`${base}/${method}/results.json`),old=read(r.dither_control.path);
    assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);assert.equal(r.dither,0);
    assert.equal(r.method,method);assert.equal(r.cases.length,12);
    assert.equal(r.dither_control.sha256,hash(r.dither_control.path));
    assert.equal(r.dither_control.bitstreams_reverified,true);assert.equal(r.dither_control.case_count,12);
    assert.equal(r.dither_control.lsb_pairs,15);assert.equal(r.self_test.disabled_prng_unchanged,true);
    for(const mode of ['on','off']){
      assert.equal(r.configs[mode].dither,0);
      assert.deepEqual({...r.configs[mode],dither:2},{...old.configs[mode],method});
    }
    for(const row of r.cases){
      const before=old.cases.find(c=>c.id===row.id);assert.ok(before);
      assert.equal(row.pcm_sha256,before.pcm_sha256);assert.equal(row.quality.segments,before.quality.segments);
      assert.equal(row.proof.method,method);assert.equal(row.proof.dither,0);
      assert.equal(row.proof.on_reference_frames,row.quality.frames);
      if(row.delay)assert.equal(row.delay.fixed_delay_seconds,before.delay.fixed_delay_seconds);
    }
    for(const level of [40,60,80]){
      const row=r.cases.find(c=>c.id===`tone-1000hz-${level}db`);
      assert.equal(row.quality.models.off.rc10us.tone_detected,false);
      assert.equal(row.quality.models.off.rc10us.sinad_db,null);
      assert.equal(row.activity.off.constant_alternating_only,true);
    }
    assert.equal(r.lsb.seed_independence_verified,true);
    assert.equal(r.lsb.seeds_are_independent_noise_trials,false);
    assert.deepEqual(r.lsb.pcm_sha256,old.lsb.pcm_sha256);
    for(const mode of ['on','off'])for(const name of ['zero','dc-plus','dc-minus','tone-plus','tone-minus']){
      const hashes=r.lsb.seeds.map(s=>s.models[mode][name].bitstream_sha256);
      assert.equal(new Set(hashes).size,1);
    }
    assert.equal(r.lsb.summaries.off.gain_magnitude,0);
  }
});

test('temporal LSB results reproduce archived coherent means instead of hiding their spread',()=>{
  const report=read(`${base}/spurs-and-windows.json`);
  for(const [name,row] of Object.entries(report.variants)){
    const method=name.startsWith('simple')?'simple':'predictive',noDither=name.endsWith('none');
    const file=noDither?`${base}/${method}/results.json`:
      `docs/benchmarks/${method==='simple'?'esp8266-rcpdm-simple-feedback-ab-2026-09-06':'esp8266-rcpdm-feedback-ab-2026-09-06'}/results.json`;
    assert.equal(row.report_sha256,hash(file));
    const original=read(file).lsb.seeds.find(s=>s.seed===2654435769);
    for(const mode of ['on','off']){
      const lsb=row.models[mode].lsb,gain=original.models[mode].differential_gain;
      assert.equal(lsb.gains.length,8);assert.equal(lsb.window_seconds,1);
      assert.ok(Math.abs(lsb.coherent_mean_magnitude-Math.hypot(gain.real,gain.imag))<1e-10);
    }
    if(noDither){
      const values=row.models.on.lsb.gains.map(g=>g.magnitude);
      assert.ok(Math.min(...values)<.5);assert.ok(Math.max(...values)>1.3);
    }
  }
});
