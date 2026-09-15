// Pointwise decoder-only equivalence, retaining every other internal address.
// No arithmetic approximation, bitrate cap, source-C or GCC snapshot change.
const assert=require('node:assert/strict'),base=require('./frozen_reloads.cjs');
const prior=require('./partition_frozen_proof.cjs'),{analyze}=require('./partition_decode.cjs');
const expectedBranches=[0x4024dbd3,0x4024dc8d,0x4024e278];
const expectedLoads=[0x4024db43,0x4024dbc5];
function findPatches(fn,{encodeZero=true}={}){
 assert.equal(fn.address,0x4024dafc);assert.equal(fn.bytes,2382);
 const program=prior.program(fn),analysis=analyze(program,{encodeZero});
 assert.deepEqual(analysis.branches.map(b=>program.rows[b.index].address),expectedBranches);
 assert.ok(analysis.branches.every(b=>b.taken));
 const loads=program.rows.flatMap((r,i)=>{
  const o=program.ops[i],state=analysis.states[i];if(!state||o.op!=='l32i')return[];
  const[d,b,offset]=o.args,br=Number(b.slice(1));
  const zero=br===1?state.mem[offset]==='encode0':state.r[br]==='ctx'&&offset==='0'&&encodeZero;
  if(!zero)return[];
  assert.equal(d,'a7');assert.ok([2,3].includes(r.bytes));
  return[{address:r.address,bytes:r.bytes,kind:'zero-load',before:r.text,instruction:(r.bytes===2?'movi.n':'movi')+' a7, 0',origin:br===1?'private stack':'immutable private ctx.encode'}];
 });
 assert.deepEqual(loads.map(p=>p.address),expectedLoads);
 const patches=[...loads,...analysis.branches.map(b=>{
  const r=program.rows[b.index],target=program.rows[b.target].address;
  let bytes=r.bytes;
  if(bytes===2){
   const next=program.rows[b.index+1];assert.equal(next.address,r.address+2);assert.equal(next.bytes,3);assert.equal(next.op,'j');
   assert.ok(analysis.dead.some(d=>d.index===b.index+1),'Overwritten following instruction must be unreachable');
   bytes=5;
  }
  assert.ok(bytes>=3);
  return{address:r.address,bytes,kind:'constant-branch',before:r.text,target,instruction:'j '+target.toString(16)};
 })].sort((a,b)=>a.address-b.address);
 // Do not overwrite any live/interior entry, including from old encoder blocks.
 for(const p of patches){
  for(const r of program.rows)if(/^b|^j$|^call0$/.test(r.op)){
   const t=prior.target(r);assert.ok(t<=p.address||t>=p.address+p.bytes,'Interior patch entry');
  }
 }
 return{patches,analysis,program};
}
function definitions(){return 'point_4024dbd8 = 0x4024dbd8;\npoint_4024e36e = 0x4024e36e;\npoint_4024e297 = 0x4024e297;';}
function prove(before,after,patches){
 const found=findPatches(before),{analysis,program}=found;
 assert.deepEqual(patches.map(({before_hex,after_hex,...p})=>p),found.patches);
 assert.equal(after.address,before.address);assert.equal(after.bytes,before.bytes);
 const current=base.rows(after.disassembly);
 // With the three known predicates replaced, raw reachability is exactly the
 // previously proven decoder paths. No removed live arithmetic or new calls.
 const live=program.rows.filter((_,i)=>analysis.states[i]);
 assert.deepEqual(current.map(r=>r.address),live.map(r=>r.address),'Changed internal instruction address/reachability');
 live.forEach((old,i)=>{
  const patch=patches.find(p=>p.address===old.address),now=current[i];
  if(!patch){assert.deepEqual(now,old);return;}
  if(patch.kind==='zero-load'){
   assert.equal(now.bytes,old.bytes);assert.equal(now.text,'movi a7, 0');
  }else{
   assert.equal(now.bytes,3);assert.equal(now.op,'j');assert.equal(prior.target(now),patch.target);
   const branch=analysis.branches.find(b=>program.rows[b.index].address===old.address);
   assert.equal(analysis.states[branch.index].r[7],'encode0');
  }
 });
 const unknown=analyze(program,{encodeZero:false});assert.equal(unknown.branches.length,0);assert.equal(unknown.dead.length,0);
 assert.equal(current.at(-1).address,program.rows.at(-1).address);assert.equal(current.at(-1).op,'ret.n');
 return{
  constant_branches:analysis.branches,zero_loads:found.patches.filter(p=>p.kind==='zero-load'),
  before_raw_instructions:program.rows.length,after_raw_instructions:current.length,
  unreachable_encoder_instructions:analysis.dead.length,
  scope:'Pointwise induction over unchanged decoder CFG: each replaced load reads immutable zero and MOVI writes identical a7; each J takes exactly the prior encode=0 successor. All remaining live instructions/addresses match, so all registers, SAR, writes, arithmetic, calls and output are unchanged. Only two nonvolatile private reads removed.',
  frame_bytes:112,unknown_encode_disables_specialization:true,
  instruction_count_note:'Same number of dynamically executed instructions per decoder path; removed load/branch work, not a claim of fewer executed instructions.'
 };
}
const contract=prior.contract;
module.exports={expectedBranches,expectedLoads,findPatches,definitions,prove,contract};
