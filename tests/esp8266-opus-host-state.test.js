const test=require('node:test'),assert=require('node:assert/strict');
const {verifyStates}=require('../tools/esp8266_opus_asm/host_state.cjs');
const report=require('../firmware/development/esp8266-opus-partition-frozen-candidate-v1/host-parent.json');
test('all24 saved PCM scenarios also preserve actual persistent states and scratch fields',()=>{
  assert.equal(report.cases.length,24);
  for(const c of report.cases)verifyStates(c.reference,c.candidate,c.name==='mixed');
});
test('host memory checks reject missing fields on both sides as well as silent size growth',()=>{
  for(const name of ['mono-12','stereo-192','mixed']){
    const c=report.cases.find(c=>c.name===name),mixed=name==='mixed';
    const keys=mixed?['persistent_bytes','sequence_packets','plc_frames']:['mono_state_bytes','stereo_state_bytes','packets','arena_guards_ok','oom_reinitialized_exact'];
    for(const key of keys){
      const a=structuredClone(c.reference),b=structuredClone(c.candidate);delete a[key];delete b[key];
      assert.throws(()=>verifyStates(a,b,mixed),/Missing host state field/);
      const altered=structuredClone(c.candidate);altered[key]=typeof altered[key]==='boolean'?false:altered[key]+1;
      assert.throws(()=>verifyStates(c.reference,altered,mixed));
    }
  }
});
