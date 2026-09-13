const assert=require('node:assert/strict');
const names=['yoradio_opus_decode_bounded','celt_decode_with_ec','quant_all_bands','alg_unquant',
 'decode_pulses','renormalise_vector','clt_mdct_backward_c','opus_fft_impl','ec_decode',
 'ec_dec_update','ec_dec_uint','ec_dec_icdf','ec_dec_bits','ec_dec_bit_logp'];
function analyzeFunctions(s){
 assert.equal(s.state,3);assert.equal(s.error,0);assert.equal(s.function_error,0);
 assert.equal(s.function_clock_hz,1000000);assert.equal(s.functions.length,names.length);
 const sample=s.results[s.function_case],root=s.functions[0];
 assert.ok(sample&&sample.samples>0);assert.equal(root.calls,sample.packets);
 assert.ok(root.cpu_us>0&&root.wall_us>0);
 assert.ok(root.cpu_us<=sample.task_us+root.calls*2,'Function CPU exceeds outer task window');
 assert.ok(root.wall_us<=sample.wall_us+root.calls,'Function wall exceeds outer decode window');
 for(const [i,r] of s.functions.entries()){
  assert.equal(r.id,i);
  for(const key of ['calls','cpu_us','self_cpu_us','max_cpu_us','wall_us','self_wall_us','max_wall_us'])
   assert.ok(Number.isInteger(r[key])&&r[key]>=0&&r[key]<=0xffffffff,'Invalid '+key);
  assert.ok(r.self_cpu_us<=r.cpu_us&&r.max_cpu_us<=r.cpu_us&&r.cpu_us<=root.cpu_us);
  assert.ok(r.self_wall_us<=r.wall_us&&r.max_wall_us<=r.wall_us&&r.wall_us<=root.wall_us);
  assert.ok(r.calls||(!r.cpu_us&&!r.wall_us));
 }
 assert.equal(s.functions.reduce((n,r)=>n+r.self_cpu_us,0),root.cpu_us,'Self CPU partition is incomplete');
 assert.equal(s.functions.reduce((n,r)=>n+r.self_wall_us,0),root.wall_us,'Self wall partition is incomplete');
 const seconds=sample.samples/48000;
 return {case_id:s.function_case,audio_seconds:seconds,
  scope:'Cross-object symbol calls only; same-TU/inlined/unwrapped work and bookkeeping remain in parent self time. CPU includes charged ISR; wall includes preemption. No overhead subtraction.',
  rows:s.functions.map((r,i)=>({...r,name:names[i],calls_per_frame:r.calls/sample.packets,
   calls_per_audio_second:r.calls/seconds,mean_cpu_us:r.calls?r.cpu_us/r.calls:0,
   inclusive_cpu_percent:100*r.cpu_us/root.cpu_us,self_cpu_percent:100*r.self_cpu_us/root.cpu_us,
   inclusive_wall_percent:100*r.wall_us/root.wall_us,self_wall_percent:100*r.self_wall_us/root.wall_us}))};
}
module.exports={names,analyzeFunctions};
