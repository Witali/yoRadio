const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const directory='docs/benchmarks/esp8266-rcpdm-6144-response-2026-09-06';
const r=JSON.parse(fs.readFileSync(path.join(root,directory,'results.json'),'utf8'));
const close=(a,b,tolerance=1e-8)=>assert.ok(Math.abs(a-b)<tolerance,`${a} != ${b}`);

test('response sweep uses equal rates, guarded band and exact historical tone controls',()=>{
  assert.equal(r.complete,true);assert.equal(r.firmware_flashed,false);
  assert.equal(r.bit_rate_hz,6144000);assert.equal(r.pcm_rate,48000);assert.equal(r.tone_level_dbfs,-3);
  assert.deepEqual(r.cases.map(c=>c.hz),[20,30,50,80,100,150,200,300,500,700,1000,1500,2000,3000,5000,7000,10000,12000,15000,18000,20000]);
  assert.deepEqual(r.audio_band_hz,[20,20000]);assert.deepEqual(r.quality_integration_band_hz,[20,20001]);
  const contents=fs.readFileSync(path.join(root,r.baseline_path));
  assert.equal(crypto.createHash('sha256').update(contents).digest('hex'),r.baseline_sha256);
  const old=JSON.parse(contents);assert.deepEqual(r.configs,old.configs);
  assert.equal(r.self_test.pass,true);assert.equal(r.self_test.word_state_checks,2826240);
  for(const row of r.cases){
    assert.equal(row.quality.frames,144000);assert.equal(row.quality.segments,2);
    assert.equal(row.proof.reference_frames_per_variant,144000);assert.equal(row.proof.variants,5);
    if(r.controls_hz.includes(row.hz)){
      const before=old.cases.find(c=>c.hz===row.hz&&c.level_dbfs===-3);
      assert.equal(row.historical_control_reverified,true);assert.equal(row.pcm_sha256,before.pcm_sha256);
      assert.deepEqual(row.bitstream_sha256,before.bitstream_sha256);
    }
    for(const name of Object.keys(r.configs))for(const filt of ['rc10us','rc40us','ladder10us']){
      const quality=row.quality.models[name][filt],response=row.response[name][filt];
      assert.equal(quality.tone_detected,true);
      // A coherent PDM Fs/4 tone has no resolved in-band residual after the
      // total-minus-fundamental subtraction. Null is not lost tone or infinity.
      if(row.hz===12000&&name==='pdm128')assert.equal(quality.sinad_db,null);
      else assert.ok(Number.isFinite(quality.sinad_db));
      if(row.hz===20000)assert.equal(quality.thd_db,null);
      assert.equal(response.window_transfers.length,2);
      const h=response.transfer;
      close(response.gain_db,20*Math.log10(Math.hypot(h.real,h.imag)));
      close(response.phase_degrees,Math.atan2(h.imag,h.real)*180/Math.PI);
      close(response.gain_db,quality.fundamental_gain_db,1e-4);
    }
  }
  assert.ok(fs.statSync(path.join(root,directory,'response-rc10us.png')).size>10000);
});

test('phase curves retain raw delay and separately compensate only the known interpolation',()=>{
  for(const [name,config] of Object.entries(r.configs))for(const [filt,curve] of Object.entries(r.curves[name])){
    const hz=r.cases.map(c=>c.hz);assert.deepEqual(curve.frequencies_hz,hz);
    let previous=0;
    for(let i=0;i<hz.length;i++){
      const c=r.cases[i].response[name][filt];let phase=c.phase_degrees;
      while(phase-previous>180)phase-=360;
      while(phase-previous< -180)phase+=360;
      previous=phase;
      close(curve.raw_phase_degrees[i],phase);
      close(curve.gain_db[i],c.gain_db);
      close(curve.interpolation_compensated_phase_degrees[i],phase+360*hz[i]*config.fixed_delay_seconds);
      close(curve.interpolation_compensated_group_delay_us[i],curve.group_delay_us[i]-config.fixed_delay_seconds*1e6);
      if(i>0&&i<hz.length-1){
        const a=hz[i]-hz[i-1],b=hz[i+1]-hz[i];
        const derivative=-b/(a*(a+b))*curve.raw_phase_degrees[i-1]
          +(b-a)/(a*b)*phase+a/(b*(a+b))*curve.raw_phase_degrees[i+1];
        close(curve.group_delay_us[i],-derivative*1e6/360);
      }
    }
  }
});
