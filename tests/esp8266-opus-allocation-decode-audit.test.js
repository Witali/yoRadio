const test=require('node:test'),assert=require('node:assert/strict');
const audit=require('../tools/esp8266_opus_asm/audit_allocation_decode.cjs');
const baseline=require('../firmware/development/esp8266-opus-ebands-final-candidate-v2/preflight.json');
const functions=baseline.actual_functions;
const caller=require('../docs/results/esp8266-opus-allocation-decode-audit-20260918.json').linked.functions.celt_decode_with_ec_dred;

test('caller passes all three zero arguments with no bypass into the setup',()=>{
 const proof=audit.callerArguments(caller,functions.clt_compute_allocation);
 assert.deepEqual(proof.writes,[48,44,40]);assert.equal(proof.call,0x40244c85);
 for(const [from,to] of [['movi.n\ta8, 0','movi.n\ta8, 1'],
   ['s32i.n\ta8, a1, 40','s8i\ta8, a1, 40']]){
  const changed=structuredClone(caller);changed.disassembly=changed.disassembly.replaceAll(from,to);
  assert.notEqual(changed.disassembly,caller.disassembly);
  assert.throws(()=>audit.callerArguments(changed,functions.clt_compute_allocation));
 }
 const changed=structuredClone(caller);
 changed.disassembly=changed.disassembly.replace(/j\t[0-9a-f]+ <[^>]*>/,'j\t40244c70 <bypass>');
 assert.notEqual(changed.disassembly,caller.disassembly);
 assert.throws(()=>audit.callerArguments(changed,functions.clt_compute_allocation),/bypasses zero/);
});

test('allocation dead-code count is explicitly conditional on immutable encode=0',()=>{
 const fn=functions.clt_compute_allocation,known=audit.analyze(fn),unknown=audit.analyze(fn,{encodeZero:false});
 assert.equal(known.branches.length,3);assert.ok(known.removed_instructions>20);
 assert.equal(unknown.removed_instructions,0);assert.equal(unknown.branches.length,0);
 assert.equal(known.frame_bytes,192);
});

test('incoming stack-argument write invalidates the conditional analysis',()=>{
 const fn=structuredClone(functions.clt_compute_allocation);
 const old=fn.disassembly;fn.disassembly=old.replace('s32i\ta12, a1, 184','s32i\ta12, a1, 232');
 assert.notEqual(fn.disassembly,old);assert.throws(()=>audit.analyze(fn),/incoming stack arguments/);
});

test('unexpected private-frame alias invalidates the conditional analysis',()=>{
 const fn=structuredClone(functions.clt_compute_allocation);
 const old=fn.disassembly;fn.disassembly=old.replace('mov.n\ta12, a7','mov.n\ta12, a1');
 assert.notEqual(fn.disassembly,old);assert.throws(()=>audit.analyze(fn));
});
