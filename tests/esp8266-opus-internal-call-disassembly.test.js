const test=require('node:test'),assert=require('node:assert/strict');
const {reachableDisassembly}=require('../tools/esp8266_opus_asm/report_layout.cjs');
const s={name:'sample',address:0x100,bytes:0x20};
const blocks={
  0x100:'100: 000005 call0 110 <sample+0x10>\n103: 0028 mov.n a2, a2\n105: f00d ret.n',
  0x110:'110: 0028 mov.n a2, a2\n112: f00d ret.n'
};
test('internal leaf traversal is opt-in and retains both helper and caller continuation',()=>{
 const calls=[],read=at=>{calls.push(at);return blocks[at]};
 const old=reachableDisassembly('',s,read);assert.doesNotMatch(old,/^110:/m);assert.match(old,/^103:/m);assert.deepEqual(calls,[0x100]);
 calls.length=0;const now=reachableDisassembly('',s,read,{followInternalCalls:true});
 assert.match(now,/^110:/m);assert.match(now,/^103:/m);assert.deepEqual(calls,[0x100,0x110]);
});
test('internal leaf traversal deduplicates recursion, excludes external calls and rejects invalid targets',()=>{
 let calls=0;const read=at=>{calls++;assert.equal(at,0x100);return '100: 000005 call0 100 <sample>\n103: 000005 call0 200 <external>\n106: f00d ret.n'};
 reachableDisassembly('',s,read,{followInternalCalls:true});assert.equal(calls,1);
 assert.throws(()=>reachableDisassembly('',s,at=>at===0x100?blocks[at]:'110: 000000 ill',{followInternalCalls:true}),/Invalid reachable/);
 assert.throws(()=>reachableDisassembly('',s,()=> '100: 000005 call0 unknown\n103: f00d ret.n',{followInternalCalls:true}),/Unresolved internal call/);
});
