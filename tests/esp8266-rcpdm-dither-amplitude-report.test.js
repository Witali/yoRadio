const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),base='docs/benchmarks/esp8266-rcpdm-dither-amplitude-2026-09-06';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);

test('dither amplitude sweep holds all other parameters fixed and reproduces controls',()=>{
  for(const method of ['predictive','simple']){
    const r=read(`${base}/${method}/results.json`);
    assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);assert.equal(r.method,method);
    assert.equal(r.cases.length,12);assert.equal(r.self_test.attenuation_reference_frames,5087232);
    assert.deepEqual(Object.keys(r.configs),['full','div2','div4','div8','div16','div32','div64','none']);
    for(const [name,c] of Object.entries(r.configs)){
      const {dither,dither_shift,amplitude_relative_to_original,triangle_multiplier,...fixed}=c;
      assert.deepEqual(fixed,{method,bits:32,bit_rate_hz:1536000,shift:4,alpha:1/16,
        feedback_enabled:true,feedback_shift:0,interpolate:true});
      assert.equal(dither,name==='none'?0:2);
      assert.equal(amplitude_relative_to_original,name==='none'?0:2**(-dither_shift));
      assert.equal(triangle_multiplier,256*amplitude_relative_to_original);
      for(const row of r.cases){
        assert.equal(row.proofs[name].on_reference_frames,row.quality.frames);
        assert.equal(row.proofs[name].dither_shift,dither_shift||0);
        assert.equal(row.proofs[name].dither,dither);
        assert.equal(row.proofs[name].method,method);
        assert.equal(row.proofs[name].prng_and_interpolation_identical,true);
        if(row.delay){
          assert.equal(row.delay.fixed_delay_seconds,31/(2*1536000));
          close(row.delay.models[name].raw_snr_db,row.quality.models[name].rc10us.snr_to_input_db);
        }
      }
    }
    for(const [name,control] of Object.entries(r.controls)){
      assert.equal(control.sha256,hash(control.path));
      assert.equal(control.regenerated_case_count,12);assert.equal(control.regenerated_lsb_count,15);
      const old=read(control.path);
      assert.deepEqual(r.lsb.pcm_sha256,old.lsb.pcm_sha256);
      for(const row of r.cases){
        const before=old.cases.find(c=>c.id===row.id);
        assert.equal(row.pcm_sha256,before.pcm_sha256);
        assert.equal(row.bitstream_sha256[name],before.bitstream_sha256.on);
        if(row.delay)for(const key of ['raw_snr_db','aligned_snr_db'])close(row.delay.models[name][key],before.delay.models.on[key]);
        for(const [filter,metrics] of Object.entries(row.quality.models[name]))for(const [key,value] of Object.entries(metrics)){
          const previous=before.quality.models.on[filter][key];
          if(typeof value==='number')close(value,previous);else assert.equal(value,previous);
        }
      }
      for(const s of r.lsb.variants[name].seeds){
        const before=old.lsb.seeds.find(seed=>seed.seed===s.seed);
        for(const [signal,measurement] of Object.entries(s.measurements)){
          assert.equal(measurement.bitstream_sha256,before.models.on[signal].bitstream_sha256);
        }
      }
    }
  }
});

test('weak-signal results contain three seeds and eight windows, not only a long average',()=>{
  for(const method of ['predictive','simple']){
    const r=read(`${base}/${method}/results.json`);
    assert.equal(r.lsb.window_seconds,1);assert.equal(r.lsb.windows_per_seed,8);
    for(const [name,variant] of Object.entries(r.lsb.variants)){
      assert.equal(variant.seeds_are_independent_noise_trials,name!=='none');
      assert.deepEqual(variant.seeds.map(s=>s.seed),[1,8266,2654435769]);
      const gains=variant.seeds.flatMap(s=>s.gains);
      assert.equal(gains.length,24);
      const mean={real:gains.reduce((s,g)=>s+g.real,0)/24,imag:gains.reduce((s,g)=>s+g.imag,0)/24};
      close(variant.summary.gain_magnitude,Math.hypot(mean.real,mean.imag));
      close(variant.summary.window_gain_min,Math.min(...gains.map(g=>Math.hypot(g.real,g.imag))));
      close(variant.summary.window_gain_max,Math.max(...gains.map(g=>Math.hypot(g.real,g.imag))));
      close(variant.summary.complex_deviation_rms,Math.sqrt(gains.reduce((s,g)=>s+(g.real-mean.real)**2+(g.imag-mean.imag)**2,0)/24));
      for(const seed of variant.seeds)for(const m of Object.values(seed.measurements))assert.equal(m.proof.on_reference_frames,480000);
    }
  }
});
