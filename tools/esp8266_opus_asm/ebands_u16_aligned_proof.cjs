// Isolate code alignment from the accepted signed16 -> EXTUI arithmetic proof.
// Parent calls, registers/SAR, memory reads and stack remain unchanged.
const assert=require('node:assert/strict');
const old=require('./ebands_u16_proof.cjs');
const {parsed}=require('./bits_fifth_proof.cjs');
const {target}=require('./partition_frozen_proof.cjs');
function alignment(helpers){
 assert.equal(helpers.length,old.specs.length);
 const originals=old.originals().leaves;
 return old.specs.map((s,i)=>{
  const before=parsed({disassembly:originals[i]}),after=parsed({disassembly:helpers[i]});
  const first=after[0];assert.equal(first.address,s.helper);assert.equal(first.op,'bbsi');
  const a=target(before[0]),b=target(first);assert.equal(b,a,'cross entry moved');
  assert.equal(b%4,0);
  assert.equal(b,i===5?0x4024dd14:s.helper+16);
  const earlyRet=after.find(r=>r.op==='ret');assert.equal(earlyRet.address+earlyRet.bytes,s.helper+13);
  // CFG disassembly must omit the padding and have no incoming branch to it.
  for(const row of after){assert.ok(row.address<s.helper+13||row.address>=s.helper+16);
   if(/^b|^j$|^call0$/.test(row.op))assert.ok(target(row)<s.helper+13||target(row)>=s.helper+16);
  }
  return {helper:s.helper,before:a,after:b,padding_bytes:3,executed_padding:false};
 });
}
function prove(functions,actual,helpers){
 const aligned=alignment(helpers);
 return {...old.prove(functions,actual,helpers),alignment:aligned,
  alignment_scope:'Five contiguous cross entries retain original +16; split entry unchanged. Three bytes after early RET are unreachable. Timing still requires physical A/B/A.'};
}
module.exports={...old,alignment,prove};
